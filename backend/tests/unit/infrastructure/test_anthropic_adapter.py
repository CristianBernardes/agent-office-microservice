"""Testes do ``AnthropicAdapter`` (ADR-058)."""

from __future__ import annotations

import pytest

from src.infrastructure.llm.anthropic_adapter import AnthropicAdapter, _parse_structured_reply

pytestmark = pytest.mark.unit


class TestParseStructuredReply:
    def test_plain_json_is_parsed(self) -> None:
        assert _parse_structured_reply('{"thought": "oi", "action": "idle"}')["thought"] == "oi"

    def test_json_inside_code_fence_is_extracted(self) -> None:
        raw = 'Aqui está:\n```json\n{"thought": "ok", "action": "speak"}\n```'
        parsed = _parse_structured_reply(raw)
        assert parsed["thought"] == "ok" and parsed["action"] == "speak"

    def test_plain_text_becomes_thought(self) -> None:
        parsed = _parse_structured_reply("  só texto livre ")
        assert parsed == {"thought": "só texto livre", "action": "idle"}


class TestAnthropicAdapter:
    def test_model_name_is_exposed(self) -> None:
        adapter = AnthropicAdapter(api_key="key", model="claude-sonnet-4-5-20250929")
        assert adapter.model_name == "claude-sonnet-4-5-20250929"

    async def test_think_without_api_key_raises_explicit_error(self) -> None:
        adapter = AnthropicAdapter(api_key="", model="claude-sonnet-4-5-20250929")
        with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
            await adapter.think(system_prompt="sistema", context="contexto")

    async def test_embed_is_not_supported(self) -> None:
        adapter = AnthropicAdapter(api_key="key", model="claude-sonnet-4-5-20250929")
        with pytest.raises(NotImplementedError):
            await adapter.embed("texto qualquer")
