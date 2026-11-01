"""Rotas HTTP de tarefas (Kanban). Camada fina: sem regra de negócio (ADR-007, ADR-016)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.tasks.task_errors import TaskNotFoundError
from src.application.tasks.task_use_cases import (
    AssignTaskUseCase,
    CompleteTaskUseCase,
    CreateTaskInput,
    CreateTaskUseCase,
    MoveTaskUseCase,
    SetTaskOwnerUseCase,
    SetTaskPriorityUseCase,
)
from src.domain.exceptions.domain_exceptions import (
    InvalidStateTransitionError,
    PermissionDeniedError,
)
from src.domain.interfaces.task_repository import ITaskRepository
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import AgentId, TaskId
from src.presentation.api.agents_router import get_request_language
from src.presentation.api.task_schemas import (
    AssignTaskRequest,
    CompleteTaskRequest,
    CreateTaskRequest,
    MoveTaskRequest,
    SetTaskOwnerRequest,
    SetTaskPriorityRequest,
    TaskResponse,
    TransitionResponse,
)
from src.presentation.dependencies import (
    get_assign_task_use_case,
    get_complete_task_use_case,
    get_create_task_use_case,
    get_move_task_use_case,
    get_set_task_owner_use_case,
    get_set_task_priority_use_case,
    get_task_repository,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


# Bloco: traduz erros de negócio em HTTP localizado (404 inexistente, 409 transição inválida).
def _http_error(error: Exception, language: Language) -> HTTPException:
    if isinstance(error, TaskNotFoundError | AgentNotFoundError):
        return HTTPException(status.HTTP_404_NOT_FOUND, error.localized(language))
    if isinstance(error, PermissionDeniedError):
        return HTTPException(status.HTTP_403_FORBIDDEN, error.localized(language))
    assert isinstance(error, InvalidStateTransitionError)
    return HTTPException(status.HTTP_409_CONFLICT, error.localized(language))


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    repository: ITaskRepository = Depends(get_task_repository),
) -> list[TaskResponse]:
    """Lista todas as tarefas."""
    return [TaskResponse.from_entity(task) for task in await repository.list_all()]


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    body: CreateTaskRequest,
    use_case: CreateTaskUseCase = Depends(get_create_task_use_case),
) -> TaskResponse:
    """Cria uma tarefa no backlog."""
    task = await use_case.execute(
        CreateTaskInput(
            title=body.title,
            description=body.description,
            priority=body.priority,
            creator_id=AgentId(value=body.actor_id),
            creator_role=body.actor_role,
        )
    )
    return TaskResponse.from_entity(task)


@router.post("/{task_id}/assign", response_model=TaskResponse)
async def assign_task(
    task_id: UUID,
    body: AssignTaskRequest,
    use_case: AssignTaskUseCase = Depends(get_assign_task_use_case),
    language: Language = Depends(get_request_language),
) -> TaskResponse:
    """Atribui a tarefa a um agente (404 inexistente, 409 agente ocupado)."""
    try:
        task = await use_case.execute(
            TaskId(value=task_id),
            AgentId(value=body.agent_id),
            AgentId(value=body.actor_id),
            body.actor_role,
        )
    except (
        TaskNotFoundError,
        AgentNotFoundError,
        InvalidStateTransitionError,
        PermissionDeniedError,
    ) as error:
        raise _http_error(error, language) from error
    return TaskResponse.from_entity(task)


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: UUID,
    body: CompleteTaskRequest,
    use_case: CompleteTaskUseCase = Depends(get_complete_task_use_case),
    language: Language = Depends(get_request_language),
) -> TaskResponse:
    """Conclui a tarefa (404 inexistente, 409 se não estiver em andamento)."""
    try:
        task = await use_case.execute(
            TaskId(value=task_id), body.result, AgentId(value=body.actor_id), body.actor_role
        )
    except (TaskNotFoundError, InvalidStateTransitionError, PermissionDeniedError) as error:
        raise _http_error(error, language) from error
    return TaskResponse.from_entity(task)


@router.post("/{task_id}/move", response_model=TaskResponse)
async def move_task(
    task_id: UUID,
    body: MoveTaskRequest,
    use_case: MoveTaskUseCase = Depends(get_move_task_use_case),
    language: Language = Depends(get_request_language),
) -> TaskResponse:
    """Move o cartão de estágio (404 inexistente, 409 inválido, 403 sem permissão)."""
    try:
        task = await use_case.execute(
            TaskId(value=task_id),
            body.to_status,
            AgentId(value=body.actor_id),
            body.actor_role,
            body.note,
            body.owner_override,
        )
    except (TaskNotFoundError, InvalidStateTransitionError, PermissionDeniedError) as error:
        raise _http_error(error, language) from error
    return TaskResponse.from_entity(task)


@router.get("/{task_id}/transitions", response_model=list[TransitionResponse])
async def list_transitions(
    task_id: UUID,
    repository: ITaskRepository = Depends(get_task_repository),
) -> list[TransitionResponse]:
    """Histórico de movimentos do cartão."""
    history = await repository.list_transitions(TaskId(value=task_id))
    return [TransitionResponse.from_entity(item) for item in history]


@router.put("/{task_id}/owner", response_model=TaskResponse)
async def set_task_owner(
    task_id: UUID,
    body: SetTaskOwnerRequest,
    use_case: SetTaskOwnerUseCase = Depends(get_set_task_owner_use_case),
    language: Language = Depends(get_request_language),
) -> TaskResponse:
    """Define o responsável sem mudar o estágio (404 inexistente, 409 agente offline)."""
    try:
        task = await use_case.execute(
            TaskId(value=task_id),
            AgentId(value=body.agent_id),
            AgentId(value=body.actor_id),
            body.actor_role,
        )
    except (TaskNotFoundError, AgentNotFoundError, InvalidStateTransitionError) as error:
        raise _http_error(error, language) from error
    return TaskResponse.from_entity(task)


@router.put("/{task_id}/priority", response_model=TaskResponse)
async def set_task_priority(
    task_id: UUID,
    body: SetTaskPriorityRequest,
    use_case: SetTaskPriorityUseCase = Depends(get_set_task_priority_use_case),
    language: Language = Depends(get_request_language),
) -> TaskResponse:
    """Redefine a prioridade da tarefa (404 se inexistente)."""
    try:
        task = await use_case.execute(
            TaskId(value=task_id), body.priority, AgentId(value=body.actor_id), body.actor_role
        )
    except TaskNotFoundError as error:
        raise _http_error(error, language) from error
    return TaskResponse.from_entity(task)
