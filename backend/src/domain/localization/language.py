"""Idiomas suportados pelo AgentOffice (ver ADR-012)."""

from __future__ import annotations

from enum import StrEnum


# Bloco: idiomas suportados. O valor é o código curto usado em .env e Accept-Language.
class Language(StrEnum):
    PT = "pt"
    EN = "en"

    @classmethod
    def parse(cls, raw_value: str | None, default: Language | None = None) -> Language:
        """Converte um código (``pt``, ``pt-BR``, ``en-US``) em ``Language``; cai no padrão."""
        fallback = default if default is not None else cls.EN
        if not raw_value:
            return fallback
        primary_tag = raw_value.strip().lower().replace("_", "-").split("-")[0]
        try:
            return cls(primary_tag)
        except ValueError:
            return fallback

    @classmethod
    def from_accept_language(cls, header: str | None, default: Language | None = None) -> Language:
        """Escolhe o idioma suportado de maior prioridade num cabeçalho ``Accept-Language``."""
        fallback = default if default is not None else cls.EN
        if not header:
            return fallback
        candidates: list[tuple[float, int, str]] = []
        for position, part in enumerate(header.split(",")):
            tag, _, params = part.strip().partition(";")
            quality = 1.0
            if params.strip().startswith("q="):
                try:
                    quality = float(params.strip()[2:])
                except ValueError:
                    quality = 0.0
            candidates.append((-quality, position, tag))
        for _, _, tag in sorted(candidates):
            primary_tag = tag.strip().lower().split("-")[0]
            if primary_tag in {language.value for language in cls}:
                return cls(primary_tag)
        return fallback
