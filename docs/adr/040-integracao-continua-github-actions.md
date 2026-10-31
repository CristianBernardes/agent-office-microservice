# ADR-040 — Integração contínua com GitHub Actions

**Status:** Aceito

## Contexto
Projeto open source com contribuições externas: a qualidade (formatação, lint, tipos, testes) dependia de cada colaborador rodar `make check` localmente.

## Decisão
Workflow `.github/workflows/ci.yml` com dois jobs: `backend` (ruff format/check, mypy, pytest unitário) e `gateway` (go vet e go test). Testes de integração ficam fora do CI por exigirem a stack Docker e o Ollama (`make test-integration` local).

## Consequências
Todo push e PR é validado automaticamente; testes de integração continuam manuais.
