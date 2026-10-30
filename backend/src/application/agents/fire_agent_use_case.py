"""Caso de uso: desligar um agente do time ("demitir").

Move o agente para o estado ``OFFLINE`` e persiste a mudança. Mantido simples e
focado em uma única responsabilidade, seguindo o Single Responsibility Principle.
"""

from __future__ import annotations

from src.domain.entities.agent import Agent
from src.domain.exceptions.domain_exceptions import DomainError
from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.value_objects.identifiers import AgentId


# Bloco: erro específico de aplicação quando o agente buscado não existe.
# Diferenciado de erros de domínio porque representa uma falha de orquestração
# (entrada inválida fornecida ao caso de uso), não uma violação de regra de
# negócio da entidade em si.
class AgentNotFoundError(DomainError):
    """Levantada quando o agente solicitado não é encontrado no repositório."""


# Bloco: caso de uso de desligamento de agente.
class FireAgentUseCase:
    def __init__(self, agent_repository: IAgentRepository) -> None:
        self._agent_repository = agent_repository

    async def execute(self, agent_id: AgentId) -> Agent:
        """Busca o agente pelo ID, marca-o como ``OFFLINE`` e persiste a mudança."""
        agent = await self._agent_repository.find_by_id(agent_id)
        if agent is None:
            raise AgentNotFoundError(f"Agente com ID '{agent_id}' não foi encontrado.")

        agent.go_offline()
        await self._agent_repository.save(agent)
        return agent
