"""Testes unitários dos relacionamentos entre agentes (ADR-027)."""

from __future__ import annotations

from uuid import UUID

import pytest

from src.application.relationships.relationship_use_cases import (
    ListRelationshipsUseCase,
    RecordInteractionInput,
    RecordInteractionUseCase,
)
from src.domain.entities.relationship import (
    Relationship,
    RelationshipStatus,
    derive_status,
    ordered_pair,
)
from src.domain.value_objects.identifiers import AgentId
from src.infrastructure.persistence.in_memory_relationship_repository import (
    InMemoryRelationshipRepository,
)

pytestmark = pytest.mark.unit

_A = AgentId(UUID(int=1))
_B = AgentId(UUID(int=2))
_C = AgentId(UUID(int=3))


class TestDomain:
    def test_pair_is_ordered(self) -> None:
        assert ordered_pair(_B, _A) == (_A, _B)
        rel = Relationship.between(_B, _A)
        assert (rel.agent_a, rel.agent_b) == (_A, _B)
        assert rel.status == RelationshipStatus.STRANGER

    def test_self_relationship_is_rejected(self) -> None:
        with pytest.raises(ValueError):
            Relationship.between(_A, _A)

    def test_unordered_or_out_of_range_is_rejected(self) -> None:
        with pytest.raises(ValueError):
            Relationship(agent_a=_B, agent_b=_A)
        with pytest.raises(ValueError):
            Relationship(agent_a=_A, agent_b=_B, score=2.0)

    @pytest.mark.parametrize(
        ("score", "interactions", "expected"),
        [
            (0.0, 0, RelationshipStatus.STRANGER),
            (0.1, 1, RelationshipStatus.ACQUAINTANCE),
            (0.1, 3, RelationshipStatus.COLLEAGUE),
            (0.6, 5, RelationshipStatus.FRIEND),
            (0.6, 4, RelationshipStatus.COLLEAGUE),
            (-0.5, 2, RelationshipStatus.RIVAL),
        ],
    )
    def test_derive_status(
        self, score: float, interactions: int, expected: RelationshipStatus
    ) -> None:
        assert derive_status(score, interactions) == expected

    def test_interact_clamps_score(self) -> None:
        rel = Relationship.between(_A, _B).interact(5.0)
        assert rel.score == 1.0
        assert rel.interactions == 1
        assert rel.last_interaction_at is not None


class TestUseCases:
    async def test_record_interaction_accumulates(self) -> None:
        repo = InMemoryRelationshipRepository()
        use_case = RecordInteractionUseCase(repo)
        await use_case.execute(RecordInteractionInput(_A, _B))
        result = await use_case.execute(RecordInteractionInput(_B, _A))
        assert result.interactions == 2
        assert result.score == pytest.approx(0.1)

    async def test_record_group_covers_every_pair_once(self) -> None:
        repo = InMemoryRelationshipRepository()
        await RecordInteractionUseCase(repo).record_group([_A, _B, _C, _A])
        listed = await ListRelationshipsUseCase(repo).execute(_A)
        assert len(listed) == 2
        assert all(r.interactions == 1 for r in listed)
        assert len(await repo.list_for(_C)) == 2
