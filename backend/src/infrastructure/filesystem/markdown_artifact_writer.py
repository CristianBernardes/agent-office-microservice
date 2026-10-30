"""Escrita de artefatos em disco, como arquivos Markdown reais.

Cada artefato é persistido sob ``workspace/projects/{artifact.path}`` (ver
RFC-002), com um frontmatter YAML contendo os mesmos metadados do artefato —
garantindo que o arquivo seja autodescritivo mesmo fora do contexto do banco.
"""

from __future__ import annotations

from pathlib import Path

from src.domain.entities.artifact import Artifact

# Bloco: raiz padrão onde os artefatos dos sprints são persistidos.
# Corresponde à estrutura `workspace/projects/{sprint}/{arquivo}.md` definida na
# Fase 4 do plano de migração — `artifact.path` já contém o `{sprint}/{arquivo}.md`.
_DEFAULT_WORKSPACE_ROOT = "workspace/projects"


# Bloco: escritor de artefatos Markdown em disco.
# Mantido como uma classe pequena e focada (Single Responsibility Principle):
# sua única responsabilidade é materializar um ``Artifact`` em um arquivo real,
# sem conhecer nada sobre persistência de metadados ou notificação via MQTT —
# essas responsabilidades pertencem ao repositório e ao caso de uso.
class MarkdownArtifactWriter:
    def __init__(self, workspace_root: str = _DEFAULT_WORKSPACE_ROOT) -> None:
        self._root = Path(workspace_root)

    async def write(self, artifact: Artifact) -> Path:
        """Escreve o conteúdo do artefato em disco, com frontmatter YAML, e retorna o caminho."""
        destination_path = self._root / artifact.path
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path.write_text(self._render(artifact), encoding="utf-8")
        return destination_path

    def _render(self, artifact: Artifact) -> str:
        """Monta o conteúdo final do arquivo: frontmatter YAML seguido do Markdown do artefato."""
        frontmatter = (
            "---\n"
            f"id: {artifact.artifact_id}\n"
            f"title: {artifact.title}\n"
            f"type: {artifact.artifact_type.value}\n"
            f"status: {artifact.status.value}\n"
            f"author_id: {artifact.author_id}\n"
            f"created_at: {artifact.created_at.isoformat()}\n"
            f"updated_at: {artifact.updated_at.isoformat()}\n"
            "---\n\n"
        )
        return frontmatter + artifact.content
