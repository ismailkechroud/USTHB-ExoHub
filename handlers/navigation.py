from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

# keyboards
from keyboards.replykeyboard import (
    explore_search_btn,
    addExo_addSolution_btn,

    languages_btn,
    years_btn,
    specialties_btn,
    modules_btn
)


# navigations
from navigation.data import (
    main_navigate as DATA,
    languages_navigate as languages
)
from navigation.screens import (
    show_languages,
    show_years,
    show_specialties,
    show_modules,
    show_exercises,

    show_actions
)
from navigation.flow import BACK_STATE


# states
from states.NavigationStates import NavigationStates
from states.ActionStates import ActionStates


router = Router()



# Choose language
@router.message(NavigationStates.language, F.text != "⬅️ Back", ~F.document)
async def choose_language(msg: types.Message, state: FSMContext):
    language = msg.text

    if language not in languages:
        await msg.answer(
            f"❌ لا توجد لغة باسم \"{language}\".\n"
            "يرجى الاختيار مرة أخرى."
        )
        return

    await state.update_data(language=language)
    await state.set_state(NavigationStates.year)

    await show_years(msg)




# Choose year
@router.message(NavigationStates.year, F.text != "⬅️ Back", ~F.document)
async def choose_year(msg: types.Message, state: FSMContext):
    year = msg.text

    years = DATA.keys()

    if year not in years:
        await msg.answer(
            f"❌ لا توجد سنة باسم \"{year}\".\n"
            "يرجى اختيار سنة أخرى."
        )
        return

    await state.update_data(year=year)
    await state.set_state(NavigationStates.specialty)

    await show_specialties(msg, year)



# Choose specialty
@router.message(NavigationStates.specialty, F.text != "⬅️ Back", ~F.document)
async def choose_specialty(msg: types.Message, state: FSMContext):
    specialty = msg.text

    data = await state.get_data()
    year = data["year"]

    specialties = DATA[year].keys()

    if specialty not in specialties:
        await msg.answer(
            f"❌ لا يوجد تخصص باسم \"{specialty}\" ضمن السنة \"{year}\".\n"
            "يرجى الاختيار مرة أخرى."
        )
        return

    await state.update_data(specialty=specialty)
    await state.set_state(NavigationStates.module)

    await show_modules(msg, year, specialty)



# Choose module
@router.message(NavigationStates.module, F.text != "⬅️ Back", ~F.document)
async def choose_module(msg: types.Message, state: FSMContext):
    module = msg.text

    data = await state.get_data()

    year = data["year"]
    specialty = data["specialty"]

    modules = DATA[year][specialty]

    if module not in modules:
        await msg.answer(
            f"❌ لا توجد مادة باسم \"{module}\" ضمن السنة \"{year}\" والتخصص \"{specialty}\".\n"
            "يرجى الاختيار مرة أخرى."
        )
        return
    
    await state.update_data(module=module)
    await state.set_state(ActionStates.choose_action)

    await show_actions(msg)
    

    

# Back
@router.message(F.text == "⬅️ Back")
async def go_back(msg: types.Message, state: FSMContext):

    current = await state.get_state()

    previous = BACK_STATE.get(current)

    if previous is None:
        return

    data = await state.get_data()

    # إزالة آخر اختيار
    if previous == NavigationStates.language:
        data.pop("year", None)

    elif previous == NavigationStates.year:
        data.pop("specialty", None)

    elif previous == NavigationStates.specialty:
        data.pop("module", None)

    await state.set_data(data)
    await state.set_state(previous)

    # عرض الشاشة المناسبة
    if previous == NavigationStates.language:

        await show_languages(msg)

    elif previous == NavigationStates.year:

        await show_years(msg)

    elif previous == NavigationStates.specialty:

        await show_specialties(
            msg,
            data["year"]
        )

    elif previous == NavigationStates.module:

        await show_modules(
            msg,
            data["year"],
            data["specialty"]
        )

    elif previous == ActionStates.choose_action:

        await show_actions(msg)
        

    elif previous == ActionStates.choose_exercise: 

        await show_exercises(
            msg,
            data["dis_of_exos"].keys()
        )


