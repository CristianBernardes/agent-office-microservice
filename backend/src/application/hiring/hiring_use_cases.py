"""Casos de uso de contratação com aprovação: o RH propõe o cargo, o dono escolhe nome e IA."""

from __future__ import annotations

from dataclasses import dataclass

from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.agents.hire_agent_use_case import HireAgentInput, HireAgentUseCase
from src.application.common.message_envelope import build_message_envelope
from src.application.tools.tool_permissions import ToolName, role_can_use_tool
from src.domain.entities.agent import Personality, Role
from src.domain.entities.hiring import HiringProposal, HiringStatus
from src.domain.exceptions.domain_exceptions import (
    DomainError,
    InvalidStateTransitionError,
    InvalidValueError,
    PermissionDeniedError,
)
from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.interfaces.hiring_repository import IHiringRepository
from src.domain.interfaces.message_bus import IMessageBus
from src.domain.value_objects.identifiers import AgentId, HiringId, TaskId

_PROPOSED_TOPIC = "office/hirings/proposed"
_DECIDED_TOPIC = "office/hirings/decided"

# Bloco: personalidade neutra para quem é contratado sem perfil definido.
_NEUTRAL_PERSONALITY = Personality(0.5, 0.5, 0.5, 0.5, 0.5)


class HiringNotFoundError(DomainError):
    """Levantada quando a proposta de contratação não existe."""


async def _publish(
    bus: IMessageBus, topic: str, proposal: HiringProposal, actor_id: str, actor_role: str
) -> None:
    envelope = build_message_envelope(
        agent_id=actor_id,
        agent_role=actor_role,
        payload={
            "proposal_id": str(proposal.proposal_id),
            "role": proposal.role.value,
            "status": proposal.status.value,
            "reason": proposal.reason,
            "hired_agent_id": str(proposal.hired_agent_id) if proposal.hired_agent_id else None,
        },
    )
    await bus.publish(topic, envelope, qos=1)


@dataclass(frozen=True, slots=True)
class ProposeHiringInput:
    proposer_id: AgentId
    role: Role
    reason: str
    task_id: TaskId | None = None


# Bloco: quem pode contratar propõe o cargo e o motivo; a proposta nunca contrata sozinha.
class ProposeHiringUseCase:
    def __init__(
        self,
        agent_repository: IAgentRepository,
        hiring_repository: IHiringRepository,
        message_bus: IMessageBus,
    ) -> None:
        self._agents = agent_repository
        self._hirings = hiring_repository
        self._bus = message_bus

    async def execute(self, data: ProposeHiringInput) -> HiringProposal:
        proposer = await self._agents.find_by_id(data.proposer_id)
        if proposer is None:
            raise AgentNotFoundError("agent.not_found", agent_id=data.proposer_id)
        if not role_can_use_tool(proposer.role, ToolName.HIRE_AGENT):
            raise PermissionDeniedError("hiring.propose_forbidden", role=proposer.role.value)
        reason = data.reason.strip()
        if not reason:
            raise InvalidValueError("hiring.reason_required")
        if data.task_id is not None:
            for existing in await self._hirings.list_all():
                if existing.task_id == data.task_id and existing.status == HiringStatus.PENDING:
                    raise InvalidStateTransitionError("hiring.already_pending")

        proposal = HiringProposal(
            HiringId.generate(), data.role, proposer.agent_id, reason, data.task_id
        )
        await self._hirings.save(proposal)
        await _publish(
            self._bus, _PROPOSED_TOPIC, proposal, str(proposer.agent_id), proposer.role.value
        )
        return proposal


@dataclass(frozen=True, slots=True)
class ApproveHiringInput:
    proposal_id: HiringId
    name: str
    llm_model: str


# Bloco: decisão do dono; aprovar contrata no cargo proposto com o nome e a IA que ele escolheu.
class DecideHiringUseCase:
    def __init__(
        self,
        hiring_repository: IHiringRepository,
        hire_agent: HireAgentUseCase,
        message_bus: IMessageBus,
        agent_repository: IAgentRepository,
    ) -> None:
        self._agents = agent_repository
        self._hirings = hiring_repository
        self._hire = hire_agent
        self._bus = message_bus

    async def approve(self, data: ApproveHiringInput) -> HiringProposal:
        proposal = await self._get(data.proposal_id)
        name = data.name.strip()
        model = data.llm_model.strip()
        if not name:
            raise InvalidValueError("hiring.name_required")
        if not model:
            raise InvalidValueError("hiring.model_required")
        proposal.ensure_pending()
        if any(a.name.casefold() == name.casefold() for a in await self._agents.list_all()):
            raise InvalidStateTransitionError("hiring.name_taken", name=name)
        agent = await self._hire.execute(
            HireAgentInput(
                name=name, role=proposal.role, personality=_NEUTRAL_PERSONALITY, llm_model=model
            )
        )
        proposal.approve(agent.agent_id)
        await self._hirings.save(proposal)
        await _publish(self._bus, _DECIDED_TOPIC, proposal, "user", "user")
        return proposal

    async def reject(self, proposal_id: HiringId) -> HiringProposal:
        proposal = await self._get(proposal_id)
        proposal.reject()
        await self._hirings.save(proposal)
        await _publish(self._bus, _DECIDED_TOPIC, proposal, "user", "user")
        return proposal

    async def _get(self, proposal_id: HiringId) -> HiringProposal:
        proposal = await self._hirings.get(proposal_id)
        if proposal is None:
            raise HiringNotFoundError("hiring.not_found", proposal_id=proposal_id)
        return proposal
