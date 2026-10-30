"""Testes unitários do ``FilePromptProvider``."""

from __future__ import annotations

import pytest

from src.domain.entities.agent import Role
from src.infrastructure.prompts.file_prompt_provider import FilePromptProvider

pytestmark = pytest.mark.unit


class TestFilePromptProvider:
    def test_loads_prompt_for_every_role(self) -> None:
        provider = FilePromptProvider()
        for role in Role:
            prompt = provider.get_system_prompt(role, agent_name="Alice")
            assert prompt, f"Prompt vazio para o papel '{role.value}'."

    def test_personalizes_prompt_with_agent_name(self) -> None:
        provider = FilePromptProvider()
        prompt = provider.get_system_prompt(Role.PRODUCT_OWNER, agent_name="Beatriz")
        assert "Beatriz" in prompt

    def test_caches_template_between_calls(self) -> None:
        provider = FilePromptProvider()
        provider.get_system_prompt(Role.TECH_LEAD, agent_name="Carlos")

        assert Role.TECH_LEAD in provider._cached_templates
