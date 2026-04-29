from structlog.typing import FilteringBoundLogger

from repositories import Repositories, UserRepository
from models import User, CreateUser
from enums import Permission


class UserService:

    def __init__(
            self,
            repository: Repositories,
            logger: FilteringBoundLogger
    ) -> None:
        if not isinstance(repository, UserRepository):
            raise ValueError("\"repository\" should be a UserRepository object")
        
        self.repo = repository
        self.logger = logger

    async def create(
            self,
            user_id: int,
            has_private: bool = False,
            permission: Permission = Permission.USER
    ) -> User | None:
        doc = await self.repo.get_one({
            "user_id": user_id
        })

        if doc:
            await self.logger.adebug(
                "User record was found",
                user_id=doc.user_id,
                has_private=doc.has_private,
                permission=doc.permission
            )
            return
        
        data = CreateUser(
            user_id=user_id,
            has_private=has_private,
            permission=permission
        )

        result = await self.repo.create(data)
        if not result:
            await self.logger.aerror(
                "Failed to create user record",
                user_id=user_id
            )
            return
        
        await self.logger.adebug(
            "User record created successfully",
            user_id=user_id,
            has_private=has_private,
            permission=permission
        )

        return result

    async def get(self, user_id: int) -> User | None:
        await self.logger.adebug(
            "Getting a user record...",
            user_id=user_id
        )

        doc = await self.repo.get_one({
            "user_id": user_id
        })

        if not doc:
            await self.logger.aerror(
                "User record was not found. Returning None...",
                user_id=user_id
            )
            return
        
        return doc
    
    async def change_has_private(self, user_id: int, status: bool) -> User | None:
        doc = await self.get(user_id)

        if not doc:
            return
        
        return await self.repo.update(
            {"user_id": user_id},
            {"has_private": status}
        )
    
    async def get_has_privtae(self, user_id: int) -> bool:
        doc = await self.get(user_id)

        if not doc:
            return
        
        return doc.has_private

    async def is_available(self, user_id: int) -> bool:
        doc = await self.get(user_id)

        return bool(doc)