#!/usr/bin/env python3
"""
Audit ejecutable del Embrión Loop — DSC-S-011 Sistema de Realidad Ejecutable.

Propósito: producir un reporte binario sobre el loop del Embrión que YO (Cowork)
NO pueda inventar. Solo hechos extraídos del código + estado de la DB.

Si la respuesta no está en este output, no la afirmo.

Uso:
    python3 tools/audit_embrion_loop.py
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
KERNEL_DIR = REPO_ROOT / "kernel"

# Archivos del Embrión a auditar
EMBRION_FILES = [
    "embrion_loop.py",
    "embrion_budget.py",
    "embrion_self_verifier.py",
    "embrion_write_policy.py",
    "embrion_inbox.py",
    "embrion_routes.py",
]


def section(title: str) -> None:
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def subsec(title: str) -> None:
    print()
    print(f"--- {title} ---")


# ── 1. ESTRUCTURA DE ARCHIVOS ───────────────────────────────────────

def audit_files() -> dict[str, Any]:
    section("1. ESTRUCTURA DE ARCHIVOS DEL EMBRIÓN")
    result = {}
    for fname in EMBRION_FILES:
        path = KERNEL_DIR / fname
        if not path.exists():
            print(f"  ❌ {fname}: NO EXISTE")
            result[fname] = {"exists": False}
            continue
        loc = sum(1 for _ in path.open(encoding="utf-8"))
        size = path.stat().st_size
        print(f"  ✅ {fname}: {loc} líneas, {size} bytes")
        result[fname] = {"exists": True, "loc": loc, "size": size}
    return result


# ── 2. ANÁLISIS ESTÁTICO DEL LOOP ───────────────────────────────────

def parse_python(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as e:
        print(f"  ❌ Parse error en {path.name}: {e}")
        return None


def audit_loop_structure() -> dict[str, Any]:
    section("2. ANÁLISIS ESTÁTICO DE embrion_loop.py")
    path = KERNEL_DIR / "embrion_loop.py"
    tree = parse_python(path)
    if not tree:
        return {}

    classes = []
    functions_module = []
    constants = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            methods = []
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    is_async = isinstance(child, ast.AsyncFunctionDef)
                    methods.append({
                        "name": child.name,
                        "async": is_async,
                        "line": child.lineno,
                    })
            classes.append({"name": node.name, "line": node.lineno, "methods": methods})
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            is_async = isinstance(node, ast.AsyncFunctionDef)
            functions_module.append({"name": node.name, "async": is_async, "line": node.lineno})
        elif isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id.isupper():
                    constants.append(tgt.id)

    subsec("Clases y métodos")
    for cls in classes:
        print(f"  Clase: {cls['name']} (línea {cls['line']})")
        for m in cls["methods"]:
            marker = "async" if m["async"] else "def  "
            print(f"    {marker} {m['name']}  (línea {m['line']})")

    subsec("Constantes de configuración (env vars / thresholds)")
    for c in constants:
        print(f"  {c}")

    subsec("Funciones a nivel de módulo")
    for f in functions_module:
        marker = "async" if f["async"] else "def  "
        print(f"  {marker} {f['name']}  (línea {f['line']})")

    return {"classes": classes, "constants": constants, "module_funcs": functions_module}


# ── 3. TRIGGERS DETECTADOS POR EL LOOP ──────────────────────────────

def audit_triggers() -> list[dict[str, str]]:
    section("3. TRIGGERS QUE EL LOOP RECONOCE")
    path = KERNEL_DIR / "embrion_loop.py"
    text = path.read_text(encoding="utf-8")

    # Buscar patrones tipo `"type": "X"` en returns del _detect_trigger
    # Heurística: líneas que contengan '"type"' o "'type'" + un valor literal
    trigger_pattern = re.compile(r'["\']type["\']\s*:\s*["\']([a-z_]+)["\']', re.IGNORECASE)
    triggers = trigger_pattern.findall(text)
    unique = sorted(set(triggers))

    print(f"  Tipos de trigger encontrados (literal string match): {len(unique)}")
    for t in unique:
        count = triggers.count(t)
        print(f"    - {t}  (mencionado {count}× en el archivo)")

    return [{"trigger": t, "mentions": triggers.count(t)} for t in unique]


# ── 4. TABLAS SUPABASE QUE EL LOOP CONSULTA ─────────────────────────

def audit_db_access() -> dict[str, Any]:
    section("4. ACCESO A SUPABASE DESDE EL LOOP")
    path = KERNEL_DIR / "embrion_loop.py"
    text = path.read_text(encoding="utf-8")

    # Buscar `table="X"` o `table='X'`
    table_pattern = re.compile(r'table\s*=\s*["\']([a-z_]+)["\']')
    tables = sorted(set(table_pattern.findall(text)))

    print(f"  Tablas referenciadas por el loop: {len(tables)}")
    for t in tables:
        print(f"    - {t}")

    # Buscar filtros por tipo
    filter_pattern = re.compile(r'filters\s*=\s*\{["\']tipo["\']\s*:\s*["\']([a-z_]+)["\']')
    filters_tipo = sorted(set(filter_pattern.findall(text)))
    print(f"  Filtros 'tipo' usados: {len(filters_tipo)}")
    for f in filters_tipo:
        print(f"    - tipo = '{f}'")

    return {"tables": tables, "filters_tipo": filters_tipo}


# ── 5. COMPARAR CON SCHEMA: ¿QUÉ tipos EXISTEN EN EMBRION_MEMORIA? ──

def report_expected_sql_check() -> None:
    section("5. QUERIES SQL QUE COWORK DEBE EJECUTAR APARTE")
    print("""
  El script Python NO puede ejecutar SQL contra Supabase directamente
  (requiere MCP). Cowork debe ejecutar estas 4 queries y pegar el
  resultado al lado de este reporte para tener verificación completa:

  Q1. Distribución de tipos:
      SELECT tipo, COUNT(*) FROM public.embrion_memoria
      GROUP BY tipo ORDER BY 2 DESC;

  Q2. Distribución de hilo_origen:
      SELECT hilo_origen, COUNT(*) FROM public.embrion_memoria
      GROUP BY hilo_origen ORDER BY 2 DESC;

  Q3. Cruce tipo × hilo_origen:
      SELECT tipo, hilo_origen, COUNT(*) FROM public.embrion_memoria
      GROUP BY tipo, hilo_origen ORDER BY 3 DESC;

  Q4. Frescura del loop:
      SELECT NOW() AS ahora,
             MAX(created_at) AS ultimo_row,
             NOW() - MAX(created_at) AS tiempo_sin_actividad
      FROM public.embrion_memoria;
