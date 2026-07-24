from datetime import datetime, timezone

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command


# states
from states.ActionStates import ActionStates

# services
from services.exercise_service import (
    extract_text_PDF,
    normalize_text_PDF,
    similarity_score,

    show_exo_imgs_to_user,
    comfirmation_exo,

    convert_pdf_to_imgs
)
from services.storage_service import (
    download_pdf_from_telegram_tmp,
    save_imgs_tmp,

    delete_file_tmp,

    get_data_table_DB,
    set_data_table_DB,
    update_data_table_DB,

    upload_images
)
from services.permission_service import require_permission



# navigation
from navigation.screens import show_exercises


# permission
from permission.constants import Role






MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

router = Router()


# helper functions
async def process_one(msg, state): # Upload + (Extraction + Normalization) + Duplication

    data = await state.get_data()
    pdf_file = data["pdf_file"]
    navigation = data["navigation"]

    # Extract Text from PDF (pdfminer)
    text = extract_text_PDF(pdf_file["path"])
    
    if not text or not text.strip():  # اتعامل مع النص فقط في البداية
        await msg.answer(
            "❌ لا يحتوي ملف PDF على نص.\n"
            "يرجى رفع ملف آخر أو استخدم /Cancel."
        )
        delete_file_tmp(pdf_file["path"])
        return

    await msg.answer("✅ PDF accepted.")


    # Normalization TXT
    normalize_text = normalize_text_PDF(text)

    await state.update_data(normalize_text=normalize_text)



    await msg.answer(
        "✅ تم استخراج البيانات من ملف PDF بنجاح.\n"
        "جارٍ الآن البحث عن التكرار... 🔍"
    )



    # get information from DB
    language = navigation["language"]
    
    exercises_table = await get_data_table_DB("exercises",{"language": language}) # same lang


    module_filter = {
        "year": navigation["year"],
        "specialty": navigation["specialty"],
        "module_name": navigation["module"]
    }

    modules_table = await get_data_table_DB("modules", module_filter) # data rows with this filter
    if modules_table:
        module_id = modules_table[0]["id"]
    else:
        new_module = await set_data_table_DB("modules", module_filter)

        module_id = new_module["id"]

    await state.update_data(module_id=module_id)
    
    

    

    # Similarity exercise

    # step 1 (get exos)
    candidates = []
    for ex in exercises_table:

        db_text = ex["normalized_text"]

        score = similarity_score(normalize_text, db_text)

        if score >= 85:

            candidates.append({
                "id": ex["id"],
                "score": score
            })
    

    # step 2 (sort exos)
    candidates.sort(key=lambda x: x["score"], reverse=True)


    # step 3 (show exo img with confirmation[yes][no]) or (cont proccess PDF)
    if candidates:

        candidate = candidates[0]

        await state.update_data(
            candidates=candidates,
            current_index=0,
        )
        

        await show_exo_imgs_to_user(msg, candidate["id"])
        await comfirmation_exo(msg, candidate)
    else:
        await msg.answer(
            "✅ لم يتم العثور على تمرين مشابه.\n"
            "سيتم إنشاء تمرين جديد.\n"
            "جارٍ معالجة ملف PDF..."
        )
        await process_two(msg, state)

