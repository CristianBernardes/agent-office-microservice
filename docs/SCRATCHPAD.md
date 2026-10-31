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

## Estado atual e ponto de retomada (após a Rodada 46)

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
| 58 | este commit | ADR-047: frontend Svelte 5 (mapa, kanban, time, chat, logs, doação pt/en) |
| 59 | este commit | Dockerfile/compose/CI do frontend e README |
| 60 | este commit | Frontend: formulário de contratação, `VITE_DEFAULT_LLM_MODEL`, verificação visual |
| 61 | este commit | Botão "Contratar time padrão" (criar tarefa exige agentes) |
| 62 | este commit | `GET /models` (Ollama) e seleção do modelo de IA ao contratar |
| 63 | este commit | Idioma por objetivo (Accept-Language → reunião/prompts) e `/models` sem embeddings |
| 64 | este commit | ciclo de trabalho autônomo (ADR-048) + escritório vivo no mapa: caminhadas, conversas, sprites distintos, cargo no rótulo |
| 65 | este commit | Responsável obrigatório fora do backlog + diretiva de idioma nos prompts |
| 66 | este commit | Poses alternativas dos sprites (interagindo_com_objetos, outra_postura_de_trabalho) |
| 67 | este commit | Cargos traduzidos nas atas |
| 68 | este commit | Correção do sprite bugado (interagindo_com_objetos) |
| 69 | este commit | Reset do banco/workspace, time completo contratado e backlog inicial |
| 70 | este commit | Kanban: WIP/limites, métricas de fluxo, cargo no cartão, timestamps de task; PayPal visível também em pt |
| 71 | este commit | Sprint planning conduzido por PO/SM, divisão de tarefas, ADR-049 |
| 72 | este commit | Refatoração SRP/DRY (task_splitter, _speak), RFC-005 e design doc do ciclo |
| 73 | este commit | Remove texto de debug `wanderIntervalMs` solto no App.svelte |
| 74 | f66141a | Timeout do Ollama via .env (`OLLAMA_REQUEST_TIMEOUT_SECONDS`) |
| 75 | este commit | Modal de doação com a história do projeto (pt/en) |
| 76 | este commit | Planejamento gera subtarefas distintas (título + entregável) via LLM; título do `.md` de planejamento no idioma do escritório |
| 77 | este commit | Corrige sessão do chão do escritório inexistente (ciclo falhava em toda fala); recriação do time/tarefas |
| 78 | fe9850a | Makefile: format-go, format-frontend e format-all |
| 79 | 4250ad1 | Etapa de teste (QA) antes da revisão — ADR-050 |
| 80 | (commit anterior) | Kanban: grade com 6 colunas (Concluído visível) |
| 81 | fa5efa5 | Sprint com no máximo 15 dias fictícios (`SPRINT_MAX_DAYS`) |
| 82 | 1f0b956 | Kanban: 6 colunas compactas em uma única linha |
| 83 | 8d87e88 | Workspace fixo (nunca criado em runtime, 777) + `.gitkeep` |
| 84 | 8d87e88 | Personagens vivos (pausas de descanso/reflexão) + modal de gráficos Kaizen |
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
| 96 | este commit | READMEs pt/en: captura `alert.png` e seção de fluxo dos containers com diagramas Mermaid (todos os serviços do compose) |

### O que funciona

290 testes unitários + 13 de integração (`docker compose up -d postgres mosquitto`, `pytest -m integration`);
ruff e mypy limpos. API: agents, tasks, goals, messages, memories, relationships, meetings, layout,
activity, research; agentes têm a ferramenta research. i18n pt/en em erros, prompts e mensagens. Persistência `memory|postgres`, bus `memory|mqtt`.
Autonomia opt-in (`AUTONOMY_ENABLED`, `MEETING_ROUNDS`). ADRs 001–038, RFCs 001–004.

### Limitações conhecidas

- `move` aplica a matriz papel × estágio; `assign`/`complete` aplicam permissão por papel (ADR-035) e a entidade valida o estágio. Frontend feito pelo assistente (ADR-047).

### Backlog

1. (feito na Rodada 35) ferramenta `research`.
2. (feito na Rodada 32) permissões em `assign`/`complete`.
3. (feito na Rodada 37) teste de integração do gateway Kafka.
5. Itens do plano de migração ainda abertos: ver Rodada 47+ (checklists das Fases 6–8).
4. Frontend (feito pelo autor).

### Regras a lembrar

ADR antes do código; `make format` a cada mudança; SCRATCHPAD em **todo** commit; sem trailer do
Copilot; commit e push sempre; responder em português; não parar para perguntar.

## Apêndice — histórico completo do git (auditado na Rodada 92)

Auditoria: todos os commits do `git log` listados abaixo, em ordem cronológica (alguns não tinham hash na tabela de rodadas).

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
