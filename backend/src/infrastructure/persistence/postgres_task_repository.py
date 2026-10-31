"""Implementação PostgreSQL do ``ITaskRepository`` (ver ADR-016)."""

from __future__ import annotations

from uuid import UUID

import asyncpg

from src.domain.entities.task import Priority, Task, TaskStatus
from src.domain.interfaces.task_repository import ITaskRepository
from src.domain.value_objects.identifiers import AgentId, TaskId

_UPSERT_SQL = """
INSERT INTO tasks (task_id, title, description, status, priority, assigned_to,
                   result, completed_at)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
ON CONFLICT (task_id) DO UPDATE SET
    title = EXCLUDED.title, description = EXCLUDED.description, status = EXCLUDED.status,
    priority = EXCLUDED.priority, assigned_to = EXCLUDED.assigned_to,
    result = EXCLUDED.result, completed_at = EXCLUDED.completed_at
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
        )

    async def find_by_id(self, task_id: TaskId) -> Task | None:
        """Retorna a tarefa com o ID informado, ou ``None``."""
        row = await self._pool.fetchrow("SELECT * FROM tasks WHERE task_id = $1", task_id.value)
        return None if row is None else _to_task(row)

    async def list_all(self) -> list[Task]:
        """Retorna todas as tarefas, da mais antiga para a mais nova."""
        rows = await self._pool.fetch("SELECT * FROM tasks ORDER BY created_at")
        return [_to_task(row) for row in rows]


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
    )
