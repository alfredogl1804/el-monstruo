"""DAN T1 S5_KERNEL_FIX — Anti-drift tests for get_tool_aware_prompt_suffix().

Repro context (2026-05-27 11:29 — iPhone E2E S5 V2):
  The LLM narrated "**Herramienta:** github" + "list_prs" in prose without
  emitting a TOOL_CALL_START event. Root cause confirmed by Cowork audit:
    1. ToolSpec "github" (legacy) coexisted in get_tool_specs() with the
       new "github_ops" (P0.4). The LLM had two valid bindings for the
       same backend, one without HITL gate.
    2. The "## Cuando Usar Cada Herramienta" block in tool_dispatch.py
       was hardcoded with legacy names and legacy actions
       (list_repos, search_code, ...) even after P0.4 renamed to
       github_ops with different actions (list_prs, create_pull_request, ...).
       The LLM trusted the prompt over the function-calling schema and
       narrated the legacy names verbatim.

T1 fix:
  - Remove ToolSpec "github" legacy from get_tool_specs().
  - Add ToolSpec.trigger_hint field (default "").
  - Generate the "## Cuando Usar Cada Herramienta" block DYNAMICALLY by
    iterating get_tool_specs() and rendering trigger_hint + action enum
    for each spec with a non-empty trigger_hint.

These tests are the structural anti-drift gate: if anyone hardcodes a tool
name or action enum in the prompt again, they fail.
"""

from __future__ import annotations

import pytest

from kernel.tool_dispatch import get_tool_aware_prompt_suffix, get_tool_specs


@pytest.fixture(scope="module")
def prompt_suffix() -> str:
    """Render the prompt once per module — cheap and deterministic."""
    return get_tool_aware_prompt_suffix()


@pytest.fixture(scope="module")
def specs():
    return get_tool_specs()


class TestNoLegacyGithub:
    """The legacy `github` ToolSpec must not leak back into the registry
    or the prompt — that was the S5 root cause."""

    def test_no_legacy_github_in_specs(self, specs):
        names = [s.name for s in specs]
        assert "github" not in names, (
            "Legacy ToolSpec 'github' is back in get_tool_specs(). "
            "This is the S5 root cause — REMOVE it. Use 'github_ops' only."
        )

    def test_github_ops_in_specs(self, specs):
        names = [s.name for s in specs]
        assert "github_ops" in names, (
            "ToolSpec 'github_ops' (P0.4) is missing from the registry. "
            "This breaks S5 HITL gate."
        )

    def test_no_legacy_github_in_prompt(self, prompt_suffix: str):
        # The prompt must NOT advertise the legacy name to the LLM.
        # Use a strict word-boundary regex to avoid matching 'github_ops' or 'github.com'.
        import re

        legacy_pattern = re.compile(r"\*\*github\*\*\s*:")
        assert not legacy_pattern.search(prompt_suffix), (
            "The prompt still contains '**github**:' (legacy hardcoded reference). "
            "This is the S5 drift bug — generate the block from get_tool_specs() instead."
        )

    def test_no_legacy_actions_in_prompt(self, prompt_suffix: str):
        # The legacy enum was: list_repos, get_repo, list_issues, create_issue,
        # list_commits, get_file, search_code. The real enum for github_ops is:
        # search_repos, search_code, get_file, list_issues, list_prs,
        # create_branch, create_or_update_file, create_pull_request, create_issue, update_issue.
        # `list_repos` and `list_commits` were in the legacy hardcoded block but NEVER
        # in github_ops — if they appear in the prompt, the legacy hardcode is back.
        assert "list_repos" not in prompt_suffix, (
            "Legacy action 'list_repos' is in the prompt. Hardcoded block is back."
        )
        assert "list_commits" not in prompt_suffix, (
            "Legacy action 'list_commits' is in the prompt. Hardcoded block is back."
        )


class TestDynamicTriggerBlock:
    """The 'Cuando Usar Cada Herramienta' block must be generated dynamically."""

    def test_section_header_present(self, prompt_suffix: str):
        assert "## Cuándo Usar Cada Herramienta" in prompt_suffix

    def test_github_ops_appears_with_action_enum(self, prompt_suffix: str):
        # github_ops trigger_hint is set, and its action property has an enum.
        # The dynamic renderer must include 'Acciones: list_prs, ...' suffix.
        assert "**github_ops**" in prompt_suffix, (
            "github_ops missing from the dynamic trigger block — trigger_hint is empty?"
        )
        assert "list_prs" in prompt_suffix, (
            "github_ops trigger block missing 'list_prs' action — enum not rendered."
        )
        assert "create_pull_request" in prompt_suffix, (
            "github_ops trigger block missing 'create_pull_request' action — enum not rendered."
        )

    def test_web_search_appears(self, prompt_suffix: str):
        assert "**web_search**" in prompt_suffix

    def test_skill_read_appears(self, prompt_suffix: str):
        # skill_read is the new P0.4 tool — should appear in trigger block.
        assert "**skill_read**" in prompt_suffix, (
            "skill_read missing from the dynamic trigger block. "
            "Did you forget its trigger_hint?"
        )

    def test_critical_rule_after_block(self, prompt_suffix: str):
        # The critical rule that closes the block must still be present.
        assert "REGLA CRÍTICA" in prompt_suffix
        assert "NO describas lo que harías" in prompt_suffix


class TestAntiDriftStructural:
    """Property-based check: every tool with a trigger_hint in get_tool_specs()
    MUST appear in the prompt's trigger block. If you add a tool with a hint,
    it shows up. If you remove one, it disappears. No manual sync."""

    def test_every_hinted_tool_renders(self, specs, prompt_suffix: str):
        missing: list[str] = []
        for spec in specs:
            if not spec.trigger_hint:
                continue
            marker = f"**{spec.name}**:"
            if marker not in prompt_suffix:
                missing.append(spec.name)
        assert not missing, (
            f"These specs have trigger_hint set but do not appear in the prompt: {missing}. "
            "The dynamic renderer is broken."
        )

    def test_no_unhinted_tool_renders(self, specs, prompt_suffix: str):
        # The inverse: a tool WITHOUT trigger_hint must NOT appear in the
        # trigger block (it can still appear in '## Herramientas Disponibles'
        # earlier, which is a different section).
        # Find the start of the trigger block to scope the check.
        anchor = "## Cuándo Usar Cada Herramienta"
        idx = prompt_suffix.find(anchor)
        assert idx >= 0, "Trigger block header missing"
        block = prompt_suffix[idx:]
        leaks: list[str] = []
        for spec in specs:
            if spec.trigger_hint:
                continue
            marker = f"**{spec.name}**:"
            if marker in block:
                leaks.append(spec.name)
        assert not leaks, (
            f"These specs have NO trigger_hint but appear in the trigger block: {leaks}. "
            "Either the renderer is leaking or hardcoded entries are back."
        )
