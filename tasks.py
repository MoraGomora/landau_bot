from aiogram import Bot

from core.container import AppContainer
from handlers.common.ban_service import BanService


async def check_users_status(bot: Bot, container: AppContainer) -> None:
    users = await container.services.chat_user.get_users_with_uncomplete_status()
    if not users:
        await container.logger.adebug(
            "Users with uncompeted status was not found"
        )

        return
    
    ban_service = BanService(bot, container)
    for user in users:
        await ban_service.ban_member(
            user.chat_id,
            user.user_id,
            user.full_name,
            "worker-task"
        )


async def delete_message(bot: Bot, container: AppContainer) -> None:
    all_msgs = container.memory.get_all()
    if not all_msgs:
        await container.logger.adebug(
            "Messages not found"
        )

        return
    
    for chat_id, msg_id in list(all_msgs.items()):
        if not isinstance(chat_id, int):
            continue

        ids = msg_id if isinstance(msg_id, list) else [msg_id]

        for mid in ids:
            result = await bot.delete_message(chat_id=chat_id, message_id=mid)
            if not result:
                await container.logger.aerror(
                    event="Failed to delete a message from chat",
                    message_id=mid,
                    chat_id=chat_id
                )
                continue

            await container.logger.adebug(
                event="Message deleted successfully from the chat",
                message_id=mid,
                chat_id=chat_id
            )

        container.memory.delete(chat_id)


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
                await container.logger.adebug(
                    "The message sent to owner successfully",
                    owner_id=owner
                )

        return
    
    await container.logger.adebug(
        "MongoDB is alive",
        status=is_connected
    )