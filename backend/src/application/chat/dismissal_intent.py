"""Detecta, numa mensagem do dono, o pedido explícito de demitir alguém (ADR-060).

Determinístico de propósito: a ordem do dono não pode depender de o LLM decidir chamar uma
ferramenta. Perguntas e frases condicionais ("caso ele não se alinhe…") não são ordens.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from src.domain.entities.agent import Agent

_ORDER = re.compile(
    r"\b(demit\w*|demiss\w*|despe(?:ç|c|d)\w*|desliga\w*|mand\w+ embora|fire|fired|dismiss\w*|"
    r"let go|sack\w*|terminate)\b",
    re.IGNORECASE,
)
_CONDITIONAL = re.compile(r"\b(caso|se|if|whether|unless|talvez|maybe)\b|\?", re.IGNORECASE)
_MIN_TOKEN = 3


def _last_mention(text: str, agent: Agent) -> int:
    """Posição da última citação do agente no texto (-1 se não citado)."""
    last = -1
    for candidate in {agent.name, *agent.name.split()[:1]}:
        if len(candidate) >= _MIN_TOKEN:
            for match in re.finditer(rf"\b{re.escape(candidate)}\b", text, re.IGNORECASE):
                last = max(last, match.start())
    return last


def detect_dismissal_targets(
    message: str, history: Sequence[str], candidates: Sequence[Agent]
) -> list[Agent]:
    """Agentes que o dono mandou demitir; vazio se a mensagem não for uma ordem clara.

    Sem nome na mensagem ("quero demitir ele!"), vale o último agente citado na conversa.
    """
    if not _ORDER.search(message) or _CONDITIONAL.search(message):
        return []
    named = [a for a in candidates if _last_mention(message, a) >= 0]
    if named:
        return named
    for previous in reversed(history):
        found = [(_last_mention(previous, a), a) for a in candidates]
        found = [(pos, a) for pos, a in found if pos >= 0]
        if found:
            return [max(found, key=lambda item: item[0])[1]]
    return []
