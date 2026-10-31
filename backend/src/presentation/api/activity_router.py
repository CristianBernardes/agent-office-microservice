"""Rota do feed de atividades. Camada fina (ADR-031)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from src.application.activity.activity_feed import ListActivityUseCase
from src.domain.entities.activity_event import ActivityEvent
from src.presentation.dependencies import get_list_activity_use_case

router = APIRouter(prefix="/activity", tags=["activity"])


class ActivityResponse(BaseModel):
    event_id: UUID
    kind: str
    agent_id: UUID | None
    payload: dict[str, Any]
    created_at: datetime

    @classmethod
    def from_entity(cls, event: ActivityEvent) -> ActivityResponse:
        return cls(
            event_id=event.event_id,
            kind=event.kind,
            agent_id=event.agent_id,
            payload=event.payload,
            created_at=event.created_at,
        )


@router.get("", response_model=list[ActivityResponse])
async def list_activity(
    limit: int = Query(default=50, ge=1, le=200),
    use_case: ListActivityUseCase = Depends(get_list_activity_use_case),
) -> list[ActivityResponse]:
    return [ActivityResponse.from_entity(e) for e in await use_case.execute(limit)]
