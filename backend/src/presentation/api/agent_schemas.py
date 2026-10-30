"""Schemas Pydantic (DTOs) da API HTTP relacionados a agentes.

Mantidos na camada de apresentação, isolados das entidades de domínio — a API
nunca expõe diretamente as entidades internas, evitando acoplar o contrato HTTP
público à modelagem interna do domínio (ver ADR-007).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.domain.entities.agent import Agent, AgentStatus, Role


# Bloco: corpo de requisição para contratar um novo agente.
class HireAgentRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    role: Role
    llm_model: str = Field(..., min_length=1)
    openness: float = Field(default=0.5, ge=0.0, le=1.0)
    conscientiousness: float = Field(default=0.5, ge=0.0, le=1.0)
    extraversion: float = Field(default=0.5, ge=0.0, le=1.0)
    agreeableness: float = Field(default=0.5, ge=0.0, le=1.0)
    neuroticism: float = Field(default=0.5, ge=0.0, le=1.0)


# Bloco: representação de um agente retornada pela API.
class AgentResponse(BaseModel):
    agent_id: str
    name: str
    role: Role
    status: AgentStatus
    llm_model: str

    @staticmethod
    def from_entity(agent: Agent) -> AgentResponse:
        """Converte a entidade de domínio ``Agent`` no DTO público da API."""
        return AgentResponse(
            agent_id=str(agent.agent_id),
            name=agent.name,
            role=agent.role,
            status=agent.status,
            llm_model=agent.llm_model,
        )
