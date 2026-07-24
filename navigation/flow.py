from states.NavigationStates import NavigationStates
from states.ActionStates import ActionStates


BACK_STATE = {

    NavigationStates.year:
        NavigationStates.language,

    NavigationStates.specialty:
        NavigationStates.year,

    NavigationStates.module:
        NavigationStates.specialty,

    ActionStates.choose_action:
        NavigationStates.module,

    ActionStates.choose_exercise:
        ActionStates.choose_action,
    
    ActionStates.waiting_pdf_to_search:
        ActionStates.choose_action
}
