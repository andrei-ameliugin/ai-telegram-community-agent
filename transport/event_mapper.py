from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from domain.events import MessageCreatedEvent

logger = logging.getLogger(__name__)


def map_update_to_event(update: dict[str, Any]) -> MessageCreatedEvent | None:
    """Convert a raw Telegram update dict into a domain event.

    Returns None if the update does not contain a processable message.
    Creates events for all messages — text may be None for non-text messages.
    """
    message = update.get("message")
    if message is None:
        return None

    message_id = message.get("message_id")
    chat = message.get("chat")
    from_user = message.get("from")

    if message_id is None or chat is None or from_user is None:
        logger.warning("Malformed message in update %s — skipping", update.get("update_id"))
        return None

    chat_id = chat.get("id")
    user_id = from_user.get("id")

    if chat_id is None or user_id is None:
        logger.warning("Missing chat_id or user_id in update %s — skipping", update.get("update_id"))
        return None

    return MessageCreatedEvent(
        message_id=message_id,
        chat_id=chat_id,
        user_id=user_id,
        text=message.get("text"),  # None for non-text messages
        occurred_at=datetime.now(timezone.utc),
        correlation_id=str(uuid.uuid4()),
    )
