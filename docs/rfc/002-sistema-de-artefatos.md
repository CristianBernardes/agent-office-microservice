# RFC-002 — Sistema de Artefatos

**Status:** Aceito (parcialmente implementado — ver "Escopo desta rodada de implementação")
**Data:** 2026-10-30
**Autor:** Cristian Bernardes

## Resumo

Define como os agentes criam, revisam e aprovam artefatos Markdown, incluindo o ciclo de vida
completo de um artefato e o conjunto de ferramentas que cada papel pode usar para manipulá-lo.

## Ciclo de Vida

```
DRAFT → IN_REVIEW → APPROVED → ARCHIVED
```

1. O agente autor cria o artefato (status inicial `DRAFT`) através do caso de uso
   `WriteArtifactUseCase`.
2. Um agente revisor (papel com permissão de `review_artifact`) move o artefato para `IN_REVIEW` e
   anexa comentários.
3. Um agente aprovador (Tech Lead ou Product Owner) move o artefato para `APPROVED`.
4. Ao final do sprint, artefatos aprovados são movidos para `ARCHIVED`.

## Ferramentas por Papel

| Ferramenta | Quem pode usar |
|-----------|----------------|
| `write_artifact` | Todos os papéis |
| `read_artifact` | Todos os papéis |
| `review_artifact` | Tech Lead, QA Engineer, Product Owner |
| `approve_artifact` | Tech Lead, Product Owner |
| `list_artifacts` | Todos os papéis |

A tabela completa de ferramentas por papel (incluindo `create_task`, `send_message`, etc.) está
detalhada na Fase 3 do plano de migração (`docs/migration-plan/fase-3-personas/`), e será
implementada em uma rodada futura junto ao registro de ferramentas (`ToolRegistry`).

## Persistência

Cada artefato possui:
- Metadados estruturados persistidos no PostgreSQL (`id`, `title`, `type`, `status`, `author_id`,
  `sprint_id`, `path`, timestamps);
- Conteúdo Markdown persistido em arquivo físico sob `workspace/projects/{sprint}/{path}`, com
  frontmatter YAML contendo os mesmos metadados, para que o arquivo seja autodescritivo mesmo fora
  do contexto do banco.

## Escopo desta rodada de implementação

Esta RFC define o contrato alvo do sistema de artefatos. Na Fase 1, apenas a entidade `Artifact`, o
enum `ArtifactType`/`ArtifactStatus` e a interface `IArtifactRepository` são definidos no domínio. A
implementação dos casos de uso (`WriteArtifactUseCase`, `ReviewArtifactUseCase`,
`ApproveArtifactUseCase`) e dos adaptadores concretos (`MarkdownArtifactWriter`,
`PostgresArtifactRepository`) é entregue na Fase 4, conforme o plano de migração.

**Atualização — Rodada 3 (Fase 4):** `WriteArtifactUseCase`, `ReviewArtifactUseCase` e
`ApproveArtifactUseCase` estão implementados nesta rodada, publicando `office/artifacts/created` e
`office/artifacts/updated` (QoS 1) via `IMessageBus`, conforme a RFC-001. `MarkdownArtifactWriter`
persiste o conteúdo em `workspace/projects/{sprint}/{path}` com frontmatter YAML, e
`InMemoryArtifactRepository` (testes) delega essa escrita em disco, mantendo os metadados também em
memória. A permissão de qual papel pode usar `write_artifact`/`review_artifact`/`approve_artifact`
é validada pelo `ToolRegistry` (ver Fase 3), não pelo caso de uso em si — o caso de uso permanece
agnóstico a `Role`, apenas orquestra a entidade `Artifact` e a persistência. A
`PostgresArtifactRepository` concreta permanece pendente para uma rodada futura (ADR-006), já que
nenhum caso de uso desta rodada exige persistência relacional real — `workspace/` em disco e o
repositório em memória são suficientes para validar o ciclo ponta a ponta via testes automatizados.
