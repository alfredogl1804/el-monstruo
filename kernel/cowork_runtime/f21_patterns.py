"""
kernel/cowork_runtime/f21_patterns.py — Sprint COWORK-AUTO-DISCIPLINE-REAL-001 T2

Catálogo canónico de patterns F21 que el detector debe matchear en outputs de
Cowork para enforzar DSC-S-016 (anti-fabricación causalidad sin grep) runtime.

Cada pattern declara:
- id: identificador estable usado en violations_detected JSONB
- regex: regex pattern (string) que matchea claims especulativos
- description: descripción humana de qué F21 instance representa
- requires_tool_call: list[str] de tool/comando que DEBE aparecer en history
                      antes de que el claim sea legítimo
- severity: P0 (bloqueo magna) | P1 (bloqueo premium) | P2 (warning)
- only_in_audit_outputs: si True, solo aplicar regex cuando output parece audit/reporte
                        (evita falsos positivos en chat conversacional)

Doctrina:
- DSC-S-016 (firmado 2026-05-12 ~09:35 UTC): "verificación binaria pre-aserción"
- DSC-G-008 v3 §4 (deducir consecuencias): patterns no se aplican en isolation —
  el detector debe pedirle al hook la `history` real (last K turns) para validar.
- Anti-Goodhart: los patterns aquí son sobre AFIRMACIONES (no sobre el contexto
  del audit que las mencione). Por eso `only_in_audit_outputs` para algunos.

Origen 10 instancias F21 reincidentes Cowork HOY (2026-05-12) canonizadas en
embrion_memoria (ver spec §0 audit pre-sprint). Cada pattern aquí mata 1+ de esas
instancias verificables binariamente vía tool call previo.

Uso programático:

    from kernel.cowork_runtime.f21_patterns import F21_PATTERNS
    for pattern in F21_PATTERNS:
        if re.search(pattern["regex"], output):
            # verificar que pattern["requires_tool_call"] aparece en history
            ...

Patrón doctrinal: NO modificar F21_PATTERNS in-place — agregar nuevas entries al
final de la lista para preservar índices estables. Cambio de regex existente
requiere DSC firmado + bump de version.
"""

from __future__ import annotations

from typing import Any

# Versión semántica del catálogo. Bump cuando se agreguen/modifiquen patterns.
F21_PATTERNS_VERSION: str = "1.0.0"

