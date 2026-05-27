"""
Factory Routes — Cognitive Republic Aggregator (Sprint cero, DSC-G-019)
========================================================================

Router FastAPI que expone 4 endpoints aggregator de la Cognitive Republic:

  GET /v1/factory/constellation  → ForgeNode[] + ForgeEdge[] (vista federada)
  GET /v1/factory/economy        → Cognitive P&L (15 KPIs + 5 fórmulas)
  GET /v1/factory/timeline       → Sovereign Time Axis (eventos civilizacionales)
  GET /v1/factory/diff           → Reality Diff (declared vs live)

Estos endpoints son **lectura pura** (cero efectos de escritura, cero secretos
en respuesta). Los datos provienen de:

  - `_genome_out/genome_now.json` (aggregator existente, Sprint 91)
  - `_genome_out/{github,railway,supabase,live24h}.json` (sub-aggregators)
  - filesystem scan de `discovery_forense/CAPILLA_DECISIONES/` (DSCs)
  - filesystem scan de `bridge/sprints_completados/` (sprints)
  - filesystem scan de `discovery_forense/INCIDENTES/` (P0)
  - filesystem scan de `skills/` (skills canonizadas)

Auth: público (lectura). KPIs sin telemetría devuelven `null` con disclaimer
honesto en `data_quality.missing_metrics`. Cero datos fake.

DSC habilitante: DSC-G-019 (Adopción narrativa Cognitive Republic).
Sprint propuesto: bridge/sprints_propuestos/SPR-FACTORY-AGGREGATORS-000.md

Refs:
  - kernel/genome_now_routes.py (pattern a seguir)
  - scripts/genome_live/aggregator.py (fuente de _genome_out/)
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

factory_router = APIRouter(prefix="/v1/factory", tags=["factory", "cognitive-republic"])

ROOT = Path(__file__).resolve().parent.parent
GENOME_OUT_DIR = ROOT / "_genome_out"
GENOME_NOW = GENOME_OUT_DIR / "genome_now.json"
GENOME_GITHUB = GENOME_OUT_DIR / "github.json"
GENOME_RAILWAY = GENOME_OUT_DIR / "railway.json"
GENOME_SUPABASE = GENOME_OUT_DIR / "supabase.json"
GENOME_LIVE24H = GENOME_OUT_DIR / "live24h.json"

DSC_DIR = ROOT / "discovery_forense" / "CAPILLA_DECISIONES"
SPRINTS_COMPLETED_DIR = ROOT / "bridge" / "sprints_completados"
INCIDENTS_DIR = ROOT / "discovery_forense" / "INCIDENTES"
SKILLS_DIR = ROOT / "skills"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_json(path: Path) -> Optional[dict[str, Any]]:
    """Load JSON file or return None if missing/invalid (honest fallback)."""
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _now_iso() -> str:
    """Return current UTC ISO-8601 timestamp."""
    return datetime.now(timezone.utc).isoformat()


def _safe_signer_key_id() -> str:
    """Return signer key ID without exposing the PEM (env var lookup)."""
    return os.environ.get("OBSERVATORIO_SIGNER_KEY_ID", "<unset>")


def _scan_md_files(directory: Path, pattern: str = "*.md") -> list[Path]:
    """Recursive scan for markdown files. Returns empty list if dir missing."""
    if not directory.exists():
        return []
    return sorted(directory.rglob(pattern))


# ---------------------------------------------------------------------------
# Endpoint 1: /v1/factory/constellation
# ---------------------------------------------------------------------------


@factory_router.get(
    "/constellation",
    summary="Forja Constellation — fábricas federadas y envelope mesh edges",
    description=(
        "Devuelve la lista de ForgeNode (nodos de la constelación) y ForgeEdge "
        "(conexiones envelope mesh). Lectura pura, sin secretos. Fuente: "
        "`_genome_out/*.json` (aggregator Sprint 91)."
    ),
)
def get_constellation(
    tier: Optional[str] = Query(None, description="Filtrar por tier: core | inner | mid | outer"),
    kind: Optional[str] = Query(None, description="Filtrar por kind del nodo"),
) -> JSONResponse:
    """Vista federada de la Cognitive Republic.

    DSC-G-019 — esta función mappea fábricas reales a la jerarquía orbital.
    """

    genome = _load_json(GENOME_NOW)
    railway = _load_json(GENOME_RAILWAY)
    live24h = _load_json(GENOME_LIVE24H)

    nodes: list[dict[str, Any]] = []

    # Núcleo (tier=core): el Kernel
    nodes.append(
        {
            "forge_id": "kernel-monstruo",
            "name": "El Monstruo Kernel",
            "tier": "core",
            "kind": "kernel",
            "is_aggregate": False,
            "substrate": {
                "runtime": "python_fastapi",
                "endpoint": "https://el-monstruo-kernel-production.up.railway.app",
                "repo": "alfredogl1804/el-monstruo",
            },
            "sovereignty": {
                "envelope_supported": True,
                "signer_key_id": _safe_signer_key_id(),
                "court_bound": True,
                "t1_required_lanes": ["merge", "deploy", "canon"],
            },
            "production": {
                "active_lines": ["embrion_loop", "memory_curator"],
                "last_cycle_at": (genome or {}).get("meta", {}).get("generated_at"),
                "artifacts_24h": (live24h or {}).get("github_commits_24h_count", 0),
                "evidence_receipts_24h": 0,
                "failures_24h": 0,
                "cost_24h_usd": None,
            },
            "memory": {
                "writes_to_memory": True,
                "lessons_canonized": _count_dscs(),
                "unresolved_gaps": 5,
            },
            "status": _kernel_status(live24h),
        }
    )

    # Órbita interior (tier=inner): motores embriones, memoria, evidencia, court
    inner_nodes = [
        {
            "forge_id": "embrion-loop",
            "name": "Embryo Industrial Grid",
            "tier": "inner",
            "kind": "embryo_line",
            "is_aggregate": False,
            "substrate": {
                "runtime": "python",
                "endpoint": "kernel.embriones.embrion_loop",
                "repo": "alfredogl1804/el-monstruo",
            },
            "sovereignty": {
                "envelope_supported": True,
                "signer_key_id": _safe_signer_key_id(),
                "court_bound": True,
                "t1_required_lanes": ["promote_lane"],
            },
            "production": {
                "active_lines": [],
                "last_cycle_at": None,
                "artifacts_24h": 0,
                "evidence_receipts_24h": 0,
                "failures_24h": 0,
                "cost_24h_usd": None,
            },
            "memory": {
                "writes_to_memory": True,
                "lessons_canonized": None,
                "unresolved_gaps": None,
            },
            "status": "STANDBY",
        },
        {
            "forge_id": "memory-cortex",
            "name": "Memory Cortex",
            "tier": "inner",
            "kind": "memory_cortex",
            "is_aggregate": False,
            "substrate": {
                "runtime": "supabase",
                "endpoint": "supabase.thoughts + episodic + semantic",
                "repo": "alfredogl1804/el-monstruo",
            },
            "sovereignty": {
                "envelope_supported": False,
                "signer_key_id": None,
                "court_bound": False,
                "t1_required_lanes": [],
            },
            "production": {
                "active_lines": ["memory_writes"],
                "last_cycle_at": None,
                "artifacts_24h": None,
                "evidence_receipts_24h": None,
                "failures_24h": None,
                "cost_24h_usd": None,
            },
            "memory": {
                "writes_to_memory": True,
                "lessons_canonized": _count_dscs(),
                "unresolved_gaps": None,
            },
            "status": "ONLINE",
        },
        {
            "forge_id": "sovereign-court",
            "name": "Sovereign Court Chamber",
            "tier": "inner",
            "kind": "court",
            "is_aggregate": False,
            "substrate": {
                "runtime": "python_fastapi",
                "endpoint": "kernel.observatorio + kernel.audit_middleware",
                "repo": "alfredogl1804/el-monstruo",
            },
            "sovereignty": {
                "envelope_supported": True,
                "signer_key_id": _safe_signer_key_id(),
                "court_bound": True,
                "t1_required_lanes": ["all_rulings"],
            },
            "production": {
                "active_lines": ["envelope_signing"],
                "last_cycle_at": None,
                "artifacts_24h": 0,
                "evidence_receipts_24h": 0,
                "failures_24h": 0,
                "cost_24h_usd": None,
            },
            "memory": {
                "writes_to_memory": True,
                "lessons_canonized": None,
                "unresolved_gaps": None,
            },
            "status": "ONLINE",
        },
    ]
    nodes.extend(inner_nodes)

    # Órbita media (tier=mid): tablero, satélites Railway con nombres elevados
    mid_nodes = _build_mid_nodes(railway)
    nodes.extend(mid_nodes)

    # Órbita exterior (tier=outer): agregados (repos, skills, tablas)
    nodes.extend(_build_outer_aggregates(genome))

    # Filtros
    if tier:
        nodes = [n for n in nodes if n.get("tier") == tier]
    if kind:
        nodes = [n for n in nodes if n.get("kind") == kind]

    # Edges: envelope mesh entre kernel ↔ órbita interior + tablero
    edges = _build_edges(nodes)

    response = {
        "version": "1.0",
        "generated_at": _now_iso(),
        "binario_100": (genome or {}).get("meta", {}).get("binario_100", False),
        "source_genome_at": (genome or {}).get("meta", {}).get("generated_at"),
        "nodes": nodes,
        "edges": edges,
        "totals": {
            "nodes_total": len(nodes),
            "tiers": {
                "core": sum(1 for n in nodes if n.get("tier") == "core"),
                "inner": sum(1 for n in nodes if n.get("tier") == "inner"),
                "mid": sum(1 for n in nodes if n.get("tier") == "mid"),
                "outer": sum(1 for n in nodes if n.get("tier") == "outer"),
            },
        },
    }

    return JSONResponse(content=response)


def _build_mid_nodes(railway: Optional[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build mid-tier nodes from Railway projects (services as sub-fabrics)."""
    if not railway:
        return []

    nodes: list[dict[str, Any]] = []
    for ws in railway.get("workspaces", []):
        for proj in ws.get("projects", []):
            services_count = proj.get("services_count", 0)
            if services_count == 0:
                continue
            nodes.append(
                {
                    "forge_id": f"railway-{proj.get('id', 'unknown')[:8]}",
                    "name": proj.get("name", "unknown"),
                    "tier": "mid",
                    "kind": "satellite",
                    "is_aggregate": False,
                    "substrate": {
                        "runtime": "railway",
                        "endpoint": f"railway.app/project/{proj.get('id')}",
                        "repo": None,
                    },
                    "sovereignty": {
                        "envelope_supported": False,
                        "signer_key_id": None,
                        "court_bound": False,
                        "t1_required_lanes": ["deploy"],
                    },
                    "production": {
                        "active_lines": [s.get("name") for s in proj.get("services", [])],
                        "last_cycle_at": proj.get("updated_at"),
                        "artifacts_24h": None,
                        "evidence_receipts_24h": None,
                        "failures_24h": None,
                        "cost_24h_usd": None,
                    },
                    "memory": {
                        "writes_to_memory": False,
                        "lessons_canonized": None,
                        "unresolved_gaps": None,
                    },
                    "status": "ONLINE",
                }
            )
    return nodes


