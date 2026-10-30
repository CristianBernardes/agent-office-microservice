# Fase 1 — Arquitetura: Clean Architecture + Nova Stack

> Esta fase define a estrutura de pastas, camadas e responsabilidades do novo backend Python e do frontend React refatorado, seguindo Clean Architecture, SOLID, DRY e YAGNI.

---

## 🎯 Objetivo

- Definir a estrutura de pastas do backend Python (Clean Architecture)
- Definir a estrutura do frontend React refatorado
- Estabelecer as interfaces (contratos) entre camadas
- Garantir que nenhuma lógica de negócio dependa de frameworks

---

## 🏛️ Clean Architecture — Visão Geral

```
┌─────────────────────────────────────────────────┐
│                  Presentation                    │  ← FastAPI, WebSocket, MQTT handlers
│  ┌───────────────────────────────────────────┐  │
│  │              Application                  │  │  ← Casos de uso (orquestração)
│  │  ┌─────────────────────────────────────┐  │  │
│  │  │              Domain                 │  │  │  ← Entidades, regras de negócio puras
│  │  │  Agent, Task, Artifact, Message     │  │  │
│  │  └─────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
         ↑                          ↑
  Infrastructure                Infrastructure
  (PostgreSQL,                  (MQTT, Ollama,
   pgvector)                     Filesystem)
```

**Regra de ouro:** As setas de dependência apontam sempre para dentro. O domínio não conhece nada externo.

---

## 📁 Estrutura Completa do Backend

```
backend/
├── src/
│   │
│   ├── domain/                          # Camada mais interna — zero dependências externas
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── agent.py                 # Agent, Role, Personality, AgentStatus
│   │   │   ├── task.py                  # Task, TaskStatus, Priority
│   │   │   ├── artifact.py              # Artifact, ArtifactType, ArtifactStatus
│   │   │   ├── message.py               # Message, MessageType
│   │   │   ├── sprint.py                # Sprint, SprintStatus, Ceremony
│   │   │   └── memory.py                # Memory, MemoryType, Embedding
│   │   │
│   │   ├── value_objects/
│   │   │   ├── agent_id.py              # AgentId (UUID tipado)
│   │   │   ├── task_id.py               # TaskId
│   │   │   ├── topic.py                 # MqttTopic (validação de formato)
│   │   │   └── artifact_path.py         # ArtifactPath (validação de caminho)
│   │   │
│   │   ├── events/
│   │   │   ├── agent_events.py          # AgentThought, AgentActed, AgentHired
│   │   │   ├── task_events.py           # TaskCreated, TaskAssigned, TaskCompleted
│   │   │   └── artifact_events.py       # ArtifactCreated, ArtifactApproved
│   │   │
│   │   └── interfaces/                  # Contratos (Dependency Inversion)
│   │       ├── llm_interface.py         # ILLMAdapter
│   │       ├── memory_repo.py           # IMemoryRepository
│   │       ├── task_repo.py             # ITaskRepository
│   │       ├── artifact_repo.py         # IArtifactRepository
│   │       ├── message_bus.py           # IMessageBus
│   │       └── agent_repo.py            # IAgentRepository
│   │
│   ├── application/                     # Casos de uso — orquestra domínio e interfaces
│   │   ├── __init__.py
│   │   ├── agents/
│   │   │   ├── think_use_case.py        # AgentThinkUseCase
│   │   │   ├── hire_agent_use_case.py   # HireAgentUseCase
│   │   │   ├── fire_agent_use_case.py   # FireAgentUseCase
│   │   │   └── send_message_use_case.py # SendMessageUseCase
│   │   │
│   │   ├── tasks/
│   │   │   ├── create_task_use_case.py  # CreateTaskUseCase
│   │   │   ├── assign_task_use_case.py  # AssignTaskUseCase
│   │   │   └── complete_task_use_case.py# CompleteTaskUseCase
│   │   │
│   │   ├── artifacts/
│   │   │   ├── write_artifact_use_case.py   # WriteArtifactUseCase
│   │   │   ├── review_artifact_use_case.py  # ReviewArtifactUseCase
│   │   │   └── approve_artifact_use_case.py # ApproveArtifactUseCase
│   │   │
│   │   ├── sprint/
│   │   │   ├── start_sprint_use_case.py # StartSprintUseCase
│   │   │   └── end_sprint_use_case.py   # EndSprintUseCase
│   │   │
│   │   └── memory/
│   │       ├── save_memory_use_case.py  # SaveMemoryUseCase
│   │       └── recall_memory_use_case.py# RecallMemoryUseCase (busca semântica)
│   │
│   ├── infrastructure/                  # Implementações concretas das interfaces
│   │   ├── __init__.py
│   │   ├── llm/
│   │   │   ├── ollama_adapter.py        # Implementa ILLMAdapter via Ollama
│   │   │   ├── openai_adapter.py        # Implementa ILLMAdapter via OpenAI-compatible
│   │   │   └── mock_llm_adapter.py      # Para testes
│   │   │
│   │   ├── messaging/
│   │   │   ├── mqtt_message_bus.py      # Implementa IMessageBus via aiomqtt
│   │   │   └── in_memory_message_bus.py # Para testes
│   │   │
│   │   ├── persistence/
│   │   │   ├── postgres/
│   │   │   │   ├── agent_repo.py        # Implementa IAgentRepository
│   │   │   │   ├── task_repo.py         # Implementa ITaskRepository
│   │   │   │   ├── memory_repo.py       # Implementa IMemoryRepository (pgvector)
│   │   │   │   └── artifact_repo.py     # Implementa IArtifactRepository
│   │   │   └── migrations/
│   │   │       └── 001_initial_schema.sql
│   │   │
│   │   └── filesystem/
│   │       └── markdown_artifact_writer.py  # Escreve .md em workspace/
│   │
│   └── presentation/                    # Entrega — FastAPI, WebSocket, MQTT
│       ├── __init__.py
│       ├── api/
│       │   ├── agents_router.py         # GET/POST /agents
│       │   ├── tasks_router.py          # GET/POST /tasks
│       │   ├── artifacts_router.py      # GET /artifacts
│       │   └── sprint_router.py         # POST /sprint/start, /sprint/end
│       │
│       ├── websocket/
│       │   └── office_hub.py            # WebSocket para o frontend
│       │
│       ├── mqtt/
│       │   └── mqtt_subscriber.py       # Assina tópicos e despacha para use cases
│       │
│       └── dependencies.py              # Injeção de dependência (FastAPI Depends)
│
├── tests/
│   ├── unit/
│   │   ├── domain/
│   │   │   ├── test_agent.py
│   │   │   ├── test_task.py
│   │   │   └── test_artifact.py
│   │   └── application/
│   │       ├── test_think_use_case.py
│   │       ├── test_create_task_use_case.py
│   │       └── test_write_artifact_use_case.py
│   │
│   └── integration/
│       ├── test_mqtt_flow.py
│       ├── test_agent_think_integration.py
│       └── test_artifact_persistence.py
│
├── pyproject.toml
├── Dockerfile
└── .env.example
```

