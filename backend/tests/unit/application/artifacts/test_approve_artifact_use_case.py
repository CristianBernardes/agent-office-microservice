"""Testes unitários do ``ApproveArtifactUseCase``."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.application.artifacts.approve_artifact_use_case import ApproveArtifactUseCase
from src.application.artifacts.artifact_errors import ArtifactNotFoundError
from src.domain.entities.agent import Role
from src.domain.entities.artifact import Artifact, ArtifactStatus, ArtifactType
from src.domain.exceptions.domain_exceptions import InvalidStateTransitionError
from src.domain.value_objects.identifiers import AgentId, ArtifactId
from src.infrastructure.filesystem.markdown_artifact_writer import MarkdownArtifactWriter
from src.infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from src.infrastructure.persistence.in_memory_artifact_repository import (
    InMemoryArtifactRepository,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def in_review_artifact() -> Artifact:
    artifact = Artifact(
        artifact_id=ArtifactId.generate(),
        title="ADR-002 — Autenticação JWT",
        content="# ADR-002",
        artifact_type=ArtifactType.ADR,
        path="sprint-1/adr-002.md",
        author_id=AgentId.generate(),
    )
    artifact.request_review()
    return artifact


class TestApproveArtifactUseCase:
    async def test_moves_in_review_artifact_to_approved(
        self, tmp_path: Path, in_review_artifact: Artifact
    ) -> None:
        repository = InMemoryArtifactRepository(
            writer=MarkdownArtifactWriter(workspace_root=str(tmp_path))
        )
        await repository.save(in_review_artifact)
        message_bus = InMemoryMessageBus()
        use_case = ApproveArtifactUseCase(artifact_repository=repository, message_bus=message_bus)

        approved_artifact = await use_case.execute(
            artifact_id=in_review_artifact.artifact_id,
            approver_id=AgentId.generate(),
            approver_role=Role.PRODUCT_OWNER,
        )

        assert approved_artifact.status == ArtifactStatus.APPROVED

    async def test_raises_when_artifact_does_not_exist(self, tmp_path: Path) -> None:
        repository = InMemoryArtifactRepository(
            writer=MarkdownArtifactWriter(workspace_root=str(tmp_path))
        )
        message_bus = InMemoryMessageBus()
        use_case = ApproveArtifactUseCase(artifact_repository=repository, message_bus=message_bus)

        with pytest.raises(ArtifactNotFoundError):
            await use_case.execute(
                artifact_id=ArtifactId.generate(),
                approver_id=AgentId.generate(),
                approver_role=Role.PRODUCT_OWNER,
            )

    async def test_raises_when_artifact_still_in_draft(self, tmp_path: Path) -> None:
        draft_artifact = Artifact(
            artifact_id=ArtifactId.generate(),
            title="Backlog — Sprint 1",
            content="# Backlog",
            artifact_type=ArtifactType.BACKLOG,
            path="sprint-1/backlog.md",
            author_id=AgentId.generate(),
        )
        repository = InMemoryArtifactRepository(
            writer=MarkdownArtifactWriter(workspace_root=str(tmp_path))
        )
        await repository.save(draft_artifact)
        message_bus = InMemoryMessageBus()
        use_case = ApproveArtifactUseCase(artifact_repository=repository, message_bus=message_bus)

        with pytest.raises(InvalidStateTransitionError):
            await use_case.execute(
                artifact_id=draft_artifact.artifact_id,
                approver_id=AgentId.generate(),
                approver_role=Role.PRODUCT_OWNER,
            )
