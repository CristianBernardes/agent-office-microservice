# ADR-046 — Consumidor Kafka→MQTT fora do escopo

**Status:** Aceito

## Contexto
O checklist da Fase 8 previa um consumidor Kafka→MQTT no gateway. Os agentes já recebem tudo direto do Mosquitto, e o Kafka serve como log durável e DLQ (ADR-024).

## Decisão
Não implementar o consumidor (YAGNI). Republicar do Kafka no MQTT reentregaria cada evento aos mesmos assinantes e, sem marcação de origem, criaria laço MQTT→Kafka→MQTT. Reavaliar quando existir um consumidor real do histórico (replay).

## Consequências
- O gateway permanece unidirecional e simples.
- Replay de eventos fica como evolução futura, com ADR próprio.
