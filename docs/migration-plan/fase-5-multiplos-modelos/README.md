# Fase 5 — Múltiplos Modelos: LLM por Agente

> Cada agente pode usar um modelo Ollama diferente, configurado via `.env`. A injeção de dependência garante que trocar de modelo não exige mudança de código.

---

## 🎯 Objetivo

- Configurar modelos LLM diferentes por papel via `.env`
- Implementar `ILLMAdapter` com suporte a Ollama e OpenAI-compatible
- Garantir que a troca de modelo seja transparente para os use cases
- Suportar múltiplos provedores (Ollama, OpenAI, Gaia, OpenRouter)

---

## ⚙️ Configuração via `.env`

```env
# .env

# Modelos por papel (Ollama)
AGENT_PO_MODEL=nemotron-3.5-bolt:latest
AGENT_SM_MODEL=nemotron-3.5-bolt:latest
AGENT_TECH_LEAD_MODEL=qwen3.6:latest
AGENT_DEV_SENIOR_MODEL=nemotron-3.5-bolt:latest
AGENT_DEV_JUNIOR_MODEL=llama3.2:latest
AGENT_QA_MODEL=qwen3.6:latest
AGENT_DATA_MODEL=qwen3.6:latest
AGENT_HR_MODEL=llama3.2:latest
AGENT_CONSULTANT_MODEL=nemotron-3.5-bolt:latest

# Modelo de embeddings (memória semântica)
OLLAMA_EMBED_MODEL=nomic-embed-text:latest

# URL do Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Provedor alternativo (opcional)
# OPENAI_API_KEY=sk-...
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_MODEL=gpt-4o-mini
```

---

## 🔌 Interface ILLMAdapter

```python
# domain/interfaces/llm_interface.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    """Resposta estruturada do LLM."""
    thought:    str                  # Pensamento interno do agente
    action:     str                  # Ação a executar
    target:     Optional[str]        # Alvo da ação (agente, tarefa, etc.)
    tool_call:  Optional[dict]       # Chamada de ferramenta, se houver
    raw:        str                  # Resposta bruta do LLM


@dataclass
class EmbeddingResponse:
    """Resposta de embedding vetorial."""
    vector:     list[float]
    model:      str
    dimensions: int


class ILLMAdapter(ABC):
    """
    Contrato para adaptadores de LLM.
    Implementações: OllamaAdapter, OpenAICompatibleAdapter, MockLLMAdapter
    """

    @abstractmethod
    async def think(
        self,
        system_prompt: str,
        context: str,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Envia contexto para o LLM e retorna resposta estruturada.

        O LLM deve retornar JSON no formato:
        {
            "thought": "...",
            "action": "send_message | write_artifact | create_task | ...",
            "target": "agent_id | null",
            "tool_call": { "tool": "...", "args": {...} } | null
        }
        """
        ...

    @abstractmethod
    async def embed(self, text: str) -> EmbeddingResponse:
        """Gera embedding vetorial para busca semântica na memória."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Nome do modelo sendo usado."""
        ...
```

---

## 🦙 OllamaAdapter

