# RFC-001 — Protocolo de Comunicação entre Agentes

**Status:** Proposto
**Data:** 2026-10-30
**Autor:** Cristian Bernardes

## Resumo

Define o protocolo de mensagens MQTT entre agentes: estrutura de tópicos, formato de envelope e
regras de QoS, servindo de contrato compartilhado entre a camada de infraestrutura de mensageria
(`MqttMessageBus`) e qualquer consumidor (outros agentes, frontend, ferramentas de observabilidade).

## Topologia de Tópicos

```
office/
├── agents/{agentId}/
│   ├── thought          # Pensamento interno do agente (QoS 0)
│   ├── action           # Ação executada (QoS 1)
│   ├── message          # Mensagem para outro agente (QoS 1)
│   └── status           # idle | thinking | working | offline (QoS 1, retain=true)
│
├── tasks/
│   ├── created          # Nova tarefa criada (QoS 1)
│   ├── assigned         # Tarefa atribuída a agente (QoS 1)
│   ├── updated          # Status da tarefa atualizado (QoS 1)
│   └── completed        # Tarefa concluída (QoS 1)
│
├── artifacts/
│   ├── created          # Novo artefato .md gerado (QoS 1)
│   └── updated          # Artefato atualizado (QoS 1)
│
└── sprint/
    ├── started          # Sprint iniciado (QoS 1, retain=true)
    ├── ended            # Sprint encerrado (QoS 1)
    └── ceremony/{type}  # planning | review | retro | standup (QoS 1)
```

## Formato de Envelope

Toda mensagem publicada em qualquer tópico segue o mesmo envelope JSON:

```json
{
  "event_id": "uuid-v4",
  "timestamp": "2026-10-30T10:00:00Z",
  "version": "1.0",
  "agent_id": "alice",
  "agent_role": "dev_senior",
  "payload": {
    "...": "específico do tipo de evento"
  }
}
```

- `event_id`: identificador único do evento (UUID v4), usado como chave de idempotência em fases
  futuras (ver Fase 8 do plano de migração).
- `timestamp`: instante de criação do evento, em UTC, formato ISO 8601.
- `version`: versão do formato de envelope — permite evolução compatível no futuro.

## Regras de QoS

- **QoS 0** — eventos que podem ser perdidos sem comprometer a correção do sistema (ex.: pensamentos
  internos do agente, usados apenas para observabilidade/debug).
- **QoS 1** — eventos de negócio (ações, mensagens, tarefas, artefatos, sprint) — exigem pelo menos
  uma entrega garantida.
- **`retain=true`** — usado para o último status conhecido de um agente e para o sprint atual, de
  forma que um novo assinante (ex.: frontend reconectando) receba imediatamente o último estado
  conhecido sem precisar esperar o próximo evento.

## Escopo desta rodada de implementação

Esta RFC define o contrato alvo completo do sistema de mensageria. Na Fase 1 (esqueleto de Clean
Architecture), apenas a interface `IMessageBus` e as implementações `MqttMessageBus` e
`InMemoryMessageBus` são entregues, validando o contrato com testes unitários e de integração. A
publicação efetiva de todos os tópicos listados acima acompanha a implementação dos casos de uso nas
fases seguintes (pensamento do agente, tarefas, artefatos, sprint).
