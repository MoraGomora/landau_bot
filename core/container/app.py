from structlog.typing import FilteringBoundLogger

from fluent.runtime import FluentLocalization

from db.redis import RedisClient
from config_reader import URL, get_env_or_config
from core import Translator


class AppContainer:

    def __init__(self, l10n: FluentLocalization, logger: FilteringBoundLogger):
        self._cache = {}

        self._url = get_env_or_config(
            "REDIS_URL", URL,
            "redis", "url"
        )
        self.logger: FilteringBoundLogger = logger
        self.l10n = l10n

        self._redis = None
        self._translator = None

    @property
    def redis(self) -> RedisClient:
        return self.get("redis", lambda: RedisClient(self._url, self.logger))

    @property
    def translator(self) -> Translator:
        return self.get("translator", lambda: Translator(self.l10n))

    def get(self, name: str, factory):
        if name not in self._cache:
            self._cache[name] = factory()
        return self._cache[name]