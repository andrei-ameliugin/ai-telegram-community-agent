from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from domain.actions import Action


class Outcome(Enum):
    """Possible outcomes of evaluating an event."""

    REPLY = "reply"
    IGNORE = "ignore"


@dataclass(frozen=True)
class Decision:
    """Structured result of evaluating an event.

    A decision must not perform side effects.
    IGNORE decisions always have an empty actions list.
    """

    outcome: Outcome
    actions: list[Action] = field(default_factory=list)
    reason: str | None = None
    requires_approval: bool = False
