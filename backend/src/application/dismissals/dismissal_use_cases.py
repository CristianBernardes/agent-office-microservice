"""Casos de uso de demissão com aprovação: o RH propõe, o dono do produto decide (ADR-056)."""

from __future__ import annotations

from dataclasses import dataclass

from src.application.agents.fire_agent_use_case import AgentNotFoundError, FireAgentUseCase
from src.application.common.message_envelope import build_message_envelope
from src.domain.entities.agent import AgentStatus, Role
from src.domain.entities.dismissal import DismissalProposal, DismissalStatus
from src.domain.exceptions.domain_exceptions import (
    DomainError,
    InvalidStateTransitionError,
    InvalidValueError,
    PermissionDeniedError,
)
from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.interfaces.dismissal_repository import IDismissalRepository
from src.domain.interfaces.message_bus import IMessageBus
from src.domain.value_objects.identifiers import AgentId, DismissalId

_PROPOSED_TOPIC = "office/dismissals/proposed"
_DECIDED_TOPIC = "office/dismissals/decided"


class DismissalNotFoundError(DomainError):
    """Levantada quando a proposta de demissão não existe."""


async def _publish(
    bus: IMessageBus, topic: str, proposal: DismissalProposal, actor_id: str, actor_role: str
) -> None:
    envelope = build_message_envelope(
        agent_id=actor_id,
        agent_role=actor_role,
        payload={
            "proposal_id": str(proposal.proposal_id),
            "agent_id": str(proposal.agent_id),
            "status": proposal.status.value,
            "reason": proposal.reason,
        },
    )
    await bus.publish(topic, envelope, qos=1)


@dataclass(frozen=True, slots=True)
class ProposeDismissalInput:
    proposer_id: AgentId
    agent_id: AgentId
    reason: str


# Bloco: só o RH propõe; a proposta exige motivo e nunca demite sozinha.
class ProposeDismissalUseCase:
    def __init__(
        self,
        agent_repository: IAgentRepository,
        dismissal_repository: IDismissalRepository,
        message_bus: IMessageBus,
    ) -> None:
        self._agents = agent_repository
        self._dismissals = dismissal_repository
        self._bus = message_bus

    async def execute(self, data: ProposeDismissalInput) -> DismissalProposal:
        proposer = await self._agents.find_by_id(data.proposer_id)
        if proposer is None:
            raise AgentNotFoundError("agent.not_found", agent_id=data.proposer_id)
        if proposer.role != Role.HR_MANAGER:
            raise PermissionDeniedError("dismissal.propose_forbidden", role=proposer.role.value)
        reason = data.reason.strip()
        if not reason:
            raise InvalidValueError("dismissal.reason_required")
        target = await self._agents.find_by_id(data.agent_id)
        if target is None:
            raise AgentNotFoundError("agent.not_found", agent_id=data.agent_id)
        if target.agent_id == proposer.agent_id:
            raise InvalidStateTransitionError("dismissal.cannot_propose_self", name=target.name)
        if target.status == AgentStatus.OFFLINE:
            raise InvalidStateTransitionError("dismissal.already_offline", name=target.name)
        for existing in await self._dismissals.list_all():
            if existing.agent_id == target.agent_id and existing.status == DismissalStatus.PENDING:
                raise InvalidStateTransitionError("dismissal.already_pending", name=target.name)

        proposal = DismissalProposal(
            DismissalId.generate(), target.agent_id, proposer.agent_id, reason
        )
        await self._dismissals.save(proposal)
        await _publish(
            self._bus, _PROPOSED_TOPIC, proposal, str(proposer.agent_id), proposer.role.value
        )
        return proposal


# Bloco: decisão do dono do produto; aprovar demite (devolve o trabalho ao fluxo), rejeitar arquiva.
class DecideDismissalUseCase:
    def __init__(
        self,
        dismissal_repository: IDismissalRepository,
        fire_agent: FireAgentUseCase,
        message_bus: IMessageBus,
    ) -> None:
        self._dismissals = dismissal_repository
        self._fire = fire_agent
        self._bus = message_bus

    async def execute(self, proposal_id: DismissalId, approved: bool) -> DismissalProposal:
        proposal = await self._dismissals.get(proposal_id)
        if proposal is None:
            raise DismissalNotFoundError("dismissal.not_found", proposal_id=proposal_id)
        proposal.decide(approved)
        if approved:
            await self._fire.execute(proposal.agent_id)
        await self._dismissals.save(proposal)
        await _publish(self._bus, _DECIDED_TOPIC, proposal, "user", "user")
        return proposal
