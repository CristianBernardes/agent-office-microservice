# Design Doc — Fluxo de Mensagens

**Status:** Aceito
**Data:** 2026-10-30

## Fluxo-alvo (quando os casos de uso de pensamento estiverem implementados)

```
1. AgentThinkUseCase é executado para um agente específico.
2. O caso de uso chama ILlmAdapter.think(system_prompt, context).
3. O caso de uso publica o pensamento em office/agents/{agentId}/thought (QoS 0).
4. O caso de uso publica a ação decidida em office/agents/{agentId}/action (QoS 1).
5. O IMessageBus distribui o evento a todos os assinantes (outros agentes, frontend).
```

## Escopo desta rodada

Nesta rodada, o fluxo acima **não é ligado ponta a ponta** — ele é o contrato-alvo documentado para
orientar a implementação das fases seguintes. O que é entregue agora:

- A interface `IMessageBus`, testável independentemente de qualquer caso de uso de negócio;
- `InMemoryMessageBus`, usado nos testes unitários da própria infraestrutura de mensageria e
  disponível para qualquer caso de uso futuro que precise de um bus leve em testes;
- `MqttMessageBus`, validado com um teste de integração que sobe contra o Mosquitto real do
  `docker-compose.yml` (marcado com `@pytest.mark.integration`, não executado por padrão em
  ambientes sem o broker disponível).

A publicação dos tópicos de negócio (`office/agents/.../thought`, `office/tasks/...`, etc.) é
implementada junto com os casos de uso correspondentes nas fases seguintes do plano de migração.
