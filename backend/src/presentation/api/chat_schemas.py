"""Schemas Pydantic (DTOs) da API de chat e objetivos (ver ADR-019)."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.entities.chat import ChatMessage, Goal, MessageKind


class SubmitGoalRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)
    session_id: UUID | None = None


class GoalResponse(BaseModel):
    goal_id: UUID
    session_id: UUID
    text: str
    status: str

    @classmethod
    def from_entity(cls, goal: Goal) -> GoalResponse:
        return cls(
            goal_id=goal.goal_id.value,
            session_id=goal.session_id.value,
            text=goal.text,
            status=goal.status.value,
        )


class SendMessageRequest(BaseModel):
    session_id: UUID
    content: str = Field(..., min_length=1, max_length=8000)
    sender_id: UUID | None = None
    recipient_id: UUID | None = None
    task_id: UUID | None = None
    kind: MessageKind = MessageKind.CHAT


class MessageResponse(BaseModel):
    message_id: UUID
    session_id: UUID
    sender_id: UUID | None
    recipient_id: UUID | None
    task_id: UUID | None
    kind: str
    content: str

    @classmethod
    def from_entity(cls, message: ChatMessage) -> MessageResponse:
        return cls(
            message_id=message.message_id.value,
            session_id=message.session_id.value,
            sender_id=message.sender_id.value if message.sender_id else None,
            recipient_id=message.recipient_id.value if message.recipient_id else None,
            task_id=message.task_id.value if message.task_id else None,
            kind=message.kind.value,
            content=message.content,
        )
