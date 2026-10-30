# ADR-003 — Modelo de Agentes por Papel

**Status:** Aceito
**Data:** 2026-10-30
**Autores:** Cristian Bernardes

## Contexto

O AgentOffice simula um time de TI completo. É necessário um modelo de domínio que represente um
agente de forma extensível, sem acoplar a lógica de "o que o agente pode fazer" a um conjunto fixo e
hardcoded de comportamentos.

## Decisão

Cada agente é modelado pela entidade `Agent`, cujo comportamento observável é determinado por um
`Role` (papel). O papel determina, em camadas superiores (não no domínio):
- O *system prompt* usado para orientar o LLM;
- As ferramentas (`tools`) disponíveis para aquele papel;
- Os tipos de artefato que o agente pode produzir;
- O modelo de LLM configurado via variável de ambiente (ver [ADR-005](./005-multiplos-modelos-ollama-por-agente.md)).

A entidade `Agent` em si permanece agnóstica a esses detalhes de infraestrutura — ela apenas expõe
seu papel, seu estado (`AgentStatus`) e sua personalidade (`Personality`), conforme o
[Design Doc — Modelo de Domínio](../design/modelo-de-dominio.md).

### Papéis desta fase

Nesta primeira fase de implementação (Fase 0 + Fase 1 do plano de migração), apenas o **enum** de
papéis e a estrutura de domínio são implementados. A definição detalhada de prompts e ferramentas por
papel (Fase 3 do plano) é tratada em uma rodada de implementação futura, mantendo o princípio YAGNI —
não antecipamos infraestrutura que ainda não é consumida.

| Role | Responsabilidade principal |
|------|------------------------------|
| `PRODUCT_OWNER` | Backlog, user stories, priorização |
| `SCRUM_MASTER` | Cerimônias, impedimentos, retrospectivas |
| `TECH_LEAD` | Arquitetura, ADRs, decisões técnicas |
| `DEV_SENIOR` | Implementação, code review, mentoria |
| `DEV_JUNIOR` | Tarefas simples, aprendizado |
| `QA_ENGINEER` | Planos de teste, bug reports |
| `DATA_ANALYST` | Métricas, KPIs, análises |
| `HR_MANAGER` | Onboarding, cultura, contratações |
| `PRODUCT_CONSULTANT` | Validação de mercado, pesquisa |

## Consequências

### Positivas
- Novos papéis podem ser adicionados sem alterar a entidade `Agent` (princípio Open/Closed).
- A entidade de domínio permanece pura — testável sem qualquer infraestrutura externa.

### Negativas / Trade-offs
- A lógica de "qual prompt/ferramenta usar para qual papel" fica em uma camada de infraestrutura
  (factory/registry), que precisa ser mantida sincronizada com o enum `Role` — mitigado com testes
  unitários que garantem cobertura de todos os papéis.

## Alternativas Consideradas

| Alternativa | Por que foi descartada |
|-------------|-------------------------|
| Subclasses de `Agent` por papel (`ProductOwnerAgent`, `TechLeadAgent`, ...) | Viola Liskov/Open-Closed ao exigir uma nova classe de domínio para cada papel; a composição via `Role` + registries de infraestrutura é mais flexível e testável. |
| Papel como `string` livre | Perde segurança de tipos e validação em tempo de desenvolvimento; `Enum` garante um conjunto fechado e auditável de papéis válidos. |
