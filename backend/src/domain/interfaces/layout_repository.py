"""Porta de persistência do layout do escritório."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.office_layout import OfficeLayout


class ILayoutRepository(ABC):
    @abstractmethod
    async def save(self, layout: OfficeLayout) -> None: ...

    @abstractmethod
    async def get(self, name: str) -> OfficeLayout | None: ...
