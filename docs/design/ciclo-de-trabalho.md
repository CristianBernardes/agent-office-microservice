# Design Doc — Ciclo de trabalho e qualidade de código

## Componentes

- `WorkLoopUseCase` (application): orquestra `_review`, `_work`, `_assign_todo`, `_plan`.
  Colaboradores injetados no construtor (Inversão de Dependência); sem acesso direto a infra.
- `task_splitter` (domain/services): funções puras de divisão de tarefas, testadas isoladamente.
- `task_workflow` (domain/policies): matriz cargo × estágio.
- `MoveTaskUseCase` / `AssignTaskUseCase`: regras de movimentação e dono obrigatório.

## Fluxo do cartão

`todo → in_progress → testing → in_review → done` (ADR-050). Na etapa `testing` o QA/tester valida a
entrega antes da revisão; reprovado, o cartão volta para `in_progress`. A migração
`2026_10_31_000010_add_testing_task_status` amplia o domínio `task_status` (constraint `task_status_check`,
validada em Postgres real).

## Responsabilidades por cargo (ADR-054)

| Cargo | Papel no fluxo |
|---|---|
| Product Owner | Conduz o planejamento, leva a proposta ao cliente (ADR-055), pode aprovar a entrega |
| Scrum Master | Planeja e coordena (atribui e bloqueia cartões) |
| Tech Lead | Executa tarefas de arquitetura/infra, coordena e revisa |
| Dev Sênior / Júnior | Executam implementação (reserva para tarefas sem área definida) |
| Analista de Dados | Executa tarefas de dados, SQL, métricas e estatística |
| RH | Executa contratação/cultura; propõe demissões ao dono (ADR-056) |
| Consultor de Produto | Executa pesquisa de mercado, concorrência e preço |
| QA | Testa (`testing`) e revisa (`in_review`) |

O dono do produto (usuário) pode mover qualquer cartão (`owner_override`), reatribuir, repriorizar e
demitir; as ações são registradas em nome do PO.

## Princípios aplicados

| Princípio | Onde |
|---|---|
| SOLID (SRP/DIP) | Casos de uso pequenos; divisão extraída para o domínio; interfaces `I*Repository` |
| DRY | Helper `_speak` único para dispatch + mensagem; prompts centralizados em `_PROMPTS` |
| YAGNI | Sem parâmetros/abstrações além do necessário; limites WIP configuráveis só onde pedido |
| Design Patterns | Repository, Use Case, Strategy (prompts por idioma), Policy, Observer (MQTT) |
| Testes | Unit (`pytest -m unit`), integração (`-m integration`, Postgres/MQTT/Kafka), e2e, Vitest, Go test |
| Documentação | ADRs (`docs/adr`), RFCs (`docs/rfc`), Design Docs (`docs/design`) |
