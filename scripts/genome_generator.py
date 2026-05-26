#!/usr/bin/env python3
"""
MONSTRUO_GENOME Generator v2.0
===============================
Genera el archivo MONSTRUO_GENOME.yaml — índice vivo, legible por IA,
que representa la totalidad del Monstruo en un solo archivo absorbible.

v2.0 — Expandido con:
  - Registro de satélites (repos adyacentes del ecosistema)
  - Metadata de ecosistema completa
  - Sección 'satellites' con health check ligero

Ejecutar: python3 scripts/genome_generator.py
Output:   MONSTRUO_GENOME.yaml (raíz del repo)

Fuentes de datos:
  1. Estructura del repo (filesystem scan)
  2. Supabase (tablas, RPCs, conteos) — via MCP o env vars
  3. Railway health endpoint
  4. Skills directory
  5. Migrations directory
  6. GitHub API (satélites del ecosistema)
"""

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Config ────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = REPO_ROOT / "MONSTRUO_GENOME.yaml"
KERNEL_DIR = REPO_ROOT / "kernel"
MIGRATIONS_DIR = REPO_ROOT / "migrations" / "sql"
SKILLS_DIR = Path("/home/ubuntu/skills")
GENOME_OUT_DIR = REPO_ROOT / "_genome_out"  # Sprint 91.7.3 fallback
RAILWAY_HEALTH_URL = "https://el-monstruo-kernel-production.up.railway.app/health"
GENOME_NOW_URL = "https://el-monstruo-kernel-production.up.railway.app/v1/genome/now"
GITHUB_OWNER = "alfredogl1804"

