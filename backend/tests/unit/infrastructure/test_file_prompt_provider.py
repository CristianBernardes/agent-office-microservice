"""Testes unitários do ``FilePromptProvider`` (pt/en)."""

from __future__ import annotations

import pytest

from src.domain.entities.agent import Role
from src.domain.localization.language import Language
from src.infrastructure.prompts.file_prompt_provider import FilePromptProvider

pytestmark = pytest.mark.unit

_CLOSING_MARKER = {Language.PT: "português", Language.EN: "English"}


class TestFilePromptProvider:
    @pytest.mark.parametrize("language", list(Language))
    def test_loads_prompt_for_every_role_and_language(self, language: Language) -> None:
        provider = FilePromptProvider()
        for role in Role:
            prompt = provider.get_system_prompt(role, "Alice", language)
            assert "Alice" in prompt
            assert "{name}" not in prompt
            assert _CLOSING_MARKER[language] in prompt

    def test_languages_produce_different_prompts(self) -> None:
        provider = FilePromptProvider()
        for role in Role:
            assert provider.get_system_prompt(role, "A", Language.PT) != provider.get_system_prompt(
                role, "A", Language.EN
            )

    def test_caches_template_per_role_and_language(self) -> None:
        provider = FilePromptProvider()
        provider.get_system_prompt(Role.TECH_LEAD, "Carlos", Language.EN)

        assert (Role.TECH_LEAD, Language.EN) in provider._cached_templates
        assert (Role.TECH_LEAD, Language.PT) not in provider._cached_templates

    def test_unmapped_role_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.infrastructure.prompts import file_prompt_provider as module

        monkeypatch.setattr(module, "_PROMPT_FILENAME_BY_ROLE", {})
        with pytest.raises(RuntimeError, match="No prompt file"):
            FilePromptProvider().get_system_prompt(Role.QA_ENGINEER, "A", Language.PT)
