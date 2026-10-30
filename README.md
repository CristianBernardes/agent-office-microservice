# AgentOffice Microservice

> Um escritório de TI simulado por agentes de IA — cada um com um papel, personalidade e modelo de
> linguagem próprios, colaborando em tempo real via MQTT para planejar, implementar e documentar
> software, exatamente como um time humano faria.

Este repositório é a reconstrução, do zero, do backend do **AgentOffice Pro** seguindo
**Clean Architecture**, princípios **SOLID**, **Clean Code**, **DRY**, **YAGNI**, injeção de
dependência, testes automatizados e documentação arquitetural rigorosa (ADRs, RFCs, Design Docs).

Projeto **open source** — contribuições são bem-vindas. Ver [`docs/SCRATCHPAD.md`](docs/SCRATCHPAD.md)
para os padrões de qualidade obrigatórios antes de abrir um PR.

## Visão da Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                      MQTT BROKER (Mosquitto)                       │
│          office/agents/# · office/tasks/# · office/artifacts/#     │
└───────────────────────────────────┬───────────────────────────────┘
                                    │
┌───────────────────────────────────▼───────────────────────────────┐
│                 BACKEND (FastAPI, Python 3.12, Clean Architecture)  │
│   presentation/ → application/ → domain/ ← infrastructure/         │
└─────────────────────────────────────────────────────────────────┘
                                    │
                    PostgreSQL + pgvector  ·  Ollama (externo ao Compose)
```

Decisões arquiteturais completas em [`docs/adr/`](docs/adr/), contratos de protocolo em
[`docs/rfc/`](docs/rfc/) e visões de design em [`docs/design/`](docs/design/). O plano de migração
completo (todas as fases, inclusive as ainda não implementadas) está em
[`docs/migration-plan/`](docs/migration-plan/).

## Requisitos

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose
- [Poetry](https://python-poetry.org/docs/#installation) 2.x (para desenvolvimento local do backend)
- [Ollama](https://ollama.com) instalado e em execução **no seu host** — este projeto nunca sobe um
  container de Ollama (ver [ADR-009](docs/adr/009-ollama-externo-ao-docker-compose.md))

## Início Rápido

```bash
# 1. Clone o repositório
git clone https://github.com/CristianBernardes/agent-office-edicao-brasileira.git
cd agent-office-edicao-brasileira/agent-office-microservice

# 2. Configure o backend
cp backend/.env.example backend/.env

# 3. Garanta que o Ollama está rodando no seu host
ollama pull nemotron-3.5-bolt:latest
ollama pull nomic-embed-text:latest

# 4. Suba toda a infraestrutura (Mosquitto + PostgreSQL + Backend)
make up

# 5. Acesse
# API:          http://localhost:7001
# Documentação: http://localhost:7001/docs
# MQTT:         localhost:7083 (TCP) / localhost:7000 (WebSocket)
```

## Portas

Todas as portas externas (host) deste projeto seguem a convenção de prefixo `70` — ver
[ADR-010](docs/adr/010-portas-de-container-com-prefixo-70.md).

| Serviço | Porta externa |
|---------|------------------|
| Backend (API HTTP) | `7001` |
| Mosquitto (MQTT TCP) | `7083` |
| Mosquitto (MQTT WebSocket) | `7000` |
| PostgreSQL | `7034` |

## Desenvolvimento

Todos os comandos de desenvolvimento, teste e qualidade estão centralizados no
[`Makefile`](Makefile):

```bash
make help             # lista todos os comandos disponíveis
make install           # instala as dependências do backend
make test-unit         # testes unitários (rápidos, sem dependências externas)
make test-integration  # testes de integração (requer 'make up')
make lint              # lint (ruff)
make format            # formatação automática (ruff format)
make type-check        # verificação de tipos estática (mypy --strict)
make check             # roda format + lint + type-check + test
```

Mais detalhes sobre a estrutura do backend em [`backend/README.md`](backend/README.md).

## Status de Implementação

Este projeto é construído incrementalmente, fase por fase, seguindo o plano de migração em
[`docs/migration-plan/`](docs/migration-plan/):

- [x] **Fase 0** — Fundação documental (ADRs, RFCs, Design Docs)
- [x] **Fase 1** — Esqueleto Clean Architecture do backend, com injeção de dependência e testes
- [ ] **Fase 2** — Integração MQTT completa nos casos de uso de negócio
- [ ] **Fase 3** — Personas (9 papéis, prompts, ferramentas)
- [ ] **Fase 4** — Sistema de artefatos Markdown
- [ ] **Fase 5** — Múltiplos modelos de LLM por agente
- [ ] Frontend (pixel-art) — fica para uma rodada futura, com sprites comprados separadamente

## Contribuindo

Este projeto é open source e aceita contribuições. Antes de abrir um PR, leia
[`docs/SCRATCHPAD.md`](docs/SCRATCHPAD.md) — ele define os padrões de qualidade obrigatórios
(SOLID, Clean Code, testes, ADRs) que toda contribuição deve seguir.
