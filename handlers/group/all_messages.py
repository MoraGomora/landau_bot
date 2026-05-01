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
            await container.logger.aerror(
                "Failed to create chat user",
                user_id=msg.from_user.id,
                chat_id=msg.chat.id
            )

            return
        
        await container.logger.ainfo(
            "Chat user record created when user sent a message to the chat",
            user_id=result.user_id,
            full_name=result.full_name,
            chat_id=result.chat_id,
            join_attempts=result.join_attempts,
            status=result.status
        )