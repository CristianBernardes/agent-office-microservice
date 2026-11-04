"""Rota HTTP do chat direto do dono do produto com o RH. Camada fina (ADR-060)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.chat.chat_use_cases import SessionNotFoundError
from src.application.chat.hr_chat_use_case import HrChatInput, HrChatUseCase, HrUnavailableError
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import SessionId
from src.presentation.api.agents_router import get_request_language
from src.presentation.api.chat_schemas import HrChatRequest, HrChatResponse
from src.presentation.dependencies import get_hr_chat_use_case

router = APIRouter(tags=["hr-chat"])


@router.post("/hr/chat", response_model=HrChatResponse)
async def talk_to_hr(
    body: HrChatRequest,
    use_case: HrChatUseCase = Depends(get_hr_chat_use_case),
    language: Language = Depends(get_request_language),
) -> HrChatResponse:
    """Envia uma mensagem ao RH (cria a sessão se não informada) e devolve a resposta."""
    try:
        result = await use_case.execute(
            HrChatInput(
                content=body.content,
                session_id=SessionId(value=body.session_id) if body.session_id else None,
                language=language,
            )
        )
    except (SessionNotFoundError, AgentNotFoundError) as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, error.localized(language)) from error
    except HrUnavailableError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, error.localized(language)) from error
    return HrChatResponse.from_result(result)
