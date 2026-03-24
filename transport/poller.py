from __future__ import annotations

import asyncio
import logging

from application.orchestrator import Orchestrator
from domain.decisions import Outcome
from infrastructure.executor import ActionExecutor
from infrastructure.telegram_client import TelegramClient
from transport.event_mapper import map_update_to_event

logger = logging.getLogger(__name__)


class Poller:
    """Telegram polling ingestion loop.

    Responsibilities:
    - fetch updates from Telegram API
    - track update offsets
    - map updates to domain events
    - pass events to orchestrator
    - pass resulting actions to executor

    No business logic — only wiring.
    """

    def __init__(
        self,
        telegram_client: TelegramClient,
        orchestrator: Orchestrator,
        executor: ActionExecutor,
        polling_timeout: int = 30,
        retry_delay: float = 5.0,
    ) -> None:
        self._telegram_client = telegram_client
        self._orchestrator = orchestrator
        self._executor = executor
        self._polling_timeout = polling_timeout
        self._retry_delay = retry_delay
        self._offset: int | None = None
        self._running = False

    async def run(self) -> None:
        """Start the polling loop. Runs until stopped."""
        self._running = True
        logger.info("Poller started")

        while self._running:
            try:
                updates = await self._telegram_client.get_updates(
                    offset=self._offset,
                    timeout=self._polling_timeout,
                )

                for update in updates:
                    await self._process_update(update)

            except Exception:
                logger.exception("Error during polling cycle, retrying in %.1fs", self._retry_delay)
                await asyncio.sleep(self._retry_delay)

        logger.info("Poller stopped")

    def stop(self) -> None:
        """Signal the polling loop to stop."""
        self._running = False

    async def _process_update(self, update: dict) -> None:
        update_id = update.get("update_id")
        if update_id is not None:
            self._offset = update_id + 1

        event = map_update_to_event(update)
        if event is None:
            return

        try:
            decision = self._orchestrator.handle_event(event)

            if decision.outcome != Outcome.IGNORE and decision.actions:
                await self._executor.execute(decision.actions)

        except Exception:
            logger.exception(
                "Error processing update %s (correlation_id=%s)",
                update_id,
                event.correlation_id,
            )
