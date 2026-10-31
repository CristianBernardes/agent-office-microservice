"""Testes unitários do idioma do escritório em tempo de execução (ADR-051)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.domain.localization.language import Language, OfficeLanguage
from src.presentation.dependencies import get_office_language
from src.presentation.main import app

pytestmark = pytest.mark.unit


@pytest.fixture
def client() -> TestClient:
    office = OfficeLanguage(Language.PT)
    app.dependency_overrides[get_office_language] = lambda: office
    yield TestClient(app)
    app.dependency_overrides.pop(get_office_language, None)


def test_reads_and_changes_language(client: TestClient) -> None:
    assert client.get("/office/language").json() == {"language": "pt"}
    assert client.put("/office/language", json={"language": "en"}).json() == {"language": "en"}
    assert client.get("/office/language").json() == {"language": "en"}


def test_unknown_language_keeps_current(client: TestClient) -> None:
    assert client.put("/office/language", json={"language": "xx"}).json() == {"language": "pt"}


def test_office_language_holder() -> None:
    office = OfficeLanguage(Language.EN)
    office.set(Language.PT)
    assert office.current is Language.PT
