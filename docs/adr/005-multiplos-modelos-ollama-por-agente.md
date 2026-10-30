# ADR-005 — Múltiplos Modelos de LLM por Agente

**Status:** Aceito
**Data:** 2026-10-30
**Autores:** Cristian Bernardes

## Contexto

Diferentes papéis exigem diferentes perfis de modelo (custo, latência, qualidade de raciocínio). Fixar
um único modelo de LLM para todos os agentes limitaria a flexibilidade do sistema e o tornaria mais
caro ou mais lento do que o necessário para tarefas simples.

## Decisão

Cada papel de agente tem seu modelo de LLM configurado de forma independente via variável de
ambiente (`.env`), lido por uma *factory* de infraestrutura (`LlmAdapterFactory`) que resolve o
adaptador correto a partir de uma interface única (`ILlmAdapter`), sem que a camada de aplicação
precise saber qual provedor está sendo usado.

Dois provedores são suportados nesta fase:
- **Ollama** (local, via HTTP) — provedor padrão, pensado para rodar no host do desenvolvedor.
- **Qualquer API compatível com o formato OpenAI** (OpenAI, OpenRouter, Gaia, LM Studio, etc.) —
  ativado automaticamente quando `OPENAI_API_KEY` está definida no ambiente.

**Importante:** o Ollama é sempre acessado como um serviço **externo** ao Docker Compose deste
projeto (ver [ADR-009](./009-ollama-externo-ao-docker-compose.md)) — o backend nunca sobe um
container de Ollama.

## Consequências

### Positivas
- Troca de modelo por papel é uma mudança de configuração, não de código (princípio Open/Closed).
- `MockLlmAdapter` permite testar toda a cadeia de aplicação sem qualquer chamada de rede real.

### Negativas / Trade-offs
- Mais uma variável de configuração por papel — mitigado com um `.env.example` completo e
  documentado, e com valores padrão sensatos no código quando a variável específica não está
  definida.

## Alternativas Consideradas

| Alternativa | Por que foi descartada |
|-------------|-------------------------|
| Um único modelo global para todos os agentes | Reduz flexibilidade de custo/qualidade por papel e contraria o objetivo de portfólio de demonstrar injeção de dependência real. |
| Modelo fixo no código (hardcoded) | Viola a premissa inegociável do projeto de que toda configuração deve vir de `.env`, sem hardcode. |
