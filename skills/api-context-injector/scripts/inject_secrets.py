#!/usr/bin/env python3.11
"""
inject_secrets.py v3.1 — Motor automatizado de inyección de secrets.

Flujo completo:
1. Detecta scaffold del proyecto (web-static, web-db-user, mobile-app, custom)
2. Lee manifiesto del proyecto (qué APIs necesita)
3. Resuelve secrets desde env vars del sandbox + Notion DB
4. Valida seguridad (bloquea inyección en frontend/estático)
5. Push a destinos: sandbox local, Vercel, Cloudflare Workers, Supabase Vault
6. Genera reporte de inyección

Uso:
    python3.11 inject_secrets.py --project /path/to/project [--target sandbox|vercel|cloudflare|supabase] [--dry-run] [--manifest manifest.yaml]
    python3.11 inject_secrets.py --generate-manifest /path/to/project   # Auto-genera manifiesto
    python3.11 inject_secrets.py --audit /path/to/project               # Audita secrets actuales
"""

import os
import re
import sys
import yaml
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# ============================================================
# CONSTANTS
# ============================================================

SKILL_DIR = Path(__file__).parent.parent
REFERENCES_DIR = SKILL_DIR / "references"
ROUTING_DIR = SKILL_DIR / "routing"

# Scaffold detection patterns
SCAFFOLD_SIGNATURES = {
    "web-static": {
        "files": ["vite.config.ts", "tailwind.config.ts", "index.html"],
        "absent": ["drizzle.config.ts", "server/"],
        "type": "frontend_only",
        "secret_injection": "BLOCKED",
        "reason": "Sitio estático expone todo al browser. Secrets irían al cliente."
    },
    "web-db-user": {
        "files": ["vite.config.ts", "drizzle.config.ts", "server/"],
        "absent": [],
        "type": "fullstack",
        "secret_injection": "BACKEND_ONLY",
        "reason": "Secrets solo en server/, NUNCA en src/ o public/"
    },
    "mobile-app": {
        "files": ["app.json", "expo", "metro.config.js"],
        "absent": [],
        "type": "mobile",
        "secret_injection": "BACKEND_ONLY",
        "reason": "Secrets solo en backend/API, nunca embebidos en app bundle"
    },
    "cloudflare-worker": {
        "files": ["wrangler.toml", "wrangler.jsonc"],
        "absent": [],
        "type": "edge",
        "secret_injection": "WRANGLER_SECRETS",
        "reason": "Secrets via wrangler secret put o API"
    },
    "next-vercel": {
        "files": ["next.config.js", "vercel.json", ".vercel/"],
        "absent": [],
        "type": "fullstack",
        "secret_injection": "VERCEL_ENV",
        "reason": "Secrets via Vercel env vars (MCP o CLI)"
    },
    "custom": {
        "files": [],
        "absent": [],
        "type": "unknown",
        "secret_injection": "MANUAL_REVIEW",
        "reason": "Scaffold no reconocido. Requiere revisión manual."
    }
}

# Known env vars in sandbox
SANDBOX_ENV_VARS = {
    "OPENAI_API_KEY": {"service": "OpenAI", "category": "llm"},
    "OPENAI_API_BASE": {"service": "OpenAI", "category": "llm"},
    "ANTHROPIC_API_KEY": {"service": "Anthropic", "category": "llm"},
    "GEMINI_API_KEY": {"service": "Google Gemini", "category": "llm"},
    "XAI_API_KEY": {"service": "Grok/xAI", "category": "llm"},
    "SONAR_API_KEY": {"service": "Perplexity", "category": "llm"},
    "OPENROUTER_API_KEY": {"service": "OpenRouter", "category": "llm"},
    "HEYGEN_API_KEY": {"service": "HeyGen", "category": "media"},
    "ELEVENLABS_API_KEY": {"service": "ElevenLabs", "category": "media"},
    "CLOUDFLARE_API_TOKEN": {"service": "Cloudflare", "category": "infra"},
    "DROPBOX_API_KEY": {"service": "Dropbox", "category": "storage"},
}

