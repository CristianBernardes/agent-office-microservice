# ADR-055 — Diálogo do PO com o cliente

**Status:** Aceito
**Data:** 2026-11-01
**Autores:** Cristian Bernardes

## Contexto

O time debatia (ADR-032) e gerava backlog sem nunca confirmar o escopo com o cliente (o usuário).

## Decisão

- Ao fim da reunião do objetivo, o PO leva a proposta ao cliente como mensagem `question` no chat
  (pt/en) e o time segue com plano provisório: o fluxo nunca fica bloqueado esperando resposta.
- O usuário responde pelo chat (campo no `ChatPanel`, `POST /messages` sem `sender_id`). O
  `ClientDialogueUseCase`, assinante de `office/chat/message`, reage só a mensagens `chat` do
  usuário: registra a resposta na memória do PO (importância alta) e responde com uma `decision`.
- O debate continua em `MEETING_ROUNDS` rodadas; cada papel diz o que, na sua área, deve realmente
  ser entregue.

## Consequências

Mais uma chamada de LLM por objetivo e por resposta. Ajustar o backlog já criado a partir da
resposta do cliente fica como evolução (hoje a resposta vira contexto e memória do PO).
