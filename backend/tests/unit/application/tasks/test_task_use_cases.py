"""Testes unitários dos casos de uso de tarefas (ADR-016)."""

from __future__ import annotations

import pytest

from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.tasks.task_errors import TaskNotFoundError
from src.application.tasks.task_use_cases import (
    AssignTaskUseCase,
    CompleteTaskUseCase,
    CreateTaskInput,
    CreateTaskUseCase,
)
from src.domain.entities.agent import Agent, AgentStatus, Personality, Role
from src.domain.entities.task import Priority, TaskStatus
from src.domain.exceptions.domain_exceptions import InvalidStateTransitionError
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import AgentId, TaskId
from src.infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from src.infrastructure.persistence.in_memory_agent_repository import InMemoryAgentRepository
from src.infrastructure.persistence.in_memory_task_repository import InMemoryTaskRepository

pytestmark = pytest.mark.unit

PO = AgentId.generate()


@pytest.fixture
def world() -> tuple[InMemoryTaskRepository, InMemoryAgentRepository, InMemoryMessageBus]:
    return InMemoryTaskRepository(), InMemoryAgentRepository(), InMemoryMessageBus()


async def _agent(repo: InMemoryAgentRepository, name: str = "Ana") -> Agent:
    agent = Agent(
        agent_id=AgentId.generate(),
        name=name,
        role=Role.DEV_SENIOR,
        personality=Personality(0.5, 0.5, 0.5, 0.5, 0.5),
        llm_model="m",
    )
    await repo.save(agent)
    return agent


async def _create(tasks: InMemoryTaskRepository, bus: InMemoryMessageBus) -> TaskId:
    task = await CreateTaskUseCase(tasks, bus).execute(
        CreateTaskInput("Landing page", "desc", Priority.HIGH, PO, Role.PRODUCT_OWNER)
    )
    return task.task_id


class TestCreate:
    async def test_creates_in_backlog_and_persists(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, _, bus = world
        task_id = await _create(tasks, bus)
        saved = await tasks.find_by_id(task_id)
        assert saved is not None
        assert saved.status == TaskStatus.BACKLOG
        assert saved.priority == Priority.HIGH


class TestAssign:
    async def test_assigns_and_marks_agent_working(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        task_id, agent = await _create(tasks, bus), await _agent(agents)
        task = await AssignTaskUseCase(tasks, agents, bus).execute(
            task_id, agent.agent_id, PO, Role.PRODUCT_OWNER
        )
        assert task.status == TaskStatus.IN_PROGRESS
        assert agent.status == AgentStatus.WORKING
        assert agent.current_task_id == task_id

    async def test_unknown_task_raises_localized(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        agent = await _agent(agents)
        with pytest.raises(TaskNotFoundError) as error:
            await AssignTaskUseCase(tasks, agents, bus).execute(
                TaskId.generate(), agent.agent_id, PO, Role.PRODUCT_OWNER
            )
        assert "não foi encontrada" in error.value.localized(Language.PT)
        assert "was not found" in error.value.localized(Language.EN)

    async def test_unknown_agent_raises(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        with pytest.raises(AgentNotFoundError):
            await AssignTaskUseCase(tasks, agents, bus).execute(
                await _create(tasks, bus), AgentId.generate(), PO, Role.PRODUCT_OWNER
            )

    async def test_busy_agent_leaves_task_untouched(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        agent = await _agent(agents)
        use_case = AssignTaskUseCase(tasks, agents, bus)
        await use_case.execute(await _create(tasks, bus), agent.agent_id, PO, Role.PRODUCT_OWNER)
        second = await _create(tasks, bus)
        with pytest.raises(InvalidStateTransitionError):
            await use_case.execute(second, agent.agent_id, PO, Role.PRODUCT_OWNER)
        stored = await tasks.find_by_id(second)
        assert stored is not None
        assert stored.status == TaskStatus.BACKLOG


class TestComplete:
    async def test_completes_and_frees_agent(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        task_id, agent = await _create(tasks, bus), await _agent(agents)
        await AssignTaskUseCase(tasks, agents, bus).execute(
            task_id, agent.agent_id, PO, Role.PRODUCT_OWNER
        )
        task = await CompleteTaskUseCase(tasks, agents, bus).execute(
            task_id, "feito", agent.agent_id, Role.DEV_SENIOR
        )
        assert task.status == TaskStatus.DONE
        assert agent.status == AgentStatus.IDLE

    async def test_backlog_task_cannot_complete(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        with pytest.raises(InvalidStateTransitionError) as error:
            await CompleteTaskUseCase(tasks, agents, bus).execute(
                await _create(tasks, bus), "x", PO, Role.PRODUCT_OWNER
            )
        assert "apenas tarefas" in error.value.localized(Language.PT)

    async def test_unknown_task_raises(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        with pytest.raises(TaskNotFoundError):
            await CompleteTaskUseCase(tasks, agents, bus).execute(
                TaskId.generate(), "x", PO, Role.PRODUCT_OWNER
            )
