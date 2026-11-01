# ADR-057 — Bloquear o raciocínio do LLM em outro idioma no texto final

**Status:** Aceito
**Data:** 2026-11-01
**Autores:** Cristian Bernardes

## Contexto

Modelos "reasoning" (ex.: `gpt-oss`) às vezes escrevem o raciocínio interno — quase sempre em
inglês, mesmo com o sistema instruído a responder em português — diretamente no campo
`content` da resposta do Ollama, em vez de usar o campo `thinking` separado da API. Isso
aparecia no balão de pensamento do escritório e em artefatos `.md` gerados pelos agentes,
mesmo com o escritório em português (ver captura de tela e
`workspace/projects/tasks/bdebb380-...md`).

## Decisão

1. **Prompt mais explícito** (`_LANGUAGE_DIRECTIVE`, pt/en): além de exigir o idioma, proíbe
   comentários sobre como a resposta será escrita, discussão de formato de ferramentas e
   qualquer texto de raciocínio interno antes do conteúdo.
2. **`think: false`** em toda chamada `POST /api/chat` ao Ollama (`OllamaAdapter.think`):
   desliga o canal de raciocínio separado em modelos que o suportam; modelos que não o
   suportam ignoram o parâmetro sem erro.
3. **Guard de defesa** (`domain/services/llm_output_guard.strip_reasoning_preamble`): se,
   mesmo assim, o raciocínio vazar para o texto, localiza a última expressão típica de
   raciocínio ("we need to", "let's", "the instruction says"...) seguida do primeiro marcador
   de conteúdo entregável (cabeçalho, negrito ou cerca de código) e corta ali. Sem essas duas
   evidências, o texto original é devolvido intacto — evita falso positivo sobre texto
   legítimo. Aplicado em `_parse_structured_reply`, então vale para todo caminho (JSON
   estruturado ou texto livre) e todo chamador (pensamento, trabalho, artefatos).

## Consequências

Reduz bastante a chance de o balão de pensamento e os artefatos mostrarem texto em outro
idioma; o guard é heurístico (`regex`), não uma garantia absoluta — texto livre que imite os
dois padrões ao mesmo tempo pode, em tese, ser cortado por engano. Validado com chamadas reais
ao `gpt-oss:20b` (modelo do RH) reproduzindo o cenário relatado: três execuções seguidas sem
vazamento.
