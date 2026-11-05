"""Testes do parser da resposta do RH sobre qual cargo contratar."""

from __future__ import annotations

import pytest

from src.application.autonomy.work_loop_use_case import _parse_hiring_answer
from src.domain.entities.agent import Role
from src.domain.entities.task import Task
from src.domain.services.task_routing import is_hiring_task
from src.domain.value_objects.identifiers import TaskId

pytestmark = pytest.mark.unit


def _task(title: str, description: str) -> Task:
    return Task(task_id=TaskId.generate(), title=title, description=description)


class TestParseHiringAnswer:
    def test_extracts_role_and_reason(self) -> None:
        assert _parse_hiring_answer("dev_mid | Precisamos de mais braços") == (
            Role.DEV_MID,
            "Precisamos de mais braços",
        )

    def test_does_not_confuse_similar_roles(self) -> None:
        parsed = _parse_hiring_answer("data_engineer | pipelines")
        assert parsed is not None and parsed[0] == Role.DATA_ENGINEER

    def test_returns_none_without_a_valid_role(self) -> None:
        assert _parse_hiring_answer("contratar alguém bom") is None


class TestIsHiringTask:
    def test_detects_portuguese_and_english(self) -> None:
        assert is_hiring_task(_task("Contratar um DBA", "")) is True
        assert is_hiring_task(_task("Hire a designer", "")) is True
        assert is_hiring_task(_task("Implementar API", "")) is False
