# Fase 8 — Microserviços: Go + Kafka + Idempotência

> Esta fase eleva o projeto a uma arquitetura de microserviços de produção real. O Go assume o roteamento MQTT de alta performance entre agentes. O Kafka garante entrega confiável, ordenação e idempotência de mensagens. O Python foca exclusivamente na inteligência dos agentes.

---

## 🎯 Objetivo

- Introduzir o **Go MQTT Gateway** como microserviço de roteamento
- Introduzir o **Kafka** como barramento de eventos confiável
- Garantir **idempotência** em todas as operações críticas
- Definir contratos claros entre os serviços
- Manter o Python focado no que faz melhor: LLM e IA

---

## 🏛️ Arquitetura Final

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (React)                             │
│                    MQTT Client (mqtt.min.js) via WebSocket                │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │ ws://localhost:9001
                                    │
┌───────────────────────────────────▼──────────────────────────────────────┐
│                        GO MQTT GATEWAY                                    │
│                                                                           │
│  ┌─────────────────┐   ┌──────────────────┐   ┌──────────────────────┐  │
│  │  MQTT Broker    │   │  Message Router  │   │  WebSocket Hub       │  │
│  │  (Mosquitto)    │◄──│  (goroutines)    │──►│  (gorilla/websocket) │  │
│  │  :1883 / :9001  │   │                  │   │                      │  │
│  └────────┬────────┘   └────────┬─────────┘   └──────────────────────┘  │
│           │                     │                                         │
│           │              ┌──────▼──────────┐                             │
│           │              │  Idempotency    │                             │
│           │              │  Filter (Redis) │                             │
│           │              └──────┬──────────┘                             │
└───────────┼─────────────────────┼───────────────────────────────────────┘
            │                     │
            │              ┌──────▼──────────────────────────────────────┐
            │              │              KAFKA                           │
            │              │                                              │
            │              │  Topics:                                     │
            │              │  • agent-thoughts     (QoS: at-least-once)  │
            │              │  • agent-actions      (QoS: exactly-once)   │
            │              │  • agent-messages     (QoS: exactly-once)   │
            │              │  • task-events        (QoS: exactly-once)   │
            │              │  • artifact-events    (QoS: exactly-once)   │
            │              │  • sprint-events      (QoS: exactly-once)   │
            │              └──────┬──────────────────────────────────────┘
            │                     │
┌───────────┼─────────────────────▼───────────────────────────────────────┐
│           │         PYTHON AGENT SERVICE (FastAPI)                       │
│           │                                                               │
│  ┌────────▼────────┐   ┌──────────────────┐   ┌──────────────────────┐  │
│  │  Kafka Consumer │   │  Agent Think     │   │  Tool Executor       │  │
│  │  (aiokafka)     │──►│  Loop            │──►│  (write_artifact,    │  │
│  └─────────────────┘   │  (asyncio)       │   │   create_task, etc.) │  │
│                         └────────┬─────────┘   └──────────────────────┘  │
│                                  │                                         │
│                    ┌─────────────┴──────────────┐                        │
│                    │                            │                         │
│           ┌────────▼────────┐        ┌──────────▼──────────┐            │
│           │  Ollama (LLM)   │        │  PostgreSQL          │            │
│           │  :11434         │        │  + pgvector          │            │
│           └─────────────────┘        └─────────────────────┘            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 🐹 Go MQTT Gateway

### Responsabilidades

1. **Receber mensagens MQTT** dos agentes (Python publica, Go roteia)
2. **Filtrar duplicatas** via Redis (idempotência por `event_id`)
3. **Publicar no Kafka** com garantia de entrega (exactly-once)
4. **Consumir do Kafka** e reenviar via MQTT para o frontend
5. **WebSocket Hub** para o frontend (alternativa ao MQTT direto)

### Estrutura do Projeto Go

