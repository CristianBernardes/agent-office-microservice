# 🏗️ Plano de Migração — AgentOffice Pro

> Documento mestre do plano de evolução do AgentOffice de um fork melhorado para um produto original de simulação de times de TI com agentes de IA autônomos.

---

## 🎯 Visão do Produto

O **AgentOffice Pro** é um simulador de time de TI completo onde agentes de IA autônomos assumem papéis reais (PO, Scrum Master, Dev Sênior, Estagiário, QA, etc.), comunicam-se entre si via **MQTT**, produzem **artefatos reais em Markdown** e utilizam **múltiplos modelos de IA** configuráveis por agente — tudo renderizado em pixel-art em tempo real.

Deixa de ser um experimento e passa a ser um **produto de portfólio de alto nível**, demonstrando domínio de:

- Arquitetura limpa (Clean Architecture, SOLID, DRY, YAGNI)
- Design Patterns aplicados
- Injeção de Dependência
- Testes unitários e de integração
- Documentação técnica profissional (ADRs, RFCs, Design Docs)
- Mensageria assíncrona com MQTT
- Múltiplos modelos de LLM por agente

---

## 📋 Fases do Projeto

| Fase | Nome | Descrição | Arquivo |
|------|------|-----------|---------|
| **0** | Fundação | ADRs, RFCs, Design Docs, estrutura de decisões | [fase-0-fundacao/](./fase-0-fundacao/README.md) |
| **1** | Arquitetura | Nova stack, Clean Architecture, estrutura de pastas | [fase-1-arquitetura/](./fase-1-arquitetura/README.md) |
| **2** | MQTT | Barramento de mensagens, tópicos, fluxo entre agentes | [fase-2-mqtt/](./fase-2-mqtt/README.md) |
| **3** | Personas | Papéis, prompts especializados, ferramentas por papel | [fase-3-personas/](./fase-3-personas/README.md) |
| **4** | Artefatos | Sistema de geração de arquivos `.md` por agentes | [fase-4-artefatos/](./fase-4-artefatos/README.md) |
| **5** | Múltiplos Modelos | Configuração de LLM por agente, injeção de dependência | [fase-5-multiplos-modelos/](./fase-5-multiplos-modelos/README.md) |
| **6** | Testes | Estratégia de testes unitários, integração e e2e | [fase-6-testes/](./fase-6-testes/README.md) |
| **7** | Deploy | Docker, CI/CD, documentação final | [fase-7-deploy/](./fase-7-deploy/README.md) |
| **8** | Microserviços | Go Gateway + Kafka + Redis + Idempotência | [fase-8-microservicos/](./fase-8-microservicos/README.md) |

---

## 📅 Cronograma Macro

```
Semana 1  ████░░░░░░░░░░░░░░░░  Fase 0 — Fundação (ADRs, RFCs, Design Docs)
Semana 2  ░░░░████░░░░░░░░░░░░  Fase 1 — Arquitetura (domain, application, infra)
Semana 3  ░░░░░░░░████░░░░░░░░  Fase 2 — MQTT (broker, tópicos, fluxo)
Semana 4  ░░░░░░░░░░░░████░░░░  Fase 3 — Personas (papéis, prompts, ferramentas)
Semana 5  ████░░░░░░░░░░░░░░░░  Fase 4 — Artefatos (sistema de .md)
Semana 6  ░░░░████░░░░░░░░░░░░  Fase 5 — Múltiplos Modelos
Semana 7  ░░░░░░░░████░░░░░░░░  Fase 6 — Testes (unit, integration, e2e)
Semana 8  ░░░░░░░░░░░░████░░░░  Fase 7 — Deploy base
Semana 9  ░░░░░░░░░░░░░░░░████  Fase 8 — Go Gateway + Kafka + Idempotência
Semana 10 ████████████████████  Polish, documentação final, portfólio
```

---

## 🔑 Princípios Não Negociáveis

1. **Nenhuma lógica de negócio no framework** — FastAPI/React são apenas entregadores
2. **Toda dependência externa atrás de uma interface** — LLM, MQTT, banco, filesystem
3. **Testes antes do código** (TDD onde possível)
4. **Toda decisão arquitetural documentada** em ADR antes de implementar
5. **Nenhuma feature sem RFC** se impactar mais de um serviço
6. **Artefatos são cidadãos de primeira classe** — agentes produzem `.md` reais, não só logs

---

## 🛠️ Stack Final

| Camada | Tecnologia | Justificativa |
|--------|-----------|---------------|
| Backend IA | Python 3.12 + FastAPI | Ecossistema de IA, async nativo, tipagem forte |
| Gateway MQTT | **Go 1.22** | Alta performance, goroutines, binário único |
| Mensageria | **Kafka** (KRaft) | Exactly-once, ordenação por agente, replay |
| Broker MQTT | Mosquitto | Pub/Sub leve, WebSocket para o frontend |
| Idempotência | **Redis** | SET NX atômico, TTL automático |
| Banco | PostgreSQL 16 + pgvector | Memória semântica com embeddings reais |
| Frontend | React + Vite + Zustand | Reativo, leve, sem overhead desnecessário |
| Canvas | Phaser.js | Pixel-art validado |
| Testes | pytest + Go test | Padrão de cada linguagem |
| CI/CD | GitHub Actions | Integração com o repositório |
| Containers | Docker + Docker Compose | Deploy reproduzível |

---

## 📁 Estrutura Final do Repositório

```
agent-office-pro/
├── go-mqtt-gateway/            # Go — roteamento MQTT + Kafka + idempotência
│   ├── cmd/gateway/main.go
│   ├── internal/
│   │   ├── mqtt/               # Subscriber + Publisher
│   │   ├── kafka/              # Producer + Consumer (exactly-once)
│   │   ├── idempotency/        # Filtro Redis (SET NX)
│   │   ├── router/             # MQTT topic → Kafka topic
│   │   └── websocket/          # Hub para o frontend
│   ├── go.mod
│   └── Dockerfile
│
├── backend/                    # Python + FastAPI — lógica de agentes e IA
│   ├── src/
│   │   ├── domain/             # Entidades puras
│   │   ├── application/        # Casos de uso
│   │   ├── infrastructure/     # Kafka, Ollama, PostgreSQL
│   │   └── presentation/       # FastAPI routes
│   └── tests/
│
├── frontend/                   # React + Vite
│   └── src/
│       ├── core/               # MQTT client, Zustand stores
│       └── features/           # office, agents, tasks, artifacts
│
├── workspace/                  # Artefatos .md gerados pelos agentes
│   └── projects/
│
├── docker/
│   ├── mosquitto/mosquitto.conf
│   └── postgres/init.sql
│
├── docs/
│   └── migration-plan/         # Este documento
│
├── docker-compose.yml          # postgres + mqtt + redis + kafka + go-gateway + backend + frontend
├── .env.example
└── README.md
```
