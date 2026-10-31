"""Implementação PostgreSQL do ``IRelationshipRepository`` (ADR-027)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import asyncpg

from src.domain.entities.relationship import Relationship, RelationshipStatus, ordered_pair
from src.domain.interfaces.relationship_repository import IRelationshipRepository
from src.domain.value_objects.identifiers import AgentId

_COLUMNS = "agent_a, agent_b, score, status, interactions, last_interaction_at"

_UPSERT_SQL = """
INSERT INTO relationships (agent_a, agent_b, score, status, interactions, last_interaction_at)
VALUES ($1, $2, $3, $4, $5, $6)
ON CONFLICT (agent_a, agent_b) DO UPDATE SET
    score = EXCLUDED.score, status = EXCLUDED.status,
    interactions = EXCLUDED.interactions, last_interaction_at = EXCLUDED.last_interaction_at
"""

_GET_SQL = f"SELECT {_COLUMNS} FROM relationships WHERE agent_a = $1 AND agent_b = $2"
_LIST_SQL = f"SELECT {_COLUMNS} FROM relationships WHERE agent_a = $1 OR agent_b = $1"


def _to_relationship(row: Mapping[str, Any]) -> Relationship:
    return Relationship(
        agent_a=AgentId(row["agent_a"]),
        agent_b=AgentId(row["agent_b"]),
        score=float(row["score"]),
        interactions=row["interactions"],
        status=RelationshipStatus(row["status"]),
        last_interaction_at=row["last_interaction_at"],
    )


class PostgresRelationshipRepository(IRelationshipRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def get(self, first: AgentId, second: AgentId) -> Relationship | None:
        a, b = ordered_pair(first, second)
        row = await self._pool.fetchrow(_GET_SQL, a.value, b.value)
        return _to_relationship(row) if row else None

    async def save(self, relationship: Relationship) -> None:
        await self._pool.execute(
            _UPSERT_SQL,
            relationship.agent_a.value,
            relationship.agent_b.value,
            relationship.score,
            relationship.status.value,
            relationship.interactions,
            relationship.last_interaction_at,
        )

    async def list_for(self, agent_id: AgentId) -> list[Relationship]:
        rows = await self._pool.fetch(_LIST_SQL, agent_id.value)
        return [_to_relationship(row) for row in rows]
