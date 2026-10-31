"""Implementação PostgreSQL do ``IArtifactRepository`` (ver ADR-014 e RFC-002)."""

from __future__ import annotations

import asyncpg

from src.domain.entities.artifact import Artifact, ArtifactStatus, ArtifactType
from src.domain.interfaces.artifact_repository import IArtifactRepository
from src.domain.value_objects.identifiers import AgentId, ArtifactId
from src.infrastructure.filesystem.markdown_artifact_writer import MarkdownArtifactWriter

_UPSERT_SQL = """
INSERT INTO artifacts (artifact_id, title, content, artifact_type, path, author_id,
                       status, created_at, updated_at)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
ON CONFLICT (artifact_id) DO UPDATE SET
    title = EXCLUDED.title, content = EXCLUDED.content,
    artifact_type = EXCLUDED.artifact_type, path = EXCLUDED.path,
    author_id = EXCLUDED.author_id, status = EXCLUDED.status,
    updated_at = EXCLUDED.updated_at
"""


# Bloco: metadados e conteúdo no banco; arquivo Markdown real escrito em disco.
class PostgresArtifactRepository(IArtifactRepository):
    def __init__(self, pool: asyncpg.Pool, writer: MarkdownArtifactWriter | None = None) -> None:
        self._pool = pool
        self._writer = writer or MarkdownArtifactWriter()

    async def save(self, artifact: Artifact) -> None:
        """Escreve o Markdown em disco e faz upsert dos dados no banco."""
        await self._writer.write(artifact)
        await self._pool.execute(
            _UPSERT_SQL,
            artifact.artifact_id.value,
            artifact.title,
            artifact.content,
            artifact.artifact_type.value,
            artifact.path,
            artifact.author_id.value,
            artifact.status.value,
            artifact.created_at,
            artifact.updated_at,
        )

    async def find_by_id(self, artifact_id: ArtifactId) -> Artifact | None:
        """Retorna o artefato com o ID informado, ou ``None``."""
        row = await self._pool.fetchrow(
            "SELECT * FROM artifacts WHERE artifact_id = $1", artifact_id.value
        )
        return None if row is None else _to_artifact(row)

    async def list_all(self) -> list[Artifact]:
        """Retorna todos os artefatos, do mais antigo ao mais recente."""
        rows = await self._pool.fetch("SELECT * FROM artifacts ORDER BY created_at")
        return [_to_artifact(row) for row in rows]


def _to_artifact(row: asyncpg.Record) -> Artifact:
    return Artifact(
        artifact_id=ArtifactId(value=row["artifact_id"]),
        title=row["title"],
        content=row["content"],
        artifact_type=ArtifactType(row["artifact_type"]),
        path=row["path"],
        author_id=AgentId(value=row["author_id"]),
        status=ArtifactStatus(row["status"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
