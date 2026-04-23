from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from fluent.runtime import FluentLocalization

from core.container import AppContainer


router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, container: AppContainer) -> None:
    """Handle /start command for regular users."""
    print("jkfhkjdshfkjsdhfkjsdhhk")
    if not await container.services.user.is_available(message.from_user.id):
        result = await container.services.user.create(
            message.from_user.id,
            True
        )
        if not result:
            return
        
    await container.logger.ainfo(
        "User started bot",
        user_id=message.from_user.id if message.from_user else None,
        username=message.from_user.username if message.from_user else None,
    )
    await message.answer(
        container.translator.call(
            "hello-msg"
        )
    )


@router.message(Command("help"))
async def cmd_help(message: Message, l10n: FluentLocalization) -> None:
    """Handle /help command."""
    await message.answer(l10n.format_value("help-msg"))


@router.message(F.content_type.in_({"photo", "video"}))
async def on_media(message: Message, l10n: FluentLocalization) -> None:
    """React to photo and video messages."""
    await message.reply(l10n.format_value("media-msg"))
