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
7. **Registrar e publicar (sem relatórios ao dono do produto):** a cada alteração, atualize este `docs/SCRATCHPAD.md` (rodada, tabela de commits, estado atual, limitações) e faça commit + push com ele incluído. Não envie relatórios nem peça confirmação ao Cristian: trabalhe continuamente, até o fim de todo o backlog, sem parar entre rodadas.

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

### Rodada 4 — Fase 5: modelo de LLM por papel via `.env` (2026-10-31)

- `domain/interfaces/llm_adapter_resolver.py`: porta `ILlmAdapterResolver.resolve(role)`.
- `infrastructure/llm/role_based_llm_adapter_resolver.py`: resolve papel → modelo (override do
  `.env` ou `OLLAMA_MODEL` padrão), cria o adaptador via factory injetada e reutiliza adaptadores
  de papéis que compartilham o mesmo modelo.
- `Settings`: variáveis `AGENT_*_MODEL` (PO, SM, TECH_LEAD, DEV_SENIOR, DEV_JUNIOR, QA, DATA, HR,
  CONSULTANT), vazias por padrão (= modelo padrão) + `role_models()`. Documentadas em
  `.env.example` e `.env`.
- `AgentThinkUseCase` agora recebe `llm_adapter_resolver` e escolhe o adaptador por `agent.role`;
  `get_llm_adapter` foi substituído por `get_llm_adapter_resolver` em `presentation/dependencies.py`.
- Testes: +3 do resolvedor, +1 de `Settings.role_models`; testes do `AgentThinkUseCase` adaptados.
  `make format`, `lint`, `type-check` limpos; 84 unitários passando. O teste de integração MQTT
  falha apenas porque o broker não estava no ar (`make up` necessário).
- **Ainda pendente:** `PostgresArtifactRepository`/`PostgresAgentRepository`, ponto de entrada para
  o Cristian disparar objetivos, provedor OpenAI-compatible (não decidido), início do frontend Svelte.

### Rodada 5 — i18n pt/en (2026-10-31)

- ADR-012. `domain/localization/` (`Language`, catálogo `MESSAGES`, `translate`).
- `DomainError(message_key, **params)` com `localized(language)`; todos os erros de entidades/casos
  de uso migrados para chaves. `InvalidValueError` também é `ValueError`.
- Prompts movidos para `prompts/pt/` e criados `prompts/en/` (9 papéis);
  `IPromptProvider.get_system_prompt(role, name, language)`, cache por (papel, idioma).
- `OFFICE_LANGUAGE` (pt|en, padrão en) em `Settings`/`.env`; `AgentThinkUseCase` recebe `language`.
- API: `Accept-Language` localiza o `detail` do 404 de `fire`.
- Testes: catálogo completo, parse/Accept-Language, erros localizados, prompts nos 2 idiomas,
  rota com 2 idiomas, settings. 107 unitários passando.
- **Pendente:** Postgres repos, entrada para disparar objetivos, OpenAI-compatible, frontend Svelte
  (já nascendo com i18n pt/en).

### Rodada 6 — Endpoint para despachar objetivos (2026-10-31)

- ADR-013. `POST /agents/{id}/think` `{"context": "..."}` → `{thought, action, target, tool_call}`;
  404 (agente inexistente) e 409 (agente OFFLINE), ambos localizados via `Accept-Language`.
- `DispatchGoalUseCase` (busca → pensa → volta a IDLE → persiste → publica status; também volta a
  IDLE se o LLM falhar). `Agent.finish_thinking()`/`is_thinking()`; chave i18n `agent.not_thinking`.
- Publicação de status extraída para `application/common/agent_status_publisher.py` (DRY).
- Testes: caso de uso (4), entidade (2), rota (4). `make format`/`lint`/`type-check` limpos;
  117 unitários passando.
- **Pendente:** Postgres repos, OpenAI-compatible (não decidido), frontend Svelte (pt/en).

### Rodada 7 — Repositórios PostgreSQL (2026-10-31)

- ADR-014. `PostgresAgentRepository` e `PostgresArtifactRepository` (asyncpg, upsert), esquema
  idempotente `schema.sql` aplicado no startup (`apply_schema`). `PERSISTENCE_BACKEND=memory|postgres`
  (padrão `memory`; valor inválido falha); `lifespan` abre/fecha a pool e falha rápido sem banco.
- Testes: repositórios com pool falsa (agente/artefato, nulos, linha corrompida, ausente), seleção
  por env, lifespan, setting inválida; integração real em `make test-integration`.
  `make format`/`lint`/`type-check` limpos; 134 unitários passando.
- **Pendente:** OpenAI-compatible (não decidido), frontend Svelte (pt/en).

### Rodada 8 — Desenho do banco e do fluxo de trabalho (2026-10-31)

- ADR-017 (Aceito): modelo relacional unificado orientado a objetivos: `goals`, `tasks` (Kanban por
  `status` + revisor), `task_transitions` (ator por etapa), `meetings`, `messages`, `memories`
  (pgvector 768), `relationships`, `tool_invocations`, `activity_events`, `office_layout`; `event_id`
  para idempotência (Fase 8). Matriz de responsabilidade por papel/etapa definida.
- ADR-015: frontend Svelte descartado nesta fase (o cenário/front serão feitos pelo autor; ativos em
  `frontend/images/sprites/office/`); mantidos `GET /agents` e CORS configurável.
- ADR-016 (Tarefas): código parcial (repositórios) ainda NAO commitado; será refeito sobre o
  schema do ADR-017.
- **Próximo:** migrações + base genérica Postgres; Tarefas/goals/transições; chat; memória; ADR-018
  (contrato MQTT); ADR de autonomia; Fase 8 (Go + Kafka); frontend.

- Convenção: **um Dockerfile por microserviço** (`backend/Dockerfile`, futuramente `frontend/Dockerfile`,
  `gateway/Dockerfile`), nunca um Dockerfile único na raiz. Ativos de arte agora em `frontend/images/`
  (esqueleto do frontend).

### Rodada 9 — Migrações estilo Laravel e schema completo (2026-10-31)

- ADR-018 (Aceito): pares `AAAA_MM_DD_HHMMSS_nome.up.sql/.down.sql`, tabela `migrations` com batch,
  transação por migração. CLI `migrator` + `make migrate|migrate-rollback|migrate-status|migrate-fresh|
  make-migration name=`. `lifespan` roda `migrate`; `schema.sql`/`apply_schema` removidos;
  `ops/postgres/init.sql` só com extensões (`vector`, `pg_trgm`).
- 9 migrações cobrindo o ADR-017 (agents com "vida", sessions/goals, tasks+dependências+transições,
  meetings, messages, artifacts, memories+relationships, tool_invocations/activity_events/office_layout).
  Validadas em Postgres real (pgvector): up e down de todas.
- Testes do migrador (ordem, batch, falha não registrada, rollback, nome inválido, par up/down).
  152 unitários passando; format/lint/mypy limpos. Bancos de dev antigos: `make migrate-fresh`.
- Também entra o código parcial de Tarefas (ADR-016: repositórios); casos de uso/rotas a seguir.
- **Próximo:** Tarefas (casos de uso, transições, rotas, tools), goals/chat, memória, ADR-019 MQTT.

### Rodada 10 — Tarefas: casos de uso, rotas e tools (ADR-016)

- Casos de uso `CreateTask`/`AssignTask`/`CompleteTask` (tarefa nasce em backlog; atribuir valida o
  agente antes; concluir devolve o agente a IDLE; evento em `office/tasks/updated`).
- Rotas `GET/POST /tasks`, `POST /tasks/{id}/assign|complete` (404/409 localizados via `Accept-Language`).
- Tools `create_task`, `assign_task`, `complete_task` no `ToolRegistry`; chave i18n `task.not_found`.
- 167 unitários passando; format/lint/mypy limpos.
- **Próximo:** `task_transitions` + matriz papel×estágio, goals/chat (`send_message`), memória, ADR-019 MQTT.

### Rodada 11 — Histórico de transições e matriz papel × estágio (ADR-016, adendo)

- `task_transitions` gravada em create/assign/complete/move (ator + papel + nota).
- `MoveTaskUseCase` + `POST /tasks/{id}/move` (403 papel sem permissão, 409 movimento inválido,
  404) e `GET /tasks/{id}/transitions`; mensagens pt/en.
- Matriz em `domain/policies/task_workflow.py`; `move_to(DONE)` agora preenche `completed_at`
  (respeita o CHECK do banco).
- 188 unitários passando; format/lint/mypy limpos.
- **Próximo:** goals/sessões + chat (`send_message`), memória (pgvector), MQTT real, autonomia dos agentes.

### Rodada 12 — Objetivos, sessões e chat (ADR-019)

- Domínio `Session`/`Goal`/`ChatMessage`, `IChatRepository` (em memória + Postgres).
- `SubmitGoalUseCase` (publica `office/goals/created`; o loop de autonomia futuro consome) e
  `SendMessageUseCase` (usuário ou agente; publica `office/chat/message`).
- Rotas `POST/GET /goals`, `POST /messages`, `GET /sessions/{id}/messages`; 404 localizado pt/en.
- Tool `send_message` no `ToolRegistry`; chave i18n `chat.session_not_found`.
- 204 unitários passando; format/lint/mypy limpos.
- **Próximo:** memória (pgvector), MQTT real (ADR-020), autonomia dos agentes, gateway Go/Kafka.

### Rodada 13 — Memória semântica (ADR-020)

- Domínio `Memory`/`MemoryType`, `IMemoryRepository` (em memória + Postgres com pgvector `<=>`).
- `RememberUseCase` e `RecallMemoryUseCase` vetorizam com o LLM do papel do agente.
- Rotas `POST/GET /agents/{id}/memories` e `POST .../recall`; 404 localizado pt/en, 422 na validação.
- 212 unitários passando; format/lint/mypy limpos.
- **Próximo:** MQTT real (ADR-021), autonomia dos agentes, gateway Go/Kafka.

### Rodada 14 — MQTT real e contrato de tópicos (ADR-021)

- `MESSAGE_BUS_BACKEND=memory|mqtt`; `lifespan` conecta/desconecta o barramento.
- Listener MQTT agora casa curingas (`+`, `#`) via `topic_matches`.
- Contrato de tópicos documentado na ADR-021; testes com cliente falso (sem broker).
- **Próximo:** loop de autonomia dos agentes (consome `office/goals/created`), gateway Go/Kafka.

### Rodada 15 — Autonomia: reunião do time sobre um objetivo (ADR-022)

- `GoalMeetingUseCase`: ao receber `office/goals/created`, os papéis presentes falam em ordem fixa
  (PO → consultor → analista → tech lead → dev sênior → QA → SM), cada um vendo a ata até ali; falas vão
  ao chat e à memória; ata gravada em `projects/{goal_id}/meeting.md` (workspace, gitignored).
- Resiliente: falha de um agente não derruba a reunião; sem agentes, nada acontece.
- Ligado por `AUTONOMY_ENABLED` (padrão `false`); handler dispara em background task.
- 229 testes unitários. **Próximo:** PO decompor o objetivo em tarefas, gateway Go/Kafka.

### Rodada 16 — PO cria o backlog da reunião (ADR-023)

- Após a ata, o PO cria no backlog uma tarefa por contribuição dos demais papéis (determinístico).
- 231 testes unitários. **Próximo:** gateway Go/Kafka (Fase 8), integração com Postgres/Mosquitto reais.

### Rodada 17 — Gateway Go MQTT → Kafka (ADR-024)

- `gateway/` (Go 1.24): assina `office/#` (QoS 1), valida o envelope, deduplica por `event_id` no Redis (SetNX 24h) e publica em `office.events` (chave = `agent_id`); inválidos vão para `office.events.dlq`.
- Compose: `kafka` (KRaft), `kafka-init` (cria os tópicos), `redis`, `gateway`.
- 4 testes Go (`go test ./...` ok). Dockerfile próprio. **Próximo:** goal_id/revisor nas tarefas, relationships, meetings/hire_agent, layout.

### Rodada 18 — Tarefas ligadas ao objetivo e ao revisor (ADR-025)

- `Task.goal_id` e `Task.reviewer_id` persistidos no Postgres; a reunião vincula o backlog ao objetivo.
- 231 testes unitários. **Próximo:** relationships, meetings/hire_agent, layout, testes de integração.

### Rodada 19 — Handler `hire_agent` (ADR-026)

- RH/PO/Tech Lead contratam agentes pela ferramenta (personalidade neutra, modelo padrão do Ollama). `start_ceremony` segue sem handler.
- 232 testes unitários. **Próximo:** relationships, meetings, layout, testes de integração.

- Documentação: READMEs pt/en com Kafka/Redis nas portas e status do gateway Go.

### Rodada 20 — Relacionamentos entre agentes (ADR-027)

- `Relationship` (par ordenado, score [-1,1], status derivado), `IRelationshipRepository` (memória + Postgres upsert), `RecordInteractionUseCase`/`ListRelationshipsUseCase`.
- `GoalMeetingUseCase` registra +0.05 para cada par que falou na reunião. 245 testes unitários.
- Pendente: rota HTTP de leitura, interações negativas (rivalidade), teste contra Postgres real.
- **Próximo:** meetings + `start_ceremony`, layout, activity_events.

### Rodada 21 — Modelos por papel (`.env` / `.env.example`)

- PO e Tech Lead: `qwen3.6`; Dev Sênior e Analista de Dados: `nemotron-3.5-bolt`; SM, Dev Júnior e RH: `gpt-oss:20b`; QA e Consultor: `sorc/qwen3.5-claude-4.6-opus`. Embeddings: `nomic-embed-text`.
- Só configuração (o `.env` é ignorado pelo git; o `.env.example` é versionado).

### Rodada 22 — Reuniões e `start_ceremony` (ADR-028)

- Domínio `Meeting` (`MeetingKind`, `MeetingStatus`, `finish`), `MeetingId`, porta `IMeetingRepository`, repositórios em memória e Postgres (upsert + participantes em transação).
- Casos de uso `StartCeremonyUseCase`, `FinishMeetingUseCase`, `ListMeetingsUseCase`; handler `start_ceremony` no `ToolRegistry` (Scrum Master & cia) e wiring em `dependencies.py`.
- Mensagens pt/en: `meeting.not_found`, `meeting.cannot_finish`, `meeting.no_participants`.
- 252 testes unitários, ruff e mypy limpos.
- Pendente: `GoalMeetingUseCase` ainda não persiste suas reuniões como `Meeting`; sem rota HTTP; repo Postgres de reuniões sem teste de integração.

## Rodada 23 — reuniões persistidas + rotas sociais (ADR-029)

- `AGENT_DATA_MODEL=nemotron3:latest` (Data Analyst) em `.env` e `.env.example`.
- `GoalMeetingUseCase` grava `Meeting` PLANNING concluída (opcional, falha tolerada).
- Rotas: `GET /agents/{id}/relationships`, `GET /goals/{id}/meetings`.
- 256 testes unitários, ruff e mypy limpos.
- Próximo: `office_layout`, `activity_events`, debate multi-rodada, testes de integração.

## Rodada 24 — layout do escritório (ADR-030)

- `OfficeLayout` (JSON opaco), `ILayoutRepository`, repos em memória e Postgres (upsert em `office_layout`).
- Rotas `GET/PUT /layout/{name}` com erros pt/en.
- 261 testes unitários, ruff e mypy limpos. Repo Postgres não testado contra banco real.
- Próximo: `activity_events`, debate multi-rodada, testes de integração.

## Rodada 25 — feed de atividades (ADR-031)

- `ActivityEvent`, `IActivityRepository`, repos em memória e Postgres (`activity_events`).
- `register_activity_feed` assina os tópicos de domínio no `lifespan`; `GET /activity?limit=`.
- Tópicos por agente (`agents/+/thought|action`) entram no feed desde a Rodada 40 (ADR-039).
- 264 testes unitários, ruff e mypy limpos.
- Próximo: debate multi-rodada, testes de integração, RFCs/Design Docs, refresh do "Estado atual".

