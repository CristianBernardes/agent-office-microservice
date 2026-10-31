# ADR-037 — Ferramenta `research` para agentes

**Status:** Aceito

## Contexto
A pesquisa que gera `.md` (ADR-034) só era acessível por HTTP. Agentes no loop autônomo não podiam acioná-la.

## Decisão
Novo `ToolName.RESEARCH`, concedido aos mesmos papéis que já têm `web_search`. O handler no `ToolRegistry` delega a `ResearchTopicUseCase`, usando o agente solicitante como pesquisador. O handler é opcional no construtor (como `hire_agent`).

## Consequências
Agentes podem pesquisar e registrar o resultado como artefato. Papéis sem busca web (QA, SM, HR) continuam sem acesso.
