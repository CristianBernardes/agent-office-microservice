# ADR-013 — Endpoint para despachar objetivos a um agente

**Status:** Aceito
**Data:** 2026-10-31
**Autores:** Cristian Bernardes

## Contexto

Até aqui só era possível fazer um agente pensar via testes ou código Python. O dono do produto
precisa de um ponto de entrada para entregar um objetivo a um agente (ex.: ao Product Owner).

## Decisão

- `POST /agents/{agent_id}/think` com corpo `{"context": "<objetivo>"}`.
- Caso de uso `DispatchGoalUseCase`: busca o agente (`AgentNotFoundError` → 404), delega ao
  `AgentThinkUseCase`, devolve o agente a `IDLE` (`Agent.finish_thinking`), persiste e publica o
  novo status no MQTT. Se o LLM falhar, o agente também volta a `IDLE` (nunca fica preso em
  `THINKING`) e o erro é propagado.
- Agente `OFFLINE` → 409 (`InvalidStateTransitionError`), mensagem localizada via `Accept-Language`.
- A publicação de status foi extraída para `application/common/agent_status_publisher.py` (DRY).
- Resposta: pensamento, ação, alvo e `tool_call` decididos pelo agente.

## Consequências

- O frontend e o usuário podem acionar qualquer agente; a execução de ferramentas continua
  governada pelo `ToolRegistry` (permissões por papel).
- Não há fila nem execução assíncrona em segundo plano; a chamada é síncrona (YAGNI).
