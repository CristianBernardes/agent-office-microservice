"""Entidade ``HiringProposal``: o RH propõe o cargo, o dono do produto escolhe nome e IA."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

from src.domain.entities.agent import Role
from src.domain.exceptions.domain_exceptions import InvalidStateTransitionError
from src.domain.value_objects.identifiers import AgentId, HiringId, TaskId


# Bloco: estados da proposta (espelha o CHECK da tabela hiring_proposals).
class HiringStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(slots=True)
class HiringProposal:
    proposal_id: HiringId
    role: Role
    proposed_by: AgentId
    reason: str
    task_id: TaskId | None = field(default=None)
    status: HiringStatus = field(default=HiringStatus.PENDING)
    hired_agent_id: AgentId | None = field(default=None)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    decided_at: datetime | None = field(default=None)

    def approve(self, hired_agent_id: AgentId) -> None:
        """Registra a aprovação e o agente contratado (só propostas pendentes)."""
        self.ensure_pending()
        self.status = HiringStatus.APPROVED
        self.hired_agent_id = hired_agent_id
        self.decided_at = datetime.now(UTC)

    def reject(self) -> None:
        """Registra a rejeição; só propostas pendentes podem ser decididas."""
        self.ensure_pending()
        self.status = HiringStatus.REJECTED
        self.decided_at = datetime.now(UTC)

    def ensure_pending(self) -> None:
        """Levanta erro se a proposta já foi decidida."""
        if self.status != HiringStatus.PENDING:
            raise InvalidStateTransitionError(
                "hiring.already_decided", proposal_id=self.proposal_id, status=self.status.value
            )
