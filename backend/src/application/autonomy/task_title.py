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
