"""Testes unitários da entidade de domínio ``Agent``.

Cobrem as transições de estado válidas e inválidas descritas na RFC-003, sem
qualquer dependência de infraestrutura externa.
"""

from __future__ import annotations

import pytest

from src.domain.entities.agent import Agent, AgentStatus, Personality, Role
from src.domain.exceptions.domain_exceptions import InvalidStateTransitionError
from src.domain.value_objects.identifiers import AgentId, TaskId

pytestmark = pytest.mark.unit


@pytest.fixture
def dev_senior_agent() -> Agent:
    """Agente de exemplo no papel de Dev Sênior, usado como fixture comum."""
    return Agent(
        agent_id=AgentId.generate(),
        name="Alice",
        role=Role.DEV_SENIOR,
        personality=Personality(
            openness=0.9,
            conscientiousness=0.9,
            extraversion=0.4,
            agreeableness=0.7,
            neuroticism=0.15,
        ),
        llm_model="mock-model",
    )


class TestAgentStatusTransitions:
    def test_new_agent_starts_idle(self, dev_senior_agent: Agent) -> None:
        assert dev_senior_agent.status == AgentStatus.IDLE

    def test_start_thinking_moves_to_thinking_status(self, dev_senior_agent: Agent) -> None:
        dev_senior_agent.start_thinking()
        assert dev_senior_agent.status == AgentStatus.THINKING

    def test_assign_task_moves_idle_agent_to_working(self, dev_senior_agent: Agent) -> None:
        task_id = TaskId.generate()
        dev_senior_agent.assign_task(task_id)
        assert dev_senior_agent.status == AgentStatus.WORKING
        assert dev_senior_agent.current_task_id == task_id

    def test_complete_task_returns_agent_to_idle(self, dev_senior_agent: Agent) -> None:
        dev_senior_agent.assign_task(TaskId.generate())
        dev_senior_agent.complete_task()
        assert dev_senior_agent.status == AgentStatus.IDLE
        assert dev_senior_agent.current_task_id is None

    def test_cannot_assign_task_to_agent_that_is_already_working(
        self, dev_senior_agent: Agent
    ) -> None:
        dev_senior_agent.assign_task(TaskId.generate())
        with pytest.raises(InvalidStateTransitionError):
            dev_senior_agent.assign_task(TaskId.generate())

    def test_cannot_complete_task_when_agent_is_idle(self, dev_senior_agent: Agent) -> None:
        with pytest.raises(InvalidStateTransitionError):
            dev_senior_agent.complete_task()

    def test_cannot_start_thinking_when_agent_is_offline(self, dev_senior_agent: Agent) -> None:
        dev_senior_agent.go_offline()
        with pytest.raises(InvalidStateTransitionError):
            dev_senior_agent.start_thinking()

    def test_go_offline_clears_current_task(self, dev_senior_agent: Agent) -> None:
        dev_senior_agent.assign_task(TaskId.generate())
        dev_senior_agent.go_offline()
        assert dev_senior_agent.status == AgentStatus.OFFLINE
        assert dev_senior_agent.current_task_id is None


class TestPersonalityValidation:
    def test_valid_personality_traits_are_accepted(self) -> None:
        personality = Personality(
            openness=0.5,
            conscientiousness=0.5,
            extraversion=0.5,
            agreeableness=0.5,
            neuroticism=0.5,
        )
        assert personality.openness == 0.5

    def test_trait_above_one_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="openness"):
            Personality(
                openness=1.1,
                conscientiousness=0.5,
                extraversion=0.5,
                agreeableness=0.5,
                neuroticism=0.5,
            )

    def test_trait_below_zero_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="neuroticism"):
            Personality(
                openness=0.5,
                conscientiousness=0.5,
                extraversion=0.5,
                agreeableness=0.5,
                neuroticism=-0.1,
            )


class TestFinishThinking:
    def test_finish_thinking_returns_to_idle(self, dev_senior_agent: Agent) -> None:
        dev_senior_agent.start_thinking()
        dev_senior_agent.finish_thinking()
        assert dev_senior_agent.status == AgentStatus.IDLE

    def test_finish_thinking_requires_thinking_status(self, dev_senior_agent: Agent) -> None:
        with pytest.raises(InvalidStateTransitionError):
            dev_senior_agent.finish_thinking()
