#!/usr/bin/env python3
"""
aggregator.py — Genome Vivo Aggregator (Sprint 91 F5 + Sprint 91.10 Atomic Map).

Lee los outputs binarios de F1-F4 y produce un único JSON canónico:

  _genome_out/genome_now.json

Campos clave:
  - meta.generated_at
  - meta.binario_100 (bool): True si todos los scanners reportaron coverage_match
  - github / railway / supabase / live24h: resúmenes ejecutivos + datos completos
  - cross_validation: hallazgos del cruzado entre fuentes
  - ecosystem_atomic_map: mapa atómico completo del ecosistema (Sprint 91.10)

Idempotente: corre N veces sin efectos colaterales.

Autor: Manus — Sprint 91 F5 + Sprint 91.10 (Atomic Map Enrichment)
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT / "_genome_out"
OUT_FILE = OUT_DIR / "genome_now.json"


def load_or_empty(name: str) -> dict:
    p = OUT_DIR / name
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except Exception as e:
        print(f"  [WARN] {p} corrupto: {e}", flush=True)
        return {}


def cross_validate(gh: dict, rly: dict, sb: dict, live: dict) -> dict:
    """Validación cruzada entre fuentes."""
    findings: list[dict] = []

    # 1. ¿Cada repo Railway aparece en GitHub?
    gh_repos = {r.get("full_name") or r.get("name") for r in gh.get("repos", [])}
    railway_repos: set[str] = set()
    for ws in rly.get("workspaces", []):
        for proj in ws.get("projects", []):
            for svc in proj.get("services", []):
                for inst in svc.get("instances", []):
                    repo = (inst.get("source") or {}).get("repo")
                    if repo:
                        railway_repos.add(repo)
                    deploy_repo = (inst.get("deploy") or {}).get("repo")
                    if deploy_repo:
                        railway_repos.add(deploy_repo)
    railway_repos = {r for r in railway_repos if r}

    missing = railway_repos - gh_repos
    if missing:
        findings.append(
            {
                "kind": "railway_repos_not_in_github",
                "severity": "warning",
                "message": f"{len(missing)} repos referenciados en Railway no aparecen en GitHub scanner",
                "items": sorted(missing)[:20],
            }
        )

    # 2. ¿Hay drift > 7 días?
    drift = live.get("drift_services_over_7d_count", 0)
    if drift > 0:
        findings.append(
            {
                "kind": "railway_drift_over_7d",
                "severity": "info",
                "message": f"{drift} servicios Railway con último deploy > 7 días",
                "count": drift,
            }
        )

    # 3. ¿Coverage_match en todos?
    matches = {
        "github": gh.get("coverage_match", False) if gh else False,
        "railway": rly.get("coverage_match", False) if rly else False,
        "supabase": sb.get("coverage_match", False) if sb else False,
        "live24h": live.get("coverage_match", False) if live else False,
    }

    return {
        "findings": findings,
        "findings_count": len(findings),
        "coverage_match_per_source": matches,
    }


def build_ecosystem_atomic_map() -> dict[str, Any]:
    """
    Sprint 91.10 — Mapa atómico estático del ecosistema.

    Datos verificados por barrido exhaustivo (wc -l real, 2026-05-29).
    Se actualiza manualmente cuando hay cambios estructurales mayores.
    """
    return {
        "version": "2026-05-29",
        "total_lines_of_code": 479653,
        "kernel_version": "v0.84.8-sprint-memento",
        "sprint_current": 91,
        "sovereignty_score": 118,
        "embrion_cycles": 191,
        "embrion_status": "standby (instrucción 22-mayo rompe-bucle)",
        "lines_by_component": {
            "kernel": {"lines": 104646, "language": "Python", "function": "Cerebro central: FastAPI + LangGraph + 13 componentes"},
            "tests": {"lines": 51966, "language": "Python", "function": "143+ tests pasando"},
            "sql_migrations": {"lines": 41499, "language": "SQL", "function": "62 migraciones Supabase aplicadas"},
            "apps_mobile": {"lines": 34327, "language": "Dart", "function": "App Flutter: 3 modos, 6 agentes, 72 archivos"},
            "skills": {"lines": 31663, "language": "Python", "function": "Skills modulares del kernel"},
            "scripts": {"lines": 32160, "language": "Python+Bash", "function": "Genome scanners, deploy helpers, seed scripts"},
            "bridge": {"lines": 16937, "language": "Mixed", "function": "Comunicación inter-hilos + handoff"},
            "apps_la_forja": {"lines": 13321, "language": "TypeScript", "function": "Backend Hono: 5 puertas LLM + budget"},
            "shell_scripts": {"lines": 14326, "language": "Bash", "function": "Automation, deploy, CI"},
            "tools": {"lines": 12259, "language": "Python", "function": "20 tools (14 activas, 3 HITL, 3 sin creds)"},
            "repos_satelite": {"lines": 97443, "language": "Mixed", "function": "11 repos satélite con código real"},
            "otros": {"lines": 29106, "language": "Python", "function": "Memory, embryos, router, governance"},
        },
        "kernel_components": [
            {"name": "engine", "lines": 1847, "function": "Grafo LangGraph: 8 nodos, ReAct, circuit breaker, recursion_limit=25"},
            {"name": "main", "lines": 1203, "function": "FastAPI app con 20+ routers montados"},
            {"name": "embrion_loop", "lines": 1372, "function": "Loop autónomo: piensa cada 60s, cooldown 5min, budget $30/día"},
            {"name": "factory_routes", "lines": 938, "function": "Constellation + Economy + Timeline + Diff (República Cognitiva)"},
            {"name": "genome_now_routes", "lines": 304, "function": "Endpoint /v1/genome/now con refresh background"},
            {"name": "onboarding", "lines": 487, "function": "Wizard 5 fases para nuevos usuarios"},
            {"name": "nodes", "lines": 800, "function": "8 nodos: classify, retrieve_context, call_llm, execute_tool, evaluate, respond, human_review, error_handler"},
        ],
        "memory_layers": [
            {"layer": "hot", "function": "In-context (ventana del modelo)"},
            {"layer": "warm_supabase", "records": 3034, "function": "Thoughts, episodic, semantic, embrión responses"},
            {"layer": "cold_mem0", "function": "Largo plazo cross-session (código listo, no deployado)"},
            {"layer": "event_store", "records": 5803, "function": "Todos los runs del kernel"},
            {"layer": "knowledge_graph", "entities": 151, "function": "LightRAG: relaciones semánticas"},
            {"layer": "sovereign_memory", "records": 1517, "axioms": 57, "function": "SMS v4.0: memorias soberanas"},
            {"layer": "error_memory", "records": 38, "resolved": 36, "function": "Aprende de fallos"},
        ],
        "catastros": [
            {"name": "Modelos LLM", "entries": 41, "function": "Rankea, recomienda, vota entre modelos IA"},
            {"name": "Agentes 2026", "entries": 21, "function": "Cataloga agentes IA del mercado"},
            {"name": "Herramientas AI", "entries": 24, "function": "Tools verticales con precios verificados"},
            {"name": "Suppliers Humanos", "entries": 36, "function": "Proveedores reales Sureste MX"},
        ],
        "agents": [
            {"name": "researcher", "model": "sonar-reasoning-pro", "tools": ["web_search", "knowledge_query"]},
            {"name": "analyst", "model": "gpt-5.5-pro", "tools": ["data_analyzer", "calculator"]},
            {"name": "writer", "model": "claude-opus-4.7", "tools": ["document_generator", "knowledge_query"]},
            {"name": "developer", "model": "claude-opus-4.7", "tools": ["code_interpreter", "file_manager"]},
            {"name": "strategist", "model": "gpt-5.5-pro", "tools": ["web_search", "data_analyzer"]},
            {"name": "communicator", "model": "gpt-5.5-pro", "tools": ["email_sender", "notification"]},
        ],
        "models_available": [
            {"model": "grok-4", "usage_pct": 56, "role": "Razonamiento rápido"},
            {"model": "sonar-reasoning-pro", "usage_pct": 15, "role": "Investigación en tiempo real"},
            {"model": "claude-opus-4.7", "usage_pct": 15, "role": "Coding, escritura técnica"},
            {"model": "gpt-5.5-pro", "usage_pct": 11, "role": "Arquitectura, estrategia"},
            {"model": "gemini-3.1-pro", "usage_pct": 2, "role": "Multimodal, análisis largo"},
            {"model": "deepseek-r1", "usage_pct": 1, "role": "Razonamiento profundo"},
        ],
        "interfaces": [
            {"name": "Telegram Bot", "stack": "Python + Railway", "status": "standby"},
            {"name": "Open WebUI", "stack": "Fork + Railway", "status": "active"},
            {"name": "Command Center", "stack": "Next.js + Railway", "status": "active"},
            {"name": "AG-UI Gateway", "stack": "Python FastAPI", "status": "active"},
            {"name": "App Flutter", "stack": "Dart, 72 archivos, 16202 líneas", "status": "functional"},
            {"name": "La Forja", "stack": "Hono API + Next.js", "status": "active"},
        ],
        "repos_satelite": [
            {"name": "like-kukulkan-tickets", "lines": 36025, "function": "Boletería Leones (TS full-stack)"},
            {"name": "tablero-campana", "lines": 15769, "function": "Forja Protocol: firmas ed25519 + SubEnvelope"},
            {"name": "crisol-8", "lines": 8376, "function": "OSINT Investigation (Python)"},
            {"name": "rug-carousel", "lines": 8412, "function": "Catálogo alfombras (TS)"},
            {"name": "el-monstruo-bot", "lines": 8268, "function": "Bot Telegram (Python)"},
            {"name": "observatorio-merida-2027", "lines": 7970, "function": "Modelo Bayesiano electoral"},
            {"name": "biblia-github-motor", "lines": 4658, "function": "Motor de biblias (Python)"},
            {"name": "command-center", "lines": 3806, "function": "Dashboard (TS/Next.js)"},
            {"name": "simulador-universal", "lines": 2462, "function": "Monte Carlo + ABM (Python)"},
            {"name": "fernando-dia-maestro-2026", "lines": 1471, "function": "Dashboard show (HTML)"},
            {"name": "forja-mcp", "lines": 226, "function": "MCP Gateway (TS)"},
        ],
        "governance": {
            "dscs_signed": 99,
            "domains": ["Governance", "Security", "Mobile", "Autonomy", "Embrion", "Architecture", "Memory", "Operations", "Brand"],
            "memento_operations": 6,
            "guardian_version": "V5 (SMS-enabled)",
            "brand_threshold": 60,
            "brand_avg_score": 90,
        },
        "factory_endpoints": [
            {"path": "/v1/factory/constellation", "function": "ForgeNodes federados"},
            {"path": "/v1/factory/economy", "function": "Cognitive P&L (15 KPIs)"},
            {"path": "/v1/factory/timeline", "function": "Sovereign Time Axis"},
            {"path": "/v1/factory/diff", "function": "Reality Diff (4 dominios)"},
        ],
        "gaps_known": [
            "embrion_loop aislado (no comparte state con kernel graph)",
            "collective RAM-only (no persiste debates)",
            "embriones domain-specialists stateless",
            "bot Telegram en standby (instrucción 22-mayo)",
            "embeddings pending en algunas tablas",
            "domain embriones doctrine-only (no ejecutan)",
            "Catastro de Modelos DB degradada (código listo, tabla no poblada)",
        ],
        "metrics": {
            "runs_total": 5803,
            "tokens_12d": "64.6M",
            "cost_today_usd": 0.83,
            "budget_daily_usd": 30,
            "sovereign_memories": 1517,
            "axioms": 57,
            "sprints_completed": 15,
            "sprints_proposed": 32,
            "branches_active": 458,
        },
    }


def aggregate() -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    print(f"[{started}] Agregando genome_now...", flush=True)

    gh = load_or_empty("github.json")
    rly = load_or_empty("railway.json")
    sb = load_or_empty("supabase.json")
    live = load_or_empty("live24h.json")

    cross = cross_validate(gh, rly, sb, live)

    binario_100 = (
        cross["coverage_match_per_source"]["github"]
        and cross["coverage_match_per_source"]["railway"]
        and cross["coverage_match_per_source"]["supabase"]
        and cross["coverage_match_per_source"]["live24h"]
    )

    # Resúmenes ejecutivos
    summaries = {
        "github": {
            # Sprint 91.5 hotfix — corregir contrato con github_scanner.py
            # El scanner produce got_total/expected_total (no repos_count/expected_total_count).
            "repos_total": gh.get("got_total", 0),
            "expected_total": gh.get("expected_total", 0),
            "match": gh.get("coverage_match", False),
            "scanned_at": gh.get("finished_at"),
        },
        "railway": {
            "workspaces": rly.get("workspaces_count", 0),
            "projects": rly.get("projects_count", 0),
            "total_services": rly.get("total_services", 0),
            "expected_services": rly.get("expected_total_services", 0),
            "match": rly.get("coverage_match", False),
            "scanned_at": rly.get("finished_at"),
        },
        "supabase": {
            "schemas": sb.get("schemas_count", 0),
            "tables": sb.get("tables_count", 0),
            "functions": sb.get("functions_count", 0),
            "extensions": sb.get("extensions_count", 0),
            "buckets": sb.get("buckets_count", 0),
            "migrations": sb.get("migrations_count", 0),
            "indexes": sb.get("indexes_count", 0),
            "triggers": sb.get("triggers_count", 0),
            "match": sb.get("coverage_match", False),
            "scanned_at": sb.get("finished_at"),
        },
        "live24h": {
            "github_commits_24h": live.get("github_commits_24h_count", 0),
            "railway_deploys_24h": live.get("railway_deploys_24h_count", 0),
            "supabase_migrations_24h": live.get("supabase_migrations_24h_count", 0),
            "drift_over_7d": live.get("drift_services_over_7d_count", 0),
            "kernel_health": live.get("kernel_health", {}).get("status", "unknown"),
            "match": live.get("coverage_match", False),
            "scanned_at": live.get("finished_at"),
        },
    }

    finished = datetime.now(timezone.utc).isoformat()

    return {
        "version": 2,
        "meta": {
            "generated_at": finished,
            "generated_by": "scripts/genome_live/aggregator.py",
            "binario_100": binario_100,
            "sprint": "Sprint 91 — Mapa Vivo 100% del Monstruo",
            "branch": "feat/sprint-91-mapa-vivo-100",
            "atomic_map_version": "2026-05-29",
        },
        "summaries": summaries,
        "cross_validation": cross,
        "ecosystem_atomic_map": build_ecosystem_atomic_map(),
        "github": gh,
        "railway": rly,
        "supabase": sb,
        "live24h": live,
    }


def main() -> int:
    OUT_DIR.mkdir(exist_ok=True)
    result = aggregate()
    OUT_FILE.write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    print("\nAGGREGATOR RESUMEN")
    print(f"  binario_100        : {result['meta']['binario_100']}")
    print(f"  github.match       : {result['summaries']['github']['match']}")
    print(f"  railway.match      : {result['summaries']['railway']['match']}")
    print(f"  supabase.match     : {result['summaries']['supabase']['match']}")
    print(f"  live24h.match      : {result['summaries']['live24h']['match']}")
    print(f"  cross_findings     : {result['cross_validation']['findings_count']}")
    print(f"  atomic_map         : {result['meta']['atomic_map_version']}")
    print(f"  output             : {OUT_FILE}")
    print(f"  size               : {OUT_FILE.stat().st_size:,} bytes")

    return 0 if result["meta"]["binario_100"] else 1


if __name__ == "__main__":
    sys.exit(main())