---

## 🧩 Entidades do Domínio

### Agent

```python
# domain/entities/agent.py
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from uuid import UUID

class Role(str, Enum):
    PRODUCT_OWNER      = "product_owner"
    SCRUM_MASTER       = "scrum_master"
    TECH_LEAD          = "tech_lead"
    DEV_SENIOR         = "dev_senior"
    DEV_JUNIOR         = "dev_junior"
    QA_ENGINEER        = "qa_engineer"
    DATA_ANALYST       = "data_analyst"
    HR_MANAGER         = "hr_manager"
    PRODUCT_CONSULTANT = "product_consultant"

class AgentStatus(str, Enum):
    IDLE      = "idle"
    THINKING  = "thinking"
    WORKING   = "working"
    TALKING   = "talking"
    OFFLINE   = "offline"

@dataclass
class Personality:
    openness:          float  # 0.0 - 1.0
    conscientiousness: float
    extraversion:      float
    agreeableness:     float
    neuroticism:       float

@dataclass
class Agent:
    id:          UUID
    name:        str
    role:        Role
    personality: Personality
    llm_model:   str
    status:      AgentStatus = AgentStatus.IDLE
    current_task_id: Optional[UUID] = None
    hired_by:    Optional[UUID] = None  # ID do agente que contratou este

    def start_thinking(self) -> None:
        self.status = AgentStatus.THINKING

    def complete_task(self) -> None:
        self.current_task_id = None
        self.status = AgentStatus.IDLE

    def assign_task(self, task_id: UUID) -> None:
        self.current_task_id = task_id
        self.status = AgentStatus.WORKING
```

### Task

