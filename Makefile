# ─────────────────────────────────────────────────────────────────────────
# AgentOffice Microservice — Makefile
#
# Centraliza todos os comandos de desenvolvimento, teste, lint e infraestrutura
# do backend. Ver docs/SCRATCHPAD.md: `make format` é obrigatório após qualquer
# alteração de código, e nenhuma validação deste Makefile pode ser ignorada.
# ─────────────────────────────────────────────────────────────────────────

BACKEND_DIR := backend
COMPOSE     := docker compose
POETRY      := poetry

.DEFAULT_GOAL := help

.PHONY: help install run up down restart logs ps \
        test test-unit test-integration coverage \
        lint format type-check check \
        clean check-poetry

## help: Lista todos os comandos disponíveis deste Makefile.
help:
	@echo "AgentOffice Microservice — comandos disponíveis:"
	@echo ""
	@echo "  Infraestrutura (Docker Compose):"
	@echo "    make up               - sobe mosquitto, postgres e backend em background"
	@echo "    make down             - derruba todos os containers"
	@echo "    make restart          - reinicia todos os containers"
	@echo "    make logs             - segue os logs de todos os containers"
	@echo "    make ps               - lista o status dos containers do projeto"
	@echo ""
	@echo "  Backend (Python / Poetry):"
	@echo "    make install          - instala as dependências do backend via Poetry"
	@echo "    make run              - executa o backend localmente (uvicorn --reload)"
	@echo ""
	@echo "  Qualidade de código:"
	@echo "    make format           - formata o código com ruff format"
	@echo "    make lint             - executa ruff check (lint)"
	@echo "    make type-check       - executa mypy em modo estrito"
	@echo "    make check            - roda format + lint + type-check + test"
	@echo ""
	@echo "  Testes:"
	@echo "    make test             - roda testes unitários e de integração"
	@echo "    make test-unit        - roda apenas testes unitários (sem dependências externas)"
	@echo "    make test-integration - roda testes de integração (requer 'make up')"
	@echo "    make coverage         - roda testes unitários com relatório de cobertura"
	@echo ""
	@echo "  Limpeza:"
	@echo "    make clean            - remove caches de build, teste e bytecode Python"

# ─── Infraestrutura (Docker Compose) ───────────────────────────────────────

## up: Sobe toda a infraestrutura do projeto (mosquitto, postgres, backend) em background.
up:
	$(COMPOSE) up -d --build

## down: Derruba todos os containers do projeto.
down:
	$(COMPOSE) down

## restart: Reinicia todos os containers do projeto.
restart: down up

## logs: Segue os logs de todos os containers em execução.
logs:
	$(COMPOSE) logs -f

## ps: Lista o status atual dos containers do projeto.
ps:
	$(COMPOSE) ps

# ─── Backend (Python / Poetry) ─────────────────────────────────────────────

## check-poetry: Verifica se o Poetry está instalado antes de qualquer comando que dependa dele.
check-poetry:
	@command -v $(POETRY) >/dev/null 2>&1 || { \
		echo "Erro: 'poetry' não foi encontrado no PATH."; \
		echo "Instale com: curl -sSL https://install.python-poetry.org | python3 -"; \
		echo "Documentação: https://python-poetry.org/docs/#installation"; \
		exit 1; \
	}

## install: Instala as dependências do backend (produção, testes e lint) via Poetry.
install: check-poetry
	cd $(BACKEND_DIR) && $(POETRY) install --with test,lint

## run: Executa o backend localmente com recarregamento automático (requer 'make install').
run: check-poetry
	cd $(BACKEND_DIR) && $(POETRY) run uvicorn src.presentation.main:app --reload --host 0.0.0.0 --port 8000

# ─── Qualidade de código ────────────────────────────────────────────────────

## format: Formata todo o código do backend com ruff format.
format: check-poetry
	cd $(BACKEND_DIR) && $(POETRY) run ruff format src/ tests/

## lint: Executa o lint (ruff check) sobre todo o código do backend.
lint: check-poetry
	cd $(BACKEND_DIR) && $(POETRY) run ruff check src/ tests/

## type-check: Executa a verificação de tipos estática (mypy --strict) sobre o código de produção.
type-check: check-poetry
	cd $(BACKEND_DIR) && $(POETRY) run mypy src/

## check: Roda a sequência completa de validação — formatação, lint, tipos e testes.
check: format lint type-check test

# ─── Testes ─────────────────────────────────────────────────────────────────

## test: Roda todos os testes (unitários e de integração).
test: check-poetry
	cd $(BACKEND_DIR) && $(POETRY) run pytest

## test-unit: Roda apenas os testes unitários — rápidos, sem dependências externas.
test-unit: check-poetry
	cd $(BACKEND_DIR) && $(POETRY) run pytest -m unit -v

## test-integration: Roda os testes de integração — requer 'make up' previamente.
test-integration: check-poetry
	cd $(BACKEND_DIR) && $(POETRY) run pytest -m integration -v

## coverage: Roda os testes unitários com relatório de cobertura no terminal.
coverage: check-poetry
	cd $(BACKEND_DIR) && $(POETRY) run pytest -m unit --cov=src --cov-report=term-missing

# ─── Limpeza ────────────────────────────────────────────────────────────────

## clean: Remove caches de build, teste e bytecode Python do backend.
clean:
	find $(BACKEND_DIR) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf $(BACKEND_DIR)/.pytest_cache $(BACKEND_DIR)/.mypy_cache $(BACKEND_DIR)/.ruff_cache
	rm -rf $(BACKEND_DIR)/.coverage $(BACKEND_DIR)/coverage.xml
