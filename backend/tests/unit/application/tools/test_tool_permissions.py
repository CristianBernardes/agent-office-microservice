"""Testes unitários da tabela de permissões ``ROLE_TOOL_PERMISSIONS``."""

from __future__ import annotations

import pytest

from src.application.tools.tool_permissions import (
    ROLE_TOOL_PERMISSIONS,
    ToolName,
    role_can_use_tool,
)
from src.domain.entities.agent import Role

pytestmark = pytest.mark.unit


class TestRoleToolPermissions:
    def test_every_role_has_a_permission_entry(self) -> None:
        for role in Role:
            assert role in ROLE_TOOL_PERMISSIONS, f"Papel '{role.value}' sem permissões definidas."

    def test_every_role_can_write_artifact(self) -> None:
        # Conforme a tabela da Fase 3: `write_artifact` é permitido a todos os
        # papéis, sem exceção.
        for role in Role:
            assert role_can_use_tool(role, ToolName.WRITE_ARTIFACT)

    def test_only_tech_lead_and_product_owner_can_approve_artifact(self) -> None:
        roles_that_can_approve = {
            role for role in Role if role_can_use_tool(role, ToolName.APPROVE_ARTIFACT)
        }
        assert roles_that_can_approve == {Role.TECH_LEAD, Role.PRODUCT_OWNER}

    def test_dev_junior_cannot_approve_artifact(self) -> None:
        assert not role_can_use_tool(Role.DEV_JUNIOR, ToolName.APPROVE_ARTIFACT)

    def test_only_scrum_master_can_start_ceremony(self) -> None:
        roles_that_can_start_ceremony = {
            role for role in Role if role_can_use_tool(role, ToolName.START_CEREMONY)
        }
        assert roles_that_can_start_ceremony == {Role.SCRUM_MASTER}