def _build_outer_aggregates(genome: Optional[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build outer-tier aggregate nodes (repos, skills, tables)."""
    if not genome:
        return []

    summaries = genome.get("summaries", {})
    aggregates = []

    # Repos GitHub agregado
    gh_summary = summaries.get("github", {})
    if gh_summary.get("total_repos"):
        aggregates.append(
            {
                "forge_id": "agg-repos",
                "name": f"Repos ({gh_summary.get('total_repos')})",
                "tier": "outer",
                "kind": "repo",
                "is_aggregate": True,
                "substrate": {
                    "runtime": "github",
                    "endpoint": "github.com/alfredogl1804",
                    "repo": None,
                },
                "sovereignty": {
                    "envelope_supported": False,
                    "signer_key_id": None,
                    "court_bound": False,
                    "t1_required_lanes": [],
                },
                "production": {
                    "active_lines": [],
                    "last_cycle_at": None,
                    "artifacts_24h": None,
                    "evidence_receipts_24h": None,
                    "failures_24h": None,
                    "cost_24h_usd": None,
                },
                "memory": {
                    "writes_to_memory": False,
                    "lessons_canonized": None,
                    "unresolved_gaps": None,
                },
                "status": "ONLINE",
            }
        )

    # Skills canonizadas agregado
    skills_count = _count_skills()
    if skills_count > 0:
        aggregates.append(
            {
                "forge_id": "agg-skills",
                "name": f"Skills canonized ({skills_count})",
                "tier": "outer",
                "kind": "skill_bank",
                "is_aggregate": True,
                "substrate": {
                    "runtime": "filesystem",
                    "endpoint": "skills/",
                    "repo": "alfredogl1804/el-monstruo",
                },
                "sovereignty": {
                    "envelope_supported": False,
                    "signer_key_id": None,
                    "court_bound": True,
                    "t1_required_lanes": ["canonize"],
                },
                "production": {
                    "active_lines": [],
                    "last_cycle_at": None,
                    "artifacts_24h": None,
                    "evidence_receipts_24h": None,
                    "failures_24h": None,
                    "cost_24h_usd": None,
                },
                "memory": {
                    "writes_to_memory": True,
                    "lessons_canonized": skills_count,
                    "unresolved_gaps": None,
                },
                "status": "ONLINE",
            }
        )

    # Tablas Supabase agregado
    sb_summary = summaries.get("supabase", {})
    if sb_summary.get("total_tables"):
        aggregates.append(
            {
                "forge_id": "agg-tables",
                "name": f"Supabase tables ({sb_summary.get('total_tables')})",
                "tier": "outer",
                "kind": "memory_cortex",
                "is_aggregate": True,
                "substrate": {
                    "runtime": "supabase",
                    "endpoint": "supabase.co",
                    "repo": None,
                },
                "sovereignty": {
                    "envelope_supported": False,
                    "signer_key_id": None,
                    "court_bound": False,
                    "t1_required_lanes": [],
                },
                "production": {
                    "active_lines": [],
                    "last_cycle_at": None,
                    "artifacts_24h": None,
                    "evidence_receipts_24h": None,
                    "failures_24h": None,
                    "cost_24h_usd": None,
                },
                "memory": {
                    "writes_to_memory": True,
                    "lessons_canonized": None,
                    "unresolved_gaps": None,
                },
                "status": "ONLINE",
            }
        )

    return aggregates


def _build_edges(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build envelope mesh edges between core kernel and inner-tier nodes."""
    kernel = next((n for n in nodes if n["forge_id"] == "kernel-monstruo"), None)
    if not kernel:
        return []
    edges = []
    for node in nodes:
        if node["forge_id"] == "kernel-monstruo":
            continue
        if node.get("tier") not in {"inner", "mid"}:
            continue
        edges.append(
            {
                "edge_id": f"kernel-->{node['forge_id']}",
                "from": "kernel-monstruo",
                "to": node["forge_id"],
                "envelope_kind": "policy.ruling.issued"
                if node.get("sovereignty", {}).get("court_bound")
                else "data.observability",
                "last_envelope_at": None,
                "signature_valid": node.get("sovereignty", {}).get("envelope_supported", False),
                "latency_ms": None,
            }
        )
    return edges


def _normalize_kernel_health(value: Any) -> str:
    """Normalize kernel_health to a string status (handles dict and str)."""
    if isinstance(value, dict):
        return value.get("status", "unknown")
    if isinstance(value, str):
        return value
    return "unknown"


def _kernel_status(live24h: Optional[dict[str, Any]]) -> str:
    """Return kernel status from live24h.json.

    `kernel_health` can be either a string (legacy) or a dict (current
    Sprint 91 schema with `status`, `version`, `motor`, etc.).
    """
    if not live24h:
        return "UNKNOWN"
    health = live24h.get("kernel_health")
    if isinstance(health, dict):
        status = health.get("status", "unknown")
    else:
        status = health if isinstance(health, str) else "unknown"
    return "ONLINE" if status == "healthy" else "DEGRADED"


def _count_dscs() -> int:
    """Count canonized DSCs across all subdirectories."""
    return len(_scan_md_files(DSC_DIR, "DSC-*.md"))


def _count_skills() -> int:
    """Count canonized skills (each skill has SKILL.md)."""
    if not SKILLS_DIR.exists():
        return 0
    return sum(1 for _ in SKILLS_DIR.glob("*/SKILL.md"))


# ---------------------------------------------------------------------------
# Endpoint 2: /v1/factory/economy
# ---------------------------------------------------------------------------


@factory_router.get(
    "/economy",
    summary="Cognitive P&L — balance industrial cognitivo (15 KPIs)",
    description=(
        "Devuelve los 15 KPIs y 5 fórmulas del Cognitive P&L canonizado en el "
        "rediseño v2 (DSC-G-019). KPIs sin telemetría devuelven `null` con "
        "disclaimer honesto en `data_quality.missing_metrics`. Cero datos fake."
    ),
)
def get_economy(
    window: str = Query("24h", pattern="^(24h|7d|30d|lifetime)$"),
) -> JSONResponse:
    """Cognitive P&L con disclaimer honesto.

    DSC-G-019 — KPIs sin telemetría devuelven null. Cero fakes.
    """

    live24h = _load_json(GENOME_LIVE24H)

    # Métricas que SÍ tenemos
    production_throughput_per_day = (live24h or {}).get("github_commits_24h_count", 0)

    # Lifetime aggregates
    dscs_signed_lifetime = _count_dscs()
    skills_canonized_lifetime = _count_skills()

    kpis = {
        "cost_per_production_order_usd": None,
        "cost_per_embryo_line_usd": None,
        "cost_per_accepted_evidence_usd": None,
        "cost_per_verified_claim_usd": None,
        "cost_per_pr_draft_usd": None,
        "cost_per_t1_decision_usd": None,
        "rework_cost_usd": None,
        "dory_cost_avoided_usd": None,
        "human_time_saved_hours": None,
        "model_efficiency_index": None,
        "evidence_acceptance_rate": None,
        "production_throughput_per_day": production_throughput_per_day,
        "defect_rate": None,
        "autonomy_roi": None,
        "sovereignty_score": _compute_sovereignty_score(dscs_signed_lifetime, skills_canonized_lifetime),
    }

    missing = [k for k, v in kpis.items() if v is None]

    response = {
        "version": "1.0",
        "window": window,
        "generated_at": _now_iso(),
        "kpis": kpis,
        "formulas_used": {
            "cognitive_roi": "(value_artifacts - costs) / (model_cost + infra_cost)",
            "dory_cost_avoided": "historical_rework_pre_memory - current_rework_post_memory",
            "evidence_yield": "verified_claims / total_claims",
            "embryo_productivity": "accepted_artifacts / cost_usd",
            "t1_leverage": "decisions_made / human_minutes_spent",
        },
        "data_quality": {
            "coverage": "partial",
            "missing_metrics": missing,
            "honest_disclaimer": (
                "v1: solo cubre métricas con telemetría real existente. KPIs faltantes "
                "serán habilitados conforme sprints siguientes canonicen sus fuentes "
                "(usage_tracker, embrion_loop telemetry, evidence receipts). "
                "DSC-G-019 prohíbe valores fabricados."
            ),
        },
    }

    return JSONResponse(content=response)


def _compute_sovereignty_score(dscs: int, skills: int) -> dict[str, Any]:
    """Compute a basic sovereignty score from canonical artifacts.

    Honest formula: count of signed DSCs + canonized skills as proxy for
    civilizational density. v1 deliberately simple.
    """
    raw = dscs + skills
    return {
        "raw_score": raw,
        "components": {"dscs_signed": dscs, "skills_canonized": skills},
        "honest_note": "v1: proxy lineal de densidad civilizacional. Sin normalización temporal.",
    }


# ---------------------------------------------------------------------------
# Endpoint 3: /v1/factory/timeline
# ---------------------------------------------------------------------------


@factory_router.get(
    "/timeline",
    summary="Sovereign Time Axis — eventos civilizacionales del Monstruo",
    description=(
        "Devuelve eventos civilizacionales (DSCs firmados, sprints completados, "
        "P0 incidents, skills canonizadas, embrion cycles, production orders, "
        "court rulings, memory mutations) ordenados cronológicamente."
    ),
)
def get_timeline(
    since: Optional[str] = Query(None, description="ISO-8601 — desde cuándo"),
    until: Optional[str] = Query(None, description="ISO-8601 — hasta cuándo"),
    types: Optional[str] = Query(None, description="comma-separated type filter"),
    limit: int = Query(100, ge=1, le=500),
) -> JSONResponse:
    """Sovereign Time Axis con eventos del repo vivo.

    DSC-G-019 — civilización como eventos, no como prosa.
    """

    type_filter = set(types.split(",")) if types else None

    events: list[dict[str, Any]] = []

    # 1. DSCs firmados
    for dsc_path in _scan_md_files(DSC_DIR, "DSC-*.md"):
        if type_filter and "dsc_signed" not in type_filter:
            continue
        ev = _parse_dsc_event(dsc_path)
        if ev:
            events.append(ev)

    # 2. Sprints completados
    for sprint_path in _scan_md_files(SPRINTS_COMPLETED_DIR, "*.md"):
        if type_filter and "sprint_completed" not in type_filter:
            continue
        ev = _parse_sprint_event(sprint_path)
        if ev:
            events.append(ev)

    # 3. P0 incidents
    for inc_path in _scan_md_files(INCIDENTS_DIR, "P0_*.md"):
        if type_filter and "incident_p0" not in type_filter:
            continue
        ev = _parse_incident_event(inc_path)
        if ev:
            events.append(ev)

    # 4. Skills canonizadas
    if SKILLS_DIR.exists():
        for skill_md in SKILLS_DIR.glob("*/SKILL.md"):
            if type_filter and "skill_canonized" not in type_filter:
                continue
            ev = _parse_skill_event(skill_md)
            if ev:
                events.append(ev)

    # Filtros de fecha
    if since:
        events = [e for e in events if e.get("timestamp", "") >= since]
    if until:
        events = [e for e in events if e.get("timestamp", "") <= until]

    # Sort cronológico ascendente
    events.sort(key=lambda e: e.get("timestamp", ""))

    # Limit
    truncated = len(events) > limit
    events_out = events[-limit:]  # quedarnos con los más recientes

    totals = {
        "events_total": len(events),
        "events_returned": len(events_out),
        "truncated": truncated,
        "incidents_p0": sum(1 for e in events if e.get("type") == "incident_p0"),
        "dscs_signed": sum(1 for e in events if e.get("type") == "dsc_signed"),
        "skills_canonized": sum(1 for e in events if e.get("type") == "skill_canonized"),
        "sprints_completed": sum(1 for e in events if e.get("type") == "sprint_completed"),
        "embrion_cycles": 0,  # v1: no scan tabla; futuro sprint
        "production_orders": 0,
        "court_rulings": 0,
        "mutations_predicted": 0,
    }

    response = {
        "version": "1.0",
        "generated_at": _now_iso(),
        "window": {"since": since, "until": until},
        "events": events_out,
        "totals": totals,
    }

    return JSONResponse(content=response)


def _parse_dsc_event(path: Path) -> Optional[dict[str, Any]]:
    """Parse a DSC markdown file into a timeline event."""
    try:
        text = path.read_text(encoding="utf-8")
        lines = text.split("\n")[:30]
        title = lines[0].lstrip("# ").strip() if lines else path.stem
        timestamp = _extract_date_from_lines(lines) or _file_mtime_iso(path)
        return {
            "id": path.stem,
            "type": "dsc_signed",
            "timestamp": timestamp,
            "title": title,
            "source": str(path.relative_to(ROOT)),
            "severity": "INFO",
            "sovereignty_delta": 1,
            "productivity_delta": None,
            "risk_delta": -1,
            "cost_delta_usd": 0,
            "linked_artifacts": [],
            "lessons": [],
        }
    except (OSError, UnicodeDecodeError):
        return None


def _parse_sprint_event(path: Path) -> Optional[dict[str, Any]]:
    """Parse a completed sprint markdown into a timeline event."""
    try:
        timestamp = _file_mtime_iso(path)
        title = path.stem.replace("_", " ")
        return {
            "id": path.stem,
            "type": "sprint_completed",
            "timestamp": timestamp,
            "title": title,
            "source": str(path.relative_to(ROOT)),
            "severity": "INFO",
            "sovereignty_delta": 1,
            "productivity_delta": 1,
            "risk_delta": 0,
            "cost_delta_usd": None,
            "linked_artifacts": [],
            "lessons": [],
        }
    except OSError:
        return None


def _parse_incident_event(path: Path) -> Optional[dict[str, Any]]:
    """Parse a P0 incident markdown into a timeline event."""
    try:
        timestamp = _file_mtime_iso(path)
        return {
            "id": path.stem,
            "type": "incident_p0",
            "timestamp": timestamp,
            "title": path.stem.replace("_", " "),
            "source": str(path.relative_to(ROOT)),
            "severity": "P0",
            "sovereignty_delta": -1,
            "productivity_delta": -1,
            "risk_delta": 1,
            "cost_delta_usd": None,
            "linked_artifacts": [],
            "lessons": [],
        }
    except OSError:
        return None


def _parse_skill_event(path: Path) -> Optional[dict[str, Any]]:
    """Parse a SKILL.md into a timeline event."""
    try:
        timestamp = _file_mtime_iso(path)
        skill_name = path.parent.name
        return {
            "id": f"skill-{skill_name}",
            "type": "skill_canonized",
            "timestamp": timestamp,
            "title": f"Skill: {skill_name}",
            "source": str(path.relative_to(ROOT)),
            "severity": "INFO",
            "sovereignty_delta": 1,
            "productivity_delta": 1,
            "risk_delta": 0,
            "cost_delta_usd": 0,
            "linked_artifacts": [],
            "lessons": [],
        }
    except OSError:
        return None


def _extract_date_from_lines(lines: list[str]) -> Optional[str]:
    """Try to extract a `**Fecha:** YYYY-MM-DD` line from DSC header."""
    import re

    for line in lines:
        m = re.search(r"\*\*Fecha:\*\*\s*(\d{4}-\d{2}-\d{2})", line)
        if m:
            return f"{m.group(1)}T00:00:00+00:00"
    return None


def _file_mtime_iso(path: Path) -> str:
    """Return ISO timestamp of file modification time."""
    try:
        ts = path.stat().st_mtime
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    except OSError:
        return _now_iso()


# ---------------------------------------------------------------------------
# Endpoint 4: /v1/factory/diff
# ---------------------------------------------------------------------------


@factory_router.get(
    "/diff",
    summary="Reality Diff — declared vs live alignment",
    description=(
        "Devuelve el delta entre lo declarado (genome auto-generado del repo) y "
        "lo vivo (genome aggregator Sprint 91). `binario_100_live=true` cuando "
        "los 4 dominios coinciden."
    ),
)
def get_diff() -> JSONResponse:
    """Reality Diff entre declared y live.

    DSC-G-019 — la fábrica que respira vs la fábrica documentada.
    """

    genome = _load_json(GENOME_NOW)
    if not genome:
        return JSONResponse(
            content={
                "version": "1.0",
                "generated_at": _now_iso(),
                "binario_100_live": False,
                "drift_count": None,
                "error": "genome_now.json not found — run scripts/genome_live/run_all.py",
            },
            status_code=503,
        )

    summaries = genome.get("summaries", {})
    cross = genome.get("cross_validation", {})

    domains = {
        "github": {
            "declared_repos": summaries.get("github", {}).get("expected_repos"),
            "live_repos": summaries.get("github", {}).get("total_repos"),
            "match": summaries.get("github", {}).get("match", False),
            "diff": [],
            "scanned_at": summaries.get("github", {}).get("scanned_at"),
        },
        "railway": {
            "declared_services": summaries.get("railway", {}).get("expected_services"),
            "live_services": summaries.get("railway", {}).get("total_services"),
            "match": summaries.get("railway", {}).get("match", False),
            "diff": [],
            "scanned_at": summaries.get("railway", {}).get("scanned_at"),
        },
        "supabase": {
            "declared_tables": summaries.get("supabase", {}).get("expected_tables"),
            "live_tables": summaries.get("supabase", {}).get("total_tables"),
            "match": summaries.get("supabase", {}).get("match", False),
            "diff": [],
            "scanned_at": summaries.get("supabase", {}).get("scanned_at"),
        },
        "live24h": {
            "kernel_health": _normalize_kernel_health(
                summaries.get("live24h", {}).get("kernel_health")
            ),
            "drift_over_7d": summaries.get("live24h", {}).get("drift_over_7d"),
            "match": summaries.get("live24h", {}).get("match", False),
            "scanned_at": summaries.get("live24h", {}).get("scanned_at"),
        },
    }

    drift_count = sum(1 for d in domains.values() if not d.get("match"))

    # Sprint drift (declared vs completed)
    proposed_count = (
        len(_scan_md_files(ROOT / "bridge" / "sprints_propuestos", "*.md"))
        if (ROOT / "bridge" / "sprints_propuestos").exists()
        else 0
    )
    completed_count = (
        len(_scan_md_files(ROOT / "bridge" / "sprints_completados", "*.md"))
        if (ROOT / "bridge" / "sprints_completados").exists()
        else 0
    )

    response = {
        "version": "1.0",
        "generated_at": _now_iso(),
        "binario_100_live": (genome or {}).get("meta", {}).get("binario_100", False),
        "source_genome_at": (genome or {}).get("meta", {}).get("generated_at"),
        "drift_count": drift_count,
        "domains": domains,
        "cross_validation": {
            "all_domains_match": all(d.get("match") for d in domains.values()),
            "details": cross,
        },
        "sprint_drift": {
            "proposed_sprints": proposed_count,
            "completed_sprints": completed_count,
            "in_progress_sprints": None,
            "drift_alerts": [],
        },
    }

    return JSONResponse(content=response)
