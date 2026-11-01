"""Entidade ``DismissalProposal``: o RH propõe, o dono do produto decide (ADR-056)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

from src.domain.exceptions.domain_exceptions import InvalidStateTransitionError
from src.domain.value_objects.identifiers import AgentId, DismissalId


# Bloco: estados da proposta (espelha o CHECK da tabela dismissal_proposals).
class DismissalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(slots=True)
class DismissalProposal:
    proposal_id: DismissalId
    agent_id: AgentId
    proposed_by: AgentId
    reason: str
    status: DismissalStatus = field(default=DismissalStatus.PENDING)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    decided_at: datetime | None = field(default=None)

    def decide(self, approved: bool) -> None:
        """Registra a decisão do dono do produto; só propostas pendentes podem ser decididas."""
        if self.status != DismissalStatus.PENDING:
            raise InvalidStateTransitionError(
                "dismissal.already_decided", proposal_id=self.proposal_id, status=self.status.value
            )
        self.status = DismissalStatus.APPROVED if approved else DismissalStatus.REJECTED
        self.decided_at = datetime.now(UTC)
