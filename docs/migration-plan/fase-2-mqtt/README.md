# Fase 2 — MQTT: Barramento de Mensagens entre Agentes

> O MQTT substitui o Colyseus como mecanismo de comunicação. Cada agente publica e assina tópicos independentemente, criando um sistema completamente desacoplado onde novos agentes entram sem alterar código existente.

---

## 🎯 Objetivo

- Configurar o broker MQTT (Mosquitto) via Docker
- Definir a topologia completa de tópicos
- Implementar o cliente MQTT no backend (Python/aiomqtt)
- Implementar o cliente MQTT no frontend (mqtt.min.js)
- Garantir que o frontend receba todos os eventos em tempo real

---

## 🏗️ Infraestrutura

### Mosquitto via Docker Compose

```yaml
# docker-compose.yml (trecho)
services:
  mqtt:
    image: eclipse-mosquitto:2.0
    container_name: agent-office-mqtt
    restart: unless-stopped
    ports:
      - "1883:1883"    # MQTT padrão
      - "9001:9001"    # WebSocket (para o frontend)
    volumes:
      - ./docker/mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf
      - ./docker/mosquitto/passwd:/mosquitto/config/passwd
    healthcheck:
      test: ["CMD", "mosquitto_pub", "-h", "localhost", "-t", "health", "-m", "ok"]
      interval: 5s
      timeout: 3s
      retries: 5
```

```
# docker/mosquitto/mosquitto.conf
listener 1883
listener 9001
protocol websockets

allow_anonymous true   # Desenvolvimento — usar autenticação em produção

# Persistência de mensagens retain
persistence true
persistence_location /mosquitto/data/

# Logs
log_dest stdout
log_type all
```

> **Por que porta 9001?** O frontend (browser) não pode usar TCP puro. O Mosquitto expõe MQTT sobre WebSocket na porta 9001, que o `mqtt.min.js` usa nativamente.

---

## 📡 Topologia de Tópicos

### Convenção de nomenclatura

```
{namespace}/{recurso}/{id}/{evento}
```

- Namespace: `office`
- Recursos: `agents`, `tasks`, `artifacts`, `sprint`
- Wildcards: `+` (um nível), `#` (múltiplos níveis)

### Mapa completo de tópicos

```
office/
│
├── agents/
│   ├── {agentId}/thought        # Pensamento interno (QoS 0)
│   ├── {agentId}/action         # Ação executada (QoS 1)
│   ├── {agentId}/message        # Mensagem para outro agente (QoS 1)
│   ├── {agentId}/status         # idle|thinking|working|talking|offline (QoS 1, retain)
│   ├── {agentId}/tool_call      # Ferramenta sendo executada (QoS 1)
│   └── {agentId}/tool_result    # Resultado da ferramenta (QoS 1)
│
├── tasks/
│   ├── created                  # Nova tarefa criada (QoS 1)
│   ├── assigned                 # Tarefa atribuída (QoS 1)
│   ├── updated                  # Status atualizado (QoS 1)
│   ├── completed                # Tarefa concluída (QoS 1)
│   └── blocked                  # Tarefa bloqueada (QoS 1)
│
├── artifacts/
│   ├── created                  # Novo artefato .md (QoS 1)
│   ├── updated                  # Artefato atualizado (QoS 1)
│   ├── review_requested         # Revisão solicitada (QoS 1)
│   └── approved                 # Artefato aprovado (QoS 1)
│
├── sprint/
│   ├── started                  # Sprint iniciado (QoS 1, retain)
│   ├── ended                    # Sprint encerrado (QoS 1)
│   ├── ceremony/planning        # Cerimônia: planning (QoS 1)
│   ├── ceremony/review          # Cerimônia: review (QoS 1)
│   ├── ceremony/retro           # Cerimônia: retrospectiva (QoS 1)
│   └── ceremony/standup         # Cerimônia: daily standup (QoS 1)
│
└── office/
    ├── agent_hired              # Novo agente contratado (QoS 1)
    └── agent_left               # Agente saiu (QoS 1)
```

---

## 📦 Formato de Payload

