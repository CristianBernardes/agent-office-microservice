# SCRATCHPAD — Agent Office Microservice

## ⚠️ OBSERVAÇÃO OBRIGATÓRIA: PADRÕES DE QUALIDADE E BOAS PRÁTICAS

**Toda implementação deve seguir rigorosamente os princípios de engenharia de software, priorizando qualidade, legibilidade, manutenibilidade, segurança, escalabilidade e consistência arquitetural.**

- **SOLID:** aplique rigorosamente os cinco princípios de SOLID, respeitando responsabilidades bem definidas, baixo acoplamento e alta coesão.
- **Design Patterns:** utilize padrões de projeto quando forem adequados ao problema, evitando complexidade desnecessária, abstrações prematuras e overengineering.
- **Clean Code:** escreva código limpo, legível, expressivo e autodocumentado, com nomes significativos, funções pequenas, responsabilidades únicas e fluxo de execução claro.
- **Formatação obrigatória:** execute `make format` após as alterações para garantir a padronização automática do código. Nunca ignore esse comando.
- **DRY (Don't Repeat Yourself):** evite duplicação de lógica, regras de negócio e código. Extraia componentes reutilizáveis quando houver uma justificativa real.
- **KISS (Keep It Simple, Stupid):** prefira soluções simples, explícitas e fáceis de manter, sem sacrificar a qualidade arquitetural.
- **YAGNI (You Aren't Gonna Need It):** implemente apenas o que é necessário para os requisitos atuais, sem criar funcionalidades ou abstrações especulativas.
- **Separação de responsabilidades:** mantenha as camadas de apresentação, domínio, aplicação e infraestrutura devidamente isoladas, respeitando a arquitetura existente.
- **Princípios de domínio:** preserve as regras de negócio em seus respectivos contextos, evitando espalhá-las entre interfaces, controllers, componentes e serviços genéricos.
- **Consistência arquitetural:** antes de implementar qualquer funcionalidade, analise a estrutura do projeto, identifique os padrões existentes e siga as convenções estabelecidas. Não introduza novas abordagens sem justificativa técnica.
- **Tratamento de erros:** implemente tratamento explícito e apropriado de exceções, estados inválidos, falhas de integração e condições inesperadas. Nunca silencie erros ou utilize valores artificiais para mascarar falhas.
- **Segurança:** valide entradas, respeite as permissões e os limites de confiança, proteja dados sensíveis e aplique o princípio do menor privilégio. Nunca exponha credenciais, tokens ou informações confidenciais.
- **Testes automatizados:** crie ou atualize testes unitários, de integração e de ponta a ponta conforme o escopo e o risco da alteração. Teste também cenários negativos, limites e casos excepcionais.
- **Regressão:** preserve o comportamento existente fora do escopo da mudança. Não remova funcionalidades, regras de negócio ou validações sem autorização explícita.
- **Performance:** evite consultas redundantes, processamento desnecessário, problemas de N+1, renderizações excessivas e alocações evitáveis. Otimize com base em evidências, sem comprometer a legibilidade.
- **Tipagem e contratos:** utilize tipagem forte sempre que disponível, respeite interfaces e contratos existentes e evite tipos genéricos, coerções implícitas e o uso indiscriminado de `any`.
- **Legibilidade e manutenção:** evite funções gigantes, classes com múltiplas responsabilidades, condicionais excessivamente complexas, números mágicos, comentários redundantes e dependências desnecessárias.
- **Dependências:** reutilize as bibliotecas já adotadas pelo projeto sempre que possível. Não adicione dependências externas sem necessidade comprovada e avaliação de seus impactos.
- **Refatoração responsável:** refatore somente o necessário para viabilizar a solução ou melhorar objetivamente a qualidade do código relacionado. Evite alterações abrangentes e não relacionadas ao requisito.
- **Compatibilidade:** respeite as versões das linguagens, frameworks, bibliotecas, APIs e contratos existentes, considerando os impactos sobre os demais módulos e consumidores.
- **Logs e observabilidade:** registre informações úteis para diagnóstico, sem expor dados sensíveis ou gerar ruído excessivo.
- **Documentação:** atualize a documentação técnica quando houver mudanças relevantes em contratos, arquitetura, configurações, fluxos de negócio ou procedimentos de execução.
- **Decisões do dono do produto são incontestáveis:** o que o Cristian decidir deve ser executado exatamente como pedido, sem contestar, reinterpretar, limitar ou "melhorar" por conta própria. Dúvidas de entendimento podem ser perguntadas antes; depois da decisão, só se executa.

### Fluxo obrigatório de trabalho

1. **Analisar:** compreenda os requisitos, investigue o código existente e identifique os componentes e as regras de negócio envolvidos antes de alterar qualquer arquivo.
2. **Planejar:** defina a solução mais simples e consistente com a arquitetura atual, considerando impactos, dependências, riscos e cenários de erro.
3. **Implementar:** desenvolva uma solução coesa, reutilizável quando apropriado, sem duplicações desnecessárias ou desvios dos padrões do projeto.
4. **Validar:** execute `make format` e os testes, linters, verificações de tipos e demais validações disponíveis e pertinentes.
5. **Revisar:** verifique possíveis regressões, problemas de segurança, inconsistências arquiteturais, código morto, alterações não relacionadas e falhas nos cenários excepcionais.
6. **Concluir:** informe objetivamente o que foi implementado, quais validações foram executadas e eventuais limitações ou pendências.

### Regra inegociável

**Nunca considere uma implementação concluída apenas porque funciona no cenário principal.** A solução deve atender aos requisitos, respeitar a arquitetura existente, preservar os comportamentos esperados, possuir testes adequados e passar pelas verificações de qualidade aplicáveis.

Não ignore falhas de testes, não desabilite verificações para fazer o pipeline passar e não declare que uma validação foi executada com sucesso sem ter confirmado seu resultado.

**Commits sem coautoria do Copilot:** nenhum commit pode ter o Copilot (ou qualquer assistente de IA) como coautor. Não inclua trailers `Co-authored-by:` referentes ao Copilot na mensagem de commit. Se a ferramenta adicionar esse trailer automaticamente, remova-o antes de commitar (ou use `git commit --amend` / `git rebase` para retirá-lo de commits já criados e ainda não enviados).

**Qualidade de código não é opcional. Toda alteração deve ser implementada com responsabilidade técnica, simplicidade, consistência e foco na manutenção de longo prazo.**

## COMMITS
**Todos os commits que fizer, este arquivo deve ser atualizado e enviado junto**
---

## Histórico de Implementação

### Rodada 1 — Fase 0 + Fase 1 do plano de migração (2026-10-30)

**Escopo entregue:**

- **Fundação documental** (`docs/adr/`, `docs/rfc/`, `docs/design/`): 10 ADRs cobrindo MQTT,
  FastAPI, modelo de agentes, artefatos Markdown, múltiplos LLMs, PostgreSQL+pgvector, Clean
  Architecture, Poetry, Ollama externo ao Compose e convenção de portas `70xx`. 3 RFCs definindo os
  contratos de protocolo de mensageria, sistema de artefatos e ciclo de vida de agente. 3 Design
  Docs com a visão geral de arquitetura, modelo de domínio e fluxo de mensagens.
- **Backend Python 3.12 + FastAPI** em `backend/`, com Clean Architecture completa:
  - `domain/`: entidades `Agent`, `Task`, `Artifact` (com transições de estado validadas),
    value objects `AgentId`/`TaskId`/`ArtifactId`, interfaces `ILlmAdapter`/`IMessageBus`/
    `IAgentRepository`, exceções de domínio.
  - `application/`: casos de uso `HireAgentUseCase` e `FireAgentUseCase`.
  - `infrastructure/`: `InMemoryAgentRepository`, `InMemoryMessageBus`, `MqttMessageBus` (via
    `aiomqtt`), `MockLlmAdapter`, `OllamaAdapter` (via `httpx`, URL sempre vinda de `.env`),
    configuração centralizada via `pydantic-settings`, conexão PostgreSQL via `asyncpg`.
  - `presentation/`: rotas FastAPI (`/health`, `/agents`), injeção de dependência via *factories*,
    bootstrap da aplicação.
  - Dockerfile multi-stage próprio do serviço (`backend/Dockerfile`), `.env.example` funcional.
- **Testes**: 40 testes unitários (domínio, aplicação, infraestrutura in-memory, rotas HTTP) + 1
  teste de integração marcado para o `MqttMessageBus` real. Cobertura de 83% no primeiro corte.
- **Qualidade de código**: `ruff check` e `ruff format` sem nenhum apontamento; `mypy --strict` sem
  nenhum erro em 37 arquivos-fonte.
- **Infraestrutura**: `docker-compose.yml` atualizado com `postgres` (`pgvector/pgvector:pg16`,
  porta `7034`) e `backend` (porta `7001`), mantendo `mosquitto` já existente (`7083`/`7000`).
  `OLLAMA_BASE_URL` sobrescrito explicitamente para `http://172.17.0.1:11434` dentro do Compose —
  o Ollama nunca é declarado como serviço deste projeto, roda sempre no host.
  Stack validada de ponta a ponta: `make up` sobe tudo, `/health` e `POST /agents` respondem,
  extensão `vector` habilitada no Postgres.
- **Makefile**: preenchido com todos os comandos (`install`, `run`, `up`/`down`/`restart`/`logs`/`ps`,
  `format`, `lint`, `type-check`, `check`, `test`/`test-unit`/`test-integration`/`coverage`, `clean`).

**Convenções fixadas nesta rodada** (ver ADRs e commits):
- Identificadores de código (variáveis, funções, classes) em inglês; comentários de bloco/docstrings
  em português.
- Tabelas e colunas de banco de dados em inglês (ainda não há tabelas de domínio nesta rodada —
  apenas a extensão `pgvector` foi habilitada).
- Zero hardcode de configuração: tudo vem de `backend/.env` (com `.env.example` funcional).
- Toda porta externa de container deste projeto começa com `70` (ver ADR-010).

**Pendente para rodadas futuras** (conforme `docs/migration-plan/`): Fase 2 (MQTT ligado aos casos de
uso de pensamento de agente), Fase 3 (personas, prompts, ferramentas por papel), Fase 4 (sistema de
artefatos completo), Fase 5 (múltiplos modelos por papel via `.env`), repositórios PostgreSQL
concretos, frontend (aguardando pacote de sprites).

### Rodada 2 — Correções pontuais + decisões fechadas para a próxima rodada (2026-10-30)

**Correções aplicadas e já commitadas/enviadas para `origin/develop`:**

- Poetry não estava instalado na máquina do Cristian (`make install` falhava com
  `poetry: not found`). Instalado oficialmente via `curl -sSL https://install.python-poetry.org |
  python3 -` em `~/.local/bin/poetry`. Adicionado alvo `check-poetry` no `Makefile` (commit
  `d86ba17`) que valida a presença do Poetry antes de qualquer comando que dependa dele, com
  mensagem de erro clara (comando de instalação + link da doc) em vez de falha crua do shell.
- `OLLAMA_BASE_URL` padronizado para `http://172.17.0.1:11434` em `backend/.env.example`,
  `backend/src/infrastructure/config/settings.py` (valor de fallback) e no ADR-009 (commit
  `b99b2b5`). Antes havia inconsistência entre o valor do `.env.example` (`localhost`) e o valor
  real usado no `docker-compose.yml` (`172.17.0.1`), o que gerava confusão. Agora os dois lugares
  usam o mesmo valor por padrão, já que o fluxo de trabalho padrão do projeto é sempre via
  `make up` (Docker Compose). `localhost:11434` continua documentado como alternativa válida
  apenas para quem executa o backend fora de container, na mesma máquina.

**⚠️ IMPORTANTE PARA RETOMAR O TRABALHO:** o Cristian editou manualmente o arquivo
`backend/.env` (não versionado, está no `.gitignore`) durante a sessão anterior, ajustando
`OLLAMA_BASE_URL` para `172.17.0.1:11434` antes mesmo da correção acima ser proposta. Esse `.env`
local já está correto — não precisa de nenhuma ação adicional nele.

**Decisões fechadas para a PRÓXIMA rodada de implementação (ainda não iniciada — nenhum código
desta rodada foi escrito, apenas decidido via perguntas ao Cristian):**

A próxima rodada vai ligar o "escritório vivo": o Cristian descreve um objetivo de produto (ex.:
"Time, crie um produto SaaS de nicho específico para vender 5 unidades/dia a R$39,90...") e os
agentes devem pesquisar, debater e gerar documentos de decisão reais em disco.

1. **Escopo da próxima rodada:** Fase 2 + Fase 3 + Fase 4 do plano de migração, todas juntas:
   - Fase 2 — `AgentThinkUseCase` real, ligado ao `MqttMessageBus` (publicação de `thought`,
     `action`, `status` nos tópicos já definidos na RFC-001).
   - Fase 3 — as 9 personas (Product Owner, Scrum Master, Tech Lead, Dev Sênior, Dev Júnior, QA
     Engineer, Analista de Dados, RH, Consultor de Produto), cada uma com system prompt próprio
     (ver `docs/migration-plan/fase-3-personas/README.md` para os prompts de referência já
     redigidos em português) e ferramentas específicas por papel (tabela de permissões já existe
     no plano de migração — `write_artifact`, `review_artifact`, `approve_artifact`, `create_task`,
     `assign_task`, `complete_task`, `send_message`, `web_search`, `hire_agent`,
     `start_ceremony`).
   - Fase 4 — sistema completo de artefatos: ciclo de vida DRAFT→IN_REVIEW→APPROVED→ARCHIVED
     (já implementado na entidade `Artifact` da Fase 1) ligado a um `WriteArtifactUseCase` real que
     persiste tanto metadados no Postgres quanto o arquivo `.md` físico em
     `workspace/projects/{sprint}/`, notificando via MQTT.

2. **Ferramenta de pesquisa web (`web_search`):** usar a API da **Tavily** (feita especificamente
   para agentes de IA/LLM, camada gratuita de 1000 buscas/mês). Precisa de `TavilySearchAdapter`
   implementando uma nova interface de domínio (ex.: `IWebSearchAdapter`), configurado via
   `TAVILY_API_KEY` no `.env` — como é uma chave paga/pessoal, o `.env.example` NÃO pode ter uma
   chave real funcional (diferente do Ollama); deve documentar a variável e instruções de onde
   obter a chave gratuita. Para testes automatizados sem chave real, criar um `MockSearchAdapter`
   seguindo o mesmo padrão já usado pelo `MockLlmAdapter`.

3. **Ponto de entrada do comando do Cristian para o time:** NENHUM endpoint HTTP novo nesta
   próxima rodada. O frontend fica para quando chegarmos nessa fase (fora de escopo agora, o
   Cristian vai comprar um pacote de sprites prontos antes). A validação ponta a ponta
   (comando → pensamento → pesquisa → artefato em disco) deve ser feita **apenas por testes
   automatizados** (unitários + integração), chamando os casos de uso diretamente no código —
   sem necessidade de expor rota REST para isso ainda.

4. **Preferência de frontend já registrada para quando chegar a hora** (não implementar agora):
   o Cristian está avaliando Svelte, Vue.js, React, SolidJS, Angular e Qwik, nessa ordem de
   preferência pessoal. Nenhuma decisão final tomada ainda — só uma lista de candidatos para
   referência futura.

**Próximo passo imediato ao retomar:** escrever os ADRs/RFCs desta nova decisão (seguindo a regra
do fluxo obrigatório deste documento — ADR antes do código) cobrindo: `IWebSearchAdapter` +
Tavily, o fluxo completo `AgentThinkUseCase`, e o ciclo de produção de artefato ponta a ponta. Só
depois disso implementar as 9 personas, os adapters e os casos de uso, com testes unitários cada
passo, seguindo exatamente o mesmo padrão de qualidade da Rodada 1 (`make check` limpo antes de
cada commit, commits atômicos sem coautoria, `SCRATCHPAD.md` atualizado a cada commit).

### Rodada 3 — Fase 2 (MQTT) + Fase 3 (Personas) + Fase 4 (Artefatos) do plano de migração,
### decisão de frontend (Svelte) e organização dos assets de pixel-art (2026-10-30)

**Escopo entregue (backend, seguindo exatamente as decisões fechadas na Rodada 2):**

- **ADR-011** (`docs/adr/011-tavily-como-provedor-de-busca-web.md`): decisão de usar a API da
  Tavily para a ferramenta `web_search`, com `IWebSearchAdapter` no domínio,
  `TavilySearchAdapter` (infraestrutura, via `httpx`) e `MockSearchAdapter` para testes. A chave
  `TAVILY_API_KEY` é pessoal/paga — documentada em `.env.example` sem valor real, exigida apenas na
  primeira chamada de `search()` (nunca na construção do adaptador, para não quebrar fluxos que não
  usam busca web).
- **RFC-001, RFC-002 e RFC-003** atualizadas de "Proposto" para "Aceito (parcialmente implementado)",
  com seções "Atualização — Rodada 3" descrevendo o estado final de cada contrato nesta rodada.
- **Fase 2 — `AgentThinkUseCase`** (`application/agents/agent_think_use_case.py`): liga
  `ILlmAdapter` + `IMessageBus` + `IPromptProvider` + `ToolRegistry`. Publica, em sequência,
  `office/agents/{id}/status` (retain=true), `office/agents/{id}/thought` (QoS 0) e
  `office/agents/{id}/action` (QoS 1), e delega `tool_call` ao `ToolRegistry` quando presente.
- **Fase 3 — Personas**:
  - `application/tools/tool_permissions.py`: enum `ToolName` com as 11 ferramentas da tabela de
    referência e `ROLE_TOOL_PERMISSIONS` transcrita literalmente dessa tabela para os 9 papéis.
  - `infrastructure/prompts/{role}.md`: os 9 system prompts em português, copiados fielmente do
    texto de referência já redigido na Fase 3 (um ajuste pontual: "TypeScript (React)" trocado para
    "TypeScript (Svelte)" no prompt do Tech Lead, para refletir a decisão de frontend desta mesma
    rodada — ver abaixo).
  - `domain/interfaces/prompt_provider.py` + `infrastructure/prompts/file_prompt_provider.py`:
    `IPromptProvider`/`FilePromptProvider`, lê e cacheia os templates Markdown por papel.
  - `application/tools/tool_registry.py`: `ToolRegistry` valida `Role` × `ToolName` antes de
    delegar a `write_artifact`/`review_artifact`/`approve_artifact`/`web_search`. As demais
    ferramentas da tabela (`create_task`, `assign_task`, `complete_task`, `send_message`,
    `hire_agent`, `start_ceremony`, `read_artifact`) já constam em `ToolName` e na tabela de
    permissões, mas levantam `ToolNotImplementedError` — não têm caso de uso próprio ainda
    (YAGNI: nenhum caso de uso desta rodada as produz).
  - **Nota de alcance:** o Big Five (`Personality`) já existe desde a Fase 1 na entidade `Agent` —
    esta rodada não precisou adicionar um `ROLE_PERSONALITIES` separado porque nenhum caso de uso
    desta rodada consome personalidade por papel; mantido como ponto de atenção para quando essa
    necessidade surgir.
- **Fase 4 — Artefatos**:
  - `domain/interfaces/artifact_repository.py`: `IArtifactRepository` (save/find_by_id/list_all).
  - `application/artifacts/write_artifact_use_case.py`,
    `application/artifacts/review_artifact_use_case.py`,
    `application/artifacts/approve_artifact_use_case.py`: os três casos de uso do ciclo de vida do
    artefato, cada um publicando `office/artifacts/created` ou `office/artifacts/updated` via
    `IMessageBus` (envelope padrão extraído para `application/common/message_envelope.py`, usado
    também pelo `AgentThinkUseCase` — DRY).
  - `infrastructure/filesystem/markdown_artifact_writer.py`: escreve o `.md` real em
    `workspace/projects/{sprint}/{arquivo}.md` com frontmatter YAML.
  - `infrastructure/persistence/in_memory_artifact_repository.py`: metadados em memória + delega a
    escrita em disco ao `MarkdownArtifactWriter` — `PostgresArtifactRepository` concreto permanece
    pendente para quando houver um consumidor real de persistência relacional (YAGNI, ver ADR-006).
- **Injeção de dependência** (`presentation/dependencies.py`): todas as novas peças conectadas —
  `get_message_bus` (`InMemoryMessageBus` ainda é o padrão deste processo; `MqttMessageBus` real
  exige bootstrap de conexão, fora do escopo desta injeção síncrona), `get_llm_adapter`
  (`OllamaAdapter`), `get_artifact_repository`, `get_prompt_provider`, `get_web_search_adapter`
  (`TavilySearchAdapter`), `get_tool_registry` e `get_agent_think_use_case`.
- **Configuração**: `tavily_api_key` adicionado a `Settings` (padrão `""`, nunca obrigatório na
  inicialização do processo) e documentado em `backend/.env.example`/`backend/.env` com
  placeholder vazio.
- **Testes**: 20 novos testes unitários cobrindo `TavilySearchAdapter` (sucesso, erro HTTP e chave
  ausente — HTTP mockado via `pytest-mock`, sem rede real), `MockSearchAdapter`,
  `MarkdownArtifactWriter`, `InMemoryArtifactRepository`, os três casos de uso de artefato,
  `tool_permissions` (cobertura dos 9 papéis), `ToolRegistry` (permissão concedida/negada/ferramenta
  não implementada), `FilePromptProvider`, `build_message_envelope` e `AgentThinkUseCase`
  (status/thought/action publicados, erro em agente `OFFLINE`, execução de `tool_call` ponta a
  ponta gerando um `.md` real). Total: **81 testes passando** (80 unitários + 1 de integração MQTT
  real, validado com `make up` ativo).
- **Qualidade de código**: `make check` (format + lint + type-check + test) limpo — `ruff
  format`/`ruff check` sem apontamentos, `mypy --strict` sem erros em 59 arquivos-fonte.
- **Validação ponta a ponta conforme decisão da Rodada 2:** nenhum endpoint HTTP novo foi
  exposto para o fluxo comando → pensamento → pesquisa → artefato; a validação é inteiramente por
  testes automatizados chamando os casos de uso diretamente (`AgentThinkUseCase` com `tool_call` de
  `write_artifact` gerando um arquivo `.md` real em disco, dentro do teste).

**Decisões de arquitetura fechadas nesta sessão (fora do código Python, registradas para quando a
Fase 8/frontend chegarem):**

1. **Frontend definido: Svelte + TypeScript** (não mais uma lista de candidatos em aberto — decisão
   final do Cristian). Critério de escolha: reatividade granular com runes, melhor equilíbrio para
   interface dinâmica, personagens e painéis. Documento `docs/design/arquitetura-geral.md`
   atualizado pelo próprio Cristian com o novo diagrama de componentes (Interface Web Svelte →
   Gateway Go → MQTT → Backend Python / Serviços Go). `docs/migration-plan/README.md` (tabela
   "Stack Final" e árvore de pastas) atualizado de React/Zustand para Svelte/runes. O prompt do
   Tech Lead (`infrastructure/prompts/tech_lead.md`) e o texto de referência da Fase 3
   (`docs/migration-plan/fase-3-personas/README.md`) também corrigidos para citar Svelte em vez de
   React na "stack disponível".
   **Pendente:** as árvores de arquivo detalhadas (`.tsx`, `Zustand`) em
   `docs/migration-plan/fase-0-fundacao/README.md`, `fase-1-arquitetura/README.md`,
   `fase-7-deploy/README.md` e `fase-8-microservicos/README.md` ainda não foram reescritas para
   Svelte — são documentos de fases futuras de frontend, fora do escopo desta rodada de backend;
   reescrever quando a implementação do frontend realmente começar.
2. **Gateway Go SEM autenticação/autorização** — decisão explícita do Cristian: o projeto é open
   source, mantido por doações, sem contas de usuário nem dados sensíveis de terceiros a proteger.
   `docs/design/arquitetura-geral.md` atualizado: removida a linha "Autenticação e autorização" do
   bloco do Gateway de Comunicação no diagrama, e adicionada a seção "Decisão: sem
   autenticação/autorização no Gateway Go" explicando o motivo e deixando explícito que qualquer
   necessidade futura de controle de acesso deve ser resolvida fora do código deste gateway (proxy
   reverso, rede privada), nunca adicionando autenticação sem uma nova decisão explícita do dono do
   produto.
3. **Assets de pixel-art comprados e organizados em `offices/`** (pasta na raiz do repositório
   `agent-office-edicao-brasileira`, fora de `agent-office-microservice/` — mesmo repositório Git
   do monorepo, já versionada): `Character Generator 2.0 Linux Build/`, `Modern_Interiors_RPG_Maker_Version/`
   (zipado), `Modern_Office_Revamped_v1.2/`, `moderninteriors-win/`, `PixelOffice/`. São 3 pacotes
   comprados (não apenas 1), o que dá liberdade para compor o escritório final combinando tiles de
   fontes diferentes quando o frontend (Fase 1 do plano, após Svelte estar configurado) começar a
   consumi-los via Phaser.js. Nenhuma integração de código com esses assets foi feita nesta rodada —
   é só o registro de que já estão disponíveis e onde estão.
4. **Identidade visual sugerida por papel** (registrada para quando o frontend mapear sprites de
   `offices/` a cada persona — nenhuma implementação ainda):

   | Papel (`Role`) | Identidade visual sugerida |
   |----------------|------------------------------|
   | `PRODUCT_OWNER` | Profissional com prancheta ou documentos |
   | `SCRUM_MASTER` | Facilitador com quadro de tarefas |
   | `TECH_LEAD` | Profissional diante de um computador com diagramas |
   | `DEV_SENIOR` | Desenvolvedor experiente em uma estação de trabalho |
   | `DEV_JUNIOR` | Desenvolvedor em uma estação de aprendizado |
   | `QA_ENGINEER` | Profissional com checklist de testes |
   | `DATA_ANALYST` | Analista com gráficos e indicadores |
   | `HR_MANAGER` | Profissional com documentos de equipe |
   | `PRODUCT_CONSULTANT` | Consultor com relatórios e gráficos de mercado |

**Pendente para a próxima rodada** (conforme `docs/migration-plan/`): Fase 5 (múltiplos modelos de
LLM por agente via `.env`, já parcialmente coberta pelo `OllamaAdapter`/ADR-005, falta a *factory*
que resolve o modelo por papel), `PostgresArtifactRepository`/`PostgresAgentRepository` concretos,
endpoint(s) HTTP ou outro ponto de entrada para o Cristian de fato disparar um objetivo de produto
para o time pensar (hoje só é possível via teste automatizado ou código Python direto), e o início
do frontend Svelte (Fase 1 do plano) consumindo os assets já organizados em `offices/`, aplicando a
identidade visual sugerida por papel listada acima.
