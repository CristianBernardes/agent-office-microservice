"""Testes unitários do ``HireAgentUseCase``.

Usa ``InMemoryAgentRepository`` como fake de infraestrutura, validando apenas o
comportamento do caso de uso — sem qualquer banco de dados real envolvido.
"""

from __future__ import annotations

import pytest

from src.application.agents.hire_agent_use_case import HireAgentInput, HireAgentUseCase
from src.domain.entities.agent import AgentStatus, Personality, Role
from src.infrastructure.persistence.in_memory_agent_repository import (
    InMemoryAgentRepository,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def neutral_personality() -> Personality:
    return Personality(
        openness=0.5,
        conscientiousness=0.5,
        extraversion=0.5,
        agreeableness=0.5,
        neuroticism=0.5,
    )


class TestHireAgentUseCase:
    async def test_creates_agent_with_idle_status(self, neutral_personality: Personality) -> None:
        repository = InMemoryAgentRepository()
        use_case = HireAgentUseCase(agent_repository=repository)

        agent = await use_case.execute(
            HireAgentInput(
                name="Alice",
                role=Role.DEV_SENIOR,
                personality=neutral_personality,
                llm_model="mock-model",
            )
        )

        assert agent.name == "Alice"
        assert agent.role == Role.DEV_SENIOR
        assert agent.status == AgentStatus.IDLE

    async def test_persists_agent_in_repository(self, neutral_personality: Personality) -> None:
        repository = InMemoryAgentRepository()
        use_case = HireAgentUseCase(agent_repository=repository)

        agent = await use_case.execute(
            HireAgentInput(
                name="Bob",
                role=Role.PRODUCT_OWNER,
                personality=neutral_personality,
                llm_model="mock-model",
            )
        )

        persisted_agent = await repository.find_by_id(agent.agent_id)
        assert persisted_agent is not None
        assert persisted_agent.name == "Bob"
