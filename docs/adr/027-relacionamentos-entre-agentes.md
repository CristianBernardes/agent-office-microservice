# ADR-027: Relacionamentos entre agentes

- Status: Aceito

## Contexto
A tabela `relationships` (migration 8) existe, mas sem domínio. Para a vida dos personagens fazer
sentido, a convivência (reuniões) deve alterar o vínculo entre eles.

## Decisão
- Entidade `Relationship` com par ordenado (`agent_a < agent_b`, espelhando o CHECK do banco),
  `score` em [-1, 1], `interactions` e `status` derivado (stranger, acquaintance, colleague,
  friend, rival) por regra de domínio.
- Porta `IRelationshipRepository` (`get`, `save`, `list_for`) com implementações em memória e
  PostgreSQL (upsert).
- `RecordInteractionUseCase` registra uma interação entre dois agentes; `GoalMeetingUseCase`
  chama-o para cada par de participantes que falaram (+0.05 por reunião).

## Consequências
Sem o caso de uso injetado a reunião funciona como antes. Interações negativas (rivalidade) ainda
não são geradas automaticamente (YAGNI).
