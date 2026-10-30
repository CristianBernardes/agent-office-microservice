# Design Doc — Arquitetura Geral

**Status:** Aceito
**Data:** 2026-10-30

## Visão de Componentes (estado final do plano de migração)

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│                  (fica para uma rodada futura)                   │
└───────────────────────────────────┬───────────────────────────────┘
                                    │ MQTT sobre WebSocket
┌───────────────────────────────────▼───────────────────────────────┐
│                      MQTT BROKER (Mosquitto)                       │
│          office/agents/# · office/tasks/# · office/artifacts/#     │
└───────────────────────────────────┬───────────────────────────────┘
                                    │
┌───────────────────────────────────▼───────────────────────────────┐
│                      BACKEND (FastAPI, Python 3.12)                │
│                                                                     │
│  presentation/  →  application/  →  domain/  ←  infrastructure/    │
│                                                                     │
│  - Agent Think Loop (use cases)                                    │
│  - MQTT Publisher/Subscriber (aiomqtt)                              │
│  - LLM Adapters (Ollama externo / OpenAI-compatible)                 │
│  - PostgreSQL + pgvector (metadados, memória semântica futura)       │
└─────────────────────────────────────────────────────────────────┘
```

## Fluxo de Dependência (Clean Architecture)

```
presentation ──depends on──▶ application ──depends on──▶ domain
infrastructure ──implements──▶ domain (interfaces)
```

A regra de ouro: as setas de dependência de código sempre apontam para dentro. O `domain/` não
importa nada de `infrastructure/`, `application/` ou `presentation/`.

## Infraestrutura Externa

| Peça | Onde roda | Observação |
|------|-----------|------------|
| PostgreSQL + pgvector | Container Docker deste projeto | Porta externa `7034` (ver ADR-010). |
| Mosquitto (MQTT) | Container Docker deste projeto | Portas externas `7083` (TCP) e `7000` (WebSocket). |
| Backend (FastAPI) | Container Docker deste projeto | Porta externa `7001`. |
| **Ollama** | **Host do desenvolvedor, fora do Docker Compose** | Ver ADR-009 — nunca em container deste projeto. |

## Escopo entregue nesta rodada

Esta rodada de implementação (Fase 0 + Fase 1 do plano de migração) entrega:
- Toda a documentação de fundação (este Design Doc, ADRs, RFCs);
- O esqueleto completo de Clean Architecture do backend, com entidades, interfaces, casos de uso
  mínimos de exemplo e injeção de dependência configurada;
- Infraestrutura de MQTT (`MqttMessageBus`) e de conexão PostgreSQL prontas para uso, com testes;
- `docker-compose.yml` atualizado com PostgreSQL real e o serviço de backend, mantendo o Mosquitto
  já existente e sem qualquer serviço de Ollama.

A implementação completa dos casos de uso de negócio (pensamento de agente, artefatos, personas,
sprints) é realizada nas fases seguintes, descritas em `docs/migration-plan/`.
