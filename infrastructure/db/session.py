from __future__ import annotations

import logging

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)


def build_engine(database_url: str) -> Engine:
    """Create a SQLAlchemy engine from a database URL.

    Secrets are never logged — only connection status.
    """
    engine = create_engine(database_url, echo=False, pool_pre_ping=True)
    logger.info("Database engine created")
    return engine


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a session factory bound to the given engine."""
    return sessionmaker(bind=engine, expire_on_commit=False)
