"""Schemas Pydantic (DTOs) da API de tarefas (ver ADR-007)."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.entities.agent import Role
from src.domain.entities.task import Priority, Task, TaskStatus, TaskTransition


# Bloco: ator que executa a ação (até haver autenticação, informado no corpo).
class _ActorMixin(BaseModel):
    actor_id: UUID
    actor_role: Role


class CreateTaskRequest(_ActorMixin):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=8000)
    priority: Priority = Priority.MEDIUM


class AssignTaskRequest(_ActorMixin):
    agent_id: UUID


class CompleteTaskRequest(_ActorMixin):
    result: str = Field(..., min_length=1, max_length=8000)


class MoveTaskRequest(_ActorMixin):
    to_status: TaskStatus
    note: str = Field(default="", max_length=1000)


class TransitionResponse(BaseModel):
    from_status: TaskStatus | None
    to_status: TaskStatus
    actor_id: str
    actor_role: Role
    note: str

    @staticmethod
    def from_entity(transition: TaskTransition) -> TransitionResponse:
        """Converte o registro de histórico no DTO público."""
        return TransitionResponse(
            from_status=transition.from_status,
            to_status=transition.to_status,
            actor_id=str(transition.actor_id),
            actor_role=transition.actor_role,
            note=transition.note,
        )


class TaskResponse(BaseModel):
    task_id: str
    title: str
    description: str
    status: TaskStatus
    priority: Priority
    assigned_to: str | None
    result: str | None

    @staticmethod
    def from_entity(task: Task) -> TaskResponse:
        """Converte a entidade ``Task`` no DTO público."""
        return TaskResponse(
            task_id=str(task.task_id),
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            assigned_to=str(task.assigned_to) if task.assigned_to else None,
            result=task.result,
        )