# Notion DB for additional credentials
NOTION_CREDENTIALS_DB = "collection://d94369d5-5dc3-437e-b483-fa86a5e98b74"

# Security: files/dirs where secrets must NEVER appear
FORBIDDEN_SECRET_LOCATIONS = [
    "src/", "public/", "static/", "dist/", "build/",
    "*.html", "*.css", "*.jsx", "*.tsx",  # frontend files
    "README.md", "package.json",  # public files
]

# Security: files/dirs where secrets ARE allowed
ALLOWED_SECRET_LOCATIONS = [
    ".env", ".env.local", ".env.production",
    "server/", "api/", "backend/", "functions/",
    "wrangler.toml",  # only for [vars], not secrets
]


# ============================================================
# SCAFFOLD DETECTION
# ============================================================

def detect_scaffold(project_path: Path) -> dict:
    """Detecta el tipo de scaffold del proyecto."""
    project_path = Path(project_path)
    if not project_path.exists():
        return {"scaffold": "not_found", "error": f"Ruta no existe: {project_path}"}

    for scaffold_name, signature in SCAFFOLD_SIGNATURES.items():
        if scaffold_name == "custom":
            continue

        # Check required files exist
        required_found = all(
            any(project_path.rglob(f)) if "*" not in f else (project_path / f).exists()
            for f in signature["files"]
        ) if signature["files"] else False

        # Check absent files don't exist
        absent_ok = all(
            not any(project_path.rglob(f))
            for f in signature["absent"]
        ) if signature["absent"] else True

        if required_found and absent_ok:
            return {
                "scaffold": scaffold_name,
                "type": signature["type"],
                "secret_injection": signature["secret_injection"],
                "reason": signature["reason"],
                "project_path": str(project_path),
            }

    return {
        "scaffold": "custom",
        "type": "unknown",
        "secret_injection": "MANUAL_REVIEW",
        "reason": SCAFFOLD_SIGNATURES["custom"]["reason"],
        "project_path": str(project_path),
    }


# ============================================================
# MANIFEST MANAGEMENT
# ============================================================

def load_manifest(manifest_path: Path) -> dict:
    """Carga el manifiesto de secrets del proyecto."""
    if not manifest_path.exists():
        return None
    with open(manifest_path, 'r') as f:
        return yaml.safe_load(f)


