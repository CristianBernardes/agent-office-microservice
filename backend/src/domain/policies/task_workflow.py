"""Política de domínio: quem pode mover uma tarefa entre estágios (ADR-016, adendo)."""

from __future__ import annotations

from src.domain.entities.agent import Role
from src.domain.entities.task import TaskStatus

_DEVS = frozenset({Role.DEV_SENIOR, Role.DEV_JUNIOR, Role.TECH_LEAD})
_COORDINATORS = frozenset({Role.SCRUM_MASTER, Role.TECH_LEAD, Role.PRODUCT_OWNER})
_PLANNERS = frozenset({Role.PRODUCT_OWNER, Role.SCRUM_MASTER})
_REVIEWERS = frozenset({Role.QA_ENGINEER, Role.TECH_LEAD})

# Bloco: matriz (estágio atual, novo estágio) → papéis autorizados.
_ALLOWED_MOVES: dict[tuple[TaskStatus, TaskStatus], frozenset[Role]] = {
    (TaskStatus.BACKLOG, TaskStatus.TODO): _PLANNERS,
    (TaskStatus.TODO, TaskStatus.IN_PROGRESS): _DEVS,
    (TaskStatus.IN_PROGRESS, TaskStatus.IN_REVIEW): _DEVS,
    (TaskStatus.IN_REVIEW, TaskStatus.DONE): _REVIEWERS | {Role.PRODUCT_OWNER},
    (TaskStatus.IN_REVIEW, TaskStatus.IN_PROGRESS): _REVIEWERS,
    (TaskStatus.BLOCKED, TaskStatus.TODO): _PLANNERS,
    **{
        (stage, TaskStatus.BLOCKED): _COORDINATORS
        for stage in (TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.IN_REVIEW)
    },
}


def is_valid_move(current: TaskStatus, target: TaskStatus) -> bool:
    """Indica se o movimento existe na matriz (independente do papel)."""
    return (current, target) in _ALLOWED_MOVES


def can_move(role: Role, current: TaskStatus, target: TaskStatus) -> bool:
    """Indica se o papel pode executar o movimento."""
    return role in _ALLOWED_MOVES.get((current, target), frozenset())


def can_assign(role: Role) -> bool:
    """Apenas coordenadores distribuem trabalho."""
    return role in _COORDINATORS


def can_complete(role: Role) -> bool:
    """Quem executa ou revisa pode concluir uma tarefa."""
    return role in _DEVS | _REVIEWERS
