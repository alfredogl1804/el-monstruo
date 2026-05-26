#!/usr/bin/env python
"""Aplica patch idempotente a kernel/embrion_scheduler.py::add_task.

Sprint D-2 cleanup destructivo scheduled_tasks (Hilo Ejecutor 2 = manus_hilo_b).
Autorizado por: DSC-S-013_scheduled_tasks_cleanup_destructivo_v1.

Estrategia: sustitución textual exacta. El "ancla" es el primer bloque
ejecutable de add_task (post-docstring), que actualmente es:

    \"\"\"
        task.next_run = self._calculate_next_run(task)
        self._tasks[task.task_id] = task

Insertamos antes de esas dos líneas el guard de idempotencia por
(name, embrion_id). El patch se aplica solo si el ancla existe
exactamente una vez. Idempotente: si detecta que el guard ya está
aplicado (marcador "scheduler_task_idempotent_reuse"), no hace nada.

Usage:
  python3 scripts/_apply_idempotent_patch.py
  # o
  python3 scripts/_apply_idempotent_patch.py --dry-run
"""

import argparse
import sys
from pathlib import Path

TARGET = Path("kernel/embrion_scheduler.py")

ANCHOR = (
    "        Persiste en Supabase (fire-and-forget).\n"
    '        """\n'
    "        task.next_run = self._calculate_next_run(task)\n"
    "        self._tasks[task.task_id] = task\n"
)

REPLACEMENT = (
    "        Persiste en Supabase (fire-and-forget).\n"
    "\n"
    "        Idempotencia (Sprint D-2, DSC-S-013):\n"
    "        Si ya existe una tarea en memoria con la misma combinación\n"
    "        ``(name, embrion_id)`` —típicamente porque ``_restore_from_supabase``\n"
    "        la trajo de DB en el startup— se REUTILIZA el ``task_id`` existente\n"
    "        en lugar de crear una nueva fila. Esto rompe el ciclo de duplicación\n"
    "        permanente de ``scheduled_tasks`` (5 filas nuevas por arranque/redeploy).\n"
    "        Solo se refresca la definición (schedule, governance, handler);\n"
    "        el estado de ejecución (last_run, total_runs, consecutive_failures)\n"
    "        se preserva del registro existente.\n"
    '        """\n'
    "        # Guard de idempotencia por (name, embrion_id) — Sprint D-2\n"
    "        existing = next(\n"
    "            (t for t in self._tasks.values()\n"
    "             if t.name == task.name and t.embrion_id == task.embrion_id),\n"
    "            None,\n"
    "        )\n"
    "        if existing is not None:\n"
    "            # Reusar task_id existente; refrescar campos de definición\n"
    "            task.task_id = existing.task_id\n"
    "            # Preservar estado de ejecución del registro existente\n"
    "            task.last_run = existing.last_run\n"
    "            task.total_runs = existing.total_runs\n"
    "            task.total_cost_usd = existing.total_cost_usd\n"
    "            task.consecutive_failures = existing.consecutive_failures\n"
    "            task.status = existing.status\n"
    "            task.paused = existing.paused\n"
    "            logger.info(\n"
    '                "scheduler_task_idempotent_reuse",\n'
    "                task_id=task.task_id,\n"
    "                name=task.name,\n"
    "                embrion=task.embrion_id,\n"
    "            )\n"
    "\n"
    "        task.next_run = self._calculate_next_run(task)\n"
    "        self._tasks[task.task_id] = task\n"
)

MARKER = "scheduler_task_idempotent_reuse"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="No escribir, solo verificar")
    args = parser.parse_args()

    if not TARGET.exists():
        print(f"ERROR: {TARGET} no encontrado (ejecutar desde la raíz del repo)")
        return 1

    content = TARGET.read_text(encoding="utf-8")

    # Idempotencia del propio patch
    if MARKER in content:
        print(f"OK: patch ya aplicado (marcador {MARKER!r} encontrado). Nada que hacer.")
        return 0

    occurrences = content.count(ANCHOR)
    if occurrences == 0:
        print("ERROR: ancla NO encontrada en el archivo. ¿Cambió el código?")
        print("Ancla esperada (primeros 200 chars):")
        print(repr(ANCHOR[:200]))
        return 2
    if occurrences > 1:
        print(f"ERROR: ancla aparece {occurrences} veces (debería ser exactamente 1)")
        return 3

    new_content = content.replace(ANCHOR, REPLACEMENT, 1)

    # Sanidad: el resultado contiene el marcador
    if MARKER not in new_content:
        print(f"ERROR: post-replacement el marcador {MARKER!r} no aparece. Patch inválido.")
        return 4

    if args.dry_run:
        print("DRY-RUN OK — el patch se aplicaría correctamente.")
        print(f"  Lineas pre:  {len(content.splitlines())}")
        print(f"  Lineas post: {len(new_content.splitlines())}")
        return 0

    TARGET.write_text(new_content, encoding="utf-8")
    print(f"OK: patch aplicado a {TARGET}")
    print(f"  Lineas pre:  {len(content.splitlines())}")
    print(f"  Lineas post: {len(new_content.splitlines())}")
    print(f"  Marcador insertado: {MARKER}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
