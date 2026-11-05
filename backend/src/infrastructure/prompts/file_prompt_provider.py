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
    Role.DEV_MID: "dev_mid.md",
    Role.DATABASE_ADMINISTRATOR: "database_administrator.md",
    Role.DEVOPS_ENGINEER: "devops_engineer.md",
    Role.SITE_RELIABILITY_ENGINEER: "site_reliability_engineer.md",
    Role.UX_UI_DESIGNER: "ux_ui_designer.md",
    Role.BUSINESS_ANALYST: "business_analyst.md",
    Role.SOFTWARE_ARCHITECT: "software_architect.md",
    Role.SECURITY_ENGINEER: "security_engineer.md",
    Role.TEST_AUTOMATION_ENGINEER: "test_automation_engineer.md",
    Role.DATA_ENGINEER: "data_engineer.md",
    Role.AI_ENGINEER: "ai_engineer.md",
    Role.ML_ENGINEER: "ml_engineer.md",
    Role.SYSTEMS_ANALYST: "systems_analyst.md",
    Role.PRODUCT_DESIGNER: "product_designer.md",
    Role.TECHNICAL_SUPPORT: "technical_support.md",
    Role.INFRASTRUCTURE_ANALYST: "infrastructure_analyst.md",
    Role.DATA_QUALITY_ANALYST: "data_quality_analyst.md",
    Role.ENGINEERING_MANAGER: "engineering_manager.md",
}


# Bloco: diretiva final e explícita de idioma — modelos tendem a derivar para o inglês.
_LANGUAGE_DIRECTIVE: dict[Language, str] = {
    Language.PT: "\n\nIMPORTANTE: responda SEMPRE em português do Brasil, mesmo que o "
    "contexto ou os termos técnicos estejam em inglês. Escreva somente o resultado final "
    "pedido, diretamente, sem comentar como você vai responder, sem discutir formato de "
    "ferramentas e sem nenhum texto de raciocínio interno antes do conteúdo.",
    Language.EN: "\n\nIMPORTANT: ALWAYS answer in English. Write only the final requested "
    "result, directly, with no commentary about how you will answer, no discussion of tool "
    "formats, and no internal reasoning text before the content.",
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
