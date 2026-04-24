from aiogram import Router

from filters import IsOwnerFilter
from . import start, settings, back, choose_chat


router = Router(name="personal")
# router.message.filter(IsOwnerFilter(is_owner=False))


router.include_routers(
    start.router,
    settings.router,
    back.router,
    choose_chat.router
)