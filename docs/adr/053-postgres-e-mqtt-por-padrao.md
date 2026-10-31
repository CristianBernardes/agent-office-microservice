# ADR-053 — Postgres e MQTT por padrão

**Status:** Aceito
**Data:** 2026-11-01
**Autores:** Cristian Bernardes

## Contexto

Com `memory` como padrão (ADR-014, ADR-021), reiniciar o backend apagava agentes e tarefas e o
gateway Kafka não recebia eventos.

## Decisão

- `.env.example` passa a usar `PERSISTENCE_BACKEND=postgres` e `MESSAGE_BUS_BACKEND=mqtt`; as
  migrações rodam no startup (ADR-018). `memory` continua disponível para desenvolvimento.
- Os testes definem `memory` em `tests/conftest.py`, sem depender do `.env` local.

## Consequências

O estado persiste entre reinícios; o compose já provê Postgres e Mosquitto.
