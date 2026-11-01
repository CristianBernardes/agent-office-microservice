"""Testes unitários dos casos de uso de tarefas (ADR-016)."""

from __future__ import annotations

import pytest

from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.tasks.task_errors import TaskNotFoundError
from src.application.tasks.task_use_cases import (
    AssignTaskUseCase,
    CompleteTaskUseCase,
    CreateTaskInput,
    CreateTaskUseCase,
    MoveTaskUseCase,
    SetTaskOwnerUseCase,
    SetTaskPriorityUseCase,
)
from src.domain.entities.agent import Agent, AgentStatus, Personality, Role
from src.domain.entities.task import Priority, TaskStatus
from src.domain.exceptions.domain_exceptions import (
    InvalidStateTransitionError,
    PermissionDeniedError,
)
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import AgentId, TaskId
from src.infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from src.infrastructure.persistence.in_memory_agent_repository import InMemoryAgentRepository
from src.infrastructure.persistence.in_memory_task_repository import InMemoryTaskRepository

pytestmark = pytest.mark.unit

PO = AgentId.generate()


@pytest.fixture
def world() -> tuple[InMemoryTaskRepository, InMemoryAgentRepository, InMemoryMessageBus]:
    return InMemoryTaskRepository(), InMemoryAgentRepository(), InMemoryMessageBus()


async def _agent(repo: InMemoryAgentRepository, name: str = "Ana") -> Agent:
    agent = Agent(
        agent_id=AgentId.generate(),
        name=name,
        role=Role.DEV_SENIOR,
        personality=Personality(0.5, 0.5, 0.5, 0.5, 0.5),
        llm_model="m",
    )
    await repo.save(agent)
    return agent


async def _create(tasks: InMemoryTaskRepository, bus: InMemoryMessageBus) -> TaskId:
    task = await CreateTaskUseCase(tasks, bus).execute(
        CreateTaskInput("Landing page", "desc", Priority.HIGH, PO, Role.PRODUCT_OWNER)
    )
    return task.task_id


