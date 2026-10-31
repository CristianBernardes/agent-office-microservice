"""Testes unitários da reunião autônoma sobre um objetivo (ADR-022)."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

import pytest

from src.application.autonomy.goal_meeting_use_case import (
    MEETING_ORDER,
    GoalMeetingInput,
    GoalMeetingUseCase,
    register_goal_autonomy,
)
from src.domain.entities.agent import Agent, Personality, Role
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import AgentId, GoalId, SessionId
from src.infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from src.infrastructure.persistence.in_memory_agent_repository import InMemoryAgentRepository

pytestmark = pytest.mark.unit


class _Dispatch:
    def __init__(self, failing: set[AgentId] | None = None) -> None:
        self.contexts: list[str] = []
        self._failing = failing or set()

    async def execute(self, agent_id: AgentId, context: str) -> Any:
        if agent_id in self._failing:
            raise ConnectionError("llm down")
        self.contexts.append(context)
        return SimpleNamespace(thought=f"fala-{len(self.contexts)}")


_TASKS: list[Any] = []


class _Recorder:
    def __init__(self) -> None:
        self.calls: list[Any] = []

    async def execute(self, data: Any) -> None:
        self.calls.append(data)


class _GroupRecorder:
    def __init__(self, sink: _Recorder) -> None:
        self._sink = sink

    async def record_group(self, ids: list[AgentId]) -> None:
        await self._sink.execute(ids)


def _agent(role: Role) -> Agent:
    return Agent(
        agent_id=AgentId.generate(),
        name=role.value,
        role=role,
        personality=Personality(0.5, 0.5, 0.5, 0.5, 0.5),
        llm_model="m",
    )


async def _build(
    roles: list[Role], language: Language = Language.EN, failing_role: Role | None = None
) -> tuple[GoalMeetingUseCase, _Dispatch, _Recorder, _Recorder, _Recorder]:
    repository = InMemoryAgentRepository()
    failing: set[AgentId] = set()
    for role in roles:
        agent = _agent(role)
        await repository.save(agent)
        if role == failing_role:
            failing.add(agent.agent_id)
    dispatch, chat, memory, artifact = _Dispatch(failing), _Recorder(), _Recorder(), _Recorder()
    tasks = _Recorder()
    _TASKS.append(tasks)
    use_case = GoalMeetingUseCase(
        repository,
        dispatch,  # type: ignore[arg-type]
        chat,  # type: ignore[arg-type]
        memory,  # type: ignore[arg-type]
        artifact,  # type: ignore[arg-type]
        language,
        create_task=tasks,  # type: ignore[arg-type]
    )
    return use_case, dispatch, chat, memory, artifact


def _input() -> GoalMeetingInput:
    return GoalMeetingInput(GoalId.generate(), SessionId.generate(), "Sell a digital product")


class TestGoalMeeting:
    async def test_speaks_in_fixed_order_and_writes_minutes(self) -> None:
        roles = [Role.QA_ENGINEER, Role.PRODUCT_OWNER, Role.TECH_LEAD]
        use_case, dispatch, chat, memory, artifact = await _build(roles)

        turns = await use_case.execute(_input())

        order = [t.agent.role for t in turns]
        assert order == [r for r in MEETING_ORDER if r in roles]
        assert len(chat.calls) == len(memory.calls) == 3
        assert len(artifact.calls) == 1
        assert artifact.calls[0].path.endswith("/meeting.md")
        assert artifact.calls[0].author_role == Role.PRODUCT_OWNER
        assert "fala-1" in dispatch.contexts[1]

    async def test_meeting_bonds_every_pair_of_speakers(self) -> None:
        use_case, *_ = await _build([Role.PRODUCT_OWNER, Role.TECH_LEAD, Role.QA_ENGINEER])
        bonds = _Recorder()
        use_case._record_interaction = _GroupRecorder(bonds)  # type: ignore[assignment]
        turns = await use_case.execute(_input())
        assert bonds.calls == [[t.agent.agent_id for t in turns]]

    async def test_context_is_localized(self) -> None:
        use_case, dispatch, *_ = await _build([Role.PRODUCT_OWNER], Language.PT)
        await use_case.execute(_input())
        assert "Objetivo do time" in dispatch.contexts[0]

    async def test_no_agents_means_no_meeting(self) -> None:
        use_case, _, chat, _, artifact = await _build([])
        assert await use_case.execute(_input()) == []
        assert chat.calls == [] and artifact.calls == []

    async def test_failing_agent_does_not_stop_meeting(self) -> None:
        roles = [Role.PRODUCT_OWNER, Role.TECH_LEAD]
        use_case, _, chat, _, artifact = await _build(roles, failing_role=Role.PRODUCT_OWNER)
        turns = await use_case.execute(_input())
        assert [t.agent.role for t in turns] == [Role.TECH_LEAD]
        assert len(chat.calls) == 1 and len(artifact.calls) == 1

    async def test_one_agent_per_role(self) -> None:
        use_case, *_ = await _build([Role.PRODUCT_OWNER, Role.PRODUCT_OWNER])
        assert len(await use_case.execute(_input())) == 1


class TestGoalSubscription:
    async def test_goal_event_triggers_meeting(self) -> None:
        bus = InMemoryMessageBus()
        recorder = _Recorder()
        await register_goal_autonomy(bus, lambda: recorder)()  # type: ignore[arg-type,return-value]
        goal_id, session_id = GoalId.generate(), SessionId.generate()

        await bus.publish(
            "office/goals/created",
            {
                "payload": {
                    "goal_id": str(goal_id.value),
                    "session_id": str(session_id.value),
                    "text": "x",
                }
            },
        )
        await asyncio.sleep(0)

        assert recorder.calls[0].goal_id == goal_id

    async def test_invalid_event_is_dropped(self) -> None:
        bus = InMemoryMessageBus()
        recorder = _Recorder()
        await register_goal_autonomy(bus, lambda: recorder)()  # type: ignore[arg-type,return-value]
        await bus.publish("office/goals/created", {"payload": {"goal_id": "nope"}})
        await bus.publish("office/goals/created", {"payload": "str"})
        await asyncio.sleep(0)
        assert recorder.calls == []


class TestBacklog:
    async def test_po_creates_one_task_per_other_role(self) -> None:
        await _build([Role.PRODUCT_OWNER, Role.TECH_LEAD, Role.QA_ENGINEER])
        # o último _Recorder de tarefas pertence ao use case recém-montado
        use_case, *_ = await _build([Role.PRODUCT_OWNER, Role.TECH_LEAD, Role.QA_ENGINEER])
        tasks = _TASKS[-1]
        await use_case.execute(_input())
        assert [c.title.split("]")[0] for c in tasks.calls] == ["[tech_lead", "[qa_engineer"]
        assert all(c.creator_role == Role.PRODUCT_OWNER for c in tasks.calls)
        assert all(c.goal_id is not None for c in tasks.calls)

    async def test_no_po_no_tasks(self) -> None:
        use_case, *_ = await _build([Role.TECH_LEAD])
        await use_case.execute(_input())
        assert _TASKS[-1].calls == []


class TestMeetingPersistence:
    async def test_meeting_is_stored_as_done_planning(self) -> None:
        from src.domain.entities.meeting import MeetingKind, MeetingStatus
        from src.infrastructure.persistence.in_memory_meeting_repository import (
            InMemoryMeetingRepository,
        )

        use_case, *_ = await _build([Role.PRODUCT_OWNER, Role.TECH_LEAD])
        repo = InMemoryMeetingRepository()
        use_case._meeting_repository = repo
        data = _input()

        turns = await use_case.execute(data)

        [meeting] = await repo.list_by_goal(data.goal_id)
        assert meeting.kind is MeetingKind.PLANNING
        assert meeting.status is MeetingStatus.DONE
        assert meeting.participants == tuple(t.agent.agent_id for t in turns)
