"""Rotas HTTP relacionadas a agentes.

A camada de apresentação apenas traduz requisições/respostas HTTP para chamadas
aos casos de uso da camada de aplicação — nenhuma regra de negócio deve ser
implementada neste módulo (ver ADR-007).
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status

from src.application.agents.fire_agent_use_case import (
    AgentNotFoundError,
    FireAgentUseCase,
)
from src.application.agents.hire_agent_use_case import HireAgentInput, HireAgentUseCase
from src.domain.entities.agent import Personality
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import AgentId
from src.infrastructure.config.settings import get_settings
from src.presentation.api.agent_schemas import AgentResponse, HireAgentRequest
from src.presentation.dependencies import get_fire_agent_use_case, get_hire_agent_use_case

router = APIRouter(prefix="/agents", tags=["agents"])


# Bloco: idioma da requisição a partir de Accept-Language (fallback: idioma do escritório).
def get_request_language(accept_language: str | None = Header(default=None)) -> Language:
    return Language.from_accept_language(accept_language, default=get_settings().language())


# Bloco: endpoint de contratação de um novo agente.
@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def hire_agent(
    request_body: HireAgentRequest,
    use_case: HireAgentUseCase = Depends(get_hire_agent_use_case),
) -> AgentResponse:
    """Contrata um novo agente com o papel, modelo e personalidade informados."""
    personality = Personality(
        openness=request_body.openness,
        conscientiousness=request_body.conscientiousness,
        extraversion=request_body.extraversion,
        agreeableness=request_body.agreeableness,
        neuroticism=request_body.neuroticism,
    )
    agent = await use_case.execute(
        HireAgentInput(
            name=request_body.name,
            role=request_body.role,
            personality=personality,
            llm_model=request_body.llm_model,
        )
    )
    return AgentResponse.from_entity(agent)


# Bloco: endpoint de desligamento de um agente existente.
@router.post("/{agent_id}/fire", response_model=AgentResponse)
async def fire_agent(
    agent_id: UUID,
    use_case: FireAgentUseCase = Depends(get_fire_agent_use_case),
    language: Language = Depends(get_request_language),
) -> AgentResponse:
    """Desliga (demite) o agente identificado por ``agent_id``."""
    try:
        agent = await use_case.execute(AgentId(value=agent_id))
    except AgentNotFoundError as not_found_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=not_found_error.localized(language)
        ) from not_found_error
    return AgentResponse.from_entity(agent)
