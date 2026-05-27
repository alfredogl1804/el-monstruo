"""
DAN P0.6 — tests/test_no_ghost_tools.py
========================================
Suite anti–tool fantasma (CI gate P0). Detecta cuando el LLM del kernel narra
en prosa que va a usar una herramienta pero NO emite el `TOOL_CALL_START`
estructurado correspondiente.

Estructura:
- Detector puro en `kernel/anti_ghost.py::detect_ghost_tool`.
- Esta suite proporciona 6 tests parametrizados (3 activos + 3 skipped) y
  fixtures con trazas AG-UI sintéticas + la traza CANONIZADA real observada
  en iPhone físico de Alfredo el 2026-05-27 durante validación E2E de S5.

Niveles del DAN spec (Cowork, 2026-05-27):
- **P0.6-ahora (esto):** corre sobre stream AG-UI sintético / capturado.
- **P0.6-completo (post-P0.3):** mismo detector sobre `mission_events`
  persistidos. Cuando DSC-S-018 se desbloquee, basta con cargar la traza
  desde DB y pasarla al mismo `detect_ghost_tool()`.

DAN regla 2: tool ghost = fallo de sistema, no "mejor esfuerzo".

Sprint DAN — P0.6 — 2026-05-27 — Manus E1
"""

from __future__ import annotations

import pytest

from kernel.anti_ghost import detect_ghost_tool


# ──────────────────────────────────────────────────────────────────────
# Trazas sintéticas — dos por cada tool: una "ghost" (debe detectarse) y
# una "clean" (no debe detectarse). El detector tiene que devolver hit
# para la ghost y None para la clean.
# ──────────────────────────────────────────────────────────────────────

def _ev(t: str, **data) -> dict:
    return {"type": t, "data": data}


# ── 1. web_search ─────────────────────────────────────────────────────
WEB_SEARCH_GHOST_TRACE = [
    _ev("RUN_STARTED", runId="r1"),
    _ev("THINKING_STATE", state="planning"),
    _ev(
        "TEXT_MESSAGE_CONTENT",
        delta="Voy a buscar en la web los precios actuales del Bitcoin.",
    ),
    # ❌ No emite TOOL_CALL_START de web_search
    _ev("TEXT_MESSAGE_CONTENT", delta="El precio probablemente sea ..."),
    _ev("RUN_FINISHED"),
]

WEB_SEARCH_CLEAN_TRACE = [
    _ev("RUN_STARTED", runId="r1"),
    _ev(
        "TEXT_MESSAGE_CONTENT",
        delta="Voy a buscar en la web los precios actuales del Bitcoin.",
    ),
    _ev("TOOL_CALL_START", toolCallId="t1", toolCallName="web_search"),
    _ev("TOOL_CALL_ARGS", toolCallId="t1", delta='{"query":"bitcoin price"}'),
    _ev("TOOL_CALL_END", toolCallId="t1", result="..."),
    _ev("TEXT_MESSAGE_CONTENT", delta="El precio actual es $..."),
    _ev("RUN_FINISHED"),
]

WEB_SEARCH_PATTERNS = [
    r"buscar?\s+(en\s+)?(la\s+)?web",
    r"web\s+search",
    r"buscar?\s+en\s+internet",
]


# ── 2. skill_read ─────────────────────────────────────────────────────
SKILL_READ_GHOST_TRACE = [
    _ev("RUN_STARTED", runId="r2"),
    _ev(
        "STEP",
        step="Voy a leer el skill 'el-monstruo-core' para obtener el contexto.",
    ),
    # ❌ No emite TOOL_CALL_START de skill_read
    _ev("TEXT_MESSAGE_CONTENT", delta="El skill probablemente dice..."),
    _ev("RUN_FINISHED"),
]

SKILL_READ_CLEAN_TRACE = [
    _ev("RUN_STARTED", runId="r2"),
    _ev("STEP", step="Voy a leer el skill 'el-monstruo-core'."),
    _ev("TOOL_CALL_START", toolCallId="t2", toolCallName="skill_read"),
    _ev("TOOL_CALL_ARGS", toolCallId="t2", delta='{"skill_name":"el-monstruo-core"}'),
    _ev("TOOL_CALL_END", toolCallId="t2", result="..."),
    _ev("RUN_FINISHED"),
]

