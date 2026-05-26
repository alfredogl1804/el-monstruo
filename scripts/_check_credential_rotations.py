#!/usr/bin/env python3
"""
_check_credential_rotations.py — Lee bridge/credentials_inventory.md y reporta
credenciales que superan el 80% de su frecuencia objetivo de rotación.

Uso (CI):
    python3 scripts/_check_credential_rotations.py --inventory bridge/credentials_inventory.md \
        --threshold-pct 80 --output reports/rotation_alerts.md

Exit codes:
    0  — ninguna alerta (todo dentro de ventana segura)
    1  — al menos 1 credencial supera el threshold (CI debe abrir issue)
    2  — error de parseo o IO

Sprint origen: S-003.A (DSC-S-008)
"""

import argparse
import datetime
import re
import sys
from pathlib import Path


def parse_inventory(text: str) -> list[dict]:
    """Extrae filas de las tablas markdown del inventario."""
    rows = []
    in_table = False
    headers: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            in_table = False
            headers = []
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells if c):
            in_table = True
            continue
        if not in_table and any("name" in c.lower() for c in cells):
            headers = [c.lower() for c in cells]
            continue
        if in_table and headers and len(cells) == len(headers):
            row = dict(zip(headers, cells))
            rows.append(row)
    return rows


def parse_date(value: str) -> datetime.date | None:
    """Parsea YYYY-MM-DD; retorna None si unknown/n/a/inválido."""
    value = value.strip().lower()
    if value in ("unknown", "n/a", "", "-", "—"):
        return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", value)
    if not m:
        return None
    try:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def parse_freq(value: str) -> int | None:
    """Parsea frecuencia en días; retorna None si n/a."""
    value = value.strip().lower()
    if value in ("n/a", "", "-", "—"):
        return None
    m = re.search(r"\d+", value)
    return int(m.group()) if m else None


def find_credential_name(row: dict) -> str | None:
    for key in ("name", "credencial", "credential"):
        if key in row and row[key]:
            return row[key].strip().strip("`")
    return None


def evaluate(rows: list[dict], today: datetime.date, threshold_pct: float, baseline: datetime.date) -> list[dict]:
    """Devuelve lista de alertas con porcentaje de frecuencia consumido."""
    alerts = []
    for row in rows:
        name = find_credential_name(row)
        if not name or name.startswith("#"):
            continue
        if name.lower() in ("name", "credencial", "credential"):
            continue
        freq = parse_freq(row.get("freq_days", ""))
        if freq is None or freq <= 0:
            continue
        last = parse_date(row.get("last_rotated_at", ""))
        effective_baseline = last if last is not None else baseline
        days_since = (today - effective_baseline).days
        pct = (days_since / freq) * 100
        if pct >= threshold_pct:
            alerts.append(
                {
                    "name": name,
                    "freq_days": freq,
                    "days_since": days_since,
                    "pct_consumed": round(pct, 1),
                    "last_rotated_at": last.isoformat() if last else "unknown",
                    "responsable": row.get("responsable", "?"),
                    "runbook": row.get("runbook", "pendiente"),
                }
            )
    return alerts


def render_markdown(alerts: list[dict], today: datetime.date, threshold_pct: float) -> str:
    if not alerts:
        return f"# Rotation Alerts — {today.isoformat()}\n\nNinguna credencial supera el {threshold_pct}% de su frecuencia objetivo. Estado: OK.\n"
    lines = [
        f"# Rotation Alerts — {today.isoformat()}",
        "",
        f"Threshold: {threshold_pct}% de la frecuencia objetivo. Total de alertas: **{len(alerts)}**.",
        "",
        "| # | Credencial | freq_days | days_since | % consumido | last_rotated_at | responsable | runbook |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for i, a in enumerate(sorted(alerts, key=lambda x: -x["pct_consumed"]), 1):
        lines.append(
            f"| {i} | `{a['name']}` | {a['freq_days']} | {a['days_since']} | "
            f"**{a['pct_consumed']}%** | {a['last_rotated_at']} | {a['responsable']} | {a['runbook']} |"
        )
    lines.append("")
    lines.append("## Acción requerida")
    lines.append("")
    lines.append(
        "Cada credencial listada arriba debe rotarse en los próximos 7-14 días siguiendo el runbook "
        "correspondiente. Tras rotar, actualizar `bridge/credentials_inventory.md` con la nueva fecha "
        "`last_rotated_at`. Política: DSC-S-008."
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check credential rotations against DSC-S-008.")
    parser.add_argument("--inventory", default="bridge/credentials_inventory.md")
    parser.add_argument("--threshold-pct", type=float, default=80.0)
    parser.add_argument(
        "--baseline", default="2026-05-10", help="Fecha conservadora si last_rotated_at es unknown (DSC-S-008)."
    )
    parser.add_argument("--output", default="reports/rotation_alerts.md")
    parser.add_argument("--today", default=None, help="Override today (YYYY-MM-DD) for testing.")
    args = parser.parse_args()

    inventory_path = Path(args.inventory)
    if not inventory_path.exists():
        print(f"ERROR: inventory file not found: {inventory_path}", file=sys.stderr)
        return 2

    text = inventory_path.read_text(encoding="utf-8")
    rows = parse_inventory(text)
    if not rows:
        print("ERROR: no rows parsed from inventory", file=sys.stderr)
        return 2

    today = datetime.date.fromisoformat(args.today) if args.today else datetime.date.today()
    baseline = datetime.date.fromisoformat(args.baseline)

    alerts = evaluate(rows, today, args.threshold_pct, baseline)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown(alerts, today, args.threshold_pct), encoding="utf-8")

    print(f"Inventory rows parsed: {len(rows)}")
    print(f"Alerts found: {len(alerts)} (threshold: {args.threshold_pct}%)")
    print(f"Report written to: {output_path}")
    if alerts:
        print("\nTop 5 alerts:")
        for a in sorted(alerts, key=lambda x: -x["pct_consumed"])[:5]:
            print(f"  - {a['name']}: {a['pct_consumed']}% ({a['days_since']}/{a['freq_days']} days)")

    return 1 if alerts else 0


if __name__ == "__main__":
    sys.exit(main())
