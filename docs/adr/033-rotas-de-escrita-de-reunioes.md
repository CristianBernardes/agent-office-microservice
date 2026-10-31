# ADR-033 — Rotas de escrita de reuniões

**Status:** Aceito

## Contexto
Reuniões só tinham leitura (ADR-029). O frontend precisa iniciar cerimônias (daily, retro…) e encerrá-las.

## Decisão
- `POST /meetings` inicia uma cerimônia (`StartCeremonyUseCase`); o organizador sempre participa.
- `POST /meetings/{id}/finish` encerra com resumo e decisões (`FinishMeetingUseCase`).
- Erros localizados: `meeting.not_found` → 404; `meeting.cannot_finish` → 409; demais → 422.
- Camada fina: sem regra de negócio no router.

## Consequências
O ciclo de vida completo da reunião é acionável via HTTP; não há ainda geração automática de ata por LLM nessas rotas.
