# Fase 7 — Deploy: Docker, CI/CD e Documentação Final

> Esta fase finaliza o projeto com infraestrutura de deploy reproduzível, pipeline de CI/CD completo e documentação final para o portfólio.

---

## 🎯 Objetivo

- Configurar Docker Compose completo com todos os serviços
- Configurar pipeline CI/CD com GitHub Actions
- Escrever README final de portfólio
- Garantir que o projeto sobe com um único comando

---

## 🐳 Docker Compose Completo

```yaml
# docker-compose.yml
version: "3.9"

services:

  # ─── Banco de Dados ───────────────────────────────────────────
  postgres:
    image: pgvector/pgvector:pg16
    container_name: agentoffice-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB:       agentoffice
      POSTGRES_USER:     agentoffice
      POSTGRES_PASSWORD: agentoffice
    ports:
      - "5434:5432"
    volumes:
      - ./.docker/pgdata:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agentoffice -d agentoffice"]
      interval: 5s
      timeout: 5s
      retries: 10

  # ─── MQTT Broker ──────────────────────────────────────────────
  mqtt:
    image: eclipse-mosquitto:2.0
    container_name: agentoffice-mqtt
    restart: unless-stopped
    ports:
      - "1883:1883"    # MQTT TCP
      - "9001:9001"    # MQTT WebSocket (frontend)
    volumes:
      - ./docker/mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf
      - ./.docker/mqtt:/mosquitto/data
    healthcheck:
      test: ["CMD", "mosquitto_pub", "-h", "localhost", "-t", "health", "-m", "ok"]
      interval: 5s
      timeout: 3s
      retries: 5

  # ─── Backend (Python + FastAPI) ───────────────────────────────
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: agentoffice-backend
    restart: unless-stopped
    env_file: .env
    environment:
      DATABASE_URL: postgresql://agentoffice:agentoffice@postgres:5432/agentoffice
      MQTT_HOST:    mqtt
      MQTT_PORT:    "1883"
      OLLAMA_BASE_URL: http://172.17.0.1:11434   # Ollama no host (Linux)
    ports:
      - "8000:8000"
    volumes:
      - ./workspace:/app/workspace   # Artefatos .md persistidos
    depends_on:
      postgres:
        condition: service_healthy
      mqtt:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ─── Frontend (React + Vite → Nginx) ──────────────────────────
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: agentoffice-frontend
    restart: unless-stopped
    ports:
      - "5173:80"
    depends_on:
      backend:
        condition: service_healthy
    environment:
      VITE_BACKEND_URL:    http://localhost:8000
      VITE_MQTT_BROKER_URL: ws://localhost:9001

volumes:
  # Nenhum volume nomeado — tudo em .docker/ local (gitignored)
```

---

## 🐍 Dockerfile do Backend

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim AS builder

WORKDIR /app

# Instala Poetry
RUN pip install poetry==1.8.3

# Copia manifesto de dependências
COPY pyproject.toml poetry.lock ./

# Instala dependências (sem dev)
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# ─── Imagem final ───────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Copia dependências instaladas
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copia código-fonte
COPY src/ ./src/

# Cria pasta de artefatos
RUN mkdir -p workspace/projects

EXPOSE 8000

