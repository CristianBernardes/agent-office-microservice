---
id: 1c1d3a53-79c7-46a7-b319-a4dd5e00ab66
title: Kafka
type: analysis
status: draft
author_id: bc07f292-9ccd-453b-b2f1-50ce18d81d34
created_at: 2026-10-31T17:12:00.207752+00:00
updated_at: 2026-10-31T17:12:00.207754+00:00
---

# Relatório sobre Apache Kafka

## Resumo
Kafka é uma plataforma de mensageria distribuída orientada a logs, projetada para alta taxa de throughput, tolerância a falhas e escalabilidade horizontal. Utiliza um modelo de publicação‑assinatura onde produtores enviam mensagens a tópicos e consumidores leem essas mensagens de forma independente.

## Principais Características
- **Log‑based storage**: mensagens são mantidas em disco por período configurável, permitindo replay.
- **Particionamento**: tópicos são divididos em partições, cada uma com seu próprio log, possibilitando paralelismo e balanceamento de carga.
- **Replication**: réplicas dos logs são mantidas em múltiplos brokers, garantindo redundância e alta disponibilidade.
- **Exactly‑once semantics**: combina transações de produtor e consumo para garantir entrega única.
- **APIs**: suporta produtores, consumidores, conectores (Connect) e streams (Streams), facilitando integração com sistemas externos.

## Arquitetura Básica
- **Broker**: instância do Kafka que gerencia tópicos, partições e réplicas.
- **ZooKeeper** (ou KRaft nas versions mais recentes): serviço de coordenação que mantém metadados e gerencia o estado do cluster.
- **Produtor**: aplicação que escreve mensagens nos tópicos.
- **Consumidor**: aplicação que lê mensagens, mantendo um offset por partição para garantir ordem e consumo controlado.

## Casos de Uso Comuns
- Integração de micro‑serviços: troca de eventos em tempo real.
- Pipeline de ingestão de dados: coleta, transformação e envio para data lakes ou bancos de dados.
- Monitoramento e logging centralizado: envio de logs de diversas fontes para um repositório unificado.
- Processamento de streaming em tempo real: uso da Kafka Streams para aplicar lógica de negócio diretamente nas mensagens.

## Conclusões
Kafka se destaca por oferecer uma infraestrutura robusta para sistemas de alta disponibilidade e baixa latência, graças ao seu modelo de log distribuído e ao suporte a replicação e partição. Sua flexibilidade nas APIs permite seu uso em cenários variados, desde integração de serviços até processamento de streaming complexo. Quando bem dimensionada, Kafka proporciona escalabilidade horizontal quase ilimitada, mantendo a consistência dos dados e facilitando a construção de arquiteturas orientadas a eventos.