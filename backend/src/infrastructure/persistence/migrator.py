"""Migrações de banco no estilo Laravel (ver ADR-018).

Cada migração é um par ``<timestamp>_<nome>.up.sql`` / ``.down.sql``. A tabela
``migrations`` guarda o que foi aplicado e o *batch*; ``rollback`` desfaz o último batch.
"""

from __future__ import annotations

import argparse
import asyncio
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import asyncpg

MIGRATIONS_DIR = Path(__file__).parent / "migrations"
_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS migrations (
    migration  TEXT PRIMARY KEY,
    batch      INTEGER NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""


# Bloco: uma migração descoberta em disco.
@dataclass(frozen=True, slots=True)
class Migration:
    name: str
    up_sql: str
    down_sql: str


class MigrationError(Exception):
    """Erro de uso das migrações (nome inválido, arquivo ausente)."""


def discover_migrations(directory: Path = MIGRATIONS_DIR) -> list[Migration]:
    """Lê os pares ``.up.sql``/``.down.sql`` em ordem de nome; ``down`` é obrigatório."""
    migrations: list[Migration] = []
    for up_file in sorted(directory.glob("*.up.sql")):
        name = up_file.name.removesuffix(".up.sql")
        down_file = directory / f"{name}.down.sql"
        if not down_file.exists():
            raise MigrationError(f"Migração '{name}' sem arquivo .down.sql")
        migrations.append(
            Migration(
                name=name,
                up_sql=up_file.read_text(encoding="utf-8"),
                down_sql=down_file.read_text(encoding="utf-8"),
            )
        )
    return migrations


async def _applied(pool: asyncpg.Pool) -> dict[str, int]:
    await pool.execute(_CREATE_TABLE_SQL)
    rows = await pool.fetch("SELECT migration, batch FROM migrations ORDER BY migration")
    return {row["migration"]: row["batch"] for row in rows}


async def migrate(pool: asyncpg.Pool, directory: Path = MIGRATIONS_DIR) -> list[str]:
    """Aplica as migrações pendentes num novo batch; retorna os nomes aplicados."""
    applied = await _applied(pool)
    pending = [m for m in discover_migrations(directory) if m.name not in applied]
    batch = max(applied.values(), default=0) + 1
    for migration in pending:
        async with pool.acquire() as connection, connection.transaction():
            await connection.execute(migration.up_sql)
            await connection.execute(
                "INSERT INTO migrations (migration, batch) VALUES ($1, $2)",
                migration.name,
                batch,
            )
    return [m.name for m in pending]


async def rollback(pool: asyncpg.Pool, directory: Path = MIGRATIONS_DIR) -> list[str]:
    """Desfaz o último batch (da mais nova para a mais antiga); retorna os nomes revertidos."""
    applied = await _applied(pool)
    if not applied:
        return []
    last_batch = max(applied.values())
    by_name = {m.name: m for m in discover_migrations(directory)}
    names = sorted((n for n, b in applied.items() if b == last_batch), reverse=True)
    for name in names:
        if name not in by_name:
            raise MigrationError(f"Arquivos da migração '{name}' não encontrados")
        async with pool.acquire() as connection, connection.transaction():
            await connection.execute(by_name[name].down_sql)
            await connection.execute("DELETE FROM migrations WHERE migration = $1", name)
    return names


async def status(
    pool: asyncpg.Pool, directory: Path = MIGRATIONS_DIR
) -> list[tuple[str, int | None]]:
    """Retorna ``(nome, batch)`` de cada migração; ``batch`` é ``None`` se pendente."""
    applied = await _applied(pool)
    return [(m.name, applied.get(m.name)) for m in discover_migrations(directory)]


async def fresh(pool: asyncpg.Pool, directory: Path = MIGRATIONS_DIR) -> list[str]:
    """Recria o schema ``public`` (destrutivo!) e reaplica todas as migrações."""
    await pool.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public")
    return await migrate(pool, directory)


def make_migration(
    name: str, directory: Path = MIGRATIONS_DIR, now: datetime | None = None
) -> tuple[Path, Path]:
    """Cria o par vazio ``.up.sql``/``.down.sql`` com prefixo de timestamp."""
    if not _NAME_PATTERN.match(name):
        raise MigrationError("Nome inválido: use snake_case (ex.: create_agents_table)")
    stamp = (now or datetime.now(UTC)).strftime("%Y_%m_%d_%H%M%S")
    up_file = directory / f"{stamp}_{name}.up.sql"
    down_file = directory / f"{stamp}_{name}.down.sql"
    up_file.write_text("-- up\n", encoding="utf-8")
    down_file.write_text("-- down\n", encoding="utf-8")
    return up_file, down_file


async def _run(command: str, database_url: str) -> None:
    pool = await asyncpg.create_pool(database_url)
    try:
        if command == "status":
            for name, batch in await status(pool):
                print(f"[{'x' if batch else ' '}] {name}" + (f" (batch {batch})" if batch else ""))
            return
        actions = {"migrate": migrate, "rollback": rollback, "fresh": fresh}
        for name in await actions[command](pool):
            print(f"{command}: {name}")
    finally:
        await pool.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrações do AgentOffice")
    parser.add_argument("command", choices=["migrate", "rollback", "status", "fresh", "make"])
    parser.add_argument("name", nargs="?", help="nome da migração (comando make)")
    args = parser.parse_args()
    if args.command == "make":
        for path in make_migration(args.name or ""):
            print(f"criado: {path}")
        return
    from src.infrastructure.config.settings import get_settings

    asyncio.run(_run(args.command, get_settings().database_url))


if __name__ == "__main__":
    main()
