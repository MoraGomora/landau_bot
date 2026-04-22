import time

from datetime import datetime, date

from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

from core.container import AppContainer
from models import Violation
from enums import Status


def next_ban_duration(
    prev_duration: int | None,
    *,
    base: int = 30,
    multiplier: float = 1.5,
    step: int = 0,
    max_duration: int | None = 3600
) -> int:
    """
    prev_duration: previous ban time (in seconds)
    base: starting value (if this is the first ban)
    multiplier: growth rate
    step: additional growth
    max_duration: ceiling (so it doesn't fly away into eternity)
    """

    if prev_duration is None:
        return base

    new = int(prev_duration * multiplier + step)

    if max_duration:
        new = min(new, max_duration)

    return new


def today() -> str:
    return date.today().isoformat()


async def ban_member(
        msg: Message, container: AppContainer,
        chat_id: int, member_id: int,
        member_name: str
) -> bool:
    await container.logger.adebug(
        "Getting info about user from Redis",
        chat_id=chat_id,
        member_id=member_id
    )

    if not await container.services.chat_user.is_available(member_id, chat_id):
        created = await container.services.chat_user.create(member_id, chat_id)
        if not created:
            return
    
    pending = await container.services.chat_user.set_status(member_id, chat_id, Status.PENDING)
    if not pending:
        await msg.answer(
            container.translator.call(
                "status-was-not-updated"
            )
        )

        return

    if await container.services.chat_user.has_violation(member_id, chat_id, today()):
        data = await container.services.chat_user.get_violation_data(
            member_id, chat_id, today()
        )

        if data:
            prev_duration = data.duration
    else:
        prev_duration = None
    
    duration = next_ban_duration(prev_duration)
    until = int(time.time()) + duration

    new_data = Violation(
        duration=duration,
        until=until
    )

    result = await container.services.chat_user.set_violation_data(
        member_id, chat_id, today(), new_data
    )
    if not result:
        await container.logger.aerror(
            "Failed to write a new data about user. Skipping this step...",
            chat_id=chat_id,
            member_id=member_id,
            result=result
        )
    else:
        await container.logger.ainfo(
            "New data about user violation writed or updated successfully",
            chat_id=chat_id,
            member_id=member_id,
            result=result
        )

    await container.logger.ainfo(
        "Start banning member...",
        chat_id=msg.chat.id,
        content_type=msg.content_type,
        member=member_id
    )
    
    try:
        banned = await msg.bot.ban_chat_member(
            chat_id, member_id,
            datetime.fromtimestamp(until)
        )
        if banned:
            done = await container.services.chat_user.set_status(member_id, chat_id, Status.DONE)
            if not done:
                await msg.answer(
                    container.translator.call(
                        "status-was-not-updated"
                    )
                )

                return
            
            attempt = await container.services.chat_user.add_join_attempt(member_id, chat_id)
            if not attempt:
                await msg.answer(
                    container.translator.call(
                        "cannot-count-join-attempt"
                    )
                )

                return
            
            has_send_violation_msg = await container.services.settings.get_has_send_violation_msg(chat_id)
            if not has_send_violation_msg:
                return
            
            user = container.translator.mention(member_id, member_name)
            duration_msg = container.translator.duration(duration)

            await container.logger.ainfo(
                "Member banned successfully. Counting \"join_attempts\"...",
                chat_id=msg.chat.id,
                content_type=msg.content_type,
                member=msg.from_user.id
            )
            
            await msg.answer(
                container.translator.call(
                    "violation-msg",
                    user=user,
                    duration_msg=duration_msg
                )
            )
            
    except TelegramBadRequest as e:
        await container.logger.aerror(
            "Failed to ban member",
            chat_id=msg.chat.id,
            content_type=msg.content_type,
            member=msg.from_user.id,
            error=str(e)
        )

        failed = await container.services.chat_user.set_status(member_id, chat_id, Status.FAILED)
        if not failed:
            await msg.answer(
                container.translator.call(
                    "status-was-not-updated"
                )
            )

            return

        await msg.answer(
            container.translator.call(
                "failed-to-ban",
                e=str(e)
            )
        )
        return