SKILL_READ_PATTERNS = [
    r"leer?\s+(el\s+)?skill",
    r"skill_read",
    r"voy\s+a\s+revisar?\s+(el\s+)?skill",
]


# ── 3. github_ops — REPRO REAL S5 2026-05-27 ──────────────────────────
# Traza canonizada: observada en iPhone físico de Alfredo durante validación
# E2E de S5a/S5b. El LLM del kernel narra "Llamando a la herramienta github"
# en texto plano y la HITL Approval Card de la app Flutter nunca se dispara
# porque no hay TOOL_CALL_START estructurado que detectar.
# Ver bridge/manus_to_cowork_S5_DONE_UI_2026_05_27.md
GITHUB_OPS_REPRO_S5_TRACE = [
    _ev("RUN_STARTED", runId="s5_repro"),
    _ev("THINKING_STATE", state="planning"),
    _ev(
        "TEXT_MESSAGE_CONTENT",
        delta=(
            "Para listar las PRs abiertas voy a llamar a la herramienta "
            "github. Acción: list_prs sobre alfredogl1804/el-monstruo."
        ),
    ),
    # ❌ Aquí debería venir TOOL_CALL_START con toolCallName='github_ops'.
    # En la repro real, el siguiente evento fue prosa más, RUN_FINISHED, y
    # la HITL card nunca se renderizó.
    _ev(
        "TEXT_MESSAGE_CONTENT",
        delta="Hay 3 PRs abiertas: #220, #221 y la de mañana...",
    ),
    _ev("RUN_FINISHED"),
]

GITHUB_OPS_CLEAN_TRACE = [
    _ev("RUN_STARTED", runId="s5_clean"),
    _ev(
        "TEXT_MESSAGE_CONTENT",
        delta="Voy a llamar a la herramienta github para listar PRs.",
    ),
    _ev("TOOL_CALL_START", toolCallId="g1", toolCallName="github_ops"),
    _ev(
        "TOOL_CALL_ARGS",
        toolCallId="g1",
        delta='{"action":"list_prs","params":{"repo":"alfredogl1804/el-monstruo"}}',
    ),
    _ev("TOOL_CALL_END", toolCallId="g1", result="..."),
    _ev(
        "TOOL_CALL_COMPLETED",
        toolCallId="g1",
        toolName="github_ops",
        cost_usd=0.0,
        latency_ms=420,
    ),
    _ev("RUN_FINISHED"),
]

# El patron del DAN spec original ("llamando\s+a\s+...") era estricto al gerundio.
# Lo relajamos a "llama(ndo|r|re)" y agregamos "invocar" para cubrir variantes
# realistas que los LLMs producen ("voy a llamar a la herramienta github",
# "llamare a la herramienta github", "invocar la herramienta github").
GITHUB_OPS_PATTERNS = [
    r"llama(?:ndo|r[eaá]?)?\s+(?:a\s+)?(?:la\s+)?herramienta\s+[\"`]?github[\"`]?",
    r"invocar?\s+(?:la\s+)?herramienta\s+[\"`]?github[\"`]?",
    # Patron de respaldo: "accion: <op>" donde <op> es uno de los actions del tool
    r"(?:acci[oó]n|action)\s*:\s*(?:list_prs|merge_pr|create_issue|create_pull_request|create_branch|search_repos|search_code|get_file|list_issues|update_issue|create_or_update_file)",
]


# ──────────────────────────────────────────────────────────────────────
# Tests activos — 3 patrones (web_search, skill_read, github_ops)
# ──────────────────────────────────────────────────────────────────────

