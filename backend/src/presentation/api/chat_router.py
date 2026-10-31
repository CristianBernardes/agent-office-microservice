"""Rotas HTTP de objetivos e chat. Camada fina: sem regra de negócio (ADR-019)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.chat.chat_use_cases import (
    SendMessageInput,
    SendMessageUseCase,
    SessionNotFoundError,
    SubmitGoalInput,
    SubmitGoalUseCase,
)
from src.domain.interfaces.chat_repository import IChatRepository
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import AgentId, SessionId, TaskId
from src.presentation.api.agents_router import get_request_language
from src.presentation.api.chat_schemas import (
    GoalResponse,
    MessageResponse,
    SendMessageRequest,
    SubmitGoalRequest,
)
from src.presentation.dependencies import (
    get_chat_repository,
    get_send_message_use_case,
    get_submit_goal_use_case,
)

router = APIRouter(tags=["chat"])


def _not_found(
    error: SessionNotFoundError | AgentNotFoundError, language: Language
) -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, error.localized(language))


@router.post("/goals", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def submit_goal(
    body: SubmitGoalRequest,
    use_case: SubmitGoalUseCase = Depends(get_submit_goal_use_case),
    language: Language = Depends(get_request_language),
) -> GoalResponse:
    """Entrega um objetivo aos agentes (cria a sessão se não informada)."""
    session_id = SessionId(value=body.session_id) if body.session_id else None
    try:
        goal = await use_case.execute(
            SubmitGoalInput(text=body.text, session_id=session_id, language=language)
        )
    except SessionNotFoundError as error:
        raise _not_found(error, language) from error
    return GoalResponse.from_entity(goal)


@router.get("/goals", response_model=list[GoalResponse])
async def list_goals(
    repository: IChatRepository = Depends(get_chat_repository),
) -> list[GoalResponse]:
    """Lista os objetivos."""
    return [GoalResponse.from_entity(goal) for goal in await repository.list_goals()]


@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    body: SendMessageRequest,
    use_case: SendMessageUseCase = Depends(get_send_message_use_case),
    language: Language = Depends(get_request_language),
) -> MessageResponse:
    """Envia uma mensagem de chat (sem ``sender_id`` = usuário)."""
    try:
        message = await use_case.execute(
            SendMessageInput(
                session_id=SessionId(value=body.session_id),
                content=body.content,
                sender_id=AgentId(value=body.sender_id) if body.sender_id else None,
                recipient_id=AgentId(value=body.recipient_id) if body.recipient_id else None,
                task_id=TaskId(value=body.task_id) if body.task_id else None,
                kind=body.kind,
            )
        )
    except (SessionNotFoundError, AgentNotFoundError) as error:
        raise _not_found(error, language) from error
    return MessageResponse.from_entity(message)


@router.get("/sessions/{session_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    session_id: UUID,
    limit: int = Query(default=100, ge=1, le=500),
    repository: IChatRepository = Depends(get_chat_repository),
    language: Language = Depends(get_request_language),
) -> list[MessageResponse]:
    """Lista as mensagens da sessão em ordem cronológica."""
    sid = SessionId(value=session_id)
    if await repository.find_session(sid) is None:
        raise _not_found(SessionNotFoundError("chat.session_not_found", session_id=sid), language)
    return [MessageResponse.from_entity(m) for m in await repository.list_messages(sid, limit)]
