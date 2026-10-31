# AgentOffice Microservice

**🌐 Language:** English · [🇧🇷 Português (BR)](./README.md)

> An IT office simulated by AI agents — each with its own role, personality and language model,
> collaborating in real time via MQTT to research, debate, decide and document, exactly like a
> real product/technology team would.

Give the team a product goal (e.g. *"build a niche SaaS to sell 5 units/day at $8"*) and watch the
agents think, research the market, debate with each other, and produce real artifacts — ADRs,
backlogs, test plans, market analyses — as versionable Markdown files, not just ephemeral logs.

**Open source** project, built from scratch following **Clean Architecture**, **SOLID**
principles, **Clean Code**, **DRY**, **YAGNI**, dependency injection, automated testing, and
rigorous architectural documentation (ADRs, RFCs, Design Docs).

---

## 💙 Before you clone or fork — help keep this project alive

This repository is **open source and free**, but it is maintained in the author's free time.
**Any donation amount is welcome** and directly helps cover **health costs and health insurance
for my family**, as well as keeping the time and energy available to keep developing AgentOffice.

If this project helped you, inspired you, or you simply want to see this idea grow well on
GitHub — please consider donating before you clone/fork below:

<table>
<tr>
<td align="center" width="260">

**🌍 PayPal (International)**

Donations via PayPal are very welcome, from anywhere in the world:

<a href="https://www.paypal.com/donate/?business=cristian.aob%40gmail.com&item_name=Support+the+AgentOffice+project&currency_code=USD">
  <img src="https://img.shields.io/badge/PayPal-Donate-00457C?style=for-the-badge&logo=paypal&logoColor=white" alt="Donate via PayPal" />
</a>

📧 Account: **cristian.aob@gmail.com**

</td>
<td align="center" width="260">

**🇧🇷 Pix (Brazil only)**

<img src="frontend/images/pix-qr-code.jpeg" alt="Pix QR Code for donations" width="220" />

Scan the QR Code with your Brazilian bank app

</td>
</tr>
</table>

Any donation, of any amount, helps keep my family's health covered and this project's idea
alive — thank you! 🙏

---

## The Team

Nine roles, each with its own system prompt, personality (Big Five traits), and set of allowed
tools:

| Role | Main responsibility |
|------|----------------------|
| **Product Owner** | Backlog, user stories, prioritization |
| **Scrum Master** | Ceremonies, impediments, retrospectives |
| **Tech Lead** | Architecture, ADRs, technical decisions |
| **Senior Developer** | Implementation, code review, mentoring |
| **Junior Developer** | Simple tasks, learning |
| **QA Engineer** | Test plans, bug reports |
| **Data Analyst** | Metrics, KPIs, analyses |
| **HR Manager** | Onboarding, culture, hiring |
| **Product Consultant** | Market validation, research |

Each role can only use the tools assigned to it (e.g. only Tech Lead and Product Owner can
`approve_artifact`; only Scrum Master can `start_ceremony`) — permission validation is
centralized and never delegated to the LLM.

## How the Agents Work

```
User command
        │
        ▼
 Agent enters "thinking" state (status published via MQTT)
        │
        ▼
 LLM (local Ollama, or any OpenAI-compatible API) receives the
 role's system prompt + context, and decides: a thought, an
 action and, optionally, a tool to run
        │
        ▼
 Tool validated against the role's permissions and executed
 (e.g. web search, write/review/approve an artifact)
        │
        ▼
 Result published via MQTT to any consumer (other agents,
 frontend, observability)
```

The entire flow is event-driven over MQTT with a standard message envelope (`event_id`,
`timestamp`, `agent_id`, `agent_role`, `payload`) — see
[RFC-001](docs/rfc/001-protocolo-de-comunicacao-entre-agentes.md) (written in Portuguese, as all
internal design documentation of this project is).

## Architecture

### Backend (Clean Architecture)

```
┌──────────────────────────────────────────────────────────────────────┐
│                      MQTT BROKER (Mosquitto)                          │
│       office/agents/#  ·  office/artifacts/#  ·  office/tasks/#       │
└──────────────────────────────┬────────────────────────────────────────┘
                                │
┌───────────────────────────────▼────────────────────────────────────────┐
│                BACKEND (FastAPI, Python 3.12)                          │
│                                                                        │
│   presentation/  →  application/  →  domain/  ←  infrastructure/      │
│                                                                        │
│   domain/         pure entities (Agent, Artifact, Task), interfaces   │
│   application/    use cases (AgentThinkUseCase, WriteArtifact...)     │
│   infrastructure/ MQTT, Ollama, Tavily, PostgreSQL, filesystem        │
│   presentation/   HTTP routes and dependency injection                │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
       PostgreSQL + pgvector  ·  Ollama (host, outside Compose)  ·  Tavily
```

The golden rule of Clean Architecture: code dependency arrows always point inward. `domain/`
never imports anything from `infrastructure/`, `application/`, or `presentation/` — every
external dependency (LLM, database, messaging, web search, filesystem) sits behind a domain
interface, allowing the implementation to be swapped without touching business rules.

### Full product vision (planned end state)