Todos os payloads seguem o mesmo envelope JSON:

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-10-29T19:00:00.000Z",
  "version": "1.0",
  "agent_id": "alice",
  "agent_role": "dev_senior",
  "payload": { }
}
```

### Exemplos por tópico

**`office/agents/alice/thought`**
```json
{
  "event_id": "...",
  "timestamp": "...",
  "agent_id": "alice",
  "agent_role": "dev_senior",
  "payload": {
    "thought": "Preciso analisar os requisitos da tarefa de autenticação antes de propor uma solução.",
    "context_summary": "Sprint 1, tarefa: Implementar login"
  }
}
```

**`office/agents/alice/action`**
```json
{
  "event_id": "...",
  "timestamp": "...",
  "agent_id": "alice",
  "agent_role": "dev_senior",
  "payload": {
    "action": "write_artifact",
    "description": "Escrevendo design doc para o módulo de autenticação",
    "tool_call": {
      "tool": "write_artifact",
      "args": {
        "path": "workspace/projects/sprint-1/design-doc-auth.md",
        "type": "design_doc",
        "title": "Design Doc — Autenticação JWT"
      }
    }
  }
}
```

**`office/agents/alice/message`**
```json
{
  "event_id": "...",
  "timestamp": "...",
  "agent_id": "alice",
  "agent_role": "dev_senior",
  "payload": {
    "target_agent_id": "bob",
    "target_agent_role": "product_owner",
    "message": "Bob, o design doc de autenticação está pronto para revisão. Usei JWT com refresh token — precisamos definir o tempo de expiração com o cliente.",
    "requires_response": true
  }
}
```

**`office/tasks/assigned`**
```json
{
  "event_id": "...",
  "timestamp": "...",
  "agent_id": "scrum_master",
  "agent_role": "scrum_master",
  "payload": {
    "task_id": "uuid",
    "task_title": "Implementar tela de login",
    "assigned_to": "alice",
    "assigned_role": "dev_senior",
    "priority": "high",
    "sprint_id": "sprint-1"
  }
}
```

**`office/artifacts/created`**
```json
{
  "event_id": "...",
  "timestamp": "...",
  "agent_id": "alice",
  "agent_role": "dev_senior",
  "payload": {
    "artifact_id": "uuid",
    "title": "Design Doc — Autenticação JWT",
    "type": "design_doc",
    "path": "workspace/projects/sprint-1/design-doc-auth.md",
    "status": "draft",
    "sprint_id": "sprint-1"
  }
}
```

---

## 🐍 Implementação Backend (Python)

### IMessageBus (interface)

```python
# domain/interfaces/message_bus.py
from abc import ABC, abstractmethod
from typing import Callable, Awaitable, Any

class IMessageBus(ABC):
    @abstractmethod
    async def publish(
        self,
        topic: str,
        payload: dict,
        qos: int = 1,
        retain: bool = False
    ) -> None: ...

    @abstractmethod
    async def subscribe(
        self,
        topic: str,
        handler: Callable[[str, dict], Awaitable[None]]
    ) -> None: ...

    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...
```

### MqttMessageBus (implementação)

```python
# infrastructure/messaging/mqtt_message_bus.py
import json
import uuid
from datetime import datetime, timezone
from typing import Callable, Awaitable

import aiomqtt

from domain.interfaces.message_bus import IMessageBus


class MqttMessageBus(IMessageBus):
    def __init__(self, host: str, port: int = 1883):
        self._host = host
        self._port = port
        self._client: aiomqtt.Client | None = None
        self._handlers: dict[str, list[Callable]] = {}

    async def connect(self) -> None:
        self._client = aiomqtt.Client(self._host, self._port)
        await self._client.__aenter__()

    async def disconnect(self) -> None:
        if self._client:
            await self._client.__aexit__(None, None, None)

    async def publish(
        self,
        topic: str,
        payload: dict,
        qos: int = 1,
        retain: bool = False
    ) -> None:
        if not self._client:
            raise RuntimeError("MQTT client not connected")

        message = json.dumps(payload, default=str)
        await self._client.publish(topic, message, qos=qos, retain=retain)

    async def subscribe(
        self,
        topic: str,
        handler: Callable[[str, dict], Awaitable[None]]
    ) -> None:
        if topic not in self._handlers:
            self._handlers[topic] = []
        self._handlers[topic].append(handler)

        if self._client:
            await self._client.subscribe(topic)

    def _build_envelope(self, agent_id: str, agent_role: str, payload: dict) -> dict:
        return {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
            "agent_id": agent_id,
            "agent_role": agent_role,
            "payload": payload,
        }
```

### Publicando eventos de agente

```python
# application/agents/think_use_case.py
from domain.interfaces.llm_interface import ILLMAdapter
from domain.interfaces.message_bus import IMessageBus
from domain.entities.agent import Agent

