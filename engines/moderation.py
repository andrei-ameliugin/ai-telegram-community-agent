from __future__ import annotations

import logging

from domain.actions import Action, ActionType
from domain.decisions import Decision, Outcome
from domain.events import MessageCreatedEvent

logger = logging.getLogger(__name__)


class ModerationEngine:
    """Rule-based moderation engine (stub).

    Evaluates a message event and returns a Decision.
    No side effects — returns Decision only.
    """

    def evaluate(self, event: MessageCreatedEvent) -> Decision:
        if event.text is None:
            return Decision(outcome=Outcome.IGNORE, actions=[])

        if "spam" in event.text.lower():
            logger.info(
                "Spam detected in message %d (chat %d, user %d)",
                event.message_id,
                event.chat_id,
                event.user_id,
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

        return Decision(outcome=Outcome.IGNORE, actions=[])
