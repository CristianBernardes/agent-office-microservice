# ADR-052 — Observabilidade: Prometheus, Grafana e Kafka UI

**Status:** Aceito
**Data:** 2026-10-31
**Autores:** Cristian Bernardes

## Contexto

Não havia como acompanhar tópicos Kafka, saúde dos serviços, métricas de negócio (tarefas por
coluna, agentes) nem desempenho da API. Para operar o escritório e cobrar o time (Kaizen) é
preciso observabilidade completa e reproduzível via `docker compose`.

## Decisão

- **Kafka UI** (`provectuslabs/kafka-ui`) para acompanhar tópicos, partições, mensagens e DLQ.
- **Prometheus** coleta `/metrics` do backend e do gateway, além dos exporters de Postgres,
  Redis e Kafka e de contêineres (`cadvisor`).
- **Grafana** com datasource e dashboard provisionados por arquivos (sem cliques manuais).
- Backend: `GET /metrics` (prometheus_client) com requisições HTTP por rota/status/latência e
  *gauges* de negócio (tarefas por status, agentes por cargo), calculados a cada coleta.
- Gateway Go: endpoint `/metrics` em texto Prometheus, sem dependência nova (contadores atômicos).
- Portas, endereços, usuário e senha do Grafana vêm do `.env` (nada fixo no código).

## Consequências

Mais contêineres no compose; o painel "Agent Office" mostra negócio, API, gateway e Kafka. Métricas
de negócio refletem o estado em memória do backend.
