# AgentOffice Microservice

**🌐 Idioma:** Português (BR) · [🇺🇸 English](./README.en.md)

> Um escritório de TI simulado por agentes de IA — cada um com um papel, personalidade e modelo de
> linguagem próprios, colaborando em tempo real via MQTT para pesquisar, debater, decidir e
> documentar, exatamente como um time humano de produto/tecnologia faria.

Dê ao time um objetivo de produto (ex.: *"criem um SaaS de nicho para vender 5 unidades/dia a
R$39,90"*) e observe os agentes pensarem, pesquisarem o mercado, debaterem entre si e produzirem
artefatos reais — ADRs, backlogs, planos de teste, análises de mercado — em arquivos Markdown
versionáveis, não apenas em logs efêmeros.

Projeto **open source**, construído do zero seguindo **Clean Architecture**, princípios **SOLID**,
**Clean Code**, **DRY**, **YAGNI**, injeção de dependência, testes automatizados e documentação
arquitetural rigorosa (ADRs, RFCs, Design Docs).

---

## 💙 Antes de clonar ou fazer fork — ajude a manter este projeto vivo

Este repositório é **open source e gratuito**, mas é mantido no tempo livre do autor. **Qualquer
valor de doação é bem-vindo** e ajuda diretamente a cobrir os **custos de saúde e o plano de saúde
da minha família**, além de manter tempo e energia disponíveis para continuar desenvolvendo o
AgentOffice.

Se este projeto te ajudou, te inspirou, ou você simplesmente quer ver essa ideia crescer bem no
GitHub — considere doar antes de seguir para o clone/fork abaixo:

<table>
<tr>
<td align="center" width="260">

**🇧🇷 Pix (Brasil)**

<img src="images/pix-qr-code.jpeg" alt="QR Code Pix para doação" width="220" />

Escaneie o QR Code com o app do seu banco

</td>
<td align="center" width="260">

**🌍 PayPal (Internacional)**

Para quem está fora do Brasil, doações via PayPal são muito bem-vindas:

[![Doar via PayPal](https://img.shields.io/badge/PayPal-Doar-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/donate/?business=cristian.aob%40gmail.com&item_name=Support+the+AgentOffice+project&currency_code=USD)

📧 Conta: **cristian.aob@gmail.com**

</td>
</tr>
</table>

Toda doação, de qualquer valor, ajuda a manter a saúde da minha família e a ideia deste projeto
viva — obrigado! 🙏

---

## O Time

Nove papéis, cada um com um system prompt próprio, personalidade (Big Five) e conjunto de
ferramentas permitidas:

| Papel | Responsabilidade principal |
|-------|------------------------------|
| **Product Owner** | Backlog, user stories, priorização |
| **Scrum Master** | Cerimônias, impedimentos, retrospectivas |
| **Tech Lead** | Arquitetura, ADRs, decisões técnicas |
| **Dev Sênior** | Implementação, code review, mentoria |
| **Dev Júnior** | Tarefas simples, aprendizado |
| **QA Engineer** | Planos de teste, bug reports |
| **Analista de Dados** | Métricas, KPIs, análises |
| **Gerente de RH** | Onboarding, cultura, contratações |
| **Consultor de Produto** | Validação de mercado, pesquisa |

Cada papel só pode usar as ferramentas que lhe foram atribuídas (ex.: só Tech Lead e Product Owner
podem `approve_artifact`; só Scrum Master pode `start_ceremony`) — a validação de permissão é
centralizada e nunca delegada ao LLM.

## Como os Agentes Trabalham

```
Comando do usuário
        │
        ▼
 Agente entra em "pensamento" (status publicado via MQTT)
        │
        ▼
 LLM (Ollama local, ou qualquer API OpenAI-compatible) recebe o
 system prompt do papel + contexto, e decide: pensamento, ação e,
 opcionalmente, uma ferramenta a executar
        │
        ▼
 Ferramenta validada contra as permissões do papel e executada
 (ex.: pesquisar na web, escrever/revisar/aprovar um artefato)
        │
        ▼
 Resultado publicado via MQTT para qualquer consumidor (outros
 agentes, frontend, observabilidade)
```

Todo o fluxo é orientado a eventos MQTT com um envelope de mensagem padrão (`event_id`, `timestamp`,
`agent_id`, `agent_role`, `payload`) — ver
[RFC-001](docs/rfc/001-protocolo-de-comunicacao-entre-agentes.md).

## Arquitetura

### Backend (Clean Architecture)

```
┌──────────────────────────────────────────────────────────────────────┐
│                      MQTT BROKER (Mosquitto)                          │
│       office/agents/#  ·  office/artifacts/#  ·  office/tasks/#       │
└──────────────────────────────┬────────────────────────────────────────┘
                                │
┌───────────────────────────────▼────────────────────────────────────────┐
│                BACKEND (FastAPI, Python 3.12)                          │
│                                                                        │
│   presentation/  →  application/  →  domain/  ←  infrastructure/      │
│                                                                        │
│   domain/         entidades puras (Agent, Artifact, Task), interfaces │
│   application/    casos de uso (AgentThinkUseCase, WriteArtifact...)  │
│   infrastructure/ MQTT, Ollama, Tavily, PostgreSQL, filesystem        │
│   presentation/   rotas HTTP e injeção de dependência                 │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
       PostgreSQL + pgvector  ·  Ollama (host, fora do Compose)  ·  Tavily
```

A regra de ouro do Clean Architecture: as setas de dependência de código sempre apontam para
dentro. O `domain/` nunca importa nada de `infrastructure/`, `application/` ou `presentation/` —
toda dependência externa (LLM, banco, mensageria, busca web, filesystem) fica atrás de uma
interface de domínio, permitindo troca de implementação sem alterar regra de negócio.

### Visão completa do produto (estado final planejado)

```
┌───────────────────────────────────────────┐
│             INTERFACE WEB                  │
│  Svelte + TypeScript                       │
│  ├── Painel de controle                    │
│  ├── Lista e estado dos agentes            │
│  ├── Logs e notificações                   │
│  └── Phaser: escritório em Pixel Art       │
└───────────────────┬─────────────────────────┘
                    │ WebSocket / HTTP
┌───────────────────▼─────────────────────────┐
│          GATEWAY DE COMUNICAÇÃO (Go)        │
│  ├── Distribuição de eventos                │
│  └── API e conexões em tempo real           │
│  (sem autenticação — projeto open source,    │
│   mantido por doações, sem dados sensíveis)  │
└───────────────────┬─────────────────────────┘
                    │
┌───────────────────▼─────────────────────────┐
│                MQTT (Mosquitto)             │
└──────────────┬──────────────┬────────────────┘
               │              │
┌──────────────▼──────┐ ┌─────▼─────────────┐
│ BACKEND PYTHON       │ │ SERVIÇOS GO       │
│ Execução de IA        │ │ Coordenação       │
│ Orquestração          │ │ Concorrência      │
│ Ferramentas           │ │ Serviços de apoio │
└───────────────────────┘ └───────────────────┘
```

O frontend (Svelte + Phaser.js, pixel-art) e o gateway Go fazem parte da visão completa do produto
e ainda não foram implementados neste repositório — ver detalhes em
[`docs/design/arquitetura-geral.md`](docs/design/arquitetura-geral.md) e no plano de migração em
[`docs/migration-plan/`](docs/migration-plan/).

### Artefatos como cidadãos de primeira classe

Agentes não apenas "conversam" — eles produzem documentos reais, versionáveis, com um ciclo de vida
explícito:

```
DRAFT → IN_REVIEW → APPROVED → ARCHIVED
```

Cada artefato é persistido como um arquivo `.md` real em `workspace/projects/{sprint}/`, com
frontmatter YAML (autor, tipo, status, datas), e cada transição de estado publica um evento MQTT —
ver [RFC-002](docs/rfc/002-sistema-de-artefatos.md).

### Busca web

Alguns papéis (Product Owner, Tech Lead, Devs, Analista de Dados, Consultor de Produto) têm acesso à
ferramenta `web_search`, resolvida via [Tavily](https://tavily.com) — uma API de busca pensada para
agentes de IA — ver [ADR-011](docs/adr/011-tavily-como-provedor-de-busca-web.md).

## Decisões Arquiteturais

Toda decisão arquitetural relevante é documentada antes de ser implementada:

- **ADRs** (`docs/adr/`) — decisões técnicas pontuais (MQTT, FastAPI, Clean Architecture, Ollama
  externo ao Compose, Tavily, portas de container, etc.)
- **RFCs** (`docs/rfc/`) — contratos que atravessam múltiplos componentes (protocolo de mensagens,
  ciclo de vida de artefatos, ciclo de vida de agentes)
- **Design Docs** (`docs/design/`) — visões de arquitetura geral do produto
- **Plano de Migração** (`docs/migration-plan/`) — todas as fases do roadmap técnico, incluindo as
  ainda não implementadas

## Requisitos

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose
- [Poetry](https://python-poetry.org/docs/#installation) 2.x (para desenvolvimento local do backend)
- [Ollama](https://ollama.com) instalado e em execução **no seu host** — este projeto nunca sobe um
  container de Ollama (ver [ADR-009](docs/adr/009-ollama-externo-ao-docker-compose.md))
- (Opcional) Uma chave gratuita da [Tavily](https://app.tavily.com) para a ferramenta `web_search`

## Início Rápido

```bash
# 1. Clone o repositório
git clone https://github.com/CristianBernardes/agent-office-edicao-brasileira.git
cd agent-office-edicao-brasileira/agent-office-microservice

# 2. Configure o backend
cp backend/.env.example backend/.env
# (opcional) edite TAVILY_API_KEY em backend/.env para habilitar busca web

# 3. Garanta que o Ollama está rodando no seu host
ollama pull nemotron-3.5-bolt:latest
ollama pull nomic-embed-text:latest

# 4. Suba toda a infraestrutura (Mosquitto + PostgreSQL + Backend)
make up

# 5. Acesse
# API:          http://localhost:7001
# Documentação: http://localhost:7001/docs
# MQTT:         localhost:7083 (TCP) / localhost:7000 (WebSocket)
```

## Portas

Todas as portas externas (host) deste projeto seguem a convenção de prefixo `70` — ver
[ADR-010](docs/adr/010-portas-de-container-com-prefixo-70.md).

| Serviço | Porta externa |
|---------|------------------|
| Backend (API HTTP) | `7001` |
| Mosquitto (MQTT TCP) | `7083` |
| Mosquitto (MQTT WebSocket) | `7000` |
| PostgreSQL | `7034` |

## Desenvolvimento

Todos os comandos de desenvolvimento, teste e qualidade estão centralizados no
[`Makefile`](Makefile):

```bash
make help              # lista todos os comandos disponíveis
make install           # instala as dependências do backend
make test-unit         # testes unitários (rápidos, sem dependências externas)
make test-integration  # testes de integração (requer 'make up')
make lint              # lint (ruff)
make format            # formatação automática (ruff format)
make type-check        # verificação de tipos estática (mypy --strict)
make check             # roda format + lint + type-check + test
```

Mais detalhes sobre a estrutura do backend em [`backend/README.md`](backend/README.md).

## Contribuindo

Este projeto é open source e aceita contribuições. Antes de abrir um PR, leia
[`docs/SCRATCHPAD.md`](docs/SCRATCHPAD.md) — ele define os padrões de qualidade obrigatórios
(SOLID, Clean Code, testes, ADRs) que toda contribuição deve seguir, além do histórico detalhado de
decisões e do estado atual de implementação de cada fase do projeto.

---

## 💙 Gostou do projeto?

Qualquer valor de doação é bem-vindo e ajuda a cobrir os custos de saúde da minha família e a
manter este projeto open source vivo e crescendo. Veja as formas de doar (Pix e PayPal) no topo
deste README, ou na [versão em inglês](./README.en.md).
