"""Configurações do quadro: bloqueio de criação de tarefas pelos agentes."""

from __future__ import annotations

from src.application.tasks.task_use_cases import CreateTaskInput, CreateTaskUseCase
from src.domain.entities.task import Task
from src.domain.exceptions.domain_exceptions import PermissionDeniedError
from src.domain.interfaces.settings_repository import ISettingsRepository

AGENTS_CAN_CREATE_TASKS_KEY = "agents_can_create_tasks"


class TaskCreationBlockedError(PermissionDeniedError):
    """Levantada quando um agente tenta criar tarefa com o bloqueio ativo."""


class GetBoardSettingsUseCase:
    def __init__(self, repository: ISettingsRepository) -> None:
        self._repository = repository

    async def agents_can_create_tasks(self) -> bool:
        return await self._repository.get_flag(AGENTS_CAN_CREATE_TASKS_KEY, True)


class UpdateBoardSettingsUseCase:
    def __init__(self, repository: ISettingsRepository) -> None:
        self._repository = repository

    async def set_agents_can_create_tasks(self, value: bool) -> None:
        await self._repository.set_flag(AGENTS_CAN_CREATE_TASKS_KEY, value)


# Bloco: criação de tarefa usada pelos agentes (ferramenta e reunião); a API humana não passa aqui.
class AgentCreateTaskUseCase(CreateTaskUseCase):
    def __init__(self, inner: CreateTaskUseCase, settings: GetBoardSettingsUseCase) -> None:
        self._inner = inner
        self._settings = settings

    async def execute(self, data: CreateTaskInput) -> Task:
        if not await self._settings.agents_can_create_tasks():
            raise TaskCreationBlockedError("task.creation_blocked", role=data.creator_role.value)
        return await self._inner.execute(data)
