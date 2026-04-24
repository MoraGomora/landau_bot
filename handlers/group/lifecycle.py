import asyncio

from aiogram import Router, F
from aiogram.types import Message, ContentType
from aiogram.exceptions import TelegramBadRequest

from core.container import AppContainer

from . import utils


router = Router(name="lifecycle")


@router.message(F.content_type == ContentType.NEW_CHAT_MEMBERS)
async def new_members(msg: Message, container: AppContainer) -> None:
    try:
        deleted = await msg.delete()
        if deleted:
            await container.logger.ainfo(
                "Service message deleted successfully",
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
                await utils.ban_member(
                    msg.bot,
                    container,
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
        await utils.ban_member(
            msg.bot,
            container,
            msg.chat.id,
            msg.from_user.id,
            member.full_name,
            msg.content_type
        )
    

@router.message(F.content_type == ContentType.LEFT_CHAT_MEMBER)
async def new_members(msg: Message, container: AppContainer) -> None:
    me = await msg.bot.get_me()
    if msg.left_chat_member.id == me.id:
        return
    
    try:
        deleted = await msg.delete()
        if deleted:
            await container.logger.ainfo(
                "Service message deleted successfully",
                chat_id=msg.chat.id,
                content_type=msg.content_type
            )
    except TelegramBadRequest as e:
        await container.logger.ainfo(
            "Failed to delete service message",
            chat_id=msg.chat.id,
            content_type=msg.content_type,
            error=str(e)
        )
        return