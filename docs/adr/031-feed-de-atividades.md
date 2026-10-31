# ADR-031 — Feed de atividades

**Status:** Aceito

## Contexto
A tabela `activity_events` (ADR-017) existe sem código. O frontend precisa de um feed do que acontece no escritório.

## Decisão
- Entidade `ActivityEvent(event_id, kind, payload, agent_id?, created_at)` e porta `IActivityRepository` (`add`, `recent(limit)`).
- `register_activity_feed(bus, factory)` assina os tópicos fixos de domínio (`goals/created`, `tasks/updated`, `artifacts/*`, `chat/message`) e grava cada envelope; `kind` é o tópico. Falha ao gravar é logada e ignorada.
- Rota `GET /activity?limit=` (1–200, padrão 50), mais recentes primeiro.
- Tópicos por agente (`agents/{id}/...`) ficam fora: o barramento não tem curinga; revisitar com o MQTT real.

## Consequências
Feed barato e desacoplado dos casos de uso, via eventos já publicados.
