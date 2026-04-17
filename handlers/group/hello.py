from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command


router = Router(name="hello")


@router.message(Command("hello"))
async def hello(msg: Message):
    await msg.answer("Hello")