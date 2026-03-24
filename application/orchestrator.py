from __future__ import annotations

import logging

from application.context import Context, ContextResolver
from domain.decisions import Decision
from domain.events import MessageCreatedEvent
from engines.moderation import ModerationEngine

logger = logging.getLogger(__name__)

_COMPONENT = "orchestrator"


class Orchestrator:
    """Central coordination layer.

    Routes events to engines and returns decisions.
    Resolves context before calling engines.
    Does NOT execute actions — that responsibility belongs to the caller.
    """

    def __init__(
        self,
        moderation_engine: ModerationEngine,
        context_resolver: ContextResolver,
    ) -> None:
        self._moderation_engine = moderation_engine
        self._context_resolver = context_resolver

    def handle_event(self, event: MessageCreatedEvent) -> Decision:
        """Resolve context, evaluate event through engines, return decision."""
        logger.info(
            "Event received",
            extra={
                "component": _COMPONENT,
                "correlation_id": event.correlation_id,
                "event_type": "MessageCreatedEvent",
                "chat_id": event.chat_id,
                "user_id": event.user_id,
                "message_id": event.message_id,
            },
        )

        context = self._context_resolver.resolve(
            bot_id=0,  # TODO: resolve from event when multi-bot is wired
            chat_id=event.chat_id,
        )

        decision = self._moderation_engine.evaluate(event, context)

        logger.info(
            "Decision produced",
            extra={
                "component": _COMPONENT,
                "correlation_id": event.correlation_id,
                "outcome": decision.outcome.value,
                "action_count": len(decision.actions),
                "reason": decision.reason,
                "requires_approval": decision.requires_approval,
            },
        )

        return decision

