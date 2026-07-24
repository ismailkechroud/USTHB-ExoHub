
from aiogram.fsm.state import State, StatesGroup

class ActionStates(StatesGroup):

    choose_action = State()

    choose_exercise = State()

    waiting_pdf_to_search = State()
    waiting_pdf_to_add_exo = State()

    waiting_img = State()

    waiting_caption = State()
