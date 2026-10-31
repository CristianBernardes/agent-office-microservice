# ADR-050 — Etapa de teste (QA) antes da revisão

**Status:** Aceito
**Data:** 2026-10-31
**Autores:** Cristian Bernardes

## Contexto

O fluxo Kanban ia de `in_progress` direto para `in_review`. Faltava a etapa em que o
testador (QA) pega a entrega e a testa; só depois de testada ela deve ser revisada.

## Decisão

- Novo status `testing` ("Em teste"): `todo → in_progress → testing → in_review → done`.
- `in_progress → testing`: quem executa (devs/Tech Lead). `testing → in_review`: apenas QA
  (aprovou nos testes). `testing → in_progress`: apenas QA (reprovou; volta ao dev).
- O ciclo de trabalho ganha o passo `_test`: o QA (nunca o próprio autor) escreve o plano/
  resultado de testes (artefato `test_plan` em `tests/<id>.md`, no idioma do escritório) e
  move a tarefa para revisão. A revisão (`_review`) só ocorre depois.
- Frontend: coluna "Em teste" com limite WIP configurável (`VITE_WIP_LIMIT_TESTING`).
- Migração `000010` amplia o domínio `task_status`.

## Consequências

Qualidade explícita no quadro e nenhum item chega à revisão sem teste. Custo: uma chamada de
LLM a mais por tarefa.