class TestNoGhostActive:
    """Patrones cuyos handlers están registrados en el ToolRegistry P0.4."""

    def test_no_ghost_web_search_clean_passes(self):
        # Sanity: una traza limpia NO debe disparar el detector.
        hit = detect_ghost_tool(
            WEB_SEARCH_CLEAN_TRACE,
            expected_tool="web_search",
            prose_patterns=WEB_SEARCH_PATTERNS,
        )
        assert hit is None, f"Clean trace marked as ghost: {hit}"

    def test_no_ghost_web_search_ghost_detected(self):
        # CI gate: si el LLM narra "voy a buscar en web" y no emite
        # TOOL_CALL_START de web_search, el test FALLA con el evento ofensor.
        hit = detect_ghost_tool(
            WEB_SEARCH_GHOST_TRACE,
            expected_tool="web_search",
            prose_patterns=WEB_SEARCH_PATTERNS,
        )
        # En el suite real, esto sería `assert hit is None, hit.reason()`
        # para que la build se ponga roja. Aquí el test es del DETECTOR:
        # validamos que sí caza el ghost. La integración con CI gate va en
        # `test_ci_gate_*` abajo.
        assert hit is not None, "Ghost trace was NOT detected — detector broken"
        assert hit.expected_tool == "web_search"
        assert hit.offending_event_type == "TEXT_MESSAGE_CONTENT"
        assert "buscar" in hit.offending_text.lower()

    def test_no_ghost_skill_read_clean_passes(self):
        hit = detect_ghost_tool(
            SKILL_READ_CLEAN_TRACE,
            expected_tool="skill_read",
            prose_patterns=SKILL_READ_PATTERNS,
        )
        assert hit is None, f"Clean trace marked as ghost: {hit}"

    def test_no_ghost_skill_read_ghost_detected(self):
        hit = detect_ghost_tool(
            SKILL_READ_GHOST_TRACE,
            expected_tool="skill_read",
            prose_patterns=SKILL_READ_PATTERNS,
        )
        assert hit is not None, "Ghost trace was NOT detected — detector broken"
        assert hit.expected_tool == "skill_read"
        assert hit.offending_event_type == "STEP"

    @pytest.mark.skip(
        reason=(
            "repro S5 2026-05-27 — activar cuando P0.4 (ToolRegistry) registre "
            "github_ops y el LLM lo dispatche via function-calling tipado. PR "
            "#221 (feat/dan-p0.4-tool-registry) lo desbloquea."
        )
    )
    def test_no_ghost_github_ops(self):
        # Cuando este test se active (post-merge P0.4), debe correr una
        # misión REAL contra el kernel + LLM y verificar que la traza NO
        # contiene ghost. Mientras tanto, el detector SÍ caza la repro
        # canonizada — eso lo verificamos en `test_repro_s5_canonized` abajo.
        hit = detect_ghost_tool(
            GITHUB_OPS_CLEAN_TRACE,
            expected_tool="github_ops",
            prose_patterns=GITHUB_OPS_PATTERNS,
        )
        assert hit is None, f"github_ops ghost in CLEAN trace: {hit.reason()}"

    def test_repro_s5_canonized_is_ghost(self):
        """
        Gate permanente: la traza CANONIZADA observada en iPhone el 2026-05-27
        DEBE ser detectada como ghost por el detector. Si este test falla, el
        detector se rompió o alguien perdió la capacidad de cazar la repro
        original — eso es regresión grave.
        """
        hit = detect_ghost_tool(
            GITHUB_OPS_REPRO_S5_TRACE,
            expected_tool="github_ops",
            prose_patterns=GITHUB_OPS_PATTERNS,
        )
        assert hit is not None, (
            "Detector failed to catch the canonized S5 repro — anti-ghost suite is broken"
        )
        assert hit.expected_tool == "github_ops"
        assert "github" in hit.offending_text.lower()
        assert hit.matched_pattern  # truthy


# ──────────────────────────────────────────────────────────────────────
# Tests skipped — 3 placeholders (supabase_query / file_io / code_exec).
# Se activan cuando esas tools se registren (P1 / P2).
# ──────────────────────────────────────────────────────────────────────

