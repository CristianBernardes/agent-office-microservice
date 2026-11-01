"""Testes do roteamento de tarefas por área de cada cargo (ADR-054)."""

from __future__ import annotations

import pytest

from src.domain.entities.agent import Agent, AgentStatus, Personality, Role
from src.domain.entities.task import Task
from src.domain.services.task_routing import select_owner, suggest_role
from src.domain.value_objects.identifiers import AgentId, TaskId

pytestmark = pytest.mark.unit


def _task(title: str, description: str = "") -> Task:
    return Task(task_id=TaskId.generate(), title=title, description=description)


def _agent(role: Role, status: AgentStatus = AgentStatus.IDLE) -> Agent:
    return Agent(
        AgentId.generate(), role.value, role, Personality(0.5, 0.5, 0.5, 0.5, 0.5), "m", status
    )


class TestSuggestRole:
    @pytest.mark.parametrize(
        ("title", "role"),
        [
            ("Contratar dois desenvolvedores", Role.HR_MANAGER),
            ("Hire a QA engineer", Role.HR_MANAGER),
            ("Analisar dados de vendas no banco de dados", Role.DATA_ANALYST),
            ("Build a SQL dashboard of metrics", Role.DATA_ANALYST),
            ("Pesquisar concorrentes e preço do mercado", Role.PRODUCT_CONSULTANT),
            ("Definir a arquitetura e o deploy", Role.TECH_LEAD),
            ("Implementar a API do backend", Role.DEV_SENIOR),
        ],
    )
    def test_matches_the_area_in_pt_and_en(self, title: str, role: Role) -> None:
        assert suggest_role(_task(title)) == role

    def test_no_match_returns_none(self) -> None:
        assert suggest_role(_task("Algo genérico")) is None

    def test_word_prefix_avoids_false_positives(self) -> None:
        assert suggest_role(_task("Capital de giro")) is None

    def test_role_tag_wins_over_keywords(self) -> None:
        assert suggest_role(_task("[data_analyst] Contratar alguém")) == Role.DATA_ANALYST


class TestSelectOwner:
    def test_picks_the_area_specialist(self) -> None:
        hr, dev = _agent(Role.HR_MANAGER), _agent(Role.DEV_SENIOR)
        assert select_owner(_task("Contratar QA"), [dev, hr], {}) == hr

    def test_falls_back_to_least_loaded_dev_without_area(self) -> None:
        busy, free = _agent(Role.DEV_SENIOR), _agent(Role.DEV_JUNIOR)
        owner = select_owner(_task("Algo"), [busy, free], {busy.agent_id: 3})
        assert owner == free

    def test_falls_back_when_specialist_is_offline(self) -> None:
        hr, dev = _agent(Role.HR_MANAGER, AgentStatus.OFFLINE), _agent(Role.DEV_SENIOR)
        assert select_owner(_task("Contratar QA"), [hr, dev], {}) == dev

    def test_idle_only_skips_busy_agents(self) -> None:
        busy = _agent(Role.HR_MANAGER, AgentStatus.WORKING)
        assert select_owner(_task("Contratar QA"), [busy], {}, idle_only=True) is None

    def test_none_when_nobody_available(self) -> None:
        assert select_owner(_task("Algo"), [_agent(Role.QA_ENGINEER)], {}) is None
