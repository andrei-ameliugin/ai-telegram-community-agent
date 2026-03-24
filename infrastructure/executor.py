from __future__ import annotations

import logging

from domain.actions import Action, ActionType
from infrastructure.telegram_client import TelegramClient

logger = logging.getLogger(__name__)

_COMPONENT = "executor"


class ActionExecutor:
    """Executes actions by dispatching to the appropriate infrastructure call.

    This is the only layer allowed to perform external side effects.
    All required data comes from the action payload — the executor
    does not receive the original event.
    """

    def __init__(self, telegram_client: TelegramClient) -> None:
        self._telegram_client = telegram_client

    async def execute(
        self,
        actions: list[Action],
        correlation_id: str | None = None,
    ) -> None:
        """Execute a list of actions sequentially."""
        for action in actions:
            await self._execute_one(action, correlation_id)

    async def _execute_one(
        self,
        action: Action,
        correlation_id: str | None,
    ) -> None:
        if action.action_type == ActionType.SEND_REPLY:
            await self._handle_send_reply(action, correlation_id)
        else:
            logger.warning(
                "Unknown action type",
                extra={
                    "component": _COMPONENT,
                    "correlation_id": correlation_id,
                    "action_type": str(action.action_type),
                },
            )

    async def _handle_send_reply(
        self,
        action: Action,
        correlation_id: str | None,
    ) -> None:
        chat_id = action.payload["chat_id"]
        text = action.payload["text"]
        reply_to_message_id = action.payload.get("reply_to_message_id")

        log_extra = {
            "component": _COMPONENT,
            "correlation_id": correlation_id,
            "action_type": ActionType.SEND_REPLY.value,
            "chat_id": chat_id,
            "reply_to_message_id": reply_to_message_id,
        }

        logger.info("Action execution started", extra=log_extra)

        try:
            await self._telegram_client.send_message(
                chat_id=chat_id,
                text=text,
                reply_to_message_id=reply_to_message_id,
            )
            logger.info("Action execution succeeded", extra=log_extra)

        except Exception:
            logger.exception("Action execution failed", extra=log_extra)
            raise
