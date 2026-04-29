#!/usr/bin/env python3.11
"""
preflight_check.py — Checklist de Pre-Vuelo para Sprint 1 del Monstruo.

Verifica que TODAS las dependencias, secrets, servicios y configuraciones
estén listas antes de arrancar la construcción del Monstruo real.

Uso:
    python3.11 preflight_check.py [--output report.json] [--fix] [--target sandbox|railway]

Categorías de verificación:
    1. Secrets / Environment Variables
    2. Python Packages (versiones ancladas)
    3. APIs operativas (ping a los 6 cerebros)
    4. Supabase (tablas, pgvector, RPC)
    5. Servicios externos (Langfuse, Firecrawl)
    6. Archivos del armero (integridad)
    7. Seguridad (LiteLLM version, hashes)
"""

import os
import sys
import json
import argparse
import subprocess
import importlib
from datetime import datetime
from pathlib import Path

# ─── Colores ───
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

# ─── Paths ───
ARMERO_ROOT = Path(__file__).parent.parent
INJECTOR_ROOT = Path("/home/ubuntu/skills/api-context-injector")
TOOLKIT_ROOT = Path("/home/ubuntu/skills/el-monstruo-toolkit")


def icon(ok):
    return f"{GREEN}PASS{RESET}" if ok else f"{RED}FAIL{RESET}"


def warn(msg):
    return f"{YELLOW}WARN{RESET} {msg}"


