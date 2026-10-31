"""Casos de uso de relacionamentos entre agentes (ADR-027)."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from src.domain.entities.relationship import Relationship
from src.domain.interfaces.relationship_repository import IRelationshipRepository
from src.domain.value_objects.identifiers import AgentId

MEETING_AFFINITY_DELTA = 0.05


@dataclass(frozen=True, slots=True)
class RecordInteractionInput:
    first: AgentId
    second: AgentId
    delta: float = MEETING_AFFINITY_DELTA


class RecordInteractionUseCase:
    def __init__(self, repository: IRelationshipRepository) -> None:
        self._repository = repository

    async def execute(self, data: RecordInteractionInput) -> Relationship:
        current = await self._repository.get(data.first, data.second)
        relationship = current or Relationship.between(data.first, data.second)
        updated = relationship.interact(data.delta)
        await self._repository.save(updated)
        return updated

    async def record_group(self, agent_ids: list[AgentId]) -> None:
        """Registra uma interação para cada par distinto do grupo."""
        for first, second in combinations(dict.fromkeys(agent_ids), 2):
            await self.execute(RecordInteractionInput(first, second))


class ListRelationshipsUseCase:
    def __init__(self, repository: IRelationshipRepository) -> None:
        self._repository = repository

    async def execute(self, agent_id: AgentId) -> list[Relationship]:
        return await self._repository.list_for(agent_id)
