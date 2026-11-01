"""Testes do guard que remove o raciocínio vazado do LLM antes do texto final (ADR-057)."""

from __future__ import annotations

import pytest

from src.domain.services.llm_output_guard import strip_reasoning_preamble

pytestmark = pytest.mark.unit


class TestStripReasoningPreamble:
    def test_strips_english_reasoning_before_a_bold_header_in_portuguese(self) -> None:
        text = (
            "We need to produce a markdown with a short draft of the results. We also need "
            "to use the tool hire_agent. The format for tool usage is like:\n\n```\n"
            'hire_agent: {\n  role: "..."\n}\n```\n\n'
            "But the instruction says: hire_agent: Contratar novos membros quando necessário. "
            "Likely we just call with the role. We'll include it as a separate block.\n\n"
            "We can produce multiple calls. We'll produce 3 calls. Then we produce the "
            "markdown.**Resultado do Trabalho de Recrutamento**\n\n| Tarefa | Competência |\n"
        )

        result = strip_reasoning_preamble(text)

        assert result.startswith("**Resultado do Trabalho de Recrutamento**")
        assert "We need to" not in result

    def test_keeps_legitimate_text_with_a_bold_header_and_no_reasoning_markers(self) -> None:
        text = "Aqui está o resumo do trabalho. **Resultado:** tudo certo, entregamos o MVP."
        assert strip_reasoning_preamble(text) == text

    def test_keeps_text_that_already_starts_with_the_deliverable(self) -> None:
        text = "**Rascunho de Postagem – Vaga de DBA**\n\n```markdown\n# Vaga\n```"
        assert strip_reasoning_preamble(text) == text

    def test_keeps_portuguese_text_with_a_bold_header_mid_sentence(self) -> None:
        text = "Precisamos entregar isto rápido. **Plano:** fazer tudo certo amanhã."
        assert strip_reasoning_preamble(text) == text

    def test_keeps_short_english_text_without_a_deliverable_marker_after_it(self) -> None:
        text = "We need alignment on scope before the sprint starts, said no one ever."
        assert strip_reasoning_preamble(text) == text

    def test_strips_before_a_markdown_heading(self) -> None:
        text = "Let's think about this. First, we should plan.\n# Plano Final\nConteúdo aqui."
        result = strip_reasoning_preamble(text)
        assert result.startswith("# Plano Final")

    def test_strips_before_a_code_fence(self) -> None:
        text = "We'll write the code now.\n```python\nprint('ok')\n```"
        result = strip_reasoning_preamble(text)
        assert result.startswith("```python")

    def test_empty_and_whitespace_only_text_is_returned_stripped(self) -> None:
        assert strip_reasoning_preamble("   ") == ""
        assert strip_reasoning_preamble("") == ""

    def test_does_not_strip_when_the_remaining_content_would_be_too_short(self) -> None:
        text = "We need to answer. **x**"
        assert strip_reasoning_preamble(text) == text
