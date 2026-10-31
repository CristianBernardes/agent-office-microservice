# ADR-029 — Reuniões de objetivo persistidas e rotas sociais

**Status:** Aceito

## Contexto
`GoalMeetingUseCase` conduzia a reunião, mas não a registrava como `Meeting` (ADR-028), e relacionamentos (ADR-027) e reuniões não tinham rota HTTP.

## Decisão
- `GoalMeetingUseCase` recebe `IMeetingRepository` opcional e grava uma `Meeting` PLANNING concluída (resumo = falas). Falha ao gravar é logada e não interrompe o fluxo.
- Novas rotas somente de leitura: `GET /agents/{id}/relationships` e `GET /goals/{id}/meetings`.

## Consequências
Frontend pode exibir vínculos e histórico de reuniões. Sem escrita HTTP (agentes agem via tools).
