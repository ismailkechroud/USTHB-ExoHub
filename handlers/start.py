# .venv
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

# states
from states.NavigationStates import NavigationStates

# keyboards
from keyboards.replykeyboard import languages_btn




router = Router()
@router.message(CommandStart())
async def start(msg: types.Message, state: FSMContext):
    
    await state.clear()

    telegram_id = msg.from_user.id # بعدها اعدله عندما اضيف نظام صلحيات
    await state.update_data(telegram_id=telegram_id)
    

    
    await state.set_state(NavigationStates.language)

    await msg.answer(
        "🔄 البدء من جديد.\n"
        "اختر لغة التمارين",
        parse_mode=ParseMode.HTML,
        reply_markup=languages_btn(),
    )


