# ADR-026: Handler da ferramenta `hire_agent`

- Status: Aceito

## Contexto
`HIRE_AGENT` constava em `ToolName` e nas permissões (HR, PO, tech lead), mas lançava
`ToolNotImplementedError`.

## Decisão
`ToolRegistry` recebe opcionalmente `HireAgentUseCase` e o modelo padrão. O handler cria o agente
(`name`, `role`, `llm_model` opcional) com personalidade neutra. A checagem de papel continua
centralizada no registry. `START_CEREMONY` segue sem handler até existir o domínio de reuniões.

## Consequências
Sem o caso de uso injetado, o comportamento anterior (não implementado) é mantido.
