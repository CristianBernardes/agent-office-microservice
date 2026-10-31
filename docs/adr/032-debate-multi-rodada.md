# ADR-032 — Debate em várias rodadas

**Status:** Aceito

## Contexto
A reunião de objetivo (ADR-022) dava uma única fala por papel. Sem réplica, não há debate real.

## Decisão
- `MEETING_ROUNDS` (padrão 1, limite 1–5) define quantas vezes cada papel fala, sempre na mesma ordem.
- A partir da 2ª rodada o contexto traz a ata acumulada e pede réplica às falas dos colegas ("debate").
- Ata, backlog, vínculos e `Meeting` consideram todas as falas; os vínculos usam participantes únicos.

## Consequências
Mais chamadas ao LLM por reunião (custo linear em rodadas); por isso o padrão continua 1.
