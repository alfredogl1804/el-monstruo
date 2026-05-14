"""tools/cowork_calibration_report.py — Sprint COWORK-MEMENTO-001 T4

CLI report agregando `public.cowork_claims_calibration` de los últimos N días.

Uso:
    python3 -m tools.cowork_calibration_report --days 7
    python3 -m tools.cowork_calibration_report --days 1 --output report.json
    python3 -m tools.cowork_calibration_report --days 7 --claim-type file_path

Output: JSON estructurado con shape:
    {
      "days": N,
      "total_claims": M,
      "by_type": {
        "file_path": {
          "verified_pre": X,
          "verified_post_match": Y,
          "verified_post_mismatch": Z,
          "unverified": W
        },
        ...
      },
      "f21_rate": (Z + W) / total_claims,
      "generated_at": ISO timestamp
    }

Patrón connection: env vars Supabase (mismo patrón session_memory.py),
con fallback sandbox a impresión "sandbox-mode" si SUPABASE_* no presentes.

Spec firmado T1: bridge/sprints_propuestos/sprint_COWORK_MEMENTO_001.md commit 78d1fb00
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Importación robusta del módulo claim_calibration desde cualquier cwd
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from kernel.cowork_runtime.claim_calibration import ClaimLogger  # noqa: E402


# ============================================================================
# Supabase client adapter (sandbox-friendly)
# ============================================================================

def _get_supabase_client() -> Optional[Any]:
    """Carga cliente Supabase desde env vars, o None si no hay credenciales.

    Variables esperadas (mismo patrón session_memory.py):
        SUPABASE_URL
        SUPABASE_SERVICE_KEY (formato sb_secret_*)
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get(
        "SUPABASE_SERVICE_ROLE_KEY"
    )
    if not url or not key:
        return None
    try:
        from supabase import create_client  # type: ignore[import-not-found]
    except ImportError:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None


class _SupabaseAggregateAdapter:
    """Wraps cliente Supabase para exponer .aggregate_claims() esperada por ClaimLogger."""

    def __init__(self, raw_client: Any) -> None:
        self._raw = raw_client

    def aggregate_claims(self, days: int, claim_type: Optional[str] = None):
        """Ejecuta SELECT GROUP BY claim_type, verification_status.

        Estrategia: usar RPC si existe, sino SELECT + agregación local
        (preferimos local para evitar añadir RPC nueva en el sprint).
        """
        query = self._raw.table("cowork_claims_calibration").select(
            "claim_type, verification_status"
        )
        # Filtro por ventana temporal
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        query = query.gte("created_at", cutoff.isoformat())
        if claim_type:
            query = query.eq("claim_type", claim_type)
        resp = query.execute()
        rows = getattr(resp, "data", []) or []
        # Agrupamos en Python (lo más portable, sin requerir nueva RPC)
        agg: dict[tuple[str, str], int] = {}
        for r in rows:
            ct = r.get("claim_type", "unknown")
            vs = r.get("verification_status", "unverified")
            agg[(ct, vs)] = agg.get((ct, vs), 0) + 1
        return [
            {"claim_type": ct, "verification_status": vs, "n": n}
            for (ct, vs), n in agg.items()
        ]


# ============================================================================
# Sandbox fallback (sin credenciales Supabase)
# ============================================================================

class _SandboxClient:
    """Cliente fake para sandbox / dev sin Supabase. Devuelve agregado vacío."""

    def aggregate_claims(self, days: int, claim_type: Optional[str] = None):
        return []


# ============================================================================
# CLI main
# ============================================================================

def build_report(days: int, claim_type: Optional[str]) -> dict:
    """Construye el reporte agregado usando ClaimLogger.aggregate_daily()."""
    raw = _get_supabase_client()
    if raw is None:
        client = _SandboxClient()
        mode = "sandbox"
    else:
        client = _SupabaseAggregateAdapter(raw)
        mode = "supabase"

    logger = ClaimLogger(supabase_client=client, session_id=None)
    report = logger.aggregate_daily(days=days, claim_type=claim_type)
    report["mode"] = mode
    report["claim_type_filter"] = claim_type
    return report


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="CLI report sobre public.cowork_claims_calibration.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Ventana temporal en días (default 7).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path archivo destino JSON (default stdout).",
    )
    parser.add_argument(
        "--claim-type",
        type=str,
        default=None,
        choices=[
            "file_path", "table_name", "column_name", "migration_number",
            "pr_number", "commit_hash", "branch_name", "sprint_name",
            "loc_count", "test_count", "fecha_iso", "version_string",
        ],
        help="Filtrar agregado por claim_type específico.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON con indent=2.",
    )
    args = parser.parse_args(argv)

    if args.days < 1:
        print("error: --days debe ser >= 1", file=sys.stderr)
        return 2

    report = build_report(days=args.days, claim_type=args.claim_type)

    indent = 2 if args.pretty else None
    payload = json.dumps(report, indent=indent, ensure_ascii=False, default=str)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload, encoding="utf-8")
        print(f"[cowork_calibration_report] escrito en {out_path}", file=sys.stderr)
    else:
        print(payload)

    return 0


if __name__ == "__main__":
    sys.exit(main())
