import pytest

from src.domain.entities.task import Task
from src.domain.services.task_splitter import distribute_extra_parts, split_task
from src.domain.value_objects.identifiers import TaskId

pytestmark = pytest.mark.unit


def _task() -> Task:
    return Task(task_id=TaskId.generate(), title="T", description="D")


def test_distribute_is_uniform() -> None:
    assert distribute_extra_parts(2, 3) == [2, 1]
    assert distribute_extra_parts(0, 3) == []
    assert distribute_extra_parts(3, 0) == [0, 0, 0]


def test_split_keeps_original_as_first_part() -> None:
    task = _task()
    parts = split_task(task, 3, "Part {index}/{total} {title}")
    assert parts[0] is task
    assert [p.title for p in parts] == ["T (1/3)", "T (2/3)", "T (3/3)"]
    assert len({p.task_id for p in parts}) == 3
    assert parts[1].description.startswith("Part 2/3 T")


def test_split_into_one_returns_task_untouched() -> None:
    task = _task()
    assert split_task(task, 1, "x") == [task]
    assert task.title == "T"
