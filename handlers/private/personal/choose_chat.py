from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from core.container import AppContainer
from keyboards.choose_chat import ChooseChatCallback
from keyboards.settings import get_settings_kb

from .state import SettingsStates


router = Router(name="choose_chat")


@router.callback_query(ChooseChatCallback.filter(), SettingsStates.CHAT_SETTINGS)
async def choose_chat_handler(
    call: CallbackQuery,
    callback_data: ChooseChatCallback,
    state: FSMContext,
    container: AppContainer
) -> None:
    await call.message.delete()
    
    chat = await container.services.settings.get(callback_data.chat_id)
    if not chat:
        await call.answer()

        return
    
    if chat.has_send_violation_msg:
        violation_status = container.translator.call("on")
    else:
        violation_status = container.translator.call("off")
    
    await call.message.answer(
        container.translator.call(
            "choose-setting"
        ),
        reply_markup=get_settings_kb(
            container.translator.call(
                "send-violation-msg",
                violation_status=violation_status
            ),
            container.translator.call(
                "turn-dynamic-violation-msg",
                dynamic_violation_status="On"
            )
        )
    )

    await state.set_state(SettingsStates.CHAT_CONFIRM_SETTINGS)
    await state.update_data(chat=chat.model_dump())
    await call.answer()