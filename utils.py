import json
from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile


def save_logs(logs, path: str) -> None:
    full_path = Path(path)
    full_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file=full_path, mode="w", encoding="utf-8") as f:
        for log in logs:
            f.write(json.dumps(obj=log, ensure_ascii=False, default=str) + "\n")

    return full_path


async def send_logs(bot: Bot, chat_id: int, path: str, caption: str) -> None:
    result = await bot.send_document(
        chat_id=chat_id,
        document=FSInputFile(path),
        caption=caption,
        parse_mode="HTML"
    )

    if not result:
        raise Exception("Failed to send logs document")