from __future__ import annotations

import logging

from domain.decisions import Decision
from domain.events import MessageCreatedEvent
from engines.moderation import ModerationEngine

logger = logging.getLogger(__name__)


class Orchestrator:
    """Central coordination layer.

    Routes events to engines and returns decisions.
    Does NOT execute actions — that responsibility belongs to the caller.
    """

    def __init__(self, moderation_engine: ModerationEngine) -> None:
        self._moderation_engine = moderation_engine

    def handle_event(self, event: MessageCreatedEvent) -> Decision:
        """Evaluate an event through the engine pipeline and return a decision."""
        logger.info(
            "Processing event: correlation_id=%s, chat_id=%d, user_id=%d",
            event.correlation_id,
            event.chat_id,
            event.user_id,
        )

        decision = self._moderation_engine.evaluate(event)

        logger.info(
            "Decision: outcome=%s, actions=%d, reason=%s, correlation_id=%s",
            decision.outcome.value,
            len(decision.actions),
            decision.reason,
            event.correlation_id,
        )

        return decision
