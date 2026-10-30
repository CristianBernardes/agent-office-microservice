"""Entidade de domínio ``Task`` e os tipos que a compõem.

Representa uma unidade de trabalho que pode ser criada por qualquer agente,
atribuída a um agente específico e concluída com um resultado textual.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

from src.domain.exceptions.domain_exceptions import InvalidStateTransitionError
from src.domain.value_objects.identifiers import AgentId, TaskId


# Bloco: estados do ciclo de vida de uma tarefa.
class TaskStatus(str, Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    BLOCKED = "blocked"


# Bloco: prioridade de negócio de uma tarefa.
class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Bloco: entidade de domínio ``Task``.
# Controla as transições válidas de estado (atribuição e conclusão), garantindo que
# uma tarefa não seja concluída sem antes ter sido atribuída a um agente.
@dataclass(slots=True)
class Task:
    task_id: TaskId
    title: str
    description: str
    status: TaskStatus = field(default=TaskStatus.BACKLOG)
    priority: Priority = field(default=Priority.MEDIUM)
    assigned_to: AgentId | None = field(default=None)
    result: str | None = field(default=None)
    completed_at: datetime | None = field(default=None)

    def assign(self, agent_id: AgentId) -> None:
        """Atribui a tarefa a um agente, movendo-a para ``IN_PROGRESS``."""
        self.assigned_to = agent_id
        self.status = TaskStatus.IN_PROGRESS

    def complete(self, result: str) -> None:
        """Conclui a tarefa com um resultado textual.

        Só é permitido concluir uma tarefa que esteja ``IN_PROGRESS`` — uma tarefa
        no backlog, por exemplo, não tem um agente trabalhando nela e não pode ser
        considerada concluída.
        """
        if self.status != TaskStatus.IN_PROGRESS:
            raise InvalidStateTransitionError(
                f"Tarefa '{self.title}' está '{self.status.value}' e não pode ser "
                "concluída — apenas tarefas 'in_progress' podem ser concluídas."
            )
        self.result = result
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now(UTC)
