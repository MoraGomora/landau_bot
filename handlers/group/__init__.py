from aiogram import Router, F
from aiogram.enums import ChatType

from . import hello, lifecycle


router = Router(name="group")
router.message.filter(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))


router.include_routers(
    hello.router,
    lifecycle.router
)