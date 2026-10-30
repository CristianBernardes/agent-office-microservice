"""Exceções de domínio do AgentOffice.

Todas as exceções levantadas pelas entidades e value objects do domínio herdam de
``DomainError``, permitindo que camadas superiores (aplicação, apresentação) capturem
e tratem erros de negócio de forma uniforme, sem depender de exceções genéricas do
Python (``ValueError``, ``RuntimeError``) que poderiam se confundir com bugs de
infraestrutura.
"""

from __future__ import annotations


# Bloco: exceção-base de domínio.
# Serve como ponto único de captura para qualquer violação de regra de negócio,
# diferenciando erros esperados (regra violada) de erros inesperados (bug).
class DomainError(Exception):
    """Erro base para qualquer violação de invariante do domínio."""


# Bloco: violação de transição de estado de uma entidade.
# Usada quando uma entidade recebe um comando que não é válido para o seu estado
# atual (ex.: atribuir uma tarefa a um agente que já está ocupado).
class InvalidStateTransitionError(DomainError):
    """Levantada quando uma transição de estado solicitada não é permitida."""


# Bloco: violação de invariante de valor.
# Usada por value objects quando um valor recebido não satisfaz as regras de
# construção do objeto (ex.: um identificador vazio).
class InvalidValueError(DomainError):
    """Levantada quando um valor fornecido viola uma invariante do domínio."""