class TestCreate:
    async def test_creates_in_backlog_and_persists(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, _, bus = world
        task_id = await _create(tasks, bus)
        saved = await tasks.find_by_id(task_id)
        assert saved is not None
        assert saved.status == TaskStatus.BACKLOG
        assert saved.priority == Priority.HIGH


class TestAssign:
    async def test_assigns_and_marks_agent_working(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        task_id, agent = await _create(tasks, bus), await _agent(agents)
        task = await AssignTaskUseCase(tasks, agents, bus).execute(
            task_id, agent.agent_id, PO, Role.PRODUCT_OWNER
        )
        assert task.status == TaskStatus.IN_PROGRESS
        assert agent.status == AgentStatus.WORKING
        assert agent.current_task_id == task_id

    async def test_unknown_task_raises_localized(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        agent = await _agent(agents)
        with pytest.raises(TaskNotFoundError) as error:
            await AssignTaskUseCase(tasks, agents, bus).execute(
                TaskId.generate(), agent.agent_id, PO, Role.PRODUCT_OWNER
            )
        assert "não foi encontrada" in error.value.localized(Language.PT)
        assert "was not found" in error.value.localized(Language.EN)

    async def test_unknown_agent_raises(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        with pytest.raises(AgentNotFoundError):
            await AssignTaskUseCase(tasks, agents, bus).execute(
                await _create(tasks, bus), AgentId.generate(), PO, Role.PRODUCT_OWNER
            )

    async def test_busy_agent_leaves_task_untouched(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        agent = await _agent(agents)
        use_case = AssignTaskUseCase(tasks, agents, bus)
        await use_case.execute(await _create(tasks, bus), agent.agent_id, PO, Role.PRODUCT_OWNER)
        second = await _create(tasks, bus)
        with pytest.raises(InvalidStateTransitionError):
            await use_case.execute(second, agent.agent_id, PO, Role.PRODUCT_OWNER)
        stored = await tasks.find_by_id(second)
        assert stored is not None
        assert stored.status == TaskStatus.BACKLOG


class TestRolePermissions:
    async def test_dev_cannot_assign(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        agent = await _agent(agents)
        with pytest.raises(PermissionDeniedError) as error:
            await AssignTaskUseCase(tasks, agents, bus).execute(
                await _create(tasks, bus), agent.agent_id, PO, Role.DEV_JUNIOR
            )
        assert "não pode atribuir" in error.value.localized(Language.PT)

    async def test_product_owner_cannot_complete(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        with pytest.raises(PermissionDeniedError) as error:
            await CompleteTaskUseCase(tasks, agents, bus).execute(
                await _create(tasks, bus), "x", PO, Role.PRODUCT_OWNER
            )
        assert "not allowed to complete" in error.value.localized(Language.EN)


class TestComplete:
    async def test_completes_and_frees_agent(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        task_id, agent = await _create(tasks, bus), await _agent(agents)
        await AssignTaskUseCase(tasks, agents, bus).execute(
            task_id, agent.agent_id, PO, Role.PRODUCT_OWNER
        )
        task = await CompleteTaskUseCase(tasks, agents, bus).execute(
            task_id, "feito", agent.agent_id, Role.DEV_SENIOR
        )
        assert task.status == TaskStatus.DONE
        assert agent.status == AgentStatus.IDLE

    async def test_backlog_task_cannot_complete(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        with pytest.raises(InvalidStateTransitionError) as error:
            await CompleteTaskUseCase(tasks, agents, bus).execute(
                await _create(tasks, bus), "x", PO, Role.DEV_SENIOR
            )
        assert "apenas tarefas" in error.value.localized(Language.PT)

    async def test_unknown_task_raises(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        with pytest.raises(TaskNotFoundError):
            await CompleteTaskUseCase(tasks, agents, bus).execute(
                TaskId.generate(), "x", PO, Role.DEV_SENIOR
            )


class TestTransitionsAndMove:
    async def test_history_records_every_stage_with_actor(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        task_id, agent = await _create(tasks, bus), await _agent(agents)
        await AssignTaskUseCase(tasks, agents, bus).execute(
            task_id, agent.agent_id, PO, Role.PRODUCT_OWNER
        )
        await CompleteTaskUseCase(tasks, agents, bus).execute(
            task_id, "ok", agent.agent_id, Role.DEV_SENIOR
        )
        history = await tasks.list_transitions(task_id)
        assert [(t.from_status, t.to_status) for t in history] == [
            (None, TaskStatus.BACKLOG),
            (TaskStatus.BACKLOG, TaskStatus.IN_PROGRESS),
            (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
        ]
        assert history[-1].actor_role == Role.DEV_SENIOR

    async def test_full_kanban_flow_by_the_right_roles(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        await _agent(agents)
        task_id = await _create(tasks, bus)
        move = MoveTaskUseCase(tasks, bus, agents)
        steps = [
            (TaskStatus.TODO, Role.SCRUM_MASTER),
            (TaskStatus.IN_PROGRESS, Role.DEV_JUNIOR),
            (TaskStatus.TESTING, Role.DEV_JUNIOR),
            (TaskStatus.IN_REVIEW, Role.QA_ENGINEER),
            (TaskStatus.DONE, Role.QA_ENGINEER),
        ]
        for target, role in steps:
            task = await move.execute(task_id, target, AgentId.generate(), role)
        assert task.status == TaskStatus.DONE
        assert task.completed_at is not None
        assert len(await tasks.list_transitions(task_id)) == 6

    async def test_role_without_permission_is_denied_and_task_untouched(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        await _agent(agents)
        task_id = await _create(tasks, bus)
        with pytest.raises(PermissionDeniedError) as error:
            await MoveTaskUseCase(tasks, bus, agents).execute(
                task_id, TaskStatus.TODO, PO, Role.DEV_JUNIOR
            )
        assert "não pode mover" in error.value.localized(Language.PT)
        assert "not allowed to move" in error.value.localized(Language.EN)
        stored = await tasks.find_by_id(task_id)
        assert stored is not None and stored.status == TaskStatus.BACKLOG

    async def test_move_outside_matrix_is_invalid(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        await _agent(agents)
        with pytest.raises(InvalidStateTransitionError):
            await MoveTaskUseCase(tasks, bus, agents).execute(
                await _create(tasks, bus), TaskStatus.DONE, PO, Role.PRODUCT_OWNER
            )

    async def test_move_unknown_task(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        with pytest.raises(TaskNotFoundError):
            await MoveTaskUseCase(tasks, bus, agents).execute(
                TaskId.generate(), TaskStatus.TODO, PO, Role.PRODUCT_OWNER
            )

    async def test_reviewer_can_send_back_and_move_clears_completion(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        await _agent(agents)
        task_id = await _create(tasks, bus)
        move = MoveTaskUseCase(tasks, bus, agents)
        for target, role in [
            (TaskStatus.TODO, Role.PRODUCT_OWNER),
            (TaskStatus.IN_PROGRESS, Role.DEV_SENIOR),
            (TaskStatus.TESTING, Role.DEV_SENIOR),
            (TaskStatus.IN_REVIEW, Role.QA_ENGINEER),
            (TaskStatus.IN_PROGRESS, Role.QA_ENGINEER),
            (TaskStatus.BLOCKED, Role.SCRUM_MASTER),
        ]:
            task = await move.execute(task_id, target, PO, role)
        assert task.status == TaskStatus.BLOCKED and task.completed_at is None


class TestOwnerRule:
    async def test_leaving_backlog_assigns_least_loaded_owner(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        one, two = await _agent(agents, "Um"), await _agent(agents, "Dois")
        first, second = await _create(tasks, bus), await _create(tasks, bus)
        move = MoveTaskUseCase(tasks, bus, agents)
        a = await move.execute(first, TaskStatus.TODO, PO, Role.PRODUCT_OWNER)
        b = await move.execute(second, TaskStatus.TODO, PO, Role.PRODUCT_OWNER)
        assert {a.assigned_to, b.assigned_to} == {one.agent_id, two.agent_id}

    async def test_without_workers_task_stays_in_backlog(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        task_id = await _create(tasks, bus)
        with pytest.raises(InvalidStateTransitionError) as error:
            await MoveTaskUseCase(tasks, bus, agents).execute(
                task_id, TaskStatus.TODO, PO, Role.PRODUCT_OWNER
            )
        assert "responsável" in error.value.localized(Language.PT)
        stored = await tasks.find_by_id(task_id)
        assert stored is not None and stored.status == TaskStatus.BACKLOG
        assert stored.assigned_to is None


async def _specialist(repo: InMemoryAgentRepository, role: Role) -> Agent:
    agent = Agent(AgentId.generate(), role.value, role, Personality(0.5, 0.5, 0.5, 0.5, 0.5), "m")
    await repo.save(agent)
    return agent


class TestAreaRoutingAndOwnerOverride:
    async def test_hiring_task_goes_to_hr_when_it_leaves_the_backlog(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        await _agent(agents)
        hr = await _specialist(agents, Role.HR_MANAGER)
        task = await CreateTaskUseCase(tasks, bus).execute(
            CreateTaskInput("Contratar um DBA", "", Priority.HIGH, PO, Role.PRODUCT_OWNER)
        )
        moved = await MoveTaskUseCase(tasks, bus, agents).execute(
            task.task_id, TaskStatus.TODO, PO, Role.PRODUCT_OWNER
        )
        assert moved.assigned_to == hr.agent_id

    async def test_owner_override_ignores_the_permission_matrix(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        dev = await _agent(agents)
        task_id = await _create(tasks, bus)
        move = MoveTaskUseCase(tasks, bus, agents)
        with pytest.raises(InvalidStateTransitionError):
            await move.execute(task_id, TaskStatus.DONE, dev.agent_id, Role.DEV_SENIOR)
        done = await move.execute(
            task_id, TaskStatus.DONE, dev.agent_id, Role.DEV_SENIOR, owner_override=True
        )
        assert done.status == TaskStatus.DONE
        assert done.completed_at is not None

    async def test_override_back_to_todo_releases_the_working_owner(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        dev, task_id = await _agent(agents), await _create(tasks, bus)
        await AssignTaskUseCase(tasks, agents, bus).execute(
            task_id, dev.agent_id, PO, Role.PRODUCT_OWNER
        )
        await MoveTaskUseCase(tasks, bus, agents).execute(
            task_id, TaskStatus.TODO, PO, Role.PRODUCT_OWNER, owner_override=True
        )
        refreshed = await agents.find_by_id(dev.agent_id)
        assert refreshed is not None
        assert refreshed.status == AgentStatus.IDLE

    async def test_set_owner_keeps_the_stage(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        analyst = await _specialist(agents, Role.DATA_ANALYST)
        task_id = await _create(tasks, bus)
        updated = await SetTaskOwnerUseCase(tasks, agents, bus).execute(
            task_id, analyst.agent_id, PO, Role.PRODUCT_OWNER
        )
        assert updated.assigned_to == analyst.agent_id
        assert updated.status == TaskStatus.BACKLOG

    async def test_set_owner_rejects_offline_and_unknown_agents(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, agents, bus = world
        gone = await _specialist(agents, Role.HR_MANAGER)
        gone.go_offline()
        await agents.save(gone)
        task_id = await _create(tasks, bus)
        use_case = SetTaskOwnerUseCase(tasks, agents, bus)
        with pytest.raises(InvalidStateTransitionError):
            await use_case.execute(task_id, gone.agent_id, PO, Role.PRODUCT_OWNER)
        with pytest.raises(AgentNotFoundError):
            await use_case.execute(task_id, AgentId.generate(), PO, Role.PRODUCT_OWNER)

    async def test_set_priority(self, world) -> None:  # type: ignore[no-untyped-def]
        tasks, _, bus = world
        task_id = await _create(tasks, bus)
        updated = await SetTaskPriorityUseCase(tasks, bus).execute(
            task_id, Priority.URGENT, PO, Role.PRODUCT_OWNER
        )
        assert updated.priority == Priority.URGENT
        with pytest.raises(TaskNotFoundError):
            await SetTaskPriorityUseCase(tasks, bus).execute(
                TaskId.generate(), Priority.LOW, PO, Role.PRODUCT_OWNER
            )
