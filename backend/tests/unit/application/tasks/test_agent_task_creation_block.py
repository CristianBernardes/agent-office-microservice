from __future__ import annotations

import pytest

from src.application.settings.board_settings_use_cases import (
    AgentCreateTaskUseCase,
    GetBoardSettingsUseCase,
    TaskCreationBlockedError,
    UpdateBoardSettingsUseCase,
)
from src.application.tasks.task_use_cases import CreateTaskInput, CreateTaskUseCase
from src.domain.entities.agent import Role
from src.domain.entities.task import Priority, Task
from src.domain.value_objects.identifiers import AgentId
from src.infrastructure.persistence.in_memory_settings_repository import (
    InMemorySettingsRepository,
)


class _FakeCreate(CreateTaskUseCase):
    def __init__(self) -> None:
        self.calls = 0

    async def execute(self, data: CreateTaskInput) -> Task:
        self.calls += 1
        return Task(task_id=None, title=data.title, description="", priority=data.priority)  # type: ignore[arg-type]


def _input() -> CreateTaskInput:
    return CreateTaskInput("t", "d", Priority.MEDIUM, AgentId.generate(), Role.PRODUCT_OWNER)


@pytest.mark.asyncio
async def test_agents_can_create_tasks_by_default_and_when_blocked_it_raises() -> None:
    repo = InMemorySettingsRepository()
    inner = _FakeCreate()
    guard = AgentCreateTaskUseCase(inner, GetBoardSettingsUseCase(repo))

    await guard.execute(_input())
    assert inner.calls == 1

    await UpdateBoardSettingsUseCase(repo).set_agents_can_create_tasks(False)
    with pytest.raises(TaskCreationBlockedError):
        await guard.execute(_input())
    assert inner.calls == 1
