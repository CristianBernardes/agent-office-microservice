"""Schemas Pydantic da API de memórias (ADR-020)."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.entities.memory import Memory, MemoryType


class RememberRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=8000)
    memory_type: MemoryType = MemoryType.OBSERVATION
    importance: float = Field(default=0.5, ge=0, le=1)
    session_id: UUID | None = None


class RecallRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    limit: int = Field(default=5, ge=1, le=50)


class MemoryResponse(BaseModel):
    memory_id: UUID
    agent_id: UUID
    content: str
    memory_type: str
    importance: float

    @classmethod
    def from_entity(cls, memory: Memory) -> MemoryResponse:
        return cls(
            memory_id=memory.memory_id.value,
            agent_id=memory.agent_id.value,
            content=memory.content,
            memory_type=memory.memory_type.value,
            importance=memory.importance,
        )
