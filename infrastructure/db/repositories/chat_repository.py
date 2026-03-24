from __future__ import annotations

from sqlalchemy.orm import Session

from infrastructure.db.models import Chat


class ChatRepository:
    """Data access for Chat entities."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, chat_id: int) -> Chat | None:
        return self._session.get(Chat, chat_id)

    def get_all(self) -> list[Chat]:
        return list(self._session.query(Chat).all())

    def add(self, chat: Chat) -> Chat:
        self._session.add(chat)
        self._session.flush()
        return chat
