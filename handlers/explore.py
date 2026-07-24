from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

# states
from states.ActionStates import ActionStates


# services
from services.storage_service import get_data_table_DB
from services.exercise_service import show_exo_imgs_to_user, show_solutions_of_exo_to_user, get_exercises_of_module

# navigation
from navigation.screens import show_exercises

router = Router()



# Explore (fetch exercises)
@router.message(ActionStates.choose_action, F.text == "Explore")
async def explore_start(msg: types.Message, state: FSMContext):
    
    data = await state.get_data()

    language = data["language"]
    year = data["year"]
    specialty = data["specialty"]
    module = data["module"]
    

    
    dis_of_exos = await get_exercises_of_module(language, year, specialty, module)
    if not dis_of_exos:
        await msg.answer("❌ لم يتم العثور على أي تمارين.")
        

    await state.update_data(dis_of_exos=dis_of_exos)
    await state.set_state(ActionStates.choose_exercise)
    
    await show_exercises(msg, dis_of_exos.keys())
        




# Choose exercise + show images with solutions btns
@router.message(ActionStates.choose_exercise, F.text, (F.text != "⬅️ Back") & (F.text != "➕ Add exercise"))
async def choose_exercise(msg: types.Message, state: FSMContext):

    choice = msg.text.replace("Exo ", "").strip() # get just number "Exo 1 -> 1"

    data = await state.get_data()
    dis_of_exos = data.get("dis_of_exos", {})

    if choice not in dis_of_exos:
        await msg.answer("❌ التمرين غير صالح.")
        return

    exo = dis_of_exos[choice]
    

    # Show Exo with solutions
    await show_exo_imgs_to_user(msg, exo["id"])
    await show_solutions_of_exo_to_user(msg, exo["id"])

    