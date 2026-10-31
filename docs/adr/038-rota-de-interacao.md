# ADR-038 — Rota de escrita de relacionamentos

**Status:** Aceito

## Contexto
Relacionamentos só tinham leitura; vínculos eram criados apenas por reuniões autônomas.

## Decisão
`POST /relationships/interactions` com `first`, `second` e `delta` (−1..1, padrão 0,05) reutiliza `RecordInteractionUseCase`. Agentes iguais ou delta fora da faixa retornam 422.

## Consequências
O frontend pode registrar interações manuais (ex.: elogio, conflito). O par é ordenado no domínio, então a ordem dos IDs não importa.