```
go-mqtt-gateway/
├── cmd/
│   └── gateway/
│       └── main.go              # Entrypoint
│
├── internal/
│   ├── mqtt/
│   │   ├── broker.go            # Conexão com Mosquitto
│   │   ├── subscriber.go        # Assina tópicos MQTT
│   │   └── publisher.go         # Publica no MQTT
│   │
│   ├── kafka/
│   │   ├── producer.go          # Publica no Kafka (exactly-once)
│   │   ├── consumer.go          # Consome do Kafka
│   │   └── topics.go            # Constantes de tópicos
│   │
│   ├── idempotency/
│   │   ├── filter.go            # Filtra duplicatas via Redis
│   │   └── redis_store.go       # Armazena event_ids processados
│   │
│   ├── router/
│   │   └── message_router.go    # Roteia MQTT → Kafka → MQTT
│   │
│   └── websocket/
│       ├── hub.go               # Hub de conexões WebSocket
│       └── client.go            # Cliente WebSocket individual
│
├── pkg/
│   ├── envelope/
│   │   └── envelope.go          # Estrutura padrão de mensagem
│   └── config/
│       └── config.go            # Configuração via env vars
│
├── go.mod
├── go.sum
└── Dockerfile
```

### Envelope de Mensagem (contrato compartilhado)

```go
// pkg/envelope/envelope.go
package envelope

import "time"

// Envelope é o contrato de mensagem entre todos os serviços.
// Todos os eventos trafegam neste formato.
type Envelope struct {
    EventID   string    `json:"event_id"`   // UUID v4 — chave de idempotência
    Timestamp time.Time `json:"timestamp"`
    Version   string    `json:"version"`    // "1.0"
    AgentID   string    `json:"agent_id"`
    AgentRole string    `json:"agent_role"`
    Payload   any       `json:"payload"`
}
```

### Filtro de Idempotência

```go
// internal/idempotency/filter.go
package idempotency

import (
    "context"
    "time"
    "github.com/redis/go-redis/v9"
)

const ttl = 24 * time.Hour  // event_ids ficam 24h no Redis

type Filter struct {
    redis *redis.Client
}

func NewFilter(rdb *redis.Client) *Filter {
    return &Filter{redis: rdb}
}

// IsNew retorna true se o event_id nunca foi visto.
// Usa SET NX (atômico) para garantir que dois workers
// não processem o mesmo evento simultaneamente.
func (f *Filter) IsNew(ctx context.Context, eventID string) (bool, error) {
    key := "idempotency:" + eventID
    ok, err := f.redis.SetNX(ctx, key, "1", ttl).Result()
    return ok, err
}
```

### Message Router

```go
// internal/router/message_router.go
package router

import (
    "context"
    "encoding/json"
    "log/slog"

    "github.com/cristian/agentoffice/pkg/envelope"
    "github.com/cristian/agentoffice/internal/idempotency"
    "github.com/cristian/agentoffice/internal/kafka"
)

// MQTT topic → Kafka topic
var topicMap = map[string]string{
    "office/agents/+/thought":    "agent-thoughts",
    "office/agents/+/action":     "agent-actions",
    "office/agents/+/message":    "agent-messages",
    "office/agents/+/status":     "agent-status",
    "office/tasks/created":       "task-events",
    "office/tasks/assigned":      "task-events",
    "office/tasks/completed":     "task-events",
    "office/artifacts/created":   "artifact-events",
    "office/artifacts/updated":   "artifact-events",
    "office/sprint/started":      "sprint-events",
    "office/sprint/ended":        "sprint-events",
}

type MessageRouter struct {
    idempotency *idempotency.Filter
    producer    *kafka.Producer
    logger      *slog.Logger
}

func NewMessageRouter(f *idempotency.Filter, p *kafka.Producer, l *slog.Logger) *MessageRouter {
    return &MessageRouter{idempotency: f, producer: p, logger: l}
}

// Route recebe uma mensagem MQTT e a roteia para o Kafka correto.
func (r *MessageRouter) Route(ctx context.Context, mqttTopic string, raw []byte) error {
    var env envelope.Envelope
    if err := json.Unmarshal(raw, &env); err != nil {
        return fmt.Errorf("envelope inválido: %w", err)
    }

    // Idempotência: ignora duplicatas
    isNew, err := r.idempotency.IsNew(ctx, env.EventID)
    if err != nil {
        return fmt.Errorf("erro no filtro de idempotência: %w", err)
    }
    if !isNew {
        r.logger.Info("evento duplicado ignorado", "event_id", env.EventID)
        return nil
    }

    // Resolve tópico Kafka
    kafkaTopic := r.resolveKafkaTopic(mqttTopic)
    if kafkaTopic == "" {
        r.logger.Warn("tópico MQTT sem mapeamento Kafka", "topic", mqttTopic)
        return nil
    }

    // Publica no Kafka com a chave sendo o agent_id (garante ordenação por agente)
    return r.producer.Publish(ctx, kafkaTopic, env.AgentID, raw)
}

func (r *MessageRouter) resolveKafkaTopic(mqttTopic string) string {
    // Resolve wildcards: office/agents/alice/action → office/agents/+/action
    for pattern, kafkaTopic := range topicMap {
        if matchTopic(pattern, mqttTopic) {
            return kafkaTopic
        }
    }
    return ""
}
```

