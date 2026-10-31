"""Testes da leitura tolerante da resposta do Ollama (ADR-036)."""

import pytest

from src.infrastructure.llm.ollama_adapter import _parse_structured_reply

pytestmark = pytest.mark.unit


def test_plain_json_is_parsed() -> None:
    assert _parse_structured_reply('{"thought": "oi", "action": "idle"}')["thought"] == "oi"


def test_json_inside_code_fence_is_extracted() -> None:
    raw = 'Aqui está:\n```json\n{"thought": "ok", "action": "speak"}\n```'
    parsed = _parse_structured_reply(raw)
    assert parsed["thought"] == "ok" and parsed["action"] == "speak"


def test_plain_text_becomes_thought() -> None:
    parsed = _parse_structured_reply("  só texto livre ")
    assert parsed == {"thought": "só texto livre", "action": "idle"}


def test_non_object_json_falls_back_to_text() -> None:
    assert _parse_structured_reply("[1, 2]")["thought"] == "[1, 2]"
