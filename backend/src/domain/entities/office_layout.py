"""Entidade do layout do escritório (ADR-030)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.domain.exceptions.domain_exceptions import DomainError


@dataclass(frozen=True)
class OfficeLayout:
    name: str
    layout: dict[str, Any]

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.layout:
            raise DomainError("layout.invalid")
