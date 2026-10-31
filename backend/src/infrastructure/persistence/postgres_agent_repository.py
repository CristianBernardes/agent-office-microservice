"""Implementação PostgreSQL do ``IAgentRepository`` (ver ADR-014)."""

from __future__ import annotations

from uuid import UUID

import asyncpg

from src.domain.entities.agent import Agent, AgentStatus, Personality, Role
from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.value_objects.identifiers import AgentId, TaskId

_UPSERT_SQL = """
INSERT INTO agents (agent_id, name, role, llm_model, status, current_task_id,
                    openness, conscientiousness, extraversion, agreeableness, neuroticism)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
ON CONFLICT (agent_id) DO UPDATE SET
    name = EXCLUDED.name, role = EXCLUDED.role, llm_model = EXCLUDED.llm_model,
    status = EXCLUDED.status, current_task_id = EXCLUDED.current_task_id,
    openness = EXCLUDED.openness, conscientiousness = EXCLUDED.conscientiousness,
    extraversion = EXCLUDED.extraversion, agreeableness = EXCLUDED.agreeableness,
    neuroticism = EXCLUDED.neuroticism
"""


# Bloco: repositório de agentes sobre uma pool asyncpg injetada.
class PostgresAgentRepository(IAgentRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def save(self, agent: Agent) -> None:
        """Insere ou atualiza o agente (upsert)."""
        personality = agent.personality
        task_id = agent.current_task_id.value if agent.current_task_id else None
        await self._pool.execute(
            _UPSERT_SQL,
            agent.agent_id.value,
            agent.name,
            agent.role.value,
            agent.llm_model,
            agent.status.value,
            task_id,
            personality.openness,
            personality.conscientiousness,
            personality.extraversion,
            personality.agreeableness,
            personality.neuroticism,
        )

    async def find_by_id(self, agent_id: AgentId) -> Agent | None:
        """Retorna o agente com o ID informado, ou ``None``."""
        row = await self._pool.fetchrow("SELECT * FROM agents WHERE agent_id = $1", agent_id.value)
        return None if row is None else _to_agent(row)

    async def list_all(self) -> list[Agent]:
        """Retorna todos os agentes, ordenados por nome."""
        rows = await self._pool.fetch("SELECT * FROM agents ORDER BY name")
        return [_to_agent(row) for row in rows]


def _to_agent(row: asyncpg.Record) -> Agent:
    task_id: UUID | None = row["current_task_id"]
    return Agent(
        agent_id=AgentId(value=row["agent_id"]),
        name=row["name"],
        role=Role(row["role"]),
        personality=Personality(
            openness=row["openness"],
            conscientiousness=row["conscientiousness"],
            extraversion=row["extraversion"],
            agreeableness=row["agreeableness"],
            neuroticism=row["neuroticism"],
        ),
        llm_model=row["llm_model"],
        status=AgentStatus(row["status"]),
        current_task_id=None if task_id is None else TaskId(value=task_id),
    )
