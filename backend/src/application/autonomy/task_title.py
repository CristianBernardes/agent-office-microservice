"""Extrai um título de tarefa limpo a partir do texto livre de um LLM."""

from __future__ import annotations

import re

_LEADING_TAG = re.compile(r"^\s*\[[^\]]{1,40}\]\s*")
_DECORATION = re.compile(r"^[\s#>*_\-`|:=~]+|[\s*_`|]+$")
_MAX_LENGTH = 120


def clean_title(text: str, fallback: str) -> str:
    """Primeira linha com conteúdo real: sem markdown, sem `[papel]`, sem separadores soltos."""
    for raw in text.splitlines():
        line = _DECORATION.sub("", _LEADING_TAG.sub("", raw)).strip()
        if any(ch.isalnum() for ch in line):
            return line[:_MAX_LENGTH]
    return fallback[:_MAX_LENGTH]


_SEPARATOR_LINE = re.compile(r"^\s*(?:[-*_=~]{3,}|```\w*)\s*$")


def clean_body(text: str) -> str:
    """Remove linhas só de separadores/cercas de código soltas no início e no fim do texto."""
    lines = text.strip().splitlines()
    while lines and (not lines[0].strip() or _SEPARATOR_LINE.match(lines[0])):
        lines.pop(0)
    while lines and (not lines[-1].strip() or _SEPARATOR_LINE.match(lines[-1])):
        lines.pop()
    return "\n".join(lines)
