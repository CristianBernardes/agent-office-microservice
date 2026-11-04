# ADR-059 — Modelo Escolhido na Contratação Sobrepõe o Padrão do Papel

**Status:** Aceito
**Data:** 2026-11-04
**Autores:** Cristian Bernardes

## Contexto

O formulário de contratação (`HireForm.svelte`, frontend) permite escolher um modelo de LLM
específico para o agente que está sendo contratado (campo `llm_model`, persistido na entidade
`Agent`). Esse valor era salvo no banco e devolvido pela API (`AgentResponse.llm_model`), mas nunca
efetivamente usado: `AgentThinkUseCase`, `ResearchTopicUseCase` e a memória semântica resolviam o
adaptador de LLM **sempre pelo papel** (`ILlmAdapterResolver.resolve(agent.role)`), lendo apenas o
modelo configurado em `.env` (`AGENT_<PAPEL>_MODEL`, ver ADR-005).

Na prática, isso significava que escolher um modelo diferente ao contratar um agente — por exemplo,
um Claude específico para testar a integração da ADR-058 — era puramente decorativo: o agente
continuava usando o modelo padrão do papel, não o modelo escolhido para ele. Esse comportamento foi
identificado ao tentar usar o modelo Claude listado no frontend para um Product Owner específico, sem
querer alterar `AGENT_PO_MODEL` no `.env` (o que afetaria *todos* os agentes com papel PO, não apenas
aquele contratado).

## Decisão

`ILlmAdapterResolver.resolve()` passa a aceitar um segundo parâmetro opcional, `model: str = ""` — o
modelo específico do agente (`agent.llm_model`). A prioridade de resolução passa a ser:

1. **Modelo do agente** (`agent.llm_model`), se não vazio — a escolha feita na contratação daquele
   agente específico;
2. **Modelo do papel** (`AGENT_<PAPEL>_MODEL` em `.env`), se o agente não tiver modelo próprio
   (compatibilidade com agentes existentes e com o comportamento anterior);
3. **Modelo padrão global** (`OLLAMA_MODEL`), como último fallback.

Essa prioridade é implementada apenas em `RoleBasedLlmAdapterResolver.resolve()` — nenhum caso de uso
precisa saber como a prioridade é resolvida, apenas passar `agent.llm_model` adiante:

- `AgentThinkUseCase.execute()` — chamada principal de raciocínio do agente;
- `ResearchTopicUseCase.execute()` — pesquisa de tema (ADR-034).

**Exceção deliberada — memória semântica:** `RememberUseCase`/`RecallMemoryUseCase`
(`memory_use_cases.py`) continuam resolvendo **apenas pelo papel**, sem passar `agent.llm_model`. A
razão é técnica, não arbitrária: embeddings de provedores diferentes não são comparáveis no mesmo
espaço vetorial, e a Anthropic não oferece uma API de embeddings (ver ADR-058) — se um agente com
modelo Claude tentasse usar a ferramenta de memória, a chamada falharia com `NotImplementedError`.
Mantendo a memória sempre no modelo de embedding do papel (Ollama, por padrão), um agente pode usar
Claude para pensar e, ainda assim, usar memória semântica normalmente.

## Consequências

### Positivas
- A escolha de modelo feita no formulário de contratação (incluindo Claude, ADR-058) passa a ter
  efeito real — cada agente pode ter seu próprio modelo, independentemente do papel.
- Nenhuma mudança de assinatura quebra o comportamento anterior: agentes com `llm_model` vazio (ou
  agentes antigos já persistidos sem essa distinção) continuam caindo no modelo do papel, como antes.
- A camada de aplicação permanece agnóstica ao provedor concreto — apenas repassa uma `string`
  adicional ao resolver, sem qualquer lógica de roteamento de provedor nos casos de uso.

### Negativas / Trade-offs
- Dois agentes com o mesmo papel podem agora ter comportamentos de raciocínio bem diferentes entre si
  (modelos diferentes), o que pode dificultar comparar/depurar decisões "do Tech Lead" de forma
  genérica — aceito, já que essa era justamente a funcionalidade pedida.
- A memória semântica de um agente com modelo Claude continua amarrada ao modelo de embedding do
  papel (Ollama); não há, nesta rodada, uma forma de escolher um provedor de embedding
  independentemente do provedor de raciocínio.

## Alternativas Consideradas

| Alternativa | Por que foi descartada |
|-------------|-------------------------|
| Deixar como está (modelo da contratação é só informativo) | Contraria a expectativa direta do dono do produto ao escolher um modelo no formulário; o campo existiria sem função real. |
| Propagar `agent.llm_model` também para `embed()` | Quebraria a memória semântica de qualquer agente com um provedor sem API de embeddings (ex.: Anthropic), sem tratamento de erro no caminho de chamada (`client_dialogue_use_case` não captura exceções do `remember`). |
| Nova interface `IPerAgentLlmAdapterResolver` separada | Duplicaria o contrato existente sem necessidade; um parâmetro opcional com fallback é suficiente e não quebra nenhum consumidor existente. |
