# ADR-017 — Modelo de dados relacional unificado

## Status
Aceito

## Contexto
O schema cresceu tabela a tabela (ADR-014, ADR-016) sem desenho global. O plano pede ainda memória
semântica (Fase 1/ADR-006), chat, cerimônias/sprints (Fase 3) e idempotência por `event_id`
(Fase 8). O repositório antigo tinha `memories`, `tasks`, `conversations`, `relationships`,
`sessions` e `office_layout`, porém com FKs ausentes, `TEXT` onde cabia `JSONB`/enum e embeddings
em JSON texto. Um banco com integridade declarativa elimina validação e código repetido na aplicação.

## Decisão
1. **Integridade no banco**: PKs `UUID`, FKs (`tasks.assigned_to → agents`,
   `artifacts.author_id → agents`, etc.), `CHECK` para enums (`status`, `role`, `priority`) e faixas
   (`score BETWEEN -1 AND 1`), `NOT NULL` por padrão.
2. **Tabelas** (nomes em inglês, ADR-006):
   - `agents`, `tasks`, `artifacts` (existentes; adicionar FKs/CHECKs e `updated_at` com trigger).
   - `sessions(session_id, scenario, started_at, ended_at, highlights JSONB)`.
   - `messages(message_id, session_id → sessions, sender_id → agents NULL=usuário,
     recipient_id → agents NULL=broadcast, topic, kind, content, created_at)`: substitui
     `conversations`; é o histórico de chat e a fonte do handler `send_message`.
   - `memories(memory_id, agent_id → agents, content, memory_type, importance, embedding
     vector(N), session_id, created_at)` com índice HNSW (`vector_cosine_ops`).
     `N` = 768 (`nomic-embed-text`), configurado no `.env` (`EMBEDDING_DIMENSIONS`) e aplicado ao aplicar o schema.
   - `relationships(agent_a, agent_b, score, status)` com `CHECK (agent_a < agent_b)` e PK
     composta: um par, uma linha.
   - `meetings` (ver seção abaixo): suporte a `start_ceremony`.
   - `activity_events(event_id, agent_id → agents NULL, kind, payload JSONB, created_at)`: feed
     do SystemLog (também publicado em `office/events`).
   - `office_layout(name UNIQUE, layout JSONB, updated_at)`: o Editor de Layout da UI antiga
     persistia no banco; o backend só guarda e serve o JSON (o cenário é feito no frontend).
3. **Idempotência (Fase 8) desde já**: `event_id UUID UNIQUE NULL` em `tasks`, `artifacts`,
   `messages`, `memories`; evita `ALTER` posterior.
4. **Schema versionado**: `schema.sql` vira arquivos ordenados em `persistence/migrations/NNN_*.sql`,
   aplicados de forma idempotente por `apply_schema` e registrados em `schema_migrations`.
5. **Menos código**: repositórios Postgres compartilham uma base genérica
   (`PostgresRepository`: upsert/`find_by_id`/`list_all` por metadados de tabela); cada repositório
   concreto só declara tabela, colunas e mapeamento entidade↔linha.
6. **Extensões**: `vector` e `pg_trgm` (busca textual em `messages`/`artifacts`).

## Fluxo de trabalho orientado a objetivos (o coração do modelo)
Exemplo: *"Crie um produto digital para eu vender 5 unidades por dia por R$ 39,90"* digitado no chat.
O banco precisa registrar **quem fez o quê, em qual etapa e por quê**:

1. **`goals`**(`goal_id`, `session_id`, `requested_by`, `text`, `status` open/done/cancelled, `outcome`,
   `created_at`, `closed_at`): todo pedido do usuário vira um objetivo. O `product_owner` o recebe,
   o `scrum_master` convoca a reunião e o trabalho se desdobra em tarefas.
2. **`tasks`** ganha `goal_id → goals`, `parent_task_id → tasks`, `created_by`, `reviewer_id → agents`,
   `blocked_reason`, `position` (ordem no Kanban) e `CHECK (reviewer_id <> assigned_to)`.
   A coluna do Kanban é o próprio `status` (backlog, todo, in_progress, in_review, done, blocked).
   `task_dependencies(task_id, depends_on_id)` modela bloqueios entre tarefas.
3. **`task_transitions`**(`transition_id`, `task_id`, `from_status`, `to_status`, `actor_id`,
   `actor_role`, `note`, `created_at`): trilha imutável de cada movimento de cartão, com o ator da
   etapa. Alimenta o histórico do card, o feed e métricas (lead time, retrabalho por QA).
