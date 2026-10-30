# ADR-004 — Artefatos em Markdown

**Status:** Aceito
**Data:** 2026-10-30
**Autores:** Cristian Bernardes

## Contexto

Os agentes precisam produzir saídas tangíveis e persistentes — não apenas trocas de mensagens
efêmeras. Esses artefatos (ADRs, planos de teste, relatórios de bug, documentação de implementação,
etc.) devem ser legíveis por humanos, versionáveis e exibíveis diretamente em um visualizador web.

## Decisão

Todo agente pode produzir artefatos no formato **Markdown** (`.md`), persistidos tanto em
**metadados no PostgreSQL** (para consulta, filtro e relacionamento com sprints/tarefas) quanto em
**arquivo físico** no sistema de arquivos do workspace (`workspace/projects/{sprint}/`), através da
porta `IArtifactRepository` e do adaptador de escrita em disco.

O ciclo de vida de um artefato (`DRAFT → IN_REVIEW → APPROVED → ARCHIVED`) e o contrato de ferramentas
que os agentes usam para manipulá-lo estão detalhados no
[RFC-002](../rfc/002-sistema-de-artefatos.md).

## Consequências

### Positivas
- Artefatos são auto-contidos, legíveis e versionáveis — um ADR produzido por um agente é indistinguível
  de um ADR escrito por um humano.
- A persistência dupla (banco + disco) permite buscas estruturadas (banco) e leitura humana direta
  (arquivo).

### Negativas / Trade-offs
- É necessário manter banco e disco consistentes; a escrita em disco é tratada como parte da mesma
  transação lógica do caso de uso (ver `WriteArtifactUseCase`), não como uma tarefa assíncrona
  desacoplada, para evitar estados inconsistentes nesta fase do projeto.

## Alternativas Consideradas

| Alternativa | Por que foi descartada |
|-------------|-------------------------|
| Persistir apenas no banco (BLOB/TEXT) | Perde a legibilidade direta em um editor de texto e a facilidade de versionamento via Git do próprio workspace. |
| Persistir apenas em disco, sem metadados no banco | Dificulta consultas estruturadas (filtrar por tipo, status, autor, sprint) sem fazer parsing de arquivos. |
