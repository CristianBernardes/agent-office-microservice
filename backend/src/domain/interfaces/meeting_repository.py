"""Porta do repositório de reuniões (ADR-028)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.meeting import Meeting
from src.domain.value_objects.identifiers import GoalId, MeetingId


class IMeetingRepository(ABC):
    @abstractmethod
    async def save(self, meeting: Meeting) -> None: ...

    @abstractmethod
    async def get(self, meeting_id: MeetingId) -> Meeting | None: ...

    @abstractmethod
    async def list_by_goal(self, goal_id: GoalId) -> list[Meeting]: ...