# ─── Satellite Registry ────────────────────────────────────────────────────────
# Satélites = repos que son productos o extensiones del Monstruo.
# Se registran manualmente aquí porque la relación es semántica, no técnica.
SATELLITES = [
    {
        "id": "like-kukulkan-tickets",
        "repo": "alfredogl1804/like-kukulkan-tickets",
        "type": "product",
        "status": "active",
        "description": "Boletería Leones de Yucatán — primer producto del Monstruo",
        "railway_url": None,  # TBD
        "supabase_project": None,  # Uses shared or own?
        "relationship": "satellite_active",
    },
    {
        "id": "el-monstruo-bot",
        "repo": "alfredogl1804/el-monstruo-bot",
        "type": "transport",
        "status": "offline",
        "description": "Telegram Bot — Transport T1 del Monstruo",
        "railway_url": "https://el-monstruo-bot-production.up.railway.app",
        "supabase_project": "xsumzuhwmivjgftsneov",  # Shared with kernel
        "relationship": "transport",
    },
    {
        "id": "el-mundo-de-tata",
        "repo": "alfredogl1804/el-mundo-de-tata",
        "type": "aspirant",
        "status": "in_development",
        "description": "Proyecto adyacente — aspira a ser satélite del Monstruo",
        "railway_url": None,
        "supabase_project": None,
        "relationship": "satellite_aspirant",
    },
    {
        "id": "forja-mcp",
        "repo": "alfredogl1804/forja-mcp",
        "type": "infrastructure",
        "status": "active",
        "description": "MCP Gateway — HTTP/SSE multiplexer para 7+ APIs",
        "railway_url": None,
        "supabase_project": None,
        "relationship": "infrastructure",
    },
    {
        "id": "el-monstruo-command-center",
        "repo": "alfredogl1804/el-monstruo-command-center",
        "type": "interface",
        "status": "active_unmapped",
        "description": "UI principal del Monstruo (Vercel, Next.js) — superficie operativa primaria",
        "railway_url": None,
        "vercel_url": None,  # TBD: confirmar dominio en Vercel
        "supabase_project": "xsumzuhwmivjgftsneov",  # Shared con kernel
        "relationship": "interface_principal",
    },
    {
        "id": "apps_la_forja",
        "repo": None,  # subsistema interno del monorepo el-monstruo
        "path": "apps/la-forja",
        "type": "subsystem",
        "status": "active_development",
        "description": "Backend Hono + Next.js. Contiene Bridge M2M Manus↔Manus en api/src/lib/manus_bridge.ts y 5 puertas canónicas en api/src/puertas/ (cowork_local, kernel_monstruo, manus_apple, manus_google, simulador)",
        "railway_url": None,
        "supabase_project": None,
        "relationship": "subsystem",
        "key_files": [
            "apps/la-forja/api/src/lib/manus_bridge.ts",
            "apps/la-forja/api/src/puertas/cowork_local.ts",
            "apps/la-forja/api/src/puertas/kernel_monstruo.ts",
            "apps/la-forja/api/src/puertas/manus_apple.ts",
            "apps/la-forja/api/src/puertas/manus_google.ts",
            "apps/la-forja/api/src/puertas/simulador.ts",
            "tools/manus_bridge.py",
        ],
    },
    {
        "id": "apps_mobile",
        "repo": None,
        "path": "apps/mobile",
        "type": "subsystem",
        "status": "active_with_drift",
        "description": "App Flutter del Monstruo — drift binario detectado en brand_dna.dart vs DSC-MO-002 (G-002 del Atlas)",
        "railway_url": None,
        "supabase_project": None,
        "relationship": "subsystem",
    },
    {
        "id": "monstruo-quantum-realm",
        "repo": None,  # vive en webdev S3, sin repo GitHub
        "webdev_origin": "s3://vida-prod-gitrepo/webdev-git/310519663226724344/Ntoi5bEXUaoi4YAZrYm5TQ",
        "type": "interface_visualization",
        "status": "active_drift_risk",
        "description": "Visualización 3D del Genoma + Catastro de IAs (R3F + Three.js). Sirve genome_visual_data.json (120 nodos) y catastro_visual_data.json (120 candidatas, 7 familias, Nano Banana Pro operable). JSONs editados manualmente — drift garantizado vs MONSTRUO_GENOME.yaml hasta que exista scripts/generate_visual_data.py.",
        "prod_url": "https://monstrrealm-ntoi5bex.manus.space",
        "supabase_project": None,
        "relationship": "interface_visualization",
        "drift_risk": "manual_json_edits",
        "data_sources_consumed": [
            "client/public/genome_visual_data.json",
            "client/public/catastro_visual_data.json",
            "client/public/genome_data.json",
        ],
    },
]


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
                        lines.append(f"{prefix}- {k}: {yaml_str(v, indent + 2)}")
                        first = False
                    else:
                        lines.append(f"{prefix}  {k}: {yaml_str(v, indent + 2)}")
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
            embriones.append(
                {
                    "id": name,
                    "path": str(f.relative_to(REPO_ROOT)),
                }
            )

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
    for match in re.finditer(r"app\.include_router\((\w+)\)", content):
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
            "manus-mcp-cli",
            "tool",
            "call",
            "execute_sql",
            "--server",
            "supabase",
            "--input",
            json.dumps({"project_id": "xsumzuhwmivjgftsneov", "query": sql}),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        # Extract JSON from the tool result
        json_match = re.search(r"\[.*?\]", output)
        if json_match:
            raw = json_match.group()
            if '\\"' in raw:
                raw = raw.replace('\\"', '"')
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                raw2 = re.sub(r'\\"', '"', json_match.group())
                try:
                    return json.loads(raw2)
                except:
                    pass
        # Try finding JSON in saved result file
        result_files = sorted(Path("/home/ubuntu/.mcp/tool-results/").glob("*supabase*"))
        if result_files:
            latest = result_files[-1]
            try:
                data = json.loads(latest.read_text())
                result_str = data.get("result", "")
                json_match2 = re.search(r"\[.*?\]", result_str)
                if json_match2:
                    return json.loads(json_match2.group())
            except:
                pass
        return []
    except Exception as e:
        print(f"  [WARN] Supabase query failed: {e}", file=sys.stderr)
        return []


def _load_genome_out_supabase() -> dict | None:
    """Sprint 91.7.3 fallback: lee _genome_out/supabase.json si existe.
    El supabase_scanner.py de Sprint 91 produce este archivo con counts reales
    cuando MCP no está disponible (entornos fuera de Manus sandbox)."""
    p = GENOME_OUT_DIR / "supabase.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def get_table_counts():
    """Get row counts for key tables. Sprint 91.7.3: fallback a _genome_out."""
    sql = """
    SELECT relname as table_name, n_live_tup as row_count
    FROM pg_stat_user_tables
    WHERE schemaname = 'public'
    ORDER BY n_live_tup DESC;
    """
    result = query_supabase(sql)
    if result:
        return result
    # Sprint 91.7.3 fallback: _genome_out/supabase.json
    sb = _load_genome_out_supabase()
    if not sb:
        return []
    out = []
    # Sprint 91.7.3 — incluir TODAS las tablas de los 17 schemas, no solo public.
    # El supabase_scanner usa keys 'table_schema' y 'table_name', con row_estimate.
    for t in sb.get("tables", []):
        schema = t.get("table_schema") or t.get("schema")
        name = t.get("table_name") or t.get("name") or ""
        if not name:
            continue
        full = f"{schema}.{name}" if schema and schema != "public" else name
        row_est = t.get("row_estimate")
        if row_est is None or row_est < 0:
            row_est = 0
        out.append({"table_name": full, "row_count": row_est})
    print(f"  [INFO] Supabase tables loaded from _genome_out: {len(out)}", file=sys.stderr)
    return out


