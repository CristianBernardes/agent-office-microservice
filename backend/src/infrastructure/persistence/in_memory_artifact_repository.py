"""Implementação em memória do ``IArtifactRepository``.

Mantém os metadados em um dicionário em memória e delega a escrita do conteúdo
em disco ao ``MarkdownArtifactWriter`` — útil para testes unitários/de
integração sem depender de um PostgreSQL real, e como implementação padrão ao
executar o backend localmente sem banco configurado (ver RFC-002 e ADR-006:
a implementação PostgreSQL concreta permanece pendente para uma rodada futura).
"""

from __future__ import annotations

from src.domain.entities.artifact import Artifact
from src.domain.interfaces.artifact_repository import IArtifactRepository
from src.domain.value_objects.identifiers import ArtifactId
from src.infrastructure.filesystem.markdown_artifact_writer import MarkdownArtifactWriter


# Bloco: repositório de artefatos baseado em um dicionário em memória, com
# escrita real em disco via ``MarkdownArtifactWriter``.
# Implementa o contrato `IArtifactRepository` por completo, permitindo
# substituição transparente por uma implementação PostgreSQL futura, sem
# alterar os casos de uso que dependem apenas da interface.
class InMemoryArtifactRepository(IArtifactRepository):
    def __init__(self, writer: MarkdownArtifactWriter | None = None) -> None:
        self._artifacts_by_id: dict[ArtifactId, Artifact] = {}
        self._writer = writer or MarkdownArtifactWriter()

    async def save(self, artifact: Artifact) -> None:
        """Persiste os metadados em memória e o conteúdo em disco (Markdown real)."""
        await self._writer.write(artifact)
        self._artifacts_by_id[artifact.artifact_id] = artifact

    async def find_by_id(self, artifact_id: ArtifactId) -> Artifact | None:
        """Retorna o artefato com o ID informado, ou ``None`` se não existir."""
        return self._artifacts_by_id.get(artifact_id)

    async def list_all(self) -> list[Artifact]:
        """Retorna todos os artefatos atualmente persistidos."""
        return list(self._artifacts_by_id.values())
