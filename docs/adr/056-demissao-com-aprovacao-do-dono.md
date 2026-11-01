# ADR-056 — Demissão proposta pelo RH com aprovação do dono

**Status:** Aceito
**Data:** 2026-11-01
**Autores:** Cristian Bernardes

## Contexto

O RH deve poder sugerir demissões com motivos plausíveis, mas a decisão é do dono do produto.

## Decisão

- Entidade `DismissalProposal` (pendente/aprovada/rejeitada) e tabela `dismissal_proposals`
  (migração `2026_11_01_000011`), com repositórios em memória e PostgreSQL.
- Ferramenta `propose_dismissal` (`agent_id`, `reason`), exclusiva do RH. O caso de uso exige motivo,
  recusa autoproposta, agente já offline e proposta pendente duplicada. Propor **nunca** demite.
- `GET /dismissals?pending_only=`, `POST /dismissals`, `POST /dismissals/{id}/approve|reject`.
  Aprovar usa `FireAgentUseCase` (offline, devolve o trabalho ao fluxo, publica o status); rejeitar
  mantém o agente. Decidir duas vezes dá 409. Eventos `office/dismissals/proposed|decided`.
- O frontend consulta as pendentes a cada atualização e mostra o `DismissalModal` (pt/en) com o
  motivo do RH; ele não fecha no fundo nem no Esc: exige "Aprovar demissão" ou "Manter no time".

## Consequências

O usuário continua podendo demitir diretamente (botão "Demitir"). A descoberta é por polling do
frontend, sem tempo real dedicado.