async def process_two(msg, state): # PDF to IMGs + Storage exo in DB
    
    data = await state.get_data()

    pdf_file = data["pdf_file"]
    navigation = data["navigation"]
    normalize_text = data["normalize_text"]
    module_id = data["module_id"]

    created_by = data["telegram_id"]


    
    # Convert pdf to imgs
    pdf_path = pdf_file["path"]
    # print(f"pdf_path outside fun: {pdf_path}")
    images = await convert_pdf_to_imgs(msg=msg, pdf_path=pdf_file["path"])


    
    # save imgs tmp
    name_folder = pdf_file["file_name"]

    imgs_files_tmp = save_imgs_tmp(images=images, name_folder=name_folder)
    if not imgs_files_tmp:
        await msg.answer(
            "❌ لم يتم إنشاء أي صور من ملف PDF.\n"
            "يرجى رفع الملف مرة أخرى أو استخدم /Cancel."
        )
        delete_file_tmp(pdf_file["path"])
        return

    

    # Storage in exercises table
    language = navigation["language"]
    year = navigation["year"]
    specialty = navigation["specialty"]
    module = navigation["module"]

    new_exercise = await set_data_table_DB(
        "exercises",
        {
            "language": language,
            "normalized_text": normalize_text,
            "created_by": created_by
            
        }
    )


    # Storage in module_exercises table
    await set_data_table_DB(
        "module_exercises",
        {
            "module_id": module_id,
            "exercise_id": new_exercise["id"]
        }
    )


    # Storage images in storage and save links in exercise_images table
    paths_imgs = await upload_images(name_folder=name_folder, exercise_id=new_exercise["id"])
    
    for c, img in enumerate(paths_imgs, start=1):
        await set_data_table_DB(
            "exercise_images",
            {
                "exercise_id": new_exercise["id"], 
                "image_url": img,
                "image_order": c,
            }
        )


    
    # update last_active
    await update_data_table_DB(
        table_name="users",
        data={"last_active": datetime.now(timezone.utc).isoformat()},
        filter_by_column={"telegram_id": created_by}
    )


    # Finish + Delete everything + Back to choose exrcises 
    await msg.answer("✅✅✅✅✅✅✅✅✅✅✅")

    delete_file_tmp(pdf_file["path"])
    for img in imgs_files_tmp:
        delete_file_tmp(img)

    await state.update_data(
        navigation=None,
        pdf_file=None,
        normalize_text=None,
        module_id=None,
        candidates=None,
        current_index=None
    )

    dis_of_exos = data["dis_of_exos"]
    await state.set_state(ActionStates.choose_exercise)
    await show_exercises(msg, dis_of_exos.keys())






# ===============================================================================

@router.message(ActionStates.choose_exercise, F.text == "➕ Add exercise")
async def add_exercise(msg: types.Message, state: FSMContext):
    

    # check the permission
    allowed, error = await require_permission(msg.from_user.id, Role.ADDER_EXERCISE)

    if not allowed:

        await msg.answer(error)
        return




    # Code

    data = await state.get_data()

    language = data["language"]
    year = data["year"]
    specialty = data["specialty"]
    module = data["module"]

    if not all([language, year, specialty, module]):
        await msg.answer("❌ يرجى إكمال خطوات التنقل أولًا (اللغة، السنة، التخصص، المادة).")
        return

    navigation = {
        "language": language,
        "year": year,
        "specialty": specialty,
        "module": module
    }

    await state.update_data(navigation=navigation)


    await msg.answer(
        "📄 أرسل ملف PDF يحتوي على تمرين واحد.\n"
        "====================================\n"
        "الشروط:\n"
        "1. يجب أن يكون الملف بصيغة PDF.\n"
        f"2. يجب ألا يتجاوز الحجم {MAX_FILE_SIZE / (1024 * 1024)} ميجابايت.\n"
        "3. يجب أن يحتوي ملف PDF على طبقة نصية.\n"
        "4. يجب أن يحتوي على تمرين واحد فقط.\n\n"

        "للإلغاء، أرسل:\n"
        "/Cancel",
        
        reply_markup=types.ReplyKeyboardRemove(),

        parse_mode=None
    )

    await state.set_state(ActionStates.waiting_pdf_to_add_exo)


@router.message(Command("Cancel"), ActionStates.waiting_pdf_to_add_exo)
async def cancel(msg: types.Message, state: FSMContext):
    
    await msg.answer("❌ تم إلغاء عملية إضافة التمرين.")

    # Clear everthing

    data = await state.get_data()
    
    await state.update_data(
        navigation=None,
        pdf_file=None,
        normalize_text=None,
        module_id=None,
        candidates=None,
        current_index=None
    )

    dis_of_exos = data["dis_of_exos"]
    await state.set_state(ActionStates.choose_exercise)
    await show_exercises(msg, dis_of_exos.keys())


    
