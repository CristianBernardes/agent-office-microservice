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
    }
)

# Bloco: quem assume uma tarefa que não casa com nenhuma área (comportamento histórico).
FALLBACK_ROLES: tuple[Role, ...] = (Role.DEV_SENIOR, Role.DEV_JUNIOR, Role.TECH_LEAD)

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
}

_TAG = re.compile(r"^\s*\[([a-z_]+)\]")


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _score(role: Role, text: str) -> int:
    # Casa no início de palavra, evitando falsos positivos como "api" em "capital".
    return sum(1 for keyword in _KEYWORDS[role] if re.search(rf"\b{re.escape(keyword)}", text))


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
