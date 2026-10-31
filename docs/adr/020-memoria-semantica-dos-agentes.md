# ADR-020 — Memória semântica dos agentes

- Status: aceita

## Contexto

Para agirem como seres que "lembram", os agentes precisam guardar observações, decisões e fatos e
recuperá-los por significado. A tabela `memories` (ADR-017/018) já tem `embedding vector(768)` e
índice HNSW (cosseno), mas nenhum código a usa.

## Decisão

- Entidade `Memory` (`MemoryType`: observation, reflection, conversation, decision, fact) com
  `importance` em [0, 1] e `MemoryId` tipado.
- Porta `IMemoryRepository`: `save`, `recall(agent_id, embedding, limit)` (mais similares primeiro,
  por cosseno) e `list_recent`. Adaptadores em memória e PostgreSQL (`embedding <=> $n::vector`).
- `RememberUseCase`: valida o agente, gera o embedding pelo LLM resolvido para o papel dele e grava.
- `RecallMemoryUseCase`: embute a consulta e devolve as memórias mais próximas, atualizando
  `last_accessed_at` (base para esquecimento futuro).
- Rotas `POST /agents/{id}/memories`, `GET /agents/{id}/memories` (recentes) e
  `POST /agents/{id}/memories/recall`; 404 localizado pt/en.
- Sem tool de agente por ora (YAGNI): o loop de autonomia chamará os casos de uso diretamente.
- O contrato de tópicos MQTT passa a ser a ADR-021.

## Consequências

- Dimensão do vetor fixa em 768 (nomic-embed-text); trocar de modelo exige migração.
- Memória por agente: nada é compartilhado, preservando a individualidade dos personagens.
