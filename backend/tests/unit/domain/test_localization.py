"""Testes unitários de i18n (idioma, catálogo e erros localizados)."""

from __future__ import annotations

import string

import pytest

from src.domain.entities.agent import Personality
from src.domain.exceptions.domain_exceptions import DomainError, InvalidValueError
from src.domain.localization.language import Language
from src.domain.localization.messages import MESSAGES, translate

pytestmark = pytest.mark.unit


class TestLanguageParse:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("pt", Language.PT),
            ("pt-BR", Language.PT),
            ("EN_us", Language.EN),
            ("fr", Language.EN),
            (None, Language.EN),
            ("", Language.EN),
        ],
    )
    def test_parse(self, raw: str | None, expected: Language) -> None:
        assert Language.parse(raw) == expected

    def test_parse_uses_custom_default(self) -> None:
        assert Language.parse("xx", default=Language.PT) == Language.PT


class TestAcceptLanguage:
    def test_picks_highest_quality_supported(self) -> None:
        assert Language.from_accept_language("fr;q=0.9, pt-BR;q=0.8, en;q=0.5") == Language.PT

    def test_respects_quality_ordering(self) -> None:
        assert Language.from_accept_language("pt;q=0.3, en;q=0.9") == Language.EN

    def test_unsupported_or_missing_falls_back(self) -> None:
        assert Language.from_accept_language("fr, de", default=Language.PT) == Language.PT
        assert Language.from_accept_language(None, default=Language.PT) == Language.PT

    def test_invalid_quality_is_ignored(self) -> None:
        assert Language.from_accept_language("pt;q=abc, en") == Language.EN


class TestCatalog:
    def test_every_key_has_every_language(self) -> None:
        for key, templates in MESSAGES.items():
            assert set(templates) == set(Language), key

    def test_placeholders_match_between_languages(self) -> None:
        formatter = string.Formatter()
        for key, templates in MESSAGES.items():
            fields = {
                language: {f for _, f, _, _ in formatter.parse(text) if f}
                for language, text in templates.items()
            }
            assert fields[Language.PT] == fields[Language.EN], key

    def test_unknown_key_returns_key(self) -> None:
        assert translate("nope", Language.PT) == "nope"

    def test_translate_formats_params(self) -> None:
        assert "x1" in translate("agent.not_found", Language.PT, agent_id="x1")


class TestLocalizedErrors:
    def test_str_is_english_and_localized_is_portuguese(self) -> None:
        error = DomainError("agent.not_found", agent_id="abc")
        assert str(error) == "Agent with ID 'abc' was not found."
        assert error.localized(Language.PT) == "Agente com ID 'abc' não foi encontrado."

    def test_invalid_personality_is_value_error_and_domain_error(self) -> None:
        with pytest.raises(InvalidValueError, match="openness") as exc_info:
            Personality(
                openness=2.0,
                conscientiousness=0.5,
                extraversion=0.5,
                agreeableness=0.5,
                neuroticism=0.5,
            )
        assert isinstance(exc_info.value, ValueError)
        assert "entre 0.0 e 1.0" in exc_info.value.localized(Language.PT)
