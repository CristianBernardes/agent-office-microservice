# ADR-001 — MQTT como Barramento de Mensagens

**Status:** Aceito
**Data:** 2026-10-30
**Autores:** Cristian Bernardes

## Contexto

Os agentes de IA do AgentOffice precisam se comunicar de forma assíncrona e desacoplada entre si e
com o frontend. Um modelo de comunicação baseado em chamadas diretas (RPC/HTTP síncrono) criaria
acoplamento forte entre agentes, dificultaria a adição de novos papéis e tornaria a observabilidade
do sistema (quem fez o quê, quando) muito mais custosa.

## Decisão

Usar **MQTT** (via broker Mosquitto) como barramento de mensagens entre todos os agentes e entre o
backend e o frontend. O backend Python se conecta ao broker via `aiomqtt` (cliente assíncrono). O
frontend (quando implementado) se conectará via MQTT sobre WebSocket.

A topologia de tópicos, o formato de envelope de mensagem e as regras de QoS estão detalhados no
[RFC-001](../rfc/001-protocolo-de-comunicacao-entre-agentes.md).

## Consequências

### Positivas
- Desacoplamento total entre agentes — cada um publica e assina tópicos de forma independente.
- Extensibilidade: novos papéis de agente podem ser adicionados sem alterar os agentes existentes.
- Observabilidade: qualquer cliente MQTT autorizado pode monitorar o fluxo de eventos do sistema.
- Push nativo para o frontend, sem necessidade de polling.

### Negativas / Trade-offs
- Requer um broker MQTT em execução (Mosquitto via Docker Compose).
- Exige modelagem cuidadosa de tópicos para evitar ambiguidade e colisão de wildcards.
- QoS 0 é "fire-and-forget" — mensagens podem ser perdidas; por isso ações e eventos de negócio
  usam QoS 1 (ver RFC-001).

## Alternativas Consideradas

| Alternativa | Por que foi descartada |
|-------------|-------------------------|
| WebSocket com estado compartilhado no servidor (abordagem do fork original) | Acoplamento forte entre agentes e servidor, difícil de escalar horizontalmente. |
| Redis Pub/Sub | Mais pesado como barramento de domínio, sem padrão de tópicos hierárquicos nativo, exigiria modelagem adicional. |
| WebSocket puro (sem MQTT) | Sem roteamento de tópicos nativo; implementação manual de pub/sub e wildcards. |
| Kafka já nesta fase | Overkill para o volume atual de mensagens; complexidade operacional alta. Fica reservado para a Fase 8 (microserviços), conforme o plano de migração. |
