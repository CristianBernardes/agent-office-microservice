"""Erros de aplicação específicos ao fluxo de artefatos.

Diferenciados de erros de domínio porque representam falhas de orquestração
(entrada inválida fornecida ao caso de uso), não violações de regra de negócio
da entidade em si — mesmo padrão já usado por ``AgentNotFoundError``.
"""

from __future__ import annotations

from src.domain.exceptions.domain_exceptions import DomainError


# Bloco: erro levantado quando o artefato buscado não existe no repositório.
class ArtifactNotFoundError(DomainError):
    """Levantada quando o artefato solicitado não é encontrado no repositório."""
