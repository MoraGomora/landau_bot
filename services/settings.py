from structlog.typing import FilteringBoundLogger

from enums import status
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
        has_dynamic_violation_time: bool = False,
        static_violation_time: int | None = None,
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
            has_dynamic_violation_time=has_dynamic_violation_time,
            static_violation_time=static_violation_time,
            has_chat_dialog=has_chat_dialog
        )

        return await self.repo.create(data)
    
    async def get(self, chat_id: int) -> Settings | None:
        """Get a settings record of chat
        
        Returs:
            `Settings` when record is available
            `None` when record is not available (logically)"""
        doc = await self.repo.get_one({
            "chat_id": chat_id
        })

        if not doc:
            await self.logger.adebug(
                "Record is not available on the database",
                chat_id=chat_id
            )
            return
        
        await self.logger.adebug(
            "Record is available on the database",
            chat_id=doc.chat_id,
            chat_name=doc.chat_name,
            owner_id=doc.owner_id,
            has_send_violation_msg=doc.has_send_violation_msg,
            has_dynamic_violation_time=doc.has_dynamic_violation_time,
            has_chat_dialog=doc.has_chat_dialog
        )

        return doc
    
    async def get_has_send_violation_msg(self, chat_id: int) -> bool | None:
        doc = await self.get(chat_id)

        if not doc:
            return
        
        await self.logger.adebug(
            "Returning a value of \"has_send_violation_msg\" key from settings record",
            chat_id=doc.chat_id,
            has_send_violation_msg=doc.has_send_violation_msg
        )
        
        return doc.has_send_violation_msg
    
    async def get_has_send_dynamic_violation_time(self, chat_id: int) -> bool | None:
        doc = await self.get(chat_id)

        if not doc:
            return
        
        await self.logger.adebug(
            "Returning a value of \"has_dynamic_violation_time\" key from settings record",
            chat_id=doc.chat_id,
            has_dynamic_violation_time=doc.has_dynamic_violation_time
        )
        
        return doc.has_dynamic_violation_time

    async def change_has_send_violation_msg(self, chat_id: int, status: bool) -> Settings | None:
        """Change a `has_send_violation_msg` on settings record of chat
        
        Returs:
            `Settings` when key `has_send_violation_msg` was changed successfully
            `None` when record is not available"""
        doc = await self.get(chat_id)

        if not doc:
            return

        return await self.repo.update(
            {"chat_id": chat_id},
            {"has_send_violation_msg": status}
        )

    async def change_has_chat_dialog(self, chat_id: int, status: bool) -> Settings | None:
        """Change a `has_chat_dialog` on settings record of chat
        
        Returs:
            `Settings` when key `has_chat_dialog` was changed successfully
            `None` when record is not available"""
        doc = await self.get(chat_id)

        if not doc:
            return

        result = await self.repo.update(
            {"chat_id": chat_id},
            {"has_chat_dialog": status}
        )

        if not result:
            await self.logger.adebug(
                "Failed to update \"has_chat_dialog\" key on settings record",
                chat_id=chat_id,
                has_chat_dialog=status
            )
            return
        
        await self.logger.adebug(
            "Settings \"has_chat_dialog\" key was updated successfully",
            chat_id=result.chat_id,
            has_chat_dialog=result.has_chat_dialog
        )

        return result
    
    async def change_chat_title(self, chat_id: int, new_title: str) -> Settings | None:
        doc = await self.get(chat_id)

        if not doc:
            return
        
        result = await self.repo.update(
            {"chat_id": chat_id},
            {"chat_name": new_title}
        )

        if not result:
            await self.logger.adebug(
                "Failed to update \"chat_name\" key on settings record",
                chat_id=chat_id,
                chat_name=new_title
            )
            return

        await self.logger.adebug(
            "Settings \"chat_name\" key was updated successfully",
            chat_id=result.chat_id,
            chat_name=result.chat_name
        )

        return result
    
    async def change_has_dynamic_violation(self, chat_id: int, status: bool) -> Settings | None:
        doc = await self.get(chat_id)

        if not doc:
            return

        result = await self.repo.update(
            {"chat_id": chat_id},
            {"has_dynamic_violation_time": status}
        )

        if not result:
            await self.logger.adebug(
                "Failed to update \"has_dynamic_violation_time\" key on settings record",
                chat_id=chat_id,
                has_dynamic_violation_time=status
            )
            return
        
        await self.logger.adebug(
            "Settings \"has_dynamic_violation_time\" key was updated successfully",
            chat_id=result.chat_id,
            has_dynamic_violation_time=result.has_dynamic_violation_time
        )

        return result
    
    async def change_static_violation_time(self, chat_id: int, delay: int | None) -> Settings | None:
        doc = await self.get(chat_id)

        if not doc:
            return
        
        result = await self.repo.update(
            {"chat_id": chat_id},
            {"static_violation_time": delay}
        )

        if not result:
            await self.logger.adebug(
                "Failed to update \"static_violation_time\" key on settings record",
                chat_id=chat_id,
                static_violation_time=delay
            )
            return

        await self.logger.adebug(
            "Settings \"static_violation_time\" key was updated successfully",
            chat_id=result.chat_id,
            static_violation_time=result.static_violation_time
        )

        return result
    
    async def is_available(self, chat_id: int) -> bool:
        doc = await self.get(chat_id=chat_id)

        return bool(doc)
    
    async def get_chats_by_owner_id(self, owner_id: int) -> list[Settings] | None:
        docs = await self.repo.get_many(
            {"owner_id": owner_id}
        )

        if not docs:
            await self.logger.adebug(
                "No records were found for the specified owner_id",
                owner_id=owner_id
            )

            return
        
        await self.logger.adebug(
            "Records were found for the specified owner_id",
            owner_id=owner_id,
            chats_count=len(docs)
        )
        
        return docs