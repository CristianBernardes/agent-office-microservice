"""Aplicação do esquema SQL do banco (idempotente) — ver ADR-014."""

from __future__ import annotations

from pathlib import Path

import asyncpg

_SCHEMA_PATH = Path(__file__).parent / "schema.sql"


async def apply_schema(pool: asyncpg.Pool) -> None:
    """Cria as tabelas ausentes; seguro para executar a cada startup."""
    await pool.execute(_SCHEMA_PATH.read_text(encoding="utf-8"))
