# ADR-028: Reuniões e cerimônias (`start_ceremony`)

- Status: Aceito

## Contexto
As tabelas `meetings` e `meeting_participants` (migration 6) existem sem domínio, e a ferramenta
`start_ceremony` (permitida ao Scrum Master e afins) lançava `ToolNotImplementedError`.

## Decisão
- Entidade `Meeting` (`MeetingKind`: planning, refinement, daily, review, retrospective,
  brainstorm; `MeetingStatus`: scheduled, in_progress, done, cancelled), com `start()` já
  criando a reunião em `in_progress` e `finish(summary, decisions)` validando a transição.
- Porta `IMeetingRepository` (`save`, `get`, `list_by_goal`) com implementações em memória e
  PostgreSQL (upsert da reunião + participantes na mesma transação).
- Casos de uso `StartCeremonyUseCase` (exige ≥1 participante, organizador entra na lista),
  `FinishMeetingUseCase` e `ListMeetingsUseCase`.
- Handler `start_ceremony` no `ToolRegistry`, argumentos: `kind`, `title`, `participants`
  (lista de UUIDs, opcional) e `goal_id` (opcional).

## Consequências
`GoalMeetingUseCase` ainda não persiste suas reuniões como `Meeting` (próximo passo, sem
quebrar o fluxo atual). Não há rota HTTP de reuniões ainda (YAGNI até o frontend precisar).
