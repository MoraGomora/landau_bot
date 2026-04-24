from typing import Dict, Awaitable, Callable

from motor.motor_asyncio import AsyncIOMotorClient

from structlog.typing import FilteringBoundLogger

from fluent.runtime import FluentLocalization

from core import Translator, SimpleWorkerManager
from repositories import Repositories
from services import Services
from config_reader import MongoConfig
from db import RedisCacheStorage, CacheStorage, utils


class AppContainer:

    def __init__(
        self,
        storage: RedisCacheStorage | CacheStorage,
        mongo_config: MongoConfig,
        l10n: FluentLocalization,
        logger: FilteringBoundLogger
    ) -> None:
        self._cache: Dict[str, Callable[[], Awaitable[None]]] = {}
        self.msgs_cache: Dict[int, int] = {}

        self.client = AsyncIOMotorClient(
            utils.build_mongodb_url(mongo_config),
            maxPoolSize=50,
            minPoolSize=5
        )

        self.logger: FilteringBoundLogger = logger
        self.l10n = l10n

        self._storage = storage

        self._translator = None
        self._repos = None
        self._services = None
        self._worker_manager = None

    @property
    def translator(self) -> Translator:
        return self.get(
            "translator",
            lambda: Translator(self.l10n)
        )

    @property
    def repositories(self) -> Repositories:
        return self.get(
            "repositories",
            lambda: Repositories(
                self.client,
                "test",
                self.logger
            )
        )

    @property
    def services(self) -> Services:
        return self.get(
            "services",
            lambda: Services(
                self.repositories,
                self._storage,
                self.logger
            )
        )
    
    @property
    def worker_manager(self) -> SimpleWorkerManager:
        return self.get(
            "worker_manager",
            lambda: SimpleWorkerManager(
                self.logger
            )
        )

    def get(self, name: str, factory):
        if name not in self._cache:
            self._cache[name] = factory()
        return self._cache[name]