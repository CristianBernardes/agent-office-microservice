"""Testes unitários de ``build_message_envelope``."""

from __future__ import annotations

import pytest

from src.application.common.message_envelope import build_message_envelope

pytestmark = pytest.mark.unit


class TestBuildMessageEnvelope:
    def test_envelope_contains_all_required_fields(self) -> None:
        envelope = build_message_envelope(
            agent_id="agent-123",
            agent_role="dev_senior",
            payload={"thought": "Pensando sobre a tarefa."},
        )

        assert envelope["agent_id"] == "agent-123"
        assert envelope["agent_role"] == "dev_senior"
        assert envelope["version"] == "1.0"
        assert envelope["payload"] == {"thought": "Pensando sobre a tarefa."}
        assert "event_id" in envelope
        assert "timestamp" in envelope

    def test_each_envelope_has_a_unique_event_id(self) -> None:
        first_envelope = build_message_envelope("a", "role", {})
        second_envelope = build_message_envelope("a", "role", {})

        assert first_envelope["event_id"] != second_envelope["event_id"]
