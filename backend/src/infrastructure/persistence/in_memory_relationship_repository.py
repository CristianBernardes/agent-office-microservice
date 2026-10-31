"""Repositório de relacionamentos em memória (testes e modo sem banco)."""

from __future__ import annotations

from src.domain.entities.relationship import Relationship, ordered_pair
from src.domain.interfaces.relationship_repository import IRelationshipRepository
from src.domain.value_objects.identifiers import AgentId


class InMemoryRelationshipRepository(IRelationshipRepository):
    def __init__(self) -> None:
        self._items: dict[tuple[AgentId, AgentId], Relationship] = {}

    async def get(self, first: AgentId, second: AgentId) -> Relationship | None:
        return self._items.get(ordered_pair(first, second))

    async def save(self, relationship: Relationship) -> None:
        self._items[(relationship.agent_a, relationship.agent_b)] = relationship

    async def list_for(self, agent_id: AgentId) -> list[Relationship]:
        return [r for r in self._items.values() if agent_id in (r.agent_a, r.agent_b)]
