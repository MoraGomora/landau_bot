from structlog.typing import FilteringBoundLogger

from repositories import Repositories, SettingsRepository
from models import Settings, CreateSettings


class SettingsService:

    def __init__(
        self,
        repository: Repositories,
        logger: FilteringBoundLogger
    ) -> None:
        if not isinstance(repository, SettingsRepository):
            raise ValueError("\"repository\" should be a SettingsRepository object")
        
        self.repo = repository
        self.logger = logger

    async def create(
        self,
        chat_id: int,
        chat_name: str,
        owner_id: int,
        has_send_violation_msg: bool = True,
        has_chat_dialog: bool = True
    ) -> Settings | None:
        """Create a new settings record for chat
        
        Returs:
            `Settings` when record is created successfully
            `None` when record is available now"""
        doc = await self.repo.get_one({
            "chat_id": chat_id,
            "owner_id": owner_id
        })

        if doc:
            await self.logger.adebug(
                "Record is available on the database"
            )
            return

        data = CreateSettings(
            chat_id=chat_id,
            chat_name=chat_name,
            owner_id=owner_id,
            has_send_violation_msg=has_send_violation_msg,
            has_chat_dialog=has_chat_dialog
        )

        return await self.repo.create(data)
    
    async def get(self, chat_id: int) -> Settings | None:
        """Get a settings record of chat
        
        Returs:
            `Settings` when record is available
            `None` when record is not available (logically)"""
        return await self.repo.get_one({
            "chat_id": chat_id
        })
    
    async def get_has_send_violation_msg(self, chat_id: int) -> bool | None:
        doc = await self.get(chat_id)

        if not doc:
            return
        
        return doc.has_send_violation_msg

    async def change_has_send_violation_msg(self, chat_id: int, status: bool) -> Settings | None:
        """Change a `has_send_violation_msg` on settings record of chat
        
        Returs:
            `Settings` when key `has_send_violation_msg` was changed successfully
            `None` when record is not available"""
        filter = {
            "chat_id": chat_id
        }

        doc = await self.repo.get_one(filter)

        if not doc:
            await self.logger.adebug(
                "Record is available on the database"
            )
            return

        return await self.repo.update(
            filter,
            {"has_send_violation_msg": status}
        )

    async def change_has_chat_dialog(self, chat_id: int, status: bool) -> Settings | None:
        """Change a `has_chat_dialog` on settings record of chat
        
        Returs:
            `Settings` when key `has_chat_dialog` was changed successfully
            `None` when record is not available"""
        filter = {
            "chat_id": chat_id
        }

        doc = await self.repo.get_one(filter)

        if not doc:
            await self.logger.adebug(
                "Record is available on the database"
            )
            return

        return await self.repo.update(
            filter,
            {"has_chat_dialog": status}
        )
    
    async def is_available(self, chat_id: int) -> bool:
        doc = await self.get(chat_id=chat_id)

        return bool(doc)