import asyncio

from aiogram import Router, F
from aiogram.types import Message, ContentType
from aiogram.exceptions import TelegramBadRequest

from fluent.runtime import FluentLocalization

from core.container import AppContainer

from . import utils


router = Router(name="lifecycle")


@router.message(F.content_type == ContentType.NEW_CHAT_MEMBERS)
async def new_members(
    msg: Message, container: AppContainer,
    l10n: FluentLocalization
):
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

    if msg.new_chat_members:
        await container.logger.ainfo(
            "User add new members to group. Start banning process...",
            chat_id=msg.chat.id,
            content_type=msg.content_type,
            count_of_users=len(msg.new_chat_members)
        )

        for member in msg.new_chat_members:
            await utils.ban_member(
                msg, container,
                msg.chat.id, member.id,
                member.full_name
            )

            await asyncio.sleep(0.1)
        return
    
    await container.logger.ainfo(
        "New user join to the group. Start banning process...",
        chat_id=msg.chat.id,
        member_id=msg.from_user.id,
        content_type=msg.content_type
    )

    await utils.ban_member(
        msg, container,
        msg.chat.id, msg.from_user.id,
        msg.from_user.full_name
    )
    

@router.message(F.content_type == ContentType.LEFT_CHAT_MEMBER)
async def new_members(msg: Message, container: AppContainer):
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