"""tests/test_cowork_sessions_dashboard.py — T6 dashboard sesiones Cowork."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kernel.cowork_runtime.session_memory import SessionMemoryStore
from kernel.dashboards.cowork_sessions import CoworkSessionsDashboard


def _make_store(tmp_path: Path, sesiones: list[dict], monkeypatch=None) -> SessionMemoryStore:
    """Crea store local con datos sembrados."""
    local_path = tmp_path / "sesiones.json"
    import json
    import os

    local_path.write_text(json.dumps(sesiones, ensure_ascii=False))
    # Forzar fallback local: pasar config=None explicito y borrar env vars en proceso
    for key in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY"):
        os.environ.pop(key, None)
    store = SessionMemoryStore(config=None, local_fallback_path=local_path)
    # Asegurar que use_supabase sea False (no hay config)
    store.use_supabase = False
    return store


def test_dashboard_genera_html_vacio_sin_sesiones(tmp_path):
    store = _make_store(tmp_path, [])
    out = tmp_path / "dash.html"
    dash = CoworkSessionsDashboard(store=store, output_path=out)
    path = dash.generate()
    assert path.exists()
    contenido = path.read_text(encoding="utf-8")
    assert "Sin sesiones registradas" in contenido
    assert "Cowork Sessions Dashboard" in contenido


def test_dashboard_metricas_basicas(tmp_path):
    from datetime import datetime, timezone

    now_iso = datetime.now(timezone.utc).isoformat()
    sesiones = [
        {
            "id": "s1",
            "fecha_inicio": now_iso,
            "sprint_activo": "TEST-001",
            "pre_flight_ejecutado": True,
            "commits_productivos": 3,
            "violaciones_detectadas": ["v1", "v2"],
            "palabras_clave_alfredo": ["avanza"],
        },
        {
            "id": "s2",
            "fecha_inicio": now_iso,
            "sprint_activo": "TEST-002",
            "pre_flight_ejecutado": False,
            "commits_productivos": 0,
            "violaciones_detectadas": ["v3"],
            "palabras_clave_alfredo": ["avanza", "no autoboicotes"],
        },
    ]
    store = _make_store(tmp_path, sesiones)
    dash = CoworkSessionsDashboard(store=store, output_path=tmp_path / "dash.html")
    metrics = dash._compute_metrics(sesiones)
    assert metrics.total_sesiones == 2
    assert metrics.preflight_ratio == 0.5
    assert metrics.avance_ratio == 0.5
    assert metrics.sesiones_audit_only == 1
    assert metrics.palabras_clave_alfredo.get("avanza") == 2


def test_dashboard_renderiza_kpis_correctos(tmp_path):
    from datetime import datetime, timezone

    sesiones = [
        {
            "id": "s1",
            "fecha_inicio": datetime.now(timezone.utc).isoformat(),
            "sprint_activo": "TEST-001",
            "pre_flight_ejecutado": True,
            "commits_productivos": 5,
            "violaciones_detectadas": [],
            "palabras_clave_alfredo": [],
        }
    ]
    store = _make_store(tmp_path, sesiones)
    dash = CoworkSessionsDashboard(store=store, output_path=tmp_path / "dash.html")
    path = dash.generate()
    contenido = path.read_text(encoding="utf-8")
    assert "TEST-001" in contenido
    assert "100%" in contenido  # preflight_ratio = 100%


def test_dashboard_cli(tmp_path, monkeypatch):
    import subprocess

    out = tmp_path / "dash.html"
    # Ejecutar CLI con use_supabase=False forzado por env (sin URL)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    monkeypatch.setenv("COWORK_SESSIONS_LOCAL_PATH", str(tmp_path / "sesiones.json"))
    result = subprocess.run(
        [sys.executable, "-m", "kernel.dashboards.cowork_sessions", "--output", str(out)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "[COWORK_DASHBOARD]" in result.stdout
    assert out.exists()


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
