"""Testes unitários dos identificadores tipados (value objects)."""

from __future__ import annotations

import pytest

from src.domain.value_objects.identifiers import AgentId, ArtifactId, TaskId

pytestmark = pytest.mark.unit


class TestAgentId:
    def test_generate_creates_unique_identifiers(self) -> None:
        first_id = AgentId.generate()
        second_id = AgentId.generate()
        assert first_id != second_id

    def test_str_representation_matches_underlying_uuid(self) -> None:
        agent_id = AgentId.generate()
        assert str(agent_id) == str(agent_id.value)

    def test_is_usable_as_dict_key(self) -> None:
        agent_id = AgentId.generate()
        mapping = {agent_id: "alice"}
        assert mapping[agent_id] == "alice"


class TestTaskId:
    def test_generate_creates_unique_identifiers(self) -> None:
        assert TaskId.generate() != TaskId.generate()


class TestArtifactId:
    def test_generate_creates_unique_identifiers(self) -> None:
        assert ArtifactId.generate() != ArtifactId.generate()
