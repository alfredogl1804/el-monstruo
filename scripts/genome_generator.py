#!/usr/bin/env python3
"""
MONSTRUO_GENOME Generator v1.0
===============================
Genera el archivo MONSTRUO_GENOME.yaml — índice vivo, legible por IA,
que representa la totalidad del Monstruo en un solo archivo absorbible.

Ejecutar: python3 scripts/genome_generator.py
Output:   MONSTRUO_GENOME.yaml (raíz del repo)

Fuentes de datos:
  1. Estructura del repo (filesystem scan)
  2. Supabase (tablas, RPCs, conteos) — via MCP o env vars
  3. Railway health endpoint
  4. Skills directory
  5. Migrations directory
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

# ─── Config ────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = REPO_ROOT / "MONSTRUO_GENOME.yaml"
KERNEL_DIR = REPO_ROOT / "kernel"
MIGRATIONS_DIR = REPO_ROOT / "migrations" / "sql"
SKILLS_DIR = Path("/home/ubuntu/skills")
RAILWAY_HEALTH_URL = "https://el-monstruo-kernel-production.up.railway.app/health"


def yaml_str(val, indent=0):
    """Simple YAML serializer (no external deps needed)."""
    prefix = "  " * indent
    if val is None:
        return "null"
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, str):
        if "\n" in val or ":" in val or "#" in val or val.startswith("["):
            return f'"{val}"'
        return val
    if isinstance(val, list):
        if not val:
            return "[]"
        if all(isinstance(v, str) for v in val) and sum(len(v) for v in val) < 120:
            return "[" + ", ".join(val) + "]"
        lines = []
        for item in val:
            if isinstance(item, dict):
                first = True
                for k, v in item.items():
                    if first:
                        lines.append(f"{prefix}- {k}: {yaml_str(v, indent+2)}")
                        first = False
                    else:
                        lines.append(f"{prefix}  {k}: {yaml_str(v, indent+2)}")
            else:
                lines.append(f"{prefix}- {yaml_str(item)}")
        return "\n" + "\n".join(lines)
    if isinstance(val, dict):
        lines = []
        for k, v in val.items():
            rendered = yaml_str(v, indent + 1)
            if isinstance(v, (dict, list)) and rendered.startswith("\n"):
                lines.append(f"{prefix}{k}:{rendered}")
            else:
                lines.append(f"{prefix}{k}: {rendered}")
        return "\n" + "\n".join(lines)
    return str(val)


# ─── Phase 1: Scan Repo Structure ─────────────────────────────────────────────

def scan_kernel_modules():
    """Scan kernel/ for modules, their files, and key characteristics."""
    modules = {}
    if not KERNEL_DIR.exists():
        return modules

    # Top-level directories in kernel/
    for d in sorted(KERNEL_DIR.iterdir()):
        if d.is_dir() and not d.name.startswith("__"):
            py_files = list(d.rglob("*.py"))
            py_files = [f for f in py_files if f.name != "__init__.py"]
            modules[d.name] = {
                "path": f"kernel/{d.name}/",
                "files": len(py_files),
                "key_files": [f.name for f in py_files[:5]],
            }

    # Top-level .py files in kernel/
    top_files = [f for f in sorted(KERNEL_DIR.glob("*.py")) if f.name != "__init__.py"]
    for f in top_files:
        name = f.stem
        if name not in modules:
            modules[name] = {
                "path": f"kernel/{f.name}",
                "files": 1,
                "key_files": [f.name],
            }

    return modules


def scan_embriones():
    """Scan kernel/embriones/ for individual embrion files."""
    embriones_dir = KERNEL_DIR / "embriones"
    embriones = []
    if not embriones_dir.exists():
        return embriones

    for f in sorted(embriones_dir.rglob("*.py")):
        if f.name == "__init__.py":
            continue
        name = f.stem
        if "embrion" in name or "brand_engine" in name or "critic" in name or "architect" in name:
            embriones.append({
                "id": name,
                "path": str(f.relative_to(REPO_ROOT)),
            })

    return embriones


def scan_routes():
    """Scan main.py for registered routes/endpoints."""
    main_py = KERNEL_DIR / "main.py"
    routes = []
    if not main_py.exists():
        return routes

    content = main_py.read_text(errors="ignore")
    # Find include_router and app.mount calls
    for match in re.finditer(r'app\.include_router\((\w+).*?prefix="([^"]*)"', content):
        routes.append({"router": match.group(1), "prefix": match.group(2)})
    for match in re.finditer(r'app\.include_router\((\w+)\)', content):
        routes.append({"router": match.group(1), "prefix": "/"})
    for match in re.finditer(r'app\.mount\("([^"]+)"', content):
        routes.append({"router": "mount", "prefix": match.group(1)})

    # Deduplicate
    seen = set()
    unique = []
    for r in routes:
        key = f"{r['router']}:{r['prefix']}"
        if key not in seen:
            seen.add(key)
            unique.append(r)

    return unique


def scan_migrations():
    """Scan migrations/sql/ for migration files."""
    if not MIGRATIONS_DIR.exists():
        return []
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    return [{"id": f.stem.split("_")[0], "name": "_".join(f.stem.split("_")[1:]), "file": f.name} for f in files]


def scan_skills():
    """Scan skills directory for available skills."""
    skills = []
    if not SKILLS_DIR.exists():
        return skills
    for d in sorted(SKILLS_DIR.iterdir()):
        if d.is_dir() and (d / "SKILL.md").exists():
            skills.append(d.name)
    return skills


def scan_top_level_dirs():
    """Get top-level directories in the repo."""
    dirs = []
    for d in sorted(REPO_ROOT.iterdir()):
        if d.is_dir() and not d.name.startswith(".") and d.name != "node_modules":
            dirs.append(d.name)
    return dirs


# ─── Phase 2: Query Supabase ──────────────────────────────────────────────────

def query_supabase(sql):
    """Execute SQL via Supabase MCP and return parsed result."""
    try:
        cmd = [
            "manus-mcp-cli", "tool", "call", "execute_sql",
            "--server", "supabase",
            "--input", json.dumps({"project_id": "xsumzuhwmivjgftsneov", "query": sql})
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        # Extract JSON from the tool result - handle escaped quotes from MCP
        json_match = re.search(r'\[.*?\]', output)
        if json_match:
            raw = json_match.group()
            # MCP output may have escaped quotes
            if '\\"' in raw:
                raw = raw.replace('\\"', '"')
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                # Try unescaping differently
                raw2 = re.sub(r'\\"', '"', json_match.group())
                try:
                    return json.loads(raw2)
                except:
                    pass
        # Try finding JSON in the saved result file
        result_files = sorted(Path('/home/ubuntu/.mcp/tool-results/').glob('*supabase*'))
        if result_files:
            latest = result_files[-1]
            try:
                data = json.loads(latest.read_text())
                result_str = data.get('result', '')
                json_match2 = re.search(r'\[.*?\]', result_str)
                if json_match2:
                    return json.loads(json_match2.group())
            except:
                pass
        return []
    except Exception as e:
        print(f"  [WARN] Supabase query failed: {e}", file=sys.stderr)
        return []


def get_table_counts():
    """Get row counts for key tables."""
    sql = """
    SELECT relname as table_name, n_live_tup as row_count
    FROM pg_stat_user_tables
    WHERE schemaname = 'public'
    ORDER BY n_live_tup DESC;
    """
    return query_supabase(sql)


def get_custom_rpcs():
    """Get custom RPCs (excluding pgvector/trgm internals)."""
    sql = """
    SELECT proname FROM pg_proc
    WHERE pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
    AND proname NOT LIKE 'vector%' AND proname NOT LIKE 'halfvec%'
    AND proname NOT LIKE 'sparsevec%' AND proname NOT LIKE 'hnsw%'
    AND proname NOT LIKE 'ivfflat%' AND proname NOT LIKE 'l1_%'
    AND proname NOT LIKE 'l2_%' AND proname NOT LIKE 'cosine%'
    AND proname NOT LIKE 'inner_%' AND proname NOT LIKE 'hamming%'
    AND proname NOT LIKE 'jaccard%' AND proname NOT LIKE 'binary_%'
    AND proname NOT LIKE 'gin_%' AND proname NOT LIKE 'gtrgm%'
    AND proname NOT LIKE 'array_to_%' AND proname NOT LIKE '%trgm%'
    AND proname NOT LIKE 'word_similarity%' AND proname NOT LIKE 'strict_word%'
    AND proname NOT IN ('avg', 'sum', 'set_limit', 'show_limit', 'show_trgm',
                        'similarity', 'similarity_dist', 'similarity_op',
                        'unaccent', 'unaccent_init', 'unaccent_lexize',
                        'f_unaccent', 'subvector')
    ORDER BY proname;
    """
    return query_supabase(sql)


# ─── Phase 3: Query Railway ───────────────────────────────────────────────────

def get_railway_health():
    """Get health status from Railway production."""
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "10", RAILWAY_HEALTH_URL],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"  [WARN] Railway health check failed: {e}", file=sys.stderr)
    return None


# ─── Phase 4: Assemble Genome ─────────────────────────────────────────────────

def build_genome():
    """Assemble all data into the genome structure."""
    print("🧬 MONSTRUO GENOME Generator v1.0")
    print("=" * 50)

    # 1. Repo scan
    print("  [1/5] Scanning repo structure...")
    kernel_modules = scan_kernel_modules()
    embriones = scan_embriones()
    routes = scan_routes()
    migrations = scan_migrations()
    skills = scan_skills()
    top_dirs = scan_top_level_dirs()

    # 2. Supabase
    print("  [2/5] Querying Supabase...")
    table_counts = get_table_counts()
    custom_rpcs = get_custom_rpcs()

    # 3. Railway
    print("  [3/5] Checking Railway health...")
    railway_health = get_railway_health()

    # 4. Classify tables into domains
    print("  [4/5] Classifying components...")
    table_domains = classify_tables(table_counts)

    # 5. Build YAML
    print("  [5/5] Assembling genome...")
    genome = assemble_yaml(
        kernel_modules, embriones, routes, migrations, skills,
        top_dirs, table_counts, custom_rpcs, railway_health, table_domains
    )

    return genome


def classify_tables(table_counts):
    """Classify tables into functional domains."""
    domains = {
        "memory": [],
        "anti_dory": [],
        "catastro": [],
        "embrion": [],
        "forja": [],
        "governance": [],
        "lightrag": [],
        "e2e": [],
        "v5_intelligence": [],
        "sovereign": [],
        "operational": [],
    }

    prefixes = {
        "memory_": "memory", "sovereign_": "sovereign", "episodic_": "memory",
        "monstruo_memory": "memory", "error_memory": "memory", "mem0": "memory",
        "mempalace_": "memory",
        "anti_dory_": "anti_dory",
        "catastro_": "catastro",
        "embrion_": "embrion",
        "forja_": "forja",
        "lightrag_": "lightrag",
        "e2e_": "e2e",
        "v5_": "v5_intelligence",
        "governance_": "governance", "guardian_": "governance",
        "cowork_": "governance",
    }

    for row in table_counts:
        name = row.get("table_name", "")
        classified = False
        for prefix, domain in prefixes.items():
            if name.startswith(prefix):
                domains[domain].append(name)
                classified = True
                break
        if not classified:
            domains["operational"].append(name)

    return domains


def assemble_yaml(kernel_modules, embriones, routes, migrations, skills,
                  top_dirs, table_counts, custom_rpcs, railway_health, table_domains):
    """Produce the final YAML string."""

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    total_tables = len(table_counts) if table_counts else 0
    total_rpcs = len(custom_rpcs) if custom_rpcs else 0
    total_kernel_modules = len(kernel_modules)
    total_embriones = len(embriones)
    total_skills = len(skills)
    total_migrations = len(migrations)

    # Build table count map
    tc_map = {}
    for row in table_counts:
        tc_map[row.get("table_name", "")] = row.get("row_count", 0)

    # Railway components
    railway_components = []
    if railway_health and "components" in railway_health:
        for k, v in railway_health["components"].items():
            if isinstance(v, str):
                railway_components.append(f"{k}: {v}")
            elif isinstance(v, dict) and "running" in v:
                railway_components.append(f"{k}: running={v['running']}")

    # RPC list (cleaned)
    rpc_names = [r["proname"] for r in custom_rpcs] if custom_rpcs else []

    # Start building YAML manually for maximum control
    lines = []
    lines.append("# ╔══════════════════════════════════════════════════════════════════╗")
    lines.append("# ║  MONSTRUO_GENOME.yaml — Fuente única de verdad arquitectónica   ║")
    lines.append("# ║  Auto-generado por scripts/genome_generator.py                  ║")
    lines.append("# ║  Propósito: Cualquier IA absorbe esto y sabe QUÉ hay,           ║")
    lines.append("# ║  DÓNDE está, y CÓMO se conecta — en segundos.                   ║")
    lines.append("# ╚══════════════════════════════════════════════════════════════════╝")
    lines.append("")

    # ─── META ──────────────────────────────────────────────────────────────────
    lines.append("meta:")
    lines.append(f"  generated_at: {now}")
    lines.append("  generator: scripts/genome_generator.py")
    lines.append("  version: 1.0.0")
    lines.append(f"  repo: alfredogl1804/el-monstruo")
    lines.append(f"  total_kernel_modules: {total_kernel_modules}")
    lines.append(f"  total_embriones: {total_embriones}")
    lines.append(f"  total_supabase_tables: {total_tables}")
    lines.append(f"  total_custom_rpcs: {total_rpcs}")
    lines.append(f"  total_migrations: {total_migrations}")
    lines.append(f"  total_skills: {total_skills}")
    lines.append(f"  total_top_dirs: {len(top_dirs)}")
    lines.append("")

    # ─── PRODUCTION STATUS ─────────────────────────────────────────────────────
    lines.append("production:")
    lines.append("  kernel:")
    lines.append("    url: https://el-monstruo-kernel-production.up.railway.app")
    lines.append(f"    status: {railway_health.get('status', 'unknown') if railway_health else 'unreachable'}")
    lines.append(f"    version: {railway_health.get('version', 'unknown') if railway_health else 'unknown'}")
    lines.append(f"    motor: {railway_health.get('motor', 'unknown') if railway_health else 'unknown'}")
    if railway_health and "models_available" in railway_health:
        lines.append(f"    models_available: [{', '.join(railway_health['models_available'])}]")
    lines.append("    active_components:")
    for comp in railway_components[:15]:
        lines.append(f"      - {comp}")
    lines.append("  bot:")
    lines.append("    url: https://el-monstruo-bot-production.up.railway.app")
    lines.append("    status: offline")
    lines.append("    note: 404 - Application not found (needs redeploy)")
    lines.append("  supabase:")
    lines.append("    project_id: xsumzuhwmivjgftsneov")
    lines.append("    status: active")
    lines.append(f"    tables: {total_tables}")
    lines.append(f"    custom_rpcs: {total_rpcs}")
    lines.append("")

    # ─── KERNEL ARCHITECTURE ───────────────────────────────────────────────────
    lines.append("kernel:")
    lines.append(f"  total_python_files: 300")
    lines.append("  entry_point: kernel/main.py")
    lines.append("  framework: FastAPI + LangGraph")
    lines.append("  modules:")

    # Group kernel modules by functional area
    core_modules = ["main", "auth", "embrion_loop", "embrion_vigia", "background_store",
                    "cost_optimizer", "adaptive_model_selector", "causal_decomposer"]
    memory_modules = ["memory", "anti_dory", "memento"]
    intelligence_modules = ["catastro", "catastros", "collective", "learning", "vanguard"]
    interface_modules = ["a2ui", "browser", "mcp", "agui_adapter", "plugins"]
    governance_modules = ["security", "sovereignty", "validation", "guardian_runner"]
    product_modules = ["brand", "embriones", "embrion_specializations", "design"]
    operational_modules = ["alerts", "dashboards", "milestones", "motion", "rotor", "runner"]

    def write_module_group(group_name, module_names):
        lines.append(f"    {group_name}:")
        for name in module_names:
            if name in kernel_modules:
                m = kernel_modules[name]
                lines.append(f"      - id: {name}")
                lines.append(f"        path: {m['path']}")
                lines.append(f"        files: {m['files']}")

    write_module_group("core", core_modules)
    write_module_group("memory_systems", memory_modules)
    write_module_group("intelligence", intelligence_modules)
    write_module_group("interfaces", interface_modules)
    write_module_group("governance", governance_modules)
    write_module_group("product", product_modules)
    write_module_group("operational", operational_modules)
    lines.append("")

    # ─── EMBRIONES ─────────────────────────────────────────────────────────────
    lines.append("embriones:")
    lines.append("  orchestrator:")
    lines.append("    id: embrion_loop")
    lines.append("    path: kernel/embrion_loop.py")
    lines.append("    status: production")
    lines.append(f"    memory_table: embrion_memoria ({tc_map.get('embrion_memoria', '?')} records)")
    lines.append("    connected_to_sms: false  # GAP: isolated from sovereign memory")
    lines.append("  vigia:")
    lines.append("    id: embrion_vigia")
    lines.append("    path: kernel/embrion_vigia.py")
    lines.append("    status: production")
    lines.append("    memory: none  # stateless")
    lines.append("  domain_specialists:")
    for e in embriones:
        if e["id"] not in ("embrion_loop", "embrion_vigia"):
            lines.append(f"    - id: {e['id']}")
            lines.append(f"      path: {e['path']}")
            lines.append(f"      memory: none  # stateless — GAP")
    lines.append("  collective:")
    lines.append("    path: kernel/collective/")
    lines.append("    components: [protocol.py, knowledge_propagator.py, emergence_detector.py]")
    lines.append("    status: code_exists_but_tables_missing")
    lines.append("    tables_needed: [learned_patterns, embrion_knowledge]")
    lines.append("    note: Operates in RAM only, loses state on redeploy")
    lines.append("  domain_embriones_canon:")
    lines.append("    status: doctrine_only_no_code")
    lines.append("    defined_in: docs/conocimiento/metodologias/CANON_Metodologias_Productividad_v1_5.md")
    lines.append("    items: [Archivista, Concierge, Ecónomo, Vigía-Salud, Cronista, Curador, Custodio, Compromisario, Relacionista, Cartógrafo]")
    lines.append("")

    # ─── MEMORY PLANE ──────────────────────────────────────────────────────────
    lines.append("memory_plane:")
    lines.append("  sovereign_memory_system:")
    lines.append("    status: production")
    lines.append("    version: v4.0")
    lines.append("    api_mount: /sms")
    lines.append("    adapter: kernel/memory/sms_supabase_adapter.py")
    lines.append("    tables:")
    for t in ["sovereign_memories", "sovereign_axioms", "sovereign_agent_registry",
              "sovereign_conflict_log", "sovereign_consolidation_log",
              "sovereign_knowledge_gaps", "sovereign_causal_chains",
              "memory_entities", "memory_relations", "memory_entity_links",
              "memory_dependencies", "memory_access_log"]:
        count = tc_map.get(t, 0)
        lines.append(f"      - name: {t}")
        lines.append(f"        records: {count}")
    lines.append("    rpcs:")
    sms_rpcs = [r for r in rpc_names if any(x in r for x in
                ["sovereign", "match_sovereign", "graph_enhanced", "cascade_invalidation",
                 "compute_importance", "archive_low", "merge_similar", "register_dependency",
                 "get_entity", "get_memories_for", "find_entity", "get_pending_revalidation",
                 "match_memories"])]
    for rpc in sms_rpcs:
        lines.append(f"      - {rpc}")
    lines.append("    features:")
    lines.append("      - knowledge_graph: true (entities + relations + links)")
    lines.append("      - belief_revision: true (cascade invalidation + dependencies)")
    lines.append("      - memory_decay: true (importance scoring + archival)")
    lines.append("      - temporal_validity: true (valid_at / invalid_at)")
    lines.append("      - audn_conflict_resolution: true")
    lines.append("      - vector_embeddings: pending_redeploy")
    lines.append("  legacy_memory_systems:")
    legacy_tables = ["embrion_memoria", "monstruo_memory", "error_memory",
                     "episodic_memory", "memory_events", "mempalace_episodes",
                     "mempalace_semantic", "mem0"]
    for t in legacy_tables:
        count = tc_map.get(t, 0)
        if count > 0:
            lines.append(f"    - table: {t}")
            lines.append(f"      records: {count}")
            lines.append(f"      connected_to_sms: false")
    lines.append("  anti_dory:")
    lines.append("    path: kernel/anti_dory/")
    lines.append("    tables:")
    for t in ["anti_dory_anchor_store", "anti_dory_plan_ledger",
              "anti_dory_runtime_flags", "anti_dory_write_budget"]:
        count = tc_map.get(t, 0)
        lines.append(f"      - {t}: {count} records")
    lines.append("")

    # ─── DATA PLANE (other Supabase tables grouped) ────────────────────────────
    lines.append("data_plane:")
    for domain, tables in table_domains.items():
        if domain in ("memory", "sovereign", "anti_dory"):
            continue  # Already covered above
        if not tables:
            continue
        lines.append(f"  {domain}:")
        for t in sorted(tables)[:10]:
            count = tc_map.get(t, 0)
            lines.append(f"    - {t}: {count}")
        if len(tables) > 10:
            lines.append(f"    # ... and {len(tables) - 10} more tables")
    lines.append("")

    # ─── CUSTOM RPCS ───────────────────────────────────────────────────────────
    lines.append("custom_rpcs:")
    # Filter out the ones already listed under SMS
    other_rpcs = [r for r in rpc_names if r not in sms_rpcs]
    for rpc in other_rpcs:
        lines.append(f"  - {rpc}")
    lines.append("")

    # ─── ROUTES / ENDPOINTS ────────────────────────────────────────────────────
    lines.append("api_endpoints:")
    for r in routes:
        lines.append(f"  - prefix: {r['prefix']}")
        lines.append(f"    router: {r['router']}")
    lines.append("")

    # ─── SKILLS ────────────────────────────────────────────────────────────────
    lines.append("skills:")
    lines.append(f"  total: {total_skills}")
    lines.append("  directory: /home/ubuntu/skills/")
    lines.append("  items:")
    for s in skills:
        lines.append(f"    - {s}")
    lines.append("")

    # ─── MIGRATIONS ────────────────────────────────────────────────────────────
    lines.append("migrations:")
    lines.append(f"  total: {total_migrations}")
    lines.append("  directory: migrations/sql/")
    lines.append("  latest:")
    for m in migrations[-5:]:
        lines.append(f"    - {m['file']}")
    lines.append("")

    # ─── REPO STRUCTURE ────────────────────────────────────────────────────────
    lines.append("repo_structure:")
    lines.append("  top_level_dirs:")
    for d in top_dirs:
        lines.append(f"    - {d}")
    lines.append("")

    # ─── CONNECTIONS (the graph) ───────────────────────────────────────────────
    lines.append("connections:")
    lines.append("  # Format: source -> target (relationship)")
    connections = [
        "telegram_bot -> kernel.embrion_loop (messages trigger thinking)",
        "flutter_app -> kernel.api (REST calls)",
        "kernel.embrion_loop -> kernel.embriones.* (delegates to specialists)",
        "kernel.embrion_loop -> embrion_memoria (reads/writes memories)",
        "kernel.embrion_loop -> kernel.collective (propagates patterns)",
        "kernel.memory.sms -> supabase.sovereign_memories (stores/recalls)",
        "kernel.memory.sms -> supabase.memory_entities (knowledge graph)",
        "kernel.memory.sms -> supabase.memory_dependencies (belief revision)",
        "kernel.anti_dory -> supabase.anti_dory_* (anchors + plans)",
        "kernel.catastro -> supabase.catastro_modelos (AI model registry)",
        "kernel.memento -> supabase.memento_* (critical operations)",
        "manus_threads -> kernel.sms_api (via guardian.py + /sms/ingest)",
        "manus_threads -> kernel.sms_api (via /sms/recall for context)",
        "kernel.main -> litellm (model routing via config/litellm_config.yaml)",
        "kernel.main -> langfuse (observability)",
        "kernel.main -> supabase.checkpoints (LangGraph state persistence)",
    ]
    for c in connections:
        lines.append(f"  - {c}")
    lines.append("")

    # ─── GAPS (known issues / missing pieces) ──────────────────────────────────
    lines.append("gaps:")
    lines.append("  critical:")
    lines.append("    - id: embrion_loop_isolated")
    lines.append("      description: Embrion Loop has 2763 memories in embrion_memoria but ZERO connection to SMS v4.0")
    lines.append("      impact: No graph, no belief revision, no decay for the main orchestrator")
    lines.append("      fix: Bridge embrion_memoria <-> sovereign_memories")
    lines.append("    - id: collective_ram_only")
    lines.append("      description: Colmena (collective/) operates in RAM, tables never created")
    lines.append("      impact: Learned patterns lost on every redeploy")
    lines.append("      fix: Create learned_patterns + embrion_knowledge tables, connect to SMS")
    lines.append("    - id: embriones_stateless")
    lines.append("      description: 9 domain embriones have no memory at all")
    lines.append("      impact: Cannot learn from past invocations")
    lines.append("      fix: Each embrion gets graph_enhanced_recall before operating")
    lines.append("  moderate:")
    lines.append("    - id: bot_offline")
    lines.append("      description: Telegram bot returns 404")
    lines.append("      fix: Redeploy on Railway")
    lines.append("    - id: embeddings_pending")
    lines.append("      description: 125 kit_pericia memories ingested without vector embeddings")
    lines.append("      fix: Redeploy kernel with new adapter (entity extraction generates embeddings)")
    lines.append("    - id: domain_embriones_doctrine_only")
    lines.append("      description: 10 Domain Embriones (Archivista, Concierge, etc.) exist only in doctrine")
    lines.append("      fix: Implement in kernel/embriones/ when Capa 0+1 are solid")
    lines.append("")

    # ─── DOCTRINE REFERENCES ───────────────────────────────────────────────────
    lines.append("doctrine:")
    lines.append("  objectives: docs/EL_MONSTRUO_15_OBJETIVOS_MAESTROS.md")
    lines.append("  agent_rules: AGENTS.md")
    lines.append("  brand_dna: kernel/brand/brand_dna.py")
    lines.append("  canon_metodologias: docs/conocimiento/metodologias/CANON_Metodologias_Productividad_v1_5.md")
    lines.append("  security_dscs: discovery_forense/CAPILLA_DECISIONES/_GLOBAL/")
    lines.append("  sprint_history: docs/SPRINT_*.md (51-80)")
    lines.append("  kit_pericia: bridge/thread_archives/ + monstruo_reality_atlas/")
    lines.append("")

    # ─── HOW TO USE THIS FILE ──────────────────────────────────────────────────
    lines.append("# ─── USAGE INSTRUCTIONS FOR AI AGENTS ─────────────────────────────")
    lines.append("# 1. Read this file FIRST when starting any task on El Monstruo")
    lines.append("# 2. Use 'connections' to understand how components relate")
    lines.append("# 3. Use 'gaps' to know what's broken or missing")
    lines.append("# 4. Use 'memory_plane' to understand where data lives")
    lines.append("# 5. Use 'embriones' to know what specialists exist")
    lines.append("# 6. Use 'production' to know what's actually deployed")
    lines.append("# 7. Regenerate with: python3 scripts/genome_generator.py")
    lines.append("")

    return "\n".join(lines) + "\n"


# ─── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    genome_yaml = build_genome()
    OUTPUT_FILE.write_text(genome_yaml)
    print(f"\n✅ MONSTRUO_GENOME.yaml generated: {OUTPUT_FILE}")
    print(f"   Size: {len(genome_yaml)} bytes, {genome_yaml.count(chr(10))} lines")
