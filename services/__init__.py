from structlog.typing import FilteringBoundLogger

from repositories import Repositories
from .settings import SettingsService
from .user import UserService
from .chat_user import ChatUserService
from db import RedisCacheStorage, CacheStorage


class Services:

    def __init__(
        self,
        repos: Repositories,
        storage: RedisCacheStorage | CacheStorage,
        logger: FilteringBoundLogger
    ) -> None:
        self.settings = SettingsService(repos.settings, logger)
        self.user = UserService(repos.user, logger)
        self.chat_user = ChatUserService(repos.chat_user, storage, logger)


__all__ = [
    "Services",
    "SettingsService",
    "UserService",
    "ChatUserService"
]