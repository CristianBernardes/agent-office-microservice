# ADR-021 — MQTT real e contrato de tópicos

- Status: aceita

## Contexto

O `MqttMessageBus` existia, mas a aplicação sempre usava o barramento em memória, e o listener só
casava tópicos exatos (sem curingas `+`/`#`), inviabilizando assinaturas como `office/#`.

## Decisão

- Config `MESSAGE_BUS_BACKEND=memory|mqtt` (padrão `memory`). Com `mqtt`, `get_message_bus()` devolve
  o `MqttMessageBus` (host/porta de `MQTT_HOST`/`MQTT_PORT`).
- O `lifespan` da aplicação conecta o barramento na subida e desconecta no desligamento.
- O listener passa a casar assinaturas com curingas MQTT (`topic_matches`).
- Todas as mensagens usam o envelope da RFC-001. Contrato de tópicos publicados:

| Tópico | Origem |
|---|---|
| `office/agents/{id}/status` / `thought` / `action` | ciclo de vida e pensamento do agente |
| `office/tasks/updated` | criação/movimentação de tarefas |
| `office/goals/created` | objetivo enviado pelo usuário |
| `office/chat/message` | mensagens do chat |
| `office/artifacts/created` / `updated` | artefatos `.md` |

- O gateway Go (futuro) assina `office/#` e encaminha ao Kafka.

## Consequências

- Em produção o fluxo real passa pelo Mosquitto; testes continuam usando o barramento em memória.
- Subir com `mqtt` sem broker falha rápido na inicialização.
