# ADR-058 — Anthropic (Claude) como Provedor de LLM em Nuvem, por Papel

**Status:** Aceito
**Data:** 2026-11-04
**Autores:** Cristian Bernardes

## Contexto

O [ADR-005](./005-multiplos-modelos-ollama-por-agente.md) já previa que a aplicação não deveria
conhecer o provedor concreto de LLM usado por cada papel — apenas o contrato `ILlmAdapter` — e
citava "qualquer API compatível com o formato OpenAI" como uma segunda família de provedores
possível. Na prática, o dono do produto quer poder usar um modelo de ponta em nuvem (Claude, da
Anthropic) para papéis que se beneficiam de maior qualidade de raciocínio (ex.: Tech Lead, QA),
mantendo os demais papéis no Ollama local, sem custo de API.

A API da Anthropic não é compatível com o formato de requisição da OpenAI (usa `x-api-key` e
`anthropic-version` em vez de `Authorization: Bearer`, e um corpo de requisição próprio — API
*Messages*), então não pode ser tratada apenas como "mais uma URL compatível"; precisa de um
adaptador dedicado.

## Decisão

Adicionamos `AnthropicAdapter` como uma segunda implementação de `ILlmAdapter`, seguindo o mesmo
padrão de integração HTTP leve (via `httpx`, sem SDK proprietário) já usado para `OllamaAdapter` e
`TavilySearchAdapter`.

A escolha de provedor por papel continua vindo de uma única variável de ambiente por papel
(`AGENT_<PAPEL>_MODEL`, ver ADR-005) — não há uma variável separada de "provedor". Em vez disso, o
próprio **nome do modelo** carrega essa informação: qualquer valor prefixado com `claude-` (ex.:
`claude-sonnet-4-5-20250929`) é roteado para `AnthropicAdapter`; todo o restante continua sendo
resolvido pelo `OllamaAdapter`, como antes. Essa decisão de roteamento vive isolada em
`is_anthropic_model()` (`infrastructure/llm/provider_resolution.py`), consumida apenas pela factory
de composição (`get_llm_adapter_resolver()` em `dependencies.py`) — a camada de aplicação e o
`RoleBasedLlmAdapterResolver` continuam agnósticos quanto a provedores concretos.

A chave de API (`ANTHROPIC_API_KEY`) é opcional em `Settings`, sem valor padrão de fábrica — só é
exigida (com erro explícito) na primeira chamada `think()` de um papel que efetivamente use um
modelo Claude, nunca na inicialização do serviço (mesmo racional do ADR-011 para a Tavily).

A rota `GET /models`, já consumida pelo frontend para preencher o seletor de modelo do formulário de
contratação (`HireForm.svelte`), passa a combinar os modelos instalados no Ollama com os modelos
Claude disponíveis na conta configurada (`GET /v1/models` da Anthropic), **somente quando
`ANTHROPIC_API_KEY` estiver definida** — sem a chave, nenhum papel consegue efetivamente usar Claude,
então nenhum modelo Claude aparece na lista nem no frontend. Nenhuma rota ou tela nova foi criada: o
mesmo contrato (`string[]`) e o mesmo componente já existentes passam a listar os dois provedores de
forma transparente, sem o usuário precisar saber qual provedor está por trás de cada nome de modelo.

**Limitação conhecida:** a Anthropic não oferece uma API de embeddings. `AnthropicAdapter.embed()`
lança `NotImplementedError` com uma mensagem explicando a limitação. Isso significa que um papel
configurado com um modelo Claude **não pode** usar a ferramenta de memória semântica (ADR-020) sem
que outra solução de embedding seja adicionada separadamente — aceitável nesta fase, já que nem todo
papel depende de memória semântica para seu fluxo de trabalho.

## Consequências

### Positivas
- Papéis específicos podem usar um modelo de ponta em nuvem sem exigir isso de todos os agentes —
  continua sendo uma mudança de configuração (`.env`), não de código.
- Zero acoplamento novo entre `domain`/`application` e o provedor: a interface `ILlmAdapter`
  permanece a única porta conhecida pelos casos de uso.
- Mesma filosofia de HTTP leve (`httpx`) já usada no resto do projeto, sem SDK proprietário adicional
  nas dependências.

### Negativas / Trade-offs
- Custo real de API por chamada (diferente do Ollama local) — fica a critério do dono do produto
  decidir quais papéis valem esse custo.
- `embed()` não suportado pela Anthropic: um papel com modelo Claude e que também precise de memória
  semântica exigiria uma solução híbrida (não implementada nesta rodada).
- O roteamento por prefixo de nome de modelo (`claude-*`) é uma convenção implícita — documentada em
  código e no `.env.example`, mas não validada por schema. Um nome de modelo futuro de outro
  provedor que acidentalmente comece com `claude-` seria mal roteado; risco aceito por ser um nome de
  modelo propositalmente específico da Anthropic.

## Alternativas Consideradas

| Alternativa | Por que foi descartada |
|-------------|-------------------------|
| Variável de ambiente explícita por papel dizendo o provedor (ex.: `AGENT_TECH_LEAD_PROVIDER=anthropic`) | Duplicaria configuração já implícita no nome do modelo e exigiria manter duas variáveis sincronizadas por papel. |
| Tratar a Anthropic como "API compatível com OpenAI" genérica | A API Messages da Anthropic tem autenticação e formato de corpo próprios, incompatíveis com o formato OpenAI citado no ADR-005; exigiria lógica condicional dentro de um único adaptador, violando o Single Responsibility Principle. |
| Adicionar um SDK oficial da Anthropic como dependência | Contraria a filosofia de integrações HTTP leves via `httpx` já estabelecida para Ollama e Tavily; aumentaria a superfície de dependências sem necessidade. |
