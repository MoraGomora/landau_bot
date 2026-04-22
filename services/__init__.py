from structlog.typing import FilteringBoundLogger

from redis.asyncio import Redis

from repositories import Repositories
from .settings import SettingsService
from .user import UserService
from .chat_user import ChatUserService


class Services:

    def __init__(
        self,
        repos: Repositories,
        redis: Redis,
        logger: FilteringBoundLogger
    ) -> None:
        self.settings = SettingsService(repos.settings, logger)
        self.user = UserService(repos.user, logger)
        self.chat_user = ChatUserService(repos.chat_user, redis, logger)


__all__ = [
    "Services",
    "SettingsService",
    "UserService",
    "ChatUserService"
]