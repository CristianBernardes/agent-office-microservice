# RFC-003 — Ciclo de Vida de um Agente

**Status:** Proposto
**Data:** 2026-10-30
**Autor:** Cristian Bernardes

## Resumo

Define os estados possíveis de um agente, as transições permitidas entre eles e os eventos
publicados em cada transição, servindo de contrato entre a entidade de domínio `Agent` e os casos de
uso que orquestram seu comportamento.

## Estados (`AgentStatus`)

```
IDLE → THINKING → WORKING → IDLE
  ↘                            ↗
    TALKING ──────────────────
  ↘
    OFFLINE
```

| Estado | Significado |
|--------|-------------|
| `IDLE` | Agente disponível, sem tarefa em andamento. |
| `THINKING` | Agente está processando um contexto através do LLM. |
| `WORKING` | Agente tem uma tarefa atribuída e está executando-a. |
| `TALKING` | Agente está em uma troca de mensagens síncrona com outro agente. |
| `OFFLINE` | Agente foi demitido ou está temporariamente indisponível. |

## Transições e Invariantes

- Um agente só pode receber uma nova tarefa atribuída (`assign_task`) quando está em `IDLE`. Tentar
  atribuir uma tarefa a um agente em `THINKING` ou `WORKING` deve ser rejeitado pela entidade de
  domínio com um erro explícito — nunca silenciosamente ignorado.
- `complete_task()` só é uma transição válida a partir de `WORKING`.
- `start_thinking()` é uma transição válida a partir de `IDLE` ou `WORKING` (um agente pode "pensar"
  sobre a tarefa que já está executando).

## Eventos Publicados

Cada transição de estado relevante publica um evento MQTT em
`office/agents/{agentId}/status`, com `retain=true`, conforme definido na
[RFC-001](./001-protocolo-de-comunicacao-entre-agentes.md).

## Escopo desta rodada de implementação

Esta RFC define o contrato alvo do ciclo de vida de um agente. Na Fase 1, a entidade `Agent` já
implementa as transições de estado e suas invariantes (validadas por testes unitários). A publicação
de eventos de status via MQTT acompanha a implementação do caso de uso `AgentThinkUseCase` em uma
rodada futura.
