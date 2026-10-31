# ADR-041 — Cobertura mínima, integração e build Docker no CI

**Status:** Aceito

## Contexto

O ADR-040 criou o CI com lint, tipos e testes unitários. A Fase 6/7 do plano de migração ainda
exige: cobertura mínima de 85%, testes de integração no push para `main` e build Docker verificado.

## Decisão

- `fail_under = 85` em `[tool.coverage.report]`; o job `backend` roda `pytest -m unit --cov=src`,
  então a queda de cobertura reprova o PR.
- Job `integration` (somente push em `main`): sobe `postgres`, `mosquitto`, `redis` e `kafka` pelo
  `docker-compose.yml` (portas já são os padrões dos testes), aplica as migrações e roda
  `pytest -m integration`.
- Job `docker`: `docker build` das imagens do backend e do gateway, sem push.

## Consequências

- Regressões de cobertura e de empacotamento são pegas antes do merge.
- A integração só roda em `main` para manter os PRs rápidos.
