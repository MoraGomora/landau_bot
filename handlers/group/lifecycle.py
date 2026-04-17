import asyncio

from aiogram import Router, F
from aiogram.types import Message, ContentType
from aiogram.exceptions import TelegramBadRequest

import structlog
from structlog.typing import FilteringBoundLogger


router = Router(name="lifecycle")
logger: FilteringBoundLogger = structlog.get_logger()


@router.message(F.content_type == ContentType.NEW_CHAT_MEMBERS)
async def new_members(msg: Message):
    try:
        deleted = await msg.delete()
        if deleted:
            await logger.ainfo(
                "Service message deleted successfully",
                chat_id=msg.chat.id,
                content_type=msg.content_type
            )
    except TelegramBadRequest as e:
        await logger.ainfo(
            "Failed to delete service message",
            chat_id=msg.chat.id,
            content_type=msg.content_type,
            error=str(e)
        )
        return

    if msg.new_chat_members:
        await logger.ainfo(
            "User add new members to group. Start banning process...",
            chat_id=msg.chat.id,
            content_type=msg.content_type
        )

        for member in msg.new_chat_members:
            try:
                await logger.ainfo(
                    "Banning member...",
                    chat_id=msg.chat.id,
                    content_type=msg.content_type,
                    member=member.id
                )
                
                banned_member = await msg.bot.ban_chat_member(msg.chat.id, member.id)
                if banned_member:
                    await logger.ainfo(
                        "Member banned successfully",
                        chat_id=msg.chat.id,
                        content_type=msg.content_type,
                        member=member.id
                    )
                    await msg.answer("User was banned successfully")
                
                await asyncio.sleep(0.1)
            except TelegramBadRequest as e:
                await logger.aerror(
                    "Failed to ban member from group",
                    chat_id=msg.chat.id,
                    content_type=msg.content_type,
                    member=member.id,
                    error=str(e)
                )
                return
        return
    
    await logger.ainfo(
        "New user join to the group. Start banning process...",
        chat_id=msg.chat.id,
        content_type=msg.content_type
    )

    banned = await msg.bot.ban_chat_member(msg.chat.id, msg.from_user.id)
    if banned:
        await logger.ainfo(
            "Member banned successfully",
            chat_id=msg.chat.id,
            content_type=msg.content_type,
            member=msg.from_user.id
        )
        await msg.answer("User was banned successfully")
        return
    

@router.message(F.content_type == ContentType.LEFT_CHAT_MEMBER)
async def new_members(msg: Message):
    try:
        deleted = await msg.delete()
        if deleted:
            await logger.ainfo(
                "Service message deleted successfully",
                chat_id=msg.chat.id,
                content_type=msg.content_type
            )
    except TelegramBadRequest as e:
        await logger.ainfo(
            "Failed to delete service message",
            chat_id=msg.chat.id,
            content_type=msg.content_type,
            error=str(e)
        )
        return