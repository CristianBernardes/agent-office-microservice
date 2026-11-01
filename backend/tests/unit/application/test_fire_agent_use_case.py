"""Testes unitários do ``FireAgentUseCase``."""

from __future__ import annotations

import pytest

from src.application.agents.fire_agent_use_case import (
    AgentNotFoundError,
    FireAgentUseCase,
)
from src.domain.entities.agent import Agent, AgentStatus, Personality, Role
from src.domain.entities.task import Task, TaskStatus
from src.domain.value_objects.identifiers import AgentId, TaskId
from src.infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from src.infrastructure.persistence.in_memory_agent_repository import (
    InMemoryAgentRepository,
)
from src.infrastructure.persistence.in_memory_task_repository import InMemoryTaskRepository

pytestmark = pytest.mark.unit


@pytest.fixture
def existing_agent() -> Agent:
    return Agent(
        agent_id=AgentId.generate(),
        name="Carol",
        role=Role.QA_ENGINEER,
        personality=Personality(0.5, 0.5, 0.5, 0.5, 0.5),
        llm_model="mock-model",
    )


class TestFireAgentUseCase:
    async def test_moves_existing_agent_to_offline(self, existing_agent: Agent) -> None:
        repository = InMemoryAgentRepository()
        await repository.save(existing_agent)
        use_case = FireAgentUseCase(agent_repository=repository)

        fired_agent = await use_case.execute(existing_agent.agent_id)

        assert fired_agent.status == AgentStatus.OFFLINE

    async def test_raises_when_agent_does_not_exist(self) -> None:
        repository = InMemoryAgentRepository()
        use_case = FireAgentUseCase(agent_repository=repository)

        with pytest.raises(AgentNotFoundError):
            await use_case.execute(AgentId.generate())


class TestFireReturnsWorkToTheFlow:
    async def test_open_tasks_are_unassigned_and_status_is_published(
        self, existing_agent: Agent
    ) -> None:
        agents, tasks, bus = (
            InMemoryAgentRepository(),
            InMemoryTaskRepository(),
            InMemoryMessageBus(),
        )
        await agents.save(existing_agent)
        mine = Task(TaskId.generate(), "T", "d", TaskStatus.IN_PROGRESS)
        mine.assigned_to = existing_agent.agent_id
        done = Task(TaskId.generate(), "D", "d", TaskStatus.DONE)
        done.assigned_to = existing_agent.agent_id
        await tasks.save(mine)
        await tasks.save(done)
        received: list[str] = []

        async def handler(topic: str, _: dict[str, object]) -> None:
            received.append(topic)

        await bus.subscribe("office/agents/+/status", handler)

        await FireAgentUseCase(agents, tasks, bus).execute(existing_agent.agent_id)

        reloaded = await tasks.find_by_id(mine.task_id)
        assert reloaded is not None
        assert (reloaded.assigned_to, reloaded.status) == (None, TaskStatus.TODO)
        kept = await tasks.find_by_id(done.task_id)
        assert kept is not None and kept.assigned_to == existing_agent.agent_id
        assert received == [f"office/agents/{existing_agent.agent_id}/status"]
