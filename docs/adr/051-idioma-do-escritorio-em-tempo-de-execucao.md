# ADR-051 — Idioma do escritório em tempo de execução

**Status:** Aceito
**Data:** 2026-10-31
**Autores:** Cristian Bernardes

## Contexto

O ciclo de trabalho (planejamento, execução, testes, revisão e seus `.md`) usava o idioma fixo
de `OFFICE_LANGUAGE`. Ao trocar pt/en na tela, as decisões do time continuavam no idioma antigo.

## Decisão

- `OfficeLanguage` (domínio): detentor mutável do idioma atual, iniciado por `OFFICE_LANGUAGE`.
- `PUT /office/language` altera e `GET /office/language` consulta o idioma; o frontend chama o PUT
  ao carregar e a cada troca de idioma.
- `WorkLoopUseCase` lê o idioma do `OfficeLanguage` a cada passo (também aceita `Language` fixo,
  por compatibilidade com os testes).
- Títulos e descrições digitados pelo usuário não são traduzidos (YAGNI).

## Consequências

Tarefas, decisões e `.md` novos seguem o idioma escolhido na tela. O estado é em memória e volta
ao valor do `.env` ao reiniciar até o frontend reenviar o idioma.
