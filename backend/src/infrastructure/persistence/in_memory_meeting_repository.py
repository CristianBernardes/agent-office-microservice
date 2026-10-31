"""Repositório de reuniões em memória (testes e modo sem banco)."""

from __future__ import annotations

from src.domain.entities.meeting import Meeting
from src.domain.interfaces.meeting_repository import IMeetingRepository
from src.domain.value_objects.identifiers import GoalId, MeetingId


class InMemoryMeetingRepository(IMeetingRepository):
    def __init__(self) -> None:
        self._items: dict[MeetingId, Meeting] = {}

    async def save(self, meeting: Meeting) -> None:
        self._items[meeting.meeting_id] = meeting

    async def get(self, meeting_id: MeetingId) -> Meeting | None:
        return self._items.get(meeting_id)

    async def list_by_goal(self, goal_id: GoalId) -> list[Meeting]:
        return [m for m in self._items.values() if m.goal_id == goal_id]
