from services.storage_service import (
    get_data_table_DB,
    set_data_table_DB,
    update_data_table_DB,
    delete_data_table_DB,
)

from permission.constants import Role, Status




# ==========================
# Get
# ==========================

async def get_user(telegram_id: int):

    users = await get_data_table_DB(
        "users",
        {"telegram_id": telegram_id}
    )

    return users if users else None

async def get_ban(telegram_id: int) -> dict | None:

    banned = await get_data_table_DB(
        "banned_users",
        {"telegram_id": telegram_id}
    )

    return banned[0] if banned else None



# ==========================
# Check
# ==========================


async def require_permission(
    telegram_id: int,
    required_role: str
) -> tuple[bool, str | None]:

    users = await get_user(telegram_id)

    if required_role == Role.ADDER_EXERCISE:
        request_command = "/add_exercise"
        status_command = "/status_exercise"
        feature = "إضافة التمارين"

    elif required_role == Role.ADDER_SOLUTION:
        request_command = "/add_solution"
        status_command = "/status_solution"
        feature = "إضافة الحلول"

    # المستخدم غير موجود
    if users is None:
        return (
            False,
            f"❌ ليس لديك صلاحية {feature}.\n\n"
            "إذا كنت ترغب في المساهمة في المشروع، يمكنك إرسال طلب باستعمال:\n"
            f"{request_command}"
        )

    # الأدمن يملك جميع الصلاحيات
    for user in users:
        if user["role"] == Role.ADMIN:
            return True, None

    # البحث عن الصلاحية المطلوبة
    for user in users:

        if user["role"] != required_role:
            continue

        # وجدنا الصلاحية المطلوبة
        if user["status"] == Status.ACTIVE:
            return True, None

        # لديه الصلاحية لكنها غير نشطة
        return (
            False,
            "❌ لديك صلاحية، لكن حالتك غير نشطة.\n\n"
            "يمكنك إرسال طلب تجديد الحالة باستعمال:\n"
            f"{status_command}"
        )

    # لم نجد الصلاحية المطلوبة
    return (
        False,
        f"❌ ليس لديك صلاحية {feature}.\n\n"
        "إذا كنت ترغب في المساهمة في المشروع، يمكنك إرسال طلب باستعمال:\n"
        f"{request_command}"
    )


# ==========================
# Create
# ==========================

async def create_user(telegram_id: int, username: str | None, full_name: str, role: str, status: str) -> dict:
    
    return await set_data_table_DB(
        "users",
        {
            "telegram_id": telegram_id,
            "username": username,
            "full_name": full_name,
            "role": role,
            "status": status,
        },
    )




# ==========================
# Update
# ==========================

async def change_role(telegram_id: int, role: str):

    await update_data_table_DB(
        "users",
        {"role": role},
        {"telegram_id": telegram_id}
    )

async def change_status(telegram_id: int, status: str):

    await update_data_table_DB(
        "users",
        {"status": status},
        {"telegram_id": telegram_id}
    )





# ==========================
# Ban
# ==========================

async def ban_user(telegram_id: int, reason: str) -> list:

    row = await set_data_table_DB(
        "banned_users",
        {"telegram_id": telegram_id, "reason": reason,}
    )
    
    return row

async def unban_user(telegram_id: int) -> bool:

    done = await delete_data_table_DB(
        "banned_users",
        {"telegram_id": telegram_id}
    )

    return done