### Kafka Producer (Exactly-Once)

```go
// internal/kafka/producer.go
package kafka

import (
    "context"
    "github.com/twmb/franz-go/pkg/kgo"
)

type Producer struct {
    client *kgo.Client
}

func NewProducer(brokers []string) (*Producer, error) {
    client, err := kgo.NewClient(
        kgo.SeedBrokers(brokers...),
        // Exactly-once semantics
        kgo.RequiredAcks(kgo.AllISRAcks()),
        kgo.ProducerBatchMaxBytes(1_000_000),
        // Idempotent producer (garante no-duplicates no Kafka)
        kgo.ProducerLinger(0),
    )
    if err != nil {
        return nil, err
    }
    return &Producer{client: client}, nil
}

// Publish publica uma mensagem no Kafka.
// key é usado para garantir ordenação (mesmo agente → mesma partição).
func (p *Producer) Publish(ctx context.Context, topic, key string, value []byte) error {
    record := &kgo.Record{
        Topic: topic,
        Key:   []byte(key),
        Value: value,
    }
    return p.client.ProduceSync(ctx, record).FirstErr()
}
```

---

## 📨 Kafka — Tópicos e Garantias

### Tópicos

| Tópico Kafka | Origem | Consumidor | Garantia | Partições |
|-------------|--------|-----------|---------|-----------|
| `agent-thoughts` | Go Gateway | Python (log) | at-least-once | 3 |
| `agent-actions` | Go Gateway | Python (executor) | **exactly-once** | 9 |
| `agent-messages` | Go Gateway | Python (think loop) | **exactly-once** | 9 |
| `agent-status` | Go Gateway | Frontend (via WS) | at-least-once | 3 |
| `task-events` | Python | Go (→ MQTT → frontend) | **exactly-once** | 6 |
| `artifact-events` | Python | Go (→ MQTT → frontend) | **exactly-once** | 6 |
| `sprint-events` | Python | Go + Frontend | **exactly-once** | 3 |

### Por que partições por agente?

```
Partição 0: alice (dev_senior)
Partição 1: bob (product_owner)
Partição 2: carol (scrum_master)
...
```

A chave de particionamento é o `agent_id`. Isso garante que **todas as mensagens de um agente chegam em ordem** ao consumidor — crítico para o loop de pensamento.

### Configuração Kafka (docker-compose)

```yaml
kafka:
  image: confluentinc/cp-kafka:7.6.0
  container_name: agentoffice-kafka
  restart: unless-stopped
  environment:
    KAFKA_NODE_ID: 1
    KAFKA_PROCESS_ROLES: broker,controller
    KAFKA_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
    KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
    KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
    KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
    KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
    # Exactly-once
    KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
    KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
  ports:
    - "9092:9092"
  healthcheck:
    test: ["CMD", "kafka-topics", "--bootstrap-server", "localhost:9092", "--list"]
    interval: 10s
    timeout: 5s
    retries: 10

redis:
  image: redis:7-alpine
  container_name: agentoffice-redis
  restart: unless-stopped
  ports:
    - "6379:6379"
  command: redis-server --save "" --appendonly no  # In-memory apenas
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 5s
    timeout: 3s
    retries: 5
```

