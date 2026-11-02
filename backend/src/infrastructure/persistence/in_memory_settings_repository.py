"""Repositório de configurações em memória."""

from __future__ import annotations

from src.domain.interfaces.settings_repository import ISettingsRepository


class InMemorySettingsRepository(ISettingsRepository):
    def __init__(self) -> None:
        self._flags: dict[str, bool] = {}

    async def get_flag(self, key: str, default: bool) -> bool:
        return self._flags.get(key, default)

    async def set_flag(self, key: str, value: bool) -> None:
        self._flags[key] = value
