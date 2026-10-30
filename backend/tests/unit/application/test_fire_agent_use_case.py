"""Testes unitários do ``FireAgentUseCase``."""

from __future__ import annotations

import pytest

from src.application.agents.fire_agent_use_case import (
    AgentNotFoundError,
    FireAgentUseCase,
)
from src.domain.entities.agent import Agent, AgentStatus, Personality, Role
from src.domain.value_objects.identifiers import AgentId
from src.infrastructure.persistence.in_memory_agent_repository import (
    InMemoryAgentRepository,
)

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
