"""Testes unitários das rotas de layout (pt/en)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from src.domain.entities.office_layout import OfficeLayout
from src.domain.exceptions.domain_exceptions import DomainError
from src.presentation.dependencies import get_layout_repository
from src.presentation.main import app

pytestmark = pytest.mark.unit

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean() -> Iterator[None]:
    get_layout_repository.cache_clear()
    yield


class TestLayoutRoutes:
    def test_put_then_get(self) -> None:
        body = {"rooms": [{"id": "meeting", "x": 1, "y": 2}]}
        assert client.put("/layout/default", json=body).status_code == 200
        assert client.get("/layout/default").json() == body

    def test_overwrite(self) -> None:
        client.put("/layout/default", json={"v": 1})
        client.put("/layout/default", json={"v": 2})
        assert client.get("/layout/default").json() == {"v": 2}

    def test_missing_is_404_in_both_languages(self) -> None:
        en = client.get("/layout/x", headers={"Accept-Language": "en"})
        pt = client.get("/layout/x", headers={"Accept-Language": "pt-BR"})
        assert en.status_code == pt.status_code == 404
        assert en.json()["detail"] != pt.json()["detail"]

    def test_empty_layout_is_rejected(self) -> None:
        assert client.put("/layout/default", json={}).status_code == 422


class TestOfficeLayout:
    def test_requires_name_and_content(self) -> None:
        with pytest.raises(DomainError):
            OfficeLayout(" ", {"a": 1})
        with pytest.raises(DomainError):
            OfficeLayout("n", {})
