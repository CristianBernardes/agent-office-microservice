# Fase 6 — Testes: Estratégia Completa

> Testes são cidadãos de primeira classe. Esta fase define a estratégia de testes unitários, de integração e e2e, com exemplos concretos para cada camada da arquitetura.

---

## 🎯 Objetivo

- Definir a pirâmide de testes do projeto
- Implementar testes unitários para o domínio e casos de uso
- Implementar testes de integração para MQTT, banco e LLM
- Implementar testes e2e para fluxos completos
- Configurar CI/CD para rodar testes automaticamente

---

## 🔺 Pirâmide de Testes

```
           /\
          /  \
         / e2e\        ← Poucos, lentos, testam fluxos completos
        /──────\
       /integra-\
      / ção      \     ← Médios, testam componentes integrados
     /────────────\
    /   unitários  \
   /                \  ← Muitos, rápidos, testam unidades isoladas
  /──────────────────\
```

| Tipo | Quantidade | Velocidade | Foco |
|------|-----------|-----------|------|
| Unitários | ~70% | < 1ms | Domínio, use cases |
| Integração | ~20% | < 1s | MQTT, banco, LLM |
| E2E | ~10% | < 30s | Fluxos completos |

---

## 🧪 Testes Unitários

### Domínio — Agent

```python
# tests/unit/domain/test_agent.py
import pytest
from uuid import uuid4
from domain.entities.agent import Agent, Role, AgentStatus, Personality

@pytest.fixture
def dev_senior() -> Agent:
    return Agent(
        id=uuid4(),
        name="Alice",
        role=Role.DEV_SENIOR,
        personality=Personality(
            openness=0.9, conscientiousness=0.9,
            extraversion=0.4, agreeableness=0.7, neuroticism=0.15
        ),
        llm_model="nemotron-3.5-bolt:latest",
    )


class TestAgentStatusTransitions:
    def test_initial_status_is_idle(self, dev_senior: Agent):
        assert dev_senior.status == AgentStatus.IDLE

    def test_start_thinking_changes_status(self, dev_senior: Agent):
        dev_senior.start_thinking()
        assert dev_senior.status == AgentStatus.THINKING

    def test_assign_task_changes_status_to_working(self, dev_senior: Agent):
        task_id = uuid4()
        dev_senior.assign_task(task_id)
        assert dev_senior.status == AgentStatus.WORKING
        assert dev_senior.current_task_id == task_id

    def test_complete_task_resets_to_idle(self, dev_senior: Agent):
        task_id = uuid4()
        dev_senior.assign_task(task_id)
        dev_senior.complete_task()
        assert dev_senior.status == AgentStatus.IDLE
        assert dev_senior.current_task_id is None

    def test_cannot_assign_task_while_thinking(self, dev_senior: Agent):
        dev_senior.start_thinking()
        with pytest.raises(ValueError, match="Agente está pensando"):
            dev_senior.assign_task(uuid4())
```

### Domínio — Task

```python
# tests/unit/domain/test_task.py
import pytest
from uuid import uuid4
from datetime import datetime
from domain.entities.task import Task, TaskStatus, Priority


class TestTaskLifecycle:
    def test_new_task_starts_in_backlog(self):
        task = Task(id=uuid4(), title="Implementar login", description="...")
        assert task.status == TaskStatus.BACKLOG

    def test_assign_changes_status_to_in_progress(self):
        task = Task(id=uuid4(), title="Implementar login", description="...")
        agent_id = uuid4()
        task.assign(agent_id)
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.assigned_to == agent_id

    def test_complete_sets_result_and_timestamp(self):
        task = Task(id=uuid4(), title="Implementar login", description="...")
        task.assign(uuid4())
        task.complete("Login implementado com JWT. Ver design-doc-auth.md")
        assert task.status == TaskStatus.DONE
        assert task.result is not None
        assert task.completed_at is not None

    def test_cannot_complete_unassigned_task(self):
        task = Task(id=uuid4(), title="Implementar login", description="...")
        with pytest.raises(ValueError, match="Tarefa não está em progresso"):
            task.complete("resultado")
```

