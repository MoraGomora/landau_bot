from aiogram.types import InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class SettingsCallback(CallbackData, prefix="settings"):
    action: str


class SettingsConfirmCallback(CallbackData, prefix="settings_confirm"):
    status: bool


def get_settings_kb(
    send_violation_message_status_text: str = "Send violation message",
    turn_status_dynamic_violation_text: str = "Turn dynamic violation",
    *,
    is_back: bool = True,
    back_text: str = "Back"
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=send_violation_message_status_text,
        callback_data=SettingsCallback(action="send_violation_message")
    )
    builder.button(
        text=turn_status_dynamic_violation_text,
        callback_data=SettingsCallback(action="turn_dynamic_violation")
    )

    if is_back:
        builder.button(
            text=back_text,
            callback_data="back"
        )

    builder.adjust(1)

    return builder.as_markup()


def get_settings_confirm_kb(
    turn_on: str = "On",
    turn_off: str = "Off",
    status: bool = True,
    *,
    is_back: bool = True,
    back_text: str = "Back"
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=turn_on if not status else turn_off,
        callback_data=SettingsConfirmCallback(status=status)
    )

    if is_back:
        builder.button(
            text=back_text,
            callback_data="back"
        )

    builder.adjust(1)
    return builder.as_markup()