"""Rotas de leitura de relacionamentos e reuniões. Camada fina (ADR-027/028)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.application.meetings.meeting_use_cases import (
    FinishMeetingUseCase,
    ListMeetingsUseCase,
    StartCeremonyInput,
    StartCeremonyUseCase,
)
from src.application.relationships.relationship_use_cases import ListRelationshipsUseCase
from src.domain.entities.meeting import MeetingKind
from src.domain.exceptions.domain_exceptions import DomainError
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import AgentId, GoalId, MeetingId
from src.presentation.api.agents_router import get_request_language
from src.presentation.api.relationship_schemas import (
    FinishMeetingRequest,
    MeetingResponse,
    RelationshipResponse,
    StartMeetingRequest,
)
from src.presentation.dependencies import (
    get_finish_meeting_use_case,
    get_list_meetings_use_case,
    get_list_relationships_use_case,
    get_start_ceremony_use_case,
)

router = APIRouter(tags=["social"])


@router.get("/agents/{agent_id}/relationships", response_model=list[RelationshipResponse])
async def list_relationships(
    agent_id: UUID,
    use_case: ListRelationshipsUseCase = Depends(get_list_relationships_use_case),
) -> list[RelationshipResponse]:
    """Vínculos do agente com os colegas."""
    items = await use_case.execute(AgentId(value=agent_id))
    return [RelationshipResponse.from_entity(item) for item in items]


@router.get("/goals/{goal_id}/meetings", response_model=list[MeetingResponse])
async def list_goal_meetings(
    goal_id: UUID,
    use_case: ListMeetingsUseCase = Depends(get_list_meetings_use_case),
) -> list[MeetingResponse]:
    """Reuniões realizadas para um objetivo."""
    meetings = await use_case.by_goal(GoalId(value=goal_id))
    return [MeetingResponse.from_entity(m) for m in meetings]


@router.post("/meetings", response_model=MeetingResponse, status_code=201)
async def start_meeting(
    body: StartMeetingRequest,
    use_case: StartCeremonyUseCase = Depends(get_start_ceremony_use_case),
) -> MeetingResponse:
    """Inicia uma cerimônia (daily, retro, planning...)."""
    try:
        kind = MeetingKind(body.kind)
    except ValueError as error:
        raise HTTPException(422, f"kind inválido: {body.kind}") from error
    meeting = await use_case.execute(
        StartCeremonyInput(
            kind=kind,
            title=body.title,
            organizer_id=AgentId(value=body.organizer_id),
            participants=tuple(AgentId(value=p) for p in body.participants),
            goal_id=GoalId(value=body.goal_id) if body.goal_id else None,
        )
    )
    return MeetingResponse.from_entity(meeting)


@router.post("/meetings/{meeting_id}/finish", response_model=MeetingResponse)
async def finish_meeting(
    meeting_id: UUID,
    body: FinishMeetingRequest,
    use_case: FinishMeetingUseCase = Depends(get_finish_meeting_use_case),
    language: Language = Depends(get_request_language),
) -> MeetingResponse:
    """Encerra a reunião com resumo e decisões."""
    try:
        meeting = await use_case.execute(
            MeetingId(value=meeting_id), body.summary, tuple(body.decisions)
        )
    except DomainError as error:
        status = 404 if error.message_key == "meeting.not_found" else 409
        raise HTTPException(status, error.localized(language)) from error
    return MeetingResponse.from_entity(meeting)
