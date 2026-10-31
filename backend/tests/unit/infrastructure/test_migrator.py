"""Testes unitários do migrador estilo Laravel (ADR-018), com pool falsa."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from src.infrastructure.persistence.migrator import (
    MIGRATIONS_DIR,
    MigrationError,
    discover_migrations,
    fresh,
    make_migration,
    migrate,
    rollback,
    status,
)

pytestmark = pytest.mark.unit


class FakeConnection:
    def __init__(self, pool: FakePool) -> None:
        self.pool = pool

    async def execute(self, sql: str, *args: Any) -> None:
        if "BOOM" in sql:
            raise RuntimeError("falhou")
        self.pool.executed.append(sql)
        if sql.startswith("INSERT INTO migrations"):
            self.pool.applied[args[0]] = args[1]
        elif sql.startswith("DELETE FROM migrations"):
            self.pool.applied.pop(args[0], None)

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        snapshot = dict(self.pool.applied)
        try:
            yield
        except BaseException:
            self.pool.applied = snapshot
            raise


class FakePool:
    def __init__(self) -> None:
        self.applied: dict[str, int] = {}
        self.executed: list[str] = []

    async def execute(self, sql: str, *args: Any) -> None:
        self.executed.append(sql)

    async def fetch(self, sql: str, *args: Any) -> list[dict[str, Any]]:
        return [{"migration": n, "batch": b} for n, b in sorted(self.applied.items())]

    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[FakeConnection]:
        yield FakeConnection(self)


def _write(directory: Path, name: str, up: str = "SELECT 1", down: str = "SELECT 2") -> None:
    (directory / f"{name}.up.sql").write_text(up)
    if down:
        (directory / f"{name}.down.sql").write_text(down)


class TestDiscover:
    def test_orders_by_name(self, tmp_path: Path) -> None:
        _write(tmp_path, "2026_01_01_000002_b")
        _write(tmp_path, "2026_01_01_000001_a")
        assert [m.name for m in discover_migrations(tmp_path)] == [
            "2026_01_01_000001_a",
            "2026_01_01_000002_b",
        ]

    def test_missing_down_raises(self, tmp_path: Path) -> None:
        _write(tmp_path, "2026_01_01_000001_a", down="")
        with pytest.raises(MigrationError):
            discover_migrations(tmp_path)

    def test_real_migrations_are_valid_pairs(self) -> None:
        migrations = discover_migrations(MIGRATIONS_DIR)
        assert len(migrations) >= 9
        assert all(m.up_sql.strip() and m.down_sql.strip() for m in migrations)


class TestMigrate:
    async def test_applies_pending_in_one_batch(self, tmp_path: Path) -> None:
        _write(tmp_path, "2026_01_01_000001_a")
        _write(tmp_path, "2026_01_01_000002_b")
        pool = FakePool()
        assert len(await migrate(pool, tmp_path)) == 2  # type: ignore[arg-type]
        assert set(pool.applied.values()) == {1}

    async def test_second_run_is_noop_and_new_ones_get_next_batch(self, tmp_path: Path) -> None:
        _write(tmp_path, "2026_01_01_000001_a")
        pool = FakePool()
        await migrate(pool, tmp_path)  # type: ignore[arg-type]
        assert await migrate(pool, tmp_path) == []  # type: ignore[arg-type]
        _write(tmp_path, "2026_01_01_000002_b")
        await migrate(pool, tmp_path)  # type: ignore[arg-type]
        assert pool.applied["2026_01_01_000002_b"] == 2

    async def test_failing_migration_is_not_recorded(self, tmp_path: Path) -> None:
        _write(tmp_path, "2026_01_01_000001_a")
        _write(tmp_path, "2026_01_01_000002_b", up="BOOM")
        pool = FakePool()
        with pytest.raises(RuntimeError):
            await migrate(pool, tmp_path)  # type: ignore[arg-type]
        assert list(pool.applied) == ["2026_01_01_000001_a"]


class TestRollbackStatusFresh:
    async def test_rollback_reverts_last_batch_only(self, tmp_path: Path) -> None:
        _write(tmp_path, "2026_01_01_000001_a")
        pool = FakePool()
        await migrate(pool, tmp_path)  # type: ignore[arg-type]
        _write(tmp_path, "2026_01_01_000002_b")
        _write(tmp_path, "2026_01_01_000003_c")
        await migrate(pool, tmp_path)  # type: ignore[arg-type]
        reverted = await rollback(pool, tmp_path)  # type: ignore[arg-type]
        assert reverted == ["2026_01_01_000003_c", "2026_01_01_000002_b"]
        assert list(pool.applied) == ["2026_01_01_000001_a"]

    async def test_rollback_with_nothing_applied(self, tmp_path: Path) -> None:
        assert await rollback(FakePool(), tmp_path) == []  # type: ignore[arg-type]

    async def test_rollback_missing_files_raises(self, tmp_path: Path) -> None:
        pool = FakePool()
        pool.applied["ghost"] = 1
        with pytest.raises(MigrationError):
            await rollback(pool, tmp_path)  # type: ignore[arg-type]

    async def test_status_marks_pending(self, tmp_path: Path) -> None:
        _write(tmp_path, "2026_01_01_000001_a")
        pool = FakePool()
        await migrate(pool, tmp_path)  # type: ignore[arg-type]
        _write(tmp_path, "2026_01_01_000002_b")
        assert await status(pool, tmp_path) == [  # type: ignore[arg-type]
            ("2026_01_01_000001_a", 1),
            ("2026_01_01_000002_b", None),
        ]

    async def test_fresh_drops_schema_then_migrates(self, tmp_path: Path) -> None:
        _write(tmp_path, "2026_01_01_000001_a")
        pool = FakePool()
        assert await fresh(pool, tmp_path) == ["2026_01_01_000001_a"]  # type: ignore[arg-type]
        assert any("DROP SCHEMA public" in sql for sql in pool.executed)


class TestMakeMigration:
    def test_creates_timestamped_pair(self, tmp_path: Path) -> None:
        now = datetime(2026, 5, 1, 10, 30, 0, tzinfo=UTC)
        up, down = make_migration("create_x_table", tmp_path, now)
        assert up.name == "2026_05_01_103000_create_x_table.up.sql"
        assert down.exists()

    @pytest.mark.parametrize("name", ["", "CamelCase", "1abc", "with-dash", "has space"])
    def test_invalid_name_raises(self, tmp_path: Path, name: str) -> None:
        with pytest.raises(MigrationError):
            make_migration(name, tmp_path)
