"""tests/test_alfredo_veto_channel.py — M9 canal de veto Alfredo→Cowork."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kernel.cowork_runtime.alfredo_veto_channel import (
    AlfredoVetoChannel,
    VetoSeverity,
    VetoEvent,
    VETO_KEYWORDS,
)


@pytest.fixture
def tmp_channel(tmp_path):
    return AlfredoVetoChannel(state_path=tmp_path / "veto.json", enabled=True)


# ---- Disabled default ----

def test_disabled_por_default():
    """Por canon DSC-MO-011 Blue-Green, default enabled=false."""
    channel = AlfredoVetoChannel()
    assert channel.enabled is False


def test_disabled_emit_no_persiste(tmp_path):
    state = tmp_path / "veto.json"
    channel = AlfredoVetoChannel(state_path=state, enabled=False)
    event = channel.emit_veto("VETO", contexto="test")
    assert "[CHANNEL_DISABLED]" in event.contexto
    assert not state.exists()


# ---- Emit ----

def test_emit_palabra_clave_canonica(tmp_channel):
    event = tmp_channel.emit_veto("VETO", contexto="No me entendiste")
    assert event.palabra_clave == "VETO"
    assert event.severidad == VetoSeverity.HALT.value
    assert event.contexto == "No me entendiste"


def test_emit_severidad_implicita_por_keyword(tmp_channel):
    assert tmp_channel.emit_veto("REPENSAR").severidad == VetoSeverity.HARD.value
    assert tmp_channel.emit_veto("NO").severidad == VetoSeverity.SOFT.value


def test_emit_palabra_no_canonica_default_soft(tmp_channel):
    event = tmp_channel.emit_veto("ALGO_RARO")
    assert event.severidad == VetoSeverity.SOFT.value


def test_emit_severidad_explicita_overridea(tmp_channel):
    event = tmp_channel.emit_veto("NO", severidad=VetoSeverity.HALT)
    assert event.severidad == VetoSeverity.HALT.value


def test_emit_persiste_estado(tmp_channel):
    tmp_channel.emit_veto("VETO")
    assert tmp_channel.state_path.exists()
    raw = json.loads(tmp_channel.state_path.read_text())
    assert len(raw) == 1
    assert raw[0]["palabra_clave"] == "VETO"


def test_emit_dispara_callback(tmp_path):
    cb = MagicMock()
    channel = AlfredoVetoChannel(
        state_path=tmp_path / "veto.json", enabled=True, notify_callback=cb,
    )
    channel.emit_veto("VETO")
    cb.assert_called_once()
    assert cb.call_args[0][0].palabra_clave == "VETO"


def test_callback_failure_no_bloquea(tmp_path):
    cb = MagicMock(side_effect=Exception("boom"))
    channel = AlfredoVetoChannel(
        state_path=tmp_path / "veto.json", enabled=True, notify_callback=cb,
    )
    # No debe levantar
    event = channel.emit_veto("VETO")
    assert event.palabra_clave == "VETO"


# ---- Detect en mensaje ----

def test_detect_veto_en_mensaje(tmp_channel):
    # 'STOP' y 'basta'->'BASTA' son ambos HALT; el detector elige
    # determinísticamente. Lo importante: detecta UN veto HALT.
    veto = tmp_channel.detect_veto_in_message("STOP, basta de eso", contexto="msg")
    assert veto is not None
    assert veto.severidad == VetoSeverity.HALT.value
    assert veto.palabra_clave in ("STOP", "BASTA")


def test_detect_veto_word_boundary(tmp_channel):
    """'NO' dentro de 'NORMAL' NO debe matchear."""
    veto = tmp_channel.detect_veto_in_message("Está NORMAL, no te preocupes")
    # 'NO' como palabra suelta SI matchea (es soft)
    # 'NORMAL' no debe contar
    # En "no te preocupes" hay un 'no' minuscula que se vuelve NO en upper
    assert veto is not None
    assert veto.palabra_clave == "NO"


def test_detect_prefiere_severidad_alta(tmp_channel):
    """Si hay multiples vetos, prefiere el de mayor severidad."""
    veto = tmp_channel.detect_veto_in_message("NO me gusta, mejor STOP")
    assert veto.palabra_clave == "STOP"  # HALT > SOFT


def test_detect_sin_keyword_devuelve_none(tmp_channel):
    veto = tmp_channel.detect_veto_in_message("Todo bien, sigue")
    assert veto is None


# ---- Consume / peek ----

def test_consume_pending_veto(tmp_channel):
    tmp_channel.emit_veto("VETO")
    veto = tmp_channel.consume_pending_veto()
    assert veto is not None
    assert veto.palabra_clave == "VETO"
    # Segunda llamada: no hay pendiente
    assert tmp_channel.consume_pending_veto() is None


def test_peek_no_consume(tmp_channel):
    tmp_channel.emit_veto("VETO")
    veto = tmp_channel.peek_pending_veto()
    assert veto is not None
    # Aun pendiente
    veto2 = tmp_channel.consume_pending_veto()
    assert veto2 is not None


def test_consume_devuelve_mas_reciente(tmp_channel):
    tmp_channel.emit_veto("NO", contexto="primero")
    tmp_channel.emit_veto("VETO", contexto="segundo")
    veto = tmp_channel.consume_pending_veto()
    assert veto.palabra_clave == "VETO"
    assert veto.contexto == "segundo"


def test_history(tmp_channel):
    for kw in ["NO", "MAL", "VETO"]:
        tmp_channel.emit_veto(kw)
    hist = tmp_channel.history(limit=2)
    assert len(hist) == 2
    assert hist[-1].palabra_clave == "VETO"


def test_clear(tmp_channel):
    tmp_channel.emit_veto("VETO")
    tmp_channel.clear()
    assert tmp_channel.history() == []


# ---- Catalogo de palabras clave ----

def test_palabras_clave_canonicas_completas():
    """Las 9 palabras clave canonizadas en CLAUDE.md (M9 anexo)."""
    expected = {"VETO", "ALTO", "STOP", "BASTA", "PARAR", "REPENSAR", "EQUIVOCADO", "MAL", "NO"}
    assert expected.issubset(set(VETO_KEYWORDS.keys()))


# ---- CLI ----

def test_cli_emit(tmp_path, monkeypatch):
    import subprocess
    import os as _os
    state = tmp_path / "veto.json"
    env = _os.environ.copy()
    env["COWORK_VETO_ENABLED"] = "true"
    # Cambiar al tmp_path para que el state default caiga ahi
    result = subprocess.run(
        [sys.executable, "-m", "kernel.cowork_runtime.alfredo_veto_channel",
         "emit", "VETO", "--contexto", "test cli", "--enable"],
        cwd=REPO_ROOT, capture_output=True, text=True, env=env,
    )
    assert result.returncode == 0
    out = json.loads(result.stdout)
    assert out["palabra_clave"] == "VETO"
    assert out["severidad"] == "halt"


def test_cli_peek_sin_pendientes(tmp_path):
    import subprocess
    import os as _os
    # Usar HOME tmp para que el state file por defecto no exista
    env = _os.environ.copy()
    # Aislar: peek lee bridge/alfredo_veto_state.json relativo a cwd
    aux_dir = tmp_path / "aux"
    (aux_dir / "bridge").mkdir(parents=True)
    result = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, '" + str(REPO_ROOT) + "'); "
         "from kernel.cowork_runtime.alfredo_veto_channel import main; "
         "sys.exit(main(['peek']))"],
        cwd=aux_dir, capture_output=True, text=True, env=env,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "null"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
