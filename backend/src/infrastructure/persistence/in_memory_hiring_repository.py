"""Repositório de propostas de contratação em memória (testes e modo sem banco)."""

from __future__ import annotations

from src.domain.entities.hiring import HiringProposal
from src.domain.interfaces.hiring_repository import IHiringRepository
from src.domain.value_objects.identifiers import HiringId


class InMemoryHiringRepository(IHiringRepository):
    def __init__(self) -> None:
        self._items: dict[HiringId, HiringProposal] = {}

    async def save(self, proposal: HiringProposal) -> None:
        self._items[proposal.proposal_id] = proposal

    async def get(self, proposal_id: HiringId) -> HiringProposal | None:
        return self._items.get(proposal_id)

    async def list_all(self) -> list[HiringProposal]:
        return sorted(self._items.values(), key=lambda p: p.created_at)
