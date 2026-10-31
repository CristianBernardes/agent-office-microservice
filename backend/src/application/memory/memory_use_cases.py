"""Casos de uso da memória semântica dos agentes (ADR-020)."""

from __future__ import annotations

from dataclasses import dataclass

from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.domain.entities.agent import Agent
from src.domain.entities.memory import Memory, MemoryType
from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.interfaces.llm_adapter_resolver import ILlmAdapterResolver
from src.domain.interfaces.memory_repository import IMemoryRepository
from src.domain.value_objects.identifiers import AgentId, MemoryId, SessionId


# Bloco: busca o agente e o vetoriza com o LLM do papel dele (DRY entre os dois casos de uso).
async def _embed_for(
    agents: IAgentRepository, resolver: ILlmAdapterResolver, agent_id: AgentId, text: str
) -> tuple[Agent, list[float]]:
    agent = await agents.find_by_id(agent_id)
    if agent is None:
        raise AgentNotFoundError("agent.not_found", agent_id=agent_id)
    response = await resolver.resolve(agent.role).embed(text)
    return agent, response.vector


@dataclass(frozen=True, slots=True)
class RememberInput:
    agent_id: AgentId
    content: str
    memory_type: MemoryType = MemoryType.OBSERVATION
    importance: float = 0.5
    session_id: SessionId | None = None


class RememberUseCase:
    def __init__(
        self,
        memory_repository: IMemoryRepository,
        agent_repository: IAgentRepository,
        llm_resolver: ILlmAdapterResolver,
    ) -> None:
        self._memories = memory_repository
        self._agents = agent_repository
        self._resolver = llm_resolver

    async def execute(self, data: RememberInput) -> Memory:
        _, vector = await _embed_for(self._agents, self._resolver, data.agent_id, data.content)
        memory = Memory(
            memory_id=MemoryId.generate(),
            agent_id=data.agent_id,
            content=data.content,
            memory_type=data.memory_type,
            importance=data.importance,
            embedding=tuple(vector),
            session_id=data.session_id,
        )
        await self._memories.save(memory)
        return memory


class RecallMemoryUseCase:
    def __init__(
        self,
        memory_repository: IMemoryRepository,
        agent_repository: IAgentRepository,
        llm_resolver: ILlmAdapterResolver,
    ) -> None:
        self._memories = memory_repository
        self._agents = agent_repository
        self._resolver = llm_resolver

    async def execute(self, agent_id: AgentId, query: str, limit: int = 5) -> list[Memory]:
        _, vector = await _embed_for(self._agents, self._resolver, agent_id, query)
        return await self._memories.recall(agent_id, vector, limit)
