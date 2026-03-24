from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.base import Base


class Bot(Base):
    """Registered Telegram bot.

    Real bot tokens are never stored in the database.
    Bots are identified by their Telegram bot ID (numeric)
    and a human-readable alias used to map to config/env tokens.
    """

    __tablename__ = "bots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_bot_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    bindings: Mapped[list[BotChatBinding]] = relationship(
        back_populates="bot", cascade="all, delete-orphan",
    )


class Chat(Base):
    """Telegram chat (group, supergroup, or private)."""

    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)

    bindings: Mapped[list[BotChatBinding]] = relationship(
        back_populates="chat", cascade="all, delete-orphan",
    )


class PolicyProfile(Base):
    """Per-chat behavior configuration."""

    __tablename__ = "policy_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    config_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")

    bindings: Mapped[list[BotChatBinding]] = relationship(
        back_populates="policy_profile",
    )


class BotChatBinding(Base):
    """Links a bot to a chat with a specific policy profile."""

    __tablename__ = "bot_chat_bindings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bot_id: Mapped[int] = mapped_column(ForeignKey("bots.id"), nullable=False)
    chat_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("chats.id"), nullable=False,
    )
    policy_profile_id: Mapped[int | None] = mapped_column(
        ForeignKey("policy_profiles.id"), nullable=True,
    )

    bot: Mapped[Bot] = relationship(back_populates="bindings")
    chat: Mapped[Chat] = relationship(back_populates="bindings")
    policy_profile: Mapped[PolicyProfile | None] = relationship(
        back_populates="bindings",
    )
