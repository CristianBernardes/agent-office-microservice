"""Contrato (porta) para persistência de agentes.

Mantida pequena e focada no que a aplicação efetivamente precisa nesta fase do
projeto (buscar, salvar e listar), evitando antecipar operações sem um caso de uso
real que as consuma (princípio YAGNI).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.agent import Agent
from src.domain.value_objects.identifiers import AgentId


# Bloco: contrato único de persistência de agentes.
class IAgentRepository(ABC):
    @abstractmethod
    async def save(self, agent: Agent) -> None:
        """Persiste um agente (criação ou atualização)."""

    @abstractmethod
    async def find_by_id(self, agent_id: AgentId) -> Agent | None:
        """Busca um agente pelo seu identificador, ou ``None`` se não existir."""

    @abstractmethod
    async def list_all(self) -> list[Agent]:
        """Lista todos os agentes atualmente persistidos."""
