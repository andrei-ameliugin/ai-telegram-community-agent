from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MessageCreatedEvent:
    """Normalized domain event for an incoming Telegram message.

    Class type serves as the event identity — no redundant event_type field.
    Created for all messages; text may be None for non-text messages.
    """

    message_id: int
    chat_id: int
    user_id: int
    text: str | None
    occurred_at: datetime
    correlation_id: str
