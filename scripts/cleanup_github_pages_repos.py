#!/usr/bin/env python3
"""Sprint 88 Tarea 3.B.1 — Cleanup de repos GitHub Pages acumulados.

Política TTL del Monstruo:
- El pipeline E2E crea un repo público `monstruo-{slug}-{run_id_short}` por cada deploy real.
- Los repos NO se borran automáticamente al final del run (deliberado: la URL queda viva
  para que Cowork audite y para que el Critic Visual tenga screenshot histórico).
- Este script ejecuta cleanup batch con tres modos:
    * --older-than-days N   (default 7): borra repos con createdAt > N días
    * --keep-last-n N       : conserva los N más recientes y borra el resto
    * --all                 : wipe completo (requiere doble confirmación)
- Por defecto corre en dry-run. Usar --execute para borrar de verdad.

Brand DNA (errores):
- e2e_cleanup_list_failed
- e2e_cleanup_delete_failed

Ejecución manual recomendada (DSC-S-005: archive default, reversible):
    # Ver qué se cleanearía
    python3 scripts/cleanup_github_pages_repos.py --older-than-days 7

    # Archivar repos > 7 días (recomendado, reversible — DSC-S-005)
    python3 scripts/cleanup_github_pages_repos.py --older-than-days 7 --archive --execute

    # Conservar últimos 5, archivar el resto (DSC-S-005)
    python3 scripts/cleanup_github_pages_repos.py --keep-last-n 5 --archive --execute

    # Borrar repos (irreversible, requiere scope delete_repo)
    python3 scripts/cleanup_github_pages_repos.py --keep-last-n 5 --delete --execute

    # Wipe total (cuidado)
    python3 scripts/cleanup_github_pages_repos.py --all --archive --execute --confirm

Política Cowork-DSC-G-008: este script NO toca repos del codebase del Monstruo
(el-monstruo, monstruo-memoria, monstruo-tickets, etc.). Solo afecta repos con
prefijo `monstruo-` que NO sean parte del registro persistente del Monstruo.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

# Pattern para eliminar ANSI escape codes (gh los inyecta aún con NO_COLOR en algunas versiones)
_ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")

# Repos PROTEGIDOS — nunca borrar aunque empiecen con "monstruo-"
PROTECTED_REPOS = frozenset(
    {
        "el-monstruo",
        "monstruo-memoria",
        "monstruo-tickets",
        "monstruo-mvp",
        "monstruo-app",
        "monstruo-tracking",
    }
)

# Patrón canónico de repos generados por el pipeline E2E
# Ejemplo: monstruo-hace-una-landing-premium-para--3_888e5d
PIPELINE_PREFIX = "monstruo-"
PIPELINE_OWNER = "alfredogl1804"


def _run(cmd: list[str], capture: bool = True) -> tuple[int, str, str]:
    """Ejecuta comando y devuelve (rc, stdout, stderr).

    Fuerza NO_COLOR para que `gh --json` devuelva JSON puro sin ANSI escapes
    (gh detecta TTY incorrectamente bajo subprocess.PIPE en algunas versiones).
    """
    env = os.environ.copy()
    env["NO_COLOR"] = "1"
    env["GH_NO_COLOR"] = "1"
    env["CLICOLOR"] = "0"
    result = subprocess.run(cmd, capture_output=capture, text=True, env=env)
    return result.returncode, result.stdout, result.stderr


def list_pipeline_repos() -> list[dict]:
    """Lista todos los repos pipeline (monstruo-* sin protegidos)."""
    cmd = [
        "gh",
        "repo",
        "list",
        PIPELINE_OWNER,
        "--limit",
        "500",
        "--json",
        "name,createdAt,description,visibility",
    ]
    rc, stdout, stderr = _run(cmd)
    if rc != 0:
        print(f"e2e_cleanup_list_failed: gh exit {rc}: {stderr}", file=sys.stderr)
        sys.exit(1)
    # gh a veces inyecta ANSI escape codes incluso con --json y NO_COLOR. Strip defensivo.
    clean_stdout = _ANSI_ESCAPE_RE.sub("", stdout)
    try:
        data = json.loads(clean_stdout)
    except json.JSONDecodeError as e:
        print(
            f"e2e_cleanup_list_failed: JSON decode error: {e}\nFirst 200 chars: {clean_stdout[:200]!r}",
            file=sys.stderr,
        )
        sys.exit(1)

    pipeline = []
    for repo in data:
        name = repo["name"]
        if not name.startswith(PIPELINE_PREFIX):
            continue
        if name in PROTECTED_REPOS:
            continue
        # Heurística adicional: el repo del pipeline tiene el sufijo `_{6_hex}` al final
        # (los últimos 8 chars del run_id). Si no lo tiene, no es del pipeline.
        if "_" not in name:
            continue
        pipeline.append(repo)
    return pipeline


def filter_older_than(repos: list[dict], days: int) -> list[dict]:
    """Repos creados hace más de N días."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    out = []
    for r in repos:
        created = datetime.fromisoformat(r["createdAt"].replace("Z", "+00:00"))
        if created < cutoff:
            out.append(r)
    return out


