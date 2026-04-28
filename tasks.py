import time

from aiogram import Bot
from aiogram.enums import ChatMemberStatus

from core.container import AppContainer
from handlers.common import BanService, utils
from enums import BanStatus


async def check_users_status(bot: Bot, container: AppContainer) -> None:
    users = await container.services.chat_user.get_users_with_uncomplete_status()
    if not users:
        return
    
    ban_service = BanService(bot, container)
    for user in users:
        await ban_service.ban_member(
            user.chat_id,
            user.user_id,
            user.full_name,
            "worker-task"
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
                await container.logger.adebug(
                    "The message sent to owner successfully",
                    owner_id=owner
                )

        return
    
    await container.logger.adebug(
        "MongoDB is alive",
        status=is_connected
    )


async def check_user_ban_status(bot: Bot, container: AppContainer) -> None:
    chat_users = await container.services.chat_user.get_all()
    if not chat_users:
        return
    
    for user in chat_users:
        user_status = await bot.get_chat_member(user.chat_id, user.user_id)

        if not user_status:
            return
        
        if user_status.status in [ChatMemberStatus.KICKED, ChatMemberStatus.RESTRICTED]:
            status = BanStatus.BANNED
        else:
            status = BanStatus.UNBANNED
        
        result = await container.services.chat_user.set_ban_status(
            user.user_id,
            user.chat_id,
            status
        )

        if not result:
            return
        
        await container.logger.adebug(
            "Chat user status was changed",
            chat_id=user.chat_id,
            user_id=user.user_id,
            user_name=user.full_name,
            status=status
        )


async def unban_member(bot: Bot, container: AppContainer) -> None:
    chat_users = await container.services.chat_user.get_all()

    if not chat_users:
        return
    
    for user in chat_users:
        user_violation = await container.services.chat_user.get_violation_data(
            user.user_id, user.chat_id, utils.today()
        )

        if not user_violation:
            return
        
        if not user_violation.until > int(time.time()):
            return
        
        result = await bot.unban_chat_member(
            user.chat_id, user.user_id
        )

        if not result:
            return
        
        status = await container.services.chat_user.set_ban_status(
            user.user_id, user.chat_id, BanStatus.UNBANNED
        )

        if not status:
            return
            