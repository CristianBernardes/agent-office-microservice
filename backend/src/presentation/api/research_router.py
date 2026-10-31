"""Rota de pesquisa de agentes. Camada fina (ADR-034)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.research.research_use_case import ResearchInput, ResearchTopicUseCase
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import AgentId
from src.presentation.api.agents_router import get_request_language
from src.presentation.dependencies import get_research_use_case

router = APIRouter(prefix="/research", tags=["research"])


class ResearchRequest(BaseModel):
    agent_id: UUID
    topic: str = Field(min_length=1, max_length=200)
    max_results: int = Field(default=5, ge=1, le=10)


class ResearchResponse(BaseModel):
    artifact_id: UUID
    title: str
    path: str
    content: str


@router.post("", response_model=ResearchResponse, status_code=201)
async def research(
    body: ResearchRequest,
    use_case: ResearchTopicUseCase = Depends(get_research_use_case),
    language: Language = Depends(get_request_language),
) -> ResearchResponse:
    """O agente pesquisa o tema e grava o relatório como artefato Markdown."""
    try:
        artifact = await use_case.execute(
            ResearchInput(AgentId(value=body.agent_id), body.topic, body.max_results)
        )
    except AgentNotFoundError as error:
        raise HTTPException(404, error.localized(language)) from error
    return ResearchResponse(
        artifact_id=artifact.artifact_id.value,
        title=artifact.title,
        path=artifact.path,
        content=artifact.content,
    )
