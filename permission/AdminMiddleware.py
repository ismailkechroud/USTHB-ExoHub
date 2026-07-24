from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from services.permission_service import get_user
from permission.constants import Role


class AdminMiddleware(BaseMiddleware):

    async def __call__(self, handler, event, data):

        user = await get_user(event.from_user.id)
        user = user[0]
        
        if user is None or user["role"] != Role.ADMIN:

            if isinstance(event, Message):
                await event.answer(
                    "⛔ ليس لديك صلاحية لاستخدام هذا البوت."
                )

            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "⛔ ليس لديك صلاحية.",
                    show_alert=True,
                )

            return

        return await handler(event, data)