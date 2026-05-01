from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from core.container import AppContainer
from keyboards.menu import MenuCallback, get_menu_kb
from keyboards.choose_chat import get_choose_chat_kb

from .state import SettingsStates
from .navigation import NavigationService, NavigationState


router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, container: AppContainer) -> None:
    """Handle /start command for regular users."""
    if not await container.services.user.is_available(message.from_user.id):
        result = await container.services.user.create(
            message.from_user.id,
            True
        )
        if not result:
            await container.logger.aerror(
                "Failed to create a user",
                user_id=message.from_user.id if message.from_user else None,
                username=message.from_user.username if message.from_user else None
            )

            return
        
    await container.logger.ainfo(
        "User started bot",
        user_id=message.from_user.id if message.from_user else None,
        username=message.from_user.username if message.from_user else None
    )
    await message.answer(
        container.translator.call(
            "hello-msg"
        ),
        reply_markup=get_menu_kb(
            container.translator.call("settings-btn"),
            container.translator.call("support-btn")
        )
    )


@router.callback_query(MenuCallback.filter())
async def main_settings(
    call: CallbackQuery,
    callback_data: MenuCallback,
    state: FSMContext,
    container: AppContainer
) -> None:
    if callback_data.action == "settings":
        await call.message.delete()
        
        chats = await container.services.settings.get_chats_by_owner_id(call.from_user.id)
        if not chats:
            await call.message.answer(
                container.translator.call(
                    "chats-not-found"
                )
            )

            await container.logger.awarning(
                "No user chats found for settings",
                user_id=call.from_user.id
            )

            await call.answer()
            
            return

        await state.set_state(SettingsStates.CHAT_SETTINGS)
        
        # Инициализируем навигацию
        data = await state.get_data()
        NavigationService.set_navigation(
            data,
            current_state=NavigationState.CHAT_SETTINGS,
            previous_state=NavigationState.MAIN_MENU
        )
        await state.update_data(**data)
        
        await call.message.answer(
            container.translator.call(
                "choose-chat"
            ),
            reply_markup=get_choose_chat_kb(
                chats,
                is_back=True,
                back_text=container.translator.call("back-btn")
            )
        )
        
        await call.answer()
    elif callback_data.action == "support":
        await container.logger.ainfo(
            "User requested support",
            user_id=call.from_user.id
        )
        
        await call.answer("This function in development")