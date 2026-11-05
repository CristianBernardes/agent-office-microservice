"""Leitura, somente leitura, dos arquivos que o usuário deixa em ``workspace/inputs``.

Permite que os agentes usem briefings, requisitos e dados (.md, .json, .txt) como
base para decidir e criar um produto. Nada é escrito aqui e só o conteúdo dessa
pasta é lido — o resto do workspace e do sistema de arquivos fica inacessível.
"""

from __future__ import annotations

from pathlib import Path

from src.domain.interfaces.reference_material_provider import IReferenceMaterialProvider

_DEFAULT_INPUTS_DIR = "workspace/inputs"
_ALLOWED_SUFFIXES = frozenset({".md", ".json", ".txt"})
# Limites para o material não estourar a janela de contexto do modelo.
_MAX_CHARS_PER_FILE = 20_000
_MAX_CHARS_TOTAL = 60_000
_TRUNCATED_MARK = "\n[... conteúdo truncado ...]"


# Bloco: leitor de material de referência a partir de uma pasta.
class WorkspaceInputsReader(IReferenceMaterialProvider):
    def __init__(self, inputs_dir: str = _DEFAULT_INPUTS_DIR) -> None:
        self._root = Path(inputs_dir)

    def read_all(self) -> str:
        """Concatena os arquivos suportados, em ordem alfabética, com um cabeçalho por arquivo."""
        if not self._root.is_dir():
            return ""

        sections: list[str] = []
        remaining = _MAX_CHARS_TOTAL
        for path in self._supported_files():
            if remaining <= 0:
                sections.append("[... demais arquivos omitidos por limite de tamanho ...]")
                break
            content = self._read(path, min(_MAX_CHARS_PER_FILE, remaining))
            if content is None:
                continue
            remaining -= len(content)
            sections.append(f"### {path.relative_to(self._root).as_posix()}\n{content}")

        return "\n\n".join(sections)

    def _supported_files(self) -> list[Path]:
        root = self._root.resolve()
        files: list[Path] = []
        for path in sorted(self._root.rglob("*")):
            relative_parts = path.relative_to(self._root).parts
            if any(part.startswith(".") for part in relative_parts):
                continue
            # `resolve()` bloqueia links simbólicos que apontem para fora da pasta.
            if (
                path.is_file()
                and path.suffix.lower() in _ALLOWED_SUFFIXES
                and root in path.resolve().parents
            ):
                files.append(path)
        return files

    @staticmethod
    def _read(path: Path, limit: int) -> str | None:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None
        if len(text) > limit:
            return text[:limit] + _TRUNCATED_MARK
        return text
