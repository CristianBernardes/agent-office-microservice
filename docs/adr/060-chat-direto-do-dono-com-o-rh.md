# ADR-060 — Chat direto do dono do produto com o RH

**Status:** Aceito
**Data:** 2026-11-04
**Autores:** Cristian Bernardes

## Contexto

O dono do produto conversa com o PO pelo chat (ADR-055), mas não tinha canal direto com o RH.
A demissão por proposta do RH (ADR-056) existia só como ferramenta (`propose_dismissal`) que o
LLM do RH raramente decidia chamar por conta própria — na prática, nunca aconteceu. O dono quer
discutir o desempenho do time com o RH e poder pedir demissões diretamente.

## Decisão

- `POST /hr/chat` (`HrChatUseCase`): grava a mensagem do dono numa sessão própria
  (`Session.scenario = "hr"`, criada se `session_id` não vier), aciona o RH via
  `DispatchGoalUseCase` e grava a resposta na mesma sessão. O histórico é lido pela rota já
  existente `GET /sessions/{id}/messages`.
- O prompt entregue ao RH inclui o elenco ativo (nome | cargo | `agent_id`) e a instrução de usar
  `propose_dismissal` quando o dono pedir ou autorizar uma demissão. Assim o RH tem os
  identificadores necessários e um pedido explícito, em vez de depender de iniciativa própria.
- A decisão final continua do dono: a proposta aparece no `DismissalModal` (ADR-056) para
  aprovar/rejeitar. Recusas da ferramenta (já pendente, já offline, sem motivo) voltam ao chat como
  mensagem `system` localizada.
- Sem RH ativo a rota responde 409; sessão inexistente (ou que não seja de RH) responde 404.
- Frontend: segundo `ChatPanel` ("Conversa com o RH"); o id da sessão fica no `localStorage`.

## Consequências

- O RH só age quando o LLM escolhe chamar a ferramenta; a qualidade depende do modelo do RH.
- Não há streaming: a resposta chega ao fim da chamada do LLM.