# Catálogo canónico — 10 patterns P1-P10 verbatim del spec firmado commit d53b80ff §2.1.
F21_PATTERNS: list[dict[str, Any]] = [
    # P1: Diff stats sin tool call previo (git diff/gh pr view)
    {
        "id": "diff_stats",
        "regex": r"\b\d+ files? changed,? \+\d+/-\d+\b",
        "description": (
            "Claim sobre 'N files changed, +M/-K' sin git diff previo. "
            "Patrón derivado de F21 propio sobre PR #117 ESPIRAL "
            "'12 files -154 deletions' cuando realidad era 11 files +1879/-0."
        ),
        "requires_tool_call": ["git diff", "gh pr view", "git diff --stat", "git show --stat"],
        "severity": "P1",
        "only_in_audit_outputs": False,
    },
    # P2: Schema DB sin SQL query previa
    {
        "id": "db_schema",
        "regex": (
            r"(?i)("
            r"CREATE TABLE\s+\w+|"
            r"schema.*column.*:.*\w+|"
            r"\btable\.\w+\s+(integer|text|jsonb|uuid|timestamptz|boolean)\b"
            r")"
        ),
        "description": (
            "Claim sobre schema (CREATE TABLE / column type / table.field type) "
            "sin execute_sql o information_schema query previa. Patrón derivado de "
            "F21 spec MIGRATION-DRIFT v1 T6 columnas inventadas (decision/source/"
            "payload/timestamp) que no existían en validation_log real."
        ),
        "requires_tool_call": [
            "execute_sql",
            "information_schema.columns",
            "pg_class",
            "\\d+",
            "psql",
        ],
        "severity": "P0",
        "only_in_audit_outputs": False,
    },
    # P3: Versiones de modelos sin grep/web fetch
    {
        "id": "model_versions",
        "regex": (
            r"\b("
            r"GPT-\d+(\.\d+)?|"
            r"Claude\s+(Opus|Sonnet|Haiku)\s+\d+(\.\d+)?|"
            r"Gemini\s+\d+(\.\d+)?|"
            r"Grok\s+\d+|"
            r"DeepSeek\s+(R|V)\d+|"
            r"Kimi\s+K\d+(\.\d+)?|"
            r"Sonar\s+(Pro|Reasoning)|"
            r"Copilot\s+365"
            r")\b"
        ),
        "description": (
            "Cita de modelo IA con versión específica sin grep al repo, web fetch o "
            "consulta a /v1/models. Patrón derivado de F21 spec REMONTOIR v3 "
            "'8 Sabios doctrina viva incluyendo Copilot 365 raw' (FALSO) e "
            "interpretación output Perplexity 'Opus 4.7 NO existe' (Perplexity solo "
            "recomendaba fallback). DSC anti-autoboicot canonizado."
        ),
        "requires_tool_call": [
            "grep",
            "WebFetch",
            "models_available",
            "/v1/models",
            "semilla v7.3",
        ],
        "severity": "P1",
        "only_in_audit_outputs": False,
    },
    # P4: Commit hashes sin verificación git log
    {
        "id": "commit_hashes",
        "regex": r"\bcommit\s+`?[0-9a-f]{7,40}`?\b",
        "description": (
            "Cita de commit hash específico (≥7 chars hex) sin git log/gh pr view/"
            "git show previo. Mata fabricación de commit hashes inexistentes."
        ),
        "requires_tool_call": [
            "git log",
            "gh pr view",
            "git show",
            "git ls-tree",
            "git rev-parse",
            "gh api",
        ],
        "severity": "P0",
        "only_in_audit_outputs": False,
    },
    # P5: Git state branches stale/ahead/behind sin tool call
    {
        "id": "git_state",
        "regex": r"\b\d+\s+commits?\s+(ahead|behind|stale)\b",
        "description": (
            "Claim sobre 'N commits ahead/behind/stale' sin git log/gh pr view --json/"
            "git rev-list previo. Patrón derivado de F21 spec MIGRATION-DRIFT v1 "
            "asumió merge directo viable (branches stale 123+144 commits) sin verificar."
        ),
        "requires_tool_call": [
            "git log",
            "gh pr view --json",
            "git rev-list",
            "git status",
        ],
        "severity": "P1",
        "only_in_audit_outputs": False,
    },
    # P6: PR existence claim sin gh pr view
    {
        "id": "pr_existence",
        "regex": r"\bPR\s*#?\d+\s+(existe|ya existe|YA EXIST|abierto|cerrado|mergeado|merged|open|closed)\b",
        "description": (
            "Claim sobre estado de PR (#N existe/abierto/cerrado/mergeado) sin "
            "gh pr view previo. Patrón derivado de F21 spec MIGRATION-DRIFT v2 T3 "
            "'crear PR' cuando #98 ya existía + F21 propio kickoff corrección 3 docs."
        ),
        "requires_tool_call": [
            "gh pr view",
            "gh pr list",
            "list_pull_requests",
            "gh api",
        ],
        "severity": "P1",
        "only_in_audit_outputs": False,
    },
    # P7: Migration filename claims sin ls
    {
        "id": "migration_filename",
        "regex": r"\b\d{4}_\w+\.sql\b",
        "description": (
            "Cita de migration filename (NNNN_nombre.sql) sin ls migrations/sql/ o "
            "git ls-tree previo. Patrón derivado de F21 V25 grave CLAIM-C migration "
            "0020 (Sprint T5 vs PAR_BICEFALO mezclados) + doble 0021 en main."
        ),
        "requires_tool_call": [
            "ls migrations/sql",
            "git ls-tree",
            "grep migrations",
            "find migrations",
        ],
        "severity": "P1",
        "only_in_audit_outputs": False,
    },
    # P8: Branch overlap claims sin diff
    {
        "id": "branch_overlap",
        "regex": r"(?i)\b(overlap|colisi[oó]n|conflict)\s+(con|with)\s+PR\s*#?\d+",
        "description": (
            "Claim sobre overlap/colisión/conflict entre branches o PRs sin "
            "git diff/git merge-tree/gh pr view --json previo. Patrón derivado de "
            "F2+F21 merge-tree vs diff lineal PR #110 G6."
        ),
        "requires_tool_call": [
            "git diff",
            "git merge-tree",
            "gh pr view --json",
        ],
        "severity": "P1",
        "only_in_audit_outputs": False,
    },
    # P9: Test count claims sin ejecución
    {
        "id": "test_count",
        "regex": r"\b\d+/\d+\s+(tests?\s+)?(passed|PASS|verde|verdes?|green|failed|FAIL)\b",
        "description": (
            "Claim sobre 'N/M tests passed/verde/failed' sin pytest/npm test/"
            "flutter test ejecución previa. Mata fabricación de coverage reports."
        ),
        "requires_tool_call": [
            "pytest",
            "npm test",
            "flutter test",
            "grep def test_",
            "go test",
        ],
        "severity": "P1",
        "only_in_audit_outputs": False,
    },
    # P10: RLS/policy claims sin SQL verification
    {
        "id": "rls_policy",
        "regex": r"(?i)\b(RLS|policy|service_role_only)\s+(habilitada|activa|funciona|enabled)\b",
        "description": (
            "Claim sobre RLS/policy enabled/funciona sin pg_policies/pg_tables/"
            "information_schema query previa. Solo se aplica en outputs que parecen "
            "audit/reporte (no en specs nuevos donde se describe la RLS futura)."
        ),
        "requires_tool_call": [
            "pg_policies",
            "pg_tables",
            "information_schema",
            "execute_sql",
            "psql",
        ],
        "severity": "P1",
        "only_in_audit_outputs": True,
    },
]


# Heurística para detectar si un output Cowork "parece audit/reporte"
# (usado por patterns con only_in_audit_outputs=True).
AUDIT_OUTPUT_INDICATORS: tuple[str, ...] = (
    "audit",
    "verificación binaria",
    "verificacion binaria",
    "reporte",
    "reportar",
    "estado verificado",
    "post-apply",
    "post-merge",
    "smoke test",
    "validación",
    "validacion",
    "DSC-G-008",
    "deducción",
    "deduccion",
)


def output_parece_audit(output: str) -> bool:
    """Heurística rápida: ¿el output parece un audit/reporte vs chat conversacional?"""
    output_lower = output.lower()
    return any(ind in output_lower for ind in AUDIT_OUTPUT_INDICATORS)


def get_pattern_by_id(pattern_id: str) -> dict[str, Any] | None:
    """Lookup pattern por id estable. Returns None si no existe."""
    for p in F21_PATTERNS:
        if p["id"] == pattern_id:
            return p
    return None


def all_pattern_ids() -> list[str]:
    """Lista de ids estables (para tests + diagnóstico)."""
    return [p["id"] for p in F21_PATTERNS]
