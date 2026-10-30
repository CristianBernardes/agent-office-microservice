# ADR-008 — Poetry como Gerenciador de Dependências Python

**Status:** Aceito
**Data:** 2026-10-30
**Autores:** Cristian Bernardes

## Contexto

O backend Python precisa de um gerenciador de dependências que suporte ambientes reprodutíveis
(lockfile), separação clara entre dependências de produção e de desenvolvimento/teste, e boa
integração com ferramentas de build de imagem Docker multi-stage.

## Decisão

Usar **Poetry** como gerenciador de dependências e de build do pacote `backend/`. O arquivo
`pyproject.toml` centraliza metadados do projeto, dependências de produção e grupos de dependências
de desenvolvimento (`test`, `lint`). O `poetry.lock` garante reprodutibilidade entre máquinas de
desenvolvimento, CI (quando configurado pelo mantenedor) e imagem Docker.

## Consequências

### Positivas
- Um único arquivo de configuração (`pyproject.toml`) describe dependências, metadados do pacote e
  configuração de ferramentas (`pytest`, `ruff`, `mypy`), reduzindo a quantidade de arquivos de
  configuração espalhados.
- `poetry export` / `poetry install --only main` permitem builds de imagem Docker enxutas, sem
  dependências de desenvolvimento.

### Negativas / Trade-offs
- Mais uma ferramenta a instalar localmente, além do `pip` — mitigado documentando o passo de
  instalação no `README.md` e automatizando via `make install`.

## Alternativas Consideradas

| Alternativa | Por que foi descartada |
|-------------|-------------------------|
| `pip` + `requirements.txt` puro | Sem lockfile determinístico nativo e sem separação de grupos de dependências de forma padronizada. |
| `pipenv` | Comunidade e ritmo de manutenção menos ativos que o Poetry no momento desta decisão. |
| `uv` | Ferramenta mais recente; Poetry foi escolhido por maturidade e familiaridade mais ampla na comunidade Python neste momento. |
