"""Contrato (porta) para resolver o adaptador de LLM adequado a cada agente.

Permite que cada papel de agente tenha um modelo padrão (Fase 5 do plano de
migração, via `.env`) e que cada agente individual sobrescreva esse padrão com o
modelo escolhido no momento da contratação (ver ADR-059) — sem que os casos de
uso conheçam como essa escolha é feita.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.agent import Role
from src.domain.interfaces.llm_adapter import ILlmAdapter


# Bloco: resolvedor de adaptador de LLM por papel, com override por agente.
class ILlmAdapterResolver(ABC):
    @abstractmethod
    def resolve(self, role: Role, model: str = "") -> ILlmAdapter:
        """Retorna o adaptador de LLM para o agente.

        ``model`` é o modelo escolhido na contratação daquele agente específico
        (``agent.llm_model``) e, quando informado, tem prioridade sobre o modelo
        padrão configurado para o papel em `.env` (ver ADR-059).
        """
