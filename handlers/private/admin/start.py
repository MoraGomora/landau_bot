import structlog
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from fluent.runtime import FluentLocalization


router = Router(name="admin")
logger = structlog.get_logger()


@router.message(CommandStart())
async def cmd_owner_hello(message: Message, l10n: FluentLocalization) -> None:
    """Handle /start command for bot owners."""
    await logger.ainfo(
        "Owner started bot",
        user_id=message.from_user.id if message.from_user else None,
    )
    await message.answer(l10n.format_value("hello-owner"))


@router.message(Command("ping"))
async def cmd_ping(message: Message, l10n: FluentLocalization) -> None:
    """Handle /ping command - health check."""
    await message.reply(l10n.format_value("ping-msg"))


@router.message(Command("stats"))
async def cmd_stats(message: Message, l10n: FluentLocalization) -> None:
    """Handle /stats command - show bot statistics."""
    await message.answer(l10n.format_value("stats-msg"))
