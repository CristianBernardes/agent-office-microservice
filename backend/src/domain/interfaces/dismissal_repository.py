"""Porta do repositório de propostas de demissão (ADR-056)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.dismissal import DismissalProposal
from src.domain.value_objects.identifiers import DismissalId


class IDismissalRepository(ABC):
    @abstractmethod
    async def save(self, proposal: DismissalProposal) -> None: ...

    @abstractmethod
    async def get(self, proposal_id: DismissalId) -> DismissalProposal | None: ...

    @abstractmethod
    async def list_all(self) -> list[DismissalProposal]: ...
