"""Porta de persistência das configurações do escritório."""

from __future__ import annotations

from abc import ABC, abstractmethod


class ISettingsRepository(ABC):
    @abstractmethod
    async def get_flag(self, key: str, default: bool) -> bool: ...

    @abstractmethod
    async def set_flag(self, key: str, value: bool) -> None: ...
