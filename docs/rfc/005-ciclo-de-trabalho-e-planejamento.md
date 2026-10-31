# RFC-005 — Ciclo de trabalho autônomo e cerimônia de planejamento

**Status:** Aceito · **Data:** 2026-10-31 · **ADRs:** 048, 049

## Resumo

Define como as tarefas do Kanban avançam sozinhas e como a cerimônia de planejamento
(sprint planning) antecede o trabalho.

## Protocolo

1. `plan`: com tarefas no backlog, o facilitador (PO, depois SM) conduz o planejamento via LLM,
   publica a fala no chão do escritório e grava o artefato `SPRINT_PLANNING` (`planning/<id>.md`).
2. Se há menos trabalho em aberto que profissionais, as tarefas são divididas em `Título (i/n)`.
3. As tarefas vão a TODO; o dono é o profissional menos carregado.
4. `assign` (coordenador) → `work` (dev, gera artefato `IMPLEMENTATION`) → `review` (QA/TL,
   nunca o próprio autor) → DONE.

Todo texto gerado segue o idioma do escritório (pt/en). Nenhuma tarefa fora do backlog fica sem
responsável (ver `MoveTaskUseCase._ensure_owner`).

## Alternativas descartadas

Mover o backlog direto para TODO sem cerimônia (ADR-048): deixava profissionais ociosos.
