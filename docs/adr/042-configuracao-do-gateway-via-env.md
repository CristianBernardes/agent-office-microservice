# ADR-042 — Configuração do gateway somente via ambiente

- **Status:** Aceito

## Contexto
O gateway Go tinha valores embutidos no código (URLs padrão, tópicos Kafka, QoS, TTL e prefixo do dedupe).
Isso viola a regra de nunca ter configuração fixa no código e dificulta ambientes distintos.

## Decisão
- Pacote `internal/config`: toda variável é obrigatória, sem padrões embutidos; falha rápido listando as ausentes.
- `gateway/.env` (não versionado) é lido opcionalmente; o ambiente real tem precedência. Modelo em `gateway/.env.example`.
- Tópicos, QoS, client id, TTL e prefixo do dedupe são configuráveis; `relay.New` recebe `Topics`.
- `docker-compose` usa `env_file: gateway/.env` (gateway e kafka-init) e sobrescreve apenas os hosts internos.
- CI copia `.env.example` para `.env` antes de subir a stack.

## Consequências
Nada fixo no código; ambientes diferentes só trocam o `.env`. Quem clona precisa copiar o `.env.example`.
