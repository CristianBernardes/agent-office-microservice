# ADR-012 — Internacionalização (Português e Inglês)

**Status:** Aceito
**Data:** 2026-10-31
**Autores:** Cristian Bernardes

## Contexto

O projeto será open source e financiado por doações, com público brasileiro e internacional. Todo o
sistema precisa funcionar em **português (pt)** e **inglês (en)**: prompts dos agentes, mensagens de
erro da API e, futuramente, o frontend.

## Decisão

- `Language` (`pt`, `en`) em `domain/localization/language.py`, com `parse` e `from_accept_language`.
- Catálogo `domain/localization/messages.py` (chave → idioma → modelo de texto) e `translate()`.
  Um teste garante que toda chave existe nos dois idiomas com os mesmos placeholders.
- `DomainError(message_key, **params)`: `str()` renderiza em inglês (logs/desenvolvedores);
  `localized(language)` renderiza no idioma pedido. `InvalidValueError` também é `ValueError`.
- API: o idioma vem do cabeçalho `Accept-Language`, com fallback para `OFFICE_LANGUAGE`.
- Prompts dos agentes em `infrastructure/prompts/{pt,en}/*.md`; o idioma do escritório vem de
  `OFFICE_LANGUAGE` (padrão `en`) e é passado ao `AgentThinkUseCase`.
- Erros destinados a desenvolvedores (`RuntimeError` de infraestrutura) ficam em inglês.
- Identificadores de código continuam em inglês; comentários/docstrings em português.

## Consequências

- Novo idioma = novo valor em `Language`, nova tradução de cada chave e uma pasta de prompts.
- Mensagens novas exigem chave no catálogo (os testes falham se faltar um idioma).
