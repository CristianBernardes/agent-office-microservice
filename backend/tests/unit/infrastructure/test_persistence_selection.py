"""Testes da seleção do backend de persistência e do lifespan (ADR-014)."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from fastapi import FastAPI
from pydantic import ValidationError

from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.persistence.in_memory_agent_repository import InMemoryAgentRepository
from src.infrastructure.persistence.postgres_agent_repository import PostgresAgentRepository
from src.infrastructure.persistence.postgres_artifact_repository import (
    PostgresArtifactRepository,
)
from src.presentation import dependencies, main

pytestmark = pytest.mark.unit


@pytest.fixture
def clean_state() -> Iterator[None]:
    get_settings.cache_clear()
    dependencies.set_database_pool(None)
    yield
    get_settings.cache_clear()
    dependencies.set_database_pool(None)


class TestPersistenceBackendSetting:
    def test_defaults_to_memory(self) -> None:
        assert Settings(_env_file=None).persistence_backend == "memory"  # type: ignore[call-arg]

    def test_invalid_value_fails_fast(self) -> None:
        with pytest.raises(ValidationError):
            Settings(persistence_backend="mongo", _env_file=None)  # type: ignore[call-arg,arg-type]


@pytest.mark.usefixtures("clean_state")
class TestRepositorySelection:
    def test_memory_backend_returns_in_memory(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("PERSISTENCE_BACKEND", "memory")
        assert isinstance(dependencies.get_agent_repository(), InMemoryAgentRepository)

    def test_postgres_backend_uses_registered_pool(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("PERSISTENCE_BACKEND", "postgres")
        dependencies.set_database_pool(object())  # type: ignore[arg-type]
        assert isinstance(dependencies.get_agent_repository(), PostgresAgentRepository)
        assert isinstance(dependencies.get_artifact_repository(), PostgresArtifactRepository)

    def test_postgres_backend_without_pool_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("PERSISTENCE_BACKEND", "postgres")
        with pytest.raises(RuntimeError, match="pool"):
            dependencies.get_agent_repository()


class FakeClosablePool:
    def __init__(self) -> None:
        self.closed = False
        self.executed: list[str] = []

    async def execute(self, sql: str, *args: Any) -> None:
        self.executed.append(sql)

    async def close(self) -> None:
        self.closed = True


@pytest.mark.usefixtures("clean_state")
class TestLifespan:
    async def test_memory_backend_does_not_open_pool(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("PERSISTENCE_BACKEND", "memory")

        async def fail(_: str) -> None:
            raise AssertionError("pool must not be created")

        monkeypatch.setattr(main, "create_postgres_pool", fail)
        async with main.lifespan(FastAPI()):
            pass

    async def test_postgres_backend_migrates_and_closes_pool(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("PERSISTENCE_BACKEND", "postgres")
        pool = FakeClosablePool()

        async def fake_create(_: str) -> FakeClosablePool:
            return pool

        migrated: list[object] = []

        async def fake_migrate(received: object) -> list[str]:
            migrated.append(received)
            return []

        monkeypatch.setattr(main, "create_postgres_pool", fake_create)
        monkeypatch.setattr(main, "migrate", fake_migrate)
        async with main.lifespan(FastAPI()):
            assert isinstance(dependencies.get_agent_repository(), PostgresAgentRepository)
        assert pool.closed
        assert migrated == [pool]
