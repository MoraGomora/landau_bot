from structlog.typing import FilteringBoundLogger

from repositories import Repositories, ChatOwnerRepository
from models import ChatOwner, CreateChatOwner


class ChatOwnerService:

    def __init__(
            self,
            repository: Repositories,
            logger: FilteringBoundLogger
    ) -> None:
        if not isinstance(repository, ChatOwnerRepository):
            raise ValueError("\"repository\" should be a ChatUserRepository object")
        
        self.repo = repository
        self.logger = logger

    async def get(self, owner_id: int) -> ChatOwner | None:
        doc = await self.repo.get_one(
            {"owner_id": owner_id}
        )

        if not doc:
            return
        
        return doc

    async def create_or_update(
            self,
            owner_id: int,
            chat_ids: int,
            new_chat_id: int
    ) -> ChatOwner | None:
        doc = await self.get(owner_id)

        if not doc:
            data = CreateChatOwner(
                owner_id=owner_id,
                chat_ids=[chat_ids],
                new_chat_id=new_chat_id
            )

            result = await self.repo.create(data)
            if not result:
                return
            
            return result
        
        if chat_ids in doc.chat_ids:
            return
        
        doc.chat_ids.append(chat_ids)

        updated = await self.repo.update(
            {"owner_id": owner_id},
            {
                "chat_ids": doc.chat_ids,
                "new_chat_id": new_chat_id
            }
        )
        if not updated:
            return
        
        return updated
    
    async def delete_chat(self, owner_id: int, chat_id: int) -> ChatOwner | None:
        doc = await self.get(owner_id)

        if not doc:
            return
        
        index = next((i for i, id in enumerate(doc.chat_ids) if id == chat_id), None)
        if not index:
            return
        
        doc.chat_ids.pop(index)

        result = await self.repo.update(
            {"owner_id": owner_id},
            {"chat_ids": doc.chat_ids}
        )
        if not result:
            return
        
        return result