@router.message(ActionStates.waiting_pdf_to_add_exo)
async def processing_PDF(msg: types.Message, state: FSMContext):


    # Validate type
    if not msg.document or msg.document.mime_type != "application/pdf":
        await msg.answer(
            "❌ يرجى إرسال ملف PDF.\n"
            "يرجى رفع الملف مرة أخرى أو استخدم /Cancel."
        )
        return
    
    # validate size
    if msg.document.file_size > MAX_FILE_SIZE:
        await msg.answer(
            f"❌ حجم ملف PDF يتجاوز الحد المسموح ({MAX_FILE_SIZE / (1024 * 1024)} ميجابايت).\n"
            "يرجى رفع الملف مرة أخرى أو استخدم /Cancel."
        )
        return
    

    # Download PDF tmp
    pdf_file = await download_pdf_from_telegram_tmp(msg) # { "path" , "file_name" } 
    await msg.answer("✅ تم استلام ملف PDF بنجاح.")

    await state.update_data(pdf_file=pdf_file)



    await msg.answer("⏳ يرجى الانتظار، جارٍ معالجة ملف PDF...")

    await process_one(msg, state)



@router.callback_query(F.data.startswith("ex_yes:"))
async def yes_handler(callback: types.CallbackQuery, state: FSMContext):
    
    await callback.answer()

    exercise_id = int(callback.data.split(":")[1])

    data = await state.get_data()

    if not data:
        await callback.answer(
            "Session expired",
            show_alert=True
        )
        return

    module_id = data["module_id"]

    module_exercises_filter = {"module_id": module_id, "exercise_id": exercise_id}

    row = await get_data_table_DB("module_exercises", module_exercises_filter)
    if row:
        await callback.message.answer("ℹ️ التمرين موجود مسبقًا، لذلك لن تتم إضافته مرة أخرى.")
        
    else:
        await set_data_table_DB("module_exercises",module_exercises_filter)
        await callback.message.answer("✅ تم ربط التمرين بالمادة بنجاح.")
    


    # update last_active
    await update_data_table_DB(
        table_name="users",
        data={"last_active": datetime.now(timezone.utc).isoformat()},
        filter_by_column={"telegram_id": callback.from_user.id}
    )


    # Finish + Delete everything + Back to choose exrcises 
    pdf_file = data["pdf_file"]

    delete_file_tmp(pdf_file["path"])

    await state.update_data(
        navigation=None,
        pdf_file=None,
        normalize_text=None,
        module_id=None,
        candidates=None,
        current_index=None
    )

    dis_of_exos = data["dis_of_exos"]
    await state.set_state(ActionStates.choose_exercise)
    await show_exercises(callback.message, dis_of_exos.keys())

    return


@router.callback_query(F.data.startswith("ex_no:"))
async def no_handler(callback: types.CallbackQuery, state: FSMContext):

    await callback.answer()

    data = await state.get_data()

    if not data:
        await callback.answer(
            "Session expired",
            show_alert=True
        )
        return

    candidates = data["candidates"]
    current_index = data["current_index"] + 1

    
    if current_index >= len(candidates):

        await callback.message.answer(
            "✅ لم يتم العثور على أي تمرين مطابق.\n"
            "سيتم إنشاء تمرين جديد.\n"
            "جارٍ متابعة معالجة ملف PDF..."
        )

        await process_two(callback.message, state)

        return

    candidate = candidates[current_index]

    await state.update_data(
        current_index=current_index
    )


    await show_exo_imgs_to_user(callback.message, candidate["id"])
    await comfirmation_exo(callback.message, candidate)








