"""Implementação em memória do ``ITaskRepository``."""

from __future__ import annotations

from src.domain.entities.task import Task, TaskTransition
from src.domain.interfaces.task_repository import ITaskRepository
from src.domain.value_objects.identifiers import TaskId


# Bloco: repositório de tarefas baseado em dicionário em memória.
class InMemoryTaskRepository(ITaskRepository):
    def __init__(self) -> None:
        self._tasks_by_id: dict[TaskId, Task] = {}
        self._transitions: list[TaskTransition] = []

    async def save(self, task: Task) -> None:
        """Persiste (cria ou atualiza) a tarefa em memória."""
        self._tasks_by_id[task.task_id] = task

    async def find_by_id(self, task_id: TaskId) -> Task | None:
        """Retorna a tarefa com o ID informado, ou ``None``."""
        return self._tasks_by_id.get(task_id)

    async def list_all(self) -> list[Task]:
        """Retorna todas as tarefas persistidas."""
        return list(self._tasks_by_id.values())

    async def delete(self, task_id: TaskId) -> None:
        """Remove a tarefa e seu histórico."""
        self._tasks_by_id.pop(task_id, None)
        self._transitions = [t for t in self._transitions if t.task_id != task_id]

    async def add_transition(self, transition: TaskTransition) -> None:
        """Acrescenta o movimento ao histórico em memória."""
        self._transitions.append(transition)

    async def list_transitions(self, task_id: TaskId) -> list[TaskTransition]:
        """Movimentos da tarefa, na ordem em que ocorreram."""
        return [t for t in self._transitions if t.task_id == task_id]