### Caso de Uso — AgentThinkUseCase

```python
# tests/unit/application/test_think_use_case.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from domain.entities.agent import Agent, Role, AgentStatus, Personality
from domain.interfaces.llm_interface import LLMResponse
from infrastructure.llm.mock_llm_adapter import MockLLMAdapter
from infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from application.agents.think_use_case import AgentThinkUseCase


@pytest.fixture
def agent() -> Agent:
    return Agent(
        id=uuid4(),
        name="Alice",
        role=Role.DEV_SENIOR,
        personality=Personality(0.9, 0.9, 0.4, 0.7, 0.15),
        llm_model="mock",
    )


@pytest.fixture
def mock_llm() -> MockLLMAdapter:
    return MockLLMAdapter(responses=[
        LLMResponse(
            thought="Vou escrever o design doc de autenticação.",
            action="write_artifact",
            target=None,
            tool_call={
                "tool": "write_artifact",
                "args": {
                    "title": "Design Doc — Auth",
                    "content": "# Auth\n\nJWT com refresh token.",
                    "type": "design_doc",
                }
            },
            raw='{"thought": "...", "action": "write_artifact"}',
        )
    ])


@pytest.fixture
def bus() -> InMemoryMessageBus:
    return InMemoryMessageBus()


class TestAgentThinkUseCase:
    @pytest.mark.asyncio
    async def test_publishes_thought_to_mqtt(self, agent, mock_llm, bus):
        use_case = AgentThinkUseCase(llm=mock_llm, bus=bus)
        await use_case.execute(agent, context="Sprint 1, tarefa: Implementar auth")

        thought_messages = bus.get_messages(f"office/agents/{agent.id}/thought")
        assert len(thought_messages) == 1
        assert "Vou escrever" in thought_messages[0]["payload"]["thought"]

    @pytest.mark.asyncio
    async def test_publishes_action_to_mqtt(self, agent, mock_llm, bus):
        use_case = AgentThinkUseCase(llm=mock_llm, bus=bus)
        await use_case.execute(agent, context="Sprint 1")

        action_messages = bus.get_messages(f"office/agents/{agent.id}/action")
        assert len(action_messages) == 1
        assert action_messages[0]["payload"]["action"] == "write_artifact"

    @pytest.mark.asyncio
    async def test_agent_status_returns_to_idle_after_think(self, agent, mock_llm, bus):
        use_case = AgentThinkUseCase(llm=mock_llm, bus=bus)
        await use_case.execute(agent, context="Sprint 1")
        assert agent.status == AgentStatus.IDLE
```

### Caso de Uso — WriteArtifactUseCase

```python
# tests/unit/application/test_write_artifact_use_case.py
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from domain.entities.artifact import ArtifactType, ArtifactStatus
from infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from application.artifacts.write_artifact_use_case import WriteArtifactUseCase, WriteArtifactInput


class TestWriteArtifactUseCase:
    @pytest.mark.asyncio
    async def test_creates_artifact_with_draft_status(self):
        repo = AsyncMock()
        bus = InMemoryMessageBus()
        use_case = WriteArtifactUseCase(artifact_repo=repo, message_bus=bus)

        artifact = await use_case.execute(WriteArtifactInput(
            title="Design Doc — Auth",
            content="# Auth\n\nJWT.",
            type=ArtifactType.DESIGN_DOC,
            path="workspace/projects/sprint-1/design-doc-auth.md",
            author_id=uuid4(),
        ))

        assert artifact.status == ArtifactStatus.DRAFT
        repo.save.assert_called_once_with(artifact)

    @pytest.mark.asyncio
    async def test_publishes_artifact_created_event(self):
        repo = AsyncMock()
        bus = InMemoryMessageBus()
        use_case = WriteArtifactUseCase(artifact_repo=repo, message_bus=bus)

        await use_case.execute(WriteArtifactInput(
            title="Backlog",
            content="# Backlog",
            type=ArtifactType.BACKLOG,
            path="workspace/projects/sprint-1/backlog.md",
            author_id=uuid4(),
        ))

        messages = bus.get_messages("office/artifacts/created")
        assert len(messages) == 1
        assert messages[0]["title"] == "Backlog"
```