def select_keep_last_n(repos: list[dict], keep: int) -> list[dict]:
    """Devuelve los repos a borrar (los más viejos), conservando los `keep` más nuevos."""
    sorted_repos = sorted(repos, key=lambda r: r["createdAt"], reverse=True)
    return sorted_repos[keep:]


def delete_repo(name: str, owner: str = PIPELINE_OWNER) -> bool:
    """Borra repo via gh CLI (irreversible). Requiere scope delete_repo."""
    cmd = ["gh", "repo", "delete", f"{owner}/{name}", "--yes"]
    rc, _, stderr = _run(cmd)
    if rc != 0:
        print(f"  e2e_cleanup_delete_failed: {name}: {stderr.strip()}", file=sys.stderr)
        return False
    return True


def archive_repo(name: str, owner: str = PIPELINE_OWNER) -> bool:
    """Archiva repo via gh CLI (reversible — DSC-S-005). Solo requiere scope `repo`."""
    cmd = ["gh", "repo", "archive", f"{owner}/{name}", "--yes"]
    rc, _, stderr = _run(cmd)
    if rc != 0:
        print(f"  e2e_cleanup_archive_failed: {name}: {stderr.strip()}", file=sys.stderr)
        return False
    return True


def parse_args():
    p = argparse.ArgumentParser(
        description="Cleanup de repos GitHub Pages generados por el pipeline E2E del Monstruo"
    )
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--older-than-days",
        type=int,
        metavar="N",
        help="Borrar repos creados hace más de N días",
    )
    mode.add_argument(
        "--keep-last-n",
        type=int,
        metavar="N",
        help="Conservar los N repos más recientes, borrar el resto",
    )
    mode.add_argument(
        "--all",
        action="store_true",
        help="Wipe total de repos pipeline (requiere --confirm)",
    )
    p.add_argument(
        "--execute",
        action="store_true",
        help="Ejecutar la operación de verdad (default: dry-run)",
    )
    p.add_argument(
        "--confirm",
        action="store_true",
        help="Confirmación explícita requerida para --all",
    )
    op = p.add_mutually_exclusive_group()
    op.add_argument(
        "--archive",
        action="store_true",
        help="Archivar (reversible) — DEFAULT por DSC-S-005.",
    )
    op.add_argument(
        "--delete",
        action="store_true",
        help="Borrar (irreversible). Requiere scope delete_repo.",
    )
    return p.parse_args()


def main():
    args = parse_args()

    print("Sprint 88 Tarea 3.B.1 — Cleanup de repos GitHub Pages")
    print("=" * 60)

    if args.all and not args.confirm:
        print("Error: --all requiere también --confirm para evitar accidentes.")
        sys.exit(2)

    print("Listando repos pipeline...")
    repos = list_pipeline_repos()
    print(f"Total repos pipeline (monstruo-*): {len(repos)}")
    print(f"Total repos protegidos (excluidos): {len(PROTECTED_REPOS)}")
    print()

    if args.all:
        target = repos
        reason = "TODOS los repos pipeline"
    elif args.older_than_days is not None:
        target = filter_older_than(repos, args.older_than_days)
        reason = f"creados hace más de {args.older_than_days} días"
    else:  # keep_last_n
        target = select_keep_last_n(repos, args.keep_last_n)
        reason = f"todos excepto los {args.keep_last_n} más recientes"

    # Determinar operación: archive (default por DSC-S-005) o delete
    if args.delete:
        op_label = "borrar"
        op_func = delete_repo
    else:
        # Default = archive (incluso si no se pasa --archive explícito)
        op_label = "archivar"
        op_func = archive_repo

    print(f"A {op_label} ({reason}): {len(target)}")
    if not target:
        print("Nada que procesar. Saliendo limpio.")
        return 0

    # Mostrar primeros 10
    sorted_target = sorted(target, key=lambda r: r["createdAt"])
    print()
    print(f"{'CREATED':<20}  {'NAME'}")
    for r in sorted_target[:10]:
        print(f"  {r['createdAt'][:19]}  {r['name']}")
    if len(sorted_target) > 10:
        print(f"  ... y {len(sorted_target) - 10} más")

    if not args.execute:
        print()
        print(f"Modo DRY-RUN. Para {op_label} de verdad, agregar --execute")
        return 0

    print()
    print(f"Procesando {len(target)} repos ({op_label})...")
    ok = 0
    failed = 0
    for r in sorted_target:
        if op_func(r["name"]):
            ok += 1
            print(f"  [OK] {r['name']}")
        else:
            failed += 1

    print()
    print(f"Resultado: {ok} {op_label}dos, {failed} fallaron")
    if failed > 0:
        sys.exit(1)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
