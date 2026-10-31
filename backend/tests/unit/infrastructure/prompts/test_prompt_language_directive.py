"""O prompt de sistema termina com a diretiva de idioma (pt/en)."""

from __future__ import annotations

import pytest

from src.domain.entities.agent import Role
from src.domain.localization.language import Language
from src.infrastructure.prompts.file_prompt_provider import FilePromptProvider

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("role", list(Role))
def test_portuguese_prompt_demands_portuguese(role: Role) -> None:
    prompt = FilePromptProvider().get_system_prompt(role, "Ana", Language.PT)
    assert prompt.rstrip().endswith("em inglês.")
    assert "SEMPRE em português" in prompt


def test_english_prompt_demands_english() -> None:
    prompt = FilePromptProvider().get_system_prompt(Role.QA_ENGINEER, "Ana", Language.EN)
    assert prompt.rstrip().endswith("ALWAYS answer in English.")
