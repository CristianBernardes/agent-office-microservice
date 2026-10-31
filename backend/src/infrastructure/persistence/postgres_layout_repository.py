"""Implementação PostgreSQL do ``ILayoutRepository`` (ADR-030)."""

from __future__ import annotations

import json

import asyncpg

from src.domain.entities.office_layout import OfficeLayout
from src.domain.interfaces.layout_repository import ILayoutRepository

_UPSERT_SQL = """
INSERT INTO office_layout (name, layout) VALUES ($1, $2::jsonb)
ON CONFLICT (name) DO UPDATE SET layout = EXCLUDED.layout
"""


class PostgresLayoutRepository(ILayoutRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def save(self, layout: OfficeLayout) -> None:
        await self._pool.execute(_UPSERT_SQL, layout.name, json.dumps(layout.layout))

    async def get(self, name: str) -> OfficeLayout | None:
        row = await self._pool.fetchrow(
            "SELECT name, layout FROM office_layout WHERE name = $1", name
        )
        if row is None:
            return None
        data = row["layout"]
        return OfficeLayout(row["name"], json.loads(data) if isinstance(data, str) else data)
