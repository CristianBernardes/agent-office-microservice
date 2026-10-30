# Fase 0 — Fundação: ADRs, RFCs e Design Docs

> Antes de escrever uma linha de código, toda decisão arquitetural relevante deve ser documentada. Esta fase garante que o time (ou você no futuro) entenda **por que** cada escolha foi feita, não apenas **o que** foi feito.

---

## 🎯 Objetivo

Estabelecer a base documental do projeto:

- **ADRs** (Architecture Decision Records) — decisões pontuais e irreversíveis
- **RFCs** (Request for Comments) — propostas que impactam múltiplos componentes
- **Design Docs** — visão geral de subsistemas complexos

---

## 📁 Estrutura de Documentos

```
docs/
├── adr/
│   ├── 001-mqtt-como-barramento-de-mensagens.md
│   ├── 002-python-fastapi-no-backend.md
│   ├── 003-modelo-de-agentes-por-papel.md
│   ├── 004-artefatos-em-markdown.md
│   ├── 005-multiplos-modelos-ollama-por-agente.md
│   ├── 006-postgresql-com-pgvector.md
│   ├── 007-clean-architecture-no-backend.md
│   └── 008-zustand-para-estado-frontend.md
│
├── rfc/
│   ├── rfc-001-protocolo-de-comunicacao-entre-agentes.md
│   ├── rfc-002-sistema-de-artefatos.md
│   └── rfc-003-ciclo-de-vida-de-um-agente.md
│
└── design/
    ├── arquitetura-geral.md
    ├── modelo-de-dominio.md
    └── fluxo-de-mensagens.md
```

---

## 📄 Template de ADR

Cada ADR segue este formato:

```markdown
# ADR-XXX — Título da Decisão

**Status:** Proposto | Aceito | Depreciado | Substituído por ADR-YYY
**Data:** YYYY-MM-DD
**Autores:** Nome(s)

## Contexto
O que motivou esta decisão? Qual problema estamos resolvendo?

## Decisão
O que decidimos fazer?

## Consequências
### Positivas
- ...

### Negativas / Trade-offs
- ...

## Alternativas Consideradas
| Alternativa | Por que foi descartada |
|-------------|----------------------|
| ...         | ...                  |
```

---

## 📄 ADR-001 — MQTT como Barramento de Mensagens

**Status:** Aceito  
**Data:** 2026-10-29

### Contexto
Os agentes precisam se comunicar de forma assíncrona e desacoplada. O sistema atual usa Colyseus (WebSocket com estado compartilhado), o que cria acoplamento forte entre agentes e servidor.

### Decisão
Usar **MQTT** (via Mosquitto broker) como barramento de mensagens entre agentes. O frontend se conecta via `mqtt.min.js` e o backend via `aiomqtt` (Python async).

### Consequências
**Positivas:**
- Desacoplamento total entre agentes — cada um publica e assina tópicos independentemente
- Escalável: novos agentes entram sem alterar código existente
- Observabilidade: qualquer cliente MQTT pode monitorar todos os eventos
- Frontend recebe eventos em tempo real sem polling

**Negativas:**
- Requer um broker MQTT rodando (Mosquitto via Docker)
- Curva de aprendizado para modelagem de tópicos
- Mensagens são fire-and-forget por padrão (QoS 0) — precisa de QoS 1 para garantias

### Alternativas Consideradas
| Alternativa | Por que foi descartada |
|-------------|----------------------|
| Colyseus (atual) | Acoplamento forte, difícil de escalar, não é padrão de mercado |
| Redis Pub/Sub | Mais pesado, requer Redis rodando, menos adequado para IoT/eventos |
| WebSocket puro | Sem roteamento de tópicos, implementação manual complexa |
| Kafka | Overkill para este volume, complexidade operacional alta |

---

## 📄 ADR-002 — Python + FastAPI no Backend

**Status:** Aceito  
**Data:** 2026-10-29

### Contexto
O backend atual é Node.js/TypeScript com Colyseus. Precisamos de uma stack que se integre melhor com o ecossistema de IA/LLM e permita evolução futura com RAG, embeddings e ferramentas de ML.

### Decisão
Reescrever o backend em **Python 3.12 + FastAPI** com suporte a async nativo.

### Consequências
**Positivas:**
- Ecossistema de IA imbatível: `ollama`, `langchain`, `llama-index`, `sentence-transformers`
- FastAPI tem suporte nativo a WebSocket e async
- Tipagem forte com Pydantic v2
- Testes com pytest são maduros e bem documentados
- Integração direta com pgvector para embeddings

