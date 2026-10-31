"""Porta de persistência das memórias dos agentes (ADR-020)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.memory import Memory
from src.domain.value_objects.identifiers import AgentId


class IMemoryRepository(ABC):
    @abstractmethod
    async def save(self, memory: Memory) -> None:
        """Grava a memória."""

    @abstractmethod
    async def recall(self, agent_id: AgentId, embedding: list[float], limit: int) -> list[Memory]:
        """Memórias do agente mais similares ao vetor (cosseno), da mais próxima à mais distante."""

    @abstractmethod
    async def list_recent(self, agent_id: AgentId, limit: int) -> list[Memory]:
        """Memórias do agente, da mais recente à mais antiga."""
