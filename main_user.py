import asyncio
from aiogram import Dispatcher

from config_bot import user_bot

from permission.BanMiddleware import BanMiddleware


# handlers of bot user
from handlers.start import router as start_router
from handlers.otherCommands import router as otherCommands_router

from handlers.navigation import router as navigation_router

from handlers.explore import router as explore_router
from handlers.search import router as search_router

from handlers.addExercise import router as addExercise_router
from handlers.addSolution import router as addSolution_router






async def main():


    dp_user = Dispatcher()


    # Bot user
    dp_user.message.middleware(BanMiddleware())
    dp_user.callback_query.middleware(BanMiddleware())
    
    dp_user.include_router(start_router)
    dp_user.include_router(otherCommands_router)

    dp_user.include_router(navigation_router)

    dp_user.include_router(addExercise_router)
    dp_user.include_router(addSolution_router)
    
    dp_user.include_router(explore_router)
    dp_user.include_router(search_router)


    
    await dp_user.start_polling(user_bot)


if __name__ == "__main__":
    asyncio.run(main())