**Negativas:**
- Reescrita completa do backend
- GIL do Python pode ser limitante em alta concorrência (mitigado com async)

### Alternativas Consideradas
| Alternativa | Por que foi descartada |
|-------------|----------------------|
| Manter Node.js | Ecossistema de IA inferior, Colyseus cria acoplamento |
| Go | Performance superior, mas ecossistema de IA muito inferior |
| Rust | Overkill, curva de aprendizado altíssima |

---

## 📄 ADR-003 — Modelo de Agentes por Papel

**Status:** Aceito  
**Data:** 2026-10-29

### Contexto
O sistema atual tem apenas dois agentes fixos (Alice/Engineer e Bob/PM). Precisamos de um modelo extensível que suporte múltiplos papéis de um time de TI real.

### Decisão
Cada agente é definido por um **Role** (papel) que determina:
- System prompt especializado
- Ferramentas disponíveis
- Artefatos que pode produzir
- Modelo LLM configurável via `.env`

### Papéis Definidos
| Role | Responsabilidade Principal |
|------|---------------------------|
| `PRODUCT_OWNER` | Backlog, user stories, priorização |
| `SCRUM_MASTER` | Cerimônias, impedimentos, retrospectivas |
| `TECH_LEAD` | Arquitetura, ADRs, decisões técnicas |
| `DEV_SENIOR` | Implementação, code review, mentoria |
| `DEV_JUNIOR` | Tarefas simples, aprendizado |
| `QA_ENGINEER` | Planos de teste, bug reports |
| `DATA_ANALYST` | Métricas, KPIs, análises |
| `HR_MANAGER` | Onboarding, cultura, contratações |
| `PRODUCT_CONSULTANT` | Validação de mercado, pesquisa |

---

## 📄 ADR-004 — Artefatos em Markdown

**Status:** Aceito  
**Data:** 2026-10-29

### Contexto
Os agentes precisam produzir saídas tangíveis e persistentes, não apenas logs de conversa.

### Decisão
Todo agente pode produzir **arquivos `.md`** salvos em `workspace/projects/{sprint}/`. O frontend exibe esses arquivos em tempo real via visualizador Markdown.

### Estrutura de Artefatos
```
workspace/projects/{sprint-name}/
├── backlog.md              # PO
├── sprint-planning.md      # Scrum Master
├── adr-*.md                # Tech Lead
├── design-doc-*.md         # Tech Lead
├── implementacao-*.md      # Dev Sênior/Júnior
├── test-plan-*.md          # QA
├── bug-report-*.md         # QA
├── analise-*.md            # Analista de Dados
└── retrospectiva.md        # Scrum Master
```

---

## 📄 RFC-001 — Protocolo de Comunicação entre Agentes

**Status:** Proposto  
**Data:** 2026-10-29

### Resumo
Define o protocolo de mensagens MQTT entre agentes: estrutura de tópicos, formato de payload e regras de QoS.

### Topologia de Tópicos

```
office/
├── agents/{agentId}/
│   ├── thought          # Pensamento interno do agente (QoS 0)
│   ├── action           # Ação executada (QoS 1)
│   ├── message          # Mensagem para outro agente (QoS 1)
│   └── status           # idle | thinking | working | offline (QoS 1, retain=true)
│
├── tasks/
│   ├── created          # Nova tarefa criada (QoS 1)
│   ├── assigned         # Tarefa atribuída a agente (QoS 1)
│   ├── updated          # Status da tarefa atualizado (QoS 1)
│   └── completed        # Tarefa concluída (QoS 1)
│
├── artifacts/
│   ├── created          # Novo artefato .md gerado (QoS 1)
│   └── updated          # Artefato atualizado (QoS 1)
│
├── sprint/
│   ├── started          # Sprint iniciado (QoS 1, retain=true)
│   ├── ended            # Sprint encerrado (QoS 1)
│   └── ceremony/{type}  # planning | review | retro | standup (QoS 1)
│
└── office/
    ├── agent_hired      # Novo agente contratado (QoS 1)
    └── agent_left       # Agente saiu do escritório (QoS 1)
```

### Formato de Payload

