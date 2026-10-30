"""Contrato (porta) para persistência de artefatos.

Mantida pequena e focada no que os casos de uso desta rodada efetivamente
precisam (salvar, buscar, listar), evitando antecipar operações sem um
consumidor real (princípio YAGNI) — ver RFC-002.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.artifact import Artifact
from src.domain.value_objects.identifiers import ArtifactId


# Bloco: contrato único de persistência de artefatos.
class IArtifactRepository(ABC):
    @abstractmethod
    async def save(self, artifact: Artifact) -> None:
        """Persiste um artefato (criação ou atualização), incluindo seu conteúdo em disco."""

    @abstractmethod
    async def find_by_id(self, artifact_id: ArtifactId) -> Artifact | None:
        """Busca um artefato pelo seu identificador, ou ``None`` se não existir."""

    @abstractmethod
    async def list_all(self) -> list[Artifact]:
        """Lista todos os artefatos atualmente persistidos."""
