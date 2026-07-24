from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from services.permission_service import get_ban


class BanMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:

        user = data.get("event_from_user")

        if user is None:
            return await handler(event, data)

        ban = await get_ban(user.id)

        if ban:

            text = (
                "🚫 <b>لقد تم حظر حسابك من استخدام USTHB ExoHub.</b>\n\n"
                f"📌 <b>السبب:</b>\n{ban['reason']}"
            )

            if isinstance(event, Message):
                await event.answer(text)

            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "🚫 أنت محظور من استخدام البوت.",
                    show_alert=True,
                )

                await event.message.answer(text)

            return

        return await handler(event, data)