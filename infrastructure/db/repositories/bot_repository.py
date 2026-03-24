from __future__ import annotations

from sqlalchemy.orm import Session

from infrastructure.db.models import Bot


class BotRepository:
    """Data access for Bot entities."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, bot_id: int) -> Bot | None:
        return self._session.get(Bot, bot_id)

    def get_by_telegram_bot_id(self, telegram_bot_id: int) -> Bot | None:
        return (
            self._session.query(Bot)
            .filter(Bot.telegram_bot_id == telegram_bot_id)
            .first()
        )

    def get_all(self) -> list[Bot]:
        return list(self._session.query(Bot).all())

    def add(self, bot: Bot) -> Bot:
        self._session.add(bot)
        self._session.flush()
        return bot


