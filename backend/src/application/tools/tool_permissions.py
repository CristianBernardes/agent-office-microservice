"""Catálogo de ferramentas disponíveis para os agentes e a tabela de permissões
por papel (ver `docs/migration-plan/fase-3-personas/README.md`).

Mantido na camada de aplicação, não no domínio: "qual ferramenta cada papel pode
usar" é uma regra de orquestração de caso de uso, não uma invariante da entidade
`Agent` em si (ver ADR-003 — a entidade permanece agnóstica a esses detalhes).
"""

from __future__ import annotations

from enum import Enum

from src.domain.entities.agent import Role


# Bloco: catálogo fechado de ferramentas que um agente pode invocar.
# Espelha exatamente a tabela "Ferramentas por Papel" da Fase 3 do plano de
# migração — nenhuma ferramenta é adicionada aqui sem antes existir na tabela
# de referência (princípio YAGNI).
class ToolName(str, Enum):
    WRITE_ARTIFACT = "write_artifact"
    READ_ARTIFACT = "read_artifact"
    REVIEW_ARTIFACT = "review_artifact"
    APPROVE_ARTIFACT = "approve_artifact"
    CREATE_TASK = "create_task"
    ASSIGN_TASK = "assign_task"
    COMPLETE_TASK = "complete_task"
    SEND_MESSAGE = "send_message"
    WEB_SEARCH = "web_search"
    HIRE_AGENT = "hire_agent"
    START_CEREMONY = "start_ceremony"
    RESEARCH = "research"


# Bloco: tabela de permissões por papel.
# Transcrita literalmente da tabela de referência da Fase 3 — qualquer mudança
# de permissão deve primeiro ser refletida naquele documento, mantendo uma
# única fonte de verdade para "o que cada papel pode fazer".
ROLE_TOOL_PERMISSIONS: dict[Role, frozenset[ToolName]] = {
    Role.PRODUCT_OWNER: frozenset(
        {
            ToolName.WRITE_ARTIFACT,
            ToolName.READ_ARTIFACT,
            ToolName.REVIEW_ARTIFACT,
            ToolName.APPROVE_ARTIFACT,
            ToolName.CREATE_TASK,
            ToolName.ASSIGN_TASK,
            ToolName.SEND_MESSAGE,
            ToolName.WEB_SEARCH,
            ToolName.RESEARCH,
            ToolName.HIRE_AGENT,
        }
    ),
    Role.SCRUM_MASTER: frozenset(
        {
            ToolName.WRITE_ARTIFACT,
            ToolName.READ_ARTIFACT,
            ToolName.CREATE_TASK,
            ToolName.ASSIGN_TASK,
            ToolName.SEND_MESSAGE,
            ToolName.START_CEREMONY,
        }
    ),
    Role.TECH_LEAD: frozenset(
        {
            ToolName.WRITE_ARTIFACT,
            ToolName.READ_ARTIFACT,
            ToolName.REVIEW_ARTIFACT,
            ToolName.APPROVE_ARTIFACT,
            ToolName.CREATE_TASK,
            ToolName.ASSIGN_TASK,
            ToolName.SEND_MESSAGE,
            ToolName.WEB_SEARCH,
            ToolName.RESEARCH,
            ToolName.HIRE_AGENT,
        }
    ),
    Role.DEV_SENIOR: frozenset(
        {
            ToolName.WRITE_ARTIFACT,
            ToolName.READ_ARTIFACT,
            ToolName.REVIEW_ARTIFACT,
            ToolName.CREATE_TASK,
            ToolName.COMPLETE_TASK,
            ToolName.SEND_MESSAGE,
            ToolName.WEB_SEARCH,
            ToolName.RESEARCH,
        }
    ),
    Role.DEV_JUNIOR: frozenset(
        {
            ToolName.WRITE_ARTIFACT,
            ToolName.READ_ARTIFACT,
            ToolName.COMPLETE_TASK,
            ToolName.SEND_MESSAGE,
            ToolName.WEB_SEARCH,
            ToolName.RESEARCH,
        }
    ),
    Role.QA_ENGINEER: frozenset(
        {
            ToolName.WRITE_ARTIFACT,
            ToolName.READ_ARTIFACT,
            ToolName.REVIEW_ARTIFACT,
            ToolName.CREATE_TASK,
            ToolName.COMPLETE_TASK,
            ToolName.SEND_MESSAGE,
        }
    ),
    Role.DATA_ANALYST: frozenset(
        {
            ToolName.WRITE_ARTIFACT,
            ToolName.READ_ARTIFACT,
            ToolName.COMPLETE_TASK,
            ToolName.SEND_MESSAGE,
            ToolName.WEB_SEARCH,
            ToolName.RESEARCH,
        }
    ),
    Role.HR_MANAGER: frozenset(
        {
            ToolName.WRITE_ARTIFACT,
            ToolName.READ_ARTIFACT,
            ToolName.COMPLETE_TASK,
            ToolName.SEND_MESSAGE,
            ToolName.HIRE_AGENT,
        }
    ),
    Role.PRODUCT_CONSULTANT: frozenset(
        {
            ToolName.WRITE_ARTIFACT,
            ToolName.READ_ARTIFACT,
            ToolName.REVIEW_ARTIFACT,
            ToolName.COMPLETE_TASK,
            ToolName.SEND_MESSAGE,
            ToolName.WEB_SEARCH,
            ToolName.RESEARCH,
        }
    ),
}


def role_can_use_tool(role: Role, tool_name: ToolName) -> bool:
    """Verifica se o papel informado tem permissão para usar a ferramenta."""
    return tool_name in ROLE_TOOL_PERMISSIONS.get(role, frozenset())
