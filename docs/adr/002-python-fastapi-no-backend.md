# ADR-002 — Python 3.12 + FastAPI no Backend

**Status:** Aceito
**Data:** 2026-10-30
**Autores:** Cristian Bernardes

## Contexto

O backend precisa orquestrar agentes de IA (LLMs), persistir estado e metadados, e expor uma API
HTTP para o frontend e para integrações externas. O ecossistema escolhido precisa ter suporte maduro
a:
- Clientes assíncronos para LLMs (Ollama, OpenAI-compatible);
- Clientes MQTT assíncronos;
- Acesso a banco de dados relacional com extensão vetorial (pgvector);
- Testes automatizados (unitários, integração) com boa curva de produtividade.

## Decisão

Usar **Python 3.12** com **FastAPI** para a camada de apresentação (API HTTP), com suporte nativo a
`async`/`await` em toda a cadeia de execução relevante (I/O de rede, banco, MQTT, LLM).

## Consequências

### Positivas
- Ecossistema de IA maduro: `ollama` (HTTP), `httpx`, `openai` (compatível com múltiplos provedores).
- FastAPI tem suporte nativo a validação de schema via Pydantic v2 e documentação OpenAPI automática.
- `pytest` + `pytest-asyncio` oferecem uma base de testes madura e amplamente documentada.
- Tipagem estática com `mypy` reduz a classe de erros de contrato entre camadas.

### Negativas / Trade-offs
- O GIL do CPython pode limitar paralelismo de CPU-bound; mitigado porque o backend é
  predominantemente I/O-bound (chamadas de rede para LLM, banco e MQTT).
- Requer disciplina para não "vazar" FastAPI (decorators, `Depends`, modelos Pydantic) para dentro das
  camadas de domínio e aplicação — ver [ADR-007](./007-clean-architecture-no-backend.md).

## Alternativas Consideradas

| Alternativa | Por que foi descartada |
|-------------|-------------------------|
| Manter a stack original (Node.js/TypeScript) | Ecossistema de IA/LLM e de computação vetorial inferior ao do Python para os objetivos do projeto. |
| Go para o backend de agentes | Performance superior, mas ecossistema de orquestração de LLM/RAG muito mais imaturo. Go é reservado para o gateway de alta performance na Fase 8. |
| Django / Django REST Framework | Overhead de ORM e convenções síncronas por padrão; FastAPI tem adoção async nativa e menor acoplamento com o framework. |
