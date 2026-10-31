# ADR-034 — Pesquisa de agentes que gera artefatos `.md`

**Status:** Aceito

## Contexto
Agentes com `web_search` e `write_artifact` precisam de um fluxo pronto: pesquisar um tema e registrar o resultado como documento.

## Decisão
- `ResearchTopicUseCase`: busca web (`IWebSearchAdapter`) → o LLM do papel do agente redige o relatório em Markdown no idioma configurado → `WriteArtifactUseCase` grava um artefato `analysis` em `workspace/research/<slug>.md`.
- Falha na busca não aborta: o relatório é redigido sem fontes e isso é indicado no contexto.
- `POST /research` (`agent_id`, `topic`) expõe o fluxo; resposta 201 com o artefato.
- Prompts e rótulos em pt/en.

## Consequências
Sem chave Tavily o relatório sai apenas com o conhecimento do modelo. Fontes são anexadas ao final do documento de forma determinística (não pelo LLM).
