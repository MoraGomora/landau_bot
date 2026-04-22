from aiogram import Dispatcher

# from . import admin_actions, group_events, personal_actions
from . import private, group


def register_all_handlers(dp: Dispatcher) -> None:
    """
    Register all handler routers with the dispatcher.

    Args:
        dp: Aiogram Dispatcher instance
    """

    dp.include_routers(
        private.router,
        group.router
    )


__all__ = [
    "register_all_handlers"
    "private",
    "group"
]