## Rodada 26 — debate multi-rodada (ADR-032)

- `MEETING_ROUNDS` (1–5, padrão 1) em settings e `.env.example`; `GoalMeetingUseCase(rounds=)`.
- Rodadas ≥2 usam o rótulo "debate" (pt/en) com a ata acumulada; backlog = 1 tarefa por agente (última fala); vínculos e `Meeting` com participantes únicos.
- 279 testes unitários, ruff e mypy limpos.
- Próximo: agentes pesquisando/escrevendo `.md`, testes de integração (Postgres/Mosquitto), RFCs/Design Docs, refresh do "Estado atual".

## Rodada 27 — integração real (Postgres + Mosquitto)

- `docker compose up -d postgres mosquitto` + `pytest -m integration`: 7 testes passando (MQTT, agente, artefato, relacionamento, reunião, layout, feed).
- Corrigidos dois testes de integração que estavam obsoletos (`Role.QA`, FK do autor do artefato).
- Repos Postgres de relacionamento/reunião/layout/atividade agora validados contra banco real. Também validados: chat/goal/mensagens, tarefa e memória com busca pgvector (10 testes de integração no total). Kafka/Redis/gateway validados na Rodada 37.

## Rodada 28 — gateway Go validado ponta a ponta

- `docker compose build gateway` OK; stack kafka+redis+kafka-init+gateway sobe.
- MQTT → gateway → Kafka verificado: envelope válido chega em `office.events`; duplicata (mesmo `event_id`) descartada pelo Redis; envelope inválido vai para `office.events.dlq`.
- Bug corrigido: o gateway subia antes dos tópicos existirem (`Unknown Topic Or Partition`); agora `depends_on: kafka-init: service_completed_successfully`.

## Rodada 29 — Rotas de escrita de reuniões (ADR-033)
- `POST /meetings` (inicia cerimônia) e `POST /meetings/{id}/finish` (encerra), localizadas pt/en.
- 272 testes unitários, ruff e mypy limpos.

## Rodada 30 — Pesquisa de agentes (ADR-034)
- `ResearchTopicUseCase`: busca web → LLM do papel redige relatório (JSON `thought`=Markdown) → artefato `analysis` em `workspace/research/<slug>.md`, fontes anexadas.
- `POST /research`. Falha na busca não aborta. pt/en.
- 279 testes unitários, ruff e mypy limpos.

## Rodada 31 — RFC-004 e Design Doc de autonomia
- `docs/rfc/004-contrato-da-api-http.md` (todas as rotas) e `docs/design/autonomia-e-reunioes.md`.

## Rodada 32 — Permissões em assign/complete (ADR-035)
- `can_assign` / `can_complete` na política de domínio; 403 localizado. 282 testes unitários.

## Rodada 33 — Ollama tolerante a respostas não-JSON (ADR-036)
- `_parse_structured_reply`: JSON direto, objeto extraído do texto ou texto livre como `thought`. 286 testes unitários.

## Rodada 34 — Passe final nos READMEs
- Seção "API HTTP" (tabela de rotas, autonomia, `MEETING_ROUNDS`, pesquisa) em pt e en.

## Rodada 35 — Ferramenta `research` (ADR-037)
- `ToolName.RESEARCH` para papéis com `web_search`; handler delega a `ResearchTopicUseCase`.

## Rodada 36 — Rota de interação (ADR-038)
- `POST /relationships/interactions` (delta −1..1; 422 para agentes iguais).

## Rodada 37 — Integração do gateway Kafka
- `tests/integration/test_gateway_kafka_integration.py`: MQTT→gateway→`office.events` (válido) e `office.events.dlq` (inválido); pula se Kafka/gateway não estiverem no ar. RFC-004 e READMEs com a rota de interações.

## Rodada 38 — Upsert de goals já fechados no Postgres
- `closed_at` agora é preenchido no INSERT quando o status não é `open` (antes violava o CHECK). Teste de integração novo (13 no total).

## Rodada 39 — Mock de embedding com 768 dimensões
- `MockLlmAdapter.embed` agora gera 768 dimensões (igual a `vector(768)`).

## Rodada 40 — Curingas no bus em memória e feed por agente (ADR-039)
- `topic_matches` compartilhado; feed assina `office/agents/+/thought|action`.

## Rodada 41 — Cobertura do ToolRegistry
- Testes de review/approve de artefato e create/assign/complete de tarefa via registry (293 unit; cobertura total 96%).

## Rodada 42 — Cobertura de factories Postgres e falhas de efeitos colaterais
- `set_database_pool` agora descarta o cache de TODOS os repositórios (antes só agent/artifact).
- Testes das factories Postgres e das falhas toleradas da reunião (304 unit).

## Rodada 43 — CI (ADR-040)
- `.github/workflows/ci.yml`: backend (ruff, mypy, pytest unit) e gateway (go vet/test).

## Rodada 44 — Badge de CI nos READMEs
- Badge do workflow `ci.yml` em `README.md` e `README.en.md`.

## Rodada 46 — Revisão de limitações e backlog
- Limitações e backlog do SCRATCHPAD atualizados com o estado real.

## Rodada 47 — CI completo (ADR-041)
- `fail_under = 85` na cobertura (atual 96,6%); job `integration` no push para `main`; job `docker` verifica o build das imagens.

## Rodada 48 — Início rápido atualizado
- READMEs pt/en listam todos os modelos Ollama do `.env.example`, a stack completa e `make migrate`.

## Rodada 49 — E2E PO → Dev → QA
- `backend/tests/e2e/test_po_dev_qa_flow.py`: fluxo completo pela API (aprovação, rejeição do QA, dev não aprova o próprio trabalho). 309 unit/e2e.

## Rodada 50 — Gateway sem valores fixos (ADR-042)
- `gateway/internal/config` (obrigatório, sem defaults), `gateway/.env.example`, compose com `env_file`, teste de concorrência do dedupe, CI copia o `.env`.

## Rodada 51 — Correção do .env do gateway
- Dentro do container valem hosts e portas convencionais (`mosquitto:1883`, `kafka:9092`, `redis:6379`); portas 70xx só para host/frontend. Compose sem sobrescritas. Tavily URL/timeout viraram settings.

## Rodada 52 — compose sem valores fixos

ADR-043. `.env.example` na raiz (Postgres, portas externas, URL do Ollama); `docker-compose.yml` usa `${VAR}`; `DATABASE_URL` montada com host `postgres:5432`. CI copia os três `.env.example`.

## Rodada 53 — Settings sem defaults de infraestrutura

ADR-044. `database_url`, `mqtt_host`, `mqtt_port`, `ollama_base_url` obrigatórios; testes definem via `tests/conftest.py`. 309 unit, mypy e ruff limpos.

## Rodada 54 — MQTT fora do compose

`MQTT_HOST`/`MQTT_PORT` removidos do `docker-compose.yml`; `backend/.env.example` traz `mosquitto:1883` (container). Fora do Docker, use localhost:7083.

## Rodada 55 — Quick Start

README copia `.env.example` da raiz, do backend e do gateway.

## Rodada 56 — idempotência no Postgres

ADR-045. `ON CONFLICT (event_id) DO NOTHING` em activity_events; teste de integração (14 integração, 309 unit).

## Rodada 57 — decisão sobre Kafka→MQTT

ADR-046: não implementar; gateway permanece unidirecional. Replay fica como evolução futura.

## Rodada 58 — Frontend Svelte 5 (ADR-047)

- Frontend completo em `frontend/` (Svelte 5 + TS + Vite, Vitest + Testing Library): mapa do escritório com sprites animados por status, quadro Kanban, time e tarefas atribuídas (andamento), conversas do time, logs em tempo real (MQTT/WS + atividade), formulário de objetivo e de nova tarefa (agentes quebram em subtarefas e escrevem os `.md` via tools), i18n pt/en.
- Doação: Pix (QR) em português, PayPal em inglês (`VITE_PAYPAL_URL`, opcional); popup na primeira visita e a cada `VITE_DONATION_REMINDER_DAYS` dias; botão "Apoiar" sempre no cabeçalho. QR copiado de `frontend/images/` no `predev`/`prebuild` (original intacto).
- Configuração só por `VITE_*` (`frontend/.env.example`). 41 testes, `svelte-check` e build limpos.
- Formulário "Contratar agente" (`POST /agents`, modelo padrão `VITE_DEFAULT_LLM_MODEL`); verificado no navegador contra a stack local: agentes sentam nas mesas certas, sprites ok. Imagem antiga do backend causava CORS — rebuild resolveu.
- Dockerfile (Node→nginx, `VITE_*` como build args), serviço `frontend` no compose (`HOST_PORT_FRONTEND=5173`, casa com CORS) e job `frontend` no CI.

## Rodada 64 — Escritório vivo

- Backend: `WorkLoopUseCase` (ADR-048) move tarefas backlog→todo→in_progress→in_review→done sozinho; `WORK_LOOP_INTERVAL_SECONDS` (0 = desligado).
- Frontend: agentes andam até colegas (folha `deslocamento_entre_salas`), conversam e voltam; `VITE_WANDER_INTERVAL_MS`; matiz distinto por índice dentro do cargo; cargo exibido no rótulo.

## Rodada 65 — Responsável obrigatório e idioma

- `MoveTaskUseCase._ensure_owner`: ao sair do backlog a tarefa recebe o dev/TL menos carregado; sem ninguém, permanece no backlog com erro localizado. Work loop respeita o responsável.
- `FilePromptProvider` anexa diretiva final de idioma (pt/en) a todo prompt de sistema; atas antigas em inglês são anteriores à correção.
- Testes: TestOwnerRule, diretiva de idioma, ajustes em e2e/rotas.

## Rodada 66 — Todos os sprites em uso

- `spriteFor(..., alt)`: idle→`interagindo_com_objetos`, thinking/working→`outra_postura_de_trabalho`; `OfficeMap` alterna a pose por agente a cada `VITE_WANDER_INTERVAL_MS`. Agora as 8 folhas de cada cargo são usadas.

## Rodada 67 — Cargos traduzidos nas atas

- Cabeçalhos da ata usam o cargo localizado (pt/en) em vez do id do papel. Suíte unitária: 330 testes verdes.

## Rodada 68 — Sprite bugado

- `interagindo_com_objetos.png` tem 48 quadros, mas só os 24 primeiros são o personagem (o resto é um carrinho). `SpriteSheet.total` separa quadros animados de quadros da folha.

## Rodada 69 — Reset e time

- Banco (`.docker/pgdata`) e `workspace/` zerados; 11 agentes contratados (todos os cargos) e 12 tarefas de backlog criadas via API pelo PO.
- Os `.md` gerados (ata, tarefas, pesquisa) seguem `OFFICE_LANGUAGE` / idioma do objetivo.

## Rodada 70 — Kanban profissional

- Backend: `Task.created_at/started_at` expostos na API (lead/cycle time).
- Frontend: `lib/metrics.ts` (WIP, vazão, lead time médio/P85, cycle time, aging) com testes; limites `VITE_WIP_LIMIT_*` (0 = sem limite); coluna `n/limite` em vermelho ao exceder; cartão mostra cargo do responsável e idade.
- Doação: `VITE_PAYPAL_URL` configurado; PayPal aparece também em pt.

## Rodada 71

Cerimônia de planejamento antes do trabalho (ADR-049): facilitador PO/SM, artefato `planning/`, divisão de tarefas em partes para ninguém ficar ocioso. Testes atualizados.

## Rodada 72

Auditoria SOLID/DRY/YAGNI: divisão de tarefas extraída para `domain/services/task_splitter.py` (com testes), helper `_speak` elimina duplicação no ciclo, RFC-005 e design doc `ciclo-de-trabalho.md`.

## Rodada 73

Removido texto de debug `wanderIntervalMs=...` que aparecia solto na página (App.svelte).

## Rodada 74

Reunião/ciclo falhavam com `httpx.ReadTimeout` (120s fixo): agora `OLLAMA_REQUEST_TIMEOUT_SECONDS` (padrão 600) vem do `.env`.

## Rodada 75

Modal de doação passa a contar a história do projeto (chave `donationThanks`, pt/en).

## Rodada 76

O planejador pede ao LLM `Título | Entregável` por subtarefa (`parse_subtasks`); sem linhas suficientes, mantém a numeração mecânica. O título/cabeçalho do artefato de planejamento agora segue o idioma (`planning_title`).

## Rodada 77

O ciclo de trabalho falhava com `SessionNotFoundError`: a sessão fixa do chão do escritório nunca era criada. `WorkLoopUseCase` agora recebe `IChatRepository` e a cria na primeira fala. Time contratado usando os modelos por cargo do `.env` (`AGENT_*_MODEL`).

## Rodada 78

Makefile: `format-go` (gofmt), `format-frontend` (prettier) e `format-all`.

## Rodada 79 — Etapa de teste antes da revisão

- ADR-050: novo status `testing`; fluxo `in_progress → testing (dev) → in_review (QA) → done`. QA escreve o plano de testes (`tests/<id>.md`) no idioma do escritório.
- Backend: enum, política de transições, migration, `_test` no ciclo de trabalho; testes unitários/e2e atualizados.
- Frontend: coluna "Em teste"/"Testing", limite `VITE_WIP_LIMIT_TESTING`, progresso e métricas.

## Rodada 80 — Coluna Concluído

- A grade do Kanban tinha 5 colunas; com `testing` a sexta (Concluído) quebrava de linha. Ajustada para 6.

## Rodada 81 — Duração máxima da sprint

- `SPRINT_MAX_DAYS` (padrão e teto 15) vai no prompt do planejamento e no markdown da sprint, no idioma escolhido. Teste unitário incluído.

## Rodada 82 — Kanban compacto

- Colunas com `minmax(0, 1fr)` e menos espaçamento para as 6 caberem numa linha; frontend reconstruído.

## Rodada 83-84 — Workspace fixo, personagens vivos e gráficos Kaizen

- `workspace/` não é mais criado em runtime (erro se ausente); subpastas e arquivos nascem com 777; `.gitkeep` versionado.
- Personagens fazem pausas aleatórias (descansar/pensar) com balões pt/en (`pickBreak`, testado).
- Botão "📊 Gráficos" ao lado do "Cartão mais antigo" abre modal Kaizen (fluxo por coluna, lead time, idade dos cartões).

## Pendências finais (Rodada 85 em diante)

- [x] 1. Idioma das tasks/decisões acompanha a troca pt/en (ADR-051: `PUT /office/language`, trava de confirmação ao trocar).
- [x] 2. Refazer o banco: recontratar o time de 11 agentes (modelos do `.env`) e recriar as 15 tarefas do comitê (script de seed versionado).
- [x] 3. Validar o fluxo ao vivo: in_progress → testing → in_review → done, `.md` no idioma certo, limite de 15 dias da sprint, pausas dos personagens.
- [x] 4. Migração `testing`: confirmar o nome da constraint `task_status_check` num Postgres real.
- [x] 5. Atualizar `docs/design/ciclo-de-trabalho.md` com a etapa de teste.
- [x] 6. Conferir no navegador: 6 colunas em uma linha e modal de gráficos Kaizen.

## Rodada 86 — idioma em tempo de execução e trava

- `OfficeLanguage` (domínio) + `GET/PUT /office/language`; o ciclo de trabalho lê o idioma a cada passo.
- Frontend envia o idioma ao carregar e ao trocar; `LanguageSwitcher` pede confirmação (aviso de possível corrupção de `.md` já escritos).
- Testes: backend 354 unit, frontend 62.

## Rodada 87 — observabilidade (ADR-052)