def generate_manifest(project_path: Path) -> dict:
    """Auto-genera un manifiesto analizando el código del proyecto."""
    project_path = Path(project_path)
    scaffold = detect_scaffold(project_path)

    # Scan code for env var references
    env_refs_found = set()
    api_imports_found = set()

    # Patterns to detect API usage in code
    env_patterns = [
        r'process\.env\.(\w+)',           # Node.js
        r'os\.environ\[[\'"]([\w]+)',     # Python
        r'os\.environ\.get\([\'"]([\w]+)',# Python
        r'import\.meta\.env\.(\w+)',      # Vite
        r'Deno\.env\.get\([\'"]([\w]+)',  # Deno
    ]

    import_patterns = {
        r'from openai': "OPENAI_API_KEY",
        r'import openai': "OPENAI_API_KEY",
        r'from anthropic': "ANTHROPIC_API_KEY",
        r'import anthropic': "ANTHROPIC_API_KEY",
        r'from elevenlabs': "ELEVENLABS_API_KEY",
        r'import elevenlabs': "ELEVENLABS_API_KEY",
        r'from google.*genai': "GEMINI_API_KEY",
        r'heygen': "HEYGEN_API_KEY",
        r'perplexity': "SONAR_API_KEY",
        r'openrouter': "OPENROUTER_API_KEY",
        r'cloudflare': "CLOUDFLARE_API_TOKEN",
        r'dropbox': "DROPBOX_API_KEY",
        r'supabase': "SUPABASE_URL",
        r'stripe': "STRIPE_SECRET_KEY",
        r'paypal': "PAYPAL_CLIENT_SECRET",
    }

    # Scan all source files
    for ext in ["*.py", "*.ts", "*.tsx", "*.js", "*.jsx", "*.mjs", "*.env*"]:
        for filepath in project_path.rglob(ext):
            if "node_modules" in str(filepath) or ".next" in str(filepath):
                continue
            try:
                content = filepath.read_text(encoding='utf-8', errors='ignore')
                # Find env var references
                for pattern in env_patterns:
                    matches = re.findall(pattern, content)
                    env_refs_found.update(matches)
                # Find API import patterns
                for pattern, env_var in import_patterns.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        api_imports_found.add(env_var)
            except Exception:
                pass

    # Combine findings
    all_needed = env_refs_found | api_imports_found

    # Build manifest
    secrets = {}
    for env_var in sorted(all_needed):
        source = "sandbox_env"
        available = bool(os.environ.get(env_var))
        if not available:
            source = "notion_db"
            available = None  # Unknown, needs Notion lookup

        # Determine if it's a known var
        info = SANDBOX_ENV_VARS.get(env_var, {"service": "Unknown", "category": "unknown"})

        secrets[env_var] = {
            "service": info["service"],
            "category": info["category"],
            "source": source,
            "available_in_sandbox": available,
            "required": True,
        }

    manifest = {
        "version": "1.0",
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "project": {
            "path": str(project_path),
            "scaffold": scaffold["scaffold"],
            "type": scaffold["type"],
            "injection_mode": scaffold["secret_injection"],
        },
        "secrets": secrets,
        "security": {
            "forbidden_locations": FORBIDDEN_SECRET_LOCATIONS,
            "allowed_locations": ALLOWED_SECRET_LOCATIONS,
        }
    }

    return manifest


def save_manifest(manifest: dict, output_path: Path):
    """Guarda el manifiesto en YAML."""
    with open(output_path, 'w') as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"   Manifiesto guardado: {output_path}")


# ============================================================
# SECRET RESOLUTION
# ============================================================

def resolve_secrets(manifest: dict) -> dict:
    """Resuelve los valores de los secrets desde las fuentes disponibles."""
    resolved = {}
    unresolved = []

    for env_var, config in manifest.get("secrets", {}).items():
        value = os.environ.get(env_var)
        if value:
            resolved[env_var] = {
                "value": value,
                "source": "sandbox_env",
                "service": config.get("service", "Unknown"),
                "masked": f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "****",
            }
        else:
            unresolved.append({
                "env_var": env_var,
                "service": config.get("service", "Unknown"),
                "source_hint": "notion_db",
                "lookup_command": f"manus-mcp-cli tool call notion-search --server notion --input '{{\"query\": \"{config.get('service', env_var)}\", \"data_source_url\": \"{NOTION_CREDENTIALS_DB}\", \"page_size\": 3}}'",
            })

    return {"resolved": resolved, "unresolved": unresolved}


# ============================================================
# SECURITY VALIDATION
# ============================================================

