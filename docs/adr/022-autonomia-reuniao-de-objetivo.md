# ADR-022 — Autonomia: reunião do time sobre um objetivo

- Status: aceita

## Contexto

`office/goals/created` é publicado (ADR-019), mas ninguém o consome. O produto exige que os agentes
"vivam": ao receber um objetivo, devem pensar juntos, conversar e deixar registro (`.md`).

## Decisão

- `GoalMeetingUseCase`: para um objetivo, convoca os papéis presentes numa ordem fixa
  (product_owner → product_consultant → data_analyst → tech_lead → dev_senior → qa_engineer →
  scrum_master). Cada agente pensa (via `DispatchGoalUseCase`, com status e eventos MQTT) tendo como
  contexto o objetivo + a ata até ali; sua fala vai ao chat da sessão (`SendMessageUseCase`) e vira
  memória (`RememberUseCase`, tipo `conversation`).
- Ao final, a ata é gravada como artefato `analysis` em `projects/{goal_id}/meeting.md`, autor =
  primeiro participante (PO, se existir). Os `.md` ficam sob `workspace/` (gitignored).
- Resiliência: falha de um agente (LLM fora do ar) é registrada e a reunião segue; sem agentes, não
  há reunião (log).
- `register_goal_autonomy(bus, use_case)` assina `office/goals/created` e dispara a reunião em
  *background task* (não bloqueia o listener MQTT).
- Ligado por `AUTONOMY_ENABLED` (padrão `false`) no `lifespan`; testes e dev simples não disparam LLM.
- Rótulos da ata/contexto são localizados pt/en (idioma do escritório).
- Fora de escopo (próximas ADRs): decomposição em tarefas pelo PO, reuniões multi-rodada, 
  agendamento por `meetings`.

## Consequências

- Primeira vida real do escritório, com custo previsível: 1 chamada de LLM por papel presente.
- Ordem fixa é simples (YAGNI); evoluirá para debate multi-rodada.
