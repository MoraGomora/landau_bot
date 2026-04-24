from aiogram.types import InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ChooseChatCallback(CallbackData, prefix="choose_chat"):
    chat_id: int


def get_choose_chat_kb(
    chats: list,
    *,
    is_back: bool = True,
    back_text: str = "Back"
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for chat in chats:
        builder.button(
            text=chat.chat_name,
            callback_data=ChooseChatCallback(chat_id=chat.chat_id)
        )

    if is_back:
        builder.button(
            text=back_text,
            callback_data="back"
        )

    builder.adjust(1)
    return builder.as_markup()