"""Seleção do backend Postgres nas factories de repositório."""

from __future__ import annotations

from typing import Any

import pytest

from src.infrastructure.config.settings import get_settings
from src.presentation import dependencies as deps

pytestmark = pytest.mark.unit

_FACTORIES = [
    (deps.get_agent_repository, "PostgresAgentRepository"),
    (deps.get_artifact_repository, "PostgresArtifactRepository"),
    (deps.get_task_repository, "PostgresTaskRepository"),
    (deps.get_chat_repository, "PostgresChatRepository"),
    (deps.get_memory_repository, "PostgresMemoryRepository"),
    (deps.get_relationship_repository, "PostgresRelationshipRepository"),
    (deps.get_activity_repository, "PostgresActivityRepository"),
    (deps.get_layout_repository, "PostgresLayoutRepository"),
    (deps.get_meeting_repository, "PostgresMeetingRepository"),
    (deps.get_dismissal_repository, "PostgresDismissalRepository"),
]


@pytest.fixture
def postgres_mode(monkeypatch: pytest.MonkeyPatch) -> Any:
    monkeypatch.setenv("PERSISTENCE_BACKEND", "postgres")
    get_settings.cache_clear()
    deps.set_database_pool(object())  # type: ignore[arg-type]
    yield
    deps.set_database_pool(None)
    monkeypatch.undo()
    get_settings.cache_clear()


@pytest.mark.parametrize(("factory", "class_name"), _FACTORIES)
def test_factory_returns_postgres_repository(
    postgres_mode: Any, factory: Any, class_name: str
) -> None:
    assert type(factory()).__name__ == class_name


def test_factory_requires_pool(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PERSISTENCE_BACKEND", "postgres")
    get_settings.cache_clear()
    deps.set_database_pool(None)
    try:
        with pytest.raises(RuntimeError):
            deps.get_task_repository()
    finally:
        monkeypatch.undo()
        get_settings.cache_clear()
        deps.set_database_pool(None)
