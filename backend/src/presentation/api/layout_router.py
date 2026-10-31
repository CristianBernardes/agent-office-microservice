"""Rotas do layout do escritório. Camada fina (ADR-030)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from src.application.layout.layout_use_cases import GetLayoutUseCase, SaveLayoutUseCase
from src.domain.exceptions.domain_exceptions import DomainError
from src.domain.localization.language import Language
from src.presentation.api.agents_router import get_request_language
from src.presentation.dependencies import get_get_layout_use_case, get_save_layout_use_case

router = APIRouter(prefix="/layout", tags=["layout"])


@router.get("/{name}")
async def get_layout(
    name: str,
    use_case: GetLayoutUseCase = Depends(get_get_layout_use_case),
    language: Language = Depends(get_request_language),
) -> dict[str, Any]:
    try:
        return (await use_case.execute(name)).layout
    except DomainError as error:
        raise HTTPException(404, error.localized(language)) from error


@router.put("/{name}")
async def put_layout(
    name: str,
    layout: dict[str, Any],
    use_case: SaveLayoutUseCase = Depends(get_save_layout_use_case),
    language: Language = Depends(get_request_language),
) -> dict[str, Any]:
    try:
        return (await use_case.execute(name, layout)).layout
    except DomainError as error:
        raise HTTPException(422, error.localized(language)) from error
