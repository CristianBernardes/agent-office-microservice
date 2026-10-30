"""Injeção de dependência da camada de apresentação (FastAPI).

Centraliza a criação das implementações concretas de infraestrutura e a
composição dos casos de uso, conectando as portas definidas em ``domain/`` às
implementações de ``infrastructure/`` (ver ADR-007). É o único lugar do backend
onde "quem implementa o quê" é decidido.
"""

from __future__ import annotations

from functools import lru_cache

from src.application.agents.fire_agent_use_case import FireAgentUseCase
from src.application.agents.hire_agent_use_case import HireAgentUseCase
from src.domain.interfaces.agent_repository import IAgentRepository
from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.persistence.in_memory_agent_repository import (
    InMemoryAgentRepository,
)


# Bloco: repositório de agentes (singleton por processo).
# Nesta rodada de implementação, a persistência padrão é em memória (ver
# ADR-006: os repositórios PostgreSQL concretos chegam quando os casos de uso de
# persistência de agente forem completados nas fases seguintes do plano de
# migração). O singleton garante que o estado em memória seja compartilhado por
# todas as requisições do processo, e não recriado a cada chamada.
@lru_cache
def get_agent_repository() -> IAgentRepository:
    """Retorna a instância única do repositório de agentes usado pela aplicação."""
    return InMemoryAgentRepository()


# Bloco: factory do caso de uso de contratação de agente.
def get_hire_agent_use_case() -> HireAgentUseCase:
    """Monta o caso de uso de contratação de agente com suas dependências."""
    return HireAgentUseCase(agent_repository=get_agent_repository())


# Bloco: factory do caso de uso de desligamento de agente.
def get_fire_agent_use_case() -> FireAgentUseCase:
    """Monta o caso de uso de desligamento de agente com suas dependências."""
    return FireAgentUseCase(agent_repository=get_agent_repository())


# Bloco: exposição direta das configurações para rotas que precisem delas.
def get_application_settings() -> Settings:
    """Retorna as configurações do serviço, lidas a partir de variáveis de ambiente."""
    return get_settings()
