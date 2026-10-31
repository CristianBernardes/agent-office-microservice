# ADR-036 — Leitura tolerante da resposta do Ollama

**Status:** Aceito

## Contexto
`OllamaAdapter.think` exigia JSON puro; modelos locais respondem com texto livre ou JSON dentro de blocos de código, o que derrubava o agente com `JSONDecodeError`.

## Decisão
`_parse_structured_reply` tenta JSON direto, depois o primeiro objeto `{...}` do texto e, por fim, usa o texto inteiro como `thought` com `action="idle"`.

## Consequências
Agentes não falham por formatação. O `raw_response` continua guardando a resposta original.