---

## 🐍 Python — Consumindo do Kafka

```python
# infrastructure/messaging/kafka_consumer.py
import json
import asyncio
from aiokafka import AIOKafkaConsumer
from domain.interfaces.message_bus import IMessageBus


class KafkaAgentConsumer:
    """
    Consome mensagens do Kafka e despacha para o loop de pensamento dos agentes.
    Garante exactly-once via commit manual após processamento bem-sucedido.
    """

    def __init__(self, brokers: list[str], group_id: str):
        self._brokers = brokers
        self._group_id = group_id
        self._consumer: AIOKafkaConsumer | None = None

    async def start(self, topics: list[str]) -> None:
        self._consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self._brokers,
            group_id=self._group_id,
            enable_auto_commit=False,   # Commit manual — exactly-once
            auto_offset_reset="earliest",
            value_deserializer=lambda v: json.loads(v.decode()),
        )
        await self._consumer.start()

    async def consume(self, handler) -> None:
        """Consome mensagens e faz commit apenas após processamento bem-sucedido."""
        async for msg in self._consumer:
            try:
                await handler(msg.topic, msg.value)
                # Commit apenas após sucesso — garante exactly-once
                await self._consumer.commit()
            except Exception as e:
                # Não faz commit — mensagem será reprocessada
                print(f"[Kafka] Erro ao processar mensagem: {e}")
```

---

## 🔁 Idempotência — Onde Aplicar

### Regra geral

> **Toda operação que modifica estado deve ser idempotente.**
> Executar a mesma operação N vezes deve ter o mesmo resultado que executar 1 vez.

### Implementação por camada

| Operação | Chave de Idempotência | Onde verificar |
|---------|----------------------|----------------|
| Roteamento MQTT → Kafka | `event_id` (UUID) | Go Gateway (Redis) |
| Criação de tarefa | `event_id` do evento | Python (PostgreSQL) |
| Criação de artefato | `event_id` do evento | Python (PostgreSQL) |
| Contratação de agente | `agent_id` | Python (PostgreSQL) |
| Conclusão de tarefa | `task_id` + `agent_id` | Python (PostgreSQL) |

### Padrão no Python (PostgreSQL)

```python
# Usar INSERT ... ON CONFLICT DO NOTHING com event_id
async def save_task_idempotent(pool, event_id: str, task: Task) -> bool:
    """
    Retorna True se inseriu, False se já existia (duplicata ignorada).
    """
    async with pool.acquire() as conn:
        result = await conn.execute("""
            INSERT INTO tasks (id, title, description, status, event_id)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (event_id) DO NOTHING
        """, task.id, task.title, task.description, task.status.value, event_id)

        return result == "INSERT 0 1"
```

```sql
-- Coluna event_id em todas as tabelas de eventos
ALTER TABLE tasks      ADD COLUMN event_id UUID UNIQUE;
ALTER TABLE artifacts  ADD COLUMN event_id UUID UNIQUE;
ALTER TABLE memories   ADD COLUMN event_id UUID UNIQUE;
```

---

## 🐹 Dockerfile do Go Gateway

```dockerfile
# go-mqtt-gateway/Dockerfile
FROM golang:1.22-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o gateway ./cmd/gateway

# ─── Imagem final (binário único, ~10MB) ────────────────────────
FROM scratch

COPY --from=builder /app/gateway /gateway

EXPOSE 8080

ENTRYPOINT ["/gateway"]
```

---

## 📋 Docker Compose Atualizado

