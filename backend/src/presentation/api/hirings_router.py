"""Rotas HTTP de contratações propostas pelo RH. Camada fina: sem regra de negócio."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.hiring.hiring_use_cases import (
    ApproveHiringInput,
    DecideHiringUseCase,
    HiringNotFoundError,
)
from src.domain.entities.agent import Role
from src.domain.entities.hiring import HiringProposal, HiringStatus
from src.domain.exceptions.domain_exceptions import (
    InvalidStateTransitionError,
    InvalidValueError,
)
from src.domain.interfaces.hiring_repository import IHiringRepository
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import HiringId
from src.presentation.api.agents_router import get_request_language
from src.presentation.dependencies import get_decide_hiring_use_case, get_hiring_repository

router = APIRouter(prefix="/hirings", tags=["hirings"])


class ApproveHiringRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    llm_model: str = Field(..., min_length=1)


class HiringResponse(BaseModel):
    proposal_id: str
    role: Role
    proposed_by: str
    reason: str
    task_id: str | None
    status: HiringStatus
    hired_agent_id: str | None
    created_at: datetime
    decided_at: datetime | None

    @staticmethod
    def from_entity(proposal: HiringProposal) -> HiringResponse:
        """Converte a entidade no DTO público."""
        return HiringResponse(
            proposal_id=str(proposal.proposal_id),
            role=proposal.role,
            proposed_by=str(proposal.proposed_by),
            reason=proposal.reason,
            task_id=str(proposal.task_id) if proposal.task_id else None,
            status=proposal.status,
            hired_agent_id=str(proposal.hired_agent_id) if proposal.hired_agent_id else None,
            created_at=proposal.created_at,
            decided_at=proposal.decided_at,
        )


def _http_error(error: Exception, language: Language) -> HTTPException:
    if isinstance(error, HiringNotFoundError | AgentNotFoundError):
        return HTTPException(status.HTTP_404_NOT_FOUND, error.localized(language))
    if isinstance(error, InvalidValueError):
        return HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, error.localized(language))
    assert isinstance(error, InvalidStateTransitionError)
    return HTTPException(status.HTTP_409_CONFLICT, error.localized(language))


@router.get("", response_model=list[HiringResponse])
async def list_hirings(
    pending_only: bool = Query(default=False),
    repository: IHiringRepository = Depends(get_hiring_repository),
) -> list[HiringResponse]:
    """Lista as propostas (``pending_only`` devolve só as que aguardam o dono do produto)."""
    items = await repository.list_all()
    return [
        HiringResponse.from_entity(p)
        for p in items
        if not pending_only or p.status == HiringStatus.PENDING
    ]


@router.post("/{proposal_id}/approve", response_model=HiringResponse)
async def approve_hiring(
    proposal_id: UUID,
    body: ApproveHiringRequest,
    use_case: DecideHiringUseCase = Depends(get_decide_hiring_use_case),
    language: Language = Depends(get_request_language),
) -> HiringResponse:
    """O dono do produto aprova, escolhendo o nome e a IA do novo profissional."""
    try:
        proposal = await use_case.approve(
            ApproveHiringInput(HiringId(value=proposal_id), body.name, body.llm_model)
        )
    except (HiringNotFoundError, InvalidValueError, InvalidStateTransitionError) as error:
        raise _http_error(error, language) from error
    return HiringResponse.from_entity(proposal)


@router.post("/{proposal_id}/reject", response_model=HiringResponse)
async def reject_hiring(
    proposal_id: UUID,
    use_case: DecideHiringUseCase = Depends(get_decide_hiring_use_case),
    language: Language = Depends(get_request_language),
) -> HiringResponse:
    """O dono do produto rejeita: ninguém é contratado."""
    try:
        proposal = await use_case.reject(HiringId(value=proposal_id))
    except (HiringNotFoundError, InvalidStateTransitionError) as error:
        raise _http_error(error, language) from error
    return HiringResponse.from_entity(proposal)