```python
# infrastructure/llm/ollama_adapter.py
import json
import httpx
from domain.interfaces.llm_interface import ILLMAdapter, LLMResponse, EmbeddingResponse

THINK_SCHEMA = {
    "type": "object",
    "properties": {
        "thought":   {"type": "string"},
        "action":    {"type": "string"},
        "target":    {"type": ["string", "null"]},
        "tool_call": {
            "oneOf": [
                {"type": "null"},
                {
                    "type": "object",
                    "properties": {
                        "tool": {"type": "string"},
                        "args": {"type": "object"}
                    },
                    "required": ["tool", "args"]
                }
            ]
        }
    },
    "required": ["thought", "action"]
}


class OllamaAdapter(ILLMAdapter):
    def __init__(self, base_url: str, model: str, embed_model: str):
        self._base_url   = base_url.rstrip("/")
        self._model      = model
        self._embed_model = embed_model
        self._client     = httpx.AsyncClient(timeout=120.0)

    @property
    def model_name(self) -> str:
        return self._model

    async def think(
        self,
        system_prompt: str,
        context: str,
        temperature: float = 0.7,
    ) -> LLMResponse:
        response = await self._client.post(
            f"{self._base_url}/api/chat",
            json={
                "model": self._model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": context},
                ],
                "format": THINK_SCHEMA,   # JSON Schema para saída estruturada
                "options": {
                    "temperature": temperature,
                    "num_predict": 1024,
                },
                "stream": False,
            }
        )
        response.raise_for_status()

        raw = response.json()["message"]["content"]
        parsed = json.loads(raw)

        return LLMResponse(
            thought=parsed.get("thought", ""),
            action=parsed.get("action", "idle"),
            target=parsed.get("target"),
            tool_call=parsed.get("tool_call"),
            raw=raw,
        )

    async def embed(self, text: str) -> EmbeddingResponse:
        response = await self._client.post(
            f"{self._base_url}/api/embeddings",
            json={"model": self._embed_model, "prompt": text}
        )
        response.raise_for_status()

        vector = response.json()["embedding"]
        return EmbeddingResponse(
            vector=vector,
            model=self._embed_model,
            dimensions=len(vector),
        )
```

---

## 🤖 OpenAICompatibleAdapter

```python
# infrastructure/llm/openai_adapter.py
import json
from openai import AsyncOpenAI
from domain.interfaces.llm_interface import ILLMAdapter, LLMResponse, EmbeddingResponse


class OpenAICompatibleAdapter(ILLMAdapter):
    """
    Funciona com qualquer API OpenAI-compatible:
    - OpenAI (api.openai.com)
    - Gaia (gaianet.ai)
    - OpenRouter (openrouter.ai)
    - LM Studio (localhost:1234)
    """

    def __init__(self, base_url: str, api_key: str, model: str, embed_model: str = "text-embedding-3-small"):
        self._model       = model
        self._embed_model = embed_model
        self._client      = AsyncOpenAI(base_url=base_url, api_key=api_key)

    @property
    def model_name(self) -> str:
        return self._model

    async def think(
        self,
        system_prompt: str,
        context: str,
        temperature: float = 0.7,
    ) -> LLMResponse:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": context},
            ],
            response_format={"type": "json_object"},
            temperature=temperature,
            max_tokens=1024,
        )

        raw = response.choices[0].message.content
        parsed = json.loads(raw)

        return LLMResponse(
            thought=parsed.get("thought", ""),
            action=parsed.get("action", "idle"),
            target=parsed.get("target"),
            tool_call=parsed.get("tool_call"),
            raw=raw,
        )

    async def embed(self, text: str) -> EmbeddingResponse:
        response = await self._client.embeddings.create(
            model=self._embed_model,
            input=text,
        )
        vector = response.data[0].embedding
        return EmbeddingResponse(
            vector=vector,
            model=self._embed_model,
            dimensions=len(vector),
        )
```

---

## 🧪 MockLLMAdapter (para testes)

```python
# infrastructure/llm/mock_llm_adapter.py
from domain.interfaces.llm_interface import ILLMAdapter, LLMResponse, EmbeddingResponse


class MockLLMAdapter(ILLMAdapter):
    """
    Adaptador mock para testes unitários e de integração.
    Permite injetar respostas pré-definidas.
    """

    def __init__(self, responses: list[LLMResponse] | None = None):
        self._responses = responses or []
        self._call_count = 0

    @property
    def model_name(self) -> str:
        return "mock-model"

    async def think(self, system_prompt: str, context: str, temperature: float = 0.7) -> LLMResponse:
        if self._responses:
            response = self._responses[self._call_count % len(self._responses)]
            self._call_count += 1
            return response

        # Resposta padrão
        return LLMResponse(
            thought="Estou analisando a situação.",
            action="write_artifact",
            target=None,
            tool_call={
                "tool": "write_artifact",
                "args": {
                    "title": "Documento de Teste",
                    "content": "# Teste\n\nConteúdo gerado pelo mock.",
                    "type": "implementation",
                }
            },
            raw='{"thought": "...", "action": "write_artifact"}',
        )

    async def embed(self, text: str) -> EmbeddingResponse:
        # Embedding fake com dimensão 384
        import hashlib
        seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % 1000
        vector = [(seed + i) / 1000.0 for i in range(384)]
        return EmbeddingResponse(vector=vector, model="mock-embed", dimensions=384)
```

