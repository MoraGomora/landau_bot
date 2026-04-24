from aiogram import Bot

from core.container import AppContainer
from handlers.group.utils import ban_member


async def check_users_status(bot: Bot, container: AppContainer) -> None:
    users = await container.services.chat_user.get_users_with_uncomplete_status()
    if not users:
        await container.logger.ainfo(
            "Users with uncompeted status was not found"
        )

        return
    
    for user in users:
        await ban_member(
            bot,
            container,
            user.chat_id,
            user.user_id,
            user.full_name,
            "worker-task"
        )


async def delete_message(bot: Bot, container: AppContainer) -> None:
    if not container.msgs_cache:
        return
    
    for chat_id, msg_id in container.msgs_cache.items():
        result = await bot.delete_message(chat_id, msg_id)
        if not result:
            await container.logger.aerror(
                "Failed to delete a message from chat",
                message_id=msg_id,
                chat_id=chat_id
            )

            return
        
        await container.logger.ainfo(
            "Message deleted successfully from the chat",
            message_id=msg_id,
            chat_id=chat_id
        )


async def test_db(owners: list, bot: Bot, container: AppContainer) -> None:
    is_connected = await container.repositories.ping()
    if not is_connected:
        await container.logger.aerror(
            "Failed to connect to MongoDB",
            status=is_connected
        )

        for owner in owners:
            await container.logger.ainfo(
                "Informating owner about connection problem...",
                owner_id=owner
            )

            result = await bot.send_message(
                owner,
                "Failed to connect to MongoDB. Check internet connection or add new IP address in MongoDB -> Network config"
            )
            if result:
                await container.logger.ainfo(
                    "The message sent to owner successfully",
                    owner_id=owner
                )

        return
    
    await container.logger.ainfo(
        "MongoDB is alive",
        status=is_connected
    )