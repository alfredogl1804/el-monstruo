#!/usr/bin/env python3
"""
El Monstruo — Auto-Repair Engine
=================================
Sprint 16 — 2026-04-20

Detecta fallos en el stack y los repara automáticamente con código.
NO depende de texto ni de promesas — ejecuta reparaciones reales.

Capacidades:
1. Detectar dependencias rotas en requirements.txt
2. Detectar GitHub Actions sin SHA pin
3. Detectar versiones obsoletas y actualizar al latest de PyPI
4. Detectar imports rotos en código Python
5. Verificar que el deploy en Railway responde correctamente
6. Auto-retry con backoff exponencial

Uso:
    python scripts/auto_repair.py                    # Scan + report
    python scripts/auto_repair.py --fix              # Scan + auto-fix
    python scripts/auto_repair.py --deploy-check     # Verify Railway deploy
    python scripts/auto_repair.py --import-check     # Verify Python imports

Principio: Si se puede detectar con código, se puede reparar con código.
"""

from __future__ import annotations

import ast
import json
import os
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests

REPO_ROOT = Path(__file__).parent.parent
REQUIREMENTS_PATH = REPO_ROOT / "requirements.txt"
KERNEL_URL = os.environ.get("KERNEL_URL", "https://el-monstruo-kernel-production.up.railway.app")
REPORT_DIR = REPO_ROOT / "reports"


@dataclass
class Issue:
    category: str  # dependency, action, import, deploy, version
    severity: str  # critical, high, medium, low
    file: str
    line: Optional[int]
    description: str
    auto_fixable: bool
    fix_applied: bool = False
    fix_description: Optional[str] = None


@dataclass
class RepairReport:
    timestamp: str
    issues_found: list[Issue] = field(default_factory=list)
    issues_fixed: list[Issue] = field(default_factory=list)
    issues_unfixable: list[Issue] = field(default_factory=list)
    deploy_status: Optional[dict] = None