```
┌───────────────────────────────────────────┐
│             WEB INTERFACE                  │
│  Svelte + TypeScript                       │
│  ├── Control panel                         │
│  ├── Agent list and state                  │
│  ├── Logs and notifications                │
│  └── Phaser: pixel-art office              │
└───────────────────┬─────────────────────────┘
                    │ WebSocket / HTTP
┌───────────────────▼─────────────────────────┐
│          COMMUNICATION GATEWAY (Go)         │
│  ├── Real-time API and connections          │
│  │   with the frontend                      │
│  └── BRIDGE between MQTT and the Python     │
│      backend: routes MQTT ⇄ Kafka, with     │
│      idempotency (Redis) and per-agent      │
│      ordering                                │
│  (no authentication — open source project,   │
│   funded by donations, no sensitive data)    │
└───────────────────┬─────────────────────────┘
                    │
┌───────────────────▼─────────────────────────┐
│                MQTT (Mosquitto)             │
└───────────────────┬──────────────────────────┘
                    │
┌───────────────────▼─────────────────────────┐
│          PYTHON BACKEND                     │
│  AI execution                               │
│  Orchestration                              │
│  Tools                                      │
└───────────────────────────────────────────────┘
```

The frontend (Svelte + Phaser.js, pixel-art) and the Go gateway — responsible for serving the
frontend in real time **and** for routing, with delivery and idempotency guarantees, the MQTT
messages exchanged by the Python backend — are part of the full product vision and have not been
implemented in this repository yet. See details in
[`docs/design/arquitetura-geral.md`](docs/design/arquitetura-geral.md) and the full migration
plan in [`docs/migration-plan/fase-8-microservicos/`](docs/migration-plan/fase-8-microservicos/README.md)
(both written in Portuguese).

### Artifacts as first-class citizens

Agents don't just "chat" — they produce real, versionable documents with an explicit lifecycle:

```
DRAFT → IN_REVIEW → APPROVED → ARCHIVED
```

Every artifact is persisted as a real `.md` file under `workspace/projects/{sprint}/`, with YAML
frontmatter (author, type, status, dates), and every state transition publishes an MQTT event —
see [RFC-002](docs/rfc/002-sistema-de-artefatos.md).

### Web search

Some roles (Product Owner, Tech Lead, Developers, Data Analyst, Product Consultant) have access
to the `web_search` tool, backed by [Tavily](https://tavily.com) — a search API built for AI
agents — see [ADR-011](docs/adr/011-tavily-como-provedor-de-busca-web.md).

## Architectural Decisions

Every relevant architectural decision is documented before being implemented:

- **ADRs** (`docs/adr/`) — point-in-time technical decisions (MQTT, FastAPI, Clean Architecture,
  Ollama outside Compose, Tavily, container ports, etc.)
- **RFCs** (`docs/rfc/`) — contracts that cross multiple components (message protocol, artifact
  lifecycle, agent lifecycle)
- **Design Docs** (`docs/design/`) — overall product architecture views
- **Migration Plan** (`docs/migration-plan/`) — every phase of the technical roadmap, including
  the ones not implemented yet

> All internal documentation (ADRs, RFCs, Design Docs, migration plan, `SCRATCHPAD.md`) is
> written in Portuguese, since this is the author's native language and this project started as
> a Brazilian edition of the original AgentOffice. Pull requests and issues in English are
> absolutely welcome.

## Requirements

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose
- [Poetry](https://python-poetry.org/docs/#installation) 2.x (for local backend development)
- [Ollama](https://ollama.com) installed and running **on your host** — this project never spins
  up an Ollama container (see [ADR-009](docs/adr/009-ollama-externo-ao-docker-compose.md))
- (Optional) A free [Tavily](https://app.tavily.com) API key for the `web_search` tool

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/CristianBernardes/agent-office-edicao-brasileira.git
cd agent-office-edicao-brasileira/agent-office-microservice

# 2. Configure the backend
cp backend/.env.example backend/.env
# (optional) set TAVILY_API_KEY in backend/.env to enable web search

# 3. Make sure Ollama is running on your host
ollama pull nemotron-3.5-bolt:latest
ollama pull nomic-embed-text:latest

# 4. Bring up the whole infrastructure (Mosquitto + PostgreSQL + Backend)
make up

# 5. Access
# API:          http://localhost:7001
# Docs:         http://localhost:7001/docs
# MQTT:         localhost:7083 (TCP) / localhost:7000 (WebSocket)
```

## Ports

All external (host) ports of this project follow the `70` prefix convention — see
[ADR-010](docs/adr/010-portas-de-container-com-prefixo-70.md).

| Service | External port |
|---------|------------------|
| Backend (HTTP API) | `7001` |
| Mosquitto (MQTT TCP) | `7083` |
| Mosquitto (MQTT WebSocket) | `7000` |
| PostgreSQL | `7034` |
| Kafka | `7092` |
| Redis | `7079` |

## Development

All development, testing, and quality commands are centralized in the
[`Makefile`](Makefile):

```bash
make help              # list all available commands
make install           # install backend dependencies
make test-unit         # unit tests (fast, no external dependencies)
make test-integration  # integration tests (requires 'make up')
make lint              # lint (ruff)
make format            # automatic formatting (ruff format)
make type-check        # static type checking (mypy --strict)
make check             # runs format + lint + type-check + test
```

More details about the backend structure in [`backend/README.md`](backend/README.md).

## Contributing

This project is open source and welcomes contributions. Before opening a PR, read
[`docs/SCRATCHPAD.md`](docs/SCRATCHPAD.md) — it defines the mandatory quality standards (SOLID,
Clean Code, tests, ADRs) every contribution must follow, plus a detailed history of decisions and
the current implementation state of every phase of the project (written in Portuguese).

---

## 💙 Liked the project?

Any donation amount is welcome and helps cover my family's health costs and keep this open
source project alive and growing. See the donation options (PayPal and Pix) at the top of this
README, or in the [Portuguese version](./README.md).
