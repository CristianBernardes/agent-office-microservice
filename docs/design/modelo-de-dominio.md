# Design Doc — Modelo de Domínio

**Status:** Aceito
**Data:** 2026-10-30

## Entidades

### `Agent`

Representa um agente de IA com um papel no time. Estado mutável: `status` (via `AgentStatus`) e
`current_task_id`. Comportamento: transições de estado controladas (ver RFC-003).

### `Task`

Representa uma unidade de trabalho atribuível a um agente. Estado mutável: `status` (via
`TaskStatus`), `assigned_to`, `result`, `completed_at`.

### `Artifact`

Representa um documento Markdown produzido por um agente. Estado mutável: `status` (via
`ArtifactStatus`). Ver RFC-002 para o ciclo de vida completo.

## Value Objects

| Value Object | Propósito |
|---------------|-----------|
| `AgentId` | Identificador tipado de agente (wrapper sobre `UUID`), evita misturar IDs de entidades diferentes por engano de tipo. |
| `TaskId` | Identificador tipado de tarefa. |
| `ArtifactId` | Identificador tipado de artefato. |

## Interfaces (Portas)

Definidas em `domain/interfaces/`, implementadas em `infrastructure/`:

| Interface | Responsabilidade | Implementações nesta rodada |
|-----------|-------------------|-------------------------------|
| `ILlmAdapter` | Abstrai o provedor de LLM (`think`, `embed`). | `MockLlmAdapter` (testes). Adapters reais (Ollama/OpenAI) chegam na Fase 5. |
| `IMessageBus` | Abstrai o barramento de mensagens (`publish`, `subscribe`, `connect`, `disconnect`). | `InMemoryMessageBus` (testes/uso local), `MqttMessageBus` (produção, via `aiomqtt`). |
| `IAgentRepository` | Abstrai a persistência de agentes. | `InMemoryAgentRepository` (testes/uso local). Repositório PostgreSQL chega quando os casos de uso de persistência de agente forem implementados. |

## Por que interfaces no domínio?

Seguindo o Princípio de Inversão de Dependência (DIP), o domínio define *o que* precisa ser feito
(o contrato), e a infraestrutura decide *como* fazer. Isso permite:
- Testar casos de uso com fakes/mocks simples, sem rede ou banco real;
- Trocar implementações (ex.: MQTT real por um bus em memória) sem alterar uma linha de
  `application/` ou `domain/`.
