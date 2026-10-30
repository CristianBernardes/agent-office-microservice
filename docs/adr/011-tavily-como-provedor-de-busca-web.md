# ADR-011 — Tavily como Provedor de Busca Web

**Status:** Aceito
**Data:** 2026-10-30
**Autores:** Cristian Bernardes

## Contexto

Vários papéis do time simulado (Product Owner, Tech Lead, Dev Sênior, Dev Júnior, Analista de Dados,
Consultor de Produto — ver `docs/migration-plan/fase-3-personas/README.md`) precisam da ferramenta
`web_search` para pesquisar mercado, concorrentes, tendências e soluções técnicas antes de produzir
artefatos de decisão. Sem essa ferramenta, os agentes ficam limitados ao conhecimento estático do
LLM, o que compromete a credibilidade de qualquer análise de mercado ou validação de produto.

É necessário escolher um provedor de busca web que:
- Tenha uma API simples de integrar via HTTP, sem SDKs pesados;
- Seja pensado para consumo por agentes de IA (respostas estruturadas, não HTML bruto para
  scraping);
- Tenha uma camada gratuita viável para desenvolvimento e para o volume de buscas esperado por este
  projeto (um time pequeno de agentes, não um produto com milhares de usuários simultâneos).

## Decisão

Adotamos a **API da Tavily** (https://tavily.com) como único provedor de busca web desta rodada de
implementação:
- Feita especificamente para agentes de IA/LLM — retorna resultados já estruturados (título, URL,
  conteúdo resumido, score de relevância), sem a necessidade de parsing de HTML;
- Camada gratuita de 1000 buscas/mês, suficiente para o volume de uso deste projeto;
- Integração via HTTP simples (`POST https://api.tavily.com/search`), sem exigir um SDK proprietário
  — mantendo a mesma filosofia de integrações HTTP leves já usada para o Ollama (`httpx`, ver
  ADR-005).

A integração segue o mesmo padrão arquitetural das demais dependências externas do projeto (ver
ADR-007 — Clean Architecture):

1. Uma nova interface de domínio, `IWebSearchAdapter`, define o contrato de busca (`search(query) ->
   list[WebSearchResult]`), sem qualquer conhecimento sobre Tavily ou HTTP.
2. `TavilySearchAdapter` (infraestrutura) implementa essa interface usando `httpx`, autenticando com
   a variável de ambiente `TAVILY_API_KEY`.
3. `MockSearchAdapter` (infraestrutura) implementa a mesma interface retornando resultados
   pré-configurados em memória, seguindo exatamente o mesmo padrão já usado por `MockLlmAdapter` —
   usado em todos os testes automatizados, sem qualquer chamada de rede real.
4. A ferramenta `web_search` do `ToolRegistry` (Fase 3) depende apenas de `IWebSearchAdapter`, nunca
   da implementação concreta.

### Configuração e segredo de API

A `TAVILY_API_KEY` é uma chave pessoal/paga, diferente do Ollama (que não exige chave). Por isso:
- `backend/.env.example` **documenta** a variável e **não contém** nenhuma chave real ou funcional —
  apenas um placeholder (`TAVILY_API_KEY=`) com um comentário explicando onde obter a chave gratuita
  (https://app.tavily.com).
- `backend/.env` (não versionado, está no `.gitignore`) é o único lugar onde a chave real deve viver,
  responsabilidade de cada desenvolvedor.
- Se `TAVILY_API_KEY` não estiver definida, o `TavilySearchAdapter` levanta um erro explícito e claro
  na primeira chamada de busca — nunca falha silenciosamente nem retorna resultados vazios como se a
  busca tivesse funcionado.

## Consequências

### Positivas
- Agentes passam a produzir pesquisas de mercado e análises técnicas com informação real, não apenas
  conhecimento estático do LLM.
- Camada gratuita suficiente para o volume de uso deste projeto, sem custo de infraestrutura adicional.
- `MockSearchAdapter` garante que toda a suíte de testes automatizados continue rodando sem rede e
  sem custo, mesmo cobrindo o fluxo completo "comando → pensamento → pesquisa → artefato".

### Negativas / Trade-offs
- Introduz uma dependência paga de terceiros no fluxo de alguns papéis — mitigado pelo fato de a
  camada gratuita (1000 buscas/mês) ser suficiente para o escopo atual do projeto, e pela ferramenta
  ficar atrás de uma interface, permitindo troca de provedor no futuro sem alterar casos de uso.
- A chave de API é um segredo pessoal que cada desenvolvedor precisa obter e configurar manualmente
  — mitigado com documentação clara no `.env.example` e erro explícito quando a chave está ausente.

## Alternativas Consideradas

| Alternativa | Por que foi descartada |
|-------------|-------------------------|
| Scraping direto de motores de busca (Google, Bing) | Viola termos de uso, exige parsing frágil de HTML e não é pensado para consumo por agentes de IA. |
| SerpAPI | Camada gratuita mais restrita e API pensada para replicar resultados de busca tradicionais (SERP), não para consumo direto por LLMs. |
| DuckDuckGo (busca não-oficial) | Sem API oficial estável e sem garantia de disponibilidade a longo prazo para um produto de portfólio. |
| Nenhuma busca web (apenas conhecimento do LLM) | Compromete a credibilidade de qualquer pesquisa de mercado ou validação de produto feita pelos agentes — contraria o objetivo da próxima rodada (pesquisar, debater e decidir com base em informação real). |
