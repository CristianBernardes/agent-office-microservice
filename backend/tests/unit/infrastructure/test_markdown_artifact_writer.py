"""Testes unitários do ``MarkdownArtifactWriter``."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.domain.entities.artifact import Artifact, ArtifactType
from src.domain.value_objects.identifiers import AgentId, ArtifactId
from src.infrastructure.filesystem.markdown_artifact_writer import MarkdownArtifactWriter

pytestmark = pytest.mark.unit


@pytest.fixture
def sample_artifact() -> Artifact:
    return Artifact(
        artifact_id=ArtifactId.generate(),
        title="ADR-001 — Exemplo de Teste",
        content="# ADR-001\n\nConteúdo de exemplo para o teste.",
        artifact_type=ArtifactType.ADR,
        path="sprint-teste/adr-001-exemplo.md",
        author_id=AgentId.generate(),
    )


class TestMarkdownArtifactWriter:
    async def test_writes_file_under_workspace_root(
        self, tmp_path: Path, sample_artifact: Artifact
    ) -> None:
        writer = MarkdownArtifactWriter(workspace_root=str(tmp_path))

        written_path = await writer.write(sample_artifact)

        assert written_path.exists()
        assert written_path.name == "adr-001-exemplo.md"

    async def test_written_content_includes_frontmatter_and_body(
        self, tmp_path: Path, sample_artifact: Artifact
    ) -> None:
        writer = MarkdownArtifactWriter(workspace_root=str(tmp_path))

        written_path = await writer.write(sample_artifact)
        content = written_path.read_text(encoding="utf-8")

        assert content.startswith("---\n")
        assert f"id: {sample_artifact.artifact_id}" in content
        assert f"title: {sample_artifact.title}" in content
        assert "type: adr" in content
        assert "status: draft" in content
        assert sample_artifact.content in content

    async def test_creates_parent_directories_when_missing(
        self, tmp_path: Path, sample_artifact: Artifact
    ) -> None:
        writer = MarkdownArtifactWriter(workspace_root=str(tmp_path))

        written_path = await writer.write(sample_artifact)

        assert written_path.parent.is_dir()

    async def test_files_and_new_folders_are_world_writable(
        self, tmp_path: Path, sample_artifact: Artifact
    ) -> None:
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        writer = MarkdownArtifactWriter(workspace_root=str(workspace / "projects"))

        written_path = await writer.write(sample_artifact)

        assert written_path.stat().st_mode & 0o777 == 0o777
        assert written_path.parent.stat().st_mode & 0o777 == 0o777
        assert (workspace / "projects").stat().st_mode & 0o777 == 0o777

    async def test_does_not_create_missing_workspace(
        self, tmp_path: Path, sample_artifact: Artifact
    ) -> None:
        writer = MarkdownArtifactWriter(workspace_root=str(tmp_path / "ausente" / "projects"))

        with pytest.raises(FileNotFoundError):
            await writer.write(sample_artifact)

        assert not (tmp_path / "ausente").exists()
