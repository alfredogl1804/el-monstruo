#!/usr/bin/env python3
"""
DTA Sync — Orquestador de las 4 automatizaciones de la bitácora.

Automatizaciones:
  1. Commit + Push automático (≥5 líneas nuevas o cierre de bloque)
  2. Index auto-regenerado (bitacora_index.md)
  3. Guardian memoria persistente (POST /v1/memory/thoughts)
  4. Genome Vivo actualizado (placeholder → _guardian_pending.jsonl)

Uso:
  python3 dta_sync.py              # Ejecuta pipeline completo
  python3 dta_sync.py --dry-run    # Muestra qué haría sin ejecutar
  python3 dta_sync.py --force      # Fuerza sync sin umbral de 5 líneas

Requisitos:
  - Python 3.9+ (stdlib only, zero dependencies)
  - git en PATH
  - Variable KERNEL_API_KEY en env (para Guardian, opcional)

Autoría: Hilo B (Manus), Sprint DTA-AUTOMATIZACIONES, 2026-05-29.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Constantes ───────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[2]
FORJA_DIR = REPO_ROOT / "forja_omega_tramo_1"
BITACORA = FORJA_DIR / "bitacora.jsonl"
INDEX_MD = FORJA_DIR / "bitacora_index.md"
PENDING_LOG = FORJA_DIR / "_guardian_pending.jsonl"

KERNEL_URL = os.environ.get(
    "KERNEL_BASE_URL",
    "https://el-monstruo-kernel-production.up.railway.app",
)
KERNEL_API_KEY = os.environ.get("KERNEL_API_KEY") or os.environ.get("MONSTRUO_API_KEY")

MIN_NEW_LINES = 5  # Umbral para auto-commit


# ─── Helpers ──────────────────────────────────────────────────────────────────


def run(cmd: list[str], cwd: Path = REPO_ROOT, check: bool = True) -> subprocess.CompletedProcess:
    """Ejecutar comando shell con output capturado."""
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)


def log(msg: str, level: str = "INFO") -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[DTA {ts}] [{level}] {msg}")


def load_jsonl(path: Path) -> list[dict]:
    """Carga todas las líneas JSONL válidas."""
    events = []
    if not path.exists():
        return events
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return events


def count_committed_lines() -> int:
    """Cuenta líneas de bitacora.jsonl en el último commit."""
    result = run(
        ["git", "show", "HEAD:forja_omega_tramo_1/bitacora.jsonl"],
        check=False,
    )
    if result.returncode != 0:
        return 0
    return len([l for l in result.stdout.splitlines() if l.strip()])


def has_close_event(events: list[dict], committed_count: int) -> bool:
    """Detecta si hay un evento de cierre en las líneas nuevas."""
    new_events = events[committed_count:]
    for ev in new_events:
        if ev.get("t") == "estado" and "cerrada" in ev.get("ref", "").lower():
            return True
        if ev.get("t") == "estado" and "cerrada" in ev.get("c", "").lower():
            return True
    return False


# ─── Automatización 2: Regenerar Index ────────────────────────────────────────


def regenerate_index(events: list[dict]) -> str:
    """Genera el contenido de bitacora_index.md a partir de los eventos."""

    doctrinas = [e for e in events if e.get("t") == "doctrina"]
    chispas = [e for e in events if e.get("t") == "chispa" and e.get("a") == "alfredo"]
    antipatrones = [e for e in events if e.get("t") == "antipattern"]
    estados = [e for e in events if e.get("t") == "estado"]
    verbatims = [e for e in events if e.get("v")]

    # Extraer estado de Q
    q_states = {}
    for ev in estados:
        ref = ev.get("ref", "")
        content = ev.get("c", "")
        if ref.startswith("Q") or "Q" in ref[:3]:
            q_states[ref] = content

    lines = []
    lines.append("# BITACORA TRAMO 1 (CAPÍTULO 1) — INDEX AUTO-GENERADO")
    lines.append("")
    lines.append(f"> Generado automáticamente por `dta_sync.py` el {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ')}")
    lines.append(f"> Total eventos JSONL: {len(events)}")
    lines.append("")

    # Doctrinas
    lines.append("## Doctrinas firmadas")
    lines.append("")
    if doctrinas:
        lines.append("| # | Sigla | Nombre |")
        lines.append("|---|-------|--------|")
        for i, d in enumerate(doctrinas, 1):
            ref = d.get("ref", "?")
            content = d.get("c", "")
            lines.append(f"| {i} | {ref} | {content[:80]} |")
    else:
        lines.append("_(ninguna registrada)_")
    lines.append("")

    # Chispas del piloto
    lines.append("## Chispas del piloto (Alfredo)")
    lines.append("")
    if chispas:
        for ch in chispas:
            ref = ch.get("ref", "?")
            content = ch.get("c", "")[:100]
            lines.append(f"- **{ref}**: {content}")
    else:
        lines.append("_(ninguna registrada)_")
    lines.append("")

    # Anti-patrones
    lines.append("## Anti-patrones detectados")
    lines.append("")
    if antipatrones:
        for ap in antipatrones:
            ref = ap.get("ref", "?")
            content = ap.get("c", "")[:100]
            lines.append(f"- **{ref}**: {content}")
    else:
        lines.append("_(ninguno registrado)_")
    lines.append("")

    # Estado de las Q
    lines.append("## Estado de las Q")
    lines.append("")
    if q_states:
        for q, state in q_states.items():
            lines.append(f"- **{q}**: {state[:120]}")
    else:
        # Extraer de estados generales
        for ev in estados[-10:]:
            ref = ev.get("ref", "")
            c = ev.get("c", "")[:120]
            lines.append(f"- **{ref}**: {c}")
    lines.append("")

    # Últimas 5 citas verbatim
    lines.append("## Últimas 5 citas verbatim")
    lines.append("")
    for v in verbatims[-5:]:
        quote = v.get("v", "")
        author = v.get("a", "?")
        lines.append(f'> *"{quote}"* — {author}')
        lines.append("")

    # DTA estado
    lines.append("## DTA Triple-Anclaje — Estado operativo")
    lines.append("")
    lines.append("| Ancla | Estado |")
    lines.append("|-------|--------|")
    lines.append("| 1. Ruta canónica en repo | ✅ ACTIVA |")
    lines.append("| 2. Guardian memoria persistente | ⚡ AUTO (dta_sync.py) |")
    lines.append("| 3. Genome Vivo via API | ⚡ PLACEHOLDER (sin endpoint PATCH) |")
    lines.append("")

    return "\n".join(lines) + "\n"


# ─── Automatización 3: Guardian Memoria Persistente ───────────────────────────


def build_guardian_payload(events: list[dict], new_count: int) -> dict:
    """Construye el payload para POST /v1/memory/thoughts (schema real del kernel)."""
    new_events = events[-new_count:] if new_count > 0 else events[-5:]

    doctrinas_new = [e for e in new_events if e.get("t") == "doctrina"]
    chispas_new = [e for e in new_events if e.get("t") == "chispa" and e.get("a") == "alfredo"]
    antipatrones_new = [e for e in new_events if e.get("t") == "antipattern"]
    estados_new = [e for e in new_events if e.get("t") == "estado"]

    summary_parts = []
    if doctrinas_new:
        siglas = ", ".join(e.get("ref", "?") for e in doctrinas_new)
        summary_parts.append(f"Doctrinas nuevas: {siglas}")
    if chispas_new:
        refs = ", ".join(e.get("ref", "?") for e in chispas_new)
        summary_parts.append(f"Chispas piloto: {refs}")
    if antipatrones_new:
        refs = ", ".join(e.get("ref", "?") for e in antipatrones_new)
        summary_parts.append(f"Anti-patrones: {refs}")
    if estados_new:
        last_state = estados_new[-1].get("c", "")[:200]
        summary_parts.append(f"Último estado: {last_state}")

    summary = " | ".join(summary_parts) if summary_parts else f"Auto-sync {new_count} eventos bitácora"
    content = f"[DTA-auto] Bitácora Forja Omega Tramo 1: {summary}"

    # Schema real: CreateThoughtRequest (required: layer, content)
    return {
        "layer": "episodic",
        "content": content,
        "summary": f"DTA auto-sync: +{new_count} eventos bitácora",
        "tags": ["dta-auto", "forja-omega", "bitacora"],
        "importance": 6,
        "project": "forja_omega_tramo_1",
        "source": "dta_sync",
        "source_ref": f"bitacora.jsonl:{len(events)}",
        "agent_id": "dta_sync_pipeline",
        "metadata": {
            "total_events": len(events),
            "new_events": new_count,
            "doctrinas_count": len([e for e in events if e.get("t") == "doctrina"]),
            "last_ts": events[-1].get("ts", "") if events else "",
            "auto": True,
        },
        "generate_embedding": True,
    }


def post_guardian(payload: dict, dry_run: bool = False) -> bool:
    """POST al endpoint de memoria del kernel."""
    if not KERNEL_API_KEY:
        log("KERNEL_API_KEY no disponible — guardando en _guardian_pending.jsonl", "WARN")
        return False

    if dry_run:
        log(f"[DRY-RUN] POST /v1/memory/thoughts: {json.dumps(payload, ensure_ascii=False)[:200]}")
        return True

    import urllib.request
    import urllib.error

    url = f"{KERNEL_URL}/v1/memory/thoughts"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": KERNEL_API_KEY,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            log(f"Guardian OK: {resp.status}")
            return True
    except urllib.error.HTTPError as e:
        log(f"Guardian HTTP {e.code}: {e.read().decode()[:200]}", "ERROR")
        return False
    except Exception as e:
        log(f"Guardian error: {e}", "ERROR")
        return False


# ─── Automatización 4: Genome Vivo (placeholder) ─────────────────────────────


def build_genome_payload(events: list[dict]) -> dict:
    """Construye payload para actualización de Genome (placeholder)."""
    doctrinas = [e for e in events if e.get("t") == "doctrina"]
    estados = [e for e in events if e.get("t") == "estado"]

    q_cerradas = sum(1 for e in estados if "cerrada" in e.get("c", "").lower())
    q_abiertas = sum(1 for e in estados if "abierta" in e.get("c", "").lower() or "pendiente" in e.get("c", "").lower())

    return {
        "doctrinas_firmadas_count": len(doctrinas),
        "ultima_doctrina_firmada": f"{doctrinas[-1].get('ref', '?')} — {doctrinas[-1].get('c', '')[:60]}" if doctrinas else "ninguna",
        "ultimo_evento_bitacora_ts": events[-1].get("ts", "") if events else "",
        "fase_detonacion_estado": f"Q cerradas: {q_cerradas}, Q abiertas/pendientes: {q_abiertas}",
        "total_eventos": len(events),
    }


def log_genome_pending(payload: dict) -> None:
    """Guarda payload en _guardian_pending.jsonl para envío manual posterior."""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "target": "genome_vivo",
        "payload": payload,
        "status": "pending",
    }
    with open(PENDING_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    log(f"Genome payload guardado en {PENDING_LOG.name}")


# ─── Automatización 1: Commit + Push ─────────────────────────────────────────


def git_commit_and_push(new_count: int, dry_run: bool = False) -> bool:
    """Commitea y pushea los cambios de forja_omega_tramo_1/."""
    branch = run(["git", "branch", "--show-current"]).stdout.strip()

    # Stage solo archivos de forja_omega_tramo_1/
    files_to_add = [
        "forja_omega_tramo_1/bitacora.jsonl",
        "forja_omega_tramo_1/bitacora_index.md",
    ]

    if dry_run:
        log(f"[DRY-RUN] git add {' '.join(files_to_add)}")
        log(f"[DRY-RUN] git commit -m 'auto-sync: bitácora +{new_count} eventos [DTA-auto]'")
        log(f"[DRY-RUN] git push origin {branch}")
        return True

    for f in files_to_add:
        if (REPO_ROOT / f).exists():
            run(["git", "add", f])

    # Verificar si hay cambios staged
    status = run(["git", "diff", "--cached", "--stat"], check=False)
    if not status.stdout.strip():
        log("Sin cambios staged — nada que commitear")
        return False

    # Commit
    msg = f"auto-sync: bitácora +{new_count} eventos [DTA-auto]"
    result = run(["git", "commit", "-m", msg], check=False)
    if result.returncode != 0:
        if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
            log("Nada que commitear")
            return False
        log(f"Commit falló: {result.stderr}", "ERROR")
        return False
    log(f"Commit OK: {msg}")

    # Push
    result = run(["git", "push", "origin", branch], check=False)
    if result.returncode != 0:
        log(f"Push falló: {result.stderr}", "ERROR")
        log("Posible conflicto de merge — requiere intervención manual")
        return False
    log(f"Push OK → origin/{branch}")
    return True


# ─── Pipeline Principal ──────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description="DTA Sync — Orquestador de automatizaciones")
    parser.add_argument("--dry-run", action="store_true", help="Muestra qué haría sin ejecutar")
    parser.add_argument("--force", action="store_true", help="Fuerza sync sin umbral de 5 líneas")
    parser.add_argument("--index-only", action="store_true", help="Solo regenera el index")
    args = parser.parse_args()

    log("═══ DTA SYNC — Pipeline de automatizaciones ═══")

    # Cargar bitácora
    if not BITACORA.exists():
        log(f"Bitácora no encontrada: {BITACORA}", "ERROR")
        return 1

    events = load_jsonl(BITACORA)
    total = len(events)
    committed = count_committed_lines()
    new_count = total - committed

    log(f"Bitácora: {total} eventos totales, {committed} commiteados, {new_count} nuevos")

    # Decidir si hay trigger
    should_sync = args.force or new_count >= MIN_NEW_LINES or has_close_event(events, committed)

    if not should_sync and not args.index_only:
        log(f"Sin trigger (nuevos={new_count} < umbral={MIN_NEW_LINES}, sin cierre). Usa --force para forzar.")
        return 0

    # AUTO 2: Regenerar index
    log("── Auto 2: Regenerando index ──")
    index_content = regenerate_index(events)
    if args.dry_run:
        log(f"[DRY-RUN] Escribiría {len(index_content)} bytes en {INDEX_MD.name}")
    else:
        INDEX_MD.write_text(index_content, encoding="utf-8")
        log(f"Index regenerado: {len(index_content)} bytes")

    if args.index_only:
        log("── Modo --index-only: terminado ──")
        return 0

    # AUTO 1: Commit + Push
    log("── Auto 1: Commit + Push ──")
    push_ok = git_commit_and_push(new_count, dry_run=args.dry_run)

    # AUTO 3: Guardian memoria persistente
    log("── Auto 3: Guardian memoria persistente ──")
    guardian_payload = build_guardian_payload(events, new_count)
    guardian_ok = post_guardian(guardian_payload, dry_run=args.dry_run)
    if not guardian_ok and not args.dry_run:
        # Fallback: guardar en pending log
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "target": "guardian_memory",
            "payload": guardian_payload,
            "status": "pending",
        }
        with open(PENDING_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        log(f"Guardian payload guardado en {PENDING_LOG.name} para envío posterior")

    # AUTO 4: Genome Vivo (placeholder)
    log("── Auto 4: Genome Vivo (placeholder) ──")
    genome_payload = build_genome_payload(events)
    if args.dry_run:
        log(f"[DRY-RUN] Genome payload: {json.dumps(genome_payload, ensure_ascii=False)[:200]}")
    else:
        log_genome_pending(genome_payload)

    # Resumen
    log("═══ RESUMEN ═══")
    log(f"  Eventos procesados: {total} ({new_count} nuevos)")
    log(f"  Index regenerado: ✅")
    log(f"  Commit+Push: {'✅' if push_ok else '❌ (ver log)'}")
    log(f"  Guardian: {'✅' if guardian_ok else '⚠️ (en pending log)'}")
    log(f"  Genome: ⚠️ (placeholder, sin endpoint PATCH)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
