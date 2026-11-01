"""Serviço de domínio puro: remove o raciocínio do LLM que vaza para o texto final (ADR-057).

Alguns modelos "reasoning" (ex.: gpt-oss) às vezes escrevem o raciocínio interno — quase
sempre em inglês, mesmo com o sistema instruído a responder em português — diretamente no
texto da resposta, em vez de usar o canal de pensamento separado da API. Esta função detecta
esse vazamento e devolve só o conteúdo final entregável.
"""

from __future__ import annotations

import re

# Bloco: expressões típicas de um modelo "pensando em voz alta" antes do conteúdo final.
_REASONING_MARKERS = re.compile(
    r"\b(we need to|we should|we can|we'll|we will|let's|let us|i'll|i will|"
    r"the user (?:says|wants|asks)|the instruction (?:says|is)|likely we|"
    r"should i|i think we|first,? we|but the instruction|we're going to)\b",
    re.IGNORECASE,
)

# Bloco: marcadores de início do conteúdo entregável (cabeçalho, negrito ou cerca de código).
_DELIVERABLE_START = re.compile(r"(\*\*[^\n*]{3,120}\*\*|#{1,6}\s+\S|```\w*\n)")

_MIN_DELIVERABLE_LENGTH = 20


def strip_reasoning_preamble(text: str) -> str:
    """Remove o raciocínio vazado antes do conteúdo final, se houver evidência clara disso.

    Localiza a última ocorrência de uma expressão de raciocínio e, depois dela, o primeiro
    marcador de conteúdo entregável; corta ali. Sem essas duas evidências, devolve o texto
    original intacto — evitando falsos positivos sobre texto legítimo.
    """
    stripped = text.strip()
    last_marker = None
    for match in _REASONING_MARKERS.finditer(stripped):
        last_marker = match
    if last_marker is None:
        return stripped

    tail = stripped[last_marker.end() :]
    deliverable = _DELIVERABLE_START.search(tail)
    if deliverable is None:
        return stripped

    rest = tail[deliverable.start() :].strip()
    return rest if len(rest) >= _MIN_DELIVERABLE_LENGTH else stripped
