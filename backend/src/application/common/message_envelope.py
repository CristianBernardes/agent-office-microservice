"""Construção do envelope padrão de mensagens MQTT (ver RFC-001).

Qualquer caso de uso que publique eventos no barramento de mensagens usa esta
função para montar o envelope, evitando duplicar a lógica de geração de
``event_id`` e timestamp em cada caso de uso individualmente (princípio DRY).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

# Bloco: versão atual do formato de envelope, conforme a RFC-001.
_ENVELOPE_VERSION = "1.0"


def build_message_envelope(
    agent_id: str,
    agent_role: str,
    payload: dict[str, object],
) -> dict[str, object]:
    """Monta o envelope padrão de mensagens definido na RFC-001."""
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "version": _ENVELOPE_VERSION,
        "agent_id": agent_id,
        "agent_role": agent_role,
        "payload": payload,
    }
