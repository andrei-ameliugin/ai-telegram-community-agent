from __future__ import annotations

import asyncio
import logging
import signal

from application.orchestrator import Orchestrator
from config import Settings
from engines.moderation import ModerationEngine
from infrastructure.executor import ActionExecutor
from infrastructure.telegram_client import TelegramClient
from transport.poller import Poller

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    settings = Settings.from_env()

    # Infrastructure
    telegram_client = TelegramClient(bot_token=settings.telegram_bot_token)
    executor = ActionExecutor(telegram_client=telegram_client)

    # Engines
    moderation_engine = ModerationEngine()

    # Application
    orchestrator = Orchestrator(moderation_engine=moderation_engine)

    # Transport
    poller = Poller(
        telegram_client=telegram_client,
        orchestrator=orchestrator,
        executor=executor,
        polling_timeout=settings.polling_timeout,
        retry_delay=settings.polling_retry_delay,
    )

    # Graceful shutdown on SIGINT / SIGTERM
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, poller.stop)

    try:
        logger.info("Starting bot…")
        await poller.run()
    finally:
        await telegram_client.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