```python
# domain/entities/task.py
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from uuid import UUID
from datetime import datetime

class TaskStatus(str, Enum):
    BACKLOG     = "backlog"
    TODO        = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW   = "in_review"
    DONE        = "done"
    BLOCKED     = "blocked"

class Priority(str, Enum):
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"
    URGENT = "urgent"

@dataclass
class Task:
    id:          UUID
    title:       str
    description: str
    status:      TaskStatus = TaskStatus.BACKLOG
    priority:    Priority   = Priority.MEDIUM
    assigned_to: Optional[UUID] = None
    created_by:  Optional[UUID] = None
    sprint_id:   Optional[UUID] = None
    result:      Optional[str]  = None
    created_at:  datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def assign(self, agent_id: UUID) -> None:
        self.assigned_to = agent_id
        self.status = TaskStatus.IN_PROGRESS

    def complete(self, result: str) -> None:
        self.result = result
        self.status = TaskStatus.DONE
        self.completed_at = datetime.utcnow()
```

### Artifact

```python
# domain/entities/artifact.py
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from uuid import UUID
from datetime import datetime

class ArtifactType(str, Enum):
    BACKLOG          = "backlog"
    SPRINT_PLANNING  = "sprint_planning"
    ADR              = "adr"
    DESIGN_DOC       = "design_doc"
    IMPLEMENTATION   = "implementation"
    TEST_PLAN        = "test_plan"
    BUG_REPORT       = "bug_report"
    ANALYSIS         = "analysis"
    RETROSPECTIVE    = "retrospective"
    USER_STORY       = "user_story"
    ONBOARDING       = "onboarding"

class ArtifactStatus(str, Enum):
    DRAFT     = "draft"
    IN_REVIEW = "in_review"
    APPROVED  = "approved"
    ARCHIVED  = "archived"

@dataclass
class Artifact:
    id:          UUID
    title:       str
    content:     str
    type:        ArtifactType
    path:        str           # ex: workspace/projects/sprint-1/backlog.md
    author_id:   UUID
    sprint_id:   Optional[UUID] = None
    status:      ArtifactStatus = ArtifactStatus.DRAFT
    created_at:  datetime = field(default_factory=datetime.utcnow)
    updated_at:  datetime = field(default_factory=datetime.utcnow)

    def approve(self) -> None:
        self.status = ArtifactStatus.APPROVED
        self.updated_at = datetime.utcnow()
```

---

## 🔌 Interfaces (Contratos)

```python
# domain/interfaces/llm_interface.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class LLMResponse:
    thought:   str
    action:    str
    target:    Optional[str]
    tool_call: Optional[dict]
    raw:       str

class ILLMAdapter(ABC):
    @abstractmethod
    async def think(self, system_prompt: str, context: str) -> LLMResponse:
        """Envia contexto para o LLM e retorna resposta estruturada."""
        ...

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Gera embedding vetorial para busca semântica."""
        ...
```

```python
# domain/interfaces/message_bus.py
from abc import ABC, abstractmethod
from typing import Callable, Awaitable

class IMessageBus(ABC):
    @abstractmethod
    async def publish(self, topic: str, payload: dict, qos: int = 1) -> None:
        """Publica mensagem em um tópico."""
        ...

    @abstractmethod
    async def subscribe(self, topic: str, handler: Callable[[dict], Awaitable[None]]) -> None:
        """Assina um tópico e registra handler assíncrono."""
        ...
```

---

## 📁 Estrutura do Frontend

```
frontend/
├── src/
│   ├── core/
│   │   ├── mqtt/
│   │   │   ├── MqttClient.ts          # Wrapper sobre mqtt.min.js
│   │   │   ├── topics.ts              # Constantes de tópicos MQTT
│   │   │   └── useMqtt.ts             # Hook React para MQTT
│   │   │
│   │   └── store/
│   │       ├── agentsStore.ts         # Zustand: estado dos agentes
│   │       ├── tasksStore.ts          # Zustand: estado das tarefas
│   │       ├── artifactsStore.ts      # Zustand: artefatos disponíveis
│   │       └── sprintStore.ts         # Zustand: sprint atual
│   │
│   ├── features/
│   │   ├── office/
│   │   │   ├── OfficeCanvas.tsx       # Phaser.js (pixel-art)
│   │   │   └── useOfficeSync.ts       # Sincroniza MQTT → Phaser
│   │   │
│   │   ├── agents/
│   │   │   ├── AgentInspector.tsx     # Painel de detalhes do agente
│   │   │   ├── AgentPulseBoard.tsx    # Status em tempo real
│   │   │   └── AgentCard.tsx          # Card individual
│   │   │
│   │   ├── tasks/
│   │   │   ├── TaskBoard.tsx          # Kanban arrastável
│   │   │   ├── TaskCard.tsx           # Card de tarefa
│   │   │   └── TaskForm.tsx           # Formulário de nova tarefa
│   │   │
│   │   ├── artifacts/
│   │   │   ├── ArtifactViewer.tsx     # Visualizador Markdown
│   │   │   ├── ArtifactList.tsx       # Lista de artefatos do sprint
│   │   │   └── ArtifactBadge.tsx      # Badge de status (draft/approved)
│   │   │
│   │   ├── chat/
│   │   │   ├── ChatPanel.tsx          # Feed de mensagens entre agentes
│   │   │   └── MessageBubble.tsx      # Balão de mensagem
│   │   │
│   │   └── sprint/
│   │       ├── SprintPanel.tsx        # Painel do sprint atual
│   │       └── CeremonyLog.tsx        # Log de cerimônias
│   │
│   └── shared/
│       ├── components/
│       │   ├── FloatingPanel.tsx      # Painel arrastável genérico
│       │   ├── MarkdownRenderer.tsx   # Renderizador MD
│       │   └── StatusBadge.tsx        # Badge de status genérico
│       └── hooks/
│           ├── useFloatingPanel.ts
│           └── useKeyboardShortcuts.ts
│
├── index.html
├── vite.config.ts
├── tsconfig.json
└── package.json
```

---

## 🔑 Princípios SOLID Aplicados

### S — Single Responsibility
Cada classe/módulo tem uma única razão para mudar:
- `AgentThinkUseCase` — apenas orquestra o ciclo de pensamento
- `OllamaAdapter` — apenas se comunica com Ollama
- `MqttMessageBus` — apenas publica/assina mensagens

### O — Open/Closed
Novos papéis de agentes são adicionados sem modificar código existente:
```python
# Adicionar novo papel = criar novo arquivo de prompt
# Não modifica AgentThinkUseCase
ROLE_PROMPTS = {
    Role.DEV_SENIOR: load_prompt("dev_senior.md"),
    Role.QA_ENGINEER: load_prompt("qa_engineer.md"),
    # Novo papel: apenas adicionar aqui
    Role.DEVOPS: load_prompt("devops.md"),
}
```

### L — Liskov Substitution
`OllamaAdapter` e `OpenAIAdapter` são intercambiáveis:
```python
# Funciona com qualquer implementação de ILLMAdapter
use_case = AgentThinkUseCase(llm=OllamaAdapter(...))
use_case = AgentThinkUseCase(llm=OpenAIAdapter(...))
use_case = AgentThinkUseCase(llm=MockLLMAdapter(...))  # Para testes
```

### I — Interface Segregation
Interfaces pequenas e focadas:
```python
class ILLMAdapter(ABC):       # Apenas think() e embed()
class IMessageBus(ABC):       # Apenas publish() e subscribe()
class IMemoryRepository(ABC): # Apenas save() e recall()
```

### D — Dependency Inversion
Use cases dependem de abstrações, não de implementações:
```python
class AgentThinkUseCase:
    def __init__(
        self,
        llm: ILLMAdapter,           # Interface, não OllamaAdapter
        message_bus: IMessageBus,   # Interface, não MqttMessageBus
        memory_repo: IMemoryRepository,
    ):
        self._llm = llm
        self._bus = message_bus
        self._memory = memory_repo
```

---

## ✅ Checklist da Fase 1

- [ ] Estrutura de pastas do backend criada
- [ ] Entidades do domínio implementadas (`Agent`, `Task`, `Artifact`, `Message`, `Sprint`)
- [ ] Value Objects implementados (`AgentId`, `TaskId`, `MqttTopic`, `ArtifactPath`)
- [ ] Interfaces (contratos) definidas (`ILLMAdapter`, `IMessageBus`, `IMemoryRepository`, etc.)
- [ ] Eventos de domínio definidos
- [ ] Estrutura do frontend criada
- [ ] Zustand stores criados (agentes, tarefas, artefatos, sprint)
- [ ] `FloatingPanel` genérico implementado
- [ ] Injeção de dependência configurada no FastAPI (`dependencies.py`)
- [ ] `pyproject.toml` com todas as dependências
- [ ] `Dockerfile` do backend
- [ ] `Dockerfile` do frontend
