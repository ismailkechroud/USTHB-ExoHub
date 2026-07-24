from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from permission.constants import Status



def exercise_yes_no_keyboard(exercise_id: str):

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✔ Yes", callback_data=f"ex_yes:{exercise_id}"),
            InlineKeyboardButton(text="✖ No", callback_data=f"ex_no:{exercise_id}")
        ]
    ])



def solutions_btn(telegram_post_links: list[str], id_exo) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=f"Solution {i}", url=link)
        for i, link in enumerate(telegram_post_links, start=1)
    ]

    return _make_3col_inline_keyboard(id_exo, buttons, add_sol_btn="➕ Add solution")




def accept_reject_btn(telegram_id: int, role: str, request_type: str, status: str) -> InlineKeyboardMarkup:

    if status == Status.ACTIVE:
        # print("permission")
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Accept", callback_data=f"accept {request_type}:{telegram_id}:{role}"),
                InlineKeyboardButton(text="❌ Reject", callback_data=f"reject {request_type}:{telegram_id}:{role}")
            ]
        ])
    
    else:
        # print("status")
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Accept", callback_data=f"accept {request_type}:{telegram_id}:{role}"),
                InlineKeyboardButton(text="❌ Reject", callback_data=f"reject {request_type}:{telegram_id}:{role}")
            ]
        ])










# Helper functions
def _make_3col_inline_keyboard(id_exo, buttons: list[InlineKeyboardButton], add_sol_btn: str = None) -> InlineKeyboardMarkup:
    keyboard = []

    for i in range(0, len(buttons), 3):
        row = [buttons[i]]

        if i + 1 < len(buttons):
            row.append(buttons[i + 1])

        if i + 2 < len(buttons):
            row.append(buttons[i + 2])

        keyboard.append(row)

    if add_sol_btn:
        keyboard.append([InlineKeyboardButton(text=add_sol_btn, callback_data=f"add_solution:{id_exo}")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)