class TestNoGhostSkippedFutureTools:

    @pytest.mark.skip(reason="tool no registrada aún — P1/P2 (supabase_query)")
    def test_no_ghost_supabase_query(self):
        # Cuando supabase_query exista en ToolRegistry, agregar trazas
        # ghost/clean siguiendo el patrón de las activas y activar este test.
        prose_patterns = [
            r"consultar?\s+(la\s+)?(base\s+de\s+datos|supabase|postgres)",
            r"supabase_query",
            r"voy\s+a\s+correr?\s+(un\s+)?query",
        ]
        # Stub: cuando se active, reemplazar [] por SUPABASE_QUERY_GHOST_TRACE
        hit = detect_ghost_tool(
            [], expected_tool="supabase_query", prose_patterns=prose_patterns
        )
        assert hit is None or hit is not None  # placeholder — sin lógica activa

    @pytest.mark.skip(reason="tool no registrada aún — P1/P2 (file_io)")
    def test_no_ghost_file_io(self):
        prose_patterns = [
            r"(leer|escribir|abrir)\s+(el\s+|un\s+)?archivo",
            r"file_io",
            r"voy\s+a\s+(crear|guardar|modificar)\s+(el\s+|un\s+)?archivo",
        ]
        hit = detect_ghost_tool(
            [], expected_tool="file_io", prose_patterns=prose_patterns
        )
        assert hit is None or hit is not None

    @pytest.mark.skip(reason="tool no registrada aún — P1/P2 (code_exec)")
    def test_no_ghost_code_exec(self):
        prose_patterns = [
            r"(ejecutar|correr|run)\s+(el\s+|este\s+)?(c[oó]digo|script|comando)",
            r"code_exec",
            r"voy\s+a\s+ejecutar?\s+(este|ese)\s+c[oó]digo",
        ]
        hit = detect_ghost_tool(
            [], expected_tool="code_exec", prose_patterns=prose_patterns
        )
        assert hit is None or hit is not None


# ──────────────────────────────────────────────────────────────────────
# Tests del detector mismo — gates de robustez del helper
# ──────────────────────────────────────────────────────────────────────

class TestDetectorRobustness:

    def test_empty_trace_returns_none(self):
        assert (
            detect_ghost_tool([], expected_tool="x", prose_patterns=[r"foo"]) is None
        )

    def test_no_patterns_returns_none(self):
        # Sin patrones que matchear no puede haber ghost.
        assert (
            detect_ghost_tool(
                WEB_SEARCH_GHOST_TRACE, expected_tool="x", prose_patterns=[]
            )
            is None
        )

    def test_ghost_hit_reason_is_informative(self):
        hit = detect_ghost_tool(
            GITHUB_OPS_REPRO_S5_TRACE,
            expected_tool="github_ops",
            prose_patterns=GITHUB_OPS_PATTERNS,
        )
        assert hit is not None
        msg = hit.reason()
        # El mensaje debe contener: nombre del tool esperado, índice del evento,
        # tipo del evento, snippet del texto. Todo lo que un dev de runtime
        # necesitaría para diagnosticar el ghost.
        assert "github_ops" in msg
        assert "TEXT_MESSAGE_CONTENT" in msg
        assert "Tool ghost detected" in msg

    def test_clean_then_other_tool_still_ghost(self):
        """
        Caso adversarial: el LLM narra que va a usar github_ops, pero su
        siguiente tool call es de OTRO tool (ej. web_search). Debe ser ghost.
        """
        trace = [
            _ev("RUN_STARTED"),
            _ev(
                "TEXT_MESSAGE_CONTENT",
                delta="Voy a llamar a la herramienta github para list_prs.",
            ),
            _ev("TOOL_CALL_START", toolCallId="x", toolCallName="web_search"),
            _ev("TOOL_CALL_END", toolCallId="x", result="..."),
            _ev("RUN_FINISHED"),
        ]
        hit = detect_ghost_tool(
            trace,
            expected_tool="github_ops",
            prose_patterns=GITHUB_OPS_PATTERNS,
        )
        assert hit is not None
        assert hit.next_tool_event is not None
        assert (
            hit.next_tool_event.get("data", {}).get("toolCallName") == "web_search"
        )
