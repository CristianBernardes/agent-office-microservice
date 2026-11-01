"""Testes das demissões propostas pelo RH e decididas pelo dono do produto (ADR-056)."""

from __future__ import annotations

import pytest

from src.application.agents.fire_agent_use_case import AgentNotFoundError, FireAgentUseCase
from src.application.dismissals.dismissal_use_cases import (
    DecideDismissalUseCase,
    DismissalNotFoundError,
    ProposeDismissalInput,
    ProposeDismissalUseCase,
)
from src.domain.entities.agent import Agent, AgentStatus, Personality, Role
from src.domain.entities.dismissal import DismissalStatus
from src.domain.entities.task import Task, TaskStatus
from src.domain.exceptions.domain_exceptions import (
    InvalidStateTransitionError,
    InvalidValueError,
    PermissionDeniedError,
)
from src.domain.value_objects.identifiers import AgentId, DismissalId, TaskId
from src.infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from src.infrastructure.persistence.in_memory_agent_repository import InMemoryAgentRepository
from src.infrastructure.persistence.in_memory_dismissal_repository import (
    InMemoryDismissalRepository,
)
from src.infrastructure.persistence.in_memory_task_repository import InMemoryTaskRepository

pytestmark = pytest.mark.unit


def _agent(role: Role) -> Agent:
    return Agent(AgentId.generate(), role.value, role, Personality(0.5, 0.5, 0.5, 0.5, 0.5), "m")


class _World:
    def __init__(self) -> None:
        self.agents = InMemoryAgentRepository()
        self.tasks = InMemoryTaskRepository()
        self.dismissals = InMemoryDismissalRepository()
        self.bus = InMemoryMessageBus()
        self.events: list[str] = []
        self.propose = ProposeDismissalUseCase(self.agents, self.dismissals, self.bus)
        self.decide = DecideDismissalUseCase(
            self.dismissals, FireAgentUseCase(self.agents, self.tasks, self.bus), self.bus
        )

    async def hire(self, role: Role) -> Agent:
        agent = _agent(role)
        await self.agents.save(agent)
        return agent


@pytest.fixture
async def world() -> _World:
    w = _World()

    async def collect(topic: str, _: dict[str, object]) -> None:
        w.events.append(topic)

    await w.bus.subscribe("office/dismissals/+", collect)
    return w


class TestPropose:
    async def test_hr_proposes_with_a_reason_and_nobody_is_fired_yet(self, world: _World) -> None:
        hr, dev = await world.hire(Role.HR_MANAGER), await world.hire(Role.DEV_JUNIOR)

        proposal = await world.propose.execute(
            ProposeDismissalInput(hr.agent_id, dev.agent_id, "  Entregas atrasadas  ")
        )

        assert proposal.status == DismissalStatus.PENDING
        assert proposal.reason == "Entregas atrasadas"
        assert (await world.agents.find_by_id(dev.agent_id)).status != AgentStatus.OFFLINE  # type: ignore[union-attr]
        assert world.events == ["office/dismissals/proposed"]

    async def test_only_hr_can_propose(self, world: _World) -> None:
        po, dev = await world.hire(Role.PRODUCT_OWNER), await world.hire(Role.DEV_JUNIOR)
        with pytest.raises(PermissionDeniedError):
            await world.propose.execute(ProposeDismissalInput(po.agent_id, dev.agent_id, "x"))

    async def test_requires_a_reason(self, world: _World) -> None:
        hr, dev = await world.hire(Role.HR_MANAGER), await world.hire(Role.DEV_JUNIOR)
        with pytest.raises(InvalidValueError):
            await world.propose.execute(ProposeDismissalInput(hr.agent_id, dev.agent_id, "   "))

    async def test_rejects_self_offline_unknown_and_duplicate(self, world: _World) -> None:
        hr, dev = await world.hire(Role.HR_MANAGER), await world.hire(Role.DEV_JUNIOR)
        gone = await world.hire(Role.QA_ENGINEER)
        gone.go_offline()
        await world.agents.save(gone)

        for target in (hr.agent_id, gone.agent_id):
            with pytest.raises(InvalidStateTransitionError):
                await world.propose.execute(ProposeDismissalInput(hr.agent_id, target, "motivo"))
        with pytest.raises(AgentNotFoundError):
            await world.propose.execute(
                ProposeDismissalInput(hr.agent_id, AgentId.generate(), "motivo")
            )
        await world.propose.execute(ProposeDismissalInput(hr.agent_id, dev.agent_id, "a"))
        with pytest.raises(InvalidStateTransitionError):
            await world.propose.execute(ProposeDismissalInput(hr.agent_id, dev.agent_id, "b"))


class TestDecide:
    async def _pending(self, world: _World) -> tuple[Agent, DismissalId]:
        hr, dev = await world.hire(Role.HR_MANAGER), await world.hire(Role.DEV_JUNIOR)
        proposal = await world.propose.execute(
            ProposeDismissalInput(hr.agent_id, dev.agent_id, "motivo")
        )
        return dev, proposal.proposal_id

    async def test_approval_fires_the_agent_and_returns_work_to_the_flow(
        self, world: _World
    ) -> None:
        dev, proposal_id = await self._pending(world)
        task = Task(TaskId.generate(), "T", "d", TaskStatus.IN_PROGRESS)
        task.assigned_to = dev.agent_id
        await world.tasks.save(task)

        decided = await world.decide.execute(proposal_id, approved=True)

        assert decided.status == DismissalStatus.APPROVED
        assert decided.decided_at is not None
        assert (await world.agents.find_by_id(dev.agent_id)).status == AgentStatus.OFFLINE  # type: ignore[union-attr]
        reloaded = await world.tasks.find_by_id(task.task_id)
        assert reloaded is not None
        assert (reloaded.assigned_to, reloaded.status) == (None, TaskStatus.TODO)
        assert world.events[-1] == "office/dismissals/decided"

    async def test_rejection_keeps_the_agent(self, world: _World) -> None:
        dev, proposal_id = await self._pending(world)

        decided = await world.decide.execute(proposal_id, approved=False)

        assert decided.status == DismissalStatus.REJECTED
        assert (await world.agents.find_by_id(dev.agent_id)).status != AgentStatus.OFFLINE  # type: ignore[union-attr]

    async def test_cannot_decide_twice_or_unknown(self, world: _World) -> None:
        _, proposal_id = await self._pending(world)
        await world.decide.execute(proposal_id, approved=False)
        with pytest.raises(InvalidStateTransitionError):
            await world.decide.execute(proposal_id, approved=True)
        with pytest.raises(DismissalNotFoundError):
            await world.decide.execute(DismissalId.generate(), approved=True)