---

## 🔗 Testes de Integração

### MQTT — Fluxo de Mensagem entre Agentes

```python
# tests/integration/test_mqtt_flow.py
import pytest
import asyncio
from uuid import uuid4

from infrastructure.messaging.mqtt_message_bus import MqttMessageBus


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_message_reaches_subscriber():
    """Agente A publica mensagem → Agente B recebe."""
    bus = MqttMessageBus(host="localhost", port=1883)
    await bus.connect()

    received = []

    async def handler(topic: str, payload: dict):
        received.append(payload)

    await bus.subscribe("office/agents/alice/message", handler)

    await bus.publish(
        topic="office/agents/alice/message",
        payload={
            "agent_id": "alice",
            "payload": {
                "target_agent_id": "bob",
                "message": "Bob, o design doc está pronto.",
            }
        },
        qos=1,
    )

    await asyncio.sleep(0.5)  # Aguarda entrega

    assert len(received) == 1
    assert received[0]["payload"]["message"] == "Bob, o design doc está pronto."

    await bus.disconnect()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_retained_status_received_on_connect():
    """Novo cliente recebe último status retido ao conectar."""
    bus1 = MqttMessageBus(host="localhost", port=1883)
    await bus1.connect()

    # Publica status com retain=True
    await bus1.publish(
        topic="office/agents/alice/status",
        payload={"agent_id": "alice", "payload": {"status": "working"}},
        qos=1,
        retain=True,
    )
    await bus1.disconnect()

    # Novo cliente conecta e deve receber o status retido
    bus2 = MqttMessageBus(host="localhost", port=1883)
    await bus2.connect()

    received = []
    async def handler(topic, payload):
        received.append(payload)

    await bus2.subscribe("office/agents/alice/status", handler)
    await asyncio.sleep(0.5)

    assert len(received) == 1
    assert received[0]["payload"]["status"] == "working"

    await bus2.disconnect()
```

### Banco de Dados — Persistência de Artefatos

```python
# tests/integration/test_artifact_persistence.py
import pytest
from uuid import uuid4

from domain.entities.artifact import ArtifactType, ArtifactStatus
from infrastructure.persistence.postgres.artifact_repo import PostgresArtifactRepository


@pytest.mark.integration
@pytest.mark.asyncio
async def test_save_and_retrieve_artifact(pg_pool):
    repo = PostgresArtifactRepository(pool=pg_pool)
    author_id = uuid4()

    from domain.entities.artifact import Artifact
    from datetime import datetime, timezone

    artifact = Artifact(
        id=uuid4(),
        title="Design Doc — Auth",
        content="# Auth\n\nJWT com refresh token.",
        type=ArtifactType.DESIGN_DOC,
        path="workspace/projects/sprint-1/design-doc-auth.md",
        author_id=author_id,
        status=ArtifactStatus.DRAFT,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    await repo.save(artifact)
    retrieved = await repo.find_by_id(artifact.id)

    assert retrieved is not None
    assert retrieved.title == "Design Doc — Auth"
    assert retrieved.status == ArtifactStatus.DRAFT
    assert retrieved.author_id == author_id
```

---

## 🌐 Testes E2E

### Fluxo Completo: PO cria tarefa → Dev implementa → QA testa

