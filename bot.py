import asyncio
import signal

import structlog
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from structlog.typing import FilteringBoundLogger

from fluent.runtime import FluentLocalization

from config_reader import get_config, get_env_or_config, URL, BotConfig, LogConfig, L10nConfig, ThrottlingConfig, MongoConfig
from logs import get_structlog_config
from fluent_loader import get_fluent_localization
from middlewares import L10nMiddleware, ThrottlingMiddleware, ContainerMiddleware
from handlers import register_all_handlers
from core.container import AppContainer
from core import SimpleWorker
import db
import tasks


def register_tasks(owners: list, bot: Bot, container: AppContainer):
    container.worker_manager.register(
        SimpleWorker(
            "check-users-status",
            lambda: tasks.check_users_status(
                bot,
                container
            ),
            60
        )
    )
    container.worker_manager.register(
        SimpleWorker(
            "delete-messages",
            lambda: tasks.delete_message(
                bot,
                container
            ),
            45
        )
    )
    container.worker_manager.register(
        SimpleWorker(
            "test-db-connection",
            lambda: tasks.test_db(
                owners,
                bot,
                container
            ),
            30
        )
    )


async def on_startup(owners: list, bot: Bot, container: AppContainer, logger: FilteringBoundLogger) -> None:
    """Actions to perform on bot startup."""
    register_tasks(owners, bot, container)
    container.worker_manager.start_all()
    
    bot_info = await bot.get_me()
    await logger.ainfo(
        "Bot started",
        username=bot_info.username,
        bot_id=bot_info.id,
    )


async def on_shutdown(bot: Bot, container: AppContainer, logger: FilteringBoundLogger) -> None:
    """Actions to perform on bot shutdown."""
    container.worker_manager.stop_all()

    me = await bot.get_me()
    await logger.ainfo(
        "Bot stopped",
        username=me.username,
        bot_id=me.id
    )


def setup_middlewares(dp: Dispatcher, container: AppContainer, locale: FluentLocalization, throttling_config: ThrottlingConfig) -> None:
    """Register all middlewares."""

    if throttling_config.enabled:
        dp.message.outer_middleware(ThrottlingMiddleware(
            rate_limit=throttling_config.rate_limit,
            max_users=throttling_config.max_users,
        ))

    dp.message.outer_middleware(L10nMiddleware(locale))
    dp.callback_query.outer_middleware(L10nMiddleware(locale))
    dp.pre_checkout_query.outer_middleware(L10nMiddleware(locale))

    dp.update.middleware(ContainerMiddleware(container))


async def main() -> None:
    """Main entry point."""
    log_config = get_config(model=LogConfig, root_key="logs")
    structlog.configure(**get_structlog_config(log_config))

    logger: FilteringBoundLogger = structlog.get_logger()

    bot_config = get_config(model=BotConfig, root_key="bot")
    l10n_config = get_config(model=L10nConfig, root_key="localization")
    mongo_config = get_config(MongoConfig, root_key="mongodb")

    redis_url = get_env_or_config(
        "REDIS_URL", URL,
        "redis", "url"
    )

    try:
        throttling_config = get_config(model=ThrottlingConfig, root_key="throttling")
    except KeyError:
        throttling_config = ThrottlingConfig()

    bot = Bot(
        token=bot_config.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()

    locale = get_fluent_localization(
        locale=l10n_config.default_locale,
        locales_dir=l10n_config.locales_path,
    )

    storage = await db.create_storage(logger, redis_url)

    container = AppContainer(
        storage,
        mongo_config,
        locale,
        logger
    )

    setup_middlewares(dp, container, locale, throttling_config)
    register_all_handlers(dp)

    stop_event = asyncio.Event()

    def signal_handler() -> None:
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, signal_handler)
        except NotImplementedError:
            pass

    await on_startup(bot_config.owners, bot, container, logger)

    try:
        polling_task = asyncio.create_task(
            dp.start_polling(bot, skip_updates=False)
        )

        await stop_event.wait()
        await logger.ainfo("Shutdown signal received...")

        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            pass

    finally:
        await on_shutdown(bot, container, logger)
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        pass
