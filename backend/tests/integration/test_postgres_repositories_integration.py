"""Integração dos repositórios PostgreSQL contra um banco real (`make up`)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

import pytest

from src.domain.entities.agent import Agent, Personality, Role
from src.domain.entities.artifact import Artifact, ArtifactType
from src.domain.value_objects.identifiers import AgentId, ArtifactId
from src.infrastructure.config.settings import get_settings
from src.infrastructure.filesystem.markdown_artifact_writer import MarkdownArtifactWriter
from src.infrastructure.persistence.migrator import fresh
from src.infrastructure.persistence.postgres_agent_repository import PostgresAgentRepository
from src.infrastructure.persistence.postgres_artifact_repository import (
    PostgresArtifactRepository,
)
from src.infrastructure.persistence.postgres_connection import create_postgres_pool

pytestmark = pytest.mark.integration


@pytest.fixture
async def pool() -> AsyncIterator[object]:
    created = await create_postgres_pool(get_settings().database_url)
    await fresh(created)
    yield created
    await created.close()


class TestPostgresRepositoriesIntegration:
    async def test_agent_roundtrip_and_update(self, pool: object) -> None:
        repository = PostgresAgentRepository(pool)  # type: ignore[arg-type]
        agent = Agent(
            agent_id=AgentId.generate(),
            name="Zed",
            role=Role.QA,
            personality=Personality(0.5, 0.5, 0.5, 0.5, 0.5),
            llm_model="m",
        )
        await repository.save(agent)
        agent.start_thinking()
        await repository.save(agent)

        assert await repository.find_by_id(agent.agent_id) == agent
        assert agent in await repository.list_all()

    async def test_artifact_roundtrip(self, pool: object, tmp_path: Path) -> None:
        repository = PostgresArtifactRepository(
            pool,  # type: ignore[arg-type]
            MarkdownArtifactWriter(workspace_root=str(tmp_path)),
        )
        artifact = Artifact(
            artifact_id=ArtifactId.generate(),
            title="ADR",
            content="# x",
            artifact_type=ArtifactType.ADR,
            path="adr/x.md",
            author_id=AgentId.generate(),
        )
        await repository.save(artifact)
        assert await repository.find_by_id(artifact.artifact_id) == artifact
