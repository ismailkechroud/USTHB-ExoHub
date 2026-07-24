
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from navigation.data import (
    main_navigate as DATA,
    languages_navigate as languages
)


# ============================================================= #
def explore_search_btn() -> ReplyKeyboardMarkup:

    items = ["Explore", "Search"]
    return _make_2col_reply_keyboard(items)

def addExo_addSolution_btn() -> ReplyKeyboardMarkup:

    items = ["Exercise", "Solution"]
    return _make_2col_reply_keyboard(items)



# ============================================================= #
def languages_btn() -> ReplyKeyboardMarkup:

    return _make_2col_reply_keyboard(languages, back=False)


def years_btn() -> ReplyKeyboardMarkup:
    
    years = list(DATA.keys())

    return _make_2col_reply_keyboard(years)


def specialties_btn(year: str) -> ReplyKeyboardMarkup:

    specialties = list(DATA[year].keys())
    
    return _make_2col_reply_keyboard(specialties)


def modules_btn(year: str, specialty: str) -> ReplyKeyboardMarkup:

    modules = list(DATA[year][specialty])

    return _make_2col_reply_keyboard(modules)



# ============================================================= #
def exercises_btn(exercises: list[int]) -> ReplyKeyboardMarkup:

    items = [f"Exo {exo}" for exo in exercises]
    return _make_3col_reply_keyboard(items, add_exo_btn="➕ Add exercise")
    








BACK = "⬅️ Back"
# ============================================================= #
def back_btn():

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BACK)]
        ],
        resize_keyboard=True
    )









# Helper functions
def _make_2col_reply_keyboard(items: list[str], back=True) -> ReplyKeyboardMarkup:
    keyboard = []

    for i in range(0, len(items), 2):
        row = [KeyboardButton(text=items[i])]

        if i + 1 < len(items):
            row.append(KeyboardButton(text=items[i + 1]))

        keyboard.append(row)


    if back:
        keyboard.append([KeyboardButton(text=BACK,)])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def _make_3col_reply_keyboard(items: list[str], back=True, add_exo_btn: str = None) -> ReplyKeyboardMarkup:
    keyboard = []

    for i in range(0, len(items), 3):
        row = [KeyboardButton(text=items[i])]

        if i + 1 < len(items):
            row.append(KeyboardButton(text=items[i + 1]))

        if i + 2 < len(items):
            row.append(KeyboardButton(text=items[i + 2]))

        keyboard.append(row)
    
    if add_exo_btn:
        keyboard.append([KeyboardButton(text=add_exo_btn)])
    
    if back:
        keyboard.append([KeyboardButton(text=BACK)])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )