#!/usr/bin/env python3
"""
Audit ejecutable de la app Flutter — DSC-S-011 Sistema de Realidad Ejecutable.

Propósito: producir reporte binario de qué hay en apps/mobile/lib/ sin
narrativa: clases, imports, providers, services, screens, dependencias.

Si la respuesta no está en este output, Cowork no la afirma.

Uso:
    python3 tools/audit_app_flutter.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(__file__).resolve().parent.parent
APP_LIB = REPO_ROOT / "apps" / "mobile" / "lib"


def section(title: str) -> None:
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def subsec(title: str) -> None:
    print()
    print(f"--- {title} ---")


# ── 1. INVENTARIO DE ARCHIVOS .dart ─────────────────────────────────

def audit_files() -> list[Path]:
    section("1. INVENTARIO DE ARCHIVOS .dart")
    files = sorted(APP_LIB.rglob("*.dart"))
    print(f"  Total archivos .dart: {len(files)}")
    print()
    by_dir: dict[str, list[Path]] = {}
    for f in files:
        rel = f.relative_to(APP_LIB)
        d = str(rel.parent) if rel.parent != Path(".") else "(root)"
        by_dir.setdefault(d, []).append(f)
    for d in sorted(by_dir.keys()):
        print(f"  {d}/ ({len(by_dir[d])} files)")
        for f in by_dir[d]:
            loc = sum(1 for _ in f.open(encoding="utf-8", errors="ignore"))
            print(f"    {f.relative_to(APP_LIB)}  → {loc} LOC")
    total_loc = sum(sum(1 for _ in f.open(encoding="utf-8", errors="ignore")) for f in files)
    print(f"\n  TOTAL LOC: {total_loc}")
    return files


# ── 2. ANÁLISIS DE CLASES Y WIDGETS ──────────────────────────────────

CLASS_RE = re.compile(r"^class\s+(\w+)(?:\s+extends\s+(\w+))?", re.MULTILINE)
STATEFUL_RE = re.compile(r"\bStatefulWidget\b")
STATELESS_RE = re.compile(r"\bStatelessWidget\b")
CONSUMER_RE = re.compile(r"\bConsumerWidget\b|\bConsumerStatefulWidget\b")


def audit_classes(files: list[Path]) -> dict[str, int]:
    section("2. CLASES + WIDGETS POR ARCHIVO")
    summary = {
        "total_classes": 0,
        "stateful": 0,
        "stateless": 0,
        "consumer": 0,
    }
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        classes = CLASS_RE.findall(text)
        if not classes:
            continue
        sf = len(STATEFUL_RE.findall(text))
        sl = len(STATELESS_RE.findall(text))
        cw = len(CONSUMER_RE.findall(text))
        summary["total_classes"] += len(classes)
        summary["stateful"] += sf
        summary["stateless"] += sl
        summary["consumer"] += cw
        marker = ""
        if cw > 0:
            marker = f" [Consumer×{cw}]"
        elif sf > 0:
            marker = f" [Stateful×{sf}]"
        elif sl > 0:
            marker = f" [Stateless×{sl}]"
        print(f"  {f.relative_to(APP_LIB)}: {len(classes)} clases{marker}")
        for cls, parent in classes[:6]:
            if parent:
                print(f"    class {cls} extends {parent}")
            else:
                print(f"    class {cls}")
    print()
    print(f"  RESUMEN: total clases={summary['total_classes']}, stateful={summary['stateful']}, "
          f"stateless={summary['stateless']}, consumer={summary['consumer']}")
    return summary


# ── 3. IMPORTS Y DEPENDENCIAS USADAS ─────────────────────────────────

IMPORT_RE = re.compile(r"^import\s+['\"]([^'\"]+)['\"]", re.MULTILINE)


def audit_imports(files: list[Path]) -> dict[str, int]:
    section("3. IMPORTS — TOP 20 PACKAGES USADOS")
    pkg_count: Counter[str] = Counter()
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        for m in IMPORT_RE.finditer(text):
            uri = m.group(1)
            if uri.startswith("package:"):
                pkg = uri.split("/", 1)[0].replace("package:", "")
                pkg_count[pkg] += 1
            elif uri.startswith("dart:"):
                pkg_count[uri] += 1
    for pkg, n in pkg_count.most_common(20):
        print(f"  {pkg:35s} ×{n}")
    return dict(pkg_count)


# ── 4. ENDPOINTS DEL KERNEL CONSUMIDOS ───────────────────────────────

URL_RE = re.compile(r"['\"]/v1/[a-zA-Z0-9_/\-{}]+['\"]")
URL_RE_FULL = re.compile(r"['\"]https?://[^'\"]+['\"]")


def audit_kernel_endpoints(files: list[Path]) -> set[str]:
    section("4. ENDPOINTS DEL KERNEL QUE LA APP CONSUME")
    endpoints: set[str] = set()
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        for m in URL_RE.finditer(text):
            endpoints.add(m.group(0).strip("'\""))
    for e in sorted(endpoints):
        print(f"  {e}")
    if not endpoints:
        print("  (ninguno detectado por regex /v1/*)")
    return endpoints


# ── 5. PROVIDERS Y SERVICES (Riverpod) ───────────────────────────────

PROVIDER_RE = re.compile(r"\b(Provider|StateNotifierProvider|StateProvider|FutureProvider|StreamProvider|NotifierProvider|AsyncNotifierProvider)<[^>]*>\s*\(")


def audit_providers(files: list[Path]) -> int:
    section("5. PROVIDERS RIVERPOD POR ARCHIVO")
    total = 0
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        matches = PROVIDER_RE.findall(text)
        if matches:
            print(f"  {f.relative_to(APP_LIB)}: {len(matches)} providers")
            total += len(matches)
    print(f"\n  TOTAL providers: {total}")
    return total


# ── 6. ROUTES / NAVEGACIÓN ───────────────────────────────────────────

ROUTE_RE = re.compile(r"path:\s*['\"]([^'\"]+)['\"]")


def audit_routes(files: list[Path]) -> list[str]:
    section("6. RUTAS DECLARADAS (go_router)")
    routes: list[str] = []
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        for m in ROUTE_RE.finditer(text):
            routes.append(m.group(1))
            print(f"  {f.relative_to(APP_LIB)}:  path: {m.group(1)}")
    return routes


# ── 7. WEBSOCKET + REAL-TIME ─────────────────────────────────────────

def audit_realtime(files: list[Path]) -> dict[str, list[str]]:
    section("7. WEBSOCKET + COMUNICACIÓN REAL-TIME")
    out = {"websocket_uses": [], "sse_uses": [], "polling_uses": []}
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        if "WebSocket" in text or "web_socket_channel" in text or "ws://" in text or "wss://" in text:
            out["websocket_uses"].append(str(f.relative_to(APP_LIB)))
        if "EventSource" in text or "text/event-stream" in text:
            out["sse_uses"].append(str(f.relative_to(APP_LIB)))
        if "Timer.periodic" in text or "Stream.periodic" in text:
            out["polling_uses"].append(str(f.relative_to(APP_LIB)))
    for k, v in out.items():
        print(f"\n  {k} ({len(v)}):")
        for p in v:
            print(f"    {p}")
    return out


# ── 8. TODOS Y STUBS DETECTADOS ──────────────────────────────────────

def audit_todos(files: list[Path]) -> int:
    section("8. TODOs + STUBS detectados en el código")
    total = 0
    patterns = [
        re.compile(r"//\s*(TODO|FIXME|XXX|HACK):?\s*(.+)", re.IGNORECASE),
        re.compile(r'throw\s+UnimplementedError\(', re.IGNORECASE),
    ]
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        lines_with_todos = []
        for i, line in enumerate(text.splitlines(), 1):
            for p in patterns:
                if p.search(line):
                    lines_with_todos.append((i, line.strip()[:120]))
                    break
        if lines_with_todos:
            print(f"\n  {f.relative_to(APP_LIB)}:")
            for ln, txt in lines_with_todos[:8]:
                print(f"    L{ln}: {txt}")
            total += len(lines_with_todos)
    print(f"\n  TOTAL TODOs/stubs: {total}")
    return total


# ── 9. PUNTOS DE CONEXIÓN POTENCIAL CON EMBRIÓN ──────────────────────

def audit_embrion_touchpoints(files: list[Path]) -> list[str]:
    section("9. REFERENCIAS A 'embrion' EN LA APP")
    refs: list[str] = []
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        for i, line in enumerate(text.splitlines(), 1):
            if "embrion" in line.lower() or "embrión" in line.lower():
                refs.append(f"{f.relative_to(APP_LIB)}:L{i}: {line.strip()[:120]}")
    for r in refs:
        print(f"  {r}")
    if not refs:
        print("  (ninguna referencia textual a 'embrion')")
    return refs


# ── 10. VEREDICTO BINARIO ────────────────────────────────────────────

def veredicto(files, classes, providers, endpoints, routes, todos, embrion_refs) -> None:
    section("10. VEREDICTO BINARIO APP FLUTTER")
    checks = [
        ("Archivos .dart >= 30", len(files) >= 30),
        ("Clases definidas >= 30", classes.get("total_classes", 0) >= 30),
        ("Providers Riverpod presentes", providers >= 1),
        ("Endpoints /v1/* consumidos", len(endpoints) >= 1),
        ("Rutas go_router declaradas", len(routes) >= 1),
        ("Referencias a 'embrion' presentes", len(embrion_refs) >= 1),
        ("TODOs/stubs limitados (<30)", todos < 30),
    ]
    for label, ok in checks:
        print(f"  {'✅' if ok else '❌'} {label}")
    passed = sum(1 for _, ok in checks if ok)
    print(f"\n  Score binario código: {passed}/{len(checks)}")


def main() -> int:
    print()
    print("#" * 70)
    print("#  AUDIT EJECUTABLE — App Flutter El Monstruo")
    print("#  DSC-S-011 Sistema de Realidad Ejecutable")
    print("#" * 70)

    files = audit_files()
    classes = audit_classes(files)
    audit_imports(files)
    endpoints = audit_kernel_endpoints(files)
    providers = audit_providers(files)
    routes = audit_routes(files)
    audit_realtime(files)
    todos = audit_todos(files)
    embrion_refs = audit_embrion_touchpoints(files)
    veredicto(files, classes, providers, endpoints, routes, todos, embrion_refs)

    print()
    print("=" * 70)
    print("  FIN — Cowork: cero afirmación sin pointer al output de arriba.")
    print("=" * 70)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
