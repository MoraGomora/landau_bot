from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from core.container import AppContainer
from keyboards.menu import get_menu_kb
from keyboards.choose_chat import get_choose_chat_kb
from keyboards.settings import get_settings_kb
from .state import SettingsStates
from .navigation import NavigationService, NavigationState


router = Router(name="back")


def _get_status_label(container: AppContainer, is_enabled: bool) -> str:
    """Возвращает локализованный статус (включено/отключено)."""
    return container.translator.call("on" if is_enabled else "off")


async def _show_main_menu(
    call: CallbackQuery,
    container: AppContainer
) -> None:
    """Показывает главное меню."""
    await call.message.answer(
        container.translator.call("hello-msg"),
        reply_markup=get_menu_kb(
            container.translator.call("settings-btn"),
            container.translator.call("support-btn")
        )
    )


async def _show_chat_settings_menu(
    call: CallbackQuery,
    state: FSMContext,
    container: AppContainer
) -> None:
    """Показывает меню выбора чата для настроек."""
    user_id = call.from_user.id
    
    try:
        await state.set_state(SettingsStates.CHAT_SETTINGS)
        
        chats = await container.services.settings.get_chats_by_owner_id(user_id)
        if not chats:
            await container.logger.awarning(
                "No chats found for user",
                user_id=user_id
            )
            await call.message.answer(
                container.translator.call("chats-not-found")
            )
            return

        await call.message.answer(
            container.translator.call("choose-chat"),
            reply_markup=get_choose_chat_kb(
                chats,
                is_back=True,
                back_text=container.translator.call("back-btn")
            )
        )
        
        # Обновляем навигацию
        data = await state.get_data()
        NavigationService.set_navigation(
            data,
            current_state=NavigationState.CHAT_SETTINGS,
            previous_state=NavigationState.MAIN_MENU
        )
        await state.update_data(**data)
        
    except Exception as e:
        await container.logger.aerror(
            "Error showing chat settings menu",
            user_id=user_id,
            error=str(e)
        )


async def _show_settings_menu(
    call: CallbackQuery,
    state: FSMContext,
    container: AppContainer
) -> None:
    """Показывает меню настроек выбранного чата."""
    user_id = call.from_user.id
    
    try:
        data = await state.get_data()
        chat = data.get("chat")
        
        if not chat:
            await container.logger.awarning(
                "Chat data not found in state",
                user_id=user_id
            )
            await call.answer(
                container.translator.call("error"),
                show_alert=True
            )
            return

        violation_status = _get_status_label(container, chat.get("has_send_violation_msg", False))
        dynamic_violation_status = "On"
        
        await state.set_state(SettingsStates.CHAT_CONFIRM_SETTINGS)
        
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
                back_text=container.translator.call("back-btn")
            )
        )
        
        # Обновляем навигацию
        NavigationService.set_navigation(
            data,
            current_state=NavigationState.CHAT_CONFIRM_SETTINGS,
            previous_state=NavigationState.CHAT_SETTINGS,
            extra_data={"chat_id": chat.get("chat_id")}
        )
        await state.update_data(**data)
        
    except Exception as e:
        await container.logger.aerror(
            "Error showing settings menu",
            user_id=user_id,
            error=str(e)
        )


@router.callback_query(F.data == "back")
async def back(
    call: CallbackQuery,
    state: FSMContext,
    container: AppContainer
) -> None:
    """
    Универсальный обработчик кнопки 'Назад'.
    
    Логика:
    - Удаляет текущее сообщение
    - Определяет предыдущее состояние из истории навигации
    - Восстанавливает соответствующее меню
    """
    user_id = call.from_user.id
    
    try:
        try:
            deleted = await call.message.delete()
            if not deleted:
                await container.logger.awarning(
                    "Failed to delete message",
                    user_id=user_id,
                    message_id=call.message.message_id
                )
        except TelegramBadRequest:
            await container.logger.awarning(
                "Message was already deleted or can't be deleted",
                user_id=user_id,
                message_id=call.message.message_id
            )
        
        await call.answer()
        
        # Получаем контекст навигации
        data = await state.get_data()
        previous_state = NavigationService.get_previous_state(data)
        
        await container.logger.adebug(
            "Back button pressed",
            user_id=user_id,
            previous_state=previous_state.value if previous_state else "None"
        )
        
        # Определяем, какое меню показать в зависимости от предыдущего состояния
        if previous_state == NavigationState.MAIN_MENU:
            await state.clear()
            await _show_main_menu(call, container)
            await container.logger.adebug(
                "Main menu shown",
                user_id=user_id
            )
            
        elif previous_state == NavigationState.CHAT_SETTINGS:
            await _show_chat_settings_menu(call, state, container)
            await container.logger.adebug(
                "Chat settings menu shown",
                user_id=user_id
            )
            
        elif previous_state == NavigationState.CHAT_CONFIRM_SETTINGS:
            await _show_settings_menu(call, state, container)
            await container.logger.adebug(
                "Settings menu shown",
                user_id=user_id
            )
            
        else:
            # По умолчанию показываем главное меню
            await state.clear()
            await _show_main_menu(call, container)
            await container.logger.adebug(
                "Previous state not found, main menu shown by default",
                user_id=user_id
            )
        
        await container.logger.ainfo(
            "Back button handled successfully",
            user_id=user_id,
            previous_state=previous_state.value if previous_state else "None"
        )
        
    except Exception as e:
        await container.logger.aerror(
            "Error handling back button",
            user_id=user_id,
            error=str(e)
        )
        await call.answer(
            container.translator.call("error"),
            show_alert=True
        )