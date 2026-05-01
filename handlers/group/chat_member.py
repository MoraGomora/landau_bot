from datetime import datetime, timezone

from aiogram import Router
from aiogram.types import ChatMemberUpdated, ChatMemberRestricted, ChatMemberBanned
from aiogram.enums import ChatMemberStatus
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, RESTRICTED, KICKED

from core.container import AppContainer
from enums import BanStatus


router = Router(name="chat_member")


async def _set_status(
        container: AppContainer,
        user_id: int,
        chat_id: int,
        status: BanStatus
) -> None:
    result = await container.services.chat_user.set_ban_status(
        user_id,
        chat_id,
        status
    )

    if not result:
        await container.logger.aerror(
            "Failed to set status for user",
            user_id=user_id,
            chat_id=chat_id
        )

        return
    
    await container.logger.ainfo(
        "Status set successfully",
        user_id=user_id,
        chat_id=chat_id,
        status=result.status
    )


async def _check_status(update: ChatMemberUpdated, container: AppContainer) -> None:
    restricted = [ChatMemberStatus.RESTRICTED, ChatMemberStatus.KICKED]

    user_id = update.new_chat_member.user.id
    chat_id = update.chat.id

    user = await update.bot.get_chat_member(
        chat_id,
        user_id
    )

    if not user:
        return
    
    if user.status not in restricted:
        await container.logger.ainfo(
            "User was unbanned before the task was executed",
            user_id=user_id,
            chat_id=chat_id
        )

        return
    
    result = await update.bot.unban_chat_member(
        chat_id,
        user_id
    )

    if not result:
        await container.logger.aerror(
            "Failed to unban user",
            user_id=user_id,
            chat_id=chat_id
        )

        return
    
    status = BanStatus.UNBANNED if user.status not in restricted else BanStatus.BANNED
    await _set_status(
        container,
        user_id,
        chat_id,
        status
    )


def _shedule_task(
        update: ChatMemberUpdated,
        container: AppContainer
) -> int | None:
    if update.new_chat_member.until_date:
        until_seconds = (update.new_chat_member.until_date - datetime.now(timezone.utc)).total_seconds() + 10

        container.task_manager.shedule(
            f"ban_member:{update.chat.id}:{update.new_chat_member.user.id}",
            lambda: _check_status(update, container),
            int(until_seconds)
        )

        return int(until_seconds)
    
    return None


async def send_msg(
        update: ChatMemberUpdated,
        container: AppContainer,
        duration: int,
        reason: str
) -> None:
    if not await container.services.user.get_has_private(update.new_chat_member.user.id):
        await container.logger.awarning(
            "Message can't be send in private messages because the user doesn't have an active private message",
            user_id=update.new_chat_member.user.id
        )

        return

    result = await update.bot.send_message(
        update.new_chat_member.user.id,
        container.translator.call(
            "restriction-notification",
            user=update.new_chat_member.user.full_name,
            chat_name=update.chat.full_name,
            duration_msg=container.translator.duration(duration),
            admin=update.from_user.full_name,
            reason=reason
        )
    )

    if not result:
        await container.logger.aerror(
            "Failed to send message to user about restriction",
            user_id=update.new_chat_member.user.id
        )

        return
    
    await container.logger.ainfo(
        "Message about restriction was sent to user successfully",
        user_id=update.new_chat_member.user.id,
        chat_id=update.chat.id,
        duration=duration,
        reason=reason
    )


@router.chat_member(ChatMemberUpdatedFilter(RESTRICTED | KICKED))
async def restricted_chat_member(update: ChatMemberUpdated, container: AppContainer) -> None:
    await container.logger.ainfo(
        "User was restricted in the chat",
        user_id=update.new_chat_member.user.id,
        admin_id=update.from_user.id,
        chat_id=update.chat.id
    )

    await _set_status(
        container,
        update.new_chat_member.user.id,
        update.chat.id,
        BanStatus.BANNED
    )

    until_seconds = _shedule_task(update, container)

    if not until_seconds:
        return
    
    me = await update.bot.get_me()

    if update.from_user.id == me.id:
        reason = container.translator.call("reason")
    else:
        reason = container.translator.call("not")
    
    await send_msg(update, container, until_seconds, reason)