# ── Dependency Scanner ─────────────────────────────────────────────
def scan_dependencies() -> list[Issue]:
    """Scan requirements.txt for issues."""
    issues = []
    if not REQUIREMENTS_PATH.exists():
        issues.append(
            Issue(
                category="dependency",
                severity="critical",
                file=str(REQUIREMENTS_PATH),
                line=None,
                description="requirements.txt not found",
                auto_fixable=False,
            )
        )
        return issues

    for i, line in enumerate(REQUIREMENTS_PATH.read_text().splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Check for unpinned dependencies
        if ">=" in stripped and "==" not in stripped:
            match = re.match(r"^([a-zA-Z0-9_-]+)", stripped)
            pkg = match.group(1) if match else stripped
            issues.append(
                Issue(
                    category="dependency",
                    severity="medium",
                    file=str(REQUIREMENTS_PATH),
                    line=i,
                    description=f"{pkg} uses range constraint instead of exact pin",
                    auto_fixable=True,
                )
            )

        # Check for known banned packages
        banned = {"litellm": "CVE-2026-35030 — SSRF in proxy mode"}
        for pkg, reason in banned.items():
            if stripped.lower().startswith(pkg):
                issues.append(
                    Issue(
                        category="dependency",
                        severity="critical",
                        file=str(REQUIREMENTS_PATH),
                        line=i,
                        description=f"BANNED package: {pkg} — {reason}",
                        auto_fixable=True,
                    )
                )

    return issues


# ── GitHub Actions Scanner ─────────────────────────────────────────
def scan_gh_actions() -> list[Issue]:
    """Scan GitHub Actions for unpinned refs."""
    issues = []
    workflows_dir = REPO_ROOT / ".github" / "workflows"
    if not workflows_dir.exists():
        return issues

    sha_pattern = re.compile(r"@([0-9a-f]{40})")
    uses_pattern = re.compile(r"uses:\s*(.+?)@(.+?)(?:\s|#|$)")

    # Actions that MUST be SHA-pinned (known supply chain targets)
    must_pin = {"aquasecurity/trivy-action", "gitleaks/gitleaks-action"}

    for yml_file in workflows_dir.glob("*.yml"):
        for i, line in enumerate(yml_file.read_text().splitlines(), 1):
            match = uses_pattern.search(line)
            if not match:
                continue

            action = match.group(1).strip()
            ref = match.group(2).strip()

            if action in must_pin and not sha_pattern.match(ref):
                issues.append(
                    Issue(
                        category="action",
                        severity="critical",
                        file=str(yml_file),
                        line=i,
                        description=f"{action}@{ref} — MUST be SHA-pinned (supply chain risk)",
                        auto_fixable=False,
                    )
                )

    return issues


# ── Import Scanner ─────────────────────────────────────────────────
def scan_imports() -> list[Issue]:
    """Scan Python files for potentially broken imports."""
    issues = []
    kernel_dir = REPO_ROOT / "kernel"
    if not kernel_dir.exists():
        return issues

    for py_file in kernel_dir.rglob("*.py"):
        try:
            tree = ast.parse(py_file.read_text())
        except SyntaxError as e:
            issues.append(
                Issue(
                    category="import",
                    severity="critical",
                    file=str(py_file),
                    line=e.lineno,
                    description=f"Syntax error: {e.msg}",
                    auto_fixable=False,
                )
            )
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                # Check for known deprecated import paths
                deprecated_imports = {
                    "langchain.agents": "Use langchain.agents (v1) or langgraph.prebuilt (v0)",
                    "langchain.llms": "Deprecated — use langchain_openai, langchain_anthropic, etc.",
                    "langchain.chat_models": "Deprecated — use langchain_openai.ChatOpenAI, etc.",
                }
                for deprecated, suggestion in deprecated_imports.items():
                    if node.module.startswith(deprecated):
                        issues.append(
                            Issue(
                                category="import",
                                severity="medium",
                                file=str(py_file),
                                line=node.lineno,
                                description=f"Deprecated import: {node.module} — {suggestion}",
                                auto_fixable=False,
                            )
                        )

    return issues


# ── Deploy Verifier ────────────────────────────────────────────────
def verify_deploy(expected_version: str, max_retries: int = 10, initial_wait: int = 15) -> dict:
    """
    Verify Railway deploy with exponential backoff.
    Returns deploy status dict.
    """
    print(f"\n  🚀 Verifying deploy at {KERNEL_URL}")
    print(f"     Expected version: {expected_version}")
    print(f"     Max retries: {max_retries}, initial wait: {initial_wait}s\n")

    for attempt in range(1, max_retries + 1):
        wait_time = initial_wait * (1.5 ** (attempt - 1))  # Exponential backoff
        if attempt > 1:
            print(f"     ⏳ Waiting {wait_time:.0f}s before retry {attempt}/{max_retries}...")
            time.sleep(wait_time)

        try:
            r = requests.get(f"{KERNEL_URL}/health", timeout=10)
            if r.status_code == 200:
                data = r.json()
                current_version = data.get("version", "unknown")
                status = data.get("status", "unknown")

                print(f"     [{attempt}] HTTP 200 — version={current_version}, status={status}")

                if current_version == expected_version:
                    print(f"     ✅ Deploy VERIFIED: {expected_version}")
                    return {
                        "verified": True,
                        "version": current_version,
                        "status": status,
                        "attempt": attempt,
                        "components": data.get("components", {}),
                    }
                else:
                    print(f"     ⏳ Version mismatch: got {current_version}, expected {expected_version}")
            else:
                print(f"     [{attempt}] HTTP {r.status_code}")

        except requests.RequestException as e:
            print(f"     [{attempt}] Connection error: {e}")

    print(f"     ❌ Deploy NOT verified after {max_retries} attempts")
    return {
        "verified": False,
        "version": "unknown",
        "status": "timeout",
        "attempt": max_retries,
    }


# ── Auto-Fix Engine ───────────────────────────────────────────────
def apply_fixes(issues: list[Issue]) -> list[Issue]:
    """Apply auto-fixes where possible."""
    fixed = []

    for issue in issues:
        if not issue.auto_fixable:
            continue

        if issue.category == "dependency" and "BANNED" in issue.description:
            # Remove banned package from requirements.txt
            content = REQUIREMENTS_PATH.read_text()
            lines = content.splitlines()
            pkg_name = issue.description.split(":")[0].replace("BANNED package", "").strip()
            new_lines = [l for l in lines if not l.strip().lower().startswith(pkg_name.lower())]
            if len(new_lines) < len(lines):
                REQUIREMENTS_PATH.write_text("\n".join(new_lines) + "\n")
                issue.fix_applied = True
                issue.fix_description = f"Removed {pkg_name} from requirements.txt"
                fixed.append(issue)

        elif issue.category == "dependency" and "range constraint" in issue.description:
            # Resolve range to exact latest version
            match = re.match(r"(\S+) uses range", issue.description)
            if match:
                pkg = match.group(1)
                try:
                    r = requests.get(f"https://pypi.org/pypi/{pkg}/json", timeout=10)
                    if r.status_code == 200:
                        latest = r.json()["info"]["version"]
                        content = REQUIREMENTS_PATH.read_text()
                        # Replace range with exact pin
                        pattern = re.compile(rf"^{re.escape(pkg)}[><=!].*$", re.MULTILINE)
                        new_content = pattern.sub(f"{pkg}=={latest}", content)
                        if new_content != content:
                            REQUIREMENTS_PATH.write_text(new_content)
                            issue.fix_applied = True
                            issue.fix_description = f"Pinned {pkg}=={latest} (was range)"
                            fixed.append(issue)
                except Exception:
                    pass

    return fixed


# ── Main Orchestrator ──────────────────────────────────────────────
def run_repair(
    fix: bool = False,
    deploy_check: bool = False,
    expected_version: str = "0.10.0-sprint16",
    import_check: bool = False,
) -> RepairReport:
    """Run the full auto-repair pipeline."""
    print(f"\n{'=' * 70}")
    print("  AUTO-REPAIR ENGINE")
    print(f"  Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print(f"  Mode: {'Fix' if fix else 'Scan only'}")
    print(f"{'=' * 70}\n")

    report = RepairReport(timestamp=datetime.now(timezone.utc).isoformat())

    # Scan
    print("  [1/4] Scanning dependencies...")
    dep_issues = scan_dependencies()
    report.issues_found.extend(dep_issues)
    print(f"        Found {len(dep_issues)} dependency issues")

    print("  [2/4] Scanning GitHub Actions...")
    action_issues = scan_gh_actions()
    report.issues_found.extend(action_issues)
    print(f"        Found {len(action_issues)} action issues")

    if import_check:
        print("  [3/4] Scanning imports...")
        import_issues = scan_imports()
        report.issues_found.extend(import_issues)
        print(f"        Found {len(import_issues)} import issues")
    else:
        print("  [3/4] Import scan skipped (use --import-check)")

    # Fix
    if fix and report.issues_found:
        print("\n  🔧 Applying auto-fixes...")
        fixed = apply_fixes(report.issues_found)
        report.issues_fixed = fixed
        for f_issue in fixed:
            print(f"      ✅ {f_issue.fix_description}")

    # Deploy check
    if deploy_check:
        print("  [4/4] Verifying deploy...")
        report.deploy_status = verify_deploy(expected_version)
    else:
        print("  [4/4] Deploy check skipped (use --deploy-check)")

    # Unfixable issues
    report.issues_unfixable = [i for i in report.issues_found if not i.auto_fixable]

    # Summary
    print(f"\n{'=' * 70}")
    print("  SUMMARY")
    print(f"  Issues found: {len(report.issues_found)}")
    print(f"  Issues fixed: {len(report.issues_fixed)}")
    print(f"  Issues unfixable: {len(report.issues_unfixable)}")
    if report.deploy_status:
        status = "✅ VERIFIED" if report.deploy_status.get("verified") else "❌ NOT VERIFIED"
        print(f"  Deploy: {status}")
    print(f"{'=' * 70}\n")

    # Save report
    REPORT_DIR.mkdir(exist_ok=True)
    report_path = REPORT_DIR / f"repair_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, "w") as f:
        json.dump(asdict(report), f, indent=2, default=str)
    print(f"  Report: {report_path}")

    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Auto-Repair Engine")
    parser.add_argument("--fix", action="store_true", help="Apply auto-fixes")
    parser.add_argument("--deploy-check", action="store_true", help="Verify Railway deploy")
    parser.add_argument("--import-check", action="store_true", help="Scan Python imports")
    parser.add_argument("--expected-version", default="0.10.0-sprint16", help="Expected deploy version")
    args = parser.parse_args()

    run_repair(
        fix=args.fix,
        deploy_check=args.deploy_check,
        expected_version=args.expected_version,
        import_check=args.import_check,
    )
