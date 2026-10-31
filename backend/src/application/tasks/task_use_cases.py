"""Casos de uso de tarefas: criar, atribuir e concluir (ver ADR-016)."""

from __future__ import annotations

from dataclasses import dataclass

from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.common.message_envelope import build_message_envelope
from src.application.tasks.task_errors import TaskNotFoundError
from src.domain.entities.agent import Role
from src.domain.entities.task import Priority, Task, TaskStatus, TaskTransition
from src.domain.exceptions.domain_exceptions import (
    InvalidStateTransitionError,
    PermissionDeniedError,
)
from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.interfaces.message_bus import IMessageBus
from src.domain.interfaces.task_repository import ITaskRepository
from src.domain.policies.task_workflow import can_assign, can_complete, can_move, is_valid_move
from src.domain.value_objects.identifiers import AgentId, GoalId, TaskId

# Bloco: tópico de notificação de atualização de tarefa, conforme a RFC-001.
_TASK_UPDATED_TOPIC = "office/tasks/updated"


# Bloco: publicação compartilhada do evento de tarefa atualizada (DRY).
async def _publish_task_updated(
    message_bus: IMessageBus, task: Task, actor_id: AgentId, actor_role: Role
) -> None:
    envelope = build_message_envelope(
        agent_id=str(actor_id),
        agent_role=actor_role.value,
        payload={
            "task_id": str(task.task_id),
            "title": task.title,
            "status": task.status.value,
            "assigned_to": str(task.assigned_to) if task.assigned_to else None,
        },
    )
    await message_bus.publish(_TASK_UPDATED_TOPIC, envelope, qos=1)


# Bloco: registro do histórico de movimentos (DRY entre todos os casos de uso).
async def _record_transition(
    repository: ITaskRepository,
    task: Task,
    from_status: TaskStatus | None,
    actor_id: AgentId,
    actor_role: Role,
    note: str = "",
) -> None:
    await repository.add_transition(
        TaskTransition(task.task_id, from_status, task.status, actor_id, actor_role, note)
    )


# Bloco: entrada de criação de tarefa.
@dataclass(frozen=True, slots=True)
class CreateTaskInput:
    title: str
    description: str
    priority: Priority
    creator_id: AgentId
    creator_role: Role
    goal_id: GoalId | None = None


# Bloco: caso de uso de criação de tarefa (nasce no backlog).
class CreateTaskUseCase:
    def __init__(self, task_repository: ITaskRepository, message_bus: IMessageBus) -> None:
        self._task_repository = task_repository
        self._message_bus = message_bus

    async def execute(self, data: CreateTaskInput) -> Task:
        task = Task(
            task_id=TaskId.generate(),
            title=data.title,
            description=data.description,
            priority=data.priority,
            goal_id=data.goal_id,
        )
        await self._task_repository.save(task)
        await _record_transition(
            self._task_repository, task, None, data.creator_id, data.creator_role
        )
        await _publish_task_updated(self._message_bus, task, data.creator_id, data.creator_role)
        return task


# Bloco: caso de uso de atribuição de tarefa a um agente.
class AssignTaskUseCase:
    def __init__(
        self,
        task_repository: ITaskRepository,
        agent_repository: IAgentRepository,
        message_bus: IMessageBus,
    ) -> None:
        self._task_repository = task_repository
        self._agent_repository = agent_repository
        self._message_bus = message_bus

    async def execute(
        self, task_id: TaskId, assignee_id: AgentId, actor_id: AgentId, actor_role: Role
    ) -> Task:
        if not can_assign(actor_role):
            raise PermissionDeniedError("task.assign_forbidden", role=actor_role.value)
        task = await self._task_repository.find_by_id(task_id)
        if task is None:
            raise TaskNotFoundError("task.not_found", task_id=task_id)
        agent = await self._agent_repository.find_by_id(assignee_id)
        if agent is None:
            raise AgentNotFoundError("agent.not_found", agent_id=assignee_id)

        # Valida o agente primeiro: se ele estiver ocupado, a tarefa não muda.
        previous = task.status
        agent.assign_task(task.task_id)
        task.assign(assignee_id)
        await self._agent_repository.save(agent)
        await self._task_repository.save(task)
        await _record_transition(
            self._task_repository, task, previous, actor_id, actor_role, f"assigned:{assignee_id}"
        )
        await _publish_task_updated(self._message_bus, task, actor_id, actor_role)
        return task


# Bloco: caso de uso de conclusão de tarefa; devolve o agente a IDLE.
class CompleteTaskUseCase:
    def __init__(
        self,
        task_repository: ITaskRepository,
        agent_repository: IAgentRepository,
        message_bus: IMessageBus,
    ) -> None:
        self._task_repository = task_repository
        self._agent_repository = agent_repository
        self._message_bus = message_bus

    async def execute(
        self, task_id: TaskId, result: str, actor_id: AgentId, actor_role: Role
    ) -> Task:
        if not can_complete(actor_role):
            raise PermissionDeniedError("task.complete_forbidden", role=actor_role.value)
        task = await self._task_repository.find_by_id(task_id)
        if task is None:
            raise TaskNotFoundError("task.not_found", task_id=task_id)

        previous = task.status
        task.complete(result)
        await self._task_repository.save(task)
        await _record_transition(self._task_repository, task, previous, actor_id, actor_role)

        if task.assigned_to is not None:
            agent = await self._agent_repository.find_by_id(task.assigned_to)
            if agent is not None and agent.current_task_id == task.task_id:
                agent.complete_task()
                await self._agent_repository.save(agent)

        await _publish_task_updated(self._message_bus, task, actor_id, actor_role)
        return task


# Bloco: caso de uso de movimento de cartão, regido pela matriz papel × estágio.
class MoveTaskUseCase:
    def __init__(self, task_repository: ITaskRepository, message_bus: IMessageBus) -> None:
        self._task_repository = task_repository
        self._message_bus = message_bus

    async def execute(
        self,
        task_id: TaskId,
        target: TaskStatus,
        actor_id: AgentId,
        actor_role: Role,
        note: str = "",
    ) -> Task:
        task = await self._task_repository.find_by_id(task_id)
        if task is None:
            raise TaskNotFoundError("task.not_found", task_id=task_id)
        previous = task.status
        params = {"title": task.title, "from_status": previous.value, "to_status": target.value}
        if not is_valid_move(previous, target):
            raise InvalidStateTransitionError("task.invalid_move", **params)
        if not can_move(actor_role, previous, target):
            raise PermissionDeniedError("task.move_forbidden", role=actor_role.value, **params)

        task.move_to(target)
        await self._task_repository.save(task)
        await _record_transition(self._task_repository, task, previous, actor_id, actor_role, note)
        await _publish_task_updated(self._message_bus, task, actor_id, actor_role)
        return task
