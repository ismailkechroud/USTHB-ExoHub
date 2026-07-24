
from aiogram.fsm.state import State, StatesGroup

class NavigationStates(StatesGroup):

    language = State()
    year = State()
    specialty = State()
    module = State()
    
    