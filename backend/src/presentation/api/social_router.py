"""Rotas de leitura de relacionamentos e reuniões. Camada fina (ADR-027/028)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from src.application.meetings.meeting_use_cases import ListMeetingsUseCase
from src.application.relationships.relationship_use_cases import ListRelationshipsUseCase
from src.domain.value_objects.identifiers import AgentId, GoalId
from src.presentation.api.relationship_schemas import MeetingResponse, RelationshipResponse
from src.presentation.dependencies import (
    get_list_meetings_use_case,
    get_list_relationships_use_case,
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
