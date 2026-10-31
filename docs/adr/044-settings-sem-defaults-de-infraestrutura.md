# ADR-044 — Settings sem defaults de infraestrutura

**Status:** Aceito

## Contexto
`Settings` trazia defaults de infraestrutura (URL do banco, host/porta do MQTT, URL do Ollama) escritos no código.

## Decisão
`database_url`, `mqtt_host`, `mqtt_port` e `ollama_base_url` passam a ser obrigatórios e vêm só do ambiente/`.env`. Os testes unitários os definem em `tests/conftest.py`.

## Consequências
- Subir o backend sem `.env` falha de forma explícita.
- Nenhum endereço de infraestrutura fica no código.
