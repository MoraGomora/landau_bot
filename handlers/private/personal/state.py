from aiogram.fsm.state import State, StatesGroup


class SettingsStates(StatesGroup):
    CHAT_SETTINGS = State()
    CHAT_CONFIRM_SETTINGS = State()