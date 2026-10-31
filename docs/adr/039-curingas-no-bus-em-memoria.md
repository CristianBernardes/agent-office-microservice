# ADR-039 — Curingas MQTT no barramento em memória

**Status:** Aceito

## Contexto
O feed de atividades não conseguia assinar tópicos por agente (`office/agents/<id>/thought`) porque o `InMemoryMessageBus` só casava tópicos exatos, divergindo do `MqttMessageBus`.

## Decisão
`topic_matches` foi extraído para `infrastructure/messaging/topic_matching.py` e usado pelos dois barramentos. O feed passa a assinar `office/agents/+/thought` e `office/agents/+/action`.

## Consequências
Comportamento idêntico entre bus em memória e MQTT; pensamentos e ações dos agentes aparecem no feed.
