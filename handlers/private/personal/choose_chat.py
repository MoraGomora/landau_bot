from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from core.container import AppContainer
from keyboards.choose_chat import ChooseChatCallback
from keyboards.settings import get_settings_kb

from .state import SettingsStates
from .navigation import NavigationService, NavigationState


router = Router(name="choose_chat")


def _get_status_label(container: AppContainer, is_enabled: bool) -> str:
    """Возвращает локализованный статус (включено/отключено)."""
    return container.translator.call("on" if is_enabled else "off")


@router.callback_query(ChooseChatCallback.filter(), SettingsStates.CHAT_SETTINGS)
async def choose_chat_handler(
    call: CallbackQuery,
    callback_data: ChooseChatCallback,
    state: FSMContext,
    container: AppContainer
) -> None:
    """Обработчик выбора чата для настроек."""
    user_id = call.from_user.id
    chat_id = callback_data.chat_id
    
    await container.logger.adebug(
        "User selected chat for settings",
        user_id=user_id,
        chat_id=chat_id
    )
    
    try:
        await call.message.delete()
        await container.logger.adebug(
            "Settings message deleted",
            user_id=user_id,
            chat_id=chat_id
        )
    except TelegramBadRequest as e:
        await container.logger.awarning(
            "Failed to delete settings message",
            user_id=user_id,
            chat_id=chat_id,
            error=str(e)
        )
    
    # Получаем данные чата
    chat = await container.services.settings.get(chat_id)
    if not chat:
        await container.logger.awarning(
            "Chat settings not found",
            user_id=user_id,
            chat_id=chat_id
        )
        await call.answer()
        return
    
    await container.logger.adebug(
        "Chat settings retrieved",
        user_id=user_id,
        chat_id=chat_id,
        has_send_violation_msg=chat.has_send_violation_msg
    )
    
    violation_status = _get_status_label(container, chat.has_send_violation_msg)
    
    dynamic_violation_status = "On"
    
    await call.message.answer(
        container.translator.call("choose-setting"),
        reply_markup=get_settings_kb(
            container.translator.call(
                "send-violation-msg",
                violation_status=violation_status
            ),
            container.translator.call(
                "turn-dynamic-violation-msg",
                dynamic_violation_status=dynamic_violation_status
            ),
            is_back=True,
            back_text=container.translator.call("back-btn")
        )
    )
    
    await state.set_state(SettingsStates.CHAT_CONFIRM_SETTINGS)
    await state.update_data(chat=chat.model_dump())
    
    # Обновляем навигацию
    data = await state.get_data()
    NavigationService.set_navigation(
        data,
        current_state=NavigationState.CHAT_CONFIRM_SETTINGS,
        previous_state=NavigationState.CHAT_SETTINGS,
        extra_data={"chat_id": chat_id}
    )
    await state.update_data(**data)
    
    await container.logger.ainfo(
        "Settings menu displayed for chat",
        user_id=user_id,
        chat_id=chat_id
    )
    
    await call.answer()