def get_custom_rpcs():
    """Get custom RPCs (excluding pgvector/trgm internals). Sprint 91.7.3: fallback."""
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
    result = query_supabase(sql)
    if result:
        return result
    # Sprint 91.7.3 fallback: _genome_out/supabase.json
    sb = _load_genome_out_supabase()
    if not sb:
        return []
    out = []
    for f in sb.get("functions", []) or sb.get("custom_functions", []) or []:
        name = f.get("name") or f.get("proname")
        schema = f.get("schema") or "public"
        if not name:
            continue
        full = f"{schema}.{name}" if schema and schema != "public" else name
        out.append({"proname": full})
    print(f"  [INFO] Custom RPCs loaded from _genome_out: {len(out)}", file=sys.stderr)
    return out


# ─── Phase 3: Query Railway ───────────────────────────────────────────────────


def get_railway_health():
    """Get health status from Railway production."""
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "10", RAILWAY_HEALTH_URL], capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"  [WARN] Railway health check failed: {e}", file=sys.stderr)
    return None


# ─── Phase 4: Query Satellites (GitHub API) ───────────────────────────────────


def get_satellite_info(satellite):
    """Get basic info about a satellite. Tolerant a entries sin repo (subsystems internos)."""
    repo = satellite.get("repo")
    info = dict(satellite)  # Copy base info

    if repo:
        try:
            # Get last commit date and default branch via gh CLI
            result = subprocess.run(
                ["gh", "repo", "view", repo, "--json", "pushedAt,defaultBranchRef,description"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout)
                info["last_push"] = data.get("pushedAt", "unknown")
                info["github_description"] = data.get("description", "")
                branch_ref = data.get("defaultBranchRef", {})
                info["default_branch"] = branch_ref.get("name", "main") if branch_ref else "main"
        except Exception:
            info["last_push"] = "unreachable"
            info["github_description"] = ""
            info["default_branch"] = "unknown"
    else:
        # Subsystem interno (path within monorepo) o webdev sin repo
        path = satellite.get("path")
        if path:
            full_path = REPO_ROOT / path
            if full_path.exists():
                # Get last modified time of the path
                try:
                    git_log = subprocess.run(
                        ["git", "-C", str(REPO_ROOT), "log", "-1", "--format=%cI", "--", path],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    info["last_push"] = git_log.stdout.strip() or "unknown"
                except Exception:
                    info["last_push"] = "unknown"
                info["path_exists"] = True
            else:
                info["path_exists"] = False
                info["last_push"] = "path_not_found"
        else:
            info["last_push"] = "no_repo_no_path"

    # Check Railway health if URL provided
    if satellite.get("railway_url"):
        try:
            result = subprocess.run(
                ["curl", "-s", "--max-time", "5", "-o", "/dev/null", "-w", "%{http_code}", satellite["railway_url"]],
                capture_output=True,
                text=True,
                timeout=10,
            )
            http_code = result.stdout.strip()
            info["railway_status"] = "online" if http_code in ("200", "301", "302") else f"offline ({http_code})"
        except Exception:
            info["railway_status"] = "unreachable"

    # Check prod_url health if provided (webdev/vercel deploys)
    if satellite.get("prod_url"):
        try:
            result = subprocess.run(
                ["curl", "-s", "--max-time", "5", "-o", "/dev/null", "-w", "%{http_code}", satellite["prod_url"]],
                capture_output=True,
                text=True,
                timeout=10,
            )
            http_code = result.stdout.strip()
            info["prod_status"] = "online" if http_code in ("200", "301", "302") else f"offline ({http_code})"
        except Exception:
            info["prod_status"] = "unreachable"

    return info


def scan_satellites():
    """Scan all registered satellites for current status."""
    results = []
    for sat in SATELLITES:
        print(f"    Checking satellite: {sat['id']}...")
        info = get_satellite_info(sat)
        results.append(info)
    return results


# ─── Phase 5: Assemble Genome ─────────────────────────────────────────────────


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
        "memory_": "memory",
        "sovereign_": "sovereign",
        "episodic_": "memory",
        "monstruo_memory": "memory",
        "error_memory": "memory",
        "mem0": "memory",
        "mempalace_": "memory",
        "anti_dory_": "anti_dory",
        "catastro_": "catastro",
        "embrion_": "embrion",
        "forja_": "forja",
        "lightrag_": "lightrag",
        "e2e_": "e2e",
        "v5_": "v5_intelligence",
        "governance_": "governance",
        "guardian_": "governance",
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


def build_genome():
    """Assemble all data into the genome structure."""
    print("🧬 MONSTRUO GENOME Generator v2.0")
    print("=" * 50)

    # 1. Repo scan
    print("  [1/6] Scanning repo structure...")
    kernel_modules = scan_kernel_modules()
    embriones = scan_embriones()
    routes = scan_routes()
    migrations = scan_migrations()
    skills = scan_skills()
    top_dirs = scan_top_level_dirs()

    # 2. Supabase
    print("  [2/6] Querying Supabase...")
    table_counts = get_table_counts()
    custom_rpcs = get_custom_rpcs()

    # 3. Railway
    print("  [3/6] Checking Railway health...")
    railway_health = get_railway_health()

    # 4. Satellites
    print("  [4/6] Scanning satellites...")
    satellites = scan_satellites()

    # 5. Classify tables
    print("  [5/6] Classifying components...")
    table_domains = classify_tables(table_counts)

    # 6. Build YAML
    print("  [6/6] Assembling genome...")
    genome = assemble_yaml(
        kernel_modules,
        embriones,
        routes,
        migrations,
        skills,
        top_dirs,
        table_counts,
        custom_rpcs,
        railway_health,
        table_domains,
        satellites,
    )

    return genome


def assemble_yaml(
    kernel_modules,
    embriones,
    routes,
    migrations,
    skills,
    top_dirs,
    table_counts,
    custom_rpcs,
    railway_health,
    table_domains,
    satellites,
):
    """Produce the final YAML string."""

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    total_tables = len(table_counts) if table_counts else 0
    total_rpcs = len(custom_rpcs) if custom_rpcs else 0
    total_kernel_modules = len(kernel_modules)
    total_embriones = len(embriones)
    total_skills = len(skills)
    total_migrations = len(migrations)
    total_satellites = len(satellites)

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
    lines.append("# ║  Auto-generado por scripts/genome_generator.py v2.0             ║")
    lines.append("# ║  Propósito: Cualquier IA absorbe esto y sabe QUÉ hay,           ║")
    lines.append("# ║  DÓNDE está, y CÓMO se conecta — en segundos.                   ║")
    lines.append("# ╚══════════════════════════════════════════════════════════════════╝")
    lines.append("")

    # ─── META ──────────────────────────────────────────────────────────────────
    lines.append("meta:")
    lines.append(f"  generated_at: {now}")
    lines.append("  generator: scripts/genome_generator.py")
    lines.append("  version: 2.0.0")
    lines.append(f"  repo: {GITHUB_OWNER}/el-monstruo")
    lines.append(f"  total_kernel_modules: {total_kernel_modules}")
    lines.append(f"  total_embriones: {total_embriones}")
    lines.append(f"  total_supabase_tables: {total_tables}")
    lines.append(f"  total_custom_rpcs: {total_rpcs}")
    lines.append(f"  total_migrations: {total_migrations}")
    lines.append(f"  total_skills: {total_skills}")
    lines.append(f"  total_top_dirs: {len(top_dirs)}")
    lines.append(f"  total_satellites: {total_satellites}")
    # Sprint 91.7.3: referencia al Mapa Vivo como fuente operativa de verdad
    lines.append("  mapa_vivo:")
    lines.append(f"    endpoint: {GENOME_NOW_URL}")
    lines.append("    health: /v1/genome/now/health")
    lines.append("    refresh_full: 'POST /v1/genome/now?refresh=full (header X-API-Key)'")
    lines.append("    job_status: /v1/genome/now/job")
    lines.append("    fuente_canonica_de: [github_repos, railway_services, supabase_tables_fns, live24h_activity]")
    lines.append("    sprint_origen: 91 (Mapa Vivo 100 binario)")
    lines.append("")

    # ─── SATELLITES (NEW in v2.0) ──────────────────────────────────────────────
    lines.append("# ─── ECOSYSTEM: Satellites ──────────────────────────────────────────")
    lines.append("# Satélites = repos que son productos, transportes o extensiones")
    lines.append("# del Monstruo. El Genoma los registra de forma LIGERA: sabe que")
    lines.append("# existen, qué son, y su estado — sin escanear sus tripas.")
    lines.append("satellites:")
    for sat in satellites:
        lines.append(f"  - id: {sat['id']}")
        lines.append(f"    repo: {sat['repo']}")
        if sat.get("path"):
            lines.append(f"    path: {sat['path']}")
        lines.append(f"    type: {sat['type']}")
        lines.append(f"    status: {sat['status']}")
        lines.append(f"    relationship: {sat['relationship']}")
        lines.append(f"    description: {sat['description']}")
        if sat.get("last_push") and sat["last_push"] != "unreachable":
            lines.append(f"    last_push: {sat['last_push']}")
        if sat.get("railway_url"):
            lines.append(f"    railway_url: {sat['railway_url']}")
            lines.append(f"    railway_status: {sat.get('railway_status', 'unknown')}")
        if sat.get("prod_url"):
            lines.append(f"    prod_url: {sat['prod_url']}")
            lines.append(f"    prod_status: {sat.get('prod_status', 'unknown')}")
        if sat.get("vercel_url"):
            lines.append(f"    vercel_url: {sat['vercel_url']}")
        if sat.get("supabase_project"):
            lines.append(f"    supabase_project: {sat['supabase_project']}")
        if sat.get("drift_risk"):
            lines.append(f"    drift_risk: {sat['drift_risk']}")
        if sat.get("key_files"):
            lines.append("    key_files:")
            for kf in sat["key_files"]:
                lines.append(f"      - {kf}")
        if sat.get("data_sources_consumed"):
            lines.append("    data_sources_consumed:")
            for ds in sat["data_sources_consumed"]:
                lines.append(f"      - {ds}")
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
    total_py = sum(1 for _ in KERNEL_DIR.rglob("*.py")) if KERNEL_DIR.exists() else 0
    lines.append(f"  total_python_files: {total_py}")
    lines.append("  entry_point: kernel/main.py")
    lines.append("  framework: FastAPI + LangGraph")
    lines.append("  modules:")

    # Group kernel modules by functional area
    core_modules = [
        "main",
        "auth",
        "embrion_loop",
        "embrion_vigia",
        "background_store",
        "cost_optimizer",
        "adaptive_model_selector",
        "causal_decomposer",
    ]
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
            lines.append("      memory: none  # stateless — GAP")
    lines.append("  collective:")
    lines.append("    path: kernel/collective/")
    lines.append("    components: [protocol.py, knowledge_propagator.py, emergence_detector.py]")
    lines.append("    status: code_exists_but_tables_missing")
    lines.append("    tables_needed: [learned_patterns, embrion_knowledge]")
    lines.append("    note: Operates in RAM only, loses state on redeploy")
    lines.append("  domain_embriones_canon:")
    lines.append("    status: doctrine_only_no_code")
    lines.append("    defined_in: docs/conocimiento/metodologias/CANON_Metodologias_Productividad_v1_5.md")
    lines.append(
        "    items: [Archivista, Concierge, Ecónomo, Vigía-Salud, Cronista, Curador, Custodio, Compromisario, Relacionista, Cartógrafo]"
    )
    lines.append("")

    # ─── MEMORY PLANE ──────────────────────────────────────────────────────────
    lines.append("memory_plane:")
    lines.append("  sovereign_memory_system:")
    lines.append("    status: production")
    lines.append("    version: v4.0")
    lines.append("    api_mount: /sms")
    lines.append("    adapter: kernel/memory/sms_supabase_adapter.py")
    lines.append("    tables:")
    for t in [
        "sovereign_memories",
        "sovereign_axioms",
        "sovereign_agent_registry",
        "sovereign_conflict_log",
        "sovereign_consolidation_log",
        "sovereign_knowledge_gaps",
        "sovereign_causal_chains",
        "memory_entities",
        "memory_relations",
        "memory_entity_links",
        "memory_dependencies",
        "memory_access_log",
    ]:
        count = tc_map.get(t, 0)
        lines.append(f"      - name: {t}")
        lines.append(f"        records: {count}")
    lines.append("    rpcs:")
    sms_rpcs = [
        r
        for r in rpc_names
        if any(
            x in r
            for x in [
                "sovereign",
                "match_sovereign",
                "graph_enhanced",
                "cascade_invalidation",
                "compute_importance",
                "archive_low",
                "merge_similar",
                "register_dependency",
                "get_entity",
                "get_memories_for",
                "find_entity",
                "get_pending_revalidation",
                "match_memories",
            ]
        )
    ]
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
    legacy_tables = [
        "embrion_memoria",
        "monstruo_memory",
        "error_memory",
        "episodic_memory",
        "memory_events",
        "mempalace_episodes",
        "mempalace_semantic",
        "mem0",
    ]
    for t in legacy_tables:
        count = tc_map.get(t, 0)
        if count > 0:
            lines.append(f"    - table: {t}")
            lines.append(f"      records: {count}")
            lines.append("      connected_to_sms: false")
    lines.append("  anti_dory:")
    lines.append("    path: kernel/anti_dory/")
    lines.append("    tables:")
    for t in ["anti_dory_anchor_store", "anti_dory_plan_ledger", "anti_dory_runtime_flags", "anti_dory_write_budget"]:
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
        "like-kukulkan-tickets -> kernel (satellite product, future integration)",
        "forja-mcp -> kernel (MCP gateway, HTTP/SSE multiplexer)",
    ]
    for c in connections:
        lines.append(f"  - {c}")
    lines.append("")

    # ─── GAPS (known issues / missing pieces) ──────────────────────────────────
    lines.append("gaps:")
    lines.append("  critical:")
    lines.append("    - id: embrion_loop_isolated")
    lines.append("      description: Embrion Loop has memories in embrion_memoria but ZERO connection to SMS v4.0")
    lines.append("      impact: No graph, no belief revision, no decay for the main orchestrator")
    lines.append("      fix: Bridge embrion_memoria <-> sovereign_memories")
    lines.append("    - id: collective_ram_only")
    lines.append("      description: Colmena (collective/) operates in RAM, tables never created")
    lines.append("      impact: Learned patterns lost on every redeploy")
    lines.append("      fix: Create learned_patterns + embrion_knowledge tables, connect to SMS")
    lines.append("    - id: embriones_stateless")
    lines.append("      description: Domain embriones have no memory at all")
    lines.append("      impact: Cannot learn from past invocations")
    lines.append("      fix: Each embrion gets graph_enhanced_recall before operating")
    lines.append("  moderate:")
    lines.append("    - id: bot_offline")
    lines.append("      description: Telegram bot returns 404")
    lines.append("      fix: Redeploy on Railway")
    lines.append("    - id: embeddings_pending")
    lines.append("      description: Memories ingested without vector embeddings")
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
    lines.append("  sprint_history: docs/SPRINT_*.md")
    lines.append("  kit_pericia: bridge/thread_archives/ + monstruo_reality_atlas/")
    lines.append("")

    # ─── HOW TO USE THIS FILE ──────────────────────────────────────────────────
    lines.append("# ─── USAGE INSTRUCTIONS FOR AI AGENTS ─────────────────────────────")
    lines.append("# 1. Read this file FIRST when starting any task on El Monstruo")
    lines.append("# 2. Use 'satellites' to know what products/extensions exist")
    lines.append("# 3. Use 'connections' to understand how components relate")
    lines.append("# 4. Use 'gaps' to know what's broken or missing")
    lines.append("# 5. Use 'memory_plane' to understand where data lives")
    lines.append("# 6. Use 'embriones' to know what specialists exist")
    lines.append("# 7. Use 'production' to know what's actually deployed")
    lines.append("# 8. Regenerate with: python3 scripts/genome_generator.py")
    lines.append("# 9. DO NOT propose creating something that already appears here")
    lines.append("")

    return "\n".join(lines) + "\n"


# ─── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    genome_yaml = build_genome()
    OUTPUT_FILE.write_text(genome_yaml)
    print(f"\n✅ MONSTRUO_GENOME.yaml generated: {OUTPUT_FILE}")
    print(f"   Size: {len(genome_yaml)} bytes, {genome_yaml.count(chr(10))} lines")
