from aiogram.types import InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class MenuCallback(CallbackData, prefix="menu"):
    action: str


def get_menu_kb(
    settings_text: str = "Settings",
    support_text: str = "Support"
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=settings_text,
        callback_data=MenuCallback(action="settings")
    )
    builder.button(
        text=support_text,
        callback_data=MenuCallback(action="support")
    )

    builder.adjust(1)
    return builder.as_markup()