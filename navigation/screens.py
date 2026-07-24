from aiogram import types
from aiogram.fsm.context import FSMContext

from keyboards.replykeyboard import (
    explore_search_btn,
    addExo_addSolution_btn,

    languages_btn,
    years_btn,
    specialties_btn,
    modules_btn,
    
    exercises_btn
)

from keyboards.inlinekeyboard import solutions_btn


# states
from states.NavigationStates import NavigationStates
from states.ActionStates import ActionStates

async def show_languages(msg: types.Message):
    await msg.answer(
        "اختر لغة التمارين",
        reply_markup=languages_btn()
    )

async def show_years(msg: types.Message):

    await msg.answer(
        "اختر السنة",
        reply_markup=years_btn()
    )

async def show_specialties(msg: types.Message, year: str):

    await msg.answer(
        "اختر التخصص",
        reply_markup=specialties_btn(year)
    )

async def show_modules(msg: types.Message, year: str, specialty: str):

    await msg.answer(
        "اختر المادة",
        reply_markup=modules_btn(year, specialty)
    )


async def show_actions(msg: types.Message):

    await msg.answer(
        "ماذا تريد؟",
        reply_markup=explore_search_btn()
    )


async def show_exercises(msg: types.Message, exercises: str):

    await msg.answer(
        "اختر التمرين",
        reply_markup=exercises_btn(exercises)
    )


async def show_solutions(msg: types.Message, telegram_post_links, id_exo):

    await msg.answer(
        text="————— 📌 Solutions —————",
        reply_markup=solutions_btn(telegram_post_links, id_exo=id_exo)
    )













async def show_currently(msg: types.Message, state: FSMContext):

    data = await state.get_data()
    currently_state = data["currently_state"]

    await state.set_state(currently_state)

    if currently_state == NavigationStates.language:

        await show_languages(msg)

    elif currently_state == NavigationStates.year:

        await show_years(msg)

    elif currently_state == NavigationStates.specialty:

        await show_specialties(
            msg,
            data["year"]
        )

    elif currently_state == NavigationStates.module:

        await show_modules(
            msg,
            data["year"],
            data["specialty"]
        )

    elif currently_state == ActionStates.choose_action:

        await show_actions(msg)
        

    elif currently_state == ActionStates.choose_exercise: 

        await show_exercises(
            msg,
            data["dis_of_exos"].keys()
        )