```yaml
services:

  postgres:   # ... (igual fase 7)
  mqtt:       # ... (igual fase 7)

  redis:
    image: redis:7-alpine
    container_name: agentoffice-redis
    ports: ["6379:6379"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s

  kafka:
    image: confluentinc/cp-kafka:7.6.0
    container_name: agentoffice-kafka
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
    ports: ["9092:9092"]
    healthcheck:
      test: ["CMD", "kafka-topics", "--bootstrap-server", "localhost:9092", "--list"]
      interval: 10s

  go-gateway:
    build:
      context: ./go-mqtt-gateway
      dockerfile: Dockerfile
    container_name: agentoffice-go-gateway
    restart: unless-stopped
    environment:
      MQTT_HOST:      mqtt
      MQTT_PORT:      "1883"
      KAFKA_BROKERS:  kafka:9092
      REDIS_URL:      redis:6379
      LOG_LEVEL:      info
    ports:
      - "8080:8080"   # WebSocket Hub para o frontend
    depends_on:
      mqtt:  { condition: service_healthy }
      kafka: { condition: service_healthy }
      redis: { condition: service_healthy }

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: agentoffice-backend
    environment:
      DATABASE_URL:    postgresql://agentoffice:agentoffice@postgres:5432/agentoffice
      KAFKA_BROKERS:   kafka:9092
      KAFKA_GROUP_ID:  agent-service
      MQTT_HOST:       mqtt
      OLLAMA_BASE_URL: http://172.17.0.1:11434
    depends_on:
      postgres: { condition: service_healthy }
      kafka:    { condition: service_healthy }

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports: ["5173:80"]
    depends_on:
      go-gateway: { condition: service_started }
      backend:    { condition: service_healthy }
```

---

## 📊 Fluxo Completo de uma Mensagem

```
1. Python publica no MQTT:
   office/agents/alice/message → { event_id: "uuid-1", ... }

2. Go Gateway recebe via MQTT subscriber

3. Go verifica idempotência no Redis:
   SET idempotency:uuid-1 1 EX 86400 NX
   → OK (novo evento)

4. Go publica no Kafka:
   topic: agent-messages
   key:   alice              ← garante ordenação por agente
   value: { event_id: "uuid-1", ... }

5. Python consome do Kafka (grupo: agent-service):
   → Desperta Bob para processar a mensagem
   → Commit manual após processamento bem-sucedido

6. Python publica resposta no MQTT:
   office/agents/bob/message → { event_id: "uuid-2", ... }

7. Go roteia uuid-2 para Kafka: agent-messages

8. Go também consome de task-events / artifact-events
   e republica no MQTT para o frontend:
   office/tasks/created → Frontend atualiza TaskBoard em tempo real
```

---

## ✅ Checklist da Fase 8

### Go Gateway
- [ ] Estrutura de projeto Go criada
- [ ] `Envelope` struct compartilhado
- [ ] Conexão MQTT com Mosquitto (`paho.mqtt.golang`)
- [ ] Filtro de idempotência com Redis (`SET NX`)
- [ ] Kafka Producer com exactly-once (`franz-go`)
- [ ] Kafka Consumer (Go consome `task-events`, `artifact-events` → republica no MQTT)
- [ ] WebSocket Hub para o frontend
- [ ] Mapeamento MQTT topic → Kafka topic
- [ ] `Dockerfile` multi-stage (binário ~10MB)
- [ ] Testes unitários: `MessageRouter`
- [ ] Testes unitários: `IdempotencyFilter`
- [ ] Testes de integração: MQTT → Kafka → MQTT

### Kafka
- [ ] Kafka no Docker Compose (KRaft mode, sem Zookeeper)
- [ ] Todos os tópicos criados com partições corretas
- [ ] Retenção configurada (7 dias)
- [ ] Exactly-once habilitado nos producers críticos

### Redis
- [ ] Redis no Docker Compose (in-memory, sem persistência)
- [ ] TTL de 24h nos event_ids
- [ ] Teste de concorrência: dois workers, mesmo event_id → apenas um processa

### Python
- [ ] `KafkaAgentConsumer` com commit manual
- [ ] `KafkaProducer` para publicar task-events e artifact-events
- [ ] Idempotência no PostgreSQL (`ON CONFLICT (event_id) DO NOTHING`)
- [ ] Coluna `event_id` em todas as tabelas de eventos

### Idempotência
- [ ] Todos os handlers verificam `event_id` antes de processar
- [ ] Teste: reenviar mesmo evento 3x → estado final idêntico a 1x
- [ ] Documentado no ADR-009: Estratégia de Idempotência
