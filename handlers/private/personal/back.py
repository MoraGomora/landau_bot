from aiogram import Router, F
from aiogram.types import CallbackQuery


router = Router(name="back")


@router.callback_query(F.data == "back")
async def back(call: CallbackQuery) -> None:
    await call.answer()