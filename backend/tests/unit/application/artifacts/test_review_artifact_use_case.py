"""Testes unitários do ``ReviewArtifactUseCase``."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.application.artifacts.artifact_errors import ArtifactNotFoundError
from src.application.artifacts.review_artifact_use_case import ReviewArtifactUseCase
from src.domain.entities.agent import Role
from src.domain.entities.artifact import Artifact, ArtifactStatus, ArtifactType
from src.domain.value_objects.identifiers import AgentId, ArtifactId
from src.infrastructure.filesystem.markdown_artifact_writer import MarkdownArtifactWriter
from src.infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from src.infrastructure.persistence.in_memory_artifact_repository import (
    InMemoryArtifactRepository,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def draft_artifact() -> Artifact:
    return Artifact(
        artifact_id=ArtifactId.generate(),
        title="Design Doc — Autenticação",
        content="# Design Doc",
        artifact_type=ArtifactType.DESIGN_DOC,
        path="sprint-1/design-doc-auth.md",
        author_id=AgentId.generate(),
    )


class TestReviewArtifactUseCase:
    async def test_moves_draft_artifact_to_in_review(
        self, tmp_path: Path, draft_artifact: Artifact
    ) -> None:
        repository = InMemoryArtifactRepository(
            writer=MarkdownArtifactWriter(workspace_root=str(tmp_path))
        )
        await repository.save(draft_artifact)
        message_bus = InMemoryMessageBus()
        use_case = ReviewArtifactUseCase(artifact_repository=repository, message_bus=message_bus)

        reviewed_artifact = await use_case.execute(
            artifact_id=draft_artifact.artifact_id,
            reviewer_id=AgentId.generate(),
            reviewer_role=Role.TECH_LEAD,
        )

        assert reviewed_artifact.status == ArtifactStatus.IN_REVIEW

    async def test_publishes_artifact_updated_event(
        self, tmp_path: Path, draft_artifact: Artifact
    ) -> None:
        repository = InMemoryArtifactRepository(
            writer=MarkdownArtifactWriter(workspace_root=str(tmp_path))
        )
        await repository.save(draft_artifact)
        message_bus = InMemoryMessageBus()
        use_case = ReviewArtifactUseCase(artifact_repository=repository, message_bus=message_bus)

        await use_case.execute(
            artifact_id=draft_artifact.artifact_id,
            reviewer_id=AgentId.generate(),
            reviewer_role=Role.TECH_LEAD,
        )

        published_messages = message_bus.get_published_messages("office/artifacts/updated")
        assert len(published_messages) == 1

    async def test_raises_when_artifact_does_not_exist(self, tmp_path: Path) -> None:
        repository = InMemoryArtifactRepository(
            writer=MarkdownArtifactWriter(workspace_root=str(tmp_path))
        )
        message_bus = InMemoryMessageBus()
        use_case = ReviewArtifactUseCase(artifact_repository=repository, message_bus=message_bus)

        with pytest.raises(ArtifactNotFoundError):
            await use_case.execute(
                artifact_id=ArtifactId.generate(),
                reviewer_id=AgentId.generate(),
                reviewer_role=Role.TECH_LEAD,
            )
