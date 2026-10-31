"""Testes unitários do ``RoleBasedLlmAdapterResolver`` e da configuração por papel."""

from __future__ import annotations

import pytest

from src.domain.entities.agent import Role
from src.domain.interfaces.llm_adapter import ILlmAdapter
from src.infrastructure.config.settings import Settings
from src.infrastructure.llm.mock_llm_adapter import MockLlmAdapter
from src.infrastructure.llm.role_based_llm_adapter_resolver import RoleBasedLlmAdapterResolver

pytestmark = pytest.mark.unit


class TestRoleBasedLlmAdapterResolver:
    def _build(self, created_models: list[str]) -> RoleBasedLlmAdapterResolver:
        def factory(model: str) -> ILlmAdapter:
            created_models.append(model)
            return MockLlmAdapter()

        return RoleBasedLlmAdapterResolver(
            adapter_factory=factory,
            default_model="default-model",
            role_models={Role.TECH_LEAD: "big-model", Role.QA_ENGINEER: "big-model"},
        )

    def test_uses_default_model_when_role_has_no_override(self) -> None:
        created: list[str] = []
        self._build(created).resolve(Role.PRODUCT_OWNER)
        assert created == ["default-model"]

    def test_uses_role_specific_model(self) -> None:
        created: list[str] = []
        self._build(created).resolve(Role.TECH_LEAD)
        assert created == ["big-model"]

    def test_reuses_adapter_for_roles_sharing_a_model(self) -> None:
        created: list[str] = []
        resolver = self._build(created)
        assert resolver.resolve(Role.TECH_LEAD) is resolver.resolve(Role.QA_ENGINEER)
        assert created == ["big-model"]


class TestSettingsRoleModels:
    def test_only_non_empty_role_models_are_returned(self) -> None:
        settings = Settings(agent_po_model="po-model", agent_qa_model="", _env_file=None)
        assert settings.role_models() == {Role.PRODUCT_OWNER: "po-model"}
