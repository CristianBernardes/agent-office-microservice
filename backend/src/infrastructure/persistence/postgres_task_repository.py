"""Implementação PostgreSQL do ``ITaskRepository`` (ver ADR-016)."""

from __future__ import annotations

from uuid import UUID

import asyncpg

from src.domain.entities.agent import Role
from src.domain.entities.task import Priority, Task, TaskStatus, TaskTransition
from src.domain.interfaces.task_repository import ITaskRepository
from src.domain.value_objects.identifiers import AgentId, GoalId, TaskId

_UPSERT_SQL = """
INSERT INTO tasks (task_id, title, description, status, priority, assigned_to,
                   result, completed_at, goal_id, reviewer_id)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
ON CONFLICT (task_id) DO UPDATE SET
    title = EXCLUDED.title, description = EXCLUDED.description, status = EXCLUDED.status,
    priority = EXCLUDED.priority, assigned_to = EXCLUDED.assigned_to,
    result = EXCLUDED.result, completed_at = EXCLUDED.completed_at,
    goal_id = EXCLUDED.goal_id, reviewer_id = EXCLUDED.reviewer_id
"""

# actor_id desconhecido vira NULL (a FK permite) para nunca perder o histórico.
_TRANSITION_SQL = """
INSERT INTO task_transitions (task_id, from_status, to_status, actor_id, actor_role, note,
                              created_at)
VALUES ($1, $2, $3, (SELECT agent_id FROM agents WHERE agent_id = $4), $5, $6, $7)
"""


# Bloco: repositório de tarefas sobre uma pool asyncpg injetada.
class PostgresTaskRepository(ITaskRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def save(self, task: Task) -> None:
        """Insere ou atualiza a tarefa (upsert)."""
        await self._pool.execute(
            _UPSERT_SQL,
            task.task_id.value,
            task.title,
            task.description,
            task.status.value,
            task.priority.value,
            task.assigned_to.value if task.assigned_to else None,
            task.result,
            task.completed_at,
            task.goal_id.value if task.goal_id else None,
            task.reviewer_id.value if task.reviewer_id else None,
        )

    async def find_by_id(self, task_id: TaskId) -> Task | None:
        """Retorna a tarefa com o ID informado, ou ``None``."""
        row = await self._pool.fetchrow("SELECT * FROM tasks WHERE task_id = $1", task_id.value)
        return None if row is None else _to_task(row)

    async def list_all(self) -> list[Task]:
        """Retorna todas as tarefas, da mais antiga para a mais nova."""
        rows = await self._pool.fetch("SELECT * FROM tasks ORDER BY created_at")
        return [_to_task(row) for row in rows]

    async def add_transition(self, transition: TaskTransition) -> None:
        """Grava o movimento em ``task_transitions``."""
        await self._pool.execute(
            _TRANSITION_SQL,
            transition.task_id.value,
            transition.from_status.value if transition.from_status else None,
            transition.to_status.value,
            transition.actor_id.value,
            transition.actor_role.value,
            transition.note,
            transition.created_at,
        )

    async def list_transitions(self, task_id: TaskId) -> list[TaskTransition]:
        """Histórico da tarefa, do mais antigo ao mais novo."""
        rows = await self._pool.fetch(
            "SELECT * FROM task_transitions WHERE task_id = $1 ORDER BY created_at",
            task_id.value,
        )
        return [_to_transition(row) for row in rows]


def _to_transition(row: asyncpg.Record) -> TaskTransition:
    actor: UUID | None = row["actor_id"]
    origin: str | None = row["from_status"]
    return TaskTransition(
        task_id=TaskId(value=row["task_id"]),
        from_status=None if origin is None else TaskStatus(origin),
        to_status=TaskStatus(row["to_status"]),
        actor_id=AgentId(value=actor) if actor else AgentId(value=UUID(int=0)),
        actor_role=Role(row["actor_role"]),
        note=row["note"] or "",
        created_at=row["created_at"],
    )


def _to_task(row: asyncpg.Record) -> Task:
    assigned: UUID | None = row["assigned_to"]
    return Task(
        task_id=TaskId(value=row["task_id"]),
        title=row["title"],
        description=row["description"],
        status=TaskStatus(row["status"]),
        priority=Priority(row["priority"]),
        assigned_to=None if assigned is None else AgentId(value=assigned),
        result=row["result"],
        completed_at=row["completed_at"],
        goal_id=None if row["goal_id"] is None else GoalId(value=row["goal_id"]),
        reviewer_id=None if row["reviewer_id"] is None else AgentId(value=row["reviewer_id"]),
    )
