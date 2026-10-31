"""Caso de uso: mover um artefato de ``IN_REVIEW`` para ``APPROVED``.

Separado do ``ReviewArtifactUseCase`` porque a decisão de aprovar pertence a um
subconjunto de papéis mais restrito (Tech Lead, Product Owner — ver RFC-002),
validado pelo ``ToolRegistry``, não por este caso de uso.
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


# Bloco: caso de uso de aprovação de artefato.
class ApproveArtifactUseCase:
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
        approver_id: AgentId,
        approver_role: Role,
    ) -> Artifact:
        """Busca o artefato, aprova-o e notifica via MQTT."""
        artifact = await self._artifact_repository.find_by_id(artifact_id)
        if artifact is None:
            raise ArtifactNotFoundError("artifact.not_found", artifact_id=artifact_id)

        artifact.approve()
        await self._artifact_repository.save(artifact)

        envelope = build_message_envelope(
            agent_id=str(approver_id),
            agent_role=approver_role.value,
            payload={
                "artifact_id": str(artifact.artifact_id),
                "status": artifact.status.value,
            },
        )
        await self._message_bus.publish(_ARTIFACT_UPDATED_TOPIC, envelope, qos=1)

        return artifact
