"""
tests/test_cowork_session_memory.py — Tests T3 (memoria persistente).

Sprint COWORK-RUNTIME-001 / T3 MAGNA P0.

DoD del prompt T3: 'Tabla cowork_sesiones creada con RLS + Pre-flight Memento
leyendo'.

Estos tests usan el fallback local JSON para no depender de Supabase real.
La validacion de la tabla en Supabase se hace en CI separado (T5) o via
smoke E2E manual.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kernel.cowork_runtime.session_memory import (
    CoworkSesion,
    SessionMemoryStore,
    SupabaseConfig,
    build_pre_flight_block,
    close_session,
    read_last_session,
    start_session,
    update_session,
)


@pytest.fixture
def tmp_store(tmp_path, monkeypatch):
    """Store con fallback local en path temporal y SIN Supabase."""
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    return SessionMemoryStore(local_fallback_path=tmp_path / "sessions.json")


# ============================================================================
# CRUD basico
# ============================================================================


class TestCRUD:
    def test_start_session_crea_fila(self, tmp_store):
        sesion = start_session(
            sprint_activo="COWORK-RUNTIME-001",
            kernel_version="0.84.8-sprint-memento",
            store=tmp_store,
        )
        assert sesion.id is not None
        assert sesion.fecha_inicio is not None
        assert sesion.sprint_activo == "COWORK-RUNTIME-001"
        assert sesion.kernel_version == "0.84.8-sprint-memento"

    def test_update_session_actualiza_campos(self, tmp_store):
        sesion = start_session(store=tmp_store)
        updated = update_session(
            sesion.id,
            {
                "turnos_totales": 5,
                "commits_productivos": 2,
                "pre_flight_ejecutado": True,
            },
            store=tmp_store,
        )
        assert updated is not None
        assert updated.turnos_totales == 5
        assert updated.commits_productivos == 2
        assert updated.pre_flight_ejecutado is True

    def test_close_session_setea_fecha_fin_y_resumen(self, tmp_store):
        sesion = start_session(store=tmp_store)
        closed = close_session(
            sesion.id,
            resumen_lecciones="Sesion productiva: T1 T2 T3 cerrados",
            deudas_pendientes=["T4 Companion Agent", "T5 CI tests"],
            store=tmp_store,
        )
        assert closed is not None
        assert closed.fecha_fin is not None
        assert closed.resumen_lecciones is not None
        assert "T1 T2 T3" in closed.resumen_lecciones
        assert "T4 Companion Agent" in closed.deudas_pendientes_proxima_sesion

    def test_get_last_devuelve_ultima_por_fecha_inicio(self, tmp_store):
        start_session(sprint_activo="A", store=tmp_store)
        # forzar timestamps distintos
        import time

        time.sleep(0.01)
        s2 = start_session(sprint_activo="B", store=tmp_store)
        last = read_last_session(store=tmp_store)
        assert last is not None
        assert last.id == s2.id
        assert last.sprint_activo == "B"

    def test_update_inexistente_devuelve_none(self, tmp_store):
        result = update_session("uuid-inexistente", {"turnos_totales": 1}, store=tmp_store)
        assert result is None


# ============================================================================
# Pre-flight Memento extendido (corazon del T3)
# ============================================================================


class TestPreFlightMemento:
    def test_block_sin_sesion_previa(self, tmp_store):
        block = build_pre_flight_block(store=tmp_store)
        assert "primera sesion" in block
        assert "CLAUDE.md" in block

    def test_block_con_sesion_cerrada_completa(self, tmp_store):
        sesion = start_session(
            sprint_activo="COWORK-RUNTIME-001",
            kernel_version="0.84.8-sprint-memento",
            store=tmp_store,
        )
        update_session(
            sesion.id,
            {
                "turnos_totales": 12,
                "commits_productivos": 3,
                "pre_flight_ejecutado": True,
                "violaciones_detectadas": [
                    "MAGNA — sugiere parar en 'andate a dormir'",
                    "PREMIUM — meta-trabajo sin avance",
                ],
                "correctivos_recibidos": [
                    "obedece ya con codigo no con texto",
                ],
            },
            store=tmp_store,
        )
        close_session(
            sesion.id,
            resumen_lecciones="Aprendi a no sugerir descanso cuando Alfredo demanda avance",
            deudas_pendientes=["Implementar M9 veto Telegram"],
            store=tmp_store,
        )
        block = build_pre_flight_block(store=tmp_store)
        # Bloque debe contener todos los elementos canonicos
        assert "COWORK_PRE_FLIGHT" in block
        assert "COWORK-RUNTIME-001" in block
        assert "0.84.8-sprint-memento" in block
        assert "MAGNA" in block
        assert "obedece ya" in block
        assert "DEUDAS PENDIENTES" in block
        assert "Implementar M9 veto Telegram" in block
        assert "Aprendi a no sugerir descanso" in block

    def test_block_con_sesion_no_cerrada_marca_interrumpida(self, tmp_store):
        sesion = start_session(store=tmp_store)
        update_session(sesion.id, {"turnos_totales": 3}, store=tmp_store)
        block = build_pre_flight_block(store=tmp_store)
        assert "interrumpida" in block.lower() or "no cerrada" in block.lower()


# ============================================================================
# CoworkSesion dataclass
# ============================================================================


class TestModelo:
    def test_to_dict_omite_none(self):
        s = CoworkSesion(turnos_totales=3, commits_productivos=1)
        d = s.to_dict()
        assert d["turnos_totales"] == 3
        assert d["commits_productivos"] == 1
        # None no debe aparecer
        assert "fecha_fin" not in d
        assert "resumen_lecciones" not in d

    def test_from_dict_ignora_keys_extra(self):
        s = CoworkSesion.from_dict({"turnos_totales": 5, "campo_inexistente": "x"})
        assert s.turnos_totales == 5


# ============================================================================
# Supabase config (anti-Dory: lectura fresca cada vez)
# ============================================================================


class TestSupabaseConfig:
    def test_from_env_devuelve_none_si_falta(self, monkeypatch):
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
        assert SupabaseConfig.from_env() is None

    def test_from_env_acepta_service_key_canonico(self, monkeypatch):
        monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "sb_secret_xxx")
        monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
        cfg = SupabaseConfig.from_env()
        assert cfg is not None
        assert cfg.url == "https://example.supabase.co"
        assert cfg.service_key == "sb_secret_xxx"

    def test_from_env_acepta_service_role_legacy(self, monkeypatch):
        monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co/")
        monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
        monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service_role_legacy_xxx")
        cfg = SupabaseConfig.from_env()
        assert cfg is not None
        # url normalizada (sin trailing slash)
        assert cfg.url == "https://example.supabase.co"
        assert cfg.service_key == "service_role_legacy_xxx"


# ============================================================================
# Migracion SQL: smoke check de canon DSC-S-006
# ============================================================================


class TestMigracionSQL:
    def test_migracion_009_existe(self):
        path = REPO_ROOT / "migrations" / "sql" / "0009_cowork_sesiones.sql"
        assert path.exists()

    def test_migracion_tiene_RLS_canon(self):
        path = REPO_ROOT / "migrations" / "sql" / "0009_cowork_sesiones.sql"
        sql = path.read_text()
        assert "ENABLE ROW LEVEL SECURITY" in sql
        assert "service_role_only" in sql
        assert "auth.role() = 'service_role'" in sql
        # Constraint pre_flight obligatorio
        assert "pre_flight_obligatorio" in sql

    def test_migracion_es_idempotente(self):
        path = REPO_ROOT / "migrations" / "sql" / "0009_cowork_sesiones.sql"
        sql = path.read_text()
        assert "CREATE TABLE IF NOT EXISTS" in sql
        assert "DROP POLICY IF EXISTS" in sql
        assert "BEGIN;" in sql
        assert re.search(r"\bCOMMIT\s*;", sql)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
