"""Implementação PostgreSQL do ``ISettingsRepository``."""

from __future__ import annotations

import json

import asyncpg

from src.domain.interfaces.settings_repository import ISettingsRepository

_UPSERT_SQL = """
INSERT INTO office_settings (key, value) VALUES ($1, $2::jsonb)
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
"""


class PostgresSettingsRepository(ISettingsRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def get_flag(self, key: str, default: bool) -> bool:
        row = await self._pool.fetchrow("SELECT value FROM office_settings WHERE key = $1", key)
        if row is None:
            return default
        value = row["value"]
        parsed = json.loads(value) if isinstance(value, str) else value
        return parsed if isinstance(parsed, bool) else default

    async def set_flag(self, key: str, value: bool) -> None:
        await self._pool.execute(_UPSERT_SQL, key, json.dumps(value))
