# Design Doc — Autonomia e reuniões

## Objetivo
Quando o usuário cria um objetivo, o time se reúne, debate, registra a ata e cria tarefas, sem intervenção.

## Fluxo
1. `POST /goals` publica `office/goals/created` no barramento.
2. `register_goal_autonomy` assina o tópico e aciona `GoalMeetingUseCase`.
3. Participantes (um por papel, ordem `MEETING_ORDER`) falam por `MEETING_ROUNDS` rodadas; a partir da 2ª há réplica (ADR-032).
4. Cada fala vira mensagem de chat e memória do agente.
5. Ao final: ata (`.md`), backlog (uma tarefa por agente), vínculos (ADR-027) e `Meeting` concluída (ADR-028).

## Resiliência
- Falha de um agente (LLM fora do ar) não derruba a reunião.
- Falhas ao gravar reunião/vínculos são registradas e ignoradas.

## Extensões
Cerimônias manuais via `/meetings` (ADR-033); pesquisa individual via `/research` (ADR-034).
