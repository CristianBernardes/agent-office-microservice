"""Caso de uso: criar um novo artefato (documento Markdown) produzido por um agente.

Orquestra a criação da entidade ``Artifact``, sua persistência (metadados +
conteúdo em disco) através da porta ``IArtifactRepository`` e a notificação via
``IMessageBus`` (ver RFC-002) — sem conhecer qual implementação concreta de
repositório ou de barramento está sendo usada (ADR-007).
"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.common.message_envelope import build_message_envelope
from src.domain.entities.agent import Role
from src.domain.entities.artifact import Artifact, ArtifactType
from src.domain.interfaces.artifact_repository import IArtifactRepository
from src.domain.interfaces.message_bus import IMessageBus
from src.domain.value_objects.identifiers import AgentId, ArtifactId

# Bloco: tópico de notificação de criação de artefato, conforme a RFC-001.
_ARTIFACT_CREATED_TOPIC = "office/artifacts/created"


# Bloco: dados de entrada do caso de uso.
# `author_role` é necessário apenas para compor o envelope da mensagem MQTT
# (ver RFC-001) — a entidade `Artifact` em si não conhece papéis.
@dataclass(frozen=True, slots=True)
class WriteArtifactInput:
    title: str
    content: str
    artifact_type: ArtifactType
    path: str
    author_id: AgentId
    author_role: Role


# Bloco: caso de uso de criação de artefato.
# Depende apenas das interfaces de repositório e de barramento (Dependency
# Inversion Principle) — nunca de implementações concretas.
class WriteArtifactUseCase:
    def __init__(
        self,
        artifact_repository: IArtifactRepository,
        message_bus: IMessageBus,
    ) -> None:
        self._artifact_repository = artifact_repository
        self._message_bus = message_bus

    async def execute(self, use_case_input: WriteArtifactInput) -> Artifact:
        """Cria um artefato em ``DRAFT``, persiste e notifica via MQTT."""
        artifact = Artifact(
            artifact_id=ArtifactId.generate(),
            title=use_case_input.title,
            content=use_case_input.content,
            artifact_type=use_case_input.artifact_type,
            path=use_case_input.path,
            author_id=use_case_input.author_id,
        )

        await self._artifact_repository.save(artifact)
        await self._publish_created_event(artifact, use_case_input.author_role)

        return artifact

    async def _publish_created_event(self, artifact: Artifact, author_role: Role) -> None:
        """Publica o evento ``office/artifacts/created`` conforme a RFC-001."""
        envelope = build_message_envelope(
            agent_id=str(artifact.author_id),
            agent_role=author_role.value,
            payload={
                "artifact_id": str(artifact.artifact_id),
                "title": artifact.title,
                "type": artifact.artifact_type.value,
                "path": artifact.path,
                "status": artifact.status.value,
            },
        )
        await self._message_bus.publish(_ARTIFACT_CREATED_TOPIC, envelope, qos=1)
