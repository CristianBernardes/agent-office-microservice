"""Porta do repositório de relacionamentos entre agentes (ADR-027)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.relationship import Relationship
from src.domain.value_objects.identifiers import AgentId


class IRelationshipRepository(ABC):
    @abstractmethod
    async def get(self, first: AgentId, second: AgentId) -> Relationship | None: ...

    @abstractmethod
    async def save(self, relationship: Relationship) -> None: ...

    @abstractmethod
    async def list_for(self, agent_id: AgentId) -> list[Relationship]: ...
