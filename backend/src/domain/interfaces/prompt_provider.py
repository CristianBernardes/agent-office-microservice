"""Contrato (porta) para obtenção do system prompt de um agente.

Mantém a camada de aplicação agnóstica a *onde* e *como* os prompts estão
armazenados (arquivo Markdown, banco de dados, etc.) — ver ADR-007.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.agent import Role
from src.domain.localization.language import Language


# Bloco: contrato único para qualquer provedor de system prompt.
class IPromptProvider(ABC):
    @abstractmethod
    def get_system_prompt(self, role: Role, agent_name: str, language: Language) -> str:
        """Retorna o system prompt do papel informado, já personalizado com o nome do agente,
        no idioma informado."""