""")


# ── 6. COSTO DEL LOOP — análisis del código ─────────────────────────

def audit_cost_model() -> dict[str, Any]:
    section("6. MODELO DE COSTO DEL LOOP (del código)")
    path = KERNEL_DIR / "embrion_loop.py"
    text = path.read_text(encoding="utf-8")

    # Extraer las constantes de configuración relevantes
    config_keys = [
        "CHECK_INTERVAL_S",
        "THINK_COOLDOWN_S",
        "DAILY_BUDGET_USD",
        "MAX_THOUGHTS_PER_DAY",
        "JUDGE_MODEL",
        "ACTOR_MODEL",
        "SILENCE_THRESHOLD",
        "CONSOLIDATION_INTERVAL",
        "SABIOS_CONSULTATION_INTERVAL",
        "RADAR_INTERVAL",
    ]

    config_values = {}
    for key in config_keys:
        pattern = re.compile(rf'{key}\s*=\s*[^=].+?\(["\']([^"\']*)["\']\s*,\s*["\']?([^"\']+?)["\']?\)')
        m = pattern.search(text)
        if m:
            config_values[key] = f"env:{m.group(1)} default={m.group(2)}"
        else:
            # Fallback: buscar asignación literal
            pattern2 = re.compile(rf'{key}\s*=\s*(.+)')
            m2 = pattern2.search(text)
            if m2:
                config_values[key] = m2.group(1).strip().split("#")[0].strip()
            else:
                config_values[key] = "NOT FOUND"
        print(f"  {key:35s} = {config_values[key]}")

    return config_values


# ── 7. VEREDICTO BINARIO ────────────────────────────────────────────

def veredicto_binario(files: dict, triggers: list, db: dict, cost: dict) -> None:
    section("7. VEREDICTO BINARIO (basado en código auditado, no en narrativa)")

    checks = []

    # Check A: ¿el loop existe operacionalmente?
    loop_ok = files.get("embrion_loop.py", {}).get("exists", False)
    checks.append(("Loop file existe", loop_ok))

    # Check B: ¿tiene mecanismo de trigger detection?
    has_triggers = len(triggers) > 0
    checks.append(("Reconoce triggers definidos en código", has_triggers))

    # Check C: ¿lee inputs de la DB?
    has_db = "embrion_memoria" in db.get("tables", [])
    checks.append(("Lee inputs de embrion_memoria", has_db))

    # Check D: ¿tiene caps de costo?
    has_budget = cost.get("DAILY_BUDGET_USD") not in (None, "NOT FOUND")
    checks.append(("Tiene cap diario de costo", has_budget))

    # Check E: ¿tiene gate de silencio?
    has_silence = cost.get("SILENCE_THRESHOLD") not in (None, "NOT FOUND")
    checks.append(("Tiene gate de silencio (silence_score)", has_silence))

    # Check F: ¿tiene Self-Verifier wired?
    has_verifier = files.get("embrion_self_verifier.py", {}).get("exists", False)
    checks.append(("Self-Verifier module existe", has_verifier))

    # Check G: ¿tiene Budget Tracker?
    has_bt = files.get("embrion_budget.py", {}).get("exists", False)
    checks.append(("Budget Tracker module existe", has_bt))

    # Check H: ¿tiene Write Policy?
    has_wp = files.get("embrion_write_policy.py", {}).get("exists", False)
    checks.append(("Write Policy module existe", has_wp))

    for label, ok in checks:
        print(f"  {'✅' if ok else '❌'} {label}")

    passed = sum(1 for _, ok in checks if ok)
    total = len(checks)
    print()
    print(f"  Score binario código: {passed}/{total}")

    print()
    print("  Para 'tiene razón de existir' vs 'quema créditos sin valor':")
    print("  → Falta verificar con SQL (ver §5):")
    print("    - Si tiene pensamientos autónomos útiles persistidos → tiene razón")
    print("    - Si solo persiste 'respuesta_embrion' a auto-prompts → quema créditos")
    print()
    print("  Cowork NO debe responder esta pregunta sin la data SQL del §5.")


def main() -> int:
    print()
    print("#" * 70)
    print("#  AUDIT EJECUTABLE — Embrión Loop")
    print("#  DSC-S-011 Sistema de Realidad Ejecutable")
    print("#  Cero narración. Solo hechos del código.")
    print("#" * 70)

    files = audit_files()
    audit_loop_structure()
    triggers = audit_triggers()
    db = audit_db_access()
    report_expected_sql_check()
    cost = audit_cost_model()
    veredicto_binario(files, triggers, db, cost)

    print()
    print("=" * 70)
    print("  FIN DEL AUDIT EJECUTABLE")
    print("  Cowork: si tu próxima afirmación NO está en este output,")
    print("  o en el resultado de las 4 queries SQL del §5, NO la digas.")
    print("=" * 70)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
