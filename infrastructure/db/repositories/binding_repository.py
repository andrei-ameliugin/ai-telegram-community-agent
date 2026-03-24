from __future__ import annotations

from sqlalchemy.orm import Session

from infrastructure.db.models import BotChatBinding


class BindingRepository:
    """Data access for BotChatBinding entities."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, binding_id: int) -> BotChatBinding | None:
        return self._session.get(BotChatBinding, binding_id)

    def get_by_bot_and_chat(
        self, bot_id: int, chat_id: int,
    ) -> BotChatBinding | None:
        return (
            self._session.query(BotChatBinding)
            .filter(
                BotChatBinding.bot_id == bot_id,
                BotChatBinding.chat_id == chat_id,
            )
            .first()
        )

    def get_all_for_bot(self, bot_id: int) -> list[BotChatBinding]:
        return list(
            self._session.query(BotChatBinding)
            .filter(BotChatBinding.bot_id == bot_id)
            .all()
        )

    def add(self, binding: BotChatBinding) -> BotChatBinding:
        self._session.add(binding)
        self._session.flush()
        return binding
