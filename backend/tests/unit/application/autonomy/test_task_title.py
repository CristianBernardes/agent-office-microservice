import pytest

from src.application.autonomy.task_title import clean_body, clean_title


@pytest.mark.unit
class TestCleanTitle:
    def test_skips_separator_lines(self) -> None:
        assert clean_title("---\n\nDefinir a arquitetura", "x") == "Definir a arquitetura"

    def test_strips_role_tag_and_markdown(self) -> None:
        assert clean_title("[dev_senior] ## **Criar API**", "x") == "Criar API"

    def test_falls_back_when_no_content(self) -> None:
        assert clean_title("---\n***", "Tarefa") == "Tarefa"

    def test_limits_length(self) -> None:
        assert len(clean_title("a" * 500, "x")) == 120


@pytest.mark.unit
class TestCleanBody:
    def test_strips_edge_separators(self) -> None:
        assert clean_body("---\n\nTexto\nmais\n***\n") == "Texto\nmais"

    def test_keeps_inner_separators(self) -> None:
        assert clean_body("a\n---\nb") == "a\n---\nb"

    def test_empty_when_only_separators(self) -> None:
        assert clean_body("---\n---") == ""
