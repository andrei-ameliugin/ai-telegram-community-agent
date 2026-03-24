from __future__ import annotations

from sqlalchemy.orm import Session

from infrastructure.db.models import PolicyProfile


class PolicyRepository:
    """Data access for PolicyProfile entities."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, profile_id: int) -> PolicyProfile | None:
        return self._session.get(PolicyProfile, profile_id)

    def get_by_name(self, name: str) -> PolicyProfile | None:
        return (
            self._session.query(PolicyProfile)
            .filter(PolicyProfile.name == name)
            .first()
        )

    def get_all(self) -> list[PolicyProfile]:
        return list(self._session.query(PolicyProfile).all())

    def add(self, profile: PolicyProfile) -> PolicyProfile:
        self._session.add(profile)
        self._session.flush()
        return profile
