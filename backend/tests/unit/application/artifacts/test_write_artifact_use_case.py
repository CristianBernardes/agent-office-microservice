"""Testes unitários do ``WriteArtifactUseCase``."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.application.artifacts.write_artifact_use_case import (
    WriteArtifactInput,
    WriteArtifactUseCase,
)
from src.domain.entities.agent import Role
from src.domain.entities.artifact import ArtifactStatus, ArtifactType
from src.domain.value_objects.identifiers import AgentId
from src.infrastructure.filesystem.markdown_artifact_writer import MarkdownArtifactWriter
from src.infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from src.infrastructure.persistence.in_memory_artifact_repository import (
    InMemoryArtifactRepository,
)

pytestmark = pytest.mark.unit


class TestWriteArtifactUseCase:
    async def test_creates_artifact_in_draft_status(self, tmp_path: Path) -> None:
        repository = InMemoryArtifactRepository(
            writer=MarkdownArtifactWriter(workspace_root=str(tmp_path))
        )
        message_bus = InMemoryMessageBus()
        use_case = WriteArtifactUseCase(artifact_repository=repository, message_bus=message_bus)

        artifact = await use_case.execute(
            WriteArtifactInput(
                title="Backlog — Sprint 1",
                content="# Backlog\n\nItens do sprint.",
                artifact_type=ArtifactType.BACKLOG,
                path="sprint-1/backlog.md",
                author_id=AgentId.generate(),
                author_role=Role.PRODUCT_OWNER,
            )
        )

        assert artifact.status == ArtifactStatus.DRAFT
        assert (tmp_path / "sprint-1/backlog.md").exists()

    async def test_persists_artifact_in_repository(self, tmp_path: Path) -> None:
        repository = InMemoryArtifactRepository(
            writer=MarkdownArtifactWriter(workspace_root=str(tmp_path))
        )
        message_bus = InMemoryMessageBus()
        use_case = WriteArtifactUseCase(artifact_repository=repository, message_bus=message_bus)

        artifact = await use_case.execute(
            WriteArtifactInput(
                title="ADR-001 — Exemplo",
                content="# ADR-001",
                artifact_type=ArtifactType.ADR,
                path="sprint-1/adr-001.md",
                author_id=AgentId.generate(),
                author_role=Role.TECH_LEAD,
            )
        )

        persisted_artifact = await repository.find_by_id(artifact.artifact_id)
        assert persisted_artifact is not None
        assert persisted_artifact.title == "ADR-001 — Exemplo"

    async def test_publishes_artifact_created_event(self, tmp_path: Path) -> None:
        repository = InMemoryArtifactRepository(
            writer=MarkdownArtifactWriter(workspace_root=str(tmp_path))
        )
        message_bus = InMemoryMessageBus()
        use_case = WriteArtifactUseCase(artifact_repository=repository, message_bus=message_bus)

        artifact = await use_case.execute(
            WriteArtifactInput(
                title="Test Plan — Login",
                content="# Test Plan",
                artifact_type=ArtifactType.TEST_PLAN,
                path="sprint-1/test-plan-login.md",
                author_id=AgentId.generate(),
                author_role=Role.QA_ENGINEER,
            )
        )

        published_messages = message_bus.get_published_messages("office/artifacts/created")
        assert len(published_messages) == 1
        payload = published_messages[0]["payload"]
        assert isinstance(payload, dict)
        assert payload["artifact_id"] == str(artifact.artifact_id)
        assert payload["status"] == "draft"
