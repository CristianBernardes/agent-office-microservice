# ADR-049 — Cerimônia de planejamento: ninguém fica ocioso

**Status:** Aceito
**Data:** 2026-11-03
**Autores:** Cristian Bernardes

## Contexto

Com tarefas no backlog, o ciclo de trabalho (ADR-048) as movia direto para TODO. O correto é
haver primeiro a cerimônia de Scrum, conduzida por um cargo alto, dividindo o trabalho.

## Decisão

- Se há tarefas no backlog, o facilitador (PO, depois SM) conduz o *sprint planning* antes de
  qualquer trabalho: o LLM descreve a divisão, publicada no chat e como artefato
  `planning/<id>.md`, no idioma do escritório (pt/en).
- Se há menos trabalho em aberto que profissionais disponíveis, tarefas são divididas em
  partes `Título (i/n)`, mantendo prioridade e objetivo, para que ninguém fique ocioso.
- Depois as tarefas vão para TODO e o dono é o menos carregado (`_ensure_owner`).

## Consequências

Uma chamada extra ao LLM por planejamento; fluxo mais fiel ao Scrum.
