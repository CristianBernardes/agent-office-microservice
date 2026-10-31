"""Repositório de layout em memória."""

from __future__ import annotations

from src.domain.entities.office_layout import OfficeLayout
from src.domain.interfaces.layout_repository import ILayoutRepository


class InMemoryLayoutRepository(ILayoutRepository):
    def __init__(self) -> None:
        self._items: dict[str, OfficeLayout] = {}

    async def save(self, layout: OfficeLayout) -> None:
        self._items[layout.name] = layout

    async def get(self, name: str) -> OfficeLayout | None:
        return self._items.get(name)
