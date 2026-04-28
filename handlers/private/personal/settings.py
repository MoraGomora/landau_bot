from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.settings import SettingsCallback, SettingsConfirmCallback, get_settings_confirm_kb
from core.container import AppContainer
from models import Settings

from .state import SettingsStates
from .utils import get_status_label

router = Router(name="settings")

# Mapping между ключами настроек и методами сервиса
# Формат: "setting_key": ("db_field", "service_method")
SETTINGS_UPDATES = {
    "send_violation_message": {
        "field": "has_send_violation_msg",
        "service_method": "change_has_send_violation_msg"
    },
    "dynamic_violation": {
        "field": "has_dynamic_violation_time",
        "service_method": "change_has_dynamic_violation"
    }
}


async def _handle_setting_action(
    call: CallbackQuery,
    chat: Settings,
    container: AppContainer,
    setting_key: str
) -> None:
    """Универсальный обработчик действий с настройками."""
    config = SETTINGS_UPDATES.get(setting_key)
    if not config:
        await container.logger.awarning(
            "Unknown settings key",
            setting_key=setting_key,
            chat_id=chat.chat_id
        )
        await call.answer()
        return
    
    field = config["field"]
    current_value = getattr(chat, field, None)
    
    if current_value is None:
        await container.logger.awarning(
            "Field not found on chat settings",
            field=field,
            chat_id=chat.chat_id
        )
        await call.answer()
        return
    
    status = get_status_label(container, current_value)

    await call.message.answer(
        container.translator.call(
            "current-setting-status",
            chat_name=chat.chat_name,
            status=status
        ),
        reply_markup=get_settings_confirm_kb(
            container.translator.call("on"),
            container.translator.call("off"),
            current_value,
            setting_key=setting_key,
            is_back=True,
            back_text=container.translator.call("back-btn")
        )
    )
    await call.answer()


async def _update_setting(
    container: AppContainer,
    chat_id: int,
    setting_key: str,
    current_status: bool
) -> tuple[bool, str]:
    """
    Универсальное обновление настройки через сервис.
    
    Args:
        container: AppContainer
        chat_id: ID чата
        setting_key: Ключ настройки из SETTINGS_UPDATES
        current_status: Текущее значение
    
    Returns:
        Кортеж (успех, новый_статус)
    """
    config = SETTINGS_UPDATES.get(setting_key)
    if not config:
        await container.logger.awarning(
            "Unknown settings key",
            setting_key=setting_key,
            chat_id=chat_id
        )
        return False, ""
    
    service_method = config["service_method"]
    new_value = not current_status
    
    # Вызываем нужный метод сервиса динамически
    method = getattr(container.services.settings, service_method, None)
    if not method:
        await container.logger.aerror(
            "Service method not found",
            method=service_method,
            chat_id=chat_id
        )
        return False, ""
    
    result = await method(chat_id, new_value)
    
    if not result:
        await container.logger.aerror(
            "Failed to update setting",
            setting_key=setting_key,
            chat_id=chat_id,
            new_value=new_value
        )
        return False, ""
    
    status = get_status_label(container, new_value)
    
    await container.logger.ainfo(
        "Setting updated",
        setting_key=setting_key,
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

    # Используем callback_data.action как ключ для поиска в SETTINGS_UPDATES
    await _handle_setting_action(call, chat, container, callback_data.action)


@router.callback_query(SettingsConfirmCallback.filter())
async def confirm_settings(
    call: CallbackQuery,
    callback_data: SettingsConfirmCallback,
    state: FSMContext,
    container: AppContainer
) -> None:
    """Универсальный обработчик подтверждения изменения настроек."""
    data = await state.get_data()
    chat = Settings.model_validate(data.get("chat"))

    success, status = await _update_setting(
        container,
        chat.chat_id,
        callback_data.setting_key,
        callback_data.status
    )

    if not success:
        await container.logger.aerror(
            "Settings update failed",
            chat_id=chat.chat_id,
            setting_key=callback_data.setting_key
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

    # Получаем обновленное значение поля из конфига
    config = SETTINGS_UPDATES.get(callback_data.setting_key)
    if config:
        field = config["field"]
        updated_value = getattr(updated_settings, field, callback_data.status)
    else:
        updated_value = callback_data.status

    await call.message.edit_text(
        container.translator.call(
            "current-setting-status",
            chat_name=chat.chat_name,
            status=status
        ),
        reply_markup=get_settings_confirm_kb(
            container.translator.call("on"),
            container.translator.call("off"),
            updated_value,
            setting_key=callback_data.setting_key,
            is_back=True,
            back_text=container.translator.call("back-btn")
        )
    )
