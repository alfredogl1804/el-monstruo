#!/usr/bin/env python3
"""
Linter pre-commit que enforza DSC-S-006 regla 1: RLS por defecto en tablas nuevas.

Sprint S-002.6 — Tarea 5
Autor: Hilo B
Fecha: 2026-05-10

Reglas que valida sobre archivos staged en git:

1. Si un archivo `migrations/sql/*.sql` o `**/*.sql` contiene un `CREATE TABLE`
   sobre el schema `public`, debe acompañarse de:
   - Un `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` para esa tabla, O
   - Un `CREATE POLICY ... ON ...` para esa tabla, O
   - Un comentario explícito `-- DSC-S-006: skip RLS justificado: <razón>`.

2. Si el archivo contiene `CREATE MATERIALIZED VIEW` sobre `public`, debe
   acompañarse de un `REVOKE ALL ON ... FROM PUBLIC` o un comentario `-- DSC-S-006: skip`.

3. No se permite `os.environ.get("SUPABASE_*", "...")` con default value
   que parezca credencial (DSC-S-004).

Uso:
    pre-commit hook (configurado en .pre-commit-config.yaml):
        $ python3 scripts/_check_rls_default.py <archivo1> <archivo2> ...

    Manual:
        $ python3 scripts/_check_rls_default.py migrations/sql/*.sql

Exit codes:
    0 — todos los archivos pasan
    1 — uno o más archivos violan reglas (impide commit)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Patrones canónicos
CREATE_TABLE_RE = re.compile(
    r"\bCREATE\s+TABLE(?:\s+IF\s+NOT\s+EXISTS)?\s+(?:public\.)?([a-zA-Z_][a-zA-Z0-9_]*)",
    re.IGNORECASE,
)
CREATE_MATVIEW_RE = re.compile(
    r"\bCREATE\s+MATERIALIZED\s+VIEW(?:\s+IF\s+NOT\s+EXISTS)?\s+(?:public\.)?([a-zA-Z_][a-zA-Z0-9_]*)",
    re.IGNORECASE,
)
ENABLE_RLS_RE = re.compile(
    r"\bALTER\s+TABLE\s+(?:public\.)?([a-zA-Z_][a-zA-Z0-9_]*)\s+ENABLE\s+ROW\s+LEVEL\s+SECURITY",
    re.IGNORECASE,
)
CREATE_POLICY_RE = re.compile(
    r"\bCREATE\s+POLICY\s+(?:\"[^\"]+\"|[a-zA-Z_][a-zA-Z0-9_]*)\s+ON\s+(?:public\.)?([a-zA-Z_][a-zA-Z0-9_]*)",
    re.IGNORECASE,
)
REVOKE_PUBLIC_RE = re.compile(
    r"\bREVOKE\s+(?:ALL|SELECT|INSERT|UPDATE|DELETE)\b[^;]*\sON\s+(?:public\.)?([a-zA-Z_][a-zA-Z0-9_]*)\s+FROM\s+(?:PUBLIC|anon|authenticated)",
    re.IGNORECASE,
)
SKIP_RLS_RE = re.compile(
    r"--\s*DSC-S-006:\s*skip\s+RLS",
    re.IGNORECASE,
)

# DSC-S-004: anti-patrón default values con secrets
DEFAULT_SECRET_RE = re.compile(
    r"""os\.environ\.get\s*\(\s*['"](SUPABASE_[A-Z_]+|.*KEY|.*SECRET|.*TOKEN)['"]\s*,\s*['"][a-zA-Z0-9_\-\.]{16,}['"]""",
    re.IGNORECASE,
)


def strip_sql_comments(content: str) -> str:
    """Elimina comentarios SQL para evitar false positives en regex de DDL.

    Conserva los comentarios `-- DSC-S-006: skip` porque son metadatos válidos.
    """
    # Eliminar /* ... */ multilinea
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    # Eliminar comentarios `-- ...` excepto los que mencionan DSC-S-006
    lines = []
    for line in content.split("\n"):
        if "--" in line:
            idx = line.index("--")
            comment = line[idx:]
            if "DSC-S-006" in comment.upper():
                # Conservar la línea entera
                lines.append(line)
            else:
                lines.append(line[:idx])
        else:
            lines.append(line)
    return "\n".join(lines)


def check_sql_file(path: Path) -> list[str]:
    """Valida un archivo SQL. Retorna lista de errores (vacía si pasa)."""
    errors: list[str] = []
    if not path.exists():
        return errors
    raw = path.read_text(encoding="utf-8", errors="replace")

    # Permitir bypass explícito a nivel de archivo
    if SKIP_RLS_RE.search(raw):
        # Si el archivo TIENE un skip explícito, validamos solo que la skip sea
        # acompañada por una razón.
        for m in SKIP_RLS_RE.finditer(raw):
            ctx_line = raw[m.start() : m.start() + 200].split("\n")[0]
            if "justificado" not in ctx_line.lower() and ":" not in ctx_line[m.end() - m.start() :]:
                errors.append(
                    f"{path}: '-- DSC-S-006: skip RLS' debe acompañarse de razón "
                    f"(ej: '-- DSC-S-006: skip RLS justificado: tabla efímera de tests')"
                )

    # Limpiar comentarios para detectar DDL
    cleaned = strip_sql_comments(raw)

    # Tablas nuevas
    created_tables = set(m.group(1).lower() for m in CREATE_TABLE_RE.finditer(cleaned))
    rls_enabled = set(m.group(1).lower() for m in ENABLE_RLS_RE.finditer(cleaned))
    policies = set(m.group(1).lower() for m in CREATE_POLICY_RE.finditer(cleaned))

    skipped_in_file = SKIP_RLS_RE.search(raw) is not None

    for table in created_tables:
        if table in rls_enabled or table in policies:
            continue
        if skipped_in_file:
            continue
        errors.append(
            f"{path}: tabla '{table}' creada sin RLS ni policy ni skip explícito "
            f"(viola DSC-S-006 regla 1). Agregar:\n"
            f"  ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY;\n"
            f"  CREATE POLICY \"service_role_only\" ON public.{table} ... ;"
        )

    # Matviews nuevas
    created_matviews = set(m.group(1).lower() for m in CREATE_MATVIEW_RE.finditer(cleaned))
    revokes = set(m.group(1).lower() for m in REVOKE_PUBLIC_RE.finditer(cleaned))
    for mv in created_matviews:
        if mv in revokes or skipped_in_file:
            continue
        errors.append(
            f"{path}: matview '{mv}' creada sin REVOKE PUBLIC ni skip "
            f"(viola DSC-S-006 espíritu). Agregar:\n"
            f"  REVOKE ALL ON public.{mv} FROM PUBLIC;\n"
            f"  GRANT SELECT, INSERT, UPDATE, DELETE ON public.{mv} TO service_role;"
        )

    return errors


def check_python_file(path: Path) -> list[str]:
    """Valida un archivo Python contra DSC-S-004."""
    errors: list[str] = []
    if not path.exists():
        return errors
    content = path.read_text(encoding="utf-8", errors="replace")
    for m in DEFAULT_SECRET_RE.finditer(content):
        line_no = content[: m.start()].count("\n") + 1
        errors.append(
            f"{path}:{line_no}: os.environ.get() con default value sospechoso. "
            f"Usar require_env() (DSC-S-004)."
        )
    return errors


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: _check_rls_default.py <file> [file...]", file=sys.stderr)
        return 0

    all_errors: list[str] = []
    for arg in argv:
        path = Path(arg)
        if not path.exists():
            continue
        if path.suffix.lower() == ".sql":
            all_errors.extend(check_sql_file(path))
        elif path.suffix.lower() == ".py":
            all_errors.extend(check_python_file(path))

    if all_errors:
        print("DSC-S-006/004 violations detected:\n", file=sys.stderr)
        for e in all_errors:
            print(f"  - {e}\n", file=sys.stderr)
        print(
            "Para hacer bypass legítimo, agregar comentario en el archivo:\n"
            "  -- DSC-S-006: skip RLS justificado: <razón>\n",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
