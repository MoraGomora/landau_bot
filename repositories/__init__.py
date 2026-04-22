from motor.motor_asyncio import AsyncIOMotorClient

from .repos import SettingsRepository, UserRepository, ChatUserRepository


class Repositories:

    def __init__(self, client: AsyncIOMotorClient, name: str):
        collection = client.get_database(name)

        self.settings = SettingsRepository(collection.settings)
        self.user = UserRepository(collection.users)
        self.chat_user = ChatUserRepository(collection.chat_users)

        self._client = client

    async def ping(self) -> bool:
        try:
            data = await self._client.admin.command("ping")

            return bool(data)
        except:
            return False


__all__ = [
    "Repositories",
    "SettingsRepository",
    "UserRepository",
    "ChatUserRepository"
]