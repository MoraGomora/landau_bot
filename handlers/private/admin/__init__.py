from aiogram import Router

from filters import IsOwnerFilter
from . import start, logs


router = Router(name="admin")
router.message.filter(IsOwnerFilter())


router.include_routers(
    start.router,
    logs.router
)