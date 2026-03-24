from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session, sessionmaker

from infrastructure.db.models import Bot, BotChatBinding, Chat, PolicyProfile

logger = logging.getLogger(__name__)

_COMPONENT = "context_resolver"


@dataclass(frozen=True)
class ModerationPolicy:
    """Moderation-specific flags extracted from policy config."""

    enabled: bool = True
    require_approval_for_ban: bool = False


@dataclass(frozen=True)
class Context:
    """Resolved runtime context for an event.

    Built from bot + chat + policy_profile before any decision is made.
    Engines receive this — they never access DB directly.
    """

    bot_id: int
    chat_id: int
    policy_name: str | None = None
    moderation: ModerationPolicy = field(default_factory=ModerationPolicy)


def _parse_moderation_policy(config_json: str) -> ModerationPolicy:
    """Extract moderation flags from policy config JSON."""
    try:
        config = json.loads(config_json)
    except (json.JSONDecodeError, TypeError):
        return ModerationPolicy()

    moderation = config.get("moderation")
    if not isinstance(moderation, dict):
        return ModerationPolicy()

    return ModerationPolicy(
        enabled=moderation.get("enabled", True),
        require_approval_for_ban=moderation.get("require_approval_for_ban", False),
    )


class ContextResolver:
    """Resolves runtime context from bot_id + chat_id using repositories.

    Lives in the application layer. Accesses DB via session factory.
    Returns a pure Context object that engines can use without DB access.
    """

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def resolve(self, bot_id: int, chat_id: int) -> Context:
        """Resolve context for a bot + chat pair.

        Returns a default context if no binding or policy is found.
        """
        with self._session_factory() as session:
            binding = (
                session.query(BotChatBinding)
                .filter(
                    BotChatBinding.bot_id == bot_id,
                    BotChatBinding.chat_id == chat_id,
                )
                .first()
            )

            if binding is None:
                logger.debug(
                    "No binding found, using default context",
                    extra={
                        "component": _COMPONENT,
                        "bot_id": bot_id,
                        "chat_id": chat_id,
                    },
                )
                return Context(bot_id=bot_id, chat_id=chat_id)

            policy = binding.policy_profile
            if policy is None:
                logger.debug(
                    "Binding found but no policy profile",
                    extra={
                        "component": _COMPONENT,
                        "bot_id": bot_id,
                        "chat_id": chat_id,
                    },
                )
                return Context(bot_id=bot_id, chat_id=chat_id)

            moderation = _parse_moderation_policy(policy.config_json)

            logger.info(
                "Context resolved",
                extra={
                    "component": _COMPONENT,
                    "bot_id": bot_id,
                    "chat_id": chat_id,
                    "policy_name": policy.name,
                    "moderation_enabled": moderation.enabled,
                },
            )

            return Context(
                bot_id=bot_id,
                chat_id=chat_id,
                policy_name=policy.name,
                moderation=moderation,
            )
