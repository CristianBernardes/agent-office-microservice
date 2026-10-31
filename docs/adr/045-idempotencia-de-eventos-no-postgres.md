# ADR-045 — Idempotência de eventos no Postgres

**Status:** Aceito

## Contexto
O gateway entrega com semântica at-least-once; o mesmo `event_id` pode chegar duas vezes. `activity_events` usa `event_id` como chave primária e a reentrega gerava erro.

## Decisão
O repositório de atividades faz `INSERT ... ON CONFLICT (event_id) DO NOTHING`. As demais tabelas já são idempotentes por upsert na chave de negócio. Os defaults de teste de `Settings` ficam em `tests/unit/conftest.py` para não sobrescrever o `.env` dos testes de integração.

## Consequências
- Reentregas não duplicam nem falham.
- Teste de integração cobre a duplicata.
