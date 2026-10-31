"""Entidade ``Relationship``: vínculo entre dois agentes (ver ADR-027)."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import Enum

from src.domain.value_objects.identifiers import AgentId


# Bloco: estado do vínculo (espelha o CHECK da tabela relationships).
class RelationshipStatus(str, Enum):
    STRANGER = "stranger"
    ACQUAINTANCE = "acquaintance"
    COLLEAGUE = "colleague"
    FRIEND = "friend"
    RIVAL = "rival"


_RIVAL_SCORE = -0.3
_FRIEND_SCORE = 0.5
_FRIEND_MIN_INTERACTIONS = 5
_COLLEAGUE_MIN_INTERACTIONS = 3


# Bloco: regra de domínio que deriva o status a partir do histórico.
def derive_status(score: float, interactions: int) -> RelationshipStatus:
    if interactions == 0:
        return RelationshipStatus.STRANGER
    if score <= _RIVAL_SCORE:
        return RelationshipStatus.RIVAL
    if score >= _FRIEND_SCORE and interactions >= _FRIEND_MIN_INTERACTIONS:
        return RelationshipStatus.FRIEND
    if interactions >= _COLLEAGUE_MIN_INTERACTIONS:
        return RelationshipStatus.COLLEAGUE
    return RelationshipStatus.ACQUAINTANCE


def ordered_pair(first: AgentId, second: AgentId) -> tuple[AgentId, AgentId]:
    """Ordena o par como o banco exige (``agent_a < agent_b``)."""
    return (first, second) if first.value < second.value else (second, first)


@dataclass(frozen=True, slots=True)
class Relationship:
    agent_a: AgentId
    agent_b: AgentId
    score: float = 0.0
    interactions: int = 0
    status: RelationshipStatus = RelationshipStatus.STRANGER
    last_interaction_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.agent_a.value >= self.agent_b.value:
            raise ValueError("agent_a deve ser menor que agent_b (use ordered_pair)")
        if not -1.0 <= self.score <= 1.0:
            raise ValueError("score deve estar entre -1 e 1")

    @classmethod
    def between(cls, first: AgentId, second: AgentId) -> Relationship:
        if first == second:
            raise ValueError("Um agente não pode ter relacionamento consigo mesmo")
        a, b = ordered_pair(first, second)
        return cls(agent_a=a, agent_b=b)

    def interact(self, delta: float, now: datetime | None = None) -> Relationship:
        score = max(-1.0, min(1.0, self.score + delta))
        interactions = self.interactions + 1
        return replace(
            self,
            score=score,
            interactions=interactions,
            status=derive_status(score, interactions),
            last_interaction_at=now or datetime.now(UTC),
        )
