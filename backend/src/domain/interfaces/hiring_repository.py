"""Porta do repositório de propostas de contratação."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.hiring import HiringProposal
from src.domain.value_objects.identifiers import HiringId


class IHiringRepository(ABC):
    @abstractmethod
    async def save(self, proposal: HiringProposal) -> None: ...

    @abstractmethod
    async def get(self, proposal_id: HiringId) -> HiringProposal | None: ...

    @abstractmethod
    async def list_all(self) -> list[HiringProposal]: ...
