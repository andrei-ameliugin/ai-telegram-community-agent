from __future__ import annotations

import logging

from domain.actions import Action, ActionType
from domain.decisions import Decision, Outcome
from domain.events import MessageCreatedEvent

logger = logging.getLogger(__name__)

_COMPONENT = "engine.moderation"


class ModerationEngine:
    """Rule-based moderation engine (stub).

    Evaluates a message event and returns a Decision.
    No side effects — returns Decision only.
    """

    def evaluate(self, event: MessageCreatedEvent) -> Decision:
        logger.debug(
            "Evaluation started",
            extra={
                "component": _COMPONENT,
                "correlation_id": event.correlation_id,
                "message_id": event.message_id,
                "chat_id": event.chat_id,
                "has_text": event.text is not None,
            },
        )

        if event.text is None:
            logger.debug(
                "Decision made: no text content",
                extra={
                    "component": _COMPONENT,
                    "correlation_id": event.correlation_id,
                    "outcome": Outcome.IGNORE.value,
                },
            )
            return Decision(outcome=Outcome.IGNORE, actions=[])

        if "spam" in event.text.lower():
            logger.info(
                "Decision made: spam detected",
                extra={
                    "component": _COMPONENT,
                    "correlation_id": event.correlation_id,
                    "outcome": Outcome.REPLY.value,
                    "message_id": event.message_id,
                    "chat_id": event.chat_id,
                    "user_id": event.user_id,
                },
            )
            action = Action(
                action_type=ActionType.SEND_REPLY,
                payload={
                    "chat_id": event.chat_id,
                    "text": "Spam detected",
                    "reply_to_message_id": event.message_id,
                },
            )
            return Decision(
                outcome=Outcome.REPLY,
                actions=[action],
                reason="Message contains spam keyword",
            )

        logger.debug(
            "Decision made: no violation",
            extra={
                "component": _COMPONENT,
                "correlation_id": event.correlation_id,
                "outcome": Outcome.IGNORE.value,
            },
        )
        return Decision(outcome=Outcome.IGNORE, actions=[])
