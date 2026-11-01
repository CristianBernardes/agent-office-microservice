"""Rotas HTTP de demissões propostas pelo RH. Camada fina: sem regra de negócio (ADR-056)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.dismissals.dismissal_use_cases import (
    DecideDismissalUseCase,
    DismissalNotFoundError,
    ProposeDismissalInput,
    ProposeDismissalUseCase,
)
from src.domain.entities.dismissal import DismissalProposal, DismissalStatus
from src.domain.exceptions.domain_exceptions import (
    InvalidStateTransitionError,
    InvalidValueError,
    PermissionDeniedError,
)
from src.domain.interfaces.dismissal_repository import IDismissalRepository
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import AgentId, DismissalId
from src.presentation.api.agents_router import get_request_language
from src.presentation.dependencies import (
    get_decide_dismissal_use_case,
    get_dismissal_repository,
    get_propose_dismissal_use_case,
)

router = APIRouter(prefix="/dismissals", tags=["dismissals"])


class ProposeDismissalRequest(BaseModel):
    proposer_id: UUID
    agent_id: UUID
    reason: str = Field(..., min_length=1, max_length=2000)


class DismissalResponse(BaseModel):
    proposal_id: str
    agent_id: str
    proposed_by: str
    reason: str
    status: DismissalStatus
    created_at: datetime
    decided_at: datetime | None

    @staticmethod
    def from_entity(proposal: DismissalProposal) -> DismissalResponse:
        """Converte a entidade no DTO público."""
        return DismissalResponse(
            proposal_id=str(proposal.proposal_id),
            agent_id=str(proposal.agent_id),
            proposed_by=str(proposal.proposed_by),
            reason=proposal.reason,
            status=proposal.status,
            created_at=proposal.created_at,
            decided_at=proposal.decided_at,
        )


def _http_error(error: Exception, language: Language) -> HTTPException:
    if isinstance(error, DismissalNotFoundError | AgentNotFoundError):
        return HTTPException(status.HTTP_404_NOT_FOUND, error.localized(language))
    if isinstance(error, PermissionDeniedError):
        return HTTPException(status.HTTP_403_FORBIDDEN, error.localized(language))
    if isinstance(error, InvalidValueError):
        return HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, error.localized(language))
    assert isinstance(error, InvalidStateTransitionError)
    return HTTPException(status.HTTP_409_CONFLICT, error.localized(language))


@router.get("", response_model=list[DismissalResponse])
async def list_dismissals(
    pending_only: bool = Query(default=False),
    repository: IDismissalRepository = Depends(get_dismissal_repository),
) -> list[DismissalResponse]:
    """Lista as propostas (``pending_only`` devolve só as que aguardam o dono do produto)."""
    items = await repository.list_all()
    return [
        DismissalResponse.from_entity(p)
        for p in items
        if not pending_only or p.status == DismissalStatus.PENDING
    ]


@router.post("", response_model=DismissalResponse, status_code=status.HTTP_201_CREATED)
async def propose_dismissal(
    body: ProposeDismissalRequest,
    use_case: ProposeDismissalUseCase = Depends(get_propose_dismissal_use_case),
    language: Language = Depends(get_request_language),
) -> DismissalResponse:
    """O RH propõe a demissão de um agente, com motivo (403 se não for RH)."""
    try:
        proposal = await use_case.execute(
            ProposeDismissalInput(
                proposer_id=AgentId(value=body.proposer_id),
                agent_id=AgentId(value=body.agent_id),
                reason=body.reason,
            )
        )
    except (
        AgentNotFoundError,
        PermissionDeniedError,
        InvalidValueError,
        InvalidStateTransitionError,
    ) as error:
        raise _http_error(error, language) from error
    return DismissalResponse.from_entity(proposal)


async def _decide(
    proposal_id: UUID,
    approved: bool,
    use_case: DecideDismissalUseCase,
    language: Language,
) -> DismissalResponse:
    try:
        proposal = await use_case.execute(DismissalId(value=proposal_id), approved)
    except (DismissalNotFoundError, InvalidStateTransitionError, AgentNotFoundError) as error:
        raise _http_error(error, language) from error
    return DismissalResponse.from_entity(proposal)


@router.post("/{proposal_id}/approve", response_model=DismissalResponse)
async def approve_dismissal(
    proposal_id: UUID,
    use_case: DecideDismissalUseCase = Depends(get_decide_dismissal_use_case),
    language: Language = Depends(get_request_language),
) -> DismissalResponse:
    """O dono do produto aprova: o agente é demitido e seu trabalho volta ao fluxo."""
    return await _decide(proposal_id, True, use_case, language)


@router.post("/{proposal_id}/reject", response_model=DismissalResponse)
async def reject_dismissal(
    proposal_id: UUID,
    use_case: DecideDismissalUseCase = Depends(get_decide_dismissal_use_case),
    language: Language = Depends(get_request_language),
) -> DismissalResponse:
    """O dono do produto rejeita: o agente continua no time."""
    return await _decide(proposal_id, False, use_case, language)
