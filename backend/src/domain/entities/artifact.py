"""Entidade de domínio ``Artifact`` e os tipos que a compõem.

Representa um documento Markdown produzido por um agente (ADR, plano de teste,
relatório de bug, etc.), com um ciclo de vida de revisão (ver RFC-002).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

from src.domain.exceptions.domain_exceptions import InvalidStateTransitionError
from src.domain.value_objects.identifiers import AgentId, ArtifactId


# Bloco: tipos de artefato que um agente pode produzir.
class ArtifactType(str, Enum):
    BACKLOG = "backlog"
    SPRINT_PLANNING = "sprint_planning"
    ADR = "adr"
    DESIGN_DOC = "design_doc"
    IMPLEMENTATION = "implementation"
    TEST_PLAN = "test_plan"
    BUG_REPORT = "bug_report"
    ANALYSIS = "analysis"
    RETROSPECTIVE = "retrospective"
    USER_STORY = "user_story"
    ONBOARDING = "onboarding"


# Bloco: estados do ciclo de vida de um artefato (ver RFC-002).
class ArtifactStatus(str, Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    ARCHIVED = "archived"


# Bloco: entidade de domínio ``Artifact``.
# Controla as transições do ciclo de revisão: um artefato só pode ser aprovado
# depois de passar por revisão, e só pode ser arquivado depois de aprovado.
@dataclass(slots=True)
class Artifact:
    artifact_id: ArtifactId
    title: str
    content: str
    artifact_type: ArtifactType
    path: str
    author_id: AgentId
    status: ArtifactStatus = field(default=ArtifactStatus.DRAFT)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def request_review(self) -> None:
        """Move o artefato de ``DRAFT`` para ``IN_REVIEW``."""
        if self.status != ArtifactStatus.DRAFT:
            raise InvalidStateTransitionError(
                "artifact.cannot_request_review", title=self.title, status=self.status.value
            )
        self.status = ArtifactStatus.IN_REVIEW
        self.updated_at = datetime.now(UTC)

    def approve(self) -> None:
        """Aprova o artefato, movendo-o de ``IN_REVIEW`` para ``APPROVED``."""
        if self.status != ArtifactStatus.IN_REVIEW:
            raise InvalidStateTransitionError(
                "artifact.cannot_approve", title=self.title, status=self.status.value
            )
        self.status = ArtifactStatus.APPROVED
        self.updated_at = datetime.now(UTC)

    def archive(self) -> None:
        """Arquiva o artefato, movendo-o de ``APPROVED`` para ``ARCHIVED``."""
        if self.status != ArtifactStatus.APPROVED:
            raise InvalidStateTransitionError(
                "artifact.cannot_archive", title=self.title, status=self.status.value
            )
        self.status = ArtifactStatus.ARCHIVED
        self.updated_at = datetime.now(UTC)
