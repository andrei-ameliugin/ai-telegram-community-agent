from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ActionType(Enum):
    """Types of side-effects the system can execute."""

    SEND_REPLY = "send_reply"


@dataclass(frozen=True)
class Action:
    """A side-effect to be executed by the execution layer.

    Payload must be self-contained — the executor does not receive
    the original event, so all required data lives here.

    SEND_REPLY payload schema:
        chat_id: int
        text: str
        reply_to_message_id: int
    """

    action_type: ActionType
    payload: dict[str, Any] = field(default_factory=dict)
