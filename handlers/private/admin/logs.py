import time

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from logs import logs_buffer
from utils import save_logs, send_logs


router = Router(name="logs")


@router.message(Command("logs"))
async def cmd_logs(message: Message, command: CommandObject) -> None:
    """Handle /logs command - show recent logs."""
    LEVEL_EMOJI = {
        "debug": "🐞",
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "critical": "🔥"
    }

    args = command.args.split() if command.args else []

    if not logs_buffer:
        await message.answer("No logs available.")
        return
    
    if len(args) == 2 and args[0].lower() == "save":
        filter_level = args[1].lower()
        filtered = [log for log in logs_buffer if log.get("level", "") == filter_level]

        if not filtered:
            await message.answer(f"No logs found for level: <code>{filter_level}</code>", parse_mode="HTML")
            return
        
        filename = f"logs/temp/export_{filter_level}_{int(time.time())}.log"

        path = save_logs(filtered, filename)
        if not path:
            await message.answer("Failed to save logs to file.")
            return
        
        await send_logs(
            bot=message.bot,
            chat_id=message.chat.id,
            path=path,
            caption=f"Exported logs for level: <code>{filter_level}</code>"
        )

        return

    filter_level = args[0].lower() if args else None

    last_logs = list(logs_buffer)[-10:]
    lines = []
    
    for log in last_logs:
        level = log.get("level", "?")
        event = log.get("event", "?")
        error = log.get("error", "")
        timestamp = log.get("timestamp", "")
        emoji = LEVEL_EMOJI.get(level, "❓")

        if filter_level and level != filter_level:
            continue

        error_line = f"\nError: {error}" if error else ""
        
        lines.append(
            f"{emoji} <b>{level.upper()}</b>\n"
            f"🕐 <i>{timestamp}</i>\n"
            f"📋 {event}"
            f"{error_line}"
        )

    if lines:
        header = f"📜 <b>Logs</b>" + (f" — <code>{filter_level}</code>" if filter_level else "") + f"\n<blockquote>{'─' * 20}</blockquote>\n\n"
        await message.answer(
            text=header + "\n\n".join(lines),
            parse_mode="HTML"
        )
    else:
        await message.answer(text=f"No logs for level: <code>{filter_level}</code>", parse_mode="HTML")