"""Constantes compartilhadas da integração com a API da Anthropic.

Isoladas aqui porque são usadas tanto por `AnthropicAdapter` (chamadas de
raciocínio) quanto pela rota `/models` (listagem de modelos disponíveis para o
frontend) — evita duplicar o número de versão da API em dois lugares.
"""

from __future__ import annotations

# Versão da API Messages/Models da Anthropic exigida no header `anthropic-version`.
ANTHROPIC_API_VERSION = "2023-06-01"
