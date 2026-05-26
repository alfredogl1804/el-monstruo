"""Tests para `kernel.dashboards.cost_history`.

Filosofía:
  * Cero red — usamos un fake `_SupabaseRest`.
  * Cero archivos persistentes en repo — escribimos a tmp_path.
  * Validamos que el HTML es bien-formado y contiene los marcadores clave.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from kernel.dashboards import cost_history
from kernel.dashboards.cost_history import (
    CostHistorySnapshot,
    _render_chart_svg,
    fetch_cost_history,
    generate_dashboard_html,
    render_dashboard_html,
    write_dashboard,
)


class _FakeSupabase:
    """Doble de _SupabaseRest que devuelve filas pre-cargadas."""

    def __init__(self, rows: list[dict]):
        self._rows = rows
        self.last_params: dict | None = None
        self.last_table: str | None = None

    def select(self, table: str, params: dict, prefer=None):
        self.last_table = table
        self.last_params = params
        return list(self._rows), {}

    def insert(self, *_a, **_kw):  # pragma: no cover - no usado aquí
        raise NotImplementedError


def _row(
    *,
    cycle_id: int,
    cost: float,
    when: datetime,
    aborted: str | None = None,
    cap_excedido: bool = False,
    model: str = "gpt-5",
    tokens: int = 1234,
) -> dict:
    return {
        "cycle_id": cycle_id,
        "latido_id": f"latido-{cycle_id}",
        "cap_per_latido_usd": 0.05,
        "cost_actual_usd": cost,
        "cost_estimated_usd": cost * 1.1,
        "cap_excedido": cap_excedido,
        "abort_reason": aborted,
        "tokens_used": tokens,
        "tokens_input": tokens // 2,
        "tokens_output": tokens // 2,
        "model_used": model,
        "trigger_type": "cron",
        "trigger_detail": "scheduled",
        "completed_at": when.isoformat(),
        "created_at": when.isoformat(),
    }


# ────────────────────────────────────────────────────────────────────
# Snapshot model


def test_snapshot_total_cycles_empty():
    snap = CostHistorySnapshot(rows=[])
    assert snap.total_cycles == 0
    assert snap.aborted_cycles == []
    assert snap.cap_excedido_count == 0


def test_snapshot_aggregates_aborted_and_excedido():
    now = datetime.now(timezone.utc)
    rows = [
        _row(cycle_id=1, cost=0.01, when=now),
        _row(cycle_id=2, cost=0.0, when=now, aborted="daily_budget_exhausted"),
        _row(cycle_id=3, cost=0.07, when=now, cap_excedido=True),
    ]
    snap = CostHistorySnapshot(rows=rows)
    assert snap.total_cycles == 3
    assert len(snap.aborted_cycles) == 1
    assert snap.cap_excedido_count == 1


def test_snapshot_spend_in_window_filters_by_time():
    now = datetime.now(timezone.utc)
    rows = [
        _row(cycle_id=1, cost=0.10, when=now - timedelta(hours=1)),
        _row(cycle_id=2, cost=0.20, when=now - timedelta(hours=12)),
        _row(cycle_id=3, cost=0.30, when=now - timedelta(days=3)),
    ]
    snap = CostHistorySnapshot(rows=rows, generated_at=now)
    assert snap.spend_in_window(24) == pytest.approx(0.30, rel=1e-3)
    assert snap.spend_in_window(24 * 7) == pytest.approx(0.60, rel=1e-3)


def test_snapshot_daily_buckets_returns_correct_length_and_keys():
    now = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
    rows = [
        _row(cycle_id=1, cost=0.05, when=now),
        _row(cycle_id=2, cost=0.10, when=now - timedelta(days=1)),
        _row(cycle_id=3, cost=0.20, when=now - timedelta(days=20)),  # fuera de ventana
    ]
    snap = CostHistorySnapshot(rows=rows, generated_at=now)
    buckets = snap.daily_buckets(days=14)
    assert len(buckets) == 14
    by_day = dict(buckets)
    assert by_day["2026-05-10"] == pytest.approx(0.05)
    assert by_day["2026-05-09"] == pytest.approx(0.10)
    # Día sin datos
    assert by_day["2026-05-05"] == 0.0


def test_snapshot_handles_missing_timestamps_safely():
    snap = CostHistorySnapshot(rows=[{"cost_actual_usd": 0.5}])
    # No revienta aunque no haya completed_at/created_at
    assert snap.spend_in_window(24) == 0.0


# ────────────────────────────────────────────────────────────────────
# fetch_cost_history


def test_fetch_uses_supabase_client_with_correct_params():
    fake = _FakeSupabase(rows=[])
    snap = fetch_cost_history(limit=42, supabase_client=fake)
    assert isinstance(snap, CostHistorySnapshot)
    assert fake.last_table == "embrion_budget_state"
    assert fake.last_params is not None
    assert fake.last_params["limit"] == "42"
    assert fake.last_params["order"] == "created_at.desc"
    assert "cost_actual_usd" in fake.last_params["select"]


def test_fetch_returns_rows_intact():
    now = datetime.now(timezone.utc)
    rows = [_row(cycle_id=1, cost=0.01, when=now)]
    fake = _FakeSupabase(rows=rows)
    snap = fetch_cost_history(supabase_client=fake)
    assert snap.total_cycles == 1
    assert snap.rows[0]["cycle_id"] == 1


# ────────────────────────────────────────────────────────────────────
# Render HTML


def test_render_chart_empty_returns_empty_state():
    out = _render_chart_svg([], 5.0)
    assert "Sin datos" in out


def test_render_chart_with_data_emits_valid_svg():
    buckets = [("2026-05-08", 0.1), ("2026-05-09", 0.3), ("2026-05-10", 0.05)]
    svg = _render_chart_svg(buckets, daily_budget=0.2)
    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")
    # 3 barras
    assert svg.count("<rect") == 3
    # Línea de cap
    assert "cap diario" in svg


def test_render_dashboard_html_contains_all_sections():
    now = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
    rows = [
        _row(cycle_id=1, cost=0.02, when=now - timedelta(hours=1)),
        _row(cycle_id=2, cost=0.0, when=now - timedelta(hours=2), aborted="daily_budget_exhausted"),
        _row(cycle_id=3, cost=0.07, when=now - timedelta(hours=3), cap_excedido=True),
    ]
    snap = CostHistorySnapshot(rows=rows, generated_at=now, daily_budget_usd=5.0, cap_per_latido_usd=0.05)
    html_str = render_dashboard_html(snap)

    assert html_str.startswith("<!DOCTYPE html>")
    assert "</html>" in html_str.strip()[-10:]
    # Secciones obligatorias
    assert "KPIs" in html_str
    assert "Gasto diario" in html_str
    assert "Últimos cycles" in html_str
    assert "Cycles abortados" in html_str
    # Tabla con datos
    assert "cycle_id" in html_str
    assert "daily_budget_exhausted" in html_str
    # SVG inline
    assert "<svg" in html_str
    # Generated_at
    assert "2026-05-10" in html_str


def test_render_dashboard_escapes_html_in_user_data():
    now = datetime.now(timezone.utc)
    malicious = _row(cycle_id=1, cost=0.01, when=now)
    malicious["abort_reason"] = "<script>alert('xss')</script>"
    malicious["model_used"] = "<img src=x onerror=alert(1)>"
    snap = CostHistorySnapshot(rows=[malicious], generated_at=now)
    html_str = render_dashboard_html(snap)
    assert "<script>alert" not in html_str
    assert "&lt;script&gt;" in html_str or "&lt;img" in html_str


def test_render_dashboard_handles_empty_rows_gracefully():
    snap = CostHistorySnapshot(rows=[], daily_budget_usd=5.0)
    html_str = render_dashboard_html(snap)
    assert "Sin cycles registrados" in html_str
    assert "el embrión está corriendo limpio" in html_str


# ────────────────────────────────────────────────────────────────────
# Integration: generate + write


def test_generate_dashboard_html_end_to_end_with_fake():
    now = datetime.now(timezone.utc)
    fake = _FakeSupabase(rows=[_row(cycle_id=99, cost=0.04, when=now)])
    out = generate_dashboard_html(supabase_client=fake)
    assert "<!DOCTYPE html>" in out
    assert "99" in out  # cycle_id renderizado


def test_write_dashboard_creates_file_at_path(tmp_path: Path):
    fake = _FakeSupabase(rows=[])
    target = tmp_path / "subdir" / "dashboard.html"
    written = write_dashboard(output_path=str(target), supabase_client=fake)
    assert Path(written).exists()
    content = Path(written).read_text(encoding="utf-8")
    assert content.startswith("<!DOCTYPE html>")
    assert "Embrión" in content


def test_write_dashboard_is_idempotent_for_same_data(tmp_path: Path):
    """Misma data debe producir mismo HTML (excepto generated_at).

    Verificamos que el cuerpo (sin la línea de generated_at) es idéntico.
    """
    now = datetime.now(timezone.utc)
    rows = [_row(cycle_id=1, cost=0.01, when=now)]
    fake = _FakeSupabase(rows=rows)

    a = tmp_path / "a.html"
    b = tmp_path / "b.html"
    write_dashboard(output_path=str(a), supabase_client=fake)
    write_dashboard(output_path=str(b), supabase_client=fake)

    body_a = re.sub(r"Generado en [^<]+", "Generado en X", a.read_text())
    body_b = re.sub(r"Generado en [^<]+", "Generado en X", b.read_text())
    assert body_a == body_b


def test_cli_main_writes_to_output(tmp_path: Path, monkeypatch):
    """Smoke del CLI: invocar `_main` con --output debe crear el archivo."""
    fake = _FakeSupabase(rows=[])

    # Inyectamos el fake interceptando _get_supabase_client
    monkeypatch.setattr(cost_history, "_get_supabase_client", lambda: fake)

    target = tmp_path / "out.html"
    rc = cost_history._main(["--output", str(target), "--limit", "10"])
    assert rc == 0
    assert target.exists()
    assert target.read_text(encoding="utf-8").startswith("<!DOCTYPE html>")


def test_cli_main_returns_1_on_error(tmp_path: Path, monkeypatch, capsys):
    def boom():
        raise RuntimeError("supabase down")

    monkeypatch.setattr(cost_history, "_get_supabase_client", boom)
    rc = cost_history._main(["--output", str(tmp_path / "x.html")])
    assert rc == 1
    captured = capsys.readouterr()
    assert "ERROR" in captured.err
