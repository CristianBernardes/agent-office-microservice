"""Rotas do idioma do escritório (ver ADR-051)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.domain.localization.language import Language, OfficeLanguage
from src.presentation.dependencies import get_office_language

router = APIRouter(prefix="/office", tags=["office"])


class LanguagePayload(BaseModel):
    language: str


# Bloco: consulta do idioma corrente.
@router.get("/language", response_model=LanguagePayload)
async def read_language(office: OfficeLanguage = Depends(get_office_language)) -> LanguagePayload:
    return LanguagePayload(language=office.current.value)


# Bloco: troca do idioma; códigos desconhecidos mantêm o idioma atual.
@router.put("/language", response_model=LanguagePayload)
async def change_language(
    payload: LanguagePayload, office: OfficeLanguage = Depends(get_office_language)
) -> LanguagePayload:
    office.set(Language.parse(payload.language, default=office.current))
    return LanguagePayload(language=office.current.value)
