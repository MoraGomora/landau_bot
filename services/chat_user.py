from typing import List

from structlog.typing import FilteringBoundLogger

from repositories import Repositories, ChatUserRepository
from models import ChatUser, CreateChatUser, Violation
from db import CacheStorage
from enums import Status, BanStatus


class ChatUserService:

    def __init__(
            self,
            repository: Repositories,
            storage: CacheStorage,
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
            full_name: str,
            chat_id: int,
            join_attempts: int = 0,
            status: Status = Status.NONE,
            ban_status: BanStatus = BanStatus.UNBANNED
    ) -> ChatUser | None:
        data = CreateChatUser(
            user_id=user_id,
            full_name=full_name,
            chat_id=chat_id,
            join_attempts=join_attempts,
            status=status,
            ban_status=ban_status
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
            full_name=result.full_name,
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
        
        await self.logger.adebug(
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
    
    async def get_users_with_uncomplete_status(self) -> List[ChatUser] | None:
        docs = await self.repo.get_many(
            {"status": {"$in": [Status.PENDING, Status.FAILED, Status.PROCESSING]}}
        )

        if not docs:
            await self.logger.aerror(
                "Users with uncompleted status was not found"
            )
            
            return None
        
        return docs
    
    async def set_status(self, user_id: int, chat_id: int, status: Status) -> bool:
        doc = await self.get(user_id, chat_id)

        if not doc:
            return
        
        result = await self.repo.update(
            {"user_id": user_id, "chat_id": chat_id},
            {"status": status}
        )

        if not result:
            await self.logger.adebug(
                "Failed to update chat user status",
                user_id=user_id,
                chat_id=chat_id
            )

            return
        
        await self.logger.adebug(
            "Status for chat user was updated successfully",
            user_id=result.user_id,
            chat_id=result.chat_id,
            status=result.status
        )

        return bool(result)
    
    async def set_ban_status(self, user_id: int, chat_id: int, status: BanStatus) -> ChatUser | None:
        doc = await self.get(user_id, chat_id)

        if not doc:
            return
        
        if doc.status == status:
            await self.logger.awarning(
                "The status will not be changed, since the value of the transmitted status is equal to the value from the database.",
                user_id=user_id,
                chat_id=chat_id,
                status=doc.status
            )

            return
        
        return await self.repo.update(
            {
                "user_id": user_id,
                "chat_id": chat_id
            },
            {"ban_status": status}
        )

    async def get_all(self) -> List[ChatUser] | None:
        docs = await self.repo.get_many({})

        if not docs:
            return
        
        return docs
    
    async def set_violation_data(self, user_id: int, chat_id: int, time: str, data: Violation) -> bool:
        key = f"key:{time}:{chat_id}:{user_id}"
        
        result = await self.storage.set(key, data.model_dump_json())
        if result:
            await self.logger.adebug(
                "Data with entered key writed successfully",
                status=result
            )
        
        return result
    
    async def get_violation_data(self, user_id: int, chat_id: int, time: str) -> Violation | None:
        key = f"key:{time}:{chat_id}:{user_id}"
        raw = await self.storage.get(key)
        
        if raw:
            await self.logger.adebug(
                "Data with entered key was found successfully",
                status=bool(raw)
            )

            return Violation.model_validate_json(raw)
        
        return None
    
    async def has_violation(self, user_id: int, chat_id: int, time: str) -> bool:
        key = f"key:{time}:{chat_id}:{user_id}"
        result = await self.storage.exists(key)

        if result:
            await self.logger.adebug(
                "Data with entered key is exists",
                status=result
            )
        
        return result