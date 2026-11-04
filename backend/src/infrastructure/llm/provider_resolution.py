"""Função utilitária para decidir, a partir do nome do modelo, qual provedor usar.

Cada papel configura apenas um *nome de modelo* em `.env` (ver ADR-005); não há
uma variável separada dizendo "este papel usa Claude". Em vez disso, o nome do
modelo carrega essa informação: qualquer modelo prefixado com ``claude-`` é
roteado para a Anthropic (ver ADR-058); todo o restante continua no Ollama.
"""

from __future__ import annotations

_ANTHROPIC_MODEL_PREFIX = "claude-"


def is_anthropic_model(model: str) -> bool:
    """Indica se o nome do modelo deve ser resolvido pela Anthropic, não pelo Ollama."""
    return model.startswith(_ANTHROPIC_MODEL_PREFIX)
