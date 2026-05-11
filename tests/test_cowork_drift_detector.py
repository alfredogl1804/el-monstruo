"""tests/test_cowork_drift_detector.py — T7 drift detector."""
from __future__ import annotations

import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kernel.cowork_runtime.drift_detector import (
    DriftDetector,
    DriftAction,
    SessionDriftState,
)


def test_disabled_default_no_op():
    """Por canon DSC-MO-011 Blue-Green, default enabled=false => NO_OP."""
    detector = DriftDetector()  # default enabled
    state = SessionDriftState(turnos=100, violaciones_acumuladas=10)
    signal = detector.evaluate(state)
    assert signal.action == DriftAction.NO_OP
    assert "disabled" in signal.razon


def test_hard_halt_por_correctivos_repetidos():
    detector = DriftDetector(enabled=True, max_correctivos_alfredo=2)
    state = SessionDriftState(correctivos_alfredo=2)
    signal = detector.evaluate(state)
    assert signal.action == DriftAction.HARD_HALT
    assert signal.severidad == 3


def test_reinject_por_violaciones_acumuladas():
    detector = DriftDetector(enabled=True, max_violaciones_acumuladas=3)
    state = SessionDriftState(violaciones_acumuladas=3)
    signal = detector.evaluate(state)
    assert signal.action == DriftAction.REINJECT_RULES
    assert signal.severidad == 2


def test_force_preflight_turno_1_sin_preflight():
    detector = DriftDetector(enabled=True)
    state = SessionDriftState(turnos=1, pre_flight_ejecutado=False)
    signal = detector.evaluate(state)
    assert signal.action == DriftAction.FORCE_PREFLIGHT


def test_no_force_preflight_si_ya_ejecutado():
    detector = DriftDetector(enabled=True, max_turnos_sin_preflight=10)
    state = SessionDriftState(turnos=1, pre_flight_ejecutado=True)
    signal = detector.evaluate(state)
    assert signal.action == DriftAction.NO_OP


def test_reinject_por_turnos_sin_preflight():
    detector = DriftDetector(enabled=True, max_turnos_sin_preflight=5)
    state = SessionDriftState(turnos=5, pre_flight_ejecutado=True)
    signal = detector.evaluate(state)
    assert signal.action == DriftAction.REINJECT_RULES


def test_no_reinject_si_reinjeccion_reciente():
    detector = DriftDetector(enabled=True, max_turnos_sin_preflight=5)
    state = SessionDriftState(
        turnos=5, pre_flight_ejecutado=True,
        ts_ultima_reinjeccion=time.time(),
    )
    signal = detector.evaluate(state)
    # Debounce: no re-inyectar si hace <60s
    assert signal.action == DriftAction.NO_OP


def test_reinject_por_tiempo_sin_preflight():
    detector = DriftDetector(
        enabled=True,
        max_turnos_sin_preflight=100,
        max_segundos_sin_preflight=1,
    )
    state = SessionDriftState(
        turnos=2,
        pre_flight_ejecutado=True,
        ts_ultimo_preflight=time.time() - 10,
    )
    signal = detector.evaluate(state)
    assert signal.action == DriftAction.REINJECT_RULES
    assert "sin re-inyectar" in signal.razon
    assert signal.metricas.get("segundos_desde_preflight") is not None


def test_estado_saludable_no_op():
    detector = DriftDetector(enabled=True)
    state = SessionDriftState(
        turnos=2,
        pre_flight_ejecutado=True,
        ts_ultimo_preflight=time.time(),
    )
    signal = detector.evaluate(state)
    assert signal.action == DriftAction.NO_OP


def test_helpers_mutators():
    detector = DriftDetector(enabled=True)
    state = SessionDriftState()
    detector.tick_turno(state)
    assert state.turnos == 1
    detector.mark_preflight_ejecutado(state)
    assert state.pre_flight_ejecutado is True
    assert state.ts_ultimo_preflight is not None
    detector.mark_reinjeccion(state)
    assert state.ts_ultima_reinjeccion is not None


def test_cli_smoke_halt():
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "kernel.cowork_runtime.drift_detector",
         "--enable", "--correctivos", "5"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    # exit code 2 = halt
    assert result.returncode == 2
    assert "hard_halt" in result.stdout


def test_cli_smoke_no_op():
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "kernel.cowork_runtime.drift_detector",
         "--enable"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0


def test_env_vars_overrides(monkeypatch):
    monkeypatch.setenv("COWORK_DRIFT_ENABLED", "true")
    monkeypatch.setenv("COWORK_DRIFT_MAX_TURNOS", "10")
    detector = DriftDetector()
    assert detector.enabled is True
    assert detector.max_turnos_sin_preflight == 10


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
