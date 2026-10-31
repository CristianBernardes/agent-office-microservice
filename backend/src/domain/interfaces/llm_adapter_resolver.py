"""Contrato (porta) para resolver o adaptador de LLM adequado a cada papel.

Permite que cada papel de agente use um modelo diferente (Fase 5 do plano de
migração) sem que os casos de uso conheçam como essa escolha é feita.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.agent import Role
from src.domain.interfaces.llm_adapter import ILlmAdapter


# Bloco: resolvedor de adaptador de LLM por papel.
class ILlmAdapterResolver(ABC):
    @abstractmethod
    def resolve(self, role: Role) -> ILlmAdapter:
        """Retorna o adaptador de LLM configurado para o papel informado."""
