import asyncio
from aiogram import Dispatcher

from config_bot import admin_bot

from permission.AdminMiddleware import AdminMiddleware


# handlers of bot admin
from handlers.admin_request import router as admin_request_router
from handlers.admin_ban import router as admin_ban_router
from handlers.admin_update import router as admin_update_router


async def main():


    dp_admin = Dispatcher()


    # Bot admin
    dp_admin.message.middleware(AdminMiddleware())
    dp_admin.callback_query.middleware(AdminMiddleware())

    dp_admin.include_router(admin_request_router)
    dp_admin.include_router(admin_ban_router)
    dp_admin.include_router(admin_update_router)

    
    await dp_admin.start_polling(admin_bot)


if __name__ == "__main__":
    asyncio.run(main())