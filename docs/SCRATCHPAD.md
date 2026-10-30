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