---

## 🏭 LLMAdapterFactory

```python
# infrastructure/llm/llm_adapter_factory.py
import os
from domain.entities.agent import Role
from domain.interfaces.llm_interface import ILLMAdapter
from .ollama_adapter import OllamaAdapter
from .openai_adapter import OpenAICompatibleAdapter

ROLE_ENV_MAP = {
    Role.PRODUCT_OWNER:      "AGENT_PO_MODEL",
    Role.SCRUM_MASTER:       "AGENT_SM_MODEL",
    Role.TECH_LEAD:          "AGENT_TECH_LEAD_MODEL",
    Role.DEV_SENIOR:         "AGENT_DEV_SENIOR_MODEL",
    Role.DEV_JUNIOR:         "AGENT_DEV_JUNIOR_MODEL",
    Role.QA_ENGINEER:        "AGENT_QA_MODEL",
    Role.DATA_ANALYST:       "AGENT_DATA_MODEL",
    Role.HR_MANAGER:         "AGENT_HR_MODEL",
    Role.PRODUCT_CONSULTANT: "AGENT_CONSULTANT_MODEL",
}

DEFAULT_MODEL = "nemotron-3.5-bolt:latest"


class LLMAdapterFactory:
    @staticmethod
    def create_for_role(role: Role) -> ILLMAdapter:
        env_key = ROLE_ENV_MAP.get(role, "AGENT_DEV_SENIOR_MODEL")
        model   = os.getenv(env_key, DEFAULT_MODEL)

        # Se OpenAI key estiver configurada, usa OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            return OpenAICompatibleAdapter(
                base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                api_key=openai_key,
                model=os.getenv("OPENAI_MODEL", model),
                embed_model=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small"),
            )

        # Padrão: Ollama
        return OllamaAdapter(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=model,
            embed_model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text:latest"),
        )
```

---

## 💉 Injeção de Dependência (FastAPI)

```python
# presentation/dependencies.py
from functools import lru_cache
from fastapi import Depends

from domain.entities.agent import Role
from domain.interfaces.llm_interface import ILLMAdapter
from domain.interfaces.message_bus import IMessageBus
from infrastructure.llm.llm_adapter_factory import LLMAdapterFactory
from infrastructure.messaging.mqtt_message_bus import MqttMessageBus
from infrastructure.persistence.postgres.agent_repo import PostgresAgentRepository
from application.agents.think_use_case import AgentThinkUseCase


@lru_cache
def get_mqtt_bus() -> IMessageBus:
    import os
    return MqttMessageBus(
        host=os.getenv("MQTT_HOST", "localhost"),
        port=int(os.getenv("MQTT_PORT", "1883")),
    )


def get_llm_for_role(role: Role) -> ILLMAdapter:
    return LLMAdapterFactory.create_for_role(role)


def get_think_use_case(
    role: Role,
    bus: IMessageBus = Depends(get_mqtt_bus),
) -> AgentThinkUseCase:
    llm = get_llm_for_role(role)
    return AgentThinkUseCase(llm=llm, bus=bus)
```

---

## ✅ Checklist da Fase 5

- [ ] `ILLMAdapter` interface com `think()` e `embed()`
- [ ] `LLMResponse` e `EmbeddingResponse` dataclasses
- [ ] `OllamaAdapter` com JSON Schema para saída estruturada
- [ ] `OpenAICompatibleAdapter` para provedores alternativos
- [ ] `MockLLMAdapter` para testes
- [ ] `LLMAdapterFactory` lendo modelos do `.env` por papel
- [ ] `ROLE_ENV_MAP` mapeando todos os 9 papéis
- [ ] `.env.example` documentado com todos os modelos
- [ ] Injeção de dependência configurada no FastAPI
- [ ] Testes unitários: `OllamaAdapter` com mock HTTP
- [ ] Testes unitários: `LLMAdapterFactory` lê `.env` corretamente
- [ ] Testes de integração: agente usa modelo correto para seu papel
