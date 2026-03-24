from __future__ import annotations

import asyncio
import logging
import signal

from application.orchestrator import Orchestrator
from config import Settings
from engines.moderation import ModerationEngine
from infrastructure.db.session import build_engine, build_session_factory
from infrastructure.executor import ActionExecutor
from infrastructure.telegram_client import TelegramClient
from transport.poller import Poller

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


class _StructuredFormatter(logging.Formatter):
    """Appends extra fields as key=value pairs to log messages."""

    _SKIP_KEYS = frozenset(
        logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys()
    )

    def format(self, record: logging.LogRecord) -> str:
        extra_fields = {
            k: v
            for k, v in record.__dict__.items()
            if k not in self._SKIP_KEYS
        }
        if extra_fields:
            pairs = " ".join(f"{k}={v}" for k, v in extra_fields.items())
            record.msg = f"{record.msg} | {pairs}"
        return super().format(record)


for _h in logging.root.handlers:
    _h.setFormatter(
        _StructuredFormatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )

logger = logging.getLogger(__name__)


async def main() -> None:
    settings = Settings.from_env()

    # Database
    engine = build_engine(settings.database_url)
    session_factory = build_session_factory(engine)
    logger.info("Database session factory ready")

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
        engine.dispose()
        await telegram_client.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())

