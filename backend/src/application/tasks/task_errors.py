"""Erros de aplicação do fluxo de tarefas."""

from __future__ import annotations

from src.domain.exceptions.domain_exceptions import DomainError


# Bloco: erro levantado quando a tarefa buscada não existe.
class TaskNotFoundError(DomainError):
    """Levantada quando a tarefa solicitada não é encontrada no repositório."""
