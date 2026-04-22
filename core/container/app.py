from motor.motor_asyncio import AsyncIOMotorClient

from structlog.typing import FilteringBoundLogger

from fluent.runtime import FluentLocalization

from redis.asyncio import Redis

from config_reader import URL, get_env_or_config
from core import Translator
from repositories import Repositories
from services import Services
from config_reader import MongoConfig
from db import utils


class AppContainer:

    def __init__(self, mongo_config: MongoConfig, l10n: FluentLocalization, logger: FilteringBoundLogger):
        self._cache = {}

        self._redis_url = get_env_or_config(
            "REDIS_URL", URL,
            "redis", "url"
        )
        self.client = AsyncIOMotorClient(
            utils.build_mongodb_url(mongo_config),
            maxPoolSize=50,
            minPoolSize=5
        )

        self.logger: FilteringBoundLogger = logger
        self.l10n = l10n

        if self._redis_url:
            self._redis = Redis.from_url(self._redis_url)
        else:
            self._redis = None

        self._translator = None
        self._repos = None
        self._services = None

    @property
    def translator(self) -> Translator:
        return self.get("translator", lambda: Translator(self.l10n))

    @property
    def repositories(self) -> Repositories:
        return self.get("repositories", lambda: Repositories(self.client, "test"))

    @property
    def services(self) -> Services:
        return self.get("services", lambda: Services(self.repositories, self._redis, self.logger))

    def get(self, name: str, factory):
        if name not in self._cache:
            self._cache[name] = factory()
        return self._cache[name]