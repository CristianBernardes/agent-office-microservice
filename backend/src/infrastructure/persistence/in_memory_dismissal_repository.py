"""Repositório de propostas de demissão em memória (testes e modo sem banco)."""

from __future__ import annotations

from src.domain.entities.dismissal import DismissalProposal
from src.domain.interfaces.dismissal_repository import IDismissalRepository
from src.domain.value_objects.identifiers import DismissalId


class InMemoryDismissalRepository(IDismissalRepository):
    def __init__(self) -> None:
        self._items: dict[DismissalId, DismissalProposal] = {}

    async def save(self, proposal: DismissalProposal) -> None:
        self._items[proposal.proposal_id] = proposal

    async def get(self, proposal_id: DismissalId) -> DismissalProposal | None:
        return self._items.get(proposal_id)

    async def list_all(self) -> list[DismissalProposal]:
        return sorted(self._items.values(), key=lambda p: p.created_at)
