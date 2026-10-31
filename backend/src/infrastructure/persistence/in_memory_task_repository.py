"""Implementação em memória do ``ITaskRepository``."""

from __future__ import annotations

from src.domain.entities.task import Task
from src.domain.interfaces.task_repository import ITaskRepository
from src.domain.value_objects.identifiers import TaskId


# Bloco: repositório de tarefas baseado em dicionário em memória.
class InMemoryTaskRepository(ITaskRepository):
    def __init__(self) -> None:
        self._tasks_by_id: dict[TaskId, Task] = {}

    async def save(self, task: Task) -> None:
        """Persiste (cria ou atualiza) a tarefa em memória."""
        self._tasks_by_id[task.task_id] = task

    async def find_by_id(self, task_id: TaskId) -> Task | None:
        """Retorna a tarefa com o ID informado, ou ``None``."""
        return self._tasks_by_id.get(task_id)

    async def list_all(self) -> list[Task]:
        """Retorna todas as tarefas persistidas."""
        return list(self._tasks_by_id.values())
