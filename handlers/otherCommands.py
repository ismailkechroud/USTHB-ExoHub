from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command


# services
from services.permission_service import get_user
from services.storage_service import get_data_table_DB, set_data_table_DB

# keyboards
from keyboards.inlinekeyboard import accept_reject_btn

# permission
from permission.constants import Role, Status, Request



router = Router()



############ helper functions

async def has_pending_request(
    telegram_id: int,
    request_type: str,
    role: str,
) -> tuple[bool, str | None]:

    request = await get_data_table_DB(
        "pending_requests",
        {
            "telegram_id": telegram_id,
            "request_type": request_type,
            "role": role,
        },
    )

    if request:
        return (
            True,
            "❌ لديك طلب قيد المراجعة بالفعل.\n"
            "يرجى انتظار رد المشرف.",
        )

    return (
        False,
        None,
    )












############ Handlers

@router.message(Command("add_exercise"))
async def request_permission_to_add_exercise(msg: types.Message):

    users = await get_user(msg.from_user.id)

    if users is not None:
        for user in users:

            if user["role"] == Role.ADMIN:
                await msg.answer("👑 أنت مدير، ولا تحتاج إلى صلحيات.")
                return
            
            if user["role"] == Role.ADMIN or user["role"] == Role.ADDER_EXERCISE:
                await msg.answer("✅ لديك صلاحية إضافة التمارين بالفعل.")
                return



    pending, error = await has_pending_request(msg.from_user.id, Request.PERMISSION , Role.ADDER_EXERCISE)

    if pending:
        await msg.answer(error)
        return

    
    username = (
        f"@{msg.from_user.username}"
        if msg.from_user.username
        else "None"
    )
    Order = {
        "telegram_id": msg.from_user.id,
        "username": username,
        "full_name": msg.from_user.full_name,
        "request_type": Request.PERMISSION,
        "role": Role.ADDER_EXERCISE,
    }


    await set_data_table_DB(table_name="pending_requests", data=Order)

    await msg.answer(
        "✅ تم إرسال طلبك إلى المشرف.\n"
        "سيتم مراجعته قريبًا."
    )


@router.message(Command("status_exercise"))
async def request_status_renewal_to_add_exercise(msg: types.Message):

    users = await get_user(msg.from_user.id)


    # البحث عن صلاحية إضافة التمارين
    has_permission = False

    if users is not None:

        for user in users:

            if user["role"] == Role.ADMIN:
                await msg.answer("👑 أنت مدير، ولا تحتاج إلى تجديد الحالة.")
                return

            if user["role"] != Role.ADDER_EXERCISE:
                continue

            has_permission = True

            if user["status"] == Status.ACTIVE:
                await msg.answer("✅ حالتك نشطة بالفعل.")
                return

            break

    # لا يملك هذه الصلاحية
    if not has_permission:
        await msg.answer(
            "❌ لا يمكنك تجديد حالتك لأنك لا تملك صلاحية إضافة التمارين.\n\n"
            "يمكنك طلب الصلاحية باستعمال:\n"
            "/add_exercise"
        )
        return

    

    pending, error = await has_pending_request(
        msg.from_user.id,
        Request.STATUS_RENEWAL,
        Role.ADDER_EXERCISE
    )

    if pending:
        await msg.answer(error)
        return

    username = (
        f"@{msg.from_user.username}"
        if msg.from_user.username
        else "None"
    )

    order = {
        "telegram_id": msg.from_user.id,
        "username": username,
        "full_name": msg.from_user.full_name,
        "request_type": Request.STATUS_RENEWAL,
        "role": Role.ADDER_EXERCISE,
    }

    await set_data_table_DB(
        table_name="pending_requests",
        data=order
    )

    await msg.answer(
        "✅ تم إرسال طلبك إلى المشرف.\n"
        "سيتم مراجعته قريبًا."
    )

# ===============================================================================

@router.message(Command("add_solution"))
async def request_permission_to_add_solution(msg: types.Message):

    users = await get_user(msg.from_user.id)

    if users is not None:
        for user in users:

            if user["role"] == Role.ADMIN:
                await msg.answer("👑 أنت مدير، ولا تحتاج إلى صلاحيات.")
                return

            if user["role"] == Role.ADDER_SOLUTION:
                await msg.answer("✅ لديك صلاحية إضافة حل بالفعل.")
                return




    pending, error = await has_pending_request(msg.from_user.id, Request.PERMISSION, Role.ADDER_SOLUTION)

    if pending:
        await msg.answer(error)
        return



    username = (
        f"@{msg.from_user.username}"
        if msg.from_user.username
        else "None"
    )
    Order = {
        "telegram_id": msg.from_user.id,
        "username": username,
        "full_name": msg.from_user.full_name,
        "request_type": Request.PERMISSION,
        "role": Role.ADDER_SOLUTION,
    }

    await set_data_table_DB(table_name="pending_requests", data=Order)

    await msg.answer(
        "✅ تم إرسال طلبك إلى المشرف.\n"
        "سيتم مراجعته قريبًا."
    )


@router.message(Command("status_solution"))
async def request_status_renewal_to_add_solution(msg: types.Message):

    users = await get_user(msg.from_user.id)

    

    # البحث عن صلاحية إضافة الحلول
    has_permission = False

    if users is not None:
        for user in users:

            if user["role"] == Role.ADMIN:
                await msg.answer("👑 أنت مدير، ولا تحتاج إلى تجديد الحالة.")
                return

            if user["role"] != Role.ADDER_SOLUTION:
                continue

            has_permission = True

            if user["status"] == Status.ACTIVE:
                await msg.answer("✅ حالتك نشطة بالفعل.")
                return

            break

    # لا يملك هذه الصلاحية
    if not has_permission:
        await msg.answer(
            "❌ لا يمكنك تجديد حالتك لأنك لا تملك صلاحية إضافة الحلول.\n\n"
            "يمكنك طلب الصلاحية باستعمال:\n"
            "/add_solution"
        )
        return


    pending, error = await has_pending_request(
        msg.from_user.id,
        Request.STATUS_RENEWAL,
        Role.ADDER_SOLUTION
    )

    if pending:
        await msg.answer(error)
        return

    username = (
        f"@{msg.from_user.username}"
        if msg.from_user.username
        else "None"
    )

    order = {
        "telegram_id": msg.from_user.id,
        "username": username,
        "full_name": msg.from_user.full_name,
        "request_type": Request.STATUS_RENEWAL,
        "role": Role.ADDER_SOLUTION,
    }

    await set_data_table_DB(
        table_name="pending_requests",
        data=order
    )

    await msg.answer(
        "✅ تم إرسال طلبك إلى المشرف.\n"
        "سيتم مراجعته قريبًا."
    )
