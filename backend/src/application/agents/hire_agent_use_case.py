"""Caso de uso: contratar um novo agente para o time.

Orquestra a criação de uma entidade ``Agent`` e sua persistência através da porta
``IAgentRepository``, sem conhecer qual implementação concreta de repositório está
sendo usada (PostgreSQL, memória, etc.) — ver ADR-007.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.entities.agent import Agent, Personality, Role
from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.value_objects.identifiers import AgentId


# Bloco: dados de entrada do caso de uso, isolando o contrato de chamada da
# entidade de domínio em si — permite evoluir a entidade sem afetar quem chama o
# caso de uso.
@dataclass(frozen=True, slots=True)
class HireAgentInput:
    name: str
    role: Role
    personality: Personality
    llm_model: str


# Bloco: caso de uso de contratação de agente.
# Depende apenas da interface de repositório (Dependency Inversion Principle) —
# nunca de uma implementação concreta.
class HireAgentUseCase:
    def __init__(self, agent_repository: IAgentRepository) -> None:
        self._agent_repository = agent_repository

    async def execute(self, use_case_input: HireAgentInput) -> Agent:
        """Cria um novo agente com o papel e modelo informados, e o persiste."""
        agent = Agent(
            agent_id=AgentId.generate(),
            name=use_case_input.name,
            role=use_case_input.role,
            personality=use_case_input.personality,
            llm_model=use_case_input.llm_model,
        )
        await self._agent_repository.save(agent)
        return agent
