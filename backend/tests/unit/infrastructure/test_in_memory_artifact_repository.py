"""Testes unitários do ``InMemoryArtifactRepository``."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.domain.entities.artifact import Artifact, ArtifactType
from src.domain.value_objects.identifiers import AgentId, ArtifactId
from src.infrastructure.filesystem.markdown_artifact_writer import MarkdownArtifactWriter
from src.infrastructure.persistence.in_memory_artifact_repository import (
    InMemoryArtifactRepository,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def sample_artifact() -> Artifact:
    return Artifact(
        artifact_id=ArtifactId.generate(),
        title="Backlog — Sprint de Teste",
        content="# Backlog\n\nConteúdo de exemplo.",
        artifact_type=ArtifactType.BACKLOG,
        path="sprint-teste/backlog.md",
        author_id=AgentId.generate(),
    )


class TestInMemoryArtifactRepository:
    async def test_save_persists_metadata_and_writes_file(
        self, tmp_path: Path, sample_artifact: Artifact
    ) -> None:
        repository = InMemoryArtifactRepository(
            writer=MarkdownArtifactWriter(workspace_root=str(tmp_path))
        )

        await repository.save(sample_artifact)

        persisted_artifact = await repository.find_by_id(sample_artifact.artifact_id)
        assert persisted_artifact is not None
        assert persisted_artifact.title == sample_artifact.title

        written_file = tmp_path / sample_artifact.path
        assert written_file.exists()

    async def test_find_by_id_returns_none_when_not_found(self, tmp_path: Path) -> None:
        repository = InMemoryArtifactRepository(
            writer=MarkdownArtifactWriter(workspace_root=str(tmp_path))
        )

        result = await repository.find_by_id(ArtifactId.generate())

        assert result is None

    async def test_list_all_returns_every_saved_artifact(
        self, tmp_path: Path, sample_artifact: Artifact
    ) -> None:
        repository = InMemoryArtifactRepository(
            writer=MarkdownArtifactWriter(workspace_root=str(tmp_path))
        )
        await repository.save(sample_artifact)

        artifacts = await repository.list_all()

        assert artifacts == [sample_artifact]
