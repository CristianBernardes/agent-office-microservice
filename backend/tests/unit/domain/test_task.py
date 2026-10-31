"""Testes unitários da entidade de domínio ``Task``."""

from __future__ import annotations

import pytest

from src.domain.entities.task import Task, TaskStatus
from src.domain.exceptions.domain_exceptions import InvalidStateTransitionError
from src.domain.value_objects.identifiers import AgentId, TaskId

pytestmark = pytest.mark.unit


@pytest.fixture
def backlog_task() -> Task:
    """Tarefa de exemplo recém-criada, ainda no backlog."""
    return Task(
        task_id=TaskId.generate(),
        title="Implementar login",
        description="Implementar autenticação JWT na API.",
    )


class TestTaskLifecycle:
    def test_new_task_starts_in_backlog(self, backlog_task: Task) -> None:
        assert backlog_task.status == TaskStatus.BACKLOG

    def test_assign_moves_task_to_in_progress(self, backlog_task: Task) -> None:
        agent_id = AgentId.generate()
        backlog_task.assign(agent_id)
        assert backlog_task.status == TaskStatus.IN_PROGRESS
        assert backlog_task.assigned_to == agent_id

    def test_complete_sets_result_and_completed_at(self, backlog_task: Task) -> None:
        backlog_task.assign(AgentId.generate())
        backlog_task.complete("Login implementado com JWT.")
        assert backlog_task.status == TaskStatus.DONE
        assert backlog_task.result == "Login implementado com JWT."
        assert backlog_task.completed_at is not None

    def test_cannot_complete_a_task_still_in_backlog(self, backlog_task: Task) -> None:
        with pytest.raises(InvalidStateTransitionError):
            backlog_task.complete("Resultado inválido.")


class TestTaskTimestamps:
    def test_created_at_is_set_and_not_started(self, backlog_task: Task) -> None:
        assert backlog_task.created_at is not None
        assert backlog_task.started_at is None

    def test_first_entry_in_progress_sets_started_at_once(self, backlog_task: Task) -> None:
        backlog_task.move_to(TaskStatus.IN_PROGRESS)
        first = backlog_task.started_at
        assert first is not None
        backlog_task.move_to(TaskStatus.IN_REVIEW)
        backlog_task.move_to(TaskStatus.IN_PROGRESS)
        assert backlog_task.started_at == first

    def test_assign_sets_started_at(self, backlog_task: Task) -> None:
        backlog_task.assign(AgentId.generate())
        assert backlog_task.started_at is not None
