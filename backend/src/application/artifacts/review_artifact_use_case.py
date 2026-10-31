"""Caso de uso: mover um artefato de ``DRAFT`` para ``IN_REVIEW``.

Mantido como um caso de uso independente (Single Responsibility Principle),
separado da criação e da aprovação — cada transição de estado do artefato tem
sua própria orquestração, podendo evoluir isoladamente (ex.: anexar
comentários de revisão em uma rodada futura, sem afetar os demais).
"""

from __future__ import annotations

from src.application.artifacts.artifact_errors import ArtifactNotFoundError
from src.application.common.message_envelope import build_message_envelope
from src.domain.entities.agent import Role
from src.domain.entities.artifact import Artifact
from src.domain.interfaces.artifact_repository import IArtifactRepository
from src.domain.interfaces.message_bus import IMessageBus
from src.domain.value_objects.identifiers import AgentId, ArtifactId

# Bloco: tópico de notificação de atualização de artefato, conforme a RFC-001.
_ARTIFACT_UPDATED_TOPIC = "office/artifacts/updated"


# Bloco: caso de uso de solicitação de revisão de artefato.
class ReviewArtifactUseCase:
    def __init__(
        self,
        artifact_repository: IArtifactRepository,
        message_bus: IMessageBus,
    ) -> None:
        self._artifact_repository = artifact_repository
        self._message_bus = message_bus

    async def execute(
        self,
        artifact_id: ArtifactId,
        reviewer_id: AgentId,
        reviewer_role: Role,
    ) -> Artifact:
        """Busca o artefato, move-o para ``IN_REVIEW`` e notifica via MQTT."""
        artifact = await self._artifact_repository.find_by_id(artifact_id)
        if artifact is None:
            raise ArtifactNotFoundError("artifact.not_found", artifact_id=artifact_id)

        artifact.request_review()
        await self._artifact_repository.save(artifact)

        envelope = build_message_envelope(
            agent_id=str(reviewer_id),
            agent_role=reviewer_role.value,
            payload={
                "artifact_id": str(artifact.artifact_id),
                "status": artifact.status.value,
            },
        )
        await self._message_bus.publish(_ARTIFACT_UPDATED_TOPIC, envelope, qos=1)

        return artifact
