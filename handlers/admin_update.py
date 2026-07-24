from datetime import datetime, timedelta, timezone

from aiogram import Router, types
from aiogram.filters import Command

from services.storage_service import (
    get_data_table_DB,
    update_data_table_DB,
)

from permission.constants import (
    Role,
    Status,
)


router = Router()

MAX_INACTIVE_DAYS = 1


@router.message(Command("update"))
async def update_users_status(msg: types.Message):

    # استخرج فقط المستخدمين النشطين
    users = await get_data_table_DB(
        table_name="users",
        filter_by_column={
            "status": Status.ACTIVE
        }
    )

    checked = 0
    updated = 0

    limit_date = datetime.now(timezone.utc) - timedelta(days=MAX_INACTIVE_DAYS)

    for user in users:

        # تجاهل الأدمن
        if user["role"] == Role.ADMIN:
            continue

        checked += 1

        telegram_id = user["telegram_id"]

        # إذا لم يكن لديه آخر نشاط نتجاوزه
        if not user["last_active"]:
            continue

        last_active = datetime.fromisoformat(
            user["last_active"].replace("Z", "+00:00")
        )

        # إذا تجاوز الحد نحوله إلى Inactive
        if last_active < limit_date:

            await update_data_table_DB(
                table_name="users",
                data={
                    "status": Status.INACTIVE
                },
                filter_by_column={
                    "id": user["id"]
                }
            )

            updated += 1

    await msg.answer(
        "✅ <b>Update Completed</b>\n\n"
        f"👥 Checked: <b>{checked}</b>\n"
        f"♻️ Updated: <b>{updated}</b>",
        parse_mode="HTML"
    )