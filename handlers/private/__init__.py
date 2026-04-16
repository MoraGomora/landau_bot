from aiogram import Router, F
from aiogram.enums import ChatType

from . import admin, personal


router = Router(name="private")
router.message.filter(F.chat.type == ChatType.PRIVATE)


router.include_routers(
    admin.router,
    personal.router
)