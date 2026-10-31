"""Repositório de memórias em memória (testes e modo sem banco)."""

from __future__ import annotations

import math

from src.domain.entities.memory import Memory
from src.domain.interfaces.memory_repository import IMemoryRepository
from src.domain.value_objects.identifiers import AgentId


def _cosine(a: tuple[float, ...], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0


class InMemoryMemoryRepository(IMemoryRepository):
    def __init__(self) -> None:
        self._memories: list[Memory] = []

    async def save(self, memory: Memory) -> None:
        self._memories.append(memory)

    async def recall(self, agent_id: AgentId, embedding: list[float], limit: int) -> list[Memory]:
        own = [m for m in self._memories if m.agent_id == agent_id and m.embedding]
        own.sort(key=lambda m: _cosine(m.embedding, embedding), reverse=True)
        return own[:limit]

    async def list_recent(self, agent_id: AgentId, limit: int) -> list[Memory]:
        own = [m for m in self._memories if m.agent_id == agent_id]
        return sorted(own, key=lambda m: m.created_at, reverse=True)[:limit]
