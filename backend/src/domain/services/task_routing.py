"""Serviço de domínio puro: decide qual cargo e qual profissional deve assumir uma tarefa (ADR-054).

O reconhecimento é determinístico (lista fixa de palavras-chave pt/en por cargo), sem custo de LLM.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable, Mapping

from src.domain.entities.agent import Agent, AgentStatus, Role
from src.domain.entities.task import Task
from src.domain.value_objects.identifiers import AgentId

# Bloco: cargos que executam tarefas (QA testa, PO/SM planejam: nunca são donos de execução).
EXECUTOR_ROLES: frozenset[Role] = frozenset(
    {
        Role.DEV_SENIOR,
        Role.DEV_JUNIOR,
        Role.TECH_LEAD,
        Role.DATA_ANALYST,
        Role.HR_MANAGER,
        Role.PRODUCT_CONSULTANT,
        Role.DEV_MID,
        Role.DATABASE_ADMINISTRATOR,
        Role.DEVOPS_ENGINEER,
        Role.SITE_RELIABILITY_ENGINEER,
        Role.UX_UI_DESIGNER,
        Role.BUSINESS_ANALYST,
        Role.SOFTWARE_ARCHITECT,
        Role.SECURITY_ENGINEER,
        Role.DATA_ENGINEER,
        Role.AI_ENGINEER,
        Role.ML_ENGINEER,
        Role.SYSTEMS_ANALYST,
        Role.PRODUCT_DESIGNER,
        Role.TECHNICAL_SUPPORT,
        Role.INFRASTRUCTURE_ANALYST,
        Role.DATA_QUALITY_ANALYST,
    }
)

# Bloco: quem assume uma tarefa que não casa com nenhuma área (comportamento histórico).
FALLBACK_ROLES: tuple[Role, ...] = (
    Role.DEV_SENIOR,
    Role.DEV_MID,
    Role.DEV_JUNIOR,
    Role.TECH_LEAD,
)

# Bloco: palavras-chave (sem acento, minúsculas) por cargo, em português e inglês.
# Prefixos (início de palavra) cobrem flexões (contrat → contratar, contratação, contratando).
_KEYWORDS: dict[Role, tuple[str, ...]] = {
    Role.HR_MANAGER: (
        "contrat",
        "recrut",
        "demiss",
        "demitir",
        "recursos humanos",
        "vaga",
        "onboarding",
        "hire",
        "hiring",
        "recruit",
        "dismiss",
        "human resources",
        "headcount",
        "talent",
        "talento",
        "cultura",
    ),
    Role.DATA_ANALYST: (
        "dado",
        "data",
        "dataset",
        "analise de",
        "analisar",
        "estatistic",
        "statistic",
        "metrica",
        "metric",
        "banco de dados",
        "database",
        "sql",
        "dba",
        "query",
        "consulta",
        "dashboard",
        "etl",
        "indicador",
        "kpi",
        "probabilidade",
        "probability",
    ),
    Role.PRODUCT_CONSULTANT: (
        "mercado",
        "market",
        "concorrente",
        "competitor",
        "cliente",
        "customer",
        "usuario",
        "user research",
        "proposta de valor",
        "value proposition",
        "pesquisa de",
        "dores",
        "pain point",
        "persona",
        "precificacao",
        "pricing",
        "preco",
        "oportunidade",
        "opportunit",
    ),
    Role.TECH_LEAD: (
        "arquitetura",
        "architecture",
        "infraestrutura",
        "infrastructure",
        "deploy",
        "pipeline",
        "ci/cd",
        "adr",
        "seguranca",
        "security",
        "revisao tecnica",
        "technical review",
        "design tecnico",
        "technical design",
    ),
    Role.DEV_SENIOR: (
        "implementar",
        "implement",
        "desenvolver",
        "develop",
        "codigo",
        "code",
        "api",
        "backend",
        "frontend",
        "refator",
        "algoritmo",
        "algorithm",
        "mvp",
        "prototipo",
        "prototype",
    ),
    Role.DATABASE_ADMINISTRATOR: (
        "indice",
        "index",
        "migracao",
        "migration",
        "modelagem de dados",
        "schema",
        "otimizar query",
        "slow query",
        "tuning",
    ),
    Role.DEVOPS_ENGINEER: (
        "docker",
        "container",
        "kubernetes",
        "k8s",
        "terraform",
        "github actions",
        "automacao de deploy",
        "devops",
    ),
    Role.SITE_RELIABILITY_ENGINEER: (
        "sre",
        "slo",
        "sla",
        "observabilidade",
        "observability",
        "incidente",
        "incident",
        "monitoramento",
        "monitoring",
        "postmortem",
        "alerta",
    ),
    Role.UX_UI_DESIGNER: (
        "ux",
        "ui",
        "wireframe",
        "prototipo de tela",
        "layout",
        "design de interface",
        "interface design",
        "figma",
        "usabilidade",
    ),
    Role.BUSINESS_ANALYST: (
        "requisito",
        "requirement",
        "regra de negocio",
        "business rule",
        "processo de negocio",
        "business process",
        "bpmn",
        "stakeholder",
    ),
    Role.SOFTWARE_ARCHITECT: (
        "escalabilidade",
        "scalability",
        "microsservico",
        "microservice",
        "integracao entre",
        "decisao tecnica",
        "technical decision",
        "padrao arquitetural",
    ),
    Role.SECURITY_ENGINEER: (
        "vulnerabilidade",
        "vulnerability",
        "owasp",
        "cve",
        "pentest",
        "criptografia",
        "encryption",
        "lgpd",
        "gdpr",
        "autenticacao",
        "authentication",
    ),
    Role.DATA_ENGINEER: (
        "elt",
        "pipeline de dados",
        "data pipeline",
        "data lake",
        "data warehouse",
        "ingestao",
        "ingestion",
        "airflow",
        "spark",
    ),
    Role.AI_ENGINEER: (
        "llm",
        "rag",
        "embedding",
        "agente de ia",
        "ai agent",
        "prompt engineering",
        "vector",
        "openai",
        "chatbot",
    ),
    Role.ML_ENGINEER: (
        "machine learning",
        "aprendizado de maquina",
        "treinamento de modelo",
        "model training",
        "modelo preditivo",
        "mlops",
        "fine-tuning",
        "feature engineering",
    ),
    Role.SYSTEMS_ANALYST: (
        "especificacao tecnica",
        "technical specification",
        "fluxo de sistema",
        "system flow",
        "integracao de sistemas",
        "systems integration",
        "caso de uso",
        "use case",
    ),
    Role.PRODUCT_DESIGNER: (
        "descoberta de produto",
        "product discovery",
        "jornada do usuario",
        "user journey",
        "design de solucao",
        "solution design",
        "design thinking",
    ),
    Role.TECHNICAL_SUPPORT: (
        "suporte",
        "support",
        "atendimento",
        "chamado",
        "ticket",
        "troubleshoot",
        "diagnostico",
        "diagnostic",
    ),
    Role.INFRASTRUCTURE_ANALYST: (
        "rede",
        "network",
        "servidor",
        "server",
        "dns",
        "firewall",
        "vpn",
        "ambiente de homologacao",
        "staging environment",
    ),
    Role.DATA_QUALITY_ANALYST: (
        "qualidade de dados",
        "data quality",
        "integridade",
        "integrity",
        "consistencia",
        "consistency",
        "validacao de dados",
        "data validation",
        "duplicad",
    ),
    Role.DEV_MID: (
        "funcionalidade",
        "feature",
        "endpoint",
    ),
}

_TAG = re.compile(r"^\s*\[([a-z_]+)\]")


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _score(role: Role, text: str) -> int:
    # Casa no início de palavra, evitando falsos positivos como "api" em "capital".
    return sum(1 for keyword in _KEYWORDS[role] if re.search(rf"\b{re.escape(keyword)}", text))


# Bloco: tarefas de contratação (o RH propõe o cargo e o dono escolhe nome e IA).
_HIRING_KEYWORDS = ("contrat", "recrut", "hire", "hiring", "recruit", "vaga")


def is_hiring_task(task: Task) -> bool:
    """Indica se a tarefa pede a contratação de alguém."""
    text = _normalize(f"{task.title} {task.description}")
    return any(re.search(rf"\b{re.escape(word)}", text) for word in _HIRING_KEYWORDS)


def suggest_role(task: Task) -> Role | None:
    """Cargo cuja área mais combina com a tarefa; ``None`` se nenhuma área bater.

    A etiqueta ``[cargo]`` no início do título (criada pelas reuniões) vence as palavras-chave.
    Em empate, a ordem de declaração em ``_KEYWORDS`` (mais específico primeiro) decide.
    """
    tag = _TAG.match(task.title)
    if tag:
        for role in EXECUTOR_ROLES:
            if role.value == tag.group(1):
                return role
    text = _normalize(f"{task.title} {task.description}")
    best: Role | None = None
    best_score = 0
    for role in _KEYWORDS:
        score = _score(role, text)
        if score > best_score:
            best, best_score = role, score
    return best


def select_owner(
    task: Task,
    agents: Iterable[Agent],
    load: Mapping[AgentId, int],
    *,
    idle_only: bool = False,
) -> Agent | None:
    """Escolhe o profissional: o menos carregado do cargo da área; senão, o dos cargos-reserva."""

    def available(roles: Iterable[Role]) -> list[Agent]:
        wanted = set(roles)
        return [
            a
            for a in agents
            if a.role in wanted
            and a.status != AgentStatus.OFFLINE
            and (not idle_only or a.status == AgentStatus.IDLE)
        ]

    role = suggest_role(task)
    for candidates in (available([role]) if role else [], available(FALLBACK_ROLES)):
        if candidates:
            return min(candidates, key=lambda a: load.get(a.agent_id, 0))
    return None
