from __future__ import annotations

import logging

from domain.actions import Action, ActionType
from infrastructure.telegram_client import TelegramClient

logger = logging.getLogger(__name__)


class ActionExecutor:
    """Executes actions by dispatching to the appropriate infrastructure call.

    This is the only layer allowed to perform external side effects.
    All required data comes from the action payload — the executor
    does not receive the original event.
    """

    def __init__(self, telegram_client: TelegramClient) -> None:
        self._telegram_client = telegram_client

    async def execute(self, actions: list[Action]) -> None:
        """Execute a list of actions sequentially."""
        for action in actions:
            await self._execute_one(action)

    async def _execute_one(self, action: Action) -> None:
        if action.action_type == ActionType.SEND_REPLY:
            await self._handle_send_reply(action)
        else:
            logger.warning("Unknown action type: %s", action.action_type)

    async def _handle_send_reply(self, action: Action) -> None:
        chat_id = action.payload["chat_id"]
        text = action.payload["text"]
        reply_to_message_id = action.payload.get("reply_to_message_id")

        logger.info(
            "Executing SEND_REPLY: chat_id=%d, reply_to=%s",
            chat_id,
            reply_to_message_id,
        )

        await self._telegram_client.send_message(
            chat_id=chat_id,
            text=text,
            reply_to_message_id=reply_to_message_id,
        )
