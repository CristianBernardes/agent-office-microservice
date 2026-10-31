# Architecture Decision Records (ADRs)

> Este diretório contém os registros de decisões arquiteturais do **AgentOffice Microservice**.
> Cada ADR documenta uma decisão pontual e, em geral, irreversível (ou de alto custo de reversão),
> com o contexto que a motivou, a decisão tomada e as consequências aceitas.

## Convenções

- Numeração sequencial, sem reaproveitamento (`001`, `002`, ...).
- Status possíveis: `Proposto`, `Aceito`, `Depreciado`, `Substituído por ADR-XXX`.
- Uma ADR só é "Aceita" depois de implementada ou com implementação em andamento no mesmo lote de trabalho.
- Nenhuma feature com impacto arquitetural deve ser implementada sem uma ADR associada (ver `docs/SCRATCHPAD.md`).

## Índice

| ADR | Título | Status |
|-----|--------|--------|
| [001](./001-mqtt-como-barramento-de-mensagens.md) | MQTT como barramento de mensagens | Aceito |
| [002](./002-python-fastapi-no-backend.md) | Python 3.12 + FastAPI no backend | Aceito |
| [003](./003-modelo-de-agentes-por-papel.md) | Modelo de agentes por papel | Aceito |
| [004](./004-artefatos-em-markdown.md) | Artefatos em Markdown | Aceito |
| [005](./005-multiplos-modelos-ollama-por-agente.md) | Múltiplos modelos de LLM por agente | Aceito |
| [006](./006-postgresql-com-pgvector.md) | PostgreSQL com pgvector | Aceito |
| [007](./007-clean-architecture-no-backend.md) | Clean Architecture no backend | Aceito |
| [008](./008-poetry-como-gerenciador-de-dependencias.md) | Poetry como gerenciador de dependências Python | Aceito |
| [009](./009-ollama-externo-ao-docker-compose.md) | Ollama externo ao Docker Compose | Aceito |
| [010](./010-portas-de-container-com-prefixo-70.md) | Convenção de portas de container com prefixo `70` | Aceito |
| [011](./011-tavily-como-provedor-de-busca-web.md) | Tavily como provedor de busca web | Aceito |
| [012](./012-internacionalizacao-pt-en.md) | Internacionalização (pt/en) | Aceito |
| [013](./013-endpoint-para-despachar-objetivos.md) | Endpoint para despachar objetivos a um agente | Aceito |
| [014](./014-repositorios-postgres-e-selecao-por-env.md) | Repositórios PostgreSQL e seleção por `.env` | Aceito |
| [015](./015-frontend-svelte-i18n-e-suporte-backend.md) | Frontend Svelte (pt/en) e suporte de backend | Aceito |
| [016](./016-tarefas-persistencia-casos-de-uso-e-rotas.md) | Tarefas: persistência, casos de uso, ferramentas e rotas | Aceito |
| [017](./017-modelo-de-dados-relacional-unificado.md) | Modelo de dados relacional unificado | Aceito |
| [018](./018-migracoes-estilo-laravel.md) | Migrações de banco estilo Laravel | Aceito |
| [019](./019-objetivos-sessoes-e-chat.md) | Objetivos, sessões e chat | Aceito |
| [020](./020-memoria-semantica-dos-agentes.md) | Memória semântica dos agentes | Aceito |
| [021](./021-mqtt-real-e-contrato-de-topicos.md) | MQTT real e contrato de tópicos | Aceito |
| [022](./022-autonomia-reuniao-de-objetivo.md) | Autonomia: reunião do time sobre um objetivo | Aceito |
| [023](./023-po-cria-backlog-da-reuniao.md) | PO cria o backlog a partir da reunião | Aceito |
| [024](./024-gateway-go-mqtt-kafka.md) | Gateway Go: MQTT → Kafka | Aceito |
| [025](./025-tarefas-vinculadas-a-objetivo-e-revisor.md) | Tarefas vinculadas a objetivo e revisor | Aceito |
| [026](./026-handler-hire-agent.md) | Handler da ferramenta hire_agent | Aceito |
| [027](./027-relacionamentos-entre-agentes.md) | Relacionamentos entre agentes | Aceito |
| [028](./028-reunioes-e-cerimonias.md) | Reuniões e cerimônias (`start_ceremony`) | Aceito |
| [029](./029-reunioes-persistidas-e-rotas-sociais.md) | Reuniões persistidas e rotas sociais | Aceito |
| [030](./030-layout-do-escritorio.md) | Layout do escritório | Aceito |
| [031](./031-feed-de-atividades.md) | Feed de atividades | Aceito |
| [032](./032-debate-multi-rodada.md) | Debate em várias rodadas | Aceito |
| [033](./033-rotas-de-escrita-de-reunioes.md) | Rotas de escrita de reuniões | Aceito |
| [034](./034-pesquisa-de-agentes.md) | Pesquisa de agentes que gera artefatos | Aceito |
| [035](./035-permissoes-assign-complete.md) | Permissões de atribuir e concluir tarefas | Aceito |
| [036](./036-leitura-tolerante-do-ollama.md) | Leitura tolerante da resposta do Ollama | Aceito |
| [037](./037-ferramenta-research.md) | Ferramenta `research` para agentes | Aceito |
| [038](./038-rota-de-interacao.md) | Rota de escrita de relacionamentos | Aceito |
| [039](./039-curingas-no-bus-em-memoria.md) | Curingas MQTT no barramento em memória | Aceito |
| [040](./040-integracao-continua-github-actions.md) | Integração contínua com GitHub Actions | Aceito |
| [041](./041-cobertura-minima-integracao-e-docker-no-ci.md) | Cobertura mínima, integração e build Docker no CI | Aceito |
| [042](./042-configuracao-do-gateway-via-env.md) | Configuração do gateway somente via ambiente | Aceito |
| [043](./043-compose-sem-valores-fixos.md) | docker-compose sem valores fixos | Aceito |
| [044](./044-settings-sem-defaults-de-infraestrutura.md) | Settings sem defaults de infraestrutura | Aceito |
| [045](./045-idempotencia-de-eventos-no-postgres.md) | Idempotência de eventos no Postgres | Aceito |
| [046](./046-consumidor-kafka-mqtt-fora-do-escopo.md) | Consumidor Kafka→MQTT fora do escopo | Aceito |
| [047](./047-frontend-svelte-construido-pelo-assistente.md) | Frontend Svelte 5 construído neste repositório | Aceito |
