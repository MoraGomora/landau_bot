import asyncio

from aiogram import Router, F
from aiogram.types import Message, ContentType
from aiogram.exceptions import TelegramBadRequest

from core.container import AppContainer
from handlers.common.ban_service import BanService
from config_reader import get_config, BotConfig


router = Router(name="lifecycle")


@router.message(F.content_type == ContentType.NEW_CHAT_MEMBERS)
async def new_chat_members(msg: Message, container: AppContainer) -> None:
    try:
        deleted = await msg.delete()
        if deleted:
            await container.logger.ainfo(
                "Service message deleted successfully after new members joined",
                chat_id=msg.chat.id,
                content_type=msg.content_type
            )
    except TelegramBadRequest as e:
        await container.logger.aerror(
            "Failed to delete service message",
            chat_id=msg.chat.id,
            content_type=msg.content_type,
            error=str(e)
        )
        return
    
    bot_config = get_config(model=BotConfig, root_key="bot")
    if msg.from_user.id in bot_config.owners:
        await container.logger.ainfo(
            "Bot owner enter to the chat",
            owner_id=msg.from_user.id,
            owner_name=msg.from_user.full_name,
            chat_id=msg.chat.id
        )
    
    me = await msg.bot.get_me()

    if msg.new_chat_members:
        await container.logger.ainfo(
            "User add new members to group. Start banning process...",
            chat_id=msg.chat.id,
            content_type=msg.content_type,
            count_of_users=len(msg.new_chat_members)
        )

        for member in msg.new_chat_members:
            if member.id == me.id:
                await container.logger.ainfo(
                    "User add me to the chat. I can't restrict myself",
                    chat_id=msg.chat.id,
                    user_id=msg.from_user.id,
                    content_type=msg.content_type
                )
                continue
            
            async with container.ban_member_lock:
                ban_service = BanService(msg.bot, container)
                await ban_service.ban_member(
                    msg.chat.id,
                    member.id,
                    member.full_name,
                    msg.content_type
                )

            await asyncio.sleep(0.1)
        return
    
    await container.logger.ainfo(
        "New user join to the group. Start banning process...",
        chat_id=msg.chat.id,
        member_id=msg.from_user.id,
        content_type=msg.content_type
    )

    async with container.ban_member_lock:
        ban_service = BanService(msg.bot, container)
        await ban_service.ban_member(
            msg.chat.id,
            msg.from_user.id,
            member.full_name,
            msg.content_type
        )
    

@router.message(F.content_type == ContentType.LEFT_CHAT_MEMBER)
async def left_chat_member(msg: Message, container: AppContainer) -> None:
    me = await msg.bot.get_me()
    if msg.left_chat_member.id == me.id:
        await container.logger.ainfo(
            "Bot was kicked or leave from chat",
            chat_id=msg.chat.id
        )

        return
    
    try:
        deleted = await msg.delete()
        if deleted:
            await container.logger.ainfo(
                "Service message deleted successfully after user left the chat",
                chat_id=msg.chat.id,
                content_type=msg.content_type
            )
    except TelegramBadRequest as e:
        await container.logger.aerror(
            "Failed to delete service message",
            chat_id=msg.chat.id,
            content_type=msg.content_type,
            error=str(e)
        )
        return
    

@router.message(F.content_type == ContentType.NEW_CHAT_TITLE)
async def chat_title_changed(msg: Message, container: AppContainer) -> None:
    try:
        deleted = await msg.delete()
        if deleted:
            await container.logger.ainfo(
                "Service message deleted successfully after chat title changed",
                chat_id=msg.chat.id,
                content_type=msg.content_type
            )
    except TelegramBadRequest as e:
        await container.logger.aerror(
            "Failed to delete service message",
            chat_id=msg.chat.id,
            content_type=msg.content_type,
            error=str(e)
        )
        return
    
    if not await container.services.settings.get(msg.chat.id):
        await container.logger.awarning(
            "Settings for this chat not found. Can't update chat title",
            chat_id=msg.chat.id
        )

        return
    
    result = await container.services.settings.change_chat_title(
        msg.chat.id, msg.chat.title
    )
    if not result:
        await container.logger.aerror(
            "Failed to update chat title in settings",
            chat_id=msg.chat.id,
            new_title=msg.chat.title
        )

        return
    
    await container.logger.ainfo(
        "Chat title updated successfully in settings",
        chat_id=msg.chat.id,
        new_title=msg.chat.title
    )