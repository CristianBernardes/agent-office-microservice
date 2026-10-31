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


def parse_subtasks(text: str, limit: int) -> list[tuple[str, str]]:
    """Extrai linhas ``título | entregável`` de uma resposta do LLM, sem títulos repetidos."""
    found: list[tuple[str, str]] = []
    seen: set[str] = set()
    for line in text.splitlines():
        title, _, deliverable = line.strip().lstrip("-*•0123456789.) ").partition("|")
        title = title.strip().strip("*").strip()
        key = title.casefold()
        if not title or not deliverable.strip() or key in seen:
            continue
        seen.add(key)
        found.append((title, deliverable.strip()))
    return found[:limit]


def split_task(
    task: Task,
    total: int,
    part_note: str,
    subtasks: list[tuple[str, str]] | None = None,
) -> list[Task]:
    """Divide ``task`` em ``total`` partes; usa ``subtasks`` distintas quando houver o bastante.

    Sem subtarefas suficientes, mantém ``task`` como parte 1 e numera as demais;
    ``part_note`` usa {index} e {total}.
    """
    if total <= 1:
        return [task]
    if subtasks is not None and len(subtasks) >= total:
        return _split_by_subtasks(task, subtasks[:total])
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


def _split_by_subtasks(task: Task, subtasks: list[tuple[str, str]]) -> list[Task]:
    parts = [task] + [
        Task(
            task_id=TaskId.generate(),
            title=task.title,
            description=task.description,
            priority=task.priority,
            goal_id=task.goal_id,
        )
        for _ in subtasks[1:]
    ]
    for part, (title, deliverable) in zip(parts, subtasks, strict=True):
        part.title = title
        part.description = deliverable
    return parts
