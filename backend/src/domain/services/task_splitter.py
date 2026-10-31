"""Serviço de domínio puro: divide uma tarefa em partes numeradas (ADR-049)."""

from __future__ import annotations

from src.domain.entities.task import Task
from src.domain.value_objects.identifiers import TaskId


def distribute_extra_parts(task_count: int, missing: int) -> list[int]:
    """Reparte ``missing`` partes extras da forma mais uniforme entre as tarefas."""
    if task_count == 0:
        return []
    base, rest = divmod(missing, task_count)
    return [base + (1 if i < rest else 0) for i in range(task_count)]


def split_task(task: Task, total: int, part_note: str) -> list[Task]:
    """Mantém ``task`` como parte 1 e cria as demais; ``part_note`` usa {index} e {total}."""
    if total <= 1:
        return [task]
    title, description = task.title, task.description
    parts = [task] + [
        Task(
            task_id=TaskId.generate(),
            title=title,
            description=description,
            priority=task.priority,
            goal_id=task.goal_id,
        )
        for _ in range(total - 1)
    ]
    for index, part in enumerate(parts, start=1):
        part.title = f"{title} ({index}/{total})"
        part.description = (
            f"{part_note.format(index=index, total=total, title=title)}\n{description}"
        )
    return parts