- Backend `GET /metrics` (prometheus_client): HTTP por rota/status/latência + gauges `office_tasks` e `office_agents`.
- Gateway Go `:9100/metrics` (`METRICS_ADDR`): recebidas/produzidas/erros por tópico.
- Compose: kafka-ui, prometheus, grafana (dashboard provisionado), postgres/redis/kafka exporters e cAdvisor; portas e credenciais no `.env`.
- Validado: todos os alvos do Prometheus `up`; Kafka UI 200; Grafana no ar. Testes: backend 356 unit, gateway ok.

## Rodada 88 — volumes sempre em `.docker/`

- Regra: todo volume do compose é bind mount dentro de `./.docker/` (ignorado pelo git). Nada de volumes nomeados/anônimos.
- Novo serviço `docker-dirs-init` (busybox) cria `prometheus`, `grafana`, `redis`, `kafka` e `mosquitto` com permissão 777 antes dos demais (o `pgdata` fica intocado: o Postgres exige 0700).
- Volumes nomeados do Prometheus/Grafana removidos; Redis, Kafka e Mosquitto agora persistem em `.docker/`.

## Rodada 89 — artefatos do workspace

- Os 3 `.md` de pesquisa (`clean-architecture`, `kafka`, `tema`) regenerados pelos agentes passam a ser commitados; a partir daqui `git add -A` inclui o `backend/workspace`.

## Rodada 90 — seed, migração e design doc

- `scripts/seed_team.py`: contrata 11 agentes (modelos `AGENT_*_MODEL` do `.env`) e cria as 15 tarefas do comitê.
- Migração `testing` aplicada num Postgres real (banco temporário): constraint `task_status_check` correta, `'testing'::task_status` válido.
- Fluxo ao vivo observado (todo/in_progress/testing em andamento após um goal).
- `docs/design/ciclo-de-trabalho.md` descreve a etapa de teste.
- Navegador: 6 colunas na mesma linha e botão de gráficos Kaizen conferidos; checklist final concluído.

## Rodada 91 — READMEs

- READMEs pt/en com 3 capturas, tecnologias, instalação do Ollama (Linux/Windows), nº de IAs e hardware mínimo.
- Botão Contratar: lista de modelos já vem de `GET /models` (Ollama `/api/tags`); campo de texto só como fallback se o Ollama estiver fora.

## Rodada 93 — transparência nas doações

- Modal de doação (pt/en) e READMEs (pt/en) dizem abertamente: o autor se endividou com a saúde da filha e precisa de ajuda; a doação é voluntária e o projeto não depende dela.

## Rodada 94 — modal de confirmação

- Novo `ConfirmModal.svelte` (alertdialog acessível, Esc/clique fora cancelam, foco inicial, textos pt/en) substitui o `window.confirm` do `LanguageSwitcher`.
- Testes do `LanguageSwitcher` atualizados (abre o modal, confirma e cancela). 62 testes e `svelte-check` ok.

## Rodada 95 — bug de sprites

- Causa: cada folha concatena 4 direções (direita, costas, esquerda, frente; as de 12 quadros têm 2); a animação percorria a tira inteira e o personagem girava.
- `spriteFor` agora devolve `start`/`count` da direção; o CSS anima só esse trecho. Parado = frente; ao andar a direção vem do trajeto (`directionBetween` em `layout.ts`).
- Testes novos em `sprites.test.ts` e `layout.test.ts` (64 ok).

## Rodada 96 — README: alerta e fluxo dos containers

- `images/alert.png` adicionada às capturas de `README.md` e `README.en.md`.
- Nova seção "Fluxo dos containers" / "Container flow" com um fluxograma Mermaid de todos os serviços do `docker-compose.yml` (docker-dirs-init, frontend, backend, mosquitto, gateway, kafka, kafka-init, redis, postgres, kafka-ui, exporters, cadvisor, prometheus, grafana, mais o Ollama externo), um diagrama de sequência do caminho de um objetivo e uma tabela de funções.

## Rodada 97 — Sprite do carrinho e SQL de tarefas

- Bug: a pose alternativa de `idle` (`interagindo_com_objetos`, 48 quadros) tratava a folha como 4 direções × 12, então a direção "frente" apontava para os quadros 36–47 (carrinho de props), mostrando uma fatia estranha no lugar do personagem. Os 24 primeiros quadros são as 4 direções × 6; os 24 últimos são o carrinho. Corrigido com `frames: 24, total: 48`; teste de regressão em `sprites.test.ts`.
- Nova pasta `sql/` (`tasks.pt.sql`, `tasks.en.sql`, `clear_tasks.sql`, `README.md`) para criar as 15 tarefas de uma vez no Postgres; testada em banco temporário com as migrações.

### Rodada 98 — Postgres/MQTT por padrão, títulos limpos (ADR-053)

- `PERSISTENCE_BACKEND=postgres` e `MESSAGE_BUS_BACKEND=mqtt` em `backend/.env.example`; migrações
  rodam no startup (lifespan). Dados sobrevivem a reinícios do backend.
- `tests/conftest.py` força backends em memória: testes independem do `.env` (360 passam).
- `task_title.clean_title`: remove `[papel]`, markdown e linhas só de separadores (`---`).

### Rodada 99 — Grafana nos READMEs

- `images/grafana.png` adicionado com legenda nos READMEs pt/en.

### Rodada 100 — Doação centralizada

- Tabela Pix/PayPal e agradecimento dentro de `<div align="center">` nos READMEs pt/en.

### Rodada 101 — Higienização, isolamento dos testes de integração

- MQTT→Kafka verificado: `office.events` recebe mensagens, DLQ vazia, gateway inscrito em `office/#`.
- `clean_body` remove separadores/cercas de código nas bordas da descrição das tarefas.
- Testes de integração Postgres (11 ok) agora usam o banco `<db>_test` (criado sob demanda); `fresh` não apaga mais o banco real.
- Agente "Mem" residual removido; time re-semeado (11 agentes, 15 tarefas).
- Limitação: Mermaid dos READMEs ainda não validado por renderização.

### Rodada 102 — Licença

- `LICENSE` (MIT, inglês) e `LICENSE.pt-BR.md` (tradução de cortesia), ambos reforçando que doações são voluntárias.
- Seção de licença nos dois READMEs.

### Rodada 103 — Divulgação

- `.github/FUNDING.yml` (botão Sponsor com link PayPal), badges nos READMEs, rascunhos de posts PT/EN em `docs/divulgacao/`.
- Pendente do autor: gravar GIF/vídeo curto e publicar; avaliar GitHub Sponsors/Ko-fi/Apoia.se.

### Rodada 104 — GitHub Sponsors

- Perfil aprovado; `github: CristianBernardes` no `FUNDING.yml` e botão nos dois READMEs.

### Rodada 105 — Merge na master

`master` fast-forward até `b95cfb6` (FUNDING.yml na branch padrão). Validação Mermaid pendente: exige instalar `mermaid`+`jsdom`, não autorizado.

### Rodada 121 — Poderes do dono, roteamento por área, diálogo PO–cliente e demissão aprovada (ADR-054/055/056)

- **Frontend:** botão "Demitir" (TeamBoard e mapa, com confirmação), Kanban com arrastar-e-soltar
  (o dono ignora a matriz via `owner_override`), cartões ordenados por prioridade, modal de edição
  (responsável/prioridade), resposta do cliente no chat e `DismissalModal` (pt/en) para aprovar/rejeitar
  demissões propostas pelo RH.
- **Backend:** `task_routing` (palavras-chave pt/en por cargo; RH/Analista/Consultor/Tech Lead/Dev
  assumem o que é da sua área); `PUT /tasks/{id}/owner|priority`; `FireAgentUseCase` devolve o
  trabalho ao fluxo e publica o status; `ClientDialogueUseCase`; `DismissalProposal` + migração
  `000011` + rotas `/dismissals` + ferramenta `propose_dismissal` (só RH); prompts do RH pt/en.
- **Ferramental:** `make format-frontend` falhava nos `.svelte` (prettier sem plugin): adicionados
  `prettier` e `prettier-plugin-svelte` (devDependencies) e `frontend/.prettierrc.json`
  (sem `;`, aspas simples, 120 colunas nos `.svelte`). Os `.svelte` foram reformatados uma vez.
- **Validação:** backend 412 unit + 12 integração (Postgres real) ok, ruff/mypy limpos; frontend
  `svelte-check` 0 erros, 79 testes, build ok.
- **Limitações:** a resposta do cliente vira contexto/memória do PO, mas não reescreve o backlog já
  criado; as demissões pendentes chegam ao frontend por polling (sem MQTT dedicado); a lista de
  palavras-chave é fixa; o RH só propõe quando o LLM chama a ferramenta (sem rotina periódica).

### Rodada 124 — READMEs pt/en

- Tabela do time atualizada (RH propõe demissões; Analista de Dados e Consultor com as novas áreas).
- Novas seções "Cada um pega o que é da sua área" e "Você é o dono do produto" (arrastar cartões,
  editar responsável/prioridade, conversa com o PO, demitir e aprovar/rejeitar propostas do RH).
- Tabela da API: `/dismissals` e `/tasks` com `/owner`, `/priority` e `owner_override`.
- Apenas documentação (sem testes a rodar).

### Rodada 125 — Remoção do CI/CD (ADR-040/041 revogados)

- Decisão do dono do produto: o projeto **não terá CI/CD**. Removidos `.github/workflows/ci.yml` e o selo
  de CI dos READMEs pt/en; ADR-040 e ADR-041 marcados como *Revogado* (histórico mantido). O item de
  backlog "testes de integração no CI" foi apagado.
- Mantidos: `.github/FUNDING.yml` (botão Sponsor) e o piso de cobertura de 85% do `pyproject` (rodado
  localmente por `make check`). Os documentos históricos de `docs/migration-plan/` (fases 6 e 7) ainda
  descrevem CI/CD como plano original e não foram reescritos.
- Rodadas 43, 44 e 47 acima ficam como histórico.

### Rodada 127 — Vazamento do raciocínio do LLM em inglês (ADR-057)

- **Bug relatado:** o balão de pensamento e artefatos `.md` (ex. `workspace/projects/tasks/bdebb380-...md`)
  mostravam o raciocínio interno do modelo em inglês ("We need to produce a markdown...",
  "the instruction says..."), mesmo com o escritório em português. Reproduzido com `gpt-oss:20b`
  (modelo do RH) chamando o Ollama local diretamente.
- **Causa:** modelos "reasoning" às vezes escrevem o raciocínio no campo `content` da resposta
  em vez do campo `thinking` separado da API do Ollama; a leitura tolerante (ADR-036) então
  trata esse texto misto como o próprio pensamento do agente.
- **Correção (três camadas):** diretiva de idioma reforçada (proíbe comentar como vai responder
  e texto de raciocínio antes do conteúdo); `think: false` em toda chamada ao Ollama; guard
  `strip_reasoning_preamble` (`domain/services/llm_output_guard.py`) que corta o raciocínio
  vazado antes do conteúdo entregável, aplicado em `_parse_structured_reply` (vale para todo
  pensamento, trabalho e artefato).
- **Validação:** 422 unit (backend) verdes; reprodução manual com três chamadas reais ao
  `gpt-oss:20b` no cenário relatado (recrutamento), sem vazamento em nenhuma.
- **Limitação:** o guard é heurístico; não há garantia absoluta contra vazamentos com um
  padrão textual diferente dos observados.

### Rodada 128 — Excluir tarefas do board

- **Pedido:** o dono do produto quer apagar tarefas criadas pelos agentes que são alucinação.
- **Backend:** `DELETE /tasks/{id}?actor_id=&actor_role=` (204; 404 se inexistente);
  `DeleteTaskUseCase` libera o agente responsável, remove a tarefa (histórico em cascata) e
  publica `office/tasks/deleted`; `ITaskRepository.delete` nas implementações em memória e Postgres.
- **Frontend:** botão "Excluir tarefa" no modal "Editar tarefa", com segundo clique de
  confirmação; `api.deleteTask` e `store.removeTask`; textos pt/en.
- **Validação:** 420 unit (backend), mypy/ruff limpos, 79 testes e svelte-check (frontend).
- **Limitação:** o frontend não escuta `office/tasks/deleted`; outra aba só atualiza no reload.

### Rodada 129 — Ambiente Windows do dono do produto (sem código)

- **Pedido:** o dono do produto passou a rodar o projeto no Windows (antes só Linux/WSL puro,
  sem Docker Desktop); `OLLAMA_URL_IN_CONTAINER`/`OLLAMA_BASE_URL` apontavam para
  `172.17.0.1` (bridge do Docker Engine no Linux), que não existe no Docker Desktop for Windows.
- **Ajuste (apenas `.env` reais, nunca `.env.example`):** `.env` (raiz) e `backend/.env` passam a
  usar `http://host.docker.internal:11434` (porta padrão do Ollama no Windows) em vez de
  `172.17.0.1`. `host.docker.internal` resolve tanto para o container do backend (via
  `OLLAMA_URL_IN_CONTAINER`, sobrescrito pelo `docker-compose.yml`) quanto para execução local
  fora de container no mesmo host Windows.
