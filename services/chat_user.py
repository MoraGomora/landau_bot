from structlog.typing import FilteringBoundLogger

from repositories import Repositories, ChatUserRepository
from models import ChatUser, CreateChatUser, Violation
from db import RedisCacheStorage, CacheStorage
from enums import Status


class ChatUserService:

    def __init__(
            self,
            repository: Repositories,
            storage: RedisCacheStorage | CacheStorage,
            logger: FilteringBoundLogger
    ) -> None:
        if not isinstance(repository, ChatUserRepository):
            raise ValueError("\"repository\" should be a ChatUserRepository object")
        
        self.repo = repository
        self.storage = storage
        self.logger = logger

    async def create(
            self,
            user_id: int,
            chat_id: int,
            join_attempts: int = 0,
            status: Status = Status.NONE
    ) -> ChatUser | None:
        data = CreateChatUser(
            user_id=user_id,
            chat_id=chat_id,
            join_attempts=join_attempts,
            status=status
        )

        result = await self.repo.create(data)
        if not result:
            await self.logger.aerror(
                "Failed to create chat user record",
                user_id=user_id,
                chat_id=chat_id
            )
            return
        
        await self.logger.adebug(
            "Chat user record created successfully",
            user_id=result.user_id,
            chat_id=result.chat_id,
            join_attempts=result.join_attempts,
            status=result.status
        )

        return result

    async def get(self, user_id: int, chat_id: int) -> ChatUser | None:
        await self.logger.adebug(
            "Getting a user record...",
            user_id=user_id
        )

        doc = await self.repo.get_one({
            "user_id": user_id,
            "chat_id": chat_id
        })

        if not doc:
            await self.logger.aerror(
                "Chat user record was not found. Returning None...",
                user_id=user_id,
                chat_id=chat_id
            )

            return
        
        await self.logger.ainfo(
            "Chat user record was found",
            user_id=doc.user_id,
            chat_id=doc.chat_id,
            join_attempts=doc.join_attempts,
            status=doc.status
        )
        
        return doc

    async def add_join_attempt(self, user_id: int, chat_id: int) -> ChatUser | None:
        doc = await self.get(user_id, chat_id)

        if not doc:
            return
        
        doc.join_attempts += 1

        return await self.repo.update(
            {"user_id": user_id, "chat_id": chat_id},
            {"join_attempts": doc.join_attempts}
        )

    async def is_available(self, user_id: int, chat_id: int) -> bool:
        doc = await self.get(user_id, chat_id)

        return bool(doc)
    
    async def set_status(self, user_id: int, chat_id: int, status: Status) -> ChatUser | None:
        doc = await self.get(user_id, chat_id)

        if not doc:
            return
        
        result = await self.repo.update(
            {"user_id": user_id, "chat_id": chat_id},
            {"status": status}
        )

        if not result:
            await self.logger.ainfo(
                "Failed to update chat user status",
                user_id=user_id,
                chat_id=chat_id
            )

            return
        
        await self.logger.ainfo(
            "Status for chat user was updated successfully",
            user_id=result.user_id,
            chat_id=result.chat_id,
            status=result.status
        )

        return result
    
    async def set_violation_data(self, user_id: int, chat_id: int, time: str, data: Violation) -> bool:
        key = f"key:{chat_id}:{user_id}:{time}"
        
        return await self.storage.set(key, data.model_dump())
    
    async def get_violation_data(self, user_id: int, chat_id: int, time: str) -> Violation | None:
        raw = await self.storage.get(f"key:{chat_id}:{user_id}:{time}")

        return Violation.model_validate(raw) if raw else None
    
    async def has_violation(self, user_id: int, chat_id: int, time: str) -> bool:
        key = f"key:{chat_id}:{user_id}:{time}"

        return await self.storage.exists(key)