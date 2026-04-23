from structlog.typing import FilteringBoundLogger

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure, PyMongoError

from .repos import SettingsRepository, UserRepository, ChatUserRepository


class Repositories:

    def __init__(
            self,
            client: AsyncIOMotorClient,
            name: str,
            logger: FilteringBoundLogger
    ) -> None:
        collection = client.get_database(name)

        self.settings = SettingsRepository(collection.settings)
        self.user = UserRepository(collection.users)
        self.chat_user = ChatUserRepository(collection.chat_users)

        self._client = client
        self._logger = logger

    async def ping(self) -> bool:
        try:
            data = await self._client.admin.command("ping")

            return bool(data)
        except OperationFailure as e:
            await self._logger.aerror(
                "OperationFailure exception when trying to ping",
                error=str(e)
            )

            exit(1)
        except PyMongoError as e:
            await self._logger.aerror(
                "PyMongoError",
                error=str(e)
            )

            return False


__all__ = [
    "Repositories",
    "SettingsRepository",
    "UserRepository",
    "ChatUserRepository"
]