CMD ["uvicorn", "src.presentation.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## ⚛️ Dockerfile do Frontend

```dockerfile
# frontend/Dockerfile

# ─── Build ──────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# ─── Serve ──────────────────────────────────────────────────────
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
```

```nginx
# frontend/nginx.conf
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    # SPA — redireciona tudo para index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy para o backend
    location /api/ {
        resolver 127.0.0.11 valid=30s;
        set $backend "backend:8000";
        proxy_pass http://$backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket para o backend
    location /ws {
        resolver 127.0.0.11 valid=30s;
        set $backend "backend:8000";
        proxy_pass http://$backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 🔄 GitHub Actions — CI/CD Completo

```yaml
# .github/workflows/ci.yml
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:

  # ─── Testes Unitários (rápido, sem serviços) ──────────────────
  unit-tests:
    name: 🧪 Testes Unitários
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Instalar dependências
        working-directory: backend
        run: pip install poetry && poetry install

      - name: Rodar testes unitários
        working-directory: backend
        run: poetry run pytest -m unit --cov=src --cov-report=xml -v

      - name: Upload cobertura
        uses: codecov/codecov-action@v4
        with:
          file: backend/coverage.xml

  # ─── Testes de Integração (com serviços) ──────────────────────
  integration-tests:
    name: 🔗 Testes de Integração
    runs-on: ubuntu-latest
    needs: unit-tests

    services:
      postgres:
        image: pgvector/pgvector:pg16
        env:
          POSTGRES_DB:       agentoffice_test
          POSTGRES_USER:     agentoffice
          POSTGRES_PASSWORD: agentoffice
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10

      mqtt:
        image: eclipse-mosquitto:2.0
        ports:
          - "1883:1883"
          - "9001:9001"

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Instalar dependências
        working-directory: backend
        run: pip install poetry && poetry install

      - name: Rodar testes de integração
        working-directory: backend
        run: poetry run pytest -m integration -v
        env:
          DATABASE_URL: postgresql://agentoffice:agentoffice@localhost:5432/agentoffice_test
          MQTT_HOST: localhost
          MQTT_PORT: "1883"

  # ─── Build Docker (verifica que builda) ───────────────────────
  docker-build:
    name: 🐳 Build Docker
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v4

      - name: Build backend
        run: docker build -t agentoffice-backend ./backend

      - name: Build frontend
        run: docker build -t agentoffice-frontend ./frontend

  # ─── Lint e Formatação ────────────────────────────────────────
  lint:
    name: 🔍 Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Instalar ferramentas
        run: pip install ruff mypy

      - name: Ruff (lint + format check)
        working-directory: backend
        run: ruff check src/ && ruff format --check src/

      - name: MyPy (type check)
        working-directory: backend
        run: mypy src/ --strict
```

---

## 📋 `.env.example` Final

```env
# ─── Ollama ───────────────────────────────────────────────────
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBED_MODEL=nomic-embed-text:latest

# ─── Modelos por Papel ────────────────────────────────────────
AGENT_PO_MODEL=nemotron-3.5-bolt:latest
AGENT_SM_MODEL=nemotron-3.5-bolt:latest
AGENT_TECH_LEAD_MODEL=qwen3.6:latest
AGENT_DEV_SENIOR_MODEL=nemotron-3.5-bolt:latest
AGENT_DEV_JUNIOR_MODEL=llama3.2:latest
AGENT_QA_MODEL=qwen3.6:latest
AGENT_DATA_MODEL=qwen3.6:latest
AGENT_HR_MODEL=llama3.2:latest
AGENT_CONSULTANT_MODEL=nemotron-3.5-bolt:latest

# ─── Banco de Dados ───────────────────────────────────────────
DATABASE_URL=postgresql://agentoffice:agentoffice@localhost:5434/agentoffice

# ─── MQTT ─────────────────────────────────────────────────────
MQTT_HOST=localhost
MQTT_PORT=1883

# ─── Provedor Alternativo (opcional) ─────────────────────────
# OPENAI_API_KEY=sk-...
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_MODEL=gpt-4o-mini
```

---

## 🚀 Início Rápido (README Final)

```bash
# 1. Clone
git clone https://github.com/CristianBernardes/agent-office-pro.git
cd agent-office-pro

# 2. Configure
cp .env.example .env
# Edite .env com seus modelos Ollama

# 3. Baixe os modelos
ollama pull nemotron-3.5-bolt:latest
ollama pull qwen3.6:latest
ollama pull llama3.2:latest
ollama pull nomic-embed-text:latest

# 4. Suba tudo
docker compose up --build -d

# 5. Acesse
# Escritório: http://localhost:5173
# API:        http://localhost:8000/docs
# MQTT:       ws://localhost:9001
```

---

## 📁 Estrutura Final do `.gitignore`

```gitignore
# Dados locais
.docker/
workspace/projects/

# Python
__pycache__/
*.pyc
.venv/
dist/
*.egg-info/

# Node
node_modules/
frontend/dist/

# Ambiente
.env
!.env.example

# IDE
.vscode/
.idea/
*.swp
```

---

## ✅ Checklist da Fase 7

- [ ] `docker-compose.yml` com todos os 4 serviços (postgres, mqtt, backend, frontend)
- [ ] `backend/Dockerfile` multi-stage com Poetry
- [ ] `frontend/Dockerfile` multi-stage com Nginx
- [ ] `docker/mosquitto/mosquitto.conf` com WebSocket habilitado
- [ ] `docker/postgres/init.sql` com schema completo + pgvector
- [ ] `.env.example` documentado com todos os modelos
- [ ] `.gitignore` com `.docker/` e `workspace/projects/`
- [ ] GitHub Actions: CI com testes unitários em todo PR
- [ ] GitHub Actions: CI com testes de integração no push para main
- [ ] GitHub Actions: build Docker verificado
- [ ] GitHub Actions: lint e type check com ruff e mypy
- [ ] README.md final com início rápido em 5 passos
- [ ] `docker compose up --build -d` sobe tudo sem erros
- [ ] Acesso em `http://localhost:5173` funciona
- [ ] API docs em `http://localhost:8000/docs` funciona
- [ ] Agentes aparecem no escritório e se comunicam via MQTT
- [ ] Artefatos `.md` são criados em `workspace/projects/`
