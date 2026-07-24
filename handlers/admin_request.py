from aiogram import Router, F, types
from aiogram.filters import Command

from config_bot import user_bot

from services.permission_service import (
    create_user,
    change_status,
)


# keyboards
from keyboards.inlinekeyboard import accept_reject_btn

# storages
from services.storage_service import get_data_table_DB, delete_data_table_DB

from permission.constants import Status, Role, Request


router = Router()






######## Helper functions

async def send_request_to_admin(
    msg: types.Message,

    telegram_id: int,
    username: str,
    full_name: str,

    role: str,
    request_type: str,      # "permission" | "status_renewal"
    status: str = Status.ACTIVE,
):


    title = (
        "📩 <b>New Permission Request</b>"
        if request_type == "permission"
        else "♻️ <b>New Status Renewal Request</b>"
    )

    label = (
        "Requested Permission"
        if request_type == "permission"
        else "Requested Status"
    )

    request_name = (
        "Add Exercise"
        if role == Role.ADDER_EXERCISE
        else "Add Solution"
    )

    text = (
        f"{title}\n\n"

        f"👤 <b>Name:</b> {full_name}\n"
        f"📛 <b>Username:</b> {username}\n"
        f"🆔 <b>Telegram ID:</b> <code>{telegram_id}</code>\n\n"

        f"📌 <b>{label}:</b>\n"
        f"➕ {request_name}"
    )

    await msg.answer(
        text,
        parse_mode="HTML",
        reply_markup=accept_reject_btn(
            telegram_id=telegram_id,
            role=role,
            request_type=request_type,
            status=status
        )
    )















@router.message(Command("get_requests"))
async def get_requests(msg: types.Message):
    
    requests = await get_data_table_DB("pending_requests")

    if not requests:
        await msg.answer("لا يوجد طلبات حاليا")
        return

    
    for req in requests:
        

        if req["request_type"] == Request.PERMISSION:

            await send_request_to_admin(
                msg=msg,
                telegram_id=req["telegram_id"],
                username=req["username"],
                full_name=req["full_name"],
                role=req["role"],
                request_type=req["request_type"],

            )
        
        else:

            await send_request_to_admin(
                msg=msg,
                telegram_id=req["telegram_id"],
                username=req["username"],
                full_name=req["full_name"],
                role=req["role"],
                request_type=req["request_type"],
                status=Status.INACTIVE

            )
        




@router.callback_query(F.data.startswith("accept") | F.data.startswith("reject"))
async def handle_request(callback: types.CallbackQuery):
    await callback.answer()


    action, data = callback.data.split(" ", 1)

    request_type, telegram_id, role = data.split(":")

    
    telegram_id = int(telegram_id)

    accepted = action == "accept"

    # print(f"request:  {action} : {data} \n {request_type} : {telegram_id} : {role} \n {accepted}")


    users = await get_data_table_DB(   # this will return just one user
        table_name="pending_requests",
        filter_by_column={
            "telegram_id": telegram_id,
            "request_type": request_type,
            "role": role,
        }
    )
    

    if not users:
        await callback.message.answer("الطلب غير موجود.", show_alert=True)
        return

    user = users[0]

    username = user["username"]
    full_name = user["full_name"]
    


    feature = (
        "إضافة التمارين"
        if role == Role.ADDER_EXERCISE
        else "إضافة الحلول"
    )


    # ==========================
    # ACCEPT
    # ==========================

    if accepted:

        if request_type == "permission":

            text = (
                "✅ تم قبول طلب الصلاحية.\n"
                f"يمكنك الآن {feature}."
            )
            

            await create_user(
                telegram_id=telegram_id,
                username=username,
                full_name=full_name,
                role=role,
                status=Status.ACTIVE
            )


        else:   # status

            text = (
                "✅ تم تجديد حالتك.\n"
                f"يمكنك الآن {feature}."
            )

            await change_status(telegram_id,Status.ACTIVE)



    # ==========================
    # REJECT
    # ==========================

    else:

        if request_type == "permission":

            text = f"❌ تم رفض طلب الصلاحية لـ {feature}."
            

        else: # Status

            text = f"❌ تم رفض طلب تجديد الحالة لـ {feature}."
            

            



    # ==========================
    # Delete Pending Request
    # ==========================

    await delete_data_table_DB(
        "pending_requests",
        {
            "telegram_id": telegram_id,
            "request_type": request_type,
            "role": role,
        }
    )


    # ==========================
    # Notify User
    # ==========================

    await user_bot.send_message(
        telegram_id,
        text
    )


    # ==========================
    # Remove Admin Message
    # ==========================


    await callback.message.delete()


    # print("Done ✅")

