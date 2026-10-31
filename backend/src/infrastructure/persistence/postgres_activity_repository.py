"""Implementação PostgreSQL do ``IActivityRepository`` (ADR-031)."""

from __future__ import annotations

import json
from typing import Any

import asyncpg

from src.domain.entities.activity_event import ActivityEvent
from src.domain.interfaces.activity_repository import IActivityRepository

_INSERT_SQL = """
INSERT INTO activity_events (event_id, agent_id, kind, payload, created_at)
VALUES ($1, $2, $3, $4::jsonb, $5)
"""


def _to_event(row: Any) -> ActivityEvent:
    payload = row["payload"]
    return ActivityEvent(
        kind=row["kind"],
        payload=json.loads(payload) if isinstance(payload, str) else payload,
        agent_id=row["agent_id"],
        event_id=row["event_id"],
        created_at=row["created_at"],
    )


class PostgresActivityRepository(IActivityRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def add(self, event: ActivityEvent) -> None:
        await self._pool.execute(
            _INSERT_SQL,
            event.event_id,
            event.agent_id,
            event.kind,
            json.dumps(event.payload, default=str),
            event.created_at,
        )

    async def recent(self, limit: int) -> list[ActivityEvent]:
        rows = await self._pool.fetch(
            "SELECT * FROM activity_events ORDER BY created_at DESC LIMIT $1", limit
        )
        return [_to_event(row) for row in rows]
