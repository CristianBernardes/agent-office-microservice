"""Exceções de domínio do AgentOffice.

Todas as exceções levantadas pelas entidades e value objects do domínio herdam de
``DomainError``, permitindo que camadas superiores (aplicação, apresentação) capturem
e tratem erros de negócio de forma uniforme, sem depender de exceções genéricas do
Python (``ValueError``, ``RuntimeError``) que poderiam se confundir com bugs de
infraestrutura.
"""

from __future__ import annotations

from src.domain.localization.language import Language
from src.domain.localization.messages import translate


# Bloco: exceção-base de domínio.
# Serve como ponto único de captura para qualquer violação de regra de negócio,
# diferenciando erros esperados (regra violada) de erros inesperados (bug).
class DomainError(Exception):
    """Erro base para qualquer violação de invariante do domínio.

    Carrega uma chave de mensagem + parâmetros; ``str()`` rende em inglês (logs) e
    ``localized`` rende no idioma pedido (ver ADR-012).
    """

    def __init__(self, message_key: str, **params: object) -> None:
        self.message_key = message_key
        self.params = params
        super().__init__(translate(message_key, Language.EN, **params))

    def localized(self, language: Language) -> str:
        """Mensagem de erro no idioma informado."""
        return translate(self.message_key, language, **self.params)


# Bloco: violação de transição de estado de uma entidade.
# Usada quando uma entidade recebe um comando que não é válido para o seu estado
# atual (ex.: atribuir uma tarefa a um agente que já está ocupado).
class InvalidStateTransitionError(DomainError):
    """Levantada quando uma transição de estado solicitada não é permitida."""


# Bloco: papel sem permissão para a ação (ex.: mover um cartão fora da sua responsabilidade).
class PermissionDeniedError(DomainError):
    """Levantada quando o papel do ator não pode executar a ação."""


# Bloco: violação de invariante de valor.
# Usada por value objects quando um valor recebido não satisfaz as regras de
# construção do objeto (ex.: um identificador vazio).
class InvalidValueError(DomainError, ValueError):
    """Levantada quando um valor fornecido viola uma invariante do domínio."""