```json
{
  "event_id": "uuid-v4",
  "timestamp": "2026-10-29T19:00:00Z",
  "agent_id": "alice",
  "agent_role": "DEV_SENIOR",
  "payload": {
    "type": "thought | action | message | status",
    "content": "...",
    "target_agent_id": "bob",   // opcional
    "task_id": "uuid",          // opcional
    "artifact_path": "..."      // opcional
  }
}
```

### Regras de QoS
- **QoS 0** — Pensamentos internos (podem ser perdidos sem problema)
- **QoS 1** — Ações, mensagens, tarefas (pelo menos uma entrega)
- **retain=true** — Status de agentes e sprint atual (novos clientes recebem o último estado)

---

## 📄 RFC-002 — Sistema de Artefatos

**Status:** Proposto  
**Data:** 2026-10-29

### Resumo
Define como agentes criam, atualizam e referenciam artefatos Markdown, incluindo o ciclo de vida de um artefato e como o frontend os exibe.

### Ciclo de Vida

```
DRAFT → IN_REVIEW → APPROVED → ARCHIVED
```

1. Agente usa ferramenta `write_artifact(path, content, status="DRAFT")`
2. Outro agente pode usar `review_artifact(path, comment)`
3. Tech Lead ou PO usa `approve_artifact(path)`
4. Artefatos aprovados ficam no histórico do sprint

### Ferramentas Disponíveis por Papel

| Ferramenta | Quem pode usar |
|-----------|----------------|
| `write_artifact` | Todos |
| `read_artifact` | Todos |
| `review_artifact` | Tech Lead, QA, PO |
| `approve_artifact` | Tech Lead, PO |
| `list_artifacts` | Todos |

---

## 📄 Design Doc — Arquitetura Geral

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Phaser.js   │  │  Painéis UI  │  │  Artifact Viewer     │  │
│  │  (pixel-art) │  │  (React)     │  │  (Markdown render)   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         └─────────────────┴──────────────────────┘              │
│                            │                                      │
│                    ┌───────▼────────┐                            │
│                    │  Zustand Store │                            │
│                    └───────┬────────┘                            │
│                            │                                      │
│              ┌─────────────┴──────────────┐                     │
│              │                            │                      │
│     ┌────────▼────────┐        ┌──────────▼──────────┐         │
│     │  MQTT Client    │        │  WebSocket Client   │         │
│     │  (mqtt.min.js)  │        │  (FastAPI WS)       │         │
│     └────────┬────────┘        └──────────┬──────────┘         │
└──────────────┼─────────────────────────────┼────────────────────┘
               │                             │
    ┌──────────▼──────────┐      ┌───────────▼──────────────┐
    │   MQTT Broker       │      │   Backend (FastAPI)       │
    │   (Mosquitto)       │      │                           │
    │                     │      │  ┌─────────────────────┐ │
    │  office/agents/+/# ◄├──────┤  │  Agent Think Loop   │ │
    │  office/tasks/#    ◄├──────┤  │  (asyncio tasks)    │ │
    │  office/artifacts/# │      │  └──────────┬──────────┘ │
    └──────────┬──────────┘      │             │             │
               │                 │  ┌──────────▼──────────┐ │
               └─────────────────►  │  MQTT Publisher     │ │
                                 │  └─────────────────────┘ │
                                 │                           │
                                 │  ┌─────────────────────┐ │
                                 │  │  LLM Adapters       │ │
                                 │  │  (Ollama/OpenAI)    │ │
                                 │  └──────────┬──────────┘ │
                                 │             │             │
                                 │  ┌──────────▼──────────┐ │
                                 │  │  PostgreSQL         │ │
                                 │  │  + pgvector         │ │
                                 │  └─────────────────────┘ │
                                 └───────────────────────────┘
```

---

## ✅ Checklist da Fase 0

- [ ] ADR-001: MQTT como barramento
- [ ] ADR-002: Python + FastAPI
- [ ] ADR-003: Modelo de agentes por papel
- [ ] ADR-004: Artefatos em Markdown
- [ ] ADR-005: Múltiplos modelos por agente
- [ ] ADR-006: PostgreSQL + pgvector
- [ ] ADR-007: Clean Architecture no backend
- [ ] ADR-008: Zustand para estado frontend
- [ ] RFC-001: Protocolo de comunicação entre agentes
- [ ] RFC-002: Sistema de artefatos
- [ ] RFC-003: Ciclo de vida de um agente
- [ ] Design Doc: Arquitetura geral
- [ ] Design Doc: Modelo de domínio
- [ ] Design Doc: Fluxo de mensagens
