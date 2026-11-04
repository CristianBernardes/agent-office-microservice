"""Resolvedor de adaptador de LLM por papel, baseado em configuração.

Cada papel pode ter um modelo próprio (via `.env`); papéis sem modelo
específico usam o modelo padrão. O modelo escolhido na contratação de um agente
específico (``agent.llm_model``), quando informado, tem prioridade sobre esses
padrões por papel (ver ADR-059) — permite que um agente use um provedor
diferente (ex.: Claude) sem afetar os demais agentes do mesmo papel. Adaptadores
são criados sob demanda e reutilizados quando duas resoluções compartilham o
mesmo modelo.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from src.domain.entities.agent import Role
from src.domain.interfaces.llm_adapter import ILlmAdapter
from src.domain.interfaces.llm_adapter_resolver import ILlmAdapterResolver


# Bloco: resolvedor que mapeia (papel, modelo do agente) -> adaptador (com cache).
# A criação do adaptador é delegada a uma factory injetada, mantendo este
# módulo independente do provedor concreto (Open/Closed Principle).
class RoleBasedLlmAdapterResolver(ILlmAdapterResolver):
    def __init__(
        self,
        adapter_factory: Callable[[str], ILlmAdapter],
        default_model: str,
        role_models: Mapping[Role, str],
    ) -> None:
        self._adapter_factory = adapter_factory
        self._default_model = default_model
        self._role_models = role_models
        self._adapters_by_model: dict[str, ILlmAdapter] = {}

    def resolve(self, role: Role, model: str = "") -> ILlmAdapter:
        """Resolve o adaptador do agente: seu próprio modelo > modelo do papel > padrão."""
        resolved_model = model or self._role_models.get(role) or self._default_model
        if resolved_model not in self._adapters_by_model:
            self._adapters_by_model[resolved_model] = self._adapter_factory(resolved_model)
        return self._adapters_by_model[resolved_model]
