# ADR-006 — PostgreSQL com pgvector

**Status:** Aceito
**Data:** 2026-10-30
**Autores:** Cristian Bernardes

## Contexto

O sistema precisa persistir entidades relacionais (agentes, tarefas, artefatos, sprints) e, em uma
fase futura, memória semântica de agentes via embeddings vetoriais, para possibilitar busca por
similaridade (RAG).

## Decisão

Usar **PostgreSQL 16** com a extensão **pgvector** como banco de dados primário do backend. A
imagem `pgvector/pgvector:pg16` é usada no Docker Compose para já disponibilizar a extensão sem
etapas manuais de instalação.

Nesta fase (Fase 0 + Fase 1 do plano de migração), apenas o esquema de conexão e a infraestrutura de
acesso ao banco são estabelecidos; os repositórios concretos (`PostgresAgentRepository`,
`PostgresTaskRepository`, etc.) e o schema de memória vetorial serão implementados nas fases
seguintes, mantendo YAGNI — não implementamos persistência para casos de uso que ainda não existem
na aplicação.

## Consequências

### Positivas
- Um único motor de banco serve tanto para dados relacionais quanto para embeddings, reduzindo a
  superfície operacional do projeto (sem um banco vetorial dedicado separado).
- `pgvector` é maduro, open-source e amplamente documentado.

### Negativas / Trade-offs
- Buscas vetoriais em pgvector são menos otimizadas que em bancos vetoriais dedicados para escalas
  muito grandes — aceitável para o escopo de portfólio/demonstração deste projeto.

## Convenção de Nomenclatura do Schema

Todas as tabelas e colunas do banco de dados deste projeto são nomeadas em **inglês**
(`snake_case`), independentemente do idioma usado na documentação (português). Esta regra é
inegociável e vale para qualquer migração/schema criado nas fases seguintes — ver também
[ADR-007](./007-clean-architecture-no-backend.md), que já estabelece inglês para identificadores de
código.

## Alternativas Consideradas

| Alternativa | Por que foi descartada |
|-------------|-------------------------|
| SQLite | Sem suporte nativo a extensões vetoriais maduras e sem boas garantias de concorrência para múltiplos agentes simultâneos. |
| Banco vetorial dedicado (Pinecone, Qdrant, Weaviate) | Adiciona mais uma peça de infraestrutura operacional; desnecessário para o volume de dados deste projeto. |
