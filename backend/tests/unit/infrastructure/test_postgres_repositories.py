"""Testes unitários dos repositórios PostgreSQL, com uma pool asyncpg falsa (ADR-014)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest

from src.domain.entities.agent import Agent, AgentStatus, Personality, Role
from src.domain.entities.artifact import Artifact, ArtifactType
from src.domain.value_objects.identifiers import AgentId, ArtifactId, TaskId
from src.infrastructure.filesystem.markdown_artifact_writer import MarkdownArtifactWriter
from src.infrastructure.persistence.postgres_agent_repository import PostgresAgentRepository
from src.infrastructure.persistence.postgres_artifact_repository import (
    PostgresArtifactRepository,
)

pytestmark = pytest.mark.unit


class FakePool:
    """Pool falsa: registra chamadas e devolve linhas pré-definidas."""

    def __init__(self, rows: list[dict[str, Any]] | None = None) -> None:
        self.rows = rows or []
        self.executed: list[tuple[str, tuple[Any, ...]]] = []

    async def execute(self, sql: str, *args: Any) -> None:
        self.executed.append((sql, args))

    async def fetchrow(self, sql: str, *args: Any) -> dict[str, Any] | None:
        return self.rows[0] if self.rows else None

    async def fetch(self, sql: str, *args: Any) -> list[dict[str, Any]]:
        return self.rows


def _agent(task_id: TaskId | None = None) -> Agent:
    return Agent(
        agent_id=AgentId.generate(),
        name="Alice",
        role=Role.DEV_SENIOR,
        personality=Personality(0.9, 0.8, 0.4, 0.7, 0.1),
        llm_model="m",
        status=AgentStatus.THINKING,
        current_task_id=task_id,
    )


def _agent_row(agent: Agent) -> dict[str, Any]:
    p = agent.personality
    return {
        "agent_id": agent.agent_id.value,
        "name": agent.name,
        "role": agent.role.value,
        "llm_model": agent.llm_model,
        "status": agent.status.value,
        "current_task_id": agent.current_task_id.value if agent.current_task_id else None,
        "openness": p.openness,
        "conscientiousness": p.conscientiousness,
        "extraversion": p.extraversion,
        "agreeableness": p.agreeableness,
        "neuroticism": p.neuroticism,
    }


class TestPostgresAgentRepository:
    async def test_save_upserts_with_mapped_values(self) -> None:
        pool = FakePool()
        agent = _agent(TaskId(value=uuid4()))
        await PostgresAgentRepository(pool).save(agent)  # type: ignore[arg-type]

        sql, args = pool.executed[0]
        assert "ON CONFLICT" in sql
        assert args[0] == agent.agent_id.value
        assert args[2] == "dev_senior"
        assert args[4] == "thinking"
        assert args[5] == agent.current_task_id.value  # type: ignore[union-attr]

    async def test_save_without_task_stores_null(self) -> None:
        pool = FakePool()
        await PostgresAgentRepository(pool).save(_agent())  # type: ignore[arg-type]
        assert pool.executed[0][1][5] is None

    async def test_find_by_id_rebuilds_entity(self) -> None:
        agent = _agent(TaskId(value=uuid4()))
        pool = FakePool([_agent_row(agent)])
        found = await PostgresAgentRepository(pool).find_by_id(agent.agent_id)  # type: ignore[arg-type]
        assert found == agent

    async def test_find_by_id_returns_none_when_missing(self) -> None:
        repository = PostgresAgentRepository(FakePool())  # type: ignore[arg-type]
        assert await repository.find_by_id(AgentId.generate()) is None

    async def test_list_all_maps_every_row(self) -> None:
        first, second = _agent(), _agent()
        pool = FakePool([_agent_row(first), _agent_row(second)])
        assert await PostgresAgentRepository(pool).list_all() == [first, second]  # type: ignore[arg-type]

    async def test_corrupted_role_raises(self) -> None:
        row = _agent_row(_agent()) | {"role": "wizard"}
        with pytest.raises(ValueError):
            await PostgresAgentRepository(FakePool([row])).find_by_id(AgentId.generate())  # type: ignore[arg-type]


def _artifact() -> Artifact:
    now = datetime.now(UTC)
    return Artifact(
        artifact_id=ArtifactId.generate(),
        title="T",
        content="# body",
        artifact_type=ArtifactType.ADR,
        path="adr/t.md",
        author_id=AgentId.generate(),
        created_at=now,
        updated_at=now,
    )


class TestPostgresArtifactRepository:
    async def test_save_writes_file_and_upserts(self, tmp_path: Path) -> None:
        pool = FakePool()
        repository = PostgresArtifactRepository(
            pool,  # type: ignore[arg-type]
            MarkdownArtifactWriter(workspace_root=str(tmp_path)),
        )
        artifact = _artifact()
        await repository.save(artifact)

        assert (tmp_path / artifact.path).exists()
        sql, args = pool.executed[0]
        assert "ON CONFLICT" in sql
        assert args[0] == artifact.artifact_id.value
        assert args[3] == "adr"
        assert args[6] == "draft"

    async def test_find_by_id_rebuilds_entity(self) -> None:
        artifact = _artifact()
        row = {
            "artifact_id": artifact.artifact_id.value,
            "title": artifact.title,
            "content": artifact.content,
            "artifact_type": "adr",
            "path": artifact.path,
            "author_id": artifact.author_id.value,
            "status": "draft",
            "created_at": artifact.created_at,
            "updated_at": artifact.updated_at,
        }
        repository = PostgresArtifactRepository(FakePool([row]))  # type: ignore[arg-type]
        assert await repository.find_by_id(artifact.artifact_id) == artifact
        assert await repository.list_all() == [artifact]

    async def test_find_by_id_returns_none_when_missing(self) -> None:
        repository = PostgresArtifactRepository(FakePool())  # type: ignore[arg-type]
        assert await repository.find_by_id(ArtifactId.generate()) is None


class TestPostgresTaskTransitions:
    async def test_add_transition_writes_enum_values(self) -> None:
        from src.domain.entities.agent import Role
        from src.domain.entities.task import TaskStatus, TaskTransition
        from src.infrastructure.persistence.postgres_task_repository import PostgresTaskRepository

        pool = FakePool()
        actor = AgentId(value=uuid4())
        await PostgresTaskRepository(pool).add_transition(  # type: ignore[arg-type]
            TaskTransition(
                TaskId(value=uuid4()), None, TaskStatus.BACKLOG, actor, Role.PRODUCT_OWNER, "n"
            )
        )
        sql, args = pool.executed[0]
        assert "task_transitions" in sql and "SELECT agent_id FROM agents" in sql
        assert args[1:6] == (None, "backlog", actor.value, "product_owner", "n")

    async def test_list_transitions_maps_rows_and_null_actor(self) -> None:
        from datetime import UTC, datetime

        from src.infrastructure.persistence.postgres_task_repository import PostgresTaskRepository

        task_id = uuid4()
        pool = FakePool(
            [
                {
                    "task_id": task_id,
                    "from_status": "todo",
                    "to_status": "in_progress",
                    "actor_id": None,
                    "actor_role": "dev_senior",
                    "note": None,
                    "created_at": datetime.now(UTC),
                }
            ]
        )
        [item] = await PostgresTaskRepository(pool).list_transitions(  # type: ignore[arg-type]
            TaskId(value=task_id)
        )
        assert item.from_status.value == "todo" and item.note == ""
