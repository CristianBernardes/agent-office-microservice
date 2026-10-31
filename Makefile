# ─────────────────────────────────────────────────────────────────────────
# AgentOffice Microservice — Makefile
#
# Centraliza todos os comandos de desenvolvimento, teste, lint e infraestrutura
# do backend. Ver docs/SCRATCHPAD.md: `make format` é obrigatório após qualquer
# alteração de código, e nenhuma validação deste Makefile pode ser ignorada.
# ─────────────────────────────────────────────────────────────────────────

BACKEND_DIR := backend
GATEWAY_DIR := gateway
FRONTEND_DIR := frontend
COMPOSE     := docker compose
POETRY      := poetry

.DEFAULT_GOAL := help

.PHONY: help install run up down restart logs ps \
        test test-unit test-integration coverage \
        migrate migrate-rollback migrate-status migrate-fresh make-migration \
        lint format format-go format-frontend format-all type-check check \
        lint-go test-go build-go lint-frontend test-frontend build-frontend \
        install-frontend check-all \
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
	@echo "    make format-go        - formata o gateway Go (gofmt)"
	@echo "    make format-frontend  - formata o frontend (prettier)"
	@echo "    make format-all       - formata backend, gateway e frontend"
	@echo "    make lint             - executa ruff check (lint)"
	@echo "    make type-check       - executa mypy em modo estrito"
	@echo "    make check            - roda format + lint + type-check + test (backend)"
	@echo "    make lint-go          - gofmt (verificação) + go vet no gateway"
	@echo "    make lint-frontend    - svelte-check + tsc no frontend"
	@echo "    make check-all        - valida backend, gateway e frontend (lint + testes)"
	@echo ""
	@echo "  Testes:"
	@echo "    make test             - roda testes unitários e de integração"
	@echo "    make test-unit        - roda apenas testes unitários (sem dependências externas)"
	@echo "    make test-integration - roda testes de integração (requer 'make up')"
	@echo "    make test-go          - roda os testes do gateway Go"
	@echo "    make test-frontend    - roda os testes do frontend (vitest)"
	@echo "    make build-go         - compila o gateway Go"
	@echo "    make build-frontend   - gera o build de produção do frontend"
	@echo "    make install-frontend - instala as dependências do frontend (npm ci)"
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

## lint-go: Verifica formatação (gofmt) e executa go vet no gateway.
lint-go:
	@cd $(GATEWAY_DIR) && out=$$(gofmt -l .); \
		if [ -n "$$out" ]; then echo "Arquivos Go fora do padrão gofmt:"; echo "$$out"; exit 1; fi
	cd $(GATEWAY_DIR) && go vet ./...

## test-go: Roda os testes do gateway Go.
test-go:
	cd $(GATEWAY_DIR) && go test ./...

## build-go: Compila o gateway Go.
build-go:
	cd $(GATEWAY_DIR) && go build ./...

## install-frontend: Instala as dependências do frontend.
install-frontend:
	cd $(FRONTEND_DIR) && npm ci

## lint-frontend: Executa svelte-check e tsc no frontend.
lint-frontend:
	cd $(FRONTEND_DIR) && npm run check

## test-frontend: Roda os testes do frontend (vitest).
test-frontend:
	cd $(FRONTEND_DIR) && npm test

## build-frontend: Gera o build de produção do frontend.
build-frontend:
	cd $(FRONTEND_DIR) && npm run build

## check-all: Valida backend, gateway e frontend (lint, tipos e testes).
check-all: check lint-go test-go lint-frontend test-frontend

## format-go: Formata o código do gateway Go com gofmt.
format-go:
	cd $(GATEWAY_DIR) && gofmt -w .

## format-frontend: Formata o código do frontend (prettier).
format-frontend:
	cd $(FRONTEND_DIR) && npx --yes prettier --write "src/**/*.{ts,svelte,css}"

## format-all: Formata backend, gateway e frontend.
format-all: format format-go format-frontend

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

## migrate: Aplica as migrações pendentes (ADR-018).
migrate: check-poetry
	cd $(BACKEND_DIR) && $(POETRY) run python -m src.infrastructure.persistence.migrator migrate

## migrate-rollback: Desfaz o último batch de migrações.
migrate-rollback: check-poetry
	cd $(BACKEND_DIR) && $(POETRY) run python -m src.infrastructure.persistence.migrator rollback

## migrate-status: Lista migrações aplicadas e pendentes.
migrate-status: check-poetry
	cd $(BACKEND_DIR) && $(POETRY) run python -m src.infrastructure.persistence.migrator status

## migrate-fresh: DESTRUTIVO — recria o schema e reaplica todas as migrações.
migrate-fresh: check-poetry
	cd $(BACKEND_DIR) && $(POETRY) run python -m src.infrastructure.persistence.migrator fresh

## make-migration: Cria um par de migração vazio (uso: make make-migration name=create_x_table).
make-migration: check-poetry
	cd $(BACKEND_DIR) && $(POETRY) run python -m src.infrastructure.persistence.migrator make $(name)

## coverage: Roda os testes unitários com relatório de cobertura no terminal.
coverage: check-poetry
	cd $(BACKEND_DIR) && $(POETRY) run pytest -m unit --cov=src --cov-report=term-missing

# ─── Limpeza ────────────────────────────────────────────────────────────────

## clean: Remove caches de build, teste e bytecode Python do backend.
clean:
	find $(BACKEND_DIR) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf $(BACKEND_DIR)/.pytest_cache $(BACKEND_DIR)/.mypy_cache $(BACKEND_DIR)/.ruff_cache
	rm -rf $(BACKEND_DIR)/.coverage $(BACKEND_DIR)/coverage.xml
