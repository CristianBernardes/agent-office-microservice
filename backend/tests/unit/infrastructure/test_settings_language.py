"""Testes unitários do idioma configurável em ``Settings``."""

from __future__ import annotations

import pytest

from src.domain.localization.language import Language
from src.infrastructure.config.settings import Settings

pytestmark = pytest.mark.unit


class TestSettingsLanguage:
    def test_default_is_english(self) -> None:
        assert Settings(_env_file=None).language() == Language.EN

    def test_reads_portuguese(self) -> None:
        assert Settings(_env_file=None, office_language="pt").language() == Language.PT

    def test_invalid_value_falls_back_to_english(self) -> None:
        assert Settings(_env_file=None, office_language="xx").language() == Language.EN
