from datetime import datetime, timedelta

import os
import time

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest

from core.container import AppContainer
from handlers.common import BanService, utils
from enums import BanStatus
from utils import send_logs


async def check_users_status(bot: Bot, container: AppContainer) -> None:
    users = await container.services.chat_user.get_users_with_uncomplete_status()
    if not users:
        return
    
    ban_service = BanService(bot, container)
    me = await bot.get_me()

    for user in users:
        admins = await bot.get_chat_administrators(user.chat_id)

        if not admins:
            await container.logger.aerror(
                "Failed to get chat administrators from Telegram. Skip current iteration...",
                chat_id=user.chat_id
            )

            continue

        if user.user_id in [admin.user.id for admin in admins]:
            await container.logger.adebug(
                "User is administrator in the chat. Skip banning...",
                user_id=user.user_id,
                chat_id=user.chat_id
            )

            continue

        if user.user_id == me.id:
            await container.logger.adebug(
                "User is the bot itself. Skip banning...",
                user_id=user.user_id,
                chat_id=user.chat_id
            )

            continue

        await ban_service.ban_member(
            user.chat_id,
            user.user_id,
            user.full_name,
            "worker-task"
        )


async def test_db(owners: list, bot: Bot, container: AppContainer) -> None:
    is_connected, error_message = await container.repositories.ping()
    if not is_connected:
        await container.logger.aerror(
            "Failed to connect to MongoDB",
            status=is_connected,
            error=error_message
        )

        for owner in owners:
            await container.logger.ainfo(
                "Informating owner about connection problem...",
                owner_id=owner
            )

            result = await bot.send_message(
                owner,
                "Failed to connect to MongoDB server. Bot catch exception when trying to ping:\n\n" + error_message
            )
            if result:
                await container.logger.adebug(
                    "The message sent to owner successfully",
                    owner_id=owner
                )
            else:
                await container.logger.aerror(
                    "Failed to send message to owner about MongoDB connection problem",
                    owner_id=owner
                )

        exit(1)
    
    await container.logger.adebug(
        "MongoDB is alive",
        status=is_connected
    )


async def check_user_ban_status(bot: Bot, container: AppContainer) -> None:
    chat_users = await container.services.chat_user.get_all()
    if not chat_users:
        await container.logger.aerror(
            "Failed to get all chat users"
        )

        return
    
    restricted = [ChatMemberStatus.KICKED, ChatMemberStatus.RESTRICTED]

    for user in chat_users:
        try:
            user_status = await bot.get_chat_member(user.chat_id, user.user_id)

            if not user_status:
                await container.logger.aerror(
                    "Failed to get chat member from Telegram. Skip current iteration...",
                    user_id=user.user_id,
                    chat_id=user.chat_id
                )

                continue

            await container.logger.adebug(
                "Got user status from Telegram. Checking if it is correct with the database record...",
                user_id=user.user_id,
                chat_id=user.chat_id,
                telegram_status=user_status.status,
                db_status=user.status
            )
            
            status = BanStatus.BANNED if user_status.status in restricted else BanStatus.UNBANNED
            result = await container.services.chat_user.set_ban_status(
                user.user_id,
                user.chat_id,
                status
            )

            if not result:
                await container.logger.aerror(
                    "Failed to set ban status for chat user. Skip current iteration...",
                    user_id=user.user_id,
                    chat_id=user.chat_id
                )

                continue

            await container.logger.adebug(
                "Ban status for user was set successfully",
                user_id=user.user_id,
                chat_id=user.chat_id,
                status=result.status
            )
        except TelegramBadRequest as e:
            await container.logger.aerror(
                "Telegram error while getting chat member. Skip current iteration...",
                user_id=user.user_id,
                chat_id=user.chat_id,
                error=str(e)
            )

            return


async def unban_member(bot: Bot, container: AppContainer) -> None:
    chat_users = await container.services.chat_user.get_all()

    if not chat_users:
        await container.logger.aerror(
            "Failed to get all chat users"
        )

        return
    
    await container.logger.adebug(
        "Got all chat users. Starting to check each user for unbanning...",
        users_count=len(chat_users)
    )
    
    for user in chat_users:
        user_violation = await container.services.chat_user.get_violation_data(
            user.user_id, user.chat_id, utils.today()
        )

        if not user_violation:
            await container.logger.adebug(
                "User violation was not found",
                user_id=user.user_id,
                chat_id=user.chat_id
            )

            return
        
        if not user_violation.until > int(time.time()):
            await container.logger.adebug(
                "User has an active violation. Skip current iteratiion...",
                user_id=user.user_id,
                chat_id=user.chat_id
            )

            continue

        await container.logger.adebug(
            "User violation time is expired. Trying to unban the user...",
            user_id=user.user_id,
            chat_id=user.chat_id
        )
        
        result = await bot.unban_chat_member(
            user.chat_id, user.user_id
        )

        if not result:
            await container.logger.aerror(
                "Failed to unban chat member. Skip current iteration...",
                user_id=user.user_id,
                chat_id=user.chat_id
            )

            continue
        
        status = await container.services.chat_user.set_ban_status(
            user.user_id, user.chat_id, BanStatus.UNBANNED
        )

        if not status:
            await container.logger.aerror(
                "Failed to set ban status for the user. Skip current iteration...",
                user_id=user.user_id,
                chat_id=user.chat_id
            )

            continue
        
        await container.logger.adebug(
            "User was unbanned successfully",
            user_id=user.user_id,
            chat_id=user.chat_id
        )


async def send_daily_logs(bot: Bot, owners: list[int], container: AppContainer) -> None:
    now = datetime.now()
    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    path = f"logs/{yesterday}.log"
    
    if not os.path.exists(path):
        return
    
    if now.hour != 0:
        return
    
    for owner_id in owners:
        await container.logger.adebug(
            "Sending daily logs to owner...",
            owner_id=owner_id,
            log_file=path
        )

        await send_logs(
            bot,
            owner_id,
            path,
            caption=f"Daily logs for {yesterday}"
        )