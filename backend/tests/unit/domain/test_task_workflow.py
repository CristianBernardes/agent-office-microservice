"""Testes da matriz papel × estágio das tarefas."""

import pytest

from src.domain.entities.agent import Role
from src.domain.entities.task import TaskStatus
from src.domain.policies.task_workflow import can_move, is_valid_move

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("role", "origin", "target", "expected"),
    [
        (Role.PRODUCT_OWNER, TaskStatus.BACKLOG, TaskStatus.TODO, True),
        (Role.DEV_JUNIOR, TaskStatus.BACKLOG, TaskStatus.TODO, False),
        (Role.DEV_SENIOR, TaskStatus.IN_PROGRESS, TaskStatus.IN_REVIEW, True),
        (Role.QA_ENGINEER, TaskStatus.IN_PROGRESS, TaskStatus.IN_REVIEW, False),
        (Role.QA_ENGINEER, TaskStatus.IN_REVIEW, TaskStatus.DONE, True),
        (Role.DEV_JUNIOR, TaskStatus.IN_REVIEW, TaskStatus.DONE, False),
        (Role.HR_MANAGER, TaskStatus.TODO, TaskStatus.BLOCKED, False),
        (Role.SCRUM_MASTER, TaskStatus.TODO, TaskStatus.BLOCKED, True),
    ],
)
def test_role_permissions(
    role: Role, origin: TaskStatus, target: TaskStatus, expected: bool
) -> None:
    assert can_move(role, origin, target) is expected


def test_done_is_terminal_and_skips_are_invalid() -> None:
    assert not is_valid_move(TaskStatus.DONE, TaskStatus.TODO)
    assert not is_valid_move(TaskStatus.BACKLOG, TaskStatus.DONE)
    assert is_valid_move(TaskStatus.BLOCKED, TaskStatus.TODO)
