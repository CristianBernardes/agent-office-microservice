# ADR-048 — Escritório vivo: ciclo de trabalho autônomo das tarefas

**Status:** Aceito
**Data:** 2026-11-02
**Autores:** Cristian Bernardes

## Contexto

A reunião de objetivo (ADR-022) só cria tarefas de backlog; depois disso nada se move e os
agentes ficam ociosos. O produto deve parecer um escritório vivo, inclusive com agentes
contratados depois.

## Decisão

- `WorkLoopUseCase.tick()` avança o Kanban respeitando a matriz papel × estágio (ADR-016):
  1. backlog → a fazer (PO/SM planejam);
  2. a fazer → em andamento (coordenador atribui a um dev/TL ocioso);
  3. em andamento → em revisão (o responsável "trabalha" via LLM, grava `tasks/<id>.md` e comenta no chat);
  4. em revisão → concluído (QA/TL ociosos revisam via LLM e libertam o responsável).
- Um passo de LLM por estágio e por tick, em sequência (Ollama local é lento).
- O ciclo roda em background no lifespan, a cada `WORK_LOOP_INTERVAL_SECONDS` (0 = desligado).
  Lê o time a cada tick, portanto contratações novas entram sozinhas.
- Falas e artefatos usam o idioma padrão do escritório (`OFFICE_LANGUAGE`).

## Consequências

- Tarefas andam sem intervenção; custo de LLM proporcional ao intervalo.
- Sem devs/revisores no time, as tarefas aguardam no estágio.