def validate_security(project_path: Path, scaffold: dict) -> dict:
    """Valida que no haya secrets expuestos y que el scaffold permita inyección."""
    issues = []
    warnings = []

    project_path = Path(project_path)
    injection_mode = scaffold.get("secret_injection", "MANUAL_REVIEW")

    # BLOCK: web-static cannot have secrets
    if injection_mode == "BLOCKED":
        issues.append({
            "severity": "CRITICAL",
            "message": f"Scaffold '{scaffold['scaffold']}' NO permite inyección de secrets. "
                       f"Los secrets serían expuestos al cliente. "
                       f"Solución: usar un proxy backend (Cloudflare Worker o Vercel Function).",
            "action": "ABORT"
        })
        return {"passed": False, "issues": issues, "warnings": warnings}

    # SCAN: check for hardcoded secrets in source
    secret_patterns = [
        (r'sk-[a-zA-Z0-9]{20,}', "OpenAI API key hardcoded"),
        (r'sk-ant-[a-zA-Z0-9]{20,}', "Anthropic API key hardcoded"),
        (r'AIza[a-zA-Z0-9_-]{35}', "Google API key hardcoded"),
        (r'xai-[a-zA-Z0-9]{20,}', "xAI API key hardcoded"),
        (r'pplx-[a-zA-Z0-9]{20,}', "Perplexity API key hardcoded"),
        (r'ghp_[a-zA-Z0-9]{36}', "GitHub token hardcoded"),
    ]

    for ext in ["*.py", "*.ts", "*.tsx", "*.js", "*.jsx", "*.html"]:
        for filepath in project_path.rglob(ext):
            if "node_modules" in str(filepath) or ".next" in str(filepath):
                continue
            try:
                content = filepath.read_text(encoding='utf-8', errors='ignore')
                for pattern, description in secret_patterns:
                    if re.search(pattern, content):
                        # Check if it's in a safe context (env var reference)
                        rel_path = str(filepath.relative_to(project_path))
                        issues.append({
                            "severity": "CRITICAL",
                            "message": f"{description} en {rel_path}",
                            "action": "REMOVE_AND_USE_ENV_VAR"
                        })
            except Exception:
                pass

    # SCAN: check .env files are in .gitignore
    gitignore_path = project_path / ".gitignore"
    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text()
        if ".env" not in gitignore_content:
            warnings.append({
                "severity": "HIGH",
                "message": ".env no está en .gitignore — secrets podrían subirse a git",
                "action": "ADD_TO_GITIGNORE"
            })
    else:
        warnings.append({
            "severity": "HIGH",
            "message": "No existe .gitignore — crear uno con .env* incluido",
            "action": "CREATE_GITIGNORE"
        })

    # SCAN: check for VITE_ prefixed secrets (exposed to frontend in Vite)
    for env_file in project_path.glob(".env*"):
        try:
            content = env_file.read_text()
            for line in content.split('\n'):
                if line.startswith("VITE_") and any(kw in line.upper() for kw in ["SECRET", "KEY", "TOKEN", "PASSWORD"]):
                    warnings.append({
                        "severity": "HIGH",
                        "message": f"Secret con prefijo VITE_ en {env_file.name}: '{line.split('=')[0]}' — será expuesto al frontend",
                        "action": "REMOVE_VITE_PREFIX_OR_MOVE_TO_BACKEND"
                    })
        except Exception:
            pass

    passed = len(issues) == 0
    return {"passed": passed, "issues": issues, "warnings": warnings}


# ============================================================
# INJECTION TARGETS
# ============================================================

