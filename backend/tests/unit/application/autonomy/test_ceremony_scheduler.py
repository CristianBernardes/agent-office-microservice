"""Testes das cerimônias automáticas (daily, refinamento, review e retrospectiva)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from src.application.autonomy.ceremony_scheduler_use_case import (
    CeremonyConfig,
    CeremonySchedulerUseCase,
)
from src.domain.entities.agent import Agent, Personality, Role
from src.domain.entities.meeting import MeetingKind
from src.domain.entities.task import Task, TaskStatus
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import AgentId, TaskId
from src.infrastructure.persistence.in_memory_agent_repository import InMemoryAgentRepository
from src.infrastructure.persistence.in_memory_meeting_repository import InMemoryMeetingRepository
from src.infrastructure.persistence.in_memory_task_repository import InMemoryTaskRepository

pytestmark = pytest.mark.unit


class _Sink:
    def __init__(self) -> None:
        self.calls: list[Any] = []

    async def execute(self, data: Any) -> None:
        self.calls.append(data)


def _agent(role: Role) -> Agent:
    return Agent(AgentId.generate(), role.value, role, Personality(0.5, 0.5, 0.5, 0.5, 0.5), "m")


async def _speak(agent: Agent, prompt: str) -> str:
    return f"{agent.name} fala"


async def _world(
    *, status: TaskStatus, daily_minutes: float = 120
) -> tuple[CeremonySchedulerUseCase, InMemoryMeetingRepository, _Sink]:
    agents, tasks, meetings, artifacts = (
        InMemoryAgentRepository(),
        InMemoryTaskRepository(),
        InMemoryMeetingRepository(),
        _Sink(),
    )
    sm, dev = _agent(Role.SCRUM_MASTER), _agent(Role.DEV_SENIOR)
    await agents.save(sm)
    await agents.save(dev)
    task = Task(TaskId.generate(), "Entregar API", "d", status=status, assigned_to=dev.agent_id)
    if status == TaskStatus.DONE:
        task.completed_at = datetime.now(UTC)
    await tasks.save(task)
    scheduler = CeremonySchedulerUseCase(
        agents,
        tasks,
        meetings,
        artifacts,  # type: ignore[arg-type]
        CeremonyConfig(timedelta(minutes=daily_minutes), timedelta(minutes=240)),
    )
    return scheduler, meetings, artifacts


async def _kinds(meetings: InMemoryMeetingRepository) -> list[MeetingKind]:
    return [m.kind for m in await meetings.list_all()]


class TestCeremonyScheduler:
    async def test_daily_runs_for_active_work_and_waits_for_the_interval(self) -> None:
        scheduler, meetings, artifacts = await _world(status=TaskStatus.IN_PROGRESS)
        assert await scheduler.tick(_speak, Language.PT) == 1
        assert await _kinds(meetings) == [MeetingKind.DAILY]
        assert len(artifacts.calls) == 1
        assert await scheduler.tick(_speak, Language.PT) == 0

    async def test_daily_runs_again_after_the_interval(self) -> None:
        scheduler, meetings, _ = await _world(status=TaskStatus.IN_PROGRESS, daily_minutes=0.0001)
        await scheduler.tick(_speak, Language.EN)
        import asyncio

        await asyncio.sleep(0.05)
        assert await scheduler.tick(_speak, Language.EN) == 1
        assert await _kinds(meetings) == [MeetingKind.DAILY, MeetingKind.DAILY]

    async def test_refinement_runs_for_backlog_tasks(self) -> None:
        scheduler, meetings, _ = await _world(status=TaskStatus.BACKLOG)
        await scheduler.tick(_speak, Language.PT)
        assert await _kinds(meetings) == [MeetingKind.REFINEMENT]

    async def test_review_and_retrospective_run_once_at_the_end_of_the_sprint(self) -> None:
        scheduler, meetings, _ = await _world(status=TaskStatus.DONE)
        assert await scheduler.tick(_speak, Language.PT) == 2
        assert await _kinds(meetings) == [MeetingKind.REVIEW, MeetingKind.RETROSPECTIVE]
        assert await scheduler.tick(_speak, Language.PT) == 0

    async def test_nothing_happens_without_a_facilitator(self) -> None:
        scheduler, meetings, _ = await _world(status=TaskStatus.IN_PROGRESS)
        for agent in await scheduler._agents.list_all():  # noqa: SLF001
            agent.go_offline()
            await scheduler._agents.save(agent)  # noqa: SLF001
        assert await scheduler.tick(_speak, Language.PT) == 0
        assert await _kinds(meetings) == []

    async def test_a_failing_speaker_does_not_break_the_loop(self) -> None:
        scheduler, meetings, _ = await _world(status=TaskStatus.IN_PROGRESS)

        async def boom(agent: Agent, prompt: str) -> str:
            raise RuntimeError("llm fora do ar")

        assert await scheduler.tick(boom, Language.PT) == 0
        assert await _kinds(meetings) == []
