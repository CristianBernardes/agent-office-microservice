# ADR-024 — Gateway Go: MQTT → Kafka

- Status: aceita

## Contexto

MQTT é o barramento em tempo real (frontend/agentes). Para auditoria, replay e consumidores
futuros, os eventos precisam de um log durável: Kafka.

## Decisão

- Serviço Go independente em `gateway/` (Dockerfile próprio). Assina `office/#`, valida o envelope
  (ADR-021: `event_id`, `timestamp`, `agent_id`, `payload`), deduplica por `event_id` (Redis
  `SET NX` com TTL; MQTT QoS 1 pode entregar duplicado) e publica em `office.events`
  (chave = `agent_id`, headers `mqtt_topic` e `event_id`).
- Envelope inválido vai para `office.events.dlq` com header `error` (nunca é perdido).
- Núcleo (`internal/relay`) depende de interfaces (`Deduper`, `Producer`) — testável sem rede.
- Kafka em modo KRaft (sem Zookeeper); `kafka-init` cria os tópicos. Redis só para dedupe.
- Falha do Redis: processa mesmo assim (preferir duplicata a perda).
- Configuração por variáveis de ambiente: `MQTT_URL`, `KAFKA_BROKERS`, `REDIS_ADDR`.

## Consequências

- O backend Python não conhece Kafka; o acoplamento é só o contrato de tópicos.
