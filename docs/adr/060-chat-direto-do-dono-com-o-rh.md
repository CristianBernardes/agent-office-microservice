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
- Ordem de demissão é executada na hora, sem depender do LLM: `detect_dismissal_targets`
  identifica verbo de demissão + nome do agente (ou o último citado na conversa, em "demita ele");
  perguntas e frases condicionais ("caso ele não se alinhe…") não são ordens. O RH então propõe
  cria a proposta pendente; a demissão só ocorre quando o dono aprova no `DismissalModal`
  (ADR-056), que abre assim que o chat recarrega as propostas pendentes.
  Nesse caso o LLM não é chamado. As demais mensagens vão ao LLM do RH, com o elenco e o
  histórico rotulado (Dono/RH) no prompt, proibido de afirmar ações que não fez.
- Tentar usar a ferramenta `propose_dismissal` via LLM foi descartado: o modelo respondia em
  texto sem emitir `tool_call` e a demissão nunca acontecia.
- Sem RH ativo a rota responde 409; sessão inexistente (ou que não seja de RH) responde 404.
- Frontend: segundo `ChatPanel` ("Conversa com o RH"); o id da sessão fica no `localStorage`.

## Consequências

- A detecção é por palavras-chave pt/en; frases ambíguas caem no LLM, sem demitir.
- Não há streaming: a resposta chega ao fim da chamada do LLM.
