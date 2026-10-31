"""Contrato (porta) para persistência de tarefas (ver ADR-016)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.task import Task
from src.domain.value_objects.identifiers import TaskId


# Bloco: contrato único de persistência de tarefas.
class ITaskRepository(ABC):
    @abstractmethod
    async def save(self, task: Task) -> None:
        """Persiste uma tarefa (criação ou atualização)."""

    @abstractmethod
    async def find_by_id(self, task_id: TaskId) -> Task | None:
        """Busca uma tarefa pelo identificador, ou ``None`` se não existir."""

    @abstractmethod
    async def list_all(self) -> list[Task]:
        """Lista todas as tarefas persistidas."""
