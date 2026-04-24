from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.settings import SettingsCallback, SettingsConfirmCallback, get_settings_confirm_kb
from core.container import AppContainer
from models import Settings

from .state import SettingsStates

router = Router(name="settings")


@router.callback_query(SettingsCallback.filter(), SettingsStates.CHAT_CONFIRM_SETTINGS)
async def main_settings(
    call: CallbackQuery,
    callback_data: SettingsCallback,
    state: FSMContext,
    container: AppContainer
) -> None:
    await call.message.delete()

    data = await state.get_data()
    chat = Settings.model_validate(data.get("chat"))

    if chat.has_send_violation_msg:
        status = container.translator.call("on")
    else:
        status = container.translator.call("off")

    if callback_data.action == "send_violation_message":
        await call.message.answer(
            container.translator.call(
                "current-setting-status",
                status=status
            ),
            reply_markup=get_settings_confirm_kb(
                container.translator.call("on"),
                container.translator.call("off"),
                chat.has_send_violation_msg
            )
        )

        await call.answer()
    elif callback_data.action == "turn_dynamic_violation":
        await call.answer()


@router.callback_query(SettingsConfirmCallback.filter())
async def confirm_settings(
    call: CallbackQuery,
    callback_data: SettingsConfirmCallback,
    state: FSMContext,
    container: AppContainer
) -> None:
    data = await state.get_data()
    chat = Settings.model_validate(data.get("chat"))

    if callback_data.status:
        result = await container.services.settings.change_has_send_violation_msg(
            chat.chat_id,
            False
        )
        if not result:
            return

        status = container.translator.call("off")

        await call.answer()
    
    elif not callback_data.status:
        result = await container.services.settings.change_has_send_violation_msg(
            chat.chat_id,
            True
        )
        if not result:
            return
        
        status = container.translator.call("on")

        await call.answer()

    await call.message.edit_text(
        container.translator.call(
            "current-setting-status",
            status=status
        ),
        reply_markup=get_settings_confirm_kb(
            container.translator.call("on"),
            container.translator.call("off"),
            result.has_send_violation_msg
        )
    )