TOPICS = {
    "thought":     "office/agents/{agent_id}/thought",
    "action":      "office/agents/{agent_id}/action",
    "status":      "office/agents/{agent_id}/status",
    "tool_call":   "office/agents/{agent_id}/tool_call",
    "tool_result": "office/agents/{agent_id}/tool_result",
}

class AgentThinkUseCase:
    def __init__(self, llm: ILLMAdapter, bus: IMessageBus):
        self._llm = llm
        self._bus = bus

    async def execute(self, agent: Agent, context: str) -> None:
        agent.start_thinking()

        # Publica status
        await self._bus.publish(
            topic=TOPICS["status"].format(agent_id=agent.id),
            payload={"status": "thinking"},
            qos=1,
            retain=True
        )

        # Chama LLM
        response = await self._llm.think(
            system_prompt=agent.system_prompt,
            context=context
        )

        # Publica pensamento (QoS 0 — pode ser perdido)
        await self._bus.publish(
            topic=TOPICS["thought"].format(agent_id=agent.id),
            payload={
                "agent_id": str(agent.id),
                "agent_role": agent.role.value,
                "payload": {"thought": response.thought}
            },
            qos=0
        )

        # Publica ação (QoS 1 — garantido)
        await self._bus.publish(
            topic=TOPICS["action"].format(agent_id=agent.id),
            payload={
                "agent_id": str(agent.id),
                "agent_role": agent.role.value,
                "payload": {
                    "action": response.action,
                    "tool_call": response.tool_call
                }
            },
            qos=1
        )
```

---

## ⚛️ Implementação Frontend (React + mqtt.min.js)

### MqttClient.ts

```typescript
// core/mqtt/MqttClient.ts
import mqtt, { MqttClient as IMqttClient } from 'mqtt';

type MessageHandler = (topic: string, payload: unknown) => void;

class MqttClient {
  private client: IMqttClient | null = null;
  private handlers = new Map<string, MessageHandler[]>();

  connect(brokerUrl: string): Promise<void> {
    return new Promise((resolve, reject) => {
      // Conecta via WebSocket (porta 9001)
      this.client = mqtt.connect(brokerUrl);

      this.client.on('connect', () => {
        console.log('[MQTT] Conectado ao broker');
        resolve();
      });

      this.client.on('error', reject);

      this.client.on('message', (topic, message) => {
        try {
          const payload = JSON.parse(message.toString());
          this.dispatch(topic, payload);
        } catch (e) {
          console.error('[MQTT] Payload inválido:', e);
        }
      });
    });
  }

  subscribe(topic: string, handler: MessageHandler): void {
    if (!this.handlers.has(topic)) {
      this.handlers.set(topic, []);
      this.client?.subscribe(topic);
    }
    this.handlers.get(topic)!.push(handler);
  }

  publish(topic: string, payload: unknown, qos: 0 | 1 = 1): void {
    this.client?.publish(topic, JSON.stringify(payload), { qos });
  }

  private dispatch(topic: string, payload: unknown): void {
    // Verifica handlers exatos
    this.handlers.get(topic)?.forEach(h => h(topic, payload));

    // Verifica wildcards (+)
    this.handlers.forEach((handlers, pattern) => {
      if (this.matchTopic(pattern, topic)) {
        handlers.forEach(h => h(topic, payload));
      }
    });
  }

  private matchTopic(pattern: string, topic: string): boolean {
    const patternParts = pattern.split('/');
    const topicParts = topic.split('/');

    for (let i = 0; i < patternParts.length; i++) {
      if (patternParts[i] === '#') return true;
      if (patternParts[i] !== '+' && patternParts[i] !== topicParts[i]) return false;
    }

    return patternParts.length === topicParts.length;
  }
}

