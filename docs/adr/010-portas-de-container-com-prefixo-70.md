# ADR-010 — Convenção de Portas de Container com Prefixo `70`

**Status:** Aceito
**Data:** 2026-10-30
**Autores:** Cristian Bernardes

## Contexto

O serviço MQTT deste projeto já expõe suas portas externas com o prefixo `70` (`7083` para MQTT TCP,
`7000` para MQTT sobre WebSocket). Para manter previsibilidade e evitar colisão com outras aplicações
comuns no ambiente de desenvolvimento do mantenedor (ex.: PostgreSQL em `5432`/`5434`, APIs genéricas
em `3000`/`8000`), todas as portas **externas** (host) de containers deste projeto devem seguir a
mesma convenção.

## Decisão

Toda porta exposta no host pelo `docker-compose.yml` deste projeto deve iniciar com o prefixo `70`.

| Serviço | Porta interna | Porta externa (host) |
|---------|---------------|------------------------|
| Mosquitto (MQTT TCP) | `1883` | `7083` |
| Mosquitto (MQTT WebSocket) | `3000` | `7000` |
| PostgreSQL | `5432` | `7034` |
| Backend (FastAPI/HTTP) | `8000` | `7001` |

Esta convenção se aplica apenas às portas publicadas no **host**. As portas internas dentro da rede
Docker (usadas na comunicação `serviço-a → serviço-b`) seguem o padrão convencional de cada
tecnologia (ex.: `5432` para Postgres, `1883` para MQTT), já que não há colisão possível dentro da
rede isolada do Compose.

## Consequências

### Positivas
- Previsibilidade: qualquer pessoa clonando o repositório sabe, de antemão, qual faixa de porta este
  projeto usa no host, reduzindo risco de colisão com outros serviços locais.
- Facilita identificar rapidamente, em `docker ps` ou em um inspetor de rede, que uma porta pertence
  a este projeto.

### Negativas / Trade-offs
- Exige lembrar de mapear a porta ao adicionar um novo serviço — mitigado documentando a tabela
  acima e revisando-a a cada novo serviço adicionado ao Compose.

## Alternativas Consideradas

| Alternativa | Por que foi descartada |
|-------------|-------------------------|
| Usar as portas padrão de cada tecnologia também no host | Risco real de colisão com instâncias locais de Postgres/APIs já em uso no ambiente de desenvolvimento do mantenedor; decisão explícita do dono do produto em sentido contrário. |
