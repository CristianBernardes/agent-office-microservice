# ─────────────────────────────────────────────────────────────────────────
# AgentOffice Backend — Dockerfile multi-stage
#
# Estágio 1 (builder): instala dependências de produção via Poetry, sem
# dependências de desenvolvimento/teste, para manter a imagem final enxuta.
# Estágio 2 (runtime): copia apenas o necessário para executar o serviço.
# ─────────────────────────────────────────────────────────────────────────

FROM python:3.12-slim AS builder

WORKDIR /app

# Instala o Poetry na mesma versão usada em desenvolvimento, garantindo que a
# resolução de dependências do build seja idêntica à local.
RUN pip install --no-cache-dir poetry==2.5.1

COPY pyproject.toml poetry.lock* ./

# Instala apenas as dependências de produção (grupo padrão), sem os grupos de
# teste/lint, e sem instalar o próprio pacote `backend` ainda (--no-root) —
# o código-fonte só é copiado no passo seguinte.
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root --no-interaction --no-ansi

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY src/ ./src/

# Diretório onde os agentes persistirão artefatos .md (ver ADR-004), criado
# antecipadamente para evitar falha de permissão na primeira escrita.
RUN mkdir -p /app/workspace/projects

EXPOSE 8000

CMD ["uvicorn", "src.presentation.main:app", "--host", "0.0.0.0", "--port", "8000"]
