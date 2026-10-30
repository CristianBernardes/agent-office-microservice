"""Implementação em memória do ``IAgentRepository``.

Útil para testes unitários/de integração sem depender de um PostgreSQL real, e
também como implementação padrão ao executar o backend localmente sem banco
configurado (ambiente mínimo de desenvolvimento). Não é adequada para produção —
os dados não sobrevivem a um restart do processo.
"""

from __future__ import annotations

from src.domain.entities.agent import Agent
from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.value_objects.identifiers import AgentId


# Bloco: repositório de agentes baseado em um dicionário em memória.
# Implementa o contrato `IAgentRepository` por completo, permitindo substituição
# transparente por uma implementação PostgreSQL futura, sem alterar os casos de
# uso que dependem apenas da interface.
class InMemoryAgentRepository(IAgentRepository):
    def __init__(self) -> None:
        self._agents_by_id: dict[AgentId, Agent] = {}

    async def save(self, agent: Agent) -> None:
        """Persiste (cria ou atualiza) um agente no dicionário em memória."""
        self._agents_by_id[agent.agent_id] = agent

    async def find_by_id(self, agent_id: AgentId) -> Agent | None:
        """Retorna o agente com o ID informado, ou ``None`` se não existir."""
        return self._agents_by_id.get(agent_id)

    async def list_all(self) -> list[Agent]:
        """Retorna todos os agentes atualmente persistidos."""
        return list(self._agents_by_id.values())
