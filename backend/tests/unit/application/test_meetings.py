"""Testes unitários de reuniões e cerimônias (ADR-028)."""

from __future__ import annotations

from uuid import UUID

import pytest

from src.application.meetings.meeting_use_cases import (
    FinishMeetingUseCase,
    ListMeetingsUseCase,
    StartCeremonyInput,
    StartCeremonyUseCase,
)
from src.domain.entities.meeting import Meeting, MeetingKind, MeetingStatus
from src.domain.exceptions.domain_exceptions import DomainError
from src.domain.value_objects.identifiers import AgentId, GoalId, MeetingId
from src.infrastructure.persistence.in_memory_meeting_repository import (
    InMemoryMeetingRepository,
)

pytestmark = pytest.mark.unit

_SM = AgentId(UUID(int=1))
_DEV = AgentId(UUID(int=2))


async def test_start_ceremony_adds_organizer_without_duplicates() -> None:
    repo = InMemoryMeetingRepository()
    meeting = await StartCeremonyUseCase(repo).execute(
        StartCeremonyInput(MeetingKind.DAILY, "Daily", _SM, participants=(_DEV, _SM))
    )

    assert meeting.status is MeetingStatus.IN_PROGRESS
    assert meeting.participants == (_SM, _DEV)
    assert await repo.get(meeting.meeting_id) == meeting


async def test_finish_records_summary_and_decisions() -> None:
    repo = InMemoryMeetingRepository()
    started = await StartCeremonyUseCase(repo).execute(
        StartCeremonyInput(MeetingKind.RETROSPECTIVE, "Retro", _SM)
    )

    done = await FinishMeetingUseCase(repo).execute(started.meeting_id, "ok", ("a", "b"))

    assert done.status is MeetingStatus.DONE
    assert done.decisions == ("a", "b")
    assert done.ended_at is not None


async def test_finish_twice_is_rejected() -> None:
    repo = InMemoryMeetingRepository()
    started = await StartCeremonyUseCase(repo).execute(
        StartCeremonyInput(MeetingKind.REVIEW, "Review", _SM)
    )
    use_case = FinishMeetingUseCase(repo)
    await use_case.execute(started.meeting_id, "ok")

    with pytest.raises(DomainError, match="cannot be finished"):
        await use_case.execute(started.meeting_id, "again")


async def test_finish_unknown_meeting_raises_not_found() -> None:
    with pytest.raises(DomainError, match="was not found"):
        await FinishMeetingUseCase(InMemoryMeetingRepository()).execute(MeetingId.generate(), "x")


async def test_meeting_without_participants_is_invalid() -> None:
    with pytest.raises(DomainError, match="at least one participant"):
        Meeting(MeetingId.generate(), MeetingKind.DAILY, "x", None, ())


async def test_list_by_goal_filters() -> None:
    repo = InMemoryMeetingRepository()
    goal = GoalId.generate()
    start = StartCeremonyUseCase(repo)
    await start.execute(StartCeremonyInput(MeetingKind.PLANNING, "P", _SM, goal_id=goal))
    await start.execute(StartCeremonyInput(MeetingKind.DAILY, "D", _SM))

    assert [m.title for m in await ListMeetingsUseCase(repo).by_goal(goal)] == ["P"]
