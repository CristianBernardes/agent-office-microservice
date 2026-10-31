"""Rotas HTTP das memórias dos agentes. Camada fina (ADR-020)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.memory.memory_use_cases import (
    RecallMemoryUseCase,
    RememberInput,
    RememberUseCase,
)
from src.domain.interfaces.memory_repository import IMemoryRepository
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import AgentId, SessionId
from src.presentation.api.agents_router import get_request_language
from src.presentation.api.memory_schemas import (
    MemoryResponse,
    RecallRequest,
    RememberRequest,
)
from src.presentation.dependencies import (
    get_memory_repository,
    get_recall_memory_use_case,
    get_remember_use_case,
)

router = APIRouter(prefix="/agents/{agent_id}/memories", tags=["memories"])


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def remember(
    agent_id: UUID,
    body: RememberRequest,
    use_case: RememberUseCase = Depends(get_remember_use_case),
    language: Language = Depends(get_request_language),
) -> MemoryResponse:
    """Grava uma memória vetorizada para o agente."""
    try:
        memory = await use_case.execute(
            RememberInput(
                agent_id=AgentId(value=agent_id),
                content=body.content,
                memory_type=body.memory_type,
                importance=body.importance,
                session_id=SessionId(value=body.session_id) if body.session_id else None,
            )
        )
    except AgentNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, error.localized(language)) from error
    return MemoryResponse.from_entity(memory)


@router.get("", response_model=list[MemoryResponse])
async def list_memories(
    agent_id: UUID,
    limit: int = Query(default=20, ge=1, le=200),
    repository: IMemoryRepository = Depends(get_memory_repository),
) -> list[MemoryResponse]:
    """Memórias recentes do agente."""
    memories = await repository.list_recent(AgentId(value=agent_id), limit)
    return [MemoryResponse.from_entity(m) for m in memories]


@router.post("/recall", response_model=list[MemoryResponse])
async def recall(
    agent_id: UUID,
    body: RecallRequest,
    use_case: RecallMemoryUseCase = Depends(get_recall_memory_use_case),
    language: Language = Depends(get_request_language),
) -> list[MemoryResponse]:
    """Recupera as memórias semanticamente mais próximas da consulta."""
    try:
        memories = await use_case.execute(AgentId(value=agent_id), body.query, body.limit)
    except AgentNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, error.localized(language)) from error
    return [MemoryResponse.from_entity(m) for m in memories]
