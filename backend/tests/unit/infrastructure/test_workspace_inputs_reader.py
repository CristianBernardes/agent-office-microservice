"""Testes unitários do ``WorkspaceInputsReader``."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.infrastructure.filesystem.workspace_inputs_reader import WorkspaceInputsReader

pytestmark = pytest.mark.unit


class TestWorkspaceInputsReader:
    def test_returns_empty_when_folder_does_not_exist(self, tmp_path: Path) -> None:
        assert WorkspaceInputsReader(str(tmp_path / "missing")).read_all() == ""

    def test_reads_supported_files_with_headers_and_skips_the_rest(self, tmp_path: Path) -> None:
        (tmp_path / "briefing.md").write_text("# Produto X", encoding="utf-8")
        (tmp_path / "dados.json").write_text('{"a": 1}', encoding="utf-8")
        (tmp_path / "imagem.png").write_bytes(b"\x89PNG")
        (tmp_path / ".segredo.md").write_text("oculto", encoding="utf-8")

        result = WorkspaceInputsReader(str(tmp_path)).read_all()

        assert "### briefing.md\n# Produto X" in result
        assert '### dados.json\n{"a": 1}' in result
        assert "PNG" not in result
        assert "oculto" not in result

    def test_reads_nested_folders(self, tmp_path: Path) -> None:
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "requisitos.md").write_text("RF-01", encoding="utf-8")

        assert "### docs/requisitos.md\nRF-01" in WorkspaceInputsReader(str(tmp_path)).read_all()

    def test_truncates_large_files(self, tmp_path: Path) -> None:
        (tmp_path / "grande.txt").write_text("x" * 50_000, encoding="utf-8")

        result = WorkspaceInputsReader(str(tmp_path)).read_all()

        assert "conteúdo truncado" in result
        assert len(result) < 25_000

    def test_ignores_files_that_are_not_utf8(self, tmp_path: Path) -> None:
        (tmp_path / "ruim.md").write_bytes(b"\xff\xfe\x00bad")

        assert WorkspaceInputsReader(str(tmp_path)).read_all() == ""
