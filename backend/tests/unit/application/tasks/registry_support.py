"""Apoio de testes: casos de uso de tarefas para montar o ``ToolRegistry``."""

from __future__ import annotations

from typing import Any

from src.application.chat.chat_use_cases import SendMessageUseCase
from src.application.tasks.task_use_cases import (
    AssignTaskUseCase,
    CompleteTaskUseCase,
    CreateTaskUseCase,
)
from src.infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from src.infrastructure.persistence.in_memory_agent_repository import InMemoryAgentRepository
from src.infrastructure.persistence.in_memory_chat_repository import InMemoryChatRepository
from src.infrastructure.persistence.in_memory_task_repository import InMemoryTaskRepository


def task_use_cases(
    bus: InMemoryMessageBus,
    tasks: InMemoryTaskRepository | None = None,
    agents: InMemoryAgentRepository | None = None,
    chat: InMemoryChatRepository | None = None,
) -> dict[str, Any]:
    tasks = tasks or InMemoryTaskRepository()
    agents = agents or InMemoryAgentRepository()
    chat = chat or InMemoryChatRepository()
    return {
        "create_task_use_case": CreateTaskUseCase(tasks, bus),
        "assign_task_use_case": AssignTaskUseCase(tasks, agents, bus),
        "complete_task_use_case": CompleteTaskUseCase(tasks, agents, bus),
        "send_message_use_case": SendMessageUseCase(chat, agents, bus),
    }