```python
# tests/e2e/test_full_sprint_flow.py
import pytest
import asyncio
from uuid import uuid4

from infrastructure.llm.mock_llm_adapter import MockLLMAdapter
from domain.interfaces.llm_interface import LLMResponse


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_po_creates_task_dev_implements_qa_tests(office_app):
    """
    Fluxo completo:
    1. PO cria user story
    2. SM atribui ao Dev Sênior
    3. Dev Sênior implementa e escreve artefato
    4. QA cria plano de testes
    5. Tarefa é marcada como concluída
    """
    events = []
    office_app.on_event(lambda e: events.append(e))

    # PO cria tarefa
    await office_app.agents["po"].think(
        context="Precisamos implementar autenticação JWT no sprint 1."
    )

    await asyncio.sleep(1)

    # Verifica que tarefa foi criada
    task_created = [e for e in events if e["type"] == "task_created"]
    assert len(task_created) >= 1

    # Dev Sênior recebe e implementa
    await office_app.agents["dev_senior"].think(
        context=f"Tarefa atribuída: {task_created[0]['payload']['title']}"
    )

    await asyncio.sleep(1)

    # Verifica que artefato foi criado
    artifact_created = [e for e in events if e["type"] == "artifact_created"]
    assert len(artifact_created) >= 1

    # QA cria plano de testes
    await office_app.agents["qa"].think(
        context=f"Feature implementada: {artifact_created[0]['payload']['title']}"
    )

    await asyncio.sleep(1)

    # Verifica plano de testes
    test_plans = [
        e for e in events
        if e["type"] == "artifact_created"
        and e["payload"]["type"] == "test_plan"
    ]
    assert len(test_plans) >= 1
```

---

## ⚙️ Configuração do pytest

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
markers = [
    "unit: testes unitários (rápidos, sem dependências externas)",
    "integration: testes de integração (requerem MQTT e PostgreSQL)",
    "e2e: testes end-to-end (requerem sistema completo rodando)",
]

# Rodar apenas unitários (CI rápido)
# pytest -m unit

# Rodar unitários + integração
# pytest -m "unit or integration"

# Rodar tudo
# pytest
```

```toml
# pyproject.toml (dependências de teste)
[tool.poetry.group.test.dependencies]
pytest = "^8.0"
pytest-asyncio = "^0.23"
pytest-cov = "^5.0"
pytest-mock = "^3.12"
httpx = "^0.27"   # Para testar endpoints FastAPI
```

---

## 🔄 CI/CD — GitHub Actions

```yaml
# .github/workflows/tests.yml
name: Testes

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    name: Testes Unitários
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install poetry && poetry install
      - run: poetry run pytest -m unit --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v4

  integration-tests:
    name: Testes de Integração
    runs-on: ubuntu-latest
    services:
      postgres:
        image: pgvector/pgvector:pg16
        env:
          POSTGRES_DB: agentoffice_test
          POSTGRES_USER: agentoffice
          POSTGRES_PASSWORD: agentoffice
        ports: ["5432:5432"]
      mqtt:
        image: eclipse-mosquitto:2.0
        ports: ["1883:1883"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install poetry && poetry install
      - run: poetry run pytest -m integration
        env:
          DATABASE_URL: postgresql://agentoffice:agentoffice@localhost:5432/agentoffice_test
          MQTT_HOST: localhost
```

---

## 📊 Metas de Cobertura

| Camada | Meta |
|--------|------|
| `domain/` | 100% |
| `application/` | 95% |
| `infrastructure/` | 80% |
| `presentation/` | 70% |
| **Total** | **85%** |

---

## ✅ Checklist da Fase 6

- [ ] `InMemoryMessageBus` para testes unitários
- [ ] `MockLLMAdapter` com respostas configuráveis
- [ ] Testes unitários: `Agent` (transições de status)
- [ ] Testes unitários: `Task` (ciclo de vida)
- [ ] Testes unitários: `Artifact` (ciclo de vida)
- [ ] Testes unitários: `AgentThinkUseCase`
- [ ] Testes unitários: `WriteArtifactUseCase`
- [ ] Testes unitários: `CreateTaskUseCase`
- [ ] Testes unitários: `HireAgentUseCase`
- [ ] Testes de integração: MQTT publish/subscribe
- [ ] Testes de integração: MQTT retain
- [ ] Testes de integração: PostgreSQL artifact persistence
- [ ] Testes de integração: PostgreSQL memory recall (pgvector)
- [ ] Testes e2e: fluxo completo PO → Dev → QA
- [ ] `pyproject.toml` com markers configurados
- [ ] GitHub Actions: CI rodando unitários em todo PR
- [ ] GitHub Actions: CI rodando integração no push para main
- [ ] Cobertura mínima de 85% configurada no CI