4. **Responsabilidade por etapa** (regra de domínio, testada; o banco guarda o ator):
   | Transição | Quem pode |
   |---|---|
   | → backlog / todo (priorizar) | `product_owner` (e `product_consultant` sugere) |
   | todo → in_progress | executor atribuído (dev_senior, dev_junior, data_analyst, product_consultant, tech_lead) |
   | in_progress → in_review | o executor |
   | in_review → done / volta a in_progress | `qa_engineer` ou `tech_lead` (nunca o próprio executor) |
   | qualquer → blocked | `scrum_master` (remove impedimentos) |
   | contratar para cobrir falta de papel | `hr_manager` (`hire_agent`) |
5. **`meetings`**(`meeting_id`, `goal_id`, `kind` planning/refinement/daily/review/retro/brainstorm,
   `organizer_id`, `status`, `started_at`, `ended_at`, `summary`, `decisions JSONB`) +
   `meeting_participants(meeting_id, agent_id)`; `messages.meeting_id` guarda a conversa. Substitui
   a antiga `ceremonies`. O `scrum_master` agenda; as decisões viram tarefas e artefatos.
6. **`artifacts`** ganha `goal_id`, `task_id`, `meeting_id` e `artifact_type` (research, prd,
   pricing, adr, plan, meeting_notes, retro). O conteúdo `.md` é gravado em
   `workspace/projects/<goal_id>/` (já no `.gitignore`, ADR-004); a tabela guarda metadados e o caminho.
7. **`tool_invocations`**(`invocation_id`, `agent_id`, `tool`, `arguments JSONB`, `result`,
   `status`, `task_id`, `created_at`): auditoria de pesquisas na web, escrita de notas etc.
   Também alimenta o `activity_events`.
8. **Vida dos agentes**: `agents` ganha `activity` (idle/thinking/talking/working/in_meeting/walking/
   resting), `mood`, `energy`, `station` (ponto do layout) e `last_active_at`. É isso que a cena
   desenha e que o laço de pensamento usa para decidir o próximo passo (ADR de autonomia, a seguir).

Percurso esperado do exemplo: usuário → `messages`/`goals` → PO cria tarefas de descoberta
(`product_consultant` e `data_analyst` pesquisam nicho, concorrência e preço de R$ 39,90 ×
5/dia ≈ R$ 5.985/mês; resultados em `artifacts`) → `scrum_master` abre `meetings` de planning →
`tech_lead` define arquitetura (ADR em `artifacts`) → devs executam → `qa_engineer` revisa →
`done` e `goals.outcome` preenchido. Tudo rastreável em `task_transitions`.

## Paridade com os painéis da UI antiga (README do `agent-office`)
| Painel / recurso antigo | Suporte de backend |
|---|---|
| TaskBoard (Kanban, atribuir pela UI) | `tasks` + `GET/POST /tasks`, `assign`, `complete` e mudança de status (ADR-016) |
| Chat (usuário ↔ agentes, conversas entre agentes) | `messages` + `POST/GET /messages`, handler `send_message` |
| Inspector (agente, memórias, relações) | `GET /agents/{id}`, `memories`, `relationships` |
| SystemLog (feed com deduplicação) | `activity_events` + tópico MQTT `office/events` (dedup por `event_id`) |
| Editor de layout | `office_layout` + `GET/PUT /layout` |
| Contratação dinâmica | handler `hire_agent` (herda modelo do `.env`, prompts pt/en) |
| Memória com importância + busca semântica | `memories` + `RecallMemoryUseCase` |
| Modo foco, balões de emoção, caminhar até mesas | só frontend, alimentado por eventos MQTT (WebSocket 9001) |
| Ferramentas (código em sandbox, busca, notas) | `ToolRegistry`; busca via Tavily (ADR-011) |
| Injeção manual de tarefas / sessões | `POST /tasks` e `sessions` |

## Consequências
- Dados inválidos são rejeitados pelo banco, reduzindo checagens e testes duplicados.
- Migrações explícitas tornam a evolução (Fase 7/8) rastreável.
- Mudar a dimensão do embedding exige nova migração.
- Testes de integração (`make up`) cobrem FKs/CHECKs; unitários seguem com `FakePool`.

## Ordem de implementação
1. Concluir Tarefas (ADR-016) sobre o novo schema (migração 002).
2. Base genérica + migrações.
3. `sessions` + `messages` + `send_message`.
4. `memories` (`IMemoryRepository`, `RecallMemoryUseCase`).
5. `goals`, `task_transitions`, `meetings`, `tool_invocations`; `relationships`; `hire_agent`.
6. ADR de autonomia (laço de pensamento dos agentes) e ADR-018 (contrato MQTT).
