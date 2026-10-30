"""Testes unitários da entidade de domínio ``Artifact``."""

from __future__ import annotations

import pytest

from src.domain.entities.artifact import Artifact, ArtifactStatus, ArtifactType
from src.domain.exceptions.domain_exceptions import InvalidStateTransitionError
from src.domain.value_objects.identifiers import AgentId, ArtifactId

pytestmark = pytest.mark.unit


@pytest.fixture
def draft_artifact() -> Artifact:
    """Artefato de exemplo recém-criado, ainda em rascunho."""
    return Artifact(
        artifact_id=ArtifactId.generate(),
        title="ADR-001 — MQTT como barramento",
        content="# ADR-001\n\nConteúdo de exemplo.",
        artifact_type=ArtifactType.ADR,
        path="sprint-1/adr-001.md",
        author_id=AgentId.generate(),
    )


class TestArtifactLifecycle:
    def test_new_artifact_starts_as_draft(self, draft_artifact: Artifact) -> None:
        assert draft_artifact.status == ArtifactStatus.DRAFT

    def test_request_review_moves_draft_to_in_review(self, draft_artifact: Artifact) -> None:
        draft_artifact.request_review()
        assert draft_artifact.status == ArtifactStatus.IN_REVIEW

    def test_approve_moves_in_review_to_approved(self, draft_artifact: Artifact) -> None:
        draft_artifact.request_review()
        draft_artifact.approve()
        assert draft_artifact.status == ArtifactStatus.APPROVED

    def test_archive_moves_approved_to_archived(self, draft_artifact: Artifact) -> None:
        draft_artifact.request_review()
        draft_artifact.approve()
        draft_artifact.archive()
        assert draft_artifact.status == ArtifactStatus.ARCHIVED

    def test_cannot_approve_artifact_still_in_draft(self, draft_artifact: Artifact) -> None:
        with pytest.raises(InvalidStateTransitionError):
            draft_artifact.approve()

    def test_cannot_archive_artifact_not_yet_approved(self, draft_artifact: Artifact) -> None:
        draft_artifact.request_review()
        with pytest.raises(InvalidStateTransitionError):
            draft_artifact.archive()

    def test_cannot_request_review_twice(self, draft_artifact: Artifact) -> None:
        draft_artifact.request_review()
        with pytest.raises(InvalidStateTransitionError):
            draft_artifact.request_review()
