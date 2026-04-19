import time
import json
from datetime import datetime, date

from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

from core.container import AppContainer


def next_ban_duration(
    prev_duration: int | None,
    *,
    base: int = 30,
    multiplier: float = 1.5,
    step: int = 0,
    max_duration: int | None = 3600
) -> int:
    """
    prev_duration: предыдущее время бана (в секундах)
    base: стартовое значение (если это первый бан)
    multiplier: коэффициент роста
    step: дополнительный прирост
    max_duration: потолок (чтобы не улетело в вечность)
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

    key = f"key:{chat_id}:{member_id}:{today()}"
    raw = await container.redis.read(key)
    
    if raw:
        await container.logger.adebug(
            "Data was found. Loading and extracting last violation time...",
            chat_id=chat_id,
            member_id=member_id
        )

        data = json.loads(raw)
        prev_duration = data.get("duration")
    else:
        await container.logger.adebug(
            "Data was not found. Creating a new record about user...",
            chat_id=chat_id,
            member_id=member_id
        )
        prev_duration = None

    duration = next_ban_duration(prev_duration)
    until = int(time.time()) + duration

    new_data = {
        "duration": duration,
        "until": until,
    }

    result = await container.redis.write(
        key,
        json.dumps(new_data)
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
            user = container.translator.mention(member_id, member_name)
            duration_msg = container.translator.duration(duration)

            await container.logger.ainfo(
                "Member banned successfully",
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
        await msg.answer(
            container.translator.call(
                "failed-to-ban",
                {"e": str(e)}
            )
        )
        return