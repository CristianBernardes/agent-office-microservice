"""Schemas Pydantic das APIs de relacionamentos e reuniões (ADR-027/028)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.entities.meeting import Meeting
from src.domain.entities.relationship import Relationship


class RecordInteractionRequest(BaseModel):
    first: UUID
    second: UUID
    delta: float = Field(default=0.05, ge=-1.0, le=1.0)


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


class StartMeetingRequest(BaseModel):
    kind: str = Field(min_length=1)
    title: str = Field(min_length=1, max_length=200)
    organizer_id: UUID
    participants: list[UUID] = Field(default_factory=list)
    goal_id: UUID | None = None


class FinishMeetingRequest(BaseModel):
    summary: str = Field(min_length=1)
    decisions: list[str] = Field(default_factory=list)
