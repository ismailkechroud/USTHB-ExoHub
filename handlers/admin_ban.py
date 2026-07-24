from aiogram import Router, types
from aiogram.filters import Command

from services.permission_service import ban_user, unban_user

router = Router()


@router.message(Command("ban"))
async def ban(msg: types.Message):

    args = msg.text.split(maxsplit=2)

    if len(args) < 3:
        await msg.answer(
            "Usage:\n"
            "/ban <telegram_id> <reason>",
            parse_mode=None
        )
        return

    try:
        telegram_id = int(args[1])
    except ValueError:
        await msg.answer("❌ Telegram ID غير صالح.")
        return

    reason = args[2]

    success = await ban_user(
        telegram_id=telegram_id,
        reason=reason
    )

    if success:
        await msg.answer("✅ تم حظر المستخدم.")
    else:
        await msg.answer("⚠️ المستخدم محظور بالفعل.")


@router.message(Command("unban"))
async def unban(msg: types.Message):

    args = msg.text.split(maxsplit=1)

    if len(args) != 2:
        await msg.answer(
            "Usage:\n"
            "/unban <telegram_id>",
            parse_mode=None
        )
        return

    try:
        telegram_id = int(args[1])
    except ValueError:
        await msg.answer("❌ Telegram ID غير صالح.")
        return



    done = await unban_user(telegram_id)

    if done:
        await msg.answer("✅ تم فك الحظر.")
    
    else:
        await msg.answer("⚠️ المستخدم غير موجود في قائمة المحظورين.")