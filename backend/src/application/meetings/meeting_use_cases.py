"""Casos de uso de reuniões e cerimônias (ADR-028)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from src.domain.entities.meeting import Meeting, MeetingKind, MeetingStatus
from src.domain.exceptions.domain_exceptions import DomainError
from src.domain.interfaces.meeting_repository import IMeetingRepository
from src.domain.value_objects.identifiers import AgentId, GoalId, MeetingId


@dataclass(frozen=True, slots=True)
class StartCeremonyInput:
    kind: MeetingKind
    title: str
    organizer_id: AgentId
    participants: tuple[AgentId, ...] = ()
    goal_id: GoalId | None = None


class StartCeremonyUseCase:
    def __init__(self, meeting_repository: IMeetingRepository) -> None:
        self._meetings = meeting_repository

    async def execute(self, data: StartCeremonyInput) -> Meeting:
        # Bloco: o organizador sempre participa, sem duplicar nem reordenar os demais.
        participants = tuple(dict.fromkeys((data.organizer_id, *data.participants)))
        meeting = Meeting(
            meeting_id=MeetingId.generate(),
            kind=data.kind,
            title=data.title,
            organizer_id=data.organizer_id,
            participants=participants,
            goal_id=data.goal_id,
            status=MeetingStatus.IN_PROGRESS,
            started_at=datetime.now(UTC),
        )
        await self._meetings.save(meeting)
        return meeting


class FinishMeetingUseCase:
    def __init__(self, meeting_repository: IMeetingRepository) -> None:
        self._meetings = meeting_repository

    async def execute(
        self, meeting_id: MeetingId, summary: str, decisions: tuple[str, ...] = ()
    ) -> Meeting:
        meeting = await self._meetings.get(meeting_id)
        if meeting is None:
            raise DomainError("meeting.not_found", meeting_id=str(meeting_id))
        finished = meeting.finish(summary, decisions)
        await self._meetings.save(finished)
        return finished


class ListMeetingsUseCase:
    def __init__(self, meeting_repository: IMeetingRepository) -> None:
        self._meetings = meeting_repository

    async def by_goal(self, goal_id: GoalId) -> list[Meeting]:
        return await self._meetings.list_by_goal(goal_id)