export const mqttClient = new MqttClient();
```

### topics.ts

```typescript
// core/mqtt/topics.ts
export const TOPICS = {
  // Agentes
  agentThought:    (id: string) => `office/agents/${id}/thought`,
  agentAction:     (id: string) => `office/agents/${id}/action`,
  agentMessage:    (id: string) => `office/agents/${id}/message`,
  agentStatus:     (id: string) => `office/agents/${id}/status`,
  agentToolCall:   (id: string) => `office/agents/${id}/tool_call`,
  agentToolResult: (id: string) => `office/agents/${id}/tool_result`,
  allAgentActions: 'office/agents/+/action',
  allAgentStatus:  'office/agents/+/status',

  // Tarefas
  taskCreated:   'office/tasks/created',
  taskAssigned:  'office/tasks/assigned',
  taskUpdated:   'office/tasks/updated',
  taskCompleted: 'office/tasks/completed',

  // Artefatos
  artifactCreated:  'office/artifacts/created',
  artifactUpdated:  'office/artifacts/updated',
  artifactApproved: 'office/artifacts/approved',

  // Sprint
  sprintStarted:  'office/sprint/started',
  sprintEnded:    'office/sprint/ended',
  ceremony:       (type: string) => `office/sprint/ceremony/${type}`,

  // Escritório
  agentHired: 'office/office/agent_hired',
  agentLeft:  'office/office/agent_left',
} as const;
```

### useMqtt.ts (hook React)

```typescript
// core/mqtt/useMqtt.ts
import { useEffect } from 'react';
import { mqttClient } from './MqttClient';
import { useAgentsStore } from '../store/agentsStore';
import { useTasksStore } from '../store/tasksStore';
import { useArtifactsStore } from '../store/artifactsStore';
import { TOPICS } from './topics';

export function useMqttSync() {
  const { updateAgentStatus, addAgentThought, addAgentMessage } = useAgentsStore();
  const { addTask, updateTask, completeTask } = useTasksStore();
  const { addArtifact, updateArtifact } = useArtifactsStore();

  useEffect(() => {
    const brokerUrl = import.meta.env.VITE_MQTT_BROKER_URL ?? 'ws://localhost:9001';

    mqttClient.connect(brokerUrl).then(() => {
      // Status dos agentes (retain — recebe último estado ao conectar)
      mqttClient.subscribe(TOPICS.allAgentStatus, (_, payload: any) => {
        updateAgentStatus(payload.agent_id, payload.payload.status);
      });

      // Pensamentos
      mqttClient.subscribe('office/agents/+/thought', (_, payload: any) => {
        addAgentThought(payload.agent_id, payload.payload.thought);
      });

      // Mensagens entre agentes
      mqttClient.subscribe('office/agents/+/message', (_, payload: any) => {
        addAgentMessage(payload);
      });

      // Tarefas
      mqttClient.subscribe(TOPICS.taskCreated,   (_, p: any) => addTask(p.payload));
      mqttClient.subscribe(TOPICS.taskAssigned,  (_, p: any) => updateTask(p.payload));
      mqttClient.subscribe(TOPICS.taskCompleted, (_, p: any) => completeTask(p.payload.task_id));

      // Artefatos
      mqttClient.subscribe(TOPICS.artifactCreated, (_, p: any) => addArtifact(p.payload));
      mqttClient.subscribe(TOPICS.artifactUpdated, (_, p: any) => updateArtifact(p.payload));
    });
  }, []);
}
```

---

## 🔄 Fluxo Completo de uma Mensagem

```
1. AgentThinkUseCase (backend)
   └── LLM retorna: { thought, action: "send_message", target: "bob", content: "..." }

2. Backend publica em MQTT:
   └── office/agents/alice/message  →  { target: "bob", message: "..." }

3. Mosquitto broker distribui para todos os assinantes:
   ├── Backend (MqttSubscriber) → desperta Bob para responder
   └── Frontend (MqttClient)   → atualiza ChatPanel em tempo real

4. Bob recebe a mensagem:
   └── AgentThinkUseCase executa com contexto atualizado

5. Bob responde:
   └── office/agents/bob/message → { target: "alice", message: "..." }

6. Frontend atualiza:
   └── ChatPanel mostra a conversa em tempo real
   └── Phaser move os sprites para se aproximarem
```

---

## ✅ Checklist da Fase 2

- [ ] Mosquitto configurado no Docker Compose (portas 1883 e 9001)
- [ ] `mosquitto.conf` com WebSocket habilitado
- [ ] `IMessageBus` interface definida
- [ ] `MqttMessageBus` implementado com `aiomqtt`
- [ ] `InMemoryMessageBus` implementado para testes
- [ ] Todos os tópicos definidos em `topics.ts`
- [ ] `MqttClient.ts` com suporte a wildcards
- [ ] `useMqtt.ts` hook sincronizando stores Zustand
- [ ] Teste de integração: publicar → receber no frontend
- [ ] Teste de integração: agente A envia mensagem → agente B recebe
- [ ] Documentação do protocolo (RFC-001) atualizada
