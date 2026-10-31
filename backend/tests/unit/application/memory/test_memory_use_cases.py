"""Testes unitários da memória semântica (ADR-020)."""

from __future__ import annotations

import pytest

from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.memory.memory_use_cases import (
    RecallMemoryUseCase,
    RememberInput,
    RememberUseCase,
)
from src.domain.entities.agent import Agent, Personality, Role
from src.domain.entities.memory import Memory, MemoryType
from src.domain.interfaces.llm_adapter import LlmEmbeddingResponse
from src.domain.interfaces.llm_adapter_resolver import ILlmAdapterResolver
from src.domain.value_objects.identifiers import AgentId, MemoryId
from src.infrastructure.llm.mock_llm_adapter import MockLlmAdapter
from src.infrastructure.persistence.in_memory_agent_repository import InMemoryAgentRepository
from src.infrastructure.persistence.in_memory_memory_repository import InMemoryMemoryRepository

pytestmark = pytest.mark.unit

_VECTORS = {"preço": [1.0, 0.0], "preco baixo": [0.9, 0.1], "reunião": [0.0, 1.0]}


class _KeywordEmbedder(MockLlmAdapter):
    async def embed(self, text: str) -> LlmEmbeddingResponse:
        return LlmEmbeddingResponse(_VECTORS[text], "kw", 2)


class _Resolver(ILlmAdapterResolver):
    def resolve(self, role: Role) -> MockLlmAdapter:
        return _KeywordEmbedder()


async def _agent(repo: InMemoryAgentRepository) -> Agent:
    agent = Agent(
        AgentId.generate(), "Ana", Role.PRODUCT_OWNER, Personality(0.5, 0.5, 0.5, 0.5, 0.5), "m"
    )
    await repo.save(agent)
    return agent


class TestMemory:
    async def test_remember_then_recall_orders_by_similarity(self) -> None:
        agents, memories = InMemoryAgentRepository(), InMemoryMemoryRepository()
        agent = await _agent(agents)
        remember = RememberUseCase(memories, agents, _Resolver())
        await remember.execute(RememberInput(agent.agent_id, "reunião", MemoryType.FACT))
        await remember.execute(RememberInput(agent.agent_id, "preco baixo"))

        found = await RecallMemoryUseCase(memories, agents, _Resolver()).execute(
            agent.agent_id, "preço", limit=1
        )
        assert [m.content for m in found] == ["preco baixo"]
        assert len(await memories.list_recent(agent.agent_id, 10)) == 2

    async def test_recall_is_isolated_per_agent(self) -> None:
        agents, memories = InMemoryAgentRepository(), InMemoryMemoryRepository()
        agent = await _agent(agents)
        await memories.save(
            Memory(MemoryId.generate(), AgentId.generate(), "x", embedding=(1.0, 0.0))
        )
        found = await RecallMemoryUseCase(memories, agents, _Resolver()).execute(
            agent.agent_id, "preço"
        )
        assert found == []

    async def test_unknown_agent_raises(self) -> None:
        agents, memories = InMemoryAgentRepository(), InMemoryMemoryRepository()
        with pytest.raises(AgentNotFoundError):
            await RememberUseCase(memories, agents, _Resolver()).execute(
                RememberInput(AgentId.generate(), "preço")
            )
        with pytest.raises(AgentNotFoundError):
            await RecallMemoryUseCase(memories, agents, _Resolver()).execute(
                AgentId.generate(), "preço"
            )

    def test_importance_out_of_range_is_rejected(self) -> None:
        with pytest.raises(ValueError):
            Memory(MemoryId.generate(), AgentId.generate(), "x", importance=1.5)
