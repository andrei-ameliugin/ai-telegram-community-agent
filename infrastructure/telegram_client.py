from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org"


class TelegramClient:
    """Thin async wrapper around the Telegram Bot API.

    Lives in the infrastructure layer — used by both the poller
    (for fetching updates) and the executor (for sending messages).
    """

    def __init__(self, bot_token: str) -> None:
        self._base_url = f"{TELEGRAM_API_BASE}/bot{bot_token}"
        self._client = httpx.AsyncClient(timeout=60.0)

    async def get_updates(
        self,
        offset: int | None = None,
        timeout: int = 30,
    ) -> list[dict[str, Any]]:
        """Fetch new updates via long polling."""
        params: dict[str, Any] = {"timeout": timeout}
        if offset is not None:
            params["offset"] = offset

        response = await self._client.get(
            f"{self._base_url}/getUpdates",
            params=params,
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("ok"):
            logger.error("Telegram getUpdates returned ok=false: %s", data)
            return []

        return data.get("result", [])

    async def send_message(
        self,
        chat_id: int,
        text: str,
        reply_to_message_id: int | None = None,
    ) -> dict[str, Any]:
        """Send a text message to a chat."""
        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
        }
        if reply_to_message_id is not None:
            payload["reply_to_message_id"] = reply_to_message_id

        response = await self._client.post(
            f"{self._base_url}/sendMessage",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("ok"):
            logger.error("Telegram sendMessage returned ok=false: %s", data)

        return data

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()
