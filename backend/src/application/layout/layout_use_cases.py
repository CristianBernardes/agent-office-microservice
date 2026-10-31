"""Casos de uso do layout do escritório (ADR-030)."""

from __future__ import annotations

from typing import Any

from src.domain.entities.office_layout import OfficeLayout
from src.domain.exceptions.domain_exceptions import DomainError
from src.domain.interfaces.layout_repository import ILayoutRepository


class GetLayoutUseCase:
    def __init__(self, repository: ILayoutRepository) -> None:
        self._repository = repository

    async def execute(self, name: str) -> OfficeLayout:
        layout = await self._repository.get(name)
        if layout is None:
            raise DomainError("layout.not_found", name=name)
        return layout


class SaveLayoutUseCase:
    def __init__(self, repository: ILayoutRepository) -> None:
        self._repository = repository

    async def execute(self, name: str, layout: dict[str, Any]) -> OfficeLayout:
        entity = OfficeLayout(name, layout)
        await self._repository.save(entity)
        return entity
