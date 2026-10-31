"""Implementação PostgreSQL (pgvector) do ``IMemoryRepository`` (ADR-020)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import asyncpg

from src.domain.entities.memory import Memory, MemoryType
from src.domain.interfaces.memory_repository import IMemoryRepository
from src.domain.value_objects.identifiers import AgentId, MemoryId, SessionId

_INSERT_SQL = """
INSERT INTO memories (memory_id, agent_id, session_id, content, memory_type, importance,
                      embedding, created_at)
VALUES ($1, $2, $3, $4, $5, $6, $7::vector, $8)
"""

_RECALL_SQL = """
UPDATE memories SET last_accessed_at = now()
WHERE memory_id IN (
    SELECT memory_id FROM memories WHERE agent_id = $1 AND embedding IS NOT NULL
    ORDER BY embedding <=> $2::vector LIMIT $3
)
RETURNING memory_id, agent_id, session_id, content, memory_type, importance, created_at,
          embedding::text AS embedding, (embedding <=> $2::vector) AS distance
"""

_RECENT_SQL = """
SELECT memory_id, agent_id, session_id, content, memory_type, importance, created_at,
       embedding::text AS embedding
FROM memories WHERE agent_id = $1 ORDER BY created_at DESC LIMIT $2
"""


# Bloco: formato textual aceito pelo pgvector, ex.: "[0.1,0.2]".
def _to_vector(values: list[float] | tuple[float, ...]) -> str | None:
    return "[" + ",".join(str(v) for v in values) + "]" if values else None


def _to_memory(row: Mapping[str, Any]) -> Memory:
    raw = row["embedding"]
    embedding = tuple(float(x) for x in raw.strip("[]").split(",")) if raw else ()
    return Memory(
        memory_id=MemoryId(row["memory_id"]),
        agent_id=AgentId(row["agent_id"]),
        content=row["content"],
        memory_type=MemoryType(row["memory_type"]),
        importance=float(row["importance"]),
        embedding=embedding,
        session_id=SessionId(row["session_id"]) if row["session_id"] else None,
        created_at=row["created_at"],
    )


class PostgresMemoryRepository(IMemoryRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def save(self, memory: Memory) -> None:
        await self._pool.execute(
            _INSERT_SQL,
            memory.memory_id.value,
            memory.agent_id.value,
            memory.session_id.value if memory.session_id else None,
            memory.content,
            memory.memory_type.value,
            memory.importance,
            _to_vector(memory.embedding),
            memory.created_at,
        )

    async def recall(self, agent_id: AgentId, embedding: list[float], limit: int) -> list[Memory]:
        rows = await self._pool.fetch(_RECALL_SQL, agent_id.value, _to_vector(embedding), limit)
        ordered = sorted(rows, key=lambda r: r["distance"])
        return [_to_memory(row) for row in ordered]

    async def list_recent(self, agent_id: AgentId, limit: int) -> list[Memory]:
        rows = await self._pool.fetch(_RECENT_SQL, agent_id.value, limit)
        return [_to_memory(row) for row in rows]
