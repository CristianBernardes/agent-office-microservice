"""Implementação do ``IPromptProvider`` que lê os prompts de arquivos Markdown.

Cada papel tem um arquivo próprio em ``src/infrastructure/prompts/{idioma}/{role}.md``
(ver `docs/migration-plan/fase-3-personas/README.md`), carregado e armazenado em
cache na primeira leitura — os prompts não mudam durante a execução do processo.
"""

from __future__ import annotations

from pathlib import Path

from src.domain.entities.agent import Role
from src.domain.interfaces.prompt_provider import IPromptProvider
from src.domain.localization.language import Language

# Bloco: diretório onde os arquivos de prompt residem, relativo a este módulo.
_PROMPTS_DIRECTORY = Path(__file__).parent

# Bloco: mapeamento explícito de papel para nome de arquivo.
# Mantido explícito (em vez de derivar o nome do arquivo de `role.value`) para
# que a renomeação futura de um `Role` não quebre silenciosamente a busca do
# arquivo correspondente.
_PROMPT_FILENAME_BY_ROLE: dict[Role, str] = {
    Role.PRODUCT_OWNER: "product_owner.md",
    Role.SCRUM_MASTER: "scrum_master.md",
    Role.TECH_LEAD: "tech_lead.md",
    Role.DEV_SENIOR: "dev_senior.md",
    Role.DEV_JUNIOR: "dev_junior.md",
    Role.QA_ENGINEER: "qa_engineer.md",
    Role.DATA_ANALYST: "data_analyst.md",
    Role.HR_MANAGER: "hr_manager.md",
    Role.PRODUCT_CONSULTANT: "product_consultant.md",
}


# Bloco: diretiva final e explícita de idioma — modelos tendem a derivar para o inglês.
_LANGUAGE_DIRECTIVE: dict[Language, str] = {
    Language.PT: "\n\nIMPORTANTE: responda SEMPRE em português do Brasil, mesmo que o "
    "contexto ou os termos técnicos estejam em inglês.",
    Language.EN: "\n\nIMPORTANT: ALWAYS answer in English.",
}


# Bloco: provedor de prompts baseado em arquivos Markdown.
class FilePromptProvider(IPromptProvider):
    def __init__(self) -> None:
        self._cached_templates: dict[tuple[Role, Language], str] = {}

    def get_system_prompt(self, role: Role, agent_name: str, language: Language) -> str:
        """Lê (com cache) o template do papel e o personaliza com o nome do agente."""
        template = self._load_template(role, language)
        return template.format(name=agent_name) + _LANGUAGE_DIRECTIVE[language]

    def _load_template(self, role: Role, language: Language) -> str:
        cache_key = (role, language)
        if cache_key not in self._cached_templates:
            filename = _PROMPT_FILENAME_BY_ROLE.get(role)
            if filename is None:
                raise RuntimeError(f"No prompt file mapped for role '{role.value}'.")
            file_path = _PROMPTS_DIRECTORY / language.value / filename
            self._cached_templates[cache_key] = file_path.read_text(encoding="utf-8")

        return self._cached_templates[cache_key]
