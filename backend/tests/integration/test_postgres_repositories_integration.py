"""Integração dos repositórios PostgreSQL contra um banco real (`make up`)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

import pytest

from src.domain.entities.activity_event import ActivityEvent
from src.domain.entities.agent import Agent, Personality, Role
from src.domain.entities.artifact import Artifact, ArtifactType
from src.domain.entities.meeting import Meeting, MeetingKind, MeetingStatus
from src.domain.entities.office_layout import OfficeLayout
from src.domain.entities.relationship import Relationship
from src.domain.value_objects.identifiers import AgentId, ArtifactId, MeetingId
from src.infrastructure.config.settings import get_settings
from src.infrastructure.filesystem.markdown_artifact_writer import MarkdownArtifactWriter
from src.infrastructure.persistence.migrator import fresh
from src.infrastructure.persistence.postgres_activity_repository import PostgresActivityRepository
from src.infrastructure.persistence.postgres_agent_repository import PostgresAgentRepository
from src.infrastructure.persistence.postgres_artifact_repository import (
    PostgresArtifactRepository,
)
from src.infrastructure.persistence.postgres_connection import create_postgres_pool
from src.infrastructure.persistence.postgres_layout_repository import PostgresLayoutRepository
from src.infrastructure.persistence.postgres_meeting_repository import PostgresMeetingRepository
from src.infrastructure.persistence.postgres_relationship_repository import (
    PostgresRelationshipRepository,
)

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
            role=Role.QA_ENGINEER,
            personality=Personality(0.5, 0.5, 0.5, 0.5, 0.5),
            llm_model="m",
        )
        await repository.save(agent)
        agent.start_thinking()
        await repository.save(agent)

        assert await repository.find_by_id(agent.agent_id) == agent
        assert agent in await repository.list_all()

    async def test_artifact_roundtrip(self, pool: object, tmp_path: Path) -> None:
        author = Agent(
            agent_id=AgentId.generate(),
            name="Ana",
            role=Role.TECH_LEAD,
            personality=Personality(0.5, 0.5, 0.5, 0.5, 0.5),
            llm_model="m",
        )
        await PostgresAgentRepository(pool).save(author)  # type: ignore[arg-type]
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
            author_id=author.agent_id,
        )
        await repository.save(artifact)
        assert await repository.find_by_id(artifact.artifact_id) == artifact


async def _agent(pool: object, name: str) -> Agent:
    agent = Agent(
        agent_id=AgentId.generate(),
        name=name,
        role=Role.DEV_SENIOR,
        personality=Personality(0.5, 0.5, 0.5, 0.5, 0.5),
        llm_model="m",
    )
    await PostgresAgentRepository(pool).save(agent)  # type: ignore[arg-type]
    return agent


class TestSocialRepositoriesIntegration:
    async def test_relationship_roundtrip(self, pool: object) -> None:
        first, second = await _agent(pool, "A"), await _agent(pool, "B")
        repository = PostgresRelationshipRepository(pool)  # type: ignore[arg-type]
        bond = Relationship.between(first.agent_id, second.agent_id).interact(0.2)
        await repository.save(bond)
        await repository.save(bond.interact(0.2))

        loaded = await repository.get(second.agent_id, first.agent_id)
        assert loaded is not None and loaded.interactions == 2
        assert len(await repository.list_for(first.agent_id)) == 1

    async def test_meeting_roundtrip(self, pool: object) -> None:
        first, second = await _agent(pool, "A"), await _agent(pool, "B")
        repository = PostgresMeetingRepository(pool)  # type: ignore[arg-type]
        meeting = Meeting(
            meeting_id=MeetingId.generate(),
            kind=MeetingKind.PLANNING,
            title="Plan",
            organizer_id=first.agent_id,
            participants=(first.agent_id, second.agent_id),
            status=MeetingStatus.IN_PROGRESS,
        ).finish("ok", ("d1",))
        await repository.save(meeting)

        loaded = await repository.get(meeting.meeting_id)
        assert loaded is not None
        assert loaded.decisions == ("d1",)
        assert set(loaded.participants) == set(meeting.participants)

    async def test_layout_upsert(self, pool: object) -> None:
        repository = PostgresLayoutRepository(pool)  # type: ignore[arg-type]
        await repository.save(OfficeLayout("main", {"v": 1}))
        await repository.save(OfficeLayout("main", {"v": 2}))
        loaded = await repository.get("main")
        assert loaded is not None and loaded.layout == {"v": 2}

    async def test_activity_recent_is_newest_first(self, pool: object) -> None:
        repository = PostgresActivityRepository(pool)  # type: ignore[arg-type]
        await repository.add(ActivityEvent(kind="first"))
        await repository.add(ActivityEvent(kind="second", payload={"k": "v"}))
        recent = await repository.recent(10)
        assert [e.kind for e in recent] == ["second", "first"]
        assert recent[0].payload == {"k": "v"}
