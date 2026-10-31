"""Injeção de dependência da camada de apresentação (FastAPI).

Centraliza a criação das implementações concretas de infraestrutura e a
composição dos casos de uso, conectando as portas definidas em ``domain/`` às
implementações de ``infrastructure/`` (ver ADR-007). É o único lugar do backend
onde "quem implementa o quê" é decidido.
"""

from __future__ import annotations

from functools import lru_cache

from src.application.agents.agent_think_use_case import AgentThinkUseCase
from src.application.agents.fire_agent_use_case import FireAgentUseCase
from src.application.agents.hire_agent_use_case import HireAgentUseCase
from src.application.artifacts.approve_artifact_use_case import ApproveArtifactUseCase
from src.application.artifacts.review_artifact_use_case import ReviewArtifactUseCase
from src.application.artifacts.write_artifact_use_case import WriteArtifactUseCase
from src.application.tools.tool_registry import ToolRegistry
from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.interfaces.artifact_repository import IArtifactRepository
from src.domain.interfaces.llm_adapter import ILlmAdapter
from src.domain.interfaces.llm_adapter_resolver import ILlmAdapterResolver
from src.domain.interfaces.message_bus import IMessageBus
from src.domain.interfaces.prompt_provider import IPromptProvider
from src.domain.interfaces.web_search_adapter import IWebSearchAdapter
from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.llm.ollama_adapter import OllamaAdapter
from src.infrastructure.llm.role_based_llm_adapter_resolver import RoleBasedLlmAdapterResolver
from src.infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from src.infrastructure.persistence.in_memory_agent_repository import (
    InMemoryAgentRepository,
)
from src.infrastructure.persistence.in_memory_artifact_repository import (
    InMemoryArtifactRepository,
)
from src.infrastructure.prompts.file_prompt_provider import FilePromptProvider
from src.infrastructure.search.tavily_adapter import TavilySearchAdapter


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


# Bloco: repositório de artefatos (singleton por processo).
# Mesmo racional do repositório de agentes: em memória nesta rodada, com a
# escrita real em disco delegada ao `MarkdownArtifactWriter` (ver RFC-002).
@lru_cache
def get_artifact_repository() -> IArtifactRepository:
    """Retorna a instância única do repositório de artefatos usado pela aplicação."""
    return InMemoryArtifactRepository()


# Bloco: barramento de mensagens (singleton por processo).
# `InMemoryMessageBus` é o padrão nesta rodada — o `MqttMessageBus` real exige
# uma conexão de rede estabelecida no bootstrap da aplicação (fora do escopo
# desta injeção de dependência síncrona; ver ADR-001).
@lru_cache
def get_message_bus() -> IMessageBus:
    """Retorna a instância única do barramento de mensagens usado pela aplicação."""
    return InMemoryMessageBus()


# Bloco: resolvedor de adaptador de LLM por papel (singleton por processo).
# `OllamaAdapter` é o provedor padrão deste projeto (ver ADR-005 e ADR-009); o
# modelo de cada papel vem de `.env` (Fase 5).
@lru_cache
def get_llm_adapter_resolver() -> ILlmAdapterResolver:
    """Retorna a instância única do resolvedor de adaptadores de LLM por papel."""
    settings = get_application_settings()

    def build_ollama_adapter(model: str) -> ILlmAdapter:
        return OllamaAdapter(
            base_url=settings.ollama_base_url,
            model=model,
            embedding_model=settings.ollama_embedding_model,
        )

    return RoleBasedLlmAdapterResolver(
        adapter_factory=build_ollama_adapter,
        default_model=settings.ollama_model,
        role_models=settings.role_models(),
    )


# Bloco: provedor de system prompts por papel (singleton por processo).
@lru_cache
def get_prompt_provider() -> IPromptProvider:
    """Retorna a instância única do provedor de prompts usado pela aplicação."""
    return FilePromptProvider()


# Bloco: adaptador de busca web (singleton por processo).
# `TavilySearchAdapter` é o provedor padrão deste projeto (ver ADR-011). A
# chave de API é resolvida de `.env` — se ausente, o adaptador falha de forma
# explícita apenas quando `web_search` é efetivamente chamado, não aqui.
@lru_cache
def get_web_search_adapter() -> IWebSearchAdapter:
    """Retorna a instância única do adaptador de busca web usado pela aplicação."""
    settings = get_application_settings()
    return TavilySearchAdapter(api_key=settings.tavily_api_key)


# Bloco: factory do caso de uso de criação de artefato.
def get_write_artifact_use_case() -> WriteArtifactUseCase:
    """Monta o caso de uso de criação de artefato com suas dependências."""
    return WriteArtifactUseCase(
        artifact_repository=get_artifact_repository(),
        message_bus=get_message_bus(),
    )


# Bloco: factory do caso de uso de solicitação de revisão de artefato.
def get_review_artifact_use_case() -> ReviewArtifactUseCase:
    """Monta o caso de uso de revisão de artefato com suas dependências."""
    return ReviewArtifactUseCase(
        artifact_repository=get_artifact_repository(),
        message_bus=get_message_bus(),
    )


# Bloco: factory do caso de uso de aprovação de artefato.
def get_approve_artifact_use_case() -> ApproveArtifactUseCase:
    """Monta o caso de uso de aprovação de artefato com suas dependências."""
    return ApproveArtifactUseCase(
        artifact_repository=get_artifact_repository(),
        message_bus=get_message_bus(),
    )


# Bloco: registro de ferramentas (singleton por processo).
# Composição central que liga os casos de uso de artefato e o adaptador de
# busca web às ferramentas que os agentes podem invocar (ver Fase 3).
@lru_cache
def get_tool_registry() -> ToolRegistry:
    """Monta o registro de ferramentas com todos os casos de uso e adaptadores necessários."""
    return ToolRegistry(
        write_artifact_use_case=get_write_artifact_use_case(),
        review_artifact_use_case=get_review_artifact_use_case(),
        approve_artifact_use_case=get_approve_artifact_use_case(),
        web_search_adapter=get_web_search_adapter(),
    )


# Bloco: factory do caso de uso de pensamento do agente.
def get_agent_think_use_case() -> AgentThinkUseCase:
    """Monta o caso de uso de pensamento do agente com suas dependências."""
    return AgentThinkUseCase(
        llm_adapter_resolver=get_llm_adapter_resolver(),
        message_bus=get_message_bus(),
        prompt_provider=get_prompt_provider(),
        tool_registry=get_tool_registry(),
    )
