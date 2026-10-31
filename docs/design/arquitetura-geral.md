# Design Doc — Arquitetura Geral

**Status:** Aceito
**Data:** 2026-10-30

## Visão de Componentes (estado final do plano de migração)

```
┌───────────────────────────────────────────┐
│             INTERFACE WEB                 │
│                                           │
│  Svelte + TypeScript                      │
│  ├── Painel de controle                   │
│  ├── Lista e estado dos agentes           │
│  ├── Logs e notificações                  │
│  └── Phaser: escritório em Pixel Art      │
└───────────────────┬───────────────────────┘
                    │
             WebSocket / HTTP
                    │
┌───────────────────▼───────────────────────┐
│          GATEWAY DE COMUNICAÇÃO           │
│                                           │
│  Go                                        │
│  ├── API e conexões em tempo real          │
│  │   com o frontend                        │
│  └── PONTE entre MQTT e o Backend Python:  │
│      roteia MQTT ⇄ Kafka, com              │
│      idempotência (Redis) e ordenação      │
│      por agente — ver Fase 8               │
└───────────────────┬───────────────────────┘
                    │
┌───────────────────▼───────────────────────┐
│                  MQTT                     │
│                                           │
│  Broker MQTT                              │
│  ├── Eventos dos agentes                  │
│  ├── Mudanças de estado                   │
│  └── Notificações de tarefas               │
└───────────────────┬────────────────────────┘
                    │
┌───────────────────▼───────────────────────┐
│          BACKEND PYTHON                   │
│                                           │
│  Execução de IA                           │
│  Orquestração                             │
│  Ferramentas                              │
│  Processamento                            │
└─────────────────────────────────────────────┘
```

O Go não é um serviço paralelo e desconectado do Python — ele é a **ponte de roteamento** entre o
broker MQTT e o backend Python (e entre o MQTT e o frontend). Toda mensagem publicada pelo Python
via MQTT passa pelo Go Gateway antes de ser roteada (com garantias de idempotência e ordenação via
Kafka/Redis) de volta ao MQTT para outros consumidores — ver detalhes completos em
[`docs/migration-plan/fase-8-microservicos/README.md`](docs/migration-plan/fase-8-microservicos/README.md).

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

## Decisão: sem autenticação/autorização no Gateway Go

O AgentOffice Pro é um projeto **open source**, mantido por doações — não há usuários pagantes,
contas, nem dados sensíveis de terceiros a proteger. Por isso, o Gateway de Comunicação (Go, Fase 8)
**não implementa autenticação nem autorização**: toda API e conexão em tempo real (WebSocket) é
aberta por padrão. Qualquer necessidade futura de controle de acesso (ex.: múltiplos usuários
hospedando sua própria instância) deve ser resolvida fora deste gateway (proxy reverso, rede privada,
etc.), nunca adicionando complexidade de autenticação ao código deste projeto sem uma nova decisão
explícita do dono do produto.

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