def inject_to_sandbox(project_path: Path, resolved: dict, dry_run: bool = False) -> dict:
    """Inyecta secrets en archivos .env del proyecto local."""
    results = []
    env_file = Path(project_path) / ".env.local"

    if dry_run:
        for env_var, info in resolved.items():
            results.append({"var": env_var, "target": str(env_file), "status": "DRY_RUN"})
        return {"target": "sandbox", "results": results}

    # Read existing .env.local
    existing = {}
    if env_file.exists():
        for line in env_file.read_text().split('\n'):
            if '=' in line and not line.startswith('#'):
                key = line.split('=', 1)[0].strip()
                existing[key] = line

    # Write/update
    with open(env_file, 'a' if env_file.exists() else 'w') as f:
        if not env_file.exists() or env_file.stat().st_size == 0:
            f.write(f"# Auto-generated by api-context-injector v3.1\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for env_var, info in resolved.items():
            if env_var not in existing:
                f.write(f"{env_var}={info['value']}\n")
                results.append({"var": env_var, "target": str(env_file), "status": "INJECTED"})
            else:
                results.append({"var": env_var, "target": str(env_file), "status": "ALREADY_EXISTS"})

    # Ensure .gitignore has .env*
    gitignore = Path(project_path) / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if ".env" not in content:
            with open(gitignore, 'a') as f:
                f.write("\n# Secrets\n.env*\n")
    else:
        with open(gitignore, 'w') as f:
            f.write("# Secrets\n.env*\nnode_modules/\n")

    return {"target": "sandbox", "results": results}


def inject_to_vercel(project_path: Path, resolved: dict, dry_run: bool = False) -> dict:
    """Inyecta secrets en Vercel via MCP."""
    results = []

    for env_var, info in resolved.items():
        if dry_run:
            results.append({"var": env_var, "target": "vercel", "status": "DRY_RUN",
                           "command": f"manus-mcp-cli tool call vercel_env_var_create --server vercel --input '...'"})
            continue

        try:
            # Use Vercel MCP to set env var
            cmd = [
                "manus-mcp-cli", "tool", "call", "create-environment-variable",
                "--server", "vercel",
                "--input", json.dumps({
                    "key": env_var,
                    "value": info["value"],
                    "type": "encrypted",
                    "target": ["production", "preview", "development"]
                })
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                results.append({"var": env_var, "target": "vercel", "status": "INJECTED"})
            else:
                results.append({"var": env_var, "target": "vercel", "status": "FAILED",
                               "error": result.stderr[:200]})
        except subprocess.TimeoutExpired:
            results.append({"var": env_var, "target": "vercel", "status": "TIMEOUT"})
        except Exception as e:
            results.append({"var": env_var, "target": "vercel", "status": "ERROR", "error": str(e)[:200]})

    return {"target": "vercel", "results": results}


def inject_to_cloudflare(project_path: Path, resolved: dict, dry_run: bool = False) -> dict:
    """Inyecta secrets en Cloudflare Workers via wrangler o API."""
    results = []
    wrangler_toml = Path(project_path) / "wrangler.toml"
    wrangler_jsonc = Path(project_path) / "wrangler.jsonc"

    has_wrangler = wrangler_toml.exists() or wrangler_jsonc.exists()

    for env_var, info in resolved.items():
        if dry_run:
            method = "wrangler secret put" if has_wrangler else "Cloudflare API"
            results.append({"var": env_var, "target": "cloudflare", "status": "DRY_RUN", "method": method})
            continue

        if has_wrangler:
            # Use wrangler CLI to set secret
            try:
                cmd = f"echo '{info['value']}' | npx wrangler secret put {env_var}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                                       timeout=30, cwd=str(project_path))
                if result.returncode == 0:
                    results.append({"var": env_var, "target": "cloudflare", "status": "INJECTED", "method": "wrangler"})
                else:
                    results.append({"var": env_var, "target": "cloudflare", "status": "FAILED",
                                   "error": result.stderr[:200], "method": "wrangler"})
            except Exception as e:
                results.append({"var": env_var, "target": "cloudflare", "status": "ERROR", "error": str(e)[:200]})
        else:
            # Use Cloudflare API directly
            try:
                import requests
                cf_token = os.environ.get("CLOUDFLARE_API_TOKEN")
                if not cf_token:
                    results.append({"var": env_var, "target": "cloudflare", "status": "NO_CF_TOKEN"})
                    continue

                # Note: would need account_id and script_name from manifest
                results.append({"var": env_var, "target": "cloudflare", "status": "NEEDS_ACCOUNT_ID",
                               "hint": "Agregar cloudflare_account_id y worker_name al manifiesto"})
            except Exception as e:
                results.append({"var": env_var, "target": "cloudflare", "status": "ERROR", "error": str(e)[:200]})

    return {"target": "cloudflare", "results": results}


def inject_to_supabase(project_path: Path, resolved: dict, dry_run: bool = False) -> dict:
    """Inyecta secrets en Supabase Vault via MCP."""
    results = []

    for env_var, info in resolved.items():
        if dry_run:
            results.append({"var": env_var, "target": "supabase_vault", "status": "DRY_RUN"})
            continue

        try:
            # Use Supabase MCP to store in vault
            cmd = [
                "manus-mcp-cli", "tool", "call", "execute_sql",
                "--server", "supabase",
                "--input", json.dumps({
                    "project_id": "NEEDS_PROJECT_ID",
                    "query": f"SELECT vault.create_secret('{info['value']}', '{env_var}', 'Injected by api-context-injector');"
                })
            ]
            if not dry_run:
                results.append({"var": env_var, "target": "supabase_vault", "status": "NEEDS_PROJECT_ID",
                               "hint": "Agregar supabase_project_id al manifiesto"})
        except Exception as e:
            results.append({"var": env_var, "target": "supabase_vault", "status": "ERROR", "error": str(e)[:200]})

    return {"target": "supabase_vault", "results": results}


# ============================================================
# AUDIT
# ============================================================

def audit_project(project_path: Path) -> dict:
    """Audita un proyecto: qué secrets tiene, dónde están, qué falta."""
    project_path = Path(project_path)
    scaffold = detect_scaffold(project_path)
    security = validate_security(project_path, scaffold)

    # Find all env files
    env_files = {}
    for env_file in project_path.glob(".env*"):
        vars_in_file = {}
        try:
            for line in env_file.read_text().split('\n'):
                if '=' in line and not line.startswith('#') and line.strip():
                    key = line.split('=', 1)[0].strip()
                    val = line.split('=', 1)[1].strip()
                    vars_in_file[key] = {
                        "has_value": bool(val),
                        "masked": f"{val[:3]}...{val[-3:]}" if len(val) > 6 else "***"
                    }
        except Exception:
            pass
        env_files[str(env_file.relative_to(project_path))] = vars_in_file

    # Find env var references in code that aren't in .env files
    all_env_in_files = set()
    for vars_dict in env_files.values():
        all_env_in_files.update(vars_dict.keys())

    code_refs = set()
    env_patterns = [
        r'process\.env\.(\w+)',
        r'os\.environ\[[\'"]([\w]+)',
        r'os\.environ\.get\([\'"]([\w]+)',
        r'import\.meta\.env\.(\w+)',
    ]
    for ext in ["*.py", "*.ts", "*.tsx", "*.js", "*.jsx"]:
        for filepath in project_path.rglob(ext):
            if "node_modules" in str(filepath):
                continue
            try:
                content = filepath.read_text(encoding='utf-8', errors='ignore')
                for pattern in env_patterns:
                    code_refs.update(re.findall(pattern, content))
            except Exception:
                pass

    missing_in_env = code_refs - all_env_in_files
    unused_in_env = all_env_in_files - code_refs

    return {
        "scaffold": scaffold,
        "security": security,
        "env_files": env_files,
        "code_references": sorted(code_refs),
        "missing_in_env_files": sorted(missing_in_env),
        "unused_in_env_files": sorted(unused_in_env),
        "recommendation": _generate_recommendation(scaffold, security, missing_in_env)
    }


def _generate_recommendation(scaffold, security, missing):
    """Genera recomendación basada en el audit."""
    if not security["passed"]:
        return "CRITICAL: Resolver issues de seguridad antes de inyectar secrets."
    if scaffold.get("secret_injection") == "BLOCKED":
        return "BLOCKED: Este scaffold no permite secrets. Crear un backend proxy."
    if missing:
        return f"ACCIÓN: {len(missing)} env vars referenciadas en código pero no en .env files. Ejecutar --generate-manifest y luego inyectar."
    return "OK: Proyecto correctamente configurado."


# ============================================================
# MAIN ORCHESTRATOR
# ============================================================

def run_injection(project_path: str, target: str = "sandbox", manifest_path: str = None,
                  dry_run: bool = False) -> dict:
    """Orquesta el flujo completo de inyección."""
    project_path = Path(project_path)
    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "project": str(project_path),
        "target": target,
        "dry_run": dry_run,
        "steps": []
    }

    # Step 1: Detect scaffold
    print(f"\n{'='*60}")
    print(f"  Secret Injection Engine v3.1")
    print(f"  Target: {target} | Dry Run: {dry_run}")
    print(f"{'='*60}")

    scaffold = detect_scaffold(project_path)
    report["scaffold"] = scaffold
    print(f"\n1. Scaffold detectado: {scaffold['scaffold']} ({scaffold['type']})")
    print(f"   Modo de inyección: {scaffold['secret_injection']}")

    # Step 2: Security validation
    security = validate_security(project_path, scaffold)
    report["security"] = security
    print(f"\n2. Validación de seguridad: {'PASSED' if security['passed'] else 'FAILED'}")
    for issue in security["issues"]:
        print(f"   ❌ [{issue['severity']}] {issue['message']}")
    for warning in security["warnings"]:
        print(f"   ⚠️  [{warning['severity']}] {warning['message']}")

    if not security["passed"]:
        print(f"\n   ABORTANDO: Resolver issues de seguridad primero.")
        report["status"] = "ABORTED_SECURITY"
        return report

    # Step 3: Load or generate manifest
    if manifest_path:
        manifest = load_manifest(Path(manifest_path))
        if not manifest:
            print(f"\n3. Manifiesto no encontrado en {manifest_path}")
            report["status"] = "MANIFEST_NOT_FOUND"
            return report
        print(f"\n3. Manifiesto cargado: {manifest_path}")
    else:
        manifest = generate_manifest(project_path)
        manifest_out = project_path / ".secrets-manifest.yaml"
        save_manifest(manifest, manifest_out)
        print(f"\n3. Manifiesto auto-generado: {manifest_out}")

    report["manifest"] = {k: v for k, v in manifest.items() if k != "secrets"}
    report["secrets_count"] = len(manifest.get("secrets", {}))
    print(f"   Secrets requeridos: {len(manifest.get('secrets', {}))}")

    # Step 4: Resolve secrets
    resolution = resolve_secrets(manifest)
    report["resolution"] = {
        "resolved_count": len(resolution["resolved"]),
        "unresolved_count": len(resolution["unresolved"]),
        "resolved_vars": [{"var": k, "source": v["source"], "masked": v["masked"]}
                         for k, v in resolution["resolved"].items()],
        "unresolved_vars": resolution["unresolved"]
    }
    print(f"\n4. Resolución de secrets:")
    print(f"   Resueltos (sandbox env): {len(resolution['resolved'])}")
    print(f"   No resueltos (necesitan Notion): {len(resolution['unresolved'])}")
    for u in resolution["unresolved"]:
        print(f"   ⚠️  {u['env_var']} ({u['service']}) — buscar en Notion DB")

    # Step 5: Inject to target
    print(f"\n5. Inyectando a: {target}")
    inject_fn = {
        "sandbox": inject_to_sandbox,
        "vercel": inject_to_vercel,
        "cloudflare": inject_to_cloudflare,
        "supabase": inject_to_supabase,
    }.get(target)

    if not inject_fn:
        print(f"   ❌ Target desconocido: {target}")
        report["status"] = "UNKNOWN_TARGET"
        return report

    injection_result = inject_fn(project_path, resolution["resolved"], dry_run)
    report["injection"] = injection_result

    injected = sum(1 for r in injection_result["results"] if r["status"] == "INJECTED")
    skipped = sum(1 for r in injection_result["results"] if r["status"] == "ALREADY_EXISTS")
    failed = sum(1 for r in injection_result["results"] if r["status"] in ("FAILED", "ERROR", "TIMEOUT"))
    dry = sum(1 for r in injection_result["results"] if r["status"] == "DRY_RUN")

    for r in injection_result["results"]:
        icon = {"INJECTED": "✅", "ALREADY_EXISTS": "⏭️", "DRY_RUN": "🔍", "FAILED": "❌"}.get(r["status"], "⚠️")
        print(f"   {icon} {r['var']}: {r['status']}")

    # Summary
    print(f"\n{'='*60}")
    print(f"  RESUMEN")
    print(f"  Scaffold: {scaffold['scaffold']}")
    print(f"  Secrets requeridos: {len(manifest.get('secrets', {}))}")
    print(f"  Resueltos: {len(resolution['resolved'])}")
    print(f"  No resueltos: {len(resolution['unresolved'])}")
    if dry_run:
        print(f"  Dry run: {dry}")
    else:
        print(f"  Inyectados: {injected}")
        print(f"  Ya existían: {skipped}")
        print(f"  Fallidos: {failed}")
    print(f"  Status: {'✅ COMPLETE' if failed == 0 else '⚠️ PARTIAL'}")
    print(f"{'='*60}")

    report["status"] = "COMPLETE" if failed == 0 else "PARTIAL"

    # Unresolved hints
    if resolution["unresolved"]:
        print(f"\n📋 Para resolver los {len(resolution['unresolved'])} secrets faltantes:")
        for u in resolution["unresolved"]:
            print(f"\n   {u['env_var']} ({u['service']}):")
            print(f"   {u['lookup_command']}")

    return report


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Motor de inyección de secrets v3.1")
    parser.add_argument("--project", help="Ruta al proyecto")
    parser.add_argument("--target", choices=["sandbox", "vercel", "cloudflare", "supabase"],
                       default="sandbox", help="Destino de inyección")
    parser.add_argument("--manifest", help="Ruta al manifiesto YAML")
    parser.add_argument("--dry-run", action="store_true", help="Simular sin inyectar")
    parser.add_argument("--generate-manifest", metavar="PATH", help="Auto-generar manifiesto para un proyecto")
    parser.add_argument("--audit", metavar="PATH", help="Auditar secrets de un proyecto")
    parser.add_argument("--detect", metavar="PATH", help="Solo detectar scaffold")
    parser.add_argument("--output", help="Guardar reporte en JSON")
    args = parser.parse_args()

    if args.detect:
        scaffold = detect_scaffold(Path(args.detect))
        print(json.dumps(scaffold, indent=2))
        return

    if args.generate_manifest:
        manifest = generate_manifest(Path(args.generate_manifest))
        output = Path(args.generate_manifest) / ".secrets-manifest.yaml"
        save_manifest(manifest, output)
        print(f"\nManifiesto generado con {len(manifest.get('secrets', {}))} secrets")
        print(yaml.dump(manifest, default_flow_style=False))
        return

    if args.audit:
        audit = audit_project(Path(args.audit))
        print(f"\n{'='*60}")
        print(f"  AUDIT REPORT")
        print(f"{'='*60}")
        print(f"Scaffold: {audit['scaffold']['scaffold']}")
        print(f"Security: {'PASSED' if audit['security']['passed'] else 'FAILED'}")
        print(f"Env files: {list(audit['env_files'].keys())}")
        print(f"Code references: {len(audit['code_references'])} env vars")
        print(f"Missing in .env: {audit['missing_in_env_files']}")
        print(f"Unused in .env: {audit['unused_in_env_files']}")
        print(f"Recommendation: {audit['recommendation']}")
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(audit, f, indent=2, default=str)
        return

    if not args.project:
        parser.print_help()
        return

    report = run_injection(
        project_path=args.project,
        target=args.target,
        manifest_path=args.manifest,
        dry_run=args.dry_run,
    )

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\nReporte guardado: {args.output}")


if __name__ == "__main__":
    main()
