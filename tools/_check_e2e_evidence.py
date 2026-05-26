"""DSC-G-010: Verifica que un PR adjunte evidencia E2E binaria.

Uso:
    python3 tools/_check_e2e_evidence.py <PR_BODY>

Reglas (parseo del body):
    1. Debe contener una sección con encabezado `## E2E Evidence` (case-insensitive).
    2. Esa sección debe tener al menos UNA de las siguientes evidencias binarias:
       - URL HTTP/HTTPS (logs Railway, screenshots, artifacts)
       - Path a archivo en el repo (`reports/...`, `tests/...`, `bridge/...`)
       - SHA de commit (`[a-f0-9]{7,40}`)
       - Bloque de código con resultado de pytest/jest/etc (líneas con `passed`, `failed`, `OK`)

Exit codes:
    0 = evidencia válida encontrada
    1 = sección presente pero vacía / sin evidencia binaria
    2 = sección `## E2E Evidence` ausente

Bypass legítimos (NO usar este checker):
    - PR con label `no-e2e-required` (typo fix, doc-only)
    - PR con label `e2e-evidence-bypass` (emergency hotfix con justificación)
"""

from __future__ import annotations

import re
import sys
from typing import Tuple

# Encabezado exacto requerido (DSC-G-010)
SECTION_HEADER_REGEX = re.compile(
    r"^##\s+E2E\s+Evidence\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# Patrones de evidencia binaria aceptados
URL_REGEX = re.compile(r"https?://[^\s<>)]+", re.IGNORECASE)
REPO_PATH_REGEX = re.compile(
    r"(?:^|\s|`)((?:reports|tests|scripts|bridge|migrations|kernel|tools|.github)/[\w./_-]+)",
    re.MULTILINE,
)
COMMIT_SHA_REGEX = re.compile(r"\b[a-f0-9]{7,40}\b")
TEST_RESULT_REGEX = re.compile(
    r"\b(?:\d+\s+(?:passed|failed|skipped|errors?)|OK|smoke\s+\d/\d)\b",
    re.IGNORECASE,
)


def extract_evidence_section(body: str) -> str | None:
    """Extrae el contenido de la sección `## E2E Evidence` hasta el siguiente `## ` o EOF."""
    match = SECTION_HEADER_REGEX.search(body)
    if not match:
        return None
    start = match.end()
    next_header = re.search(r"^##\s+\S", body[start:], re.MULTILINE)
    end = start + next_header.start() if next_header else len(body)
    return body[start:end].strip()


def check_binary_evidence(section: str) -> Tuple[bool, list[str]]:
    """Devuelve (válido, lista de evidencias detectadas)."""
    found: list[str] = []
    if URL_REGEX.search(section):
        urls = URL_REGEX.findall(section)
        found.extend(f"url:{u}" for u in urls[:3])
    if REPO_PATH_REGEX.search(section):
        paths = REPO_PATH_REGEX.findall(section)
        found.extend(f"path:{p}" for p in paths[:3])
    if COMMIT_SHA_REGEX.search(section):
        shas = COMMIT_SHA_REGEX.findall(section)
        found.extend(f"sha:{s}" for s in shas[:3])
    if TEST_RESULT_REGEX.search(section):
        tests = TEST_RESULT_REGEX.findall(section)
        found.extend(f"test:{t}" for t in tests[:3])
    return (len(found) > 0, found)


def check_pr_body(body: str) -> Tuple[int, str]:
    """Verifica el body del PR. Devuelve (exit_code, mensaje)."""
    if not body or not body.strip():
        return (2, "DSC-G-010 FALLA: PR body vacio. Seccion `## E2E Evidence` requerida.")

    section = extract_evidence_section(body)
    if section is None:
        return (
            2,
            "DSC-G-010 FALLA: seccion `## E2E Evidence` ausente en el body del PR. "
            "Agregar esa seccion con al menos una URL/path/SHA/test result, o aplicar el "
            "label `no-e2e-required` (doc-only) o `e2e-evidence-bypass` (emergency).",
        )

    valid, evidence = check_binary_evidence(section)
    if not valid:
        return (
            1,
            f"DSC-G-010 FALLA: seccion `## E2E Evidence` presente pero sin evidencia "
            f"binaria. Contenido encontrado: {section[:200]!r}. Necesario: URL HTTP, path "
            f"a archivo del repo, SHA de commit, o resultado de tests (passed/failed/OK).",
        )

    return (
        0,
        f"DSC-G-010 OK: {len(evidence)} evidencia(s) binaria(s) detectada(s): "
        + ", ".join(evidence[:5])
        + ("..." if len(evidence) > 5 else ""),
    )


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("ERROR: pasar el body del PR como primer argumento.", file=sys.stderr)
        return 3

    body = argv[1]
    exit_code, msg = check_pr_body(body)
    if exit_code == 0:
        print(msg)
    else:
        print(msg, file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
