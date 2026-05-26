#!/usr/bin/env python3
"""
run_all.py — Orquestador del Genome Vivo (Sprint 91 F6/F7/F8).

Corre los 4 scanners + aggregator en secuencia, guarda un snapshot
con timestamp, compara con la corrida anterior, y reporta diff.

Uso:
  python3 scripts/genome_live/run_all.py

Output:
  _genome_out/runs/YYYYMMDDTHHMMSSZ/{github,railway,supabase,live24h,genome_now}.json
  _genome_out/runs/last_diff.json

Verificación binaria de estabilidad (F8):
  3 corridas consecutivas con binario_100=True separadas por ≥1h
  → genome es estable.

Autor: Manus — Sprint 91
"""

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT / "_genome_out"
RUNS_DIR = OUT_DIR / "runs"
SCRIPTS = ROOT / "scripts" / "genome_live"

SCANNERS = [
    ("github", SCRIPTS / "github_scanner.py"),
    ("railway", SCRIPTS / "railway_scanner.py"),
    ("supabase", SCRIPTS / "supabase_scanner.py"),
    ("live24h", SCRIPTS / "live24h_scanner.py"),
]
AGGREGATOR = SCRIPTS / "aggregator.py"


def run_script(script: Path) -> tuple[bool, str]:
    """Corre un script Python; devuelve (ok, tail_stdout)."""
    try:
        proc = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=900,
            cwd=str(ROOT),
        )
        ok = proc.returncode == 0
        tail = (proc.stdout or "").strip().splitlines()[-3:]
        if not ok:
            tail.append(f"[stderr] {(proc.stderr or '')[-200:]}")
        return ok, "\n  ".join(tail)
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)


def snapshot_to_run(run_dir: Path) -> None:
    """Copia los outputs actuales a run_dir/."""
    run_dir.mkdir(parents=True, exist_ok=True)
    for name in ["github", "railway", "supabase", "live24h", "genome_now"]:
        src = OUT_DIR / f"{name}.json"
        if src.exists():
            shutil.copy(src, run_dir / src.name)


def previous_run() -> Path | None:
    if not RUNS_DIR.exists():
        return None
    runs = sorted([p for p in RUNS_DIR.iterdir() if p.is_dir()], reverse=True)
    return runs[0] if runs else None


def compare_runs(prev: Path, curr: Path) -> dict[str, Any]:
    """Compara conteos clave entre dos corridas."""
    diffs: dict[str, Any] = {}
    for fname in ["github.json", "railway.json", "supabase.json", "live24h.json"]:
        p_old = prev / fname
        p_new = curr / fname
        if not (p_old.exists() and p_new.exists()):
            continue
        try:
            old = json.loads(p_old.read_text())
            new = json.loads(p_new.read_text())
        except Exception:
            continue

        keys: list[str] = []
        if fname == "github.json":
            keys = ["repos_count"]
        elif fname == "railway.json":
            keys = ["projects_count", "total_services", "total_environments"]
        elif fname == "supabase.json":
            keys = ["schemas_count", "tables_count", "functions_count", "extensions_count", "migrations_count"]
        elif fname == "live24h.json":
            keys = ["github_commits_24h_count", "railway_deploys_24h_count", "drift_services_over_7d_count"]

        per_file: dict[str, Any] = {}
        for k in keys:
            o = old.get(k)
            n = new.get(k)
            if o != n:
                per_file[k] = {"old": o, "new": n, "diff": (n or 0) - (o or 0)}
        if per_file:
            diffs[fname] = per_file
    return diffs


def main() -> int:
    started = datetime.now(timezone.utc)
    ts = started.strftime("%Y%m%dT%H%M%SZ")
    print(f"[{started.isoformat()}] run_all START")

    prev = previous_run()
    if prev:
        print(f"  corrida anterior: {prev.name}")

    # 1. Run scanners
    results: dict[str, dict[str, Any]] = {}
    for name, script in SCANNERS:
        if not script.exists():
            results[name] = {"ok": False, "tail": f"{script} no existe"}
            continue
        print(f"  → {name}_scanner.py ...", flush=True)
        ok, tail = run_script(script)
        results[name] = {"ok": ok, "tail": tail}
        print(f"    ok={ok}\n  {tail}", flush=True)

    # 2. Aggregator
    print(f"  → aggregator.py ...", flush=True)
    agg_ok, agg_tail = run_script(AGGREGATOR)
    results["aggregator"] = {"ok": agg_ok, "tail": agg_tail}
    print(f"    ok={agg_ok}\n  {agg_tail}", flush=True)

    # 3. Snapshot
    run_dir = RUNS_DIR / ts
    snapshot_to_run(run_dir)
    print(f"  snapshot guardado: {run_dir}", flush=True)

    # 4. Diff vs corrida anterior
    diff: dict[str, Any] = {}
    if prev:
        diff = compare_runs(prev, run_dir)

    # 5. binario_100 actual
    genome_path = run_dir / "genome_now.json"
    binario_100 = False
    if genome_path.exists():
        try:
            data = json.loads(genome_path.read_text())
            binario_100 = data.get("meta", {}).get("binario_100", False)
        except Exception:
            pass

    finished = datetime.now(timezone.utc)
    summary = {
        "ts": ts,
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "duration_seconds": (finished - started).total_seconds(),
        "previous_run": prev.name if prev else None,
        "scanner_results": results,
        "binario_100": binario_100,
        "diff_vs_previous": diff,
        "diff_count": sum(len(v) for v in diff.values()) if diff else 0,
    }

    (RUNS_DIR / "last_diff.json").write_text(json.dumps(summary, indent=2, default=str))

    print(f"\nRUN ALL RESUMEN")
    print(f"  ts                : {ts}")
    print(f"  duration_s        : {summary['duration_seconds']:.1f}")
    print(f"  binario_100       : {binario_100}")
    print(f"  diff_vs_previous  : {summary['diff_count']} cambios")
    if diff:
        for fname, changes in diff.items():
            print(f"    {fname}: {changes}")

    # 6. Aggregator a la raíz también (idempotente)
    if (run_dir / "genome_now.json").exists():
        shutil.copy(run_dir / "genome_now.json", OUT_DIR / "genome_now.json")

    return 0 if binario_100 else 1


if __name__ == "__main__":
    sys.exit(main())
