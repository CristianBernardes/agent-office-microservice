# AgentOffice Backend

Backend em **Python 3.12 + FastAPI**, construído com **Clean Architecture**, responsável por
orquestrar os agentes de IA do [AgentOffice Pro](../README.md).

## Arquitetura

```
src/
├── domain/           # Entidades, value objects e interfaces — zero dependências externas
├── application/      # Casos de uso — orquestra o domínio através das interfaces
├── infrastructure/    # Implementações concretas (MQTT, LLM, PostgreSQL, config)
└── presentation/      # FastAPI — rotas HTTP e injeção de dependência
```

Veja as decisões arquiteturais completas em [`docs/adr/`](../docs/adr/) e o contrato de
mensageria em [`docs/rfc/001-protocolo-de-comunicacao-entre-agentes.md`](../docs/rfc/001-protocolo-de-comunicacao-entre-agentes.md).

## Requisitos

- Python 3.12+
- [Poetry](https://python-poetry.org/docs/#installation) 2.x
- Docker + Docker Compose (para PostgreSQL e Mosquitto)
- [Ollama](https://ollama.com) instalado e em execução **no host** — nunca em container deste
  projeto (ver [ADR-009](../docs/adr/009-ollama-externo-ao-docker-compose.md))

## Como executar localmente

```bash
# 1. Instale as dependências
make install

# 2. Copie o .env de exemplo
cp backend/.env.example backend/.env

# 3. Suba a infraestrutura (PostgreSQL + Mosquitto)
make up

# 4. Rode o backend
make run
```

A API ficará disponível em `http://localhost:7001`, com documentação interativa em
`http://localhost:7001/docs`.

## Testes e qualidade

Todos os comandos de teste, lint e formatação estão centralizados no
[`Makefile`](../Makefile) da raiz deste microserviço:

```bash
make test             # testes unitários + integração
make test-unit        # apenas testes unitários (rápidos, sem dependências externas)
make test-integration # testes de integração (requer `make up`)
make lint             # ruff check + mypy
make format           # ruff format
```
