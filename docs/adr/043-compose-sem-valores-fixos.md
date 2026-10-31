# ADR-043 — docker-compose sem valores fixos

**Status:** Aceito

## Contexto
O `docker-compose.yml` ainda tinha credenciais do Postgres, portas externas e a URL do Ollama escritas no arquivo.

## Decisão
- Um `.env` na raiz (não versionado, com `.env.example` versionado) alimenta a interpolação `${VAR}` do compose: credenciais do Postgres, portas externas (`HOST_PORT_*`) e a URL do Ollama vista de dentro do container.
- A `DATABASE_URL` do backend é montada no compose a partir das variáveis do Postgres, com host e porta convencionais (`postgres:5432`).
- Portas 70xx existem apenas no host/frontend; dentro dos containers valem as convencionais.
- O CI copia os três `.env.example` antes de subir a stack.

## Consequências
- Trocar credenciais ou portas não exige editar o compose.
- É preciso copiar os `.env.example` antes do primeiro `docker compose up`.
