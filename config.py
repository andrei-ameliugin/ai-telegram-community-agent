from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables.

    Secrets are never hardcoded — always sourced from env vars.
    """

    telegram_bot_token: str
    polling_timeout: int = 30
    polling_retry_delay: float = 5.0

    @classmethod
    def from_env(cls) -> Settings:
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        if not token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is required")

        return cls(
            telegram_bot_token=token,
            polling_timeout=int(os.environ.get("POLLING_TIMEOUT", "30")),
            polling_retry_delay=float(os.environ.get("POLLING_RETRY_DELAY", "5.0")),
        )
