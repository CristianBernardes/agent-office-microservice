"""Contrato (porta) para o material de referência fornecido pelo usuário.

São os arquivos (Markdown, JSON, texto) que o usuário deixa para os agentes lerem
antes de decidir — briefings, requisitos, dados — sem que a camada de aplicação
saiba onde nem como estão armazenados.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


# Bloco: contrato único para qualquer fonte de material de referência.
class IReferenceMaterialProvider(ABC):
    @abstractmethod
    def read_all(self) -> str:
        """Retorna o material de referência já formatado para o contexto do agente,
        ou string vazia quando não há nenhum."""