class PreflightChecker:
    def __init__(self, target="sandbox", fix=False):
        self.target = target
        self.fix = fix
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "target": target,
            "categories": {},
            "summary": {"pass": 0, "fail": 0, "warn": 0},
            "ready_to_build": False,
        }

    def _record(self, category, check_name, status, detail=""):
        if category not in self.results["categories"]:
            self.results["categories"][category] = []
        self.results["categories"][category].append({
            "check": check_name,
            "status": status,  # pass, fail, warn
            "detail": detail,
        })
        self.results["summary"][status] += 1

    # ─── 1. SECRETS ───
    def check_secrets(self):
        print(f"\n{BOLD}{CYAN}[1/7] Secrets / Environment Variables{RESET}")
        cat = "secrets"

        required = {
            "OPENAI_API_KEY": "GPT-5.4 (orquestador)",
            "ANTHROPIC_API_KEY": "Claude Sonnet 4.6 (arquitecto)",
            "GEMINI_API_KEY": "Gemini 3.1 Pro (creativo)",
            "XAI_API_KEY": "Grok 4.20 (código/tiempo real)",
            "SONAR_API_KEY": "Perplexity Sonar (investigador)",
            "OPENROUTER_API_KEY": "DeepSeek R1 + modelos (razonador)",
        }

        sprint1_new = {
            "SUPABASE_URL": "URL del proyecto Supabase",
            "SUPABASE_SERVICE_KEY": "Service role key (DB access)",
            "LANGFUSE_PUBLIC_KEY": "Langfuse observabilidad",
            "LANGFUSE_SECRET_KEY": "Langfuse secret",
            "LANGFUSE_HOST": "Langfuse host URL",
            "LITELLM_MASTER_KEY": "LiteLLM proxy master key",
        }

        optional = {
            "ELEVENLABS_API_KEY": "ElevenLabs audio",
            "HEYGEN_API_KEY": "HeyGen video",
            "DROPBOX_API_KEY": "Dropbox storage",
            "CLOUDFLARE_API_TOKEN": "Cloudflare infra",
            "TELEGRAM_BOT_TOKEN": "Telegram bot",
        }

        # Required (6 cerebros)
        for var, desc in required.items():
            val = os.environ.get(var, "")
            ok = bool(val) and len(val) > 10
            status = "pass" if ok else "fail"
            detail = f"Set ({len(val)} chars)" if ok else "NOT SET — BLOCKER"
            print(f"  [{icon(ok)}] {var}: {desc} — {detail}")
            self._record(cat, var, status, detail)

        # Sprint 1 new
        print(f"\n  {BOLD}Sprint 1 nuevas:{RESET}")
        for var, desc in sprint1_new.items():
            val = os.environ.get(var, "")
            ok = bool(val) and len(val) > 5
            status = "pass" if ok else "warn"
            detail = f"Set ({len(val)} chars)" if ok else "NOT SET — crear antes de Sprint 1"
            print(f"  [{icon(ok) if ok else warn('')}] {var}: {desc} — {detail}")
            self._record(cat, var, status, detail)

        # Optional
        print(f"\n  {BOLD}Opcionales:{RESET}")
        for var, desc in optional.items():
            val = os.environ.get(var, "")
            ok = bool(val) and len(val) > 5
            status = "pass" if ok else "warn"
            detail = f"Set ({len(val)} chars)" if ok else "Not set (optional)"
            print(f"  [{icon(ok) if ok else warn('')}] {var}: {desc}")
            self._record(cat, var, status, detail)

    # ─── 2. PYTHON PACKAGES ───
    def check_packages(self):
        print(f"\n{BOLD}{CYAN}[2/7] Python Packages{RESET}")
        cat = "packages"

        critical_packages = {
            "langgraph": "1.1.6",
            "litellm": "1.83.3",
            "langchain_core": None,  # any version
            "openai": None,
            "anthropic": None,
            "google.genai": None,
            "fastapi": None,
            "langfuse": None,
        }

        optional_packages = {
            "mem0ai": None,
            "supabase": None,
            "httpx": None,
        }

        for pkg, required_version in critical_packages.items():
            try:
                mod = importlib.import_module(pkg.replace("-", "_"))
                installed_version = getattr(mod, "__version__", "unknown")

                if required_version and installed_version != required_version:
                    print(f"  [{RED}FAIL{RESET}] {pkg}: v{installed_version} (NEED {required_version})")
                    self._record(cat, pkg, "fail", f"v{installed_version} != {required_version}")
                else:
                    print(f"  [{GREEN}PASS{RESET}] {pkg}: v{installed_version}")
                    self._record(cat, pkg, "pass", f"v{installed_version}")
            except ImportError:
                print(f"  [{RED}FAIL{RESET}] {pkg}: NOT INSTALLED")
                self._record(cat, pkg, "fail", "not installed")
                if self.fix:
                    pip_name = pkg.replace("_", "-").replace(".", "-")
                    ver = f"=={required_version}" if required_version else ""
                    print(f"    → Fixing: pip install {pip_name}{ver}")
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", f"{pip_name}{ver}"],
                        capture_output=True
                    )

        print(f"\n  {BOLD}Opcionales:{RESET}")
        for pkg, _ in optional_packages.items():
            try:
                mod = importlib.import_module(pkg.replace("-", "_"))
                v = getattr(mod, "__version__", "unknown")
                print(f"  [{GREEN}PASS{RESET}] {pkg}: v{v}")
                self._record(cat, pkg, "pass", f"v{v}")
            except ImportError:
                print(f"  [{YELLOW}WARN{RESET}] {pkg}: not installed (install before Sprint 1)")
                self._record(cat, pkg, "warn", "not installed")

    # ─── 3. APIs OPERATIVAS ───
    def check_apis(self):
        print(f"\n{BOLD}{CYAN}[3/7] APIs Operativas (6 Cerebros){RESET}")
        cat = "apis"

        try:
            sys.path.insert(0, str(INJECTOR_ROOT / "scripts"))
            from health_check import HEALTH_CHECKS, run_health_checks

            results = run_health_checks(quick=True)

            for name, check_result in results["checks"].items():
                status_str = check_result.get("status", "unknown")
                ok = status_str == "ok"
                status = "pass" if ok else ("warn" if status_str == "skipped" else "fail")
                latency = check_result.get("latency_s", "?")
                detail = f"{status_str} ({latency}s)" if ok else status_str
                self._record(cat, name, status, detail)

            sabios = results.get("sabios_healthy", 0)
            all_ok = results.get("all_sabios_ok", False)
            print(f"\n  Sabios healthy: {sabios}/6 {'— OK' if all_ok else '— INSUFICIENTE (min 3)'}")

        except Exception as e:
            print(f"  [{RED}FAIL{RESET}] No se pudo ejecutar health_check: {e}")
            self._record(cat, "health_check", "fail", str(e)[:200])

    # ─── 4. SUPABASE ───
    def check_supabase(self):
        print(f"\n{BOLD}{CYAN}[4/7] Supabase (Base de Datos + pgvector){RESET}")
        cat = "supabase"

        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_SERVICE_KEY", "")

        if not url or not key:
            print(f"  [{YELLOW}WARN{RESET}] SUPABASE_URL o SUPABASE_SERVICE_KEY no configurados")
            print(f"         → Crear antes de Sprint 1 (Día 2: Memoria)")
            self._record(cat, "supabase_connection", "warn", "credentials not set")
            return

        try:
            import requests
            headers = {
                "apikey": key,
                "Authorization": f"Bearer {key}",
            }

            # Check connection
            r = requests.get(f"{url}/rest/v1/", headers=headers, timeout=10)
            ok = r.status_code in [200, 406]
            print(f"  [{icon(ok)}] Conexión a Supabase: HTTP {r.status_code}")
            self._record(cat, "connection", "pass" if ok else "fail", f"HTTP {r.status_code}")

            # Check pgvector extension
            r2 = requests.post(
                f"{url}/rest/v1/rpc/check_pgvector",
                headers={**headers, "Content-Type": "application/json"},
                json={},
                timeout=10,
            )
            if r2.status_code == 200:
                print(f"  [{GREEN}PASS{RESET}] pgvector extension activa")
                self._record(cat, "pgvector", "pass")
            else:
                print(f"  [{YELLOW}WARN{RESET}] pgvector: RPC check_pgvector no existe (crear en Día 2)")
                self._record(cat, "pgvector", "warn", "RPC not found — setup needed")

            # Check monstruo_memory table
            r3 = requests.get(
                f"{url}/rest/v1/monstruo_memory?select=id&limit=1",
                headers=headers,
                timeout=10,
            )
            if r3.status_code == 200:
                print(f"  [{GREEN}PASS{RESET}] Tabla monstruo_memory existe")
                self._record(cat, "monstruo_memory_table", "pass")
            else:
                print(f"  [{YELLOW}WARN{RESET}] Tabla monstruo_memory no existe (crear en Día 2)")
                self._record(cat, "monstruo_memory_table", "warn", "table not found")

        except Exception as e:
            print(f"  [{RED}FAIL{RESET}] Error conectando a Supabase: {e}")
            self._record(cat, "connection", "fail", str(e)[:200])

    # ─── 5. SERVICIOS EXTERNOS ───
    def check_external_services(self):
        print(f"\n{BOLD}{CYAN}[5/7] Servicios Externos{RESET}")
        cat = "external_services"

        # Langfuse
        langfuse_host = os.environ.get("LANGFUSE_HOST", "")
        langfuse_pub = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
        if langfuse_host and langfuse_pub:
            try:
                import requests
                r = requests.get(f"{langfuse_host}/api/public/health", timeout=10)
                ok = r.status_code == 200
                print(f"  [{icon(ok)}] Langfuse: {'operativo' if ok else f'HTTP {r.status_code}'}")
                self._record(cat, "langfuse", "pass" if ok else "fail")
            except Exception as e:
                print(f"  [{RED}FAIL{RESET}] Langfuse: {e}")
                self._record(cat, "langfuse", "fail", str(e)[:100])
        else:
            print(f"  [{YELLOW}WARN{RESET}] Langfuse: no configurado (crear cuenta en cloud.langfuse.com)")
            self._record(cat, "langfuse", "warn", "not configured")

        # Firecrawl (optional)
        firecrawl_key = os.environ.get("FIRECRAWL_API_KEY", "")
        if firecrawl_key:
            print(f"  [{GREEN}PASS{RESET}] Firecrawl: API key configurada")
            self._record(cat, "firecrawl", "pass")
        else:
            print(f"  [{YELLOW}WARN{RESET}] Firecrawl: no configurado (opcional, Crawl4AI como fallback)")
            self._record(cat, "firecrawl", "warn", "not configured — crawl4ai available")

    # ─── 6. ARCHIVOS DEL ARMERO ───
    def check_armero_files(self):
        print(f"\n{BOLD}{CYAN}[6/7] Integridad del Armero{RESET}")
        cat = "armero_files"

        expected_files = [
            "SKILL.md",
            "config/skill_config.yaml",
            "references/build_stack/langgraph.yaml",
            "references/build_stack/litellm.yaml",
            "references/build_stack/mem0_memory.yaml",
            "references/build_stack/langfuse.yaml",
            "references/build_stack/firecrawl.yaml",
            "references/build_stack/console_web.yaml",
            "references/build_stack/complementary_tools.yaml",
            "references/embeddings/embedding_models.yaml",
            "templates/sprint1/architecture_skeleton.py",
            "templates/sprint1/env_template.yaml",
            "templates/sprint1/requirements.txt",
        ]

        for f in expected_files:
            path = ARMERO_ROOT / f
            ok = path.exists()
            size = path.stat().st_size if ok else 0
            print(f"  [{icon(ok)}] {f}" + (f" ({size:,} bytes)" if ok else " — MISSING"))
            self._record(cat, f, "pass" if ok else "fail", f"{size} bytes" if ok else "missing")

        # Validate YAMLs
        import yaml
        yaml_files = [f for f in expected_files if f.endswith(".yaml")]
        yaml_ok = 0
        for f in yaml_files:
            path = ARMERO_ROOT / f
            if path.exists():
                try:
                    with open(path) as fh:
                        yaml.safe_load(fh)
                    yaml_ok += 1
                except yaml.YAMLError as e:
                    print(f"  [{RED}FAIL{RESET}] YAML parse error: {f} — {e}")
                    self._record(cat, f"yaml_valid_{f}", "fail", str(e)[:100])

        print(f"\n  YAML válidos: {yaml_ok}/{len(yaml_files)}")

    # ─── 7. SEGURIDAD ───
    def check_security(self):
        print(f"\n{BOLD}{CYAN}[7/7] Seguridad{RESET}")
        cat = "security"

        # LiteLLM version check
        try:
            import litellm
            v = litellm.__version__
            ok = v == "1.83.3"
            if ok:
                print(f"  [{GREEN}PASS{RESET}] LiteLLM v{v} (segura)")
                self._record(cat, "litellm_version", "pass", f"v{v}")
            else:
                print(f"  [{RED}FAIL{RESET}] LiteLLM v{v} — PELIGRO: solo v1.83.3 es segura")
                self._record(cat, "litellm_version", "fail", f"v{v} — unsafe")
        except ImportError:
            print(f"  [{YELLOW}WARN{RESET}] LiteLLM no instalado (instalar antes de Sprint 1)")
            self._record(cat, "litellm_version", "warn", "not installed")

        # Check no hardcoded secrets in skeleton
        skeleton = ARMERO_ROOT / "templates/sprint1/architecture_skeleton.py"
        if skeleton.exists():
            content = skeleton.read_text()
            patterns = ["sk-", "sk_", "xai-", "AIza", "eyJ"]
            found = [p for p in patterns if p in content and f'"{p}' in content]
            if found:
                print(f"  [{RED}FAIL{RESET}] Posibles secrets hardcodeados en skeleton: {found}")
                self._record(cat, "no_hardcoded_secrets", "fail", f"patterns: {found}")
            else:
                print(f"  [{GREEN}PASS{RESET}] No hay secrets hardcodeados en skeleton")
                self._record(cat, "no_hardcoded_secrets", "pass")

        # Check .gitignore patterns
        print(f"  [{GREEN}PASS{RESET}] Recordatorio: .env* DEBE estar en .gitignore del proyecto")
        self._record(cat, "gitignore_reminder", "pass", "manual check needed")

    # ─── RUN ALL ───
    def run(self):
        print(f"\n{'='*60}")
        print(f"  {BOLD}PREFLIGHT CHECK — El Monstruo Sprint 1{RESET}")
        print(f"  Target: {self.target}")
        print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*60}")

        self.check_secrets()
        self.check_packages()
        self.check_apis()
        self.check_supabase()
        self.check_external_services()
        self.check_armero_files()
        self.check_security()

        # Summary
        s = self.results["summary"]
        total = s["pass"] + s["fail"] + s["warn"]
        self.results["ready_to_build"] = s["fail"] == 0

        print(f"\n{'='*60}")
        print(f"  {BOLD}RESUMEN{RESET}")
        print(f"  {GREEN}PASS: {s['pass']}{RESET}")
        print(f"  {RED}FAIL: {s['fail']}{RESET}")
        print(f"  {YELLOW}WARN: {s['warn']}{RESET}")
        print(f"  Total: {total}")
        print(f"\n  {'🟢 LISTO PARA CONSTRUIR' if self.results['ready_to_build'] else '🔴 NO LISTO — resolver FAILs primero'}")

        if s["warn"] > 0 and s["fail"] == 0:
            print(f"  {YELLOW}⚠ Hay {s['warn']} warnings — funcional pero incompleto{RESET}")

        print(f"{'='*60}")

        return self.results


def main():
    parser = argparse.ArgumentParser(description="Preflight Check — El Monstruo Sprint 1")
    parser.add_argument("--output", help="Guardar reporte en JSON")
    parser.add_argument("--fix", action="store_true", help="Intentar corregir problemas automáticamente")
    parser.add_argument("--target", default="sandbox", choices=["sandbox", "railway"],
                        help="Entorno objetivo (default: sandbox)")
    args = parser.parse_args()

    checker = PreflightChecker(target=args.target, fix=args.fix)
    results = checker.run()

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nReporte guardado: {args.output}")


if __name__ == "__main__":
    main()
