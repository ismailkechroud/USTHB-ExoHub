from datetime import datetime, timezone

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command


# states
from states.ActionStates import ActionStates

# services
from services.storage_service import download_img_from_telegram_tmp, set_data_table_DB, update_data_table_DB, delete_file_tmp
from services.exercise_service import send_solution_to_channel
from services.permission_service import require_permission



# navigation
from navigation.screens import show_currently


# permission
from permission.constants import Role





MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

router = Router()



@router.callback_query(F.data.startswith("add_solution:"))
async def add_solution(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()


    # check the permission
    allowed, error = await require_permission(callback.from_user.id, Role.ADDER_SOLUTION)

    if not allowed:
        await callback.answer()

        await callback.message.answer(error)
        return


    
    # Code

    exercise_id = int(callback.data.split(":")[1])

    currently_state = await state.get_state()

    await state.update_data(
        exercise_id=exercise_id,
        paths=[],

        currently_state=currently_state
    )

    await state.set_state(ActionStates.waiting_img)


    await callback.message.answer(
        f"📤 أرسل صور حل التمرين رقم #{exercise_id}.\n"
        "عند الانتهاء أرسل /Done.\n"
        "وللإلغاء أرسل /Cancel.",

        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode=None
    )




@router.message(Command("Cancel"), ActionStates.waiting_img)
async def cancel(msg: types.Message, state: FSMContext):
    
    await msg.answer("❌ تم إلغاء عملية إضافة حل.")


    # Clear everthing

    data = await state.get_data()

    paths = data["paths"]
    
    for path in paths:
        delete_file_tmp(path)


    await show_currently(msg, state)
        
    await state.update_data(
        exercise_id=None,
        paths=None,
        currently_state=None
    )




@router.message(Command("Done"), ActionStates.waiting_img)
async def finish_upload(msg: types.Message, state: FSMContext):

    data = await state.get_data()

    exercise_id = data["exercise_id"]
    paths = data["paths"]

    if not paths:

        await msg.answer(
            "❌ لم يتم رفع أي صور.\n\n"
            "تم إلغاء عملية إضافة الحل.\n"
            "اضغط على ➕ إضافة حل للبدء من جديد.\n"
            "أو..."
        )

        await show_currently(msg, state)

        await state.update_data(
            exercise_id=None,
            paths=[],
            currently_state=None
        )
        

        return
    
    await msg.answer("📝 أكتب وصفًا لهذا الحل.")
    
    await state.set_state(ActionStates.waiting_caption)


    

    

@router.message(ActionStates.waiting_caption)
async def build_caption_and_send_to_channel(msg: types.Message, state: FSMContext):

    await msg.answer("⏳ جارٍ نشر الحل في القناة...")


    data = await state.get_data()

    language_tag = (data.get("language") or "").replace(" ", "_")
    year_tag = (data.get("year") or "").replace(" ", "_")
    specialty_tag = (data.get("specialty") or "").replace(" ", "_")
    module_tag = (data.get("module") or "").replace(" ", "_")


    hashtags = "\n".join(
        f"▶️ {tag}"
        for tag in [
            language_tag,
            year_tag,
            specialty_tag,
            module_tag,
        ]
        if tag
    )



    description = msg.text
    user = f"{msg.from_user.full_name}"

    caption = (
        f"👤 المساهم: {user}\n\n"

        f"📝 الوصف:\n{description}\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        f"{hashtags}\n\n"

        "الصور ⏬⏬⏬"
    )
    
    
    paths = data["paths"]
    exercise_id = data["exercise_id"]

    post_link = await send_solution_to_channel(msg=msg, paths=paths, caption=caption)
    added_by = msg.from_user.id

    await set_data_table_DB(
        table_name="solutions",
        data={"exercise_id": exercise_id, "telegram_post_link": post_link, "added_by": added_by}
    )

    await msg.answer("✅ تم نشر الحل بنجاح.")



    # update last_active
    await update_data_table_DB(
        table_name="users",
        data={"last_active": datetime.now(timezone.utc).isoformat()},
        filter_by_column={"telegram_id": added_by}
    )
    
    # Clear everthing
    for path in paths:
        delete_file_tmp(path)

    await show_currently(msg, state)
        
    await state.update_data(
        exercise_id=None,
        paths=None,
        currently_state=None
    )



@router.message(ActionStates.waiting_img, F.photo | F.document)
async def receive_img(msg: types.Message, state: FSMContext):
    

    # Validate type
    if not (msg.photo or (msg.document and msg.document.mime_type.startswith("image/"))):

        await msg.answer(
            "❌ يرجى إرسال الصور فقط.\n\n"
            "تم إلغاء عملية إضافة الحل.\n"
            "اضغط على ➕ إضافة حل للبدء من جديد.\n"
            "أو..."
        )  

        await show_currently(msg, state)
        
        await state.update_data(
            exercise_id=None,
            paths=[],
            currently_state=None
        )

        return
    

    # validate size
    if msg.photo:
        file_size = msg.photo[-1].file_size
    else:
        file_size = msg.document.file_size

    if file_size > MAX_FILE_SIZE:

        await msg.answer(
            f"❌ حجم الصورة كبير جدًا. يجب ألا يتجاوز {MAX_FILE_SIZE / (1024 * 1024)} ميجابايت.\n\n"
            "تم إلغاء عملية إضافة الحل.\n"
            "اضغط على ➕ إضافة حل للبدء من جديد.\n"
            "أو..."
        )

        await show_currently(msg, state)
        
        await state.update_data(
            exercise_id=None,
            paths=[],
            currently_state=None
        )

        return




    path = await download_img_from_telegram_tmp(msg=msg)
    
    data = await state.get_data()
    paths = data.get("paths", [])

    paths.append(path)

    await state.update_data(paths=paths)
    
