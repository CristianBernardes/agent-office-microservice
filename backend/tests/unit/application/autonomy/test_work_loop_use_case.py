"""Testes unitários do ciclo de trabalho autônomo (ADR-048)."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from src.application.autonomy.work_loop_use_case import _FLOOR_SESSION, WorkLoopUseCase
from src.application.tasks.task_use_cases import AssignTaskUseCase, MoveTaskUseCase
from src.domain.entities.agent import Agent, AgentStatus, Personality, Role
from src.domain.entities.task import Task, TaskStatus
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import AgentId, TaskId
from src.infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from src.infrastructure.persistence.in_memory_agent_repository import InMemoryAgentRepository
from src.infrastructure.persistence.in_memory_chat_repository import InMemoryChatRepository
from src.infrastructure.persistence.in_memory_task_repository import InMemoryTaskRepository

pytestmark = pytest.mark.unit


class _Dispatch:
    def __init__(self) -> None:
        self.prompts: list[str] = []
        self.languages: list[Any] = []

    async def execute(self, agent_id: AgentId, context: str, language: Any = None) -> Any:
        self.prompts.append(context)
        self.languages.append(language)
        return SimpleNamespace(thought="ok")


class _Sink:
    def __init__(self) -> None:
        self.calls: list[Any] = []

    async def execute(self, data: Any) -> None:
        self.calls.append(data)


def _agent(role: Role) -> Agent:
    return Agent(
        agent_id=AgentId.generate(),
        name=role.value,
        role=role,
        personality=Personality(0.5, 0.5, 0.5, 0.5, 0.5),
        llm_model="m",
    )


async def _build(
    roles: list[Role], language: Language = Language.EN
) -> tuple[WorkLoopUseCase, InMemoryTaskRepository, InMemoryAgentRepository, _Dispatch, _Sink]:
    agents, tasks, bus = InMemoryAgentRepository(), InMemoryTaskRepository(), InMemoryMessageBus()
    for role in roles:
        await agents.save(_agent(role))
    await tasks.save(Task(task_id=TaskId.generate(), title="T", description="d"))
    dispatch, chat, artifacts = _Dispatch(), _Sink(), _Sink()
    loop = WorkLoopUseCase(
        agents,
        tasks,
        AssignTaskUseCase(tasks, agents, bus),
        MoveTaskUseCase(tasks, bus, agents),
        dispatch,  # type: ignore[arg-type]
        chat,  # type: ignore[arg-type]
        artifacts,  # type: ignore[arg-type]
        bus,
        language,
        InMemoryChatRepository(),
    )
    return loop, tasks, agents, dispatch, artifacts


async def _status(tasks: InMemoryTaskRepository) -> TaskStatus:
    return (await tasks.list_all())[0].status


_TEAM = [Role.PRODUCT_OWNER, Role.DEV_SENIOR, Role.QA_ENGINEER]


async def test_task_walks_the_whole_kanban_across_ticks() -> None:
    loop, tasks, agents, _, artifacts = await _build(_TEAM)
    await loop.tick()
    expected = [
        TaskStatus.IN_PROGRESS,
        TaskStatus.TESTING,
        TaskStatus.IN_REVIEW,
        TaskStatus.DONE,
    ]
    for status in expected:
        await loop.tick()
        assert await _status(tasks) == status
    assert len(artifacts.calls) == 3  # planning + entrega + testes
    assert all(a.status == AgentStatus.IDLE for a in await agents.list_all())


async def test_task_waits_without_workers() -> None:
    loop, tasks, _, _, _ = await _build([Role.PRODUCT_OWNER])
    await loop.tick()
    assert await _status(tasks) == TaskStatus.BACKLOG


async def test_delivery_waits_for_tester_before_review() -> None:
    loop, tasks, _, _, _ = await _build([Role.PRODUCT_OWNER, Role.DEV_SENIOR])
    for _ in range(5):
        await loop.tick()
    assert await _status(tasks) == TaskStatus.TESTING


async def test_prompts_use_the_office_language() -> None:
    loop, _, _, dispatch, _ = await _build(_TEAM, Language.PT)
    for _ in range(5):
        await loop.tick()
    assert dispatch.languages == [Language.PT] * 4
    assert "planejamento" in dispatch.prompts[0]
    assert "Você está trabalhando" in dispatch.prompts[1]
    assert "testador" in dispatch.prompts[2]
    assert "Revise" in dispatch.prompts[3]


async def test_newly_hired_worker_picks_up_waiting_task() -> None:
    loop, tasks, agents, _, _ = await _build([Role.PRODUCT_OWNER])
    await loop.tick()
    await agents.save(_agent(Role.DEV_JUNIOR))
    await loop.tick()
    await loop.tick()
    assert await _status(tasks) == TaskStatus.IN_PROGRESS
    assert all(t.assigned_to is not None for t in await tasks.list_all())


async def test_planning_splits_work_so_nobody_is_idle() -> None:
    team = [Role.PRODUCT_OWNER, Role.DEV_SENIOR, Role.DEV_SENIOR, Role.DEV_JUNIOR, Role.QA_ENGINEER]
    loop, tasks, _, dispatch, artifacts = await _build(team)
    await loop.tick()
    all_tasks = await tasks.list_all()
    assert len(all_tasks) == 3
    assert all(t.status == TaskStatus.TODO for t in all_tasks)
    assert len({t.assigned_to for t in all_tasks}) == 3
    assert "(1/3)" in all_tasks[0].title or any("(1/3)" in t.title for t in all_tasks)
    assert "subtasks" in dispatch.prompts[0].lower()
    assert any("sprint planning" in p.lower() for p in dispatch.prompts)
    assert artifacts.calls[0].path.startswith("planning/")


async def test_planning_is_led_by_a_planner_role() -> None:
    loop, tasks, agents, dispatch, _ = await _build([Role.DEV_SENIOR, Role.SCRUM_MASTER])
    await loop.tick()
    assert await _status(tasks) == TaskStatus.TODO


@pytest.mark.parametrize(
    ("language", "title"),
    [(Language.PT, "Planejamento da sprint"), (Language.EN, "Sprint planning")],
)
async def test_planning_artifact_follows_the_office_language(
    language: Language, title: str
) -> None:
    loop, _, _, _, artifacts = await _build([Role.PRODUCT_OWNER, Role.DEV_SENIOR], language)
    await loop.tick()
    planning = next(c for c in artifacts.calls if c.path.startswith("planning/"))
    assert planning.title == title
    assert planning.content.startswith(f"# {title}")


async def test_floor_session_is_created_on_first_speech() -> None:
    chat = InMemoryChatRepository()
    agents, tasks, bus = InMemoryAgentRepository(), InMemoryTaskRepository(), InMemoryMessageBus()
    owner = _agent(Role.PRODUCT_OWNER)
    await agents.save(owner)
    loop = WorkLoopUseCase(
        agents,
        tasks,
        AssignTaskUseCase(tasks, agents, bus),
        MoveTaskUseCase(tasks, bus, agents),
        _Dispatch(),  # type: ignore[arg-type]
        _Sink(),  # type: ignore[arg-type]
        _Sink(),  # type: ignore[arg-type]
        bus,
        Language.EN,
        chat,
    )
    await loop._speak(owner, "hi")
    assert await chat.find_session(_FLOOR_SESSION) is not None


async def test_planning_states_the_sprint_day_limit() -> None:
    loop, _, _, dispatch, artifacts = await _build(_TEAM, Language.PT)
    for _ in range(3):
        await loop.tick()
    assert "15 dias fictícios" in dispatch.prompts[0]
    assert "15 dias fictícios" in artifacts.calls[0].content


async def test_hiring_task_is_owned_and_worked_by_hr() -> None:
    loop, tasks, agents, dispatch, _ = await _build(
        [Role.PRODUCT_OWNER, Role.DEV_SENIOR, Role.HR_MANAGER, Role.QA_ENGINEER]
    )
    task = (await tasks.list_all())[0]
    task.title = "Contratar um DBA"
    await tasks.save(task)
    hr = next(a for a in await agents.list_all() if a.role == Role.HR_MANAGER)

    for _ in range(3):
        await loop.tick()

    assert {t.assigned_to for t in await tasks.list_all()} == {hr.agent_id}
    assert any("You are working" in p for p in dispatch.prompts)


async def test_fired_owner_hands_the_task_to_another_professional() -> None:
    loop, tasks, agents, _, _ = await _build([Role.PRODUCT_OWNER, Role.DEV_SENIOR, Role.DEV_JUNIOR])
    await loop.tick()
    task = (await tasks.list_all())[0]
    task.assigned_to = None
    task.status = TaskStatus.TODO
    await tasks.save(task)

    await loop.tick()

    owner = (await tasks.list_all())[0].assigned_to
    assert owner is not None
