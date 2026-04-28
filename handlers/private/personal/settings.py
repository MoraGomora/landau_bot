from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.settings import SettingsCallback, SettingsConfirmCallback, get_settings_confirm_kb
from core.container import AppContainer
from models import Settings

from .state import SettingsStates

router = Router(name="settings")

# Константы для действий
SETTINGS_ACTIONS = {
    "send_violation_message": "violation_message",
    "turn_dynamic_violation": "dynamic_violation"
}


def _get_status_label(container: AppContainer, is_enabled: bool) -> str:
    """Возвращает локализованный статус (включено/отключено)."""
    return container.translator.call("on" if is_enabled else "off")


async def _handle_send_violation_message_action(
    call: CallbackQuery,
    chat: Settings,
    container: AppContainer
) -> None:
    """Обработка действия отправки сообщения о нарушении."""
    status = _get_status_label(container, chat.has_send_violation_msg)

    await call.message.answer(
        container.translator.call(
            "current-setting-status",
            chat_name=chat.chat_name,
            status=status
        ),
        reply_markup=get_settings_confirm_kb(
            container.translator.call("on"),
            container.translator.call("off"),
            chat.has_send_violation_msg,
            is_back=True,
            back_text=container.translator.call("back-btn")
        )
    )
    await call.answer()


async def _handle_dynamic_violation_action(
    call: CallbackQuery,
    chat: Settings,
    container: AppContainer
) -> None:
    """Обработка действия динамического нарушения."""
    # TODO: Реализовать логику для динамического нарушения
    # На данный момент эта функция заглушка
    await container.logger.adebug(
        "Dynamic violation action not yet implemented",
        chat_id=chat.chat_id
    )
    await call.message.answer(
        "Feature in development"
    )
    await call.answer()


async def _update_violation_message_setting(
    container: AppContainer,
    chat_id: int,
    current_status: bool
) -> tuple[bool, str]:
    """
    Обновляет настройку отправки сообщения о нарушении.
    
    Returns:
        Кортеж (успех, новый_статус)
    """
    new_value = not current_status
    
    result = await container.services.settings.change_has_send_violation_msg(
        chat_id,
        new_value
    )
    
    if not result:
        await container.logger.aerror(
            "Failed to update violation message setting",
            chat_id=chat_id,
            new_value=new_value
        )
        return False, ""
    
    status = _get_status_label(container, new_value)
    
    await container.logger.ainfo(
        "Violation message setting updated",
        chat_id=chat_id,
        new_value=new_value
    )
    
    return True, status


@router.callback_query(SettingsCallback.filter(), SettingsStates.CHAT_CONFIRM_SETTINGS)
async def main_settings(
    call: CallbackQuery,
    callback_data: SettingsCallback,
    state: FSMContext,
    container: AppContainer
) -> None:
    """Обработчик основных действий с настройками."""
    await call.message.delete()

    data = await state.get_data()
    chat = Settings.model_validate(data.get("chat"))

    action_handlers = {
        "send_violation_message": _handle_send_violation_message_action,
        "turn_dynamic_violation": _handle_dynamic_violation_action,
    }

    handler = action_handlers.get(callback_data.action)
    if handler:
        await handler(call, chat, container)
    else:
        await container.logger.awarning(
            "Unknown settings action",
            action=callback_data.action,
            chat_id=chat.chat_id
        )
        await call.answer()


@router.callback_query(SettingsConfirmCallback.filter())
async def confirm_settings(
    call: CallbackQuery,
    callback_data: SettingsConfirmCallback,
    state: FSMContext,
    container: AppContainer
) -> None:
    """Обработчик подтверждения изменения настроек."""
    data = await state.get_data()
    chat = Settings.model_validate(data.get("chat"))

    success, status = await _update_violation_message_setting(
        container,
        chat.chat_id,
        callback_data.status
    )

    if not success:
        await container.logger.aerror(
            "Settings update failed",
            chat_id=chat.chat_id
        )
        await call.answer(
            container.translator.call("settings-update-failed"),
            show_alert=True
        )
        return

    await call.answer()

    updated_settings = await container.services.settings.get(chat.chat_id)
    
    if not updated_settings:
        await container.logger.aerror(
            "Failed to fetch updated settings",
            chat_id=chat.chat_id
        )
        return

    await call.message.edit_text(
        container.translator.call(
            "current-setting-status",
            chat_name=chat.chat_name,
            status=status
        ),
        reply_markup=get_settings_confirm_kb(
            container.translator.call("on"),
            container.translator.call("off"),
            updated_settings.has_send_violation_msg,
            is_back=True,
            back_text=container.translator.call("back-btn")
        )
    )