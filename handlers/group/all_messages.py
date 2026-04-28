from aiogram import Router
from aiogram.types import Message

from core.container import AppContainer


router = Router(name="all_messages")


@router.message()
async def all_messages(msg: Message, container: AppContainer) -> None:
    if msg.sender_chat:
        return

    if not await container.services.chat_user.get(msg.from_user.id, msg.chat.id):
        result = await container.services.chat_user.create(
            msg.from_user.id,
            msg.from_user.full_name,
            msg.chat.id
        )

        if not result:
            return