- **Suporte adicional (sem alterar código do projeto):** diagnóstico e correção de ambiente —
  habilitar "Add the `*.docker.internal` names to the host's hosts file" nas configurações do
  Docker Desktop; habilitar a integração WSL com a distro `Ubuntu-24.04`; reinício de
  `wsl --shutdown` + Docker Desktop após erro transitório `Wsl/Service/0x8007274c` na integração;
  localização e inicialização do executável per-user (`%LOCALAPPDATA%\Programs\DockerDesktop\`)
  quando o atalho do menu Iniciar não abria a janela.
- **Validação:** nenhum teste automatizado aplicável (mudança de configuração local/ambiente,
  não de código versionado além dos dois `.env`, que são ignorados pelo git).
- **Limitação:** o ADR-009 documenta `172.17.0.1` como valor padrão para Linux/Docker Engine
  nativo; o Windows com Docker Desktop precisa de `host.docker.internal` — isso é uma divergência
  de ambiente local, não uma mudança na documentação/padrão do projeto (`.env.example` inalterado).

### Rodada 130 — Selecionar responsável já na criação da tarefa

- **Pedido:** no formulário de nova tarefa, se já houver profissionais contratados, deve ser
  possível selecionar o responsável no momento da criação (não só depois, editando a tarefa). O
  `select` de responsável só deve aparecer se houver ao menos um agente contratado.
- **Frontend:** `TaskForm.svelte` recebe a lista de `agents` (antes só recebia `hasAgents:
  boolean`); exibe um `<select>` de responsável (com opção "Sem responsável") somente quando
  `agents.length > 0`, no mesmo padrão já usado em `TaskEditModal.svelte`; o `ownerId` escolhido
  é enviado ao callback `onsubmit`. `App.svelte` passa `agents={team}` ao `TaskForm` e, em
  `createTask`, após criar a tarefa via `POST /tasks`, chama `api.setTaskOwner` (endpoint já
  existente, reaproveitado do fluxo de edição) se um responsável foi selecionado.
- **Backend:** nenhuma mudança — o endpoint `PUT /tasks/{id}/owner` (`SetTaskOwnerUseCase`) já
  cobria a atribuição de responsável sem mudar o estágio da tarefa.
- **Validação:** `npm run test` (frontend) 81 testes verdes, incluindo 2 novos cenários
  (selecionar responsável no formulário; `select` ausente sem agentes) e 1 teste existente
  ajustado para a nova assinatura do callback `onsubmit`; `npm run check` (svelte-check + tsc)
  sem erros ou avisos.
- **Limitação:** nenhuma identificada; o fluxo reutiliza integralmente a API existente.

### Rodada 131 — Containers autossuficientes: Poetry e npm sem instalação externa

- **Pedido:** o dono do produto não queria precisar de Poetry nem de Node.js/npm instalados fora
  do Docker para subir a stack e rodar migrations — tudo deveria funcionar só com `docker`/`docker
  compose` no host.
- **Backend (`backend/Dockerfile`):** o estágio final (runtime) passou a instalar também o Poetry
  (reaproveitando o `site-packages` já populado pelo estágio builder) e a copiar
  `pyproject.toml`/`poetry.lock*`, permitindo rodar `poetry run ...` **dentro do container**, sem
  precisar de venv nem de Poetry no host.
- **`Makefile`:** os alvos `migrate`, `migrate-rollback`, `migrate-status`, `migrate-fresh` e
  `make-migration` deixaram de depender de `check-poetry`/Poetry local e passaram a executar via
  `docker compose exec backend poetry run python -m
  src.infrastructure.persistence.migrator ...`. Novo alvo auxiliar `ensure-backend-up` (idempotente,
  `docker compose up -d backend`) é pré-requisito dos cinco alvos de migration, garantindo que o
  container (e o `postgres`, via `depends_on: condition: service_healthy`) esteja de pé antes do
  comando — dispensando `make up` manual antes de migrar.
- **Frontend (`frontend/Dockerfile`, novo `frontend/entrypoint.sh`, novo `frontend/nginx.conf`):**
  o Dockerfile deixou de ser multi-stage (`node:24-alpine` builder → `nginx:1.27-alpine` runtime,
  com `npm ci`/`npm run build` só em build-time da imagem) e passou a ser uma imagem única
  `node:24-alpine` com `nginx` instalado via `apk add`. O `entrypoint.sh` roda a cada **subida do
  container**: `npm install`, `npm run build` (vite build) e publica o `dist/` em
  `/usr/share/nginx/html` antes de iniciar `nginx -g "daemon off;"`. Como o pacote `nginx` do
  Alpine vem com um `default.conf` que retorna 404 para tudo (diferente da imagem oficial
  `nginx:alpine`), foi adicionado `frontend/nginx.conf` servindo `/usr/share/nginx/html` com
  fallback de SPA (`try_files $uri $uri/ /index.html`).
- **`docker-compose.yml`:** como o build do frontend agora acontece em runtime (dentro do
  container), as variáveis `VITE_*` do serviço `frontend` migraram de `build.args` (só existem em
  build-time da imagem) para `environment:` (lidas pelo Vite via `process.env` quando o
  `entrypoint.sh` roda `npm run build`).
- **READMEs (`README.md`, `README.en.md`):** seção "Requisitos"/"Requirements" reescrita —
  Poetry/Node.js/Go deixam de ser pré-requisitos para **subir o projeto** (`make up`), permanecendo
  apenas como requisito opcional para desenvolvimento fora do Docker; o roteiro WSL2 no Windows foi
  simplificado para instalar só `git`/`curl` na distro (nenhuma ferramenta de linguagem). Seção
  "Desenvolvimento"/"Development" agora separa claramente os alvos de migration (via container, sem
  Poetry no host) dos alvos de desenvolvimento local do backend (`install`/`lint`/`format`/`test*`,
  que continuam exigindo Poetry no host por rodarem fora de container).
- **Validação:** rebuild completo das duas imagens (`docker compose build backend frontend`) e
  recriação dos containers; `make migrate-status` testado com o `backend` previamente parado,
  confirmando que `ensure-backend-up` o sobe automaticamente (aguardando o `postgres` ficar
  healthy) antes de listar as 12 migrações aplicadas; frontend verificado com `curl` (HTTP 200,
  bundle com as variáveis `VITE_*` do `.env` da raiz corretamente embutidas) e com os logs do
  `entrypoint.sh` mostrando `npm install`/`vite build` rodando a cada `docker compose up`/`restart`.
- **Limitação:** o build do frontend agora roda a cada subida do container (sem cache de camada
  Docker para `node_modules`), adicionando alguns segundos de latência à inicialização em troca de
  não depender de Node.js no host — trade-off aceito explicitamente pelo dono do produto. O
  `node_modules` instalado existe apenas dentro do container (não há bind mount do código do
  frontend no `docker-compose.yml`, decisão também mantida a pedido do dono do produto).

### Rodada 132 — README: roteiro de instalação no Windows (WSL2 + Docker Desktop)

- Nova seção "Rodando no Windows (WSL2 + Docker Desktop)" no `README.md` (commit `c08ed10`):
  instalar WSL2 com Ubuntu 24.04, habilitar a integração do Docker Desktop com essa distro (sem
  instalar Docker Engine dentro do WSL) e, dentro da distro, instalar as ferramentas de
  desenvolvimento opcionais (`build-essential`, Poetry, Node.js 20+, Go 1.22+) — nenhuma vem
  pré-instalada no Ubuntu. Reforça que o Ollama continua rodando no Windows nativo, nunca dentro
  do WSL/container.
- Apenas documentação; sem testes aplicáveis.

### Rodada 133 — Bloquear criação de tarefas por agentes

- **Pedido:** o dono do produto quer poder impedir que agentes autônomos criem novas tarefas no
  backlog (ex.: durante a divisão de tarefas do planejamento), sem depender só da regra textual
  da ata de reunião.
- **Backend (`37f5f03`):** nova tabela `office_settings` (migração `000012`) e
  `ISettingsRepository` (`backend/src/domain/interfaces/settings_repository.py`) com implementações
  em memória e Postgres; `BoardSettingsUseCases` (get/update) e rotas
  `GET`/`PUT /settings/board` (`agents_can_create_tasks`); mensagens i18n para o bloqueio.
- **Frontend:** toggle em `App.svelte` para o dono ligar/desligar a criação de tarefas pelos
  agentes, consumindo as novas rotas.
- **Validação:** `test_agent_task_creation_block.py` cobre o bloqueio; `test_dependencies_postgres.py`
  ajustado para o novo repositório.
- **Limitação (resolvida na Rodada 136):** o `WorkLoopUseCase` ainda não consultava essa
  configuração ao dividir tarefas — a tarefa de divisão podia gerar novas tarefas mesmo com o
  toggle desligado.

### Rodada 134 — Regressão no select de modelos do formulário de contratação

- **Bug:** o select de modelo de IA no formulário de contratar agente parou de ser preenchido a
  partir de `GET /models`. Corrigido em `frontend/src/App.svelte` (commits `f550275`/`102f4c6`,
  aplicados de forma equivalente em três branches/merges paralelos de `develop` — por isso o
  mesmo diff aparece sob três hashes diferentes no histórico).

### Rodada 135 — Community standards do GitHub

- `.github/CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md` e templates de issue/PR em
  português (commit `4ea12f8`), depois complementados com as versões em inglês
  (`CODE_OF_CONDUCT.en.md`, `CONTRIBUTING.en.md`, `SECURITY.en.md`,
  `ISSUE_TEMPLATE/*.en.md`) e links cruzados pt↔en no topo de cada arquivo (commit `f3759bd`).
  Apenas documentação de comunidade; sem testes aplicáveis.

### Rodada 136 — `WorkLoopUseCase` respeita o bloqueio de criação de tarefas

- Fecha a limitação da Rodada 133: `WorkLoopUseCase` (`backend/src/application/autonomy/work_loop_use_case.py`)
  agora consulta `agents_can_create_tasks` antes de dividir uma tarefa em subtarefas; se a criação
  estiver bloqueada, a divisão (que poderia gerar novas tarefas) é evitada. Ajuste também em
  `backend/src/presentation/dependencies.py` para injetar a dependência de configurações no caso
  de uso. Sem teste unitário novo dedicado a este ajuste pontual.

### Rodada 137 — `.env.example` do backend atualizado

- `backend/.env.example` atualizado (commit `dc99ffc`) para refletir variáveis adicionadas nas
  rodadas recentes (ex.: configuração de bloqueio de tarefas). Apenas documentação de
  configuração; `.env` reais não versionados não são alterados por este commit.

### Rodada 138 — Anthropic (Claude) como provedor de LLM por agente (ADR-058/059)

- **Pedido do dono do produto:** integrar IAs de ponta em nuvem (ex.: Claude) ao sistema, com a
  escolha de modelo aparecendo no frontend (formulário de contratação) e tendo efeito real no
  agente contratado, desde que a credencial (`ANTHROPIC_API_KEY`) esteja configurada no `.env`.
- **`AnthropicAdapter`** (`backend/src/infrastructure/llm/anthropic_adapter.py`): nova
  implementação de `ILlmAdapter` via API *Messages* da Anthropic (HTTP puro com `httpx`, sem SDK
  proprietário — mesmo padrão de integração leve do `OllamaAdapter`/`TavilySearchAdapter`).
  Qualquer modelo com prefixo `claude-` é roteado automaticamente para esse adaptador
  (`provider_resolution.py::is_anthropic_model`); todo o restante continua no `OllamaAdapter`.
  Chave de API opcional em `Settings`, sem valor padrão — só exigida (erro explícito) na primeira
  chamada `think()` de um papel que efetivamente use Claude, nunca na inicialização do serviço.
  A Anthropic não tem API de embeddings; `AnthropicAdapter.embed()` levanta
  `NotImplementedError` deliberadamente (ADR-058).
- **`GET /models` passa a listar também os modelos Claude** (`models_router.py`): combina os
  modelos do Ollama com `GET /v1/models` da Anthropic quando `ANTHROPIC_API_KEY` está
  configurada — sem a chave, nenhuma chamada à Anthropic é feita e nenhum modelo Claude aparece
  na lista nem no dropdown do `HireForm` (frontend). Rótulo do campo no frontend atualizado de
  "Modelo (Ollama)" para "Modelo (LLM)" em pt/en, já que a lista agora pode misturar provedores.
- **Correção de bug: modelo do agente era ignorado na resolução do LLM.** Ao investigar se a
  escolha de modelo feita na contratação realmente tinha efeito, foi identificado que
  `AgentThinkUseCase`, `ResearchTopicUseCase` e a memória semântica sempre resolviam o adaptador
  **pelo papel** (`ILlmAdapterResolver.resolve(agent.role)`), ignorando por completo o
  `agent.llm_model` individual escolhido na contratação — o campo era salvo e devolvido pela API,
  mas nunca influenciava qual LLM o agente de fato usava. `ILlmAdapterResolver.resolve()` passou
  a aceitar um segundo parâmetro opcional (`model: str = ""`); `RoleBasedLlmAdapterResolver`
  prioriza agora **modelo do agente > modelo do papel (`.env`) > modelo padrão global**.
  `AgentThinkUseCase` e `ResearchTopicUseCase` repassam `agent.llm_model`; a memória semântica
  (`memory_use_cases.py`) continua resolvendo só pelo papel, deliberadamente, já que a Anthropic
  não tem embeddings e um agente com Claude não pode perder a capacidade de memória (ADR-059).
- **Correção de teste frágil:** `test_research_router.py` sobrescrevia `get_llm_adapter_resolver`
  via `app.dependency_overrides`, mas essa função é chamada diretamente (não via `Depends(...)`
  encadeado) dentro de `get_research_use_case()` — o override nunca interceptava de fato, e o
  teste só passava por coincidência quando o Ollama local da máquina tinha o modelo certo
  instalado. Corrigido para sobrescrever `get_research_use_case` diretamente (a dependência que a
  rota de fato declara via `Depends(...)`).
- **Validação end-to-end real:** subido um backend de teste isolado (memória, porta própria),
  contratado um agente PO com `claude-haiku-4-5-20251001` e feito `think()` de verdade contra a
  API da Anthropic (resposta real em português, confirmando a integração). Prova decisiva:
  reiniciando o mesmo backend com `ANTHROPIC_API_KEY=""`, a mesma chamada falhou com
  `RuntimeError: ANTHROPIC_API_KEY não configurada...` — confirmando que a chamada é real e
  depende genuinamente da credencial, não é simulada nem hardcoded.
- Novos ADRs: `docs/adr/058-anthropic-claude-como-provedor-de-llm-em-nuvem.md` e
  `docs/adr/059-modelo-do-agente-sobrepoe-modelo-do-papel.md`.
- Testes: 442 unit no backend (antes 440 — novos cenários de `/models` com/sem chave Anthropic e
  prioridade do modelo do agente no resolver), 82 no frontend (novo cenário cobrindo modelos
  Claude listados no `HireForm`). `ruff`/`mypy` limpos nos arquivos alterados;
  `svelte-check`/`tsc` sem erros.

### Rodada 139 — Chat direto do dono com o RH (ADR-060)

- **Pedido do dono do produto:** um quadro de chat com o RH, como o do PO, para discutir o
  desempenho do time e pedir demissões (a ferramenta `propose_dismissal` existia, mas nunca era
  usada pelo LLM do RH).
- **Backend:** `HrChatUseCase` + `POST /hr/chat` (`hr_chat_router.py`): sessão própria
  (`scenario="hr"`), prompt com o elenco (nome | cargo | `agent_id`) e instrução explícita de
  chamar `propose_dismissal`; recusas da ferramenta voltam como mensagem `system` localizada;
  409 sem RH ativo, 404 para sessão inexistente/não-RH. Prompts do RH (pt/en) reforçados.
  A aprovação final continua no `DismissalModal` (ADR-056).
- **Frontend:** segundo `ChatPanel` ("Conversa com o RH") com título/placeholder próprios; sessão
  guardada no `localStorage`; mensagens do dono agora aparecem como "Você" (antes "Sistema");
  botão bloqueado enquanto o RH responde.
- **Validação:** backend 453 unit, ruff/mypy limpos; frontend `svelte-check` 0 erros, 83 testes.
- **Correção (mesma rodada):** a modal não aparecia porque o RH respondia em texto sem emitir
  `tool_call`. Pedido do dono: a ordem de demissão no chat é detectada automaticamente (sem JSON),
  mas só cria a proposta pendente; quem demite é o dono na modal (ADR-056). `dismissal_intent.detect_dismissal_targets` (determinístico, pt/en) + `HrChatUseCase`
  propõe; o LLM não é chamado nesse caso. Perguntas/condicionais não
  demitem. 455 unit.
- **Limitações:** sem streaming; detecção por palavras-chave; respostas de conversa não
  validadas contra um LLM real.

### Rodada 140 — Gateway de LLM em nuvem compatível com OpenAI

- **Pedido do dono do produto:** trazer para o backend modelos de nuvem expostos por um proxy
  (`https://ollama.scriptsavvy.com.br`) que fala apenas o formato OpenAI (`/v1/models` e
  `/v1/chat/completions`); `/api/chat` e `/api/tags` do Ollama não existem nele.
- **Backend:** `OpenAICompatibleAdapter` (`openai_compatible_adapter.py`) chama
  `/v1/chat/completions` e reaproveita o parser tolerante do `AnthropicAdapter`; embeddings
  continuam em outro provedor. `provider_resolution.is_cloud_gateway_model` roteia modelos
  `us.anthropic.*` para ele (o resto segue no Ollama; `claude-*` segue na Anthropic).
  `GET /models` também lista `/v1/models` do gateway (vazio se não configurado ou fora do ar).
- **Configuração:** `CLOUD_LLM_BASE_URL`, `CLOUD_LLM_API_KEY` (opcional) e
  `CLOUD_LLM_REQUEST_TIMEOUT_SECONDS` (padrão 300). Vazias no `.env.example`; a URL real fica
  só no `.env` local (ignorado pelo git).
- **Validação:** 453 unit passando; `GET /v1/models` real retornou 20 modelos.
- **Limitações:** chamada de chat de ponta a ponta não validada; sem testes dedicados do
  adaptador/roteamento; a lista traz todos os modelos do gateway, sem filtro.

### Rodada 141 — 18 novos cargos disponíveis para contratação

- **Pedido do dono do produto:** ampliar os profissionais do sistema com `dev_mid`,
  `database_administrator`, `devops_engineer`, `site_reliability_engineer`, `ux_ui_designer`,
  `business_analyst`, `software_architect`, `security_engineer`, `test_automation_engineer`,
  `data_engineer`, `ai_engineer`, `ml_engineer`, `systems_analyst`, `product_designer`,
  `technical_support`, `infrastructure_analyst`, `data_quality_analyst` e `engineering_manager`.
- **Backend:** novos valores em `Role`; prompts `pt/` e `en/` por cargo; mapa de arquivos em
  `file_prompt_provider.py`; permissões de ferramentas (`tool_permissions.py`: técnicos como o
  Dev Sênior, Engenheiro de Testes como QA, Gerente de Engenharia pode contratar mas não propor
  desligamento — só o RH); nomes na ata da reunião; `EXECUTOR_ROLES` + palavras-chave pt/en
  para o roteamento de tarefas (`task_routing.py`), `dev_mid` entra nos cargos-reserva;
  `test_automation_engineer` passa a testar/revisar como o QA (`task_workflow.py` e
  `work_loop_use_case.py`). Migração `2026_11_05_000013_expand_agent_roles` amplia o domínio
  `agent_role` (a `down` remove agentes dos novos cargos).
- **Frontend:** `Role`/`ROLES` e rótulos pt/en; os novos cargos reaproveitam sprites e assento
  de um cargo base (`BASE_ROLE` em `types.ts`), pois ainda não há arte própria.
- **Validação:** `ruff format`; 474 unit/integração passando (falha só o teste MQTT que exige
  broker; o `ruff check` aponta um I001 antigo em `openai_compatible_adapter.py`);
  vitest 83 passando.
- **Limitações:** sem sprites/assentos próprios; sem variável `AGENT_*_MODEL` por novo cargo
  (usam o modelo informado na contratação); palavras-chave de roteamento são heurísticas;
  a migração precisa ser aplicada no banco existente.

### Rodada 142 — RH contrata via tarefa, com aprovação do dono (modal)

- **Pedido do dono do produto:** o RH deve contratar de fato, via tarefa; antes de contratar,
  um modal mostra o profissional (cargo + motivo) e o dono escolhe o nome e a IA.
- **Backend:** entidade `HiringProposal` (`hiring_proposals`, migração `2026_11_05_000014`),
  `IHiringRepository` (memória/Postgres), `ProposeHiringUseCase`/`DecideHiringUseCase`
  (`application/hiring`) e rotas `GET /hirings?pending_only=`, `POST /hirings/{id}/approve`
  (`name`, `llm_model`) e `POST /hirings/{id}/reject`. A ferramenta `hire_agent` agora só
  **propõe** (args `role`, `reason`, `task_id`), nunca contrata sozinha; erros localizados pt/en.
  O ciclo de trabalho (`work_loop_use_case.py`): quando o RH executa uma tarefa de contratação
  (`is_hiring_task`: contrat/recrut/vaga/hire/recruit), pergunta ao LLM qual cargo e registra a
  proposta (uma pendente por tarefa); resposta sem cargo válido é ignorada com aviso no log.
- **Frontend:** `HiringModal.svelte` (cargo, motivo, nome pré-preenchido com o cargo, seletor de
  IA com os modelos do `/models`), `api.listPendingHirings/approveHiring/rejectHiring`,
  `store.hirings`; o modal aparece uma proposta por vez, depois das demissões pendentes. Os
  novos cargos da Rodada 141 já aparecem no formulário de contratação manual.
- **Validação:** `ruff format`; 479 unit passando; mypy limpo; vitest 85 passando.
- **Limitações:** a escolha do cargo pelo RH depende da resposta do LLM (formato
  `cargo | motivo`); sem rota HTTP para propor contratação (só ferramenta/ciclo); a migração
  precisa ser aplicada; o gateway/MQTT dos tópicos `office/hirings/*` não foi validado ponta a ponta.

### Rodada 143 — time só com RH consegue andar

- **Problema:** com apenas o RH contratado, a tarefa de contratação ficava parada no backlog:
  só PO/SM planejam e só SM/TL/PO coordenam. **Correção:** `HR_MANAGER` e
  `ENGINEERING_MANAGER` entram como reserva em `_PLANNERS`/`_COORDINATORS` (política
  `task_workflow.py` e ciclo `work_loop_use_case.py`); PO/SM continuam com prioridade.
- **Console do navegador:** o 404 de `/sessions/.../messages` é a sessão do chat com o RH
  guardada no navegador após reset do banco (o front já recomeça a conversa); o 422 de
  `POST /goals` ocorre quando o texto do objetivo passa de 4000 caracteres.

- **Limite de texto:** objetivo (`POST /goals`) e mensagens de chat passam de 4000/8000 para 20000 caracteres (`chat_schemas.py`); a coluna já é `TEXT`.

- **Limite das tarefas:** título 200→500, descrição e resultado 8000→50000 caracteres (`task_schemas.py`).

### Rodada 144 — bug do modal de contratação e READMEs

- **Bug:** ao clicar em "Contratar" com um nome já existente (coluna `agents.name` é única), o
  backend dava 500 e o modal não fechava, sem explicação. **Correção:** `DecideHiringUseCase`
  valida o nome (sem diferenciar maiúsculas) e devolve 409 localizado pt/en
  (`hiring.name_taken`); o `HiringModal` mostra o aviso `hiringNameTaken` e mantém os dados.
- **Documentação:** `README.md` e `README.en.md` listam os 27 cargos (com identificadores),
  descrevem o fluxo de contratação com aprovação do dono e trazem `images/proposta_de_contratacao.png`.
- **Validação:** 483 unit (backend), mypy limpo, vitest 87.

### Rodada 145 — troca de licença: MIT → AGPL-3.0 + licença comercial

- **Decisão do dono do produto:** licenciamento duplo. `LICENSE` agora é o texto oficial da
  AGPL-3.0 (com cabeçalho de contato para licença comercial); `LICENSE.pt-BR.md` é um resumo de
  cortesia; selos e seção de licença dos dois READMEs e `pyproject.toml` atualizados.
- **Observações:** só vale para versões novas (cópias já baixadas continuam sob MIT); contribuições
  de terceiros exigem aceite do licenciamento duplo; o texto comercial deve passar por revisão jurídica.

## Estado atual e ponto de retomada (após a Rodada 145)

### Commits por rodada (branch `develop`, tudo no remoto)

| Rodada | Commit | Tema |
|---|---|---|
| 4–13 | ver `git log` | LLM por papel, i18n, think, Postgres, migrações, tarefas, transições, chat, memória |
| 14 | `25fa799` | MQTT real + contrato de tópicos (ADR-021) |
| 15–16 | `2681383`, `4869413` | Autonomia: reunião e backlog do PO (ADR-022/023) |
| 17 | `8b3b97f` | Gateway Go: MQTT→Kafka, dedupe Redis, DLQ (ADR-024) |
| 18–19 | `7515fe1`, `6bfe83b` | goal_id/revisor (ADR-025), hire_agent (ADR-026) |
| 20–22 | `43cf3e9`, `652a84c` | Relacionamentos (ADR-027), reuniões/start_ceremony (ADR-028) |
| 23 | `11ef1c1` | Reuniões persistidas + rotas sociais (ADR-029) |
| 24–25 | `11506be`, `dc26758` | Layout do escritório (ADR-030), feed de atividades (ADR-031) |
| 26 | `e327104` | Debate multi-rodada (ADR-032) |
| 27 | `5ccd9be`, `03f655e` | Integração real: Postgres, pgvector, MQTT (10 testes) |
| 28 | ver `git log` | Gateway Go validado ponta a ponta |
| 29 | `6dd057f` | Rotas de escrita de reuniões (ADR-033) |
| 30 | `7a65d4d` | Pesquisa de agentes → artefato .md (ADR-034) |
| 31 | `c58abf1` | RFC-004 + design doc de autonomia |
| 32 | `49ecd0e` | Permissões assign/complete (ADR-035) |
| 33 | `07ce6e3` | Ollama tolerante (ADR-036) |
| 34 | `10d2688` | README: seção API HTTP |
| 35 | `9c07a79` | Ferramenta research (ADR-037) |
| 36 | `60776a8` | POST /relationships/interactions (ADR-038) |
| 37 | `b20afc7` | Integração gateway Kafka (2 testes) |
| 38 | `06bdecf` | Fix closed_at de goal já concluída |
| 39 | `c2f8042` | Embedding mock 768 dims |
| 40 | `49e54c8` | Curingas no bus em memória; feed por agente (291 unit + 13 integração; ADRs 001–039) |
| 41 | `7f691e5` | Cobertura do ToolRegistry (293 unit) |
| 42 | `af24d88` | Factories Postgres + cache da pool (304 unit) |
| 43 | `16cc8d9` | CI GitHub Actions (ADR-040; ADRs 001–040) |
| 44 | `b8c1cd4` | Badge de CI nos READMEs |
| 45 | `7f964ec` | Testes de prompt sem mapeamento e Tavily close (306 unit) |
| 46 | `c1c8a5e` | Limitações e backlog revisados |
| 47 | `85246fb` | Cobertura mínima 85% + jobs integration/docker no CI (ADR-041) |
| 48 | `583fd26` | Início rápido dos READMEs atualizado |
| 49 | `4927af8` | E2E PO → Dev → QA (309 testes) |
| 50 | `a1485c7` | Gateway configurável via .env (ADR-042) |
| 51 | `3d9339c` | Gateway .env com hosts/portas de container; Tavily URL/timeout em settings |
| 52 | `53609f1` | ADR-043: compose sem valores fixos (.env raiz, HOST_PORT_*, credenciais Postgres) |
| 53 | `1737958` | ADR-044: Settings sem defaults de infraestrutura |
| 54 | `c85e6ba` | MQTT do backend movido do compose para backend/.env.example (valores de container) |
| 55 | `dd3d2cc` | README: Quick Start copia os três .env.example |
| 56 | `4f637a6` | ADR-045: idempotência de activity_events por event_id; conftest movido para tests/unit |
| 57 | `bce6183` | ADR-046: consumidor Kafka→MQTT fora do escopo (YAGNI, risco de laço) |
| 58 | `bfd7674` | ADR-047: frontend Svelte 5 (mapa, kanban, time, chat, logs, doação pt/en) |
| 59 | `5b9d28f` | Dockerfile/compose/CI do frontend e README |
| 60 | `72b57c2` | Frontend: formulário de contratação, `VITE_DEFAULT_LLM_MODEL`, verificação visual |
| 61 | `00c3848` | Botão "Contratar time padrão" (criar tarefa exige agentes) |
| 62 | `3481ea7` | `GET /models` (Ollama) e seleção do modelo de IA ao contratar |
| 63 | `55fd2b7` | Idioma por objetivo (Accept-Language → reunião/prompts) e `/models` sem embeddings |
| 64 | `af89e77` | ciclo de trabalho autônomo (ADR-048) + escritório vivo no mapa: caminhadas, conversas, sprites distintos, cargo no rótulo |
| 65 | `a536e8f` | Responsável obrigatório fora do backlog + diretiva de idioma nos prompts |
| 66 | `7a7c044` | Poses alternativas dos sprites (interagindo_com_objetos, outra_postura_de_trabalho) |
| 67 | `71a8e84` | Cargos traduzidos nas atas |
| 68 | `01b6b55` | Correção do sprite bugado (interagindo_com_objetos) |
| 69 | `9b50022` | Reset do banco/workspace, time completo contratado e backlog inicial |
| 70 | `7c989bb` | Kanban: WIP/limites, métricas de fluxo, cargo no cartão, timestamps de task; PayPal visível também em pt |
| 71 | `e165023` | Sprint planning conduzido por PO/SM, divisão de tarefas, ADR-049 |
| 72 | `e7a1d43` | Refatoração SRP/DRY (task_splitter, _speak), RFC-005 e design doc do ciclo |
| 73 | `3a8882d` | Remove texto de debug `wanderIntervalMs` solto no App.svelte |
| 74 | `f66141a` | Timeout do Ollama via .env (`OLLAMA_REQUEST_TIMEOUT_SECONDS`) |
| 75 | `fe3fce8` | Modal de doação com a história do projeto (pt/en) |
| 76 | `84671cb` | Planejamento gera subtarefas distintas (título + entregável) via LLM; título do `.md` de planejamento no idioma do escritório |
| 77 | `5fb7e7b` | Corrige sessão do chão do escritório inexistente (ciclo falhava em toda fala); recriação do time/tarefas |
| 78 | `fe9850a` | Makefile: format-go, format-frontend e format-all |
| 79 | `4250ad1` | Etapa de teste (QA) antes da revisão — ADR-050 |
| 80 | `3615f39` | Kanban: grade com 6 colunas (Concluído visível) |
| 81 | `fa5efa5` | Sprint com no máximo 15 dias fictícios (`SPRINT_MAX_DAYS`) |
| 82 | `1f0b956` | Kanban: 6 colunas compactas em uma única linha |
| 83 | `8d87e88` | Workspace fixo (nunca criado em runtime, 777) + `.gitkeep` |
| 84 | `8d87e88` | Personagens vivos (pausas de descanso/reflexão) + modal de gráficos Kaizen |
| 85 | `1781cfb` | Pendências finais registradas no SCRATCHPAD |
| 86 | `8bec86a` | ADR-051: idioma do escritório em tempo de execução + trava avisando que trocar pode corromper arquivos |
| 87 | `2768a1c` | ADR-052: observabilidade completa (Kafka UI, Prometheus, Grafana, exporters, cAdvisor, `/metrics` no backend e no gateway) |
| 88 | `10bb61d` | Todos os volumes do compose movidos para `.docker/` (777 via `docker-dirs-init`) |
| 89 | `e83db75` | Artefatos `.md` de pesquisa gerados pelos agentes em `backend/workspace` commitados |
| 90 | `5237cc0` | `scripts/seed_team.py`, migração `testing` validada em Postgres real, design doc do ciclo atualizado |
| 91 | `3e75623` | READMEs pt/en detalhados com capturas, Ollama, hardware; seletor de modelos já vem do Ollama |
| 92 | `f45e3ea` | Auditoria do `git log` x SCRATCHPAD: apêndice com o histórico completo de commits |
| 93 | `96488a8` | Texto de doação transparente (dívida com saúde da filha, sem apelo emocional) no modal e nos READMEs |
| 94 | `b04ff45` | Modal de confirmação profissional (`ConfirmModal`) no lugar do `window.confirm` na troca de idioma |
| 95 | `d31ab04` | Correção de sprites: animação limitada a uma direção da folha (antes girava) e direção de caminhada pelo trajeto |
| 96 | `cd39667` | READMEs pt/en: captura `alert.png` e seção de fluxo dos containers com diagramas Mermaid (todos os serviços do compose) |
| 97 | `76f091c` | Sprite: folha `interagindo_com_objetos` só tem 24 quadros de personagem (o resto é o carrinho de props); pasta `sql/` com as 15 tarefas em pt/en |
| 98 | `bf8793b` | Postgres + MQTT por padrão (ADR-053), testes isolados do `.env`, títulos de tarefa higienizados (`clean_title`), SCRATCHPAD reescrito |
| 99 | `42dc1d9` | `grafana.png` nos READMEs pt/en |
| 100 | `927edb3` | Seção de doação centralizada (`div align=center`) nos READMEs |
| 101 | `3998ea9` | `clean_body`, testes de integração em banco `<db>_test`, verificação MQTT→Kafka |
| 102 | `2c16021` | LICENSE (MIT) em inglês e português, com nota de doações voluntárias; links nos READMEs |
| 103 | `19b9668` | `FUNDING.yml`, badges de licença/doação e rascunhos de divulgação (`docs/divulgacao/`) |
| 104 | `b95cfb6` | GitHub Sponsors (`CristianBernardes`) no `FUNDING.yml` e nos READMEs |
| 105 | `9f326cb`/`9ecb95d` | `develop` mesclada na `master` (botão Sponsor ativo); Mermaid dos READMEs segue sem validação por renderização (instalação não autorizada) |
| 106 | `2b46abe` | PayPal (link de doação já usado nos READMEs) incluído no `FUNDING.yml` |
| 107 | `197e260` | Vídeo de demonstração do YouTube no topo dos READMEs |
| 108 | `3c4c315` | Tentativa de embed (iframe) do vídeo nos READMEs, com a miniatura clicável como alternativa |
| 109 | `bed16c5` | Iframe removido dos READMEs (GitHub não renderiza); aguardando URL `user-attachments` do vídeo para player inline |
| 110 | `f909388` | Link simples do YouTube abaixo da miniatura nos READMEs |
| 111 | `8f341c9` | Vídeo de demonstração (`videos/video_demo.mp4`, convertido de HEVC para H.264) em tag `<video>` nos READMEs |
| 112 | `9db4282` | Tag `<video>` e `videos/video_demo.mp4` removidos (não tocava no GitHub); ficam miniatura e link do YouTube |
| 113 | `b5499ef` | Link simples do YouTube removido dos READMEs (fica só a miniatura clicável) |
| 114 | `424eccd` | Imagem Agent_Office_2.png como chamada clicável para o vídeo nos READMEs |
| 115 | `da154f5` | Todas as imagens (badges, vídeo e capturas de tela) centralizadas nos READMEs |
| 116 | `b25ddaf` | READMEs: removidas afirmações obsoletas (frontend "não implementado", Phaser, fases pendentes) |
| 117 | `ed874cb` | Verificação final: backend 363 unit, frontend 64 testes verdes; estado atual atualizado. Pendências só do autor: Stripe/Sponsors, conta Apoia-se (trocar [LINK-APOIA-SE] no artigo), publicar divulgação, validar Mermaid |
| 118 | `7ca1918` | Makefile: alvos lint-go, test-go, build-go, lint-frontend, test-frontend, build-frontend, install-frontend e check-all | `make lint-go`, `make lint-frontend` e `make test-go` | `Makefile`, `docs/SCRATCHPAD.md` |
| 119 | `0b6e9e9` | Containers recriados, banco refeito (`migrator fresh`) e seed de 11 agentes + 15 tarefas para testar a TAVILY_API_KEY | health 200, 11 agentes, 15 tarefas | `docs/SCRATCHPAD.md` |
| 120 | `b68add4` | Formatação prettier do frontend (`make format-frontend`) commitada | alterações apenas de formato | `frontend/src/**`, `docs/SCRATCHPAD.md` |
| 121 | `947f741` | Demitir, arrastar/editar tarefas, roteamento por área, diálogo PO–cliente, demissão aprovada pelo dono (ADR-054/055/056); prettier com plugin Svelte | backend 412 unit + 12 integração; frontend 79 testes | `backend/src/**`, `frontend/src/**`, `docs/adr/05[4-6]*`, `docs/SCRATCHPAD.md` |
| 122 | `303bc22` | Artefatos `.md` de pesquisa regenerados pelos agentes (`clean-architecture`, `kafka`, `tema`) commitados | apenas conteúdo gerado | `backend/workspace/projects/workspace/research/*.md`, `docs/SCRATCHPAD.md` |
| 123 | `cd5cf42`/`7d9d258` | `develop` mesclada na `master` (rodadas 121–122: poderes do dono, roteamento por área, diálogo PO–cliente, demissão aprovada) | merge sem conflitos | `docs/SCRATCHPAD.md` |
| 124 | `742a62d` | READMEs pt/en: responsabilidades por cargo, poderes do dono do produto, demissão aprovada e rotas novas | documentação apenas | `README.md`, `README.en.md`, `docs/SCRATCHPAD.md` |
| 125 | `e3945c8` | Remove o CI/CD: workflow e selo de CI apagados; ADR-040/041 revogados | documentação e configuração | `.github/workflows/ci.yml`, `README*.md`, `docs/adr/*`, `docs/SCRATCHPAD.md` |
| 126 | `d068a8a`/`e749501` | `develop` mesclada na `master`: o workflow de CI sai também da branch padrão | merge sem conflitos | `docs/SCRATCHPAD.md` |
| 127 | `8b2e029` | Bloqueia vazamento do raciocínio do LLM em inglês no balão de pensamento e nos artefatos (ADR-057) | 422 unit (backend); validação manual com gpt-oss real | `backend/src/domain/services/llm_output_guard.py`, `backend/src/infrastructure/llm/ollama_adapter.py`, `backend/src/infrastructure/prompts/file_prompt_provider.py`, `docs/adr/057*`, `docs/SCRATCHPAD.md` |
| 128 | `1838b94`/`f912538` | Exclusão de tarefas do board pelo dono do produto | 420 unit (backend); 79 (frontend) | `backend/src/application/tasks/task_use_cases.py`, `backend/src/presentation/api/tasks_router.py`, `frontend/src/components/TaskEditModal.svelte`, `README*.md`, `docs/SCRATCHPAD.md` |
| 129 | (sem código versionado) | `.env`/`backend/.env` ajustados para `host.docker.internal:11434` (Windows + Docker Desktop, sem Docker Desktop antes); `.env.example` inalterado | sem testes aplicáveis (config local) | `.env`, `backend/.env` (ambos ignorados pelo git) |
| 130 | `e806442` | Seleção de responsável já na criação da tarefa (select só aparece com agentes contratados) | 81 testes (frontend), svelte-check limpo | `frontend/src/components/TaskForm.svelte`, `frontend/src/App.svelte`, `frontend/src/components/components.test.ts`, `docs/SCRATCHPAD.md` |
| 131 | `6372256` | Backend roda Poetry dentro do container (migrations via `docker compose exec`, sem Poetry no host); frontend instala npm e builda via `entrypoint.sh` a cada subida (sem Node.js no host); READMEs ajustados | `make migrate-status` com backend parado (sobe via `ensure-backend-up`), `curl` no frontend com `VITE_*` embutidas no bundle | `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/entrypoint.sh`, `frontend/nginx.conf`, `docker-compose.yml`, `Makefile`, `README.md`, `README.en.md`, `docs/SCRATCHPAD.md` |
| 132 | `c08ed10` | README: roteiro de instalação no Windows via WSL2 + Docker Desktop (distro Ubuntu 24.04, ferramentas de dev dentro da distro) | documentação apenas | `README.md` |
| 133 | `37f5f03` | Configuração `agents_can_create_tasks` do quadro: nova tabela `office_settings`, rotas `GET/PUT /settings/board`, UI para o dono ligar/desligar a criação de tarefas pelos agentes | teste de bloqueio de criação por agente | `backend/src/application/settings/**`, `backend/src/domain/interfaces/settings_repository.py`, `backend/src/infrastructure/persistence/*settings_repository.py`, `backend/src/presentation/api/settings_router.py`, `frontend/src/App.svelte` |
| 134 | `f550275`/`102f4c6` | Corrige regressão: select de modelos do formulário de contratação parou de ser populado por `GET /models` (três commits equivalentes em merges paralelos de `develop`) | correção visual (frontend) | `frontend/src/App.svelte` |
| 135 | `4ea12f8`/`f3759bd` | Community standards: `CODE_OF_CONDUCT`, `CONTRIBUTING`, `SECURITY`, templates de issue/PR (pt/en com links cruzados) | documentação apenas | `.github/CODE_OF_CONDUCT*.md`, `.github/CONTRIBUTING*.md`, `.github/SECURITY*.md`, `.github/ISSUE_TEMPLATE/*`, `.github/PULL_REQUEST_TEMPLATE.md` |
| 136 | `c4e9b27` | `WorkLoopUseCase` passa a respeitar a configuração `agents_can_create_tasks` do quadro: a divisão de tarefas (que poderia criar novas) é evitada quando a criação está bloqueada | ajuste de comportamento, sem teste novo dedicado | `backend/src/application/autonomy/work_loop_use_case.py`, `backend/src/presentation/dependencies.py` |
| 137 | `dc99ffc` | Atualização de `backend/.env.example` com variáveis adicionadas nas rodadas recentes | documentação de configuração | `backend/.env.example` |
| 138 | `84c5bf9` | Anthropic (Claude) como provedor de LLM por agente (ADR-058); correção do modelo do agente ignorado na resolução do LLM (ADR-059); `GET /models` lista Claude no `HireForm` | 442 unit (backend); 82 (frontend); validação end-to-end real contra a API da Anthropic | `backend/src/infrastructure/llm/anthropic_*.py`, `backend/src/infrastructure/llm/provider_resolution.py`, `backend/src/infrastructure/llm/role_based_llm_adapter_resolver.py`, `backend/src/domain/interfaces/llm_adapter_resolver.py`, `backend/src/application/agents/agent_think_use_case.py`, `backend/src/application/research/research_use_case.py`, `backend/src/presentation/api/models_router.py`, `backend/src/presentation/dependencies.py`, `frontend/src/lib/messages.ts`, `docs/adr/058*`, `docs/adr/059*` |
| 139 | `62426d4` | Chat direto do dono com o RH (ADR-060): `POST /hr/chat`, segundo `ChatPanel`, prompts do RH reforçados | 453 unit (backend); 83 (frontend) | `backend/src/application/chat/hr_chat_use_case.py`, `backend/src/presentation/api/hr_chat_router.py`, `frontend/src/App.svelte`, `frontend/src/components/ChatPanel.svelte`, `docs/adr/060*` |
| 140 | (este commit) | Gateway de LLM em nuvem compatível com OpenAI: `OpenAICompatibleAdapter`, roteamento de `us.anthropic.*`, `GET /models` lista o gateway, variáveis `CLOUD_LLM_*` | 453 unit (backend); listagem real validada | `backend/src/infrastructure/llm/openai_compatible_adapter.py`, `backend/src/infrastructure/llm/provider_resolution.py`, `backend/src/infrastructure/config/settings.py`, `backend/src/presentation/api/models_router.py`, `backend/src/presentation/dependencies.py`, `backend/.env.example` |

### O que funciona

442 testes unitários (backend) + 13 de integração (`docker compose up -d postgres mosquitto`,
`pytest -m integration`); ruff e mypy limpos. Frontend: 82 testes (vitest) e svelte-check sem
erros. API: agents, tasks, goals, messages, memories, relationships, meetings, layout, activity,
research, models (lista Ollama + Claude); agentes têm a ferramenta research. i18n pt/en em erros,
prompts e mensagens. Persistência `memory|postgres`, bus `memory|mqtt`. Autonomia opt-in
(`AUTONOMY_ENABLED`, `MEETING_ROUNDS`). LLM por agente: Ollama como padrão (ADR-005/009) e
Anthropic/Claude como provedor opcional em nuvem, selecionável por agente individual no formulário
de contratação quando `ANTHROPIC_API_KEY` está configurada (ADR-058/059) — o modelo escolhido na
contratação tem prioridade sobre o padrão do papel. ADRs 001–059, RFCs 001–004. Backend e frontend
sobem via `docker compose up` sem exigir Poetry/Node.js instalados no host (Rodada 131) —
migrations rodam dentro do container `backend` via `poetry run`; o frontend instala npm e builda via
`entrypoint.sh` em toda subida do container.

### Limitações conhecidas

- Mermaid dos READMEs não foi validado por renderização (mermaid-cli indisponível no ambiente).
- Qualidade das respostas depende do modelo Ollama local; saídas ruins são higienizadas só nos títulos.
- Sprites verificados por testes unitários e inspeção no navegador; novos sheets exigem conferir quadros.
- Ollama é externo (não vai no compose).
- ADR-009 documenta `172.17.0.1` como padrão do projeto para Linux/Docker Engine nativo; no
  ambiente Windows do dono do produto (Docker Desktop), os `.env` reais usam
  `host.docker.internal` (Rodada 129) — divergência de ambiente local, não do padrão documentado.
- Frontend builda a cada subida do container (`npm install` + `vite build` no `entrypoint.sh`,
  Rodada 131), sem cache de camada Docker para `node_modules` — adiciona alguns segundos de
  latência à inicialização, trade-off aceito explicitamente pelo dono do produto em troca de não
  precisar de Node.js no host; `node_modules` existe só dentro do container (sem bind mount do
  código do frontend no compose, também decidido pelo dono do produto).
- Memória semântica (`remember`/`recall`) de um agente com modelo Claude continua usando o
  embedding do Ollama do papel (`AGENT_<PAPEL>_MODEL`/`OLLAMA_MODEL`), nunca Claude — decisão
  deliberada (ADR-059), já que a Anthropic não oferece API de embeddings.

### Backlog

1. Validar o Mermaid por renderização quando houver ambiente com Chromium.
2. Mais guardas de saída de LLM (descrições, atas) além dos títulos.

### Regras a lembrar

ADR antes do código; `make format` a cada mudança; SCRATCHPAD em **todo** commit; sem trailer do
Copilot; commit e push sempre; responder em português; não parar para perguntar.

## Apêndice — histórico completo do git (auditado na Rodada 92; atualizado na Rodada 138)

Auditoria: todos os commits do `git log --all` listados abaixo, em ordem cronológica (alguns não
tinham hash na tabela de rodadas). A partir da Rodada 92 passam a aparecer também commits de
infraestrutura do agente (`Agent host session ... baseline checkpoint/turn N/turn N start`) e
merges (`Merge pull request`, `Merge branch`, `Merge develop into master`) — mantidos aqui por
completude do `git log`, mesmo sem narrativa de rodada própria, já que não alteram código de
produto por si só.

| Hash | Data | Mensagem |
|---|---|---|
| `a292898` | 2026-10-30 | Commit inicial de planejamento |
| `723353e` | 2026-10-30 | Adiconado arquivos iniciais do Projeto |
| `7ed7c37` | 2026-10-30 | Adicionado arquivo .gitignore e mais arquivos a pasta docs |
| `2ab7d5b` | 2026-10-30 | Adicionado postgres ao arquivo docker-compose.yml |
| `758995e` | 2026-10-30 | Aletrado senha e banco de dados do postgres no  docker-compose.yml |
| `cf05919` | 2026-10-30 | Criado pasta ops para arquivos de inicialização do banco de dados |
| `0fa38f8` | 2026-10-30 | Alteração da pasta de configuração do mqtt |
| `0c1d599` | 2026-10-30 | Removido comentário do container do  mqtt |
| `2713878` | 2026-10-30 | Adicionado ADRs, RFCs e Design Docs da Fase 0 (fundação arquitetural) |
| `855da9d` | 2026-10-30 | Implementado esqueleto Clean Architecture do backend Python (Fase 1) |
| `cd46b27` | 2026-10-30 | Adicionado Postgres (pgvector) e backend ao docker-compose.yml, portas 70xx |
| `35993cd` | 2026-10-30 | Preenchido Makefile e README do microserviço, atualizado .gitignore |
| `ecdaa9d` | 2026-10-30 | Atualizado SCRATCHPAD.md com histórico da rodada Fase 0 + Fase 1 |
| `d86ba17` | 2026-10-30 | Adicionado verificacao de pre-requisito do Poetry no Makefile |
| `b99b2b5` | 2026-10-30 | Padronizado OLLAMA_BASE_URL para 172.17.0.1 como valor padrao do projeto |
| `842c132` | 2026-10-30 | Registrado no SCRATCHPAD.md o ponto de retomada para a proxima sessao |
| `39077be` | 2026-10-30 | Adicionado ADR-011 sobre Tavily como provedor de busca web |
| `288966c` | 2026-10-30 | Atualizado RFC-001, RFC-002 e RFC-003 com o escopo implementado na rodada 3 |
| `c2f9670` | 2026-10-30 | Implementado AgentThinkUseCase e envelope padrao de mensagens (Fase 2) |
| `5f8515a` | 2026-10-30 | Implementadas as 9 personas com prompts, permissoes e ToolRegistry (Fase 3) |
| `cc7f427` | 2026-10-30 | Implementados IWebSearchAdapter, TavilySearchAdapter e MockSearchAdapter |
| `4e70396` | 2026-10-30 | Implementado sistema completo de artefatos: write, review e approve (Fase 4) |
| `e3cd330` | 2026-10-30 | Conectada injecao de dependencia das Fases 2, 3 e 4 no dependencies.py |
| `f6f7f10` | 2026-10-30 | Atualizada arquitetura geral: frontend Svelte e gateway Go sem autenticacao |
| `e8ba9f2` | 2026-10-30 | Atualizado SCRATCHPAD.md com historico da rodada 3 |
| `c9230cc` | 2026-10-30 | Reescrito README.md para descrever o produto e a arquitetura, nao o progresso |
| `91db91c` | 2026-10-30 | Adicionada secao de doacoes (Pix/PayPal) e README.en.md em ingles |
| `5021e31` | 2026-10-30 | Tornado o botao PayPal clicavel usando tag HTML dentro da tabela |
| `d23b8d7` | 2026-10-30 | Corrigido diagrama: Go e a ponte MQTT-Python, nao um servico paralelo |
| `1c3b64c` | 2026-10-31 | Fase 5: modelo de LLM por papel via .env (ILlmAdapterResolver) |
| `99c66f3` | 2026-10-31 | Rodada 5: i18n pt/en (ADR-012) — erros localizados, prompts por idioma, Accept-Language |
| `8267f46` | 2026-10-31 | Rodada 6: endpoint POST /agents/{id}/think para despachar objetivos (ADR-013) |
| `78f92d3` | 2026-10-31 | Rodada 7: repositórios PostgreSQL e seleção de persistência por env (ADR-014) |
| `84d1c94` | 2026-10-31 | Documenta PERSISTENCE_BACKEND no .env.example |
| `89e4f15` | 2026-10-31 | feat(api): GET /agents e CORS configurável (ADR-015) |
| `a03127a` | 2026-10-31 | docs(adr): ADR-017 modelo de dados orientado a objetivos e fluxo de trabalho |
| `929253b` | 2026-10-31 | chore(frontend): esqueleto do frontend com sprites e imagens do escritório |
| `ecb1a25` | 2026-10-31 | feat(db): migrações estilo Laravel e schema completo do escritório (ADR-018) |
| `871db6c` | 2026-10-31 | feat(tasks): casos de uso, rotas e tools de tarefas com i18n (ADR-016) |
| `d35c14e` | 2026-10-31 | feat(tasks): histórico de transições e matriz papel x estágio com rotas move/transitions |
| `fe1a4c5` | 2026-10-31 | feat(chat): objetivos, sessões e mensagens com rotas, tool send_message e testes (ADR-019) |
| `6066d20` | 2026-10-31 | feat(memory): memória semântica dos agentes com pgvector (ADR-020) |
| `25fa799` | 2026-10-31 | feat(messaging): MQTT real no lifespan, curingas e contrato de tópicos (ADR-021) |
| `a8358d6` | 2026-10-31 | docs(scratchpad): estado atual, commits por rodada, limitações e backlog |
| `2681383` | 2026-10-31 | feat(autonomy): reunião do time sobre objetivos (ADR-022) |
| `4869413` | 2026-10-31 | feat(autonomy): PO cria backlog a partir da reunião (ADR-023) |
| `8b3b97f` | 2026-10-31 | feat(gateway): relay MQTT->Kafka em Go com dedupe Redis e DLQ (ADR-024) |
| `9a5ee08` | 2026-10-31 | fix(gateway): alinha imagem Go do Dockerfile com go.mod (1.26) |
| `7515fe1` | 2026-10-31 | feat(tasks): goal_id e reviewer_id nas tarefas (ADR-025) |
| `6bfe83b` | 2026-10-31 | feat(tools): handler hire_agent (ADR-026) |
| `c5d02eb` | 2026-10-31 | docs: READMEs pt/en com gateway Go, Kafka e Redis |
| `43cf3e9` | 2026-10-31 | feat(relationships): vínculo entre agentes atualizado por reuniões (ADR-027) |
| `dcfd030` | 2026-10-31 | chore(config): modelos Ollama por papel no .env.example |
| `652a84c` | 2026-10-31 | feat(meetings): dominio de reunioes e ferramenta start_ceremony (ADR-028) |
| `11ef1c1` | 2026-10-31 | feat: persist goal meetings, add relationship/meeting routes (ADR-029), nemotron3 for data analyst |
| `11506be` | 2026-10-31 | feat: office layout API and persistence (ADR-030) |
| `dc26758` | 2026-10-31 | feat: activity feed from bus events (ADR-031) |
| `e327104` | 2026-10-31 | feat: multi-round debate in goal meetings (ADR-032) |
| `5ccd9be` | 2026-10-31 | test: integration tests for social/layout/activity postgres repos |
| `03f655e` | 2026-10-31 | test: integration tests for chat, task and pgvector memory |
| `701be12` | 2026-10-31 | docs(scratchpad): refresh current state after round 27 |
| `b75bcf7` | 2026-10-31 | fix(compose): gateway waits for kafka-init topics; validated MQTT->Kafka e2e |
| `6dd057f` | 2026-10-31 | feat(meetings): rotas POST /meetings e /finish (ADR-033) |
| `7a65d4d` | 2026-10-31 | feat(research): agentes pesquisam e geram artefato .md (ADR-034) |
| `c58abf1` | 2026-10-31 | docs: RFC-004 contrato da API e design doc de autonomia |
| `bf9d3dc` | 2026-10-31 | docs: atualiza estado atual do SCRATCHPAD |
| `49ecd0e` | 2026-10-31 | feat: permissões por papel em assign e complete (ADR-035) |
| `0bf42c0` | 2026-10-31 | feat: leitura tolerante da resposta do Ollama (ADR-036) |
| `07ce6e3` | 2026-10-31 | docs: ADR-036 e SCRATCHPAD da rodada 33 |
| `10d2688` | 2026-10-31 | docs: seção API HTTP nos READMEs (pt/en) |
| `9c07a79` | 2026-10-31 | feat(tools): ferramenta research para agentes (ADR-037) |
| `7f1dd72` | 2026-10-31 | docs: atualiza estado atual do SCRATCHPAD (rodadas 32-35) |
| `60776a8` | 2026-10-31 | feat(api): POST /relationships/interactions (ADR-038) |
| `b20afc7` | 2026-10-31 | test(integration): gateway MQTT para Kafka e docs de rota (rodada 37) |
| `06bdecf` | 2026-10-31 | fix(postgres): goal inserido ja fechado respeita o CHECK de closed_at (rodada 38) |
| `c2f8042` | 2026-10-31 | fix(llm): mock de embedding com 768 dimensoes (rodada 39) |
| `49e54c8` | 2026-10-31 | feat: curingas no bus em memória e feed por agente (ADR-039) |
| `461afc4` | 2026-10-31 | docs: atualiza SCRATCHPAD (feed por agente) |
| `7f691e5` | 2026-10-31 | test: cobertura do ToolRegistry (review/approve/tarefas) |
| `af24d88` | 2026-10-31 | fix: set_database_pool limpa todos os caches; testes de factories e falhas da reunião |
| `16cc8d9` | 2026-10-31 | ci: workflow GitHub Actions (ADR-040) |
| `b8c1cd4` | 2026-10-31 | docs: badge de CI nos READMEs |
| `7f964ec` | 2026-10-31 | test: cobre prompt sem mapeamento e close do Tavily |
| `c1c8a5e` | 2026-10-31 | docs: revisa limitações e backlog no SCRATCHPAD |
| `85246fb` | 2026-10-31 | ci: cobertura minima 85%, integracao em main e build Docker (ADR-041) |
| `583fd26` | 2026-10-31 | docs: inicio rapido com todos os modelos e migrate |
| `4927af8` | 2026-10-31 | test: e2e do fluxo PO -> Dev -> QA pela API |
| `ee3b230` | 2026-10-31 | docs: tabela de commits do SCRATCHPAD (rodadas 44-49) |
| `a1485c7` | 2026-10-31 | feat(gateway): configuracao somente via .env, sem valores fixos (ADR-042) |
| `3d9339c` | 2026-10-31 | fix(gateway): .env com hosts/portas de container; tavily configuravel |
| `53609f1` | 2026-10-31 | Compose sem valores fixos: .env raiz e interpolação (ADR-043) |
| `1737958` | 2026-10-31 | Settings sem defaults de infraestrutura (ADR-044) |
| `c85e6ba` | 2026-10-31 | MQTT do backend via .env.example |
| `dd3d2cc` | 2026-10-31 | README: Quick Start com os três .env.example |
| `4f637a6` | 2026-10-31 | Idempotência de activity_events por event_id (ADR-045) |
| `bce6183` | 2026-10-31 | ADR-046: consumidor Kafka→MQTT fora do escopo |
| `bfd7674` | 2026-10-31 | feat(frontend): frontend Svelte 5 com mapa, kanban, chat, logs, doação e i18n (ADR-047) |
| `5b9d28f` | 2026-10-31 | feat(frontend): Dockerfile, serviço no compose, job de CI e README |
| `72b57c2` | 2026-10-31 | feat(frontend): formulário de contratação de agentes e modelo padrão via env |
| `00c3848` | 2026-10-31 | feat(frontend): botão para contratar o time padrão |
| `3481ea7` | 2026-10-31 | feat: escolha do modelo de IA ao contratar (GET /models) |
| `55fd2b7` | 2026-10-31 | feat: agentes respondem no idioma do objetivo; /models sem embeddings |
| `af89e77` | 2026-10-31 | feat: ciclo de trabalho autônomo e escritório vivo (caminhadas, sprites distintos, cargo) |
| `a536e8f` | 2026-10-31 | feat: responsável obrigatório fora do backlog e diretiva de idioma nos prompts |
| `7a7c044` | 2026-10-31 | feat(frontend): usa todas as folhas de sprites com poses alternativas |
| `71a8e84` | 2026-10-31 | feat: cargos traduzidos nos cabeçalhos da ata |
| `01b6b55` | 2026-10-31 | fix(frontend): anima só os quadros do personagem em interagindo_com_objetos |
| `9b50022` | 2026-10-31 | docs: rodada 69 reset do ambiente e time inicial |
| `7c989bb` | 2026-10-31 | feat: métricas Kanban, WIP, cargo no cartão, PayPal visível |
| `e165023` | 2026-10-31 | feat: cerimônia de sprint planning e divisão de tarefas (ADR-049) |
| `7109164` | 2026-10-31 | chore: atualiza artefatos de pesquisa do workspace |
| `e7a1d43` | 2026-10-31 | refactor: extrai task_splitter, DRY no ciclo; RFC-005 e design doc |
| `3a8882d` | 2026-10-31 | fix(frontend): remove texto de debug solto na página |
| `f66141a` | 2026-10-31 | fix: timeout do Ollama configurável via .env |
| `fe3fce8` | 2026-10-31 | feat: história do projeto no modal de doação (pt/en) |
| `84671cb` | 2026-10-31 | feat: planejamento gera subtarefas distintas e .md no idioma do escritório |
| `5fb7e7b` | 2026-10-31 | fix: cria a sessão do chão do escritório antes da primeira fala do ciclo |
| `fe9850a` | 2026-10-31 | build: format-go, format-frontend e format-all no Makefile |
| `4250ad1` | 2026-10-31 | feat: etapa de teste (QA) antes da revisão (ADR-050) |
| `3615f39` | 2026-10-31 | fix(frontend): grade do Kanban com 6 colunas |
| `fa5efa5` | 2026-10-31 | feat: sprint com no máximo 15 dias fictícios (SPRINT_MAX_DAYS) |
| `1f0b956` | 2026-10-31 | fix(frontend): Kanban compacto, 6 colunas em uma linha |
| `8d87e88` | 2026-10-31 | feat: workspace fixo 777, personagens com pausas e modal de graficos Kaizen |
| `1781cfb` | 2026-10-31 | docs: pendencias finais no SCRATCHPAD |
| `8bec86a` | 2026-10-31 | feat: idioma do escritorio em tempo de execucao (ADR-051) e trava ao trocar idioma |
| `2768a1c` | 2026-10-31 | feat: observabilidade completa com Kafka UI, Prometheus e Grafana (ADR-052) |
| `10bb61d` | 2026-10-31 | chore: todos os volumes do compose ficam em .docker/ |
| `e83db75` | 2026-10-31 | chore: commita artefatos de pesquisa do workspace |
| `5237cc0` | 2026-10-31 | Rodada 90: seed do time, migração testing validada, design doc do ciclo |
| `09cf9f6` | 2026-10-31 | Rodada 90: checklist final concluído (conferência no navegador) |
| `3e75623` | 2026-10-31 | Rodada 91: READMEs detalhados com capturas, Ollama e hardware |
| `f45e3ea` | 2026-10-31 | Rodada 92: auditoria do git log e apêndice completo no SCRATCHPAD |
| `96488a8` | 2026-10-31 | Rodada 93: texto de doação transparente no modal e nos READMEs |
| `b04ff45` | 2026-10-31 | Rodada 94: modal de confirmação profissional na troca de idioma |
| `d31ab04` | 2026-10-31 | Rodada 95: corrige sprites girando (anima só uma direção da folha) |
| `cd39667` | 2026-10-31 | Rodada 96: README com alerta de idioma e fluxo Mermaid dos containers |
| `76f091c` | 2026-10-31 | Rodada 97: corrige sprite do carrinho de props e adiciona sql/ com tarefas pt/en |
| `bf8793b` | 2026-10-31 | feat: Postgres e MQTT por padrão, testes isolados, títulos de tarefa higienizados (ADR-053) |
| `9424777` | 2026-10-31 | docs: imagem do Grafana nos READMEs pt/en |
| `2e3ce57` | 2026-10-31 | docs: legendas das imagens nos READMEs |
| `42dc1d9` | 2026-10-31 | docs: corrige renderização das legendas das imagens nos READMEs |
| `927edb3` | 2026-10-31 | docs: centraliza a seção de doação nos READMEs |
| `3998ea9` | 2026-10-31 | feat: higieniza descrições de tarefas, isola testes de integração e verifica fluxo MQTT→Kafka |
| `2c16021` | 2026-10-31 | docs: adiciona LICENSE MIT em inglês e português com nota de doações voluntárias |
| `19b9668` | 2026-10-31 | docs: FUNDING.yml, badges de licença/doação e rascunhos de divulgação |
| `b95cfb6` | 2026-10-31 | docs: adiciona GitHub Sponsors ao FUNDING.yml e aos READMEs |
| `9f326cb` | 2026-10-31 | docs: registra rodada 105 (merge na master) |
| `9ecb95d` | 2026-10-31 | Merge pull request #1 from CristianBernardes/develop |
| `2b46abe` | 2026-10-31 | docs: inclui PayPal no FUNDING.yml |
| `c631760` | 2026-10-31 | Merge remote-tracking branch 'origin/master' |
| `197e260` | 2026-10-31 | docs: adiciona vídeo de demonstração no topo dos READMEs |
| `a6396ab` | 2026-10-31 | Merge develop into master |
| `3c4c315` | 2026-10-31 | docs: tenta embed iframe do vídeo nos READMEs |
| `a61ed58` | 2026-10-31 | Merge develop into master |
| `bed16c5` | 2026-10-31 | docs: remove iframe do vídeo (não renderiza no GitHub) |
| `18cd72b` | 2026-10-31 | Merge develop into master |
| `f909388` | 2026-10-31 | docs: adiciona link do YouTube no formato simples |
| `bfd811c` | 2026-10-31 | Merge develop into master |
| `8f341c9` | 2026-10-31 | docs: vídeo de demonstração em MP4 (H.264) embutido nos READMEs |
| `dc430a5` | 2026-10-31 | Merge develop into master |
| `9db4282` | 2026-10-31 | docs: remove vídeo embutido (não tocava); mantém link do YouTube |
| `8cc4b20` | 2026-10-31 | Merge develop into master |
| `b5499ef` | 2026-10-31 | docs: remove link simples do YouTube dos READMEs |
| `a2c5228` | 2026-10-31 | Merge develop into master |
| `424eccd` | 2026-10-31 | docs: usa Agent_Office_2.png como chamada para o vídeo |
| `f62aa0f` | 2026-10-31 | Merge develop into master |
| `da154f5` | 2026-10-31 | docs: centraliza todas as imagens dos READMEs |
| `345f601` | 2026-10-31 | Merge develop into master |
| `b25ddaf` | 2026-10-31 | docs: remove pendências inexistentes dos READMEs (frontend e gateway já implementados) |
| `74b541b` | 2026-10-31 | Merge develop into master |
| `ed874cb` | 2026-10-31 | docs: verificação final e estado atual |
| `c3ec815` | 2026-10-31 | Merge develop into master |
| `7ca1918` | 2026-10-31 | build: alvos de lint, teste e build de Go e frontend no Makefile |
| `3360ee2` | 2026-10-31 | Merge develop into master |
| `0b6e9e9` | 2026-10-31 | docs(scratchpad): rodada 119, banco refeito e seed |
| `fc919b6` | 2026-10-31 | Merge develop into master |
| `b68add4` | 2026-10-31 | style(frontend): formata o frontend com prettier |
| `957f22a` | 2026-10-31 | Merge develop into master |
| `ca235fb` | 2026-10-31 | Atualização do Link do Vídeo |
| `450ec86` | 2026-10-31 | Merge pull request #2 from CristianBernardes/develop |
| `43c41b4` | 2026-10-31 | Agent host session 6f73206e-cd7b-4bcd-8b1a-ca6b309e8139 - baseline checkpoint |
| `ac677ba` | 2026-10-31 | Agent host session 6f73206e-cd7b-4bcd-8b1a-ca6b309e8139 - turn 1 start |
| `d646c0f` | 2026-10-31 | Agent host session 6f73206e-cd7b-4bcd-8b1a-ca6b309e8139 - turn 1 |
| `b2aab6c` | 2026-10-31 | Agent host session 7f667ded-8d8c-4c07-9b7b-89f20f56a451 - baseline checkpoint |
| `4e40cc7` | 2026-10-31 | Agent host session 564f1508-38ae-4a6c-9ca5-b7747fe242af - baseline checkpoint |
| `38b6ca1` | 2026-10-31 | Agent host session 9539eef0-0a35-4bc3-be7a-3a535095978e - baseline checkpoint |
| `3dddb6f` | 2026-10-31 | Agent host session 0d5dbc41-b276-4ee6-be66-223a2b987321 - baseline checkpoint |
| `c4d16b3` | 2026-10-31 | Agent host session 042c4cfd-2603-419d-a4e6-175494067c31 - baseline checkpoint |
| `43e047d` | 2026-11-01 | Agent host session 57dc4d89-2711-4b04-8889-e2723ae68fd6 - baseline checkpoint |
| `2e3e769` | 2026-11-01 | Agent host session 57dc4d89-2711-4b04-8889-e2723ae68fd6 - turn 1 start |
| `1637add` | 2026-11-01 | Agent host session 57dc4d89-2711-4b04-8889-e2723ae68fd6 - turn 1 |
| `c839cd3` | 2026-11-01 | Agent host session 57dc4d89-2711-4b04-8889-e2723ae68fd6 - turn 2 start |
| `bd5072c` | 2026-11-01 | Agent host session 57dc4d89-2711-4b04-8889-e2723ae68fd6 - turn 2 |
| `947f741` | 2026-11-01 | feat: poderes do dono, roteamento por área, diálogo PO-cliente e demissão aprovada (ADR-054/055/056) |
| `303bc22` | 2026-11-01 | docs: atualiza artefatos de pesquisa gerados pelos agentes |
| `0509844` | 2026-11-01 | Agent host session 57dc4d89-2711-4b04-8889-e2723ae68fd6 - turn 3 start |
| `f3bb866` | 2026-11-01 | Agent host session 57dc4d89-2711-4b04-8889-e2723ae68fd6 - turn 3 |
| `cd5cf42` | 2026-11-01 | docs(scratchpad): rodada 123, merge da develop na master |
| `7d9d258` | 2026-11-01 | Merge develop into master |
| `e97563d` | 2026-11-01 | Agent host session 57dc4d89-2711-4b04-8889-e2723ae68fd6 - turn 4 start |
| `23f5c6b` | 2026-11-01 | Agent host session 57dc4d89-2711-4b04-8889-e2723ae68fd6 - turn 4 |
| `742a62d` | 2026-11-01 | docs: READMEs e SCRATCHPAD com responsabilidades por cargo, poderes do dono e demissão aprovada |
| `9ebc4d6` | 2026-11-01 | Agent host session 57dc4d89-2711-4b04-8889-e2723ae68fd6 - turn 5 start |
| `b7a9934` | 2026-11-01 | Agent host session 57dc4d89-2711-4b04-8889-e2723ae68fd6 - turn 5 |
| `e3945c8` | 2026-11-01 | chore: remove CI/CD (workflow, selo e ADR-040/041 revogados) |
| `7b181d3` | 2026-11-01 | Agent host session 57dc4d89-2711-4b04-8889-e2723ae68fd6 - turn 6 start |
| `947f023` | 2026-11-01 | Agent host session 57dc4d89-2711-4b04-8889-e2723ae68fd6 - turn 6 |
| `d068a8a` | 2026-11-01 | docs(scratchpad): rodada 126, merge da develop na master |
| `e749501` | 2026-11-01 | Merge develop into master |
| `bd58a33` | 2026-11-01 | Agent host session 57dc4d89-2711-4b04-8889-e2723ae68fd6 - turn 7 start |
| `b173f8a` | 2026-11-01 | Agent host session 57dc4d89-2711-4b04-8889-e2723ae68fd6 - turn 7 |
| `69e5a24` | 2026-11-01 | Agent host session 57dc4d89-2711-4b04-8889-e2723ae68fd6 - turn 8 start |
| `80524f1` | 2026-11-01 | Agent host session 57dc4d89-2711-4b04-8889-e2723ae68fd6 - turn 8 |
| `8b2e029` | 2026-11-01 | fix(llm): bloqueia vazamento do raciocínio do LLM em outro idioma (ADR-057) |
| `99da28a` | 2026-11-01 | Agent host session bd7a51ba-fe34-49e4-abdf-40293b255483 - baseline checkpoint |
| `b1f565a` | 2026-11-01 | Agent host session bd7a51ba-fe34-49e4-abdf-40293b255483 - turn 1 start |
| `64333ca` | 2026-11-01 | Agent host session bd7a51ba-fe34-49e4-abdf-40293b255483 - turn 1 |
| `1838b94` | 2026-11-01 | feat: permite excluir tarefas do board |
| `a4c87c5` | 2026-11-01 | Merge branch 'develop' |
| `b6041ee` | 2026-11-01 | Agent host session bd7a51ba-fe34-49e4-abdf-40293b255483 - turn 2 start |
| `28fc600` | 2026-11-01 | Agent host session bd7a51ba-fe34-49e4-abdf-40293b255483 - turn 2 |
| `f912538` | 2026-11-01 | docs: README e SCRATCHPAD com exclusão de tarefas (rodada 128) |
| `892f787` | 2026-11-01 | Merge branch 'develop' |
| `7687ebe` | 2026-11-01 | Agent host session bd7a51ba-fe34-49e4-abdf-40293b255483 - turn 3 start |
| `bc13ef7` | 2026-11-01 | Agent host session bd7a51ba-fe34-49e4-abdf-40293b255483 - turn 3 |
| `2610b18` | 2026-11-02 | Merge pull request #3 from CristianBernardes/develop |
| `e806442` | 2026-11-02 | feat: permite selecionar responsavel ja na criacao da tarefa |
| `c08ed10` | 2026-11-02 | Atualização do README.md |
| `1c757eb` | 2026-11-02 | Merge branch 'develop' |
| `37f5f03` | 2026-11-02 | feat: permite bloquear criação de tarefas por agentes |
| `9613a99` | 2026-11-02 | Merge pull request #4 from CristianBernardes/develop |
| `102f4c6` | 2026-11-02 | fix(frontend): volta a preencher o select de modelos com GET /models |
| `5657133` | 2026-11-02 | fix(frontend): volta a preencher o select de modelos com GET /models |
| `fd64ce2` | 2026-11-02 | Agent host session bd7a51ba-fe34-49e4-abdf-40293b255483 - turn 4 start |
| `1027374` | 2026-11-02 | Agent host session bd7a51ba-fe34-49e4-abdf-40293b255483 - turn 4 |
| `07065b8` | 2026-11-02 | Agent host session bd7a51ba-fe34-49e4-abdf-40293b255483 - turn 5 start |
| `531e542` | 2026-11-02 | Agent host session bd7a51ba-fe34-49e4-abdf-40293b255483 - turn 5 |
| `6e5d1bf` | 2026-11-02 | Agent host session bd7a51ba-fe34-49e4-abdf-40293b255483 - turn 6 start |
| `67316e2` | 2026-11-02 | Agent host session bd7a51ba-fe34-49e4-abdf-40293b255483 - turn 6 |
| `f550275` | 2026-11-02 | fix(frontend): volta a preencher o select de modelos com GET /models |
| `37d5a16` | 2026-11-02 | Merge remote-tracking branch 'origin/develop' into develop |
| `9892c2a` | 2026-11-02 | Merge remote-tracking branch 'origin/develop' into develop |
| `2bcdbf7` | 2026-11-02 | fix(frontend): volta a preencher o select de modelos com GET /models |
| `6a4ac8e` | 2026-11-02 | Merge remote-tracking branch 'origin/master' |
| `ec4b4e1` | 2026-11-02 | Merge remote-tracking branch 'origin/master' |
| `69f98b2` | 2026-11-02 | Agent host session bd7a51ba-fe34-49e4-abdf-40293b255483 - turn 7 start |
| `66a91d2` | 2026-11-02 | Agent host session bd7a51ba-fe34-49e4-abdf-40293b255483 - turn 7 |
| `4b68e2b` | 2026-11-02 | Agent host session bd7a51ba-fe34-49e4-abdf-40293b255483 - turn 8 start |
| `92c7a79` | 2026-11-02 | Agent host session bd7a51ba-fe34-49e4-abdf-40293b255483 - turn 8 |
| `36e37da` | 2026-11-02 | Merge pull request #5 from CristianBernardes/develop |
| `4ea12f8` | 2026-11-02 | docs: adiciona arquivos de community standards |
| `55cd6b7` | 2026-11-02 | Merge pull request #6 from CristianBernardes/develop |
| `f3759bd` | 2026-11-02 | docs: versões em inglês dos community standards com links cruzados |
| `c9a2c48` | 2026-11-02 | Merge pull request #7 from CristianBernardes/develop |
| `f8b12c8` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - baseline checkpoint |
| `977bdbd` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 1 start |
| `1e57f85` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 1 |
| `69d3194` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 2 start |
| `488b099` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 2 |
| `7296db7` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 3 start |
| `ae2eb3d` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 3 |
| `dc4eb8e` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 4 start |
| `aaf2f57` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 4 |
| `33ec62e` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 5 start |
| `6500f2d` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 5 |
| `67fb414` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 6 start |
| `aff46e3` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 6 |
| `f3b89b7` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 7 start |
| `8a6a12a` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 7 |
| `e262e10` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 8 start |
| `ae671bd` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 8 |
| `1c14b8a` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 9 start |
| `7fdf9ea` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 9 |
| `2bdb763` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 10 start |
| `f477bbc` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 10 |
| `6372256` | 2026-11-02 | feat: colocar dependências de desenvolvimento em contêiner para simplificar a configuração |
| `bb5bcc3` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 11 start |
| `7b553dd` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 11 |
| `b6e8d28` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 12 start |
| `b06ef4c` | 2026-11-03 | Agent host session 92e9ba09-5af3-4113-839f-2c7e27205cd5 - turn 12 |
| `e1dd829` | 2026-11-03 | Merge pull request #8 from CristianBernardes/develop |
| `ad7e7be` | 2026-11-03 | Agent host session b25cd88c-3d3d-4c45-b12c-83092626b4d1 - baseline checkpoint |
| `9d02ccc` | 2026-11-03 | Agent host session b25cd88c-3d3d-4c45-b12c-83092626b4d1 - turn 1 start |
| `15a518e` | 2026-11-03 | Agent host session b25cd88c-3d3d-4c45-b12c-83092626b4d1 - turn 1 |
| `c4e9b27` | 2026-11-03 | feat: respeita configuração de bloqueio de criação de tarefas por agentes |
| `c827cd7` | 2026-11-03 | Merge pull request #9 from CristianBernardes/develop |
| `9d94edc` | 2026-11-03 | Agent host session b25cd88c-3d3d-4c45-b12c-83092626b4d1 - turn 2 start |
| `95d99a1` | 2026-11-03 | Agent host session b25cd88c-3d3d-4c45-b12c-83092626b4d1 - turn 2 |
| `dc99ffc` | 2026-11-03 | feat: Atualização do .env.example |
| `e3799e4` | 2026-11-03 | Merge pull request #10 from CristianBernardes/develop |
| `891f3f2` | 2026-11-03 | Agent host session 88479d08-5c94-49a5-afa2-e5cceb005b2c - baseline checkpoint |
| `4611591` | 2026-11-03 | Agent host session 88479d08-5c94-49a5-afa2-e5cceb005b2c - turn 1 start |
| `a6ff566` | 2026-11-03 | Agent host session 88479d08-5c94-49a5-afa2-e5cceb005b2c - turn 1 |
| `6201b37` | 2026-11-03 | docs: Atualiza SCRATCHPAD com rodadas recentes e histórico de commits |
| `2dd54f9` | 2026-11-03 | Merge pull request #11 from CristianBernardes/develop |
| `d73799f` | 2026-11-04 | Agent host session a98ed388-5d97-46d3-80fb-3ee34183ac6c - baseline checkpoint |
| `384df56` | 2026-11-04 | Agent host session a98ed388-5d97-46d3-80fb-3ee34183ac6c - turn 1 start |
| `67d1d79` | 2026-11-04 | Agent host session a98ed388-5d97-46d3-80fb-3ee34183ac6c - turn 1 |
| `fae1a12` | 2026-11-04 | Agent host session a98ed388-5d97-46d3-80fb-3ee34183ac6c - turn 2 start |
| `253ddce` | 2026-11-04 | Agent host session a98ed388-5d97-46d3-80fb-3ee34183ac6c - turn 2 |
| `6396d04` | 2026-11-04 | Agent host session a98ed388-5d97-46d3-80fb-3ee34183ac6c - turn 3 start |
| `913570a` | 2026-11-04 | Agent host session a98ed388-5d97-46d3-80fb-3ee34183ac6c - turn 3 |
| `c2d713c` | 2026-11-04 | Agent host session a98ed388-5d97-46d3-80fb-3ee34183ac6c - turn 4 start |
| `37f195f` | 2026-11-04 | Agent host session a98ed388-5d97-46d3-80fb-3ee34183ac6c - turn 4 |
| `04d0936` | 2026-11-04 | Agent host session a98ed388-5d97-46d3-80fb-3ee34183ac6c - turn 5 start |
| `4fd64b9` | 2026-11-04 | Agent host session a98ed388-5d97-46d3-80fb-3ee34183ac6c - turn 5 |
| `b93b341` | 2026-11-04 | Agent host session a98ed388-5d97-46d3-80fb-3ee34183ac6c - turn 6 start |
| `2576d64` | 2026-11-04 | Agent host session a98ed388-5d97-46d3-80fb-3ee34183ac6c - turn 6 |
| `84c5bf9` | 2026-11-04 | feat: integra Anthropic (Claude) como provedor de LLM por agente |
