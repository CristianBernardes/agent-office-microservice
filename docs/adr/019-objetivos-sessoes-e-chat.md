# ADR-019 — Objetivos, sessões e chat

**Status:** Aceito
**Data:** 2026-10-31
**Autores:** Cristian Bernardes

## Contexto

O dono do produto digita objetivos no chat ("Crie um produto digital para vender 5 unidades por
dia por R$ 39,90") e os agentes precisam conversar entre si e com ele. O banco já tem `sessions`,
`goals` e `messages` (ADR-017/018), mas não há código que os use. Sem um chat persistido, o
frontend não consegue exibir a caixa de mensagens e os agentes não "falam".

## Decisão

- Entidades de domínio `Goal`, `Session` e `ChatMessage` (`MessageKind`: chat, thought, system,
  question, decision), com identificadores tipados `GoalId`, `SessionId`, `MessageId`.
- Porta única `IChatRepository` (sessões, objetivos e mensagens: mesma raiz de consistência), com
  adaptadores em memória e PostgreSQL.
- Casos de uso:
  - `SubmitGoalUseCase`: cria a sessão se não for informada, grava o objetivo (pedido pelo usuário)
    e a mensagem inicial; publica `office/goals/created` e `office/chat/message`.
  - `SendMessageUseCase`: usuário (sem remetente) ou agente envia mensagem a um destinatário ou em
    broadcast; valida sessão, remetente e destinatário; publica `office/chat/message`.
- Rotas: `POST/GET /goals`, `POST /messages`, `GET /sessions/{id}/messages` (404 localizado pt/en).
- Tool `send_message` no `ToolRegistry` (já permitida por papel em `tool_permissions`).
- O objetivo **não** dispara o LLM aqui: o loop de autonomia (ADR futura) consome
  `office/goals/created`. Isto mantém o caso de uso síncrono e testável (YAGNI).
- A numeração do contrato de tópicos MQTT passa a ser a ADR-020.

## Consequências

- O frontend lê o histórico por sessão e recebe novas mensagens via MQTT.
- Mensagem de usuário usa `sender_id NULL` e papel `user` no envelope.
- Mensagens de agentes inexistentes são rejeitadas antes de tocar o banco.
