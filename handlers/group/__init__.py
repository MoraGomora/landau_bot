from aiogram import Router, F
from aiogram.enums import ChatType

from . import hello, lifecycle, bot_lifecycle, all_messages


router = Router(name="group")
router.message.filter(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
router.my_chat_member.filter(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))


router.include_routers(
    hello.router,
    lifecycle.router,
    bot_lifecycle.router,
    all_messages.router
)