from aiogram import Router

from filters import IsOwnerFilter
from . import start


router = Router(name="personal")
router.message.filter(IsOwnerFilter(is_owner=False))


router.include_routers(
    start.router
)