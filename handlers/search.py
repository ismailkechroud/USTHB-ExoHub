from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

# states
from states.ActionStates import ActionStates

# keyboards
from keyboards.replykeyboard import (
    back_btn
)


# services
from services.storage_service import (
    get_data_table_DB,
    download_pdf_from_telegram_tmp,
    delete_file_tmp
)
from services.exercise_service import (
    show_exo_imgs_to_user,
    show_solutions_of_exo_to_user,

    similarity_score,
    normalize_text_PDF,
    extract_text_PDF,

    get_exercises_of_module
)

# navigation
from navigation.screens import show_exercises





MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


router = Router()


@router.message(ActionStates.choose_action, F.text == "Search")
async def search(msg: types.Message, state: FSMContext):

    await state.set_state(ActionStates.waiting_pdf_to_search)

    await msg.answer(
        "📄 أرسل أو أعد توجيه ملف PDF يحتوي على تمرين واحد أو سلسلة تمارين.",
        reply_markup=back_btn()
    )




@router.message(ActionStates.waiting_pdf_to_search)
async def specific_search(msg: types.Message, state: FSMContext):

    # Validate type
    if not msg.document or msg.document.mime_type != "application/pdf":
        await msg.answer("❌ يرجى إرسال ملف بصيغة PDF فقط.")
        return
    
    # validate size
    if msg.document.file_size > MAX_FILE_SIZE:
        await msg.answer(f"❌ حجم ملف PDF يتجاوز الحد المسموح ({MAX_FILE_SIZE / (1024 * 1024)} ميجابايت).")
        return


    data = await state.get_data()

    language = data["language"]
    year = data["year"]
    specialty = data["specialty"]
    module = data["module"]

    await msg.answer(f"⏳ جارٍ البحث عن تمارين مادة \"{module}\"...")

    ######################### Specific Search

    # 1. get exercises of module
    dis_of_exos = await get_exercises_of_module(language, year, specialty, module)
    if not dis_of_exos:
        await msg.answer("❌ لم يتم العثور على أي تمرين مطابق.")
        return

    # 2. Download PDF
    pdf_file = await download_pdf_from_telegram_tmp(msg) # { "path" , "file_name" } 


    # 3. Extract text
    text = extract_text_PDF(pdf_file["path"])
    if not text or not text.strip():
        msg.answer("❌ ملف PDF لا يحتوي على نص قابل للاستخراج.")
        return


    # 4. Normalize
    normalize_text = normalize_text_PDF(text)


    # 5. Search only inside module_id
    matches = []
    for exo in dis_of_exos.values():
        db_text = exo["normalized_text"]

        score = similarity_score(db_text, normalize_text)

        if score >= 85:
            matches.append({
                "id": exo["id"],
                "score": score
            })
    



    # 6. Return matches
    if not matches:
        await msg.answer("❌ لم يتم العثور على أي تمرين مطابق.")
    
    else:
        matches.sort(key=lambda x: x["score"], reverse=True)

        for match in matches:

            # Show Exo with solutions
            exo_id = match["id"]
            await show_exo_imgs_to_user(msg, exo_id)
            await show_solutions_of_exo_to_user(msg, exo_id)


    # 7. Delete PDF tmp
    delete_file_tmp(pdf_file["path"])




@router.message(F.document.mime_type == "application/pdf")
async def global_search(msg: types.Message, state: FSMContext):

    # print("Hello")
    current_state = await state.get_state()

    
    if current_state in {ActionStates.waiting_pdf_to_search, ActionStates.waiting_pdf_to_add_exo}:
        return
    

    
    # Validate type
    if msg.document.mime_type != "application/pdf":
        return
    
    # validate size
    if msg.document.file_size > MAX_FILE_SIZE:
        return
    

    await msg.answer("⏳ جارٍ البحث عن التمارين، يرجى الانتظار...")

    ######################### Global Search

    # 1. Download PDF
    pdf_file = await download_pdf_from_telegram_tmp(msg) # { "path" , "file_name" } 


    # 2. Extract text
    text = extract_text_PDF(pdf_file["path"])
    if not text or not text.strip():
        msg.answer("❌ ملف PDF لا يحتوي على نص قابل للاستخراج.")
        return
    

    # 3. Normalize
    normalize_text = normalize_text_PDF(text)


    # 4. Search General
    exercises_table = await get_data_table_DB("exercises")

    matches = []
    for exo in exercises_table:
        db_text = exo["normalized_text"]

        score = similarity_score(db_text, normalize_text)

        if score >= 85:
            matches.append({
                "id": exo["id"],
                "score": score
            })
    

    if not matches:
        await msg.answer("❌ لم يتم العثور على أي تمرين.")
    
    else:
        matches.sort(key=lambda x: x["score"], reverse=True)

        for match in matches:

            # Show Exo with solutions
            exo_id = match["id"]
            await show_exo_imgs_to_user(msg, exo_id)
            await show_solutions_of_exo_to_user(msg, exo_id)
        

    # 5. Delete PDF tmp
    delete_file_tmp(pdf_file["path"])