"""Schemas Pydantic das APIs de relacionamentos e reuniões (ADR-027/028)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.domain.entities.meeting import Meeting
from src.domain.entities.relationship import Relationship


class RelationshipResponse(BaseModel):
    agent_a: UUID
    agent_b: UUID
    score: float
    status: str
    interactions: int
    last_interaction_at: datetime | None

    @classmethod
    def from_entity(cls, relationship: Relationship) -> RelationshipResponse:
        return cls(
            agent_a=relationship.agent_a.value,
            agent_b=relationship.agent_b.value,
            score=relationship.score,
            status=relationship.status.value,
            interactions=relationship.interactions,
            last_interaction_at=relationship.last_interaction_at,
        )


class MeetingResponse(BaseModel):
    meeting_id: UUID
    kind: str
    title: str
    status: str
    goal_id: UUID | None
    organizer_id: UUID | None
    participants: list[UUID]
    summary: str
    decisions: list[str]
    started_at: datetime | None
    ended_at: datetime | None

    @classmethod
    def from_entity(cls, meeting: Meeting) -> MeetingResponse:
        return cls(
            meeting_id=meeting.meeting_id.value,
            kind=meeting.kind.value,
            title=meeting.title,
            status=meeting.status.value,
            goal_id=meeting.goal_id.value if meeting.goal_id else None,
            organizer_id=meeting.organizer_id.value if meeting.organizer_id else None,
            participants=[p.value for p in meeting.participants],
            summary=meeting.summary,
            decisions=list(meeting.decisions),
            started_at=meeting.started_at,
            ended_at=meeting.ended_at,
        )
