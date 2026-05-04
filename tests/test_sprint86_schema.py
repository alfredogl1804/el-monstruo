"""
Sprint 86 Bloque 1 — Tests del schema Supabase de El Catastro.

Valida:
  1. SQL migration parsea limpio (sintaxis básica)
  2. Las 5 tablas + vista + función + RLS están declaradas
  3. Pydantic models del módulo kernel.catastro reflejan el SQL
  4. Validators custom (slug format, dominios no vacíos, hitl consistency) funcionan
  5. Enums espejan los CHECK CONSTRAINTS

NO requiere conexión a Supabase ni env vars — son tests offline puros.

[Hilo Manus Catastro] — 2026-05-04
"""
from __future__ import annotations

import re
from datetime import datetime, date
from pathlib import Path

import pytest


SQL_PATH = Path(__file__).resolve().parent.parent / "scripts" / "016_sprint86_catastro_schema.sql"


# ============================================================================
# A) Tests de la migration SQL
# ============================================================================

@pytest.fixture(scope="module")
def sql_text() -> str:
    assert SQL_PATH.exists(), f"Migration SQL no encontrada en {SQL_PATH}"
    return SQL_PATH.read_text(encoding="utf-8")


def test_sql_extension_pgvector(sql_text):
    assert re.search(r"CREATE EXTENSION IF NOT EXISTS vector", sql_text), \
        "pgvector extension no declarada"


@pytest.mark.parametrize("tabla", [
    "catastro_modelos",
    "catastro_historial",
    "catastro_eventos",
    "catastro_notas",
    "catastro_curadores",
])
def test_sql_5_tablas_declaradas(sql_text, tabla):
    pattern = rf"CREATE TABLE IF NOT EXISTS\s+{tabla}\s*\("
    assert re.search(pattern, sql_text), f"Tabla {tabla!r} no declarada"


def test_sql_vista_materializada(sql_text):
    assert re.search(
        r"CREATE MATERIALIZED VIEW IF NOT EXISTS\s+catastro_metricas_diarias",
        sql_text,
    ), "Vista materializada catastro_metricas_diarias no declarada"


def test_sql_funcion_match(sql_text):
    assert "CREATE OR REPLACE FUNCTION match_catastro_modelos" in sql_text, \
        "Función match_catastro_modelos no declarada"
    # Verifica que devuelve similarity como FLOAT
    assert "similarity FLOAT" in sql_text, \
        "match_catastro_modelos no devuelve similarity FLOAT"


def test_sql_rls_habilitado_en_5_tablas(sql_text):
    for tabla in ["catastro_modelos", "catastro_historial", "catastro_eventos",
                  "catastro_notas", "catastro_curadores"]:
        pattern = rf"ALTER TABLE\s+{tabla}\s+ENABLE ROW LEVEL SECURITY"
        assert re.search(pattern, sql_text), f"RLS no habilitado en {tabla}"


def test_sql_policies_read_public(sql_text):
    for tabla in ["catastro_modelos", "catastro_historial", "catastro_eventos",
                  "catastro_notas", "catastro_curadores"]:
        pattern = rf'CREATE POLICY\s+"{tabla}_read_public"\s+ON\s+{tabla}'
        assert re.search(pattern, sql_text), f"Policy read_public no creada en {tabla}"


def test_sql_check_constraints_estado(sql_text):
    """Estado del modelo debe tener los 6 valores válidos."""
    for v in ['production', 'beta', 'open-source', 'deprecated', 'alpha', 'preview']:
        assert f"'{v}'" in sql_text, f"Valor de estado {v!r} no presente en CHECK"


def test_sql_check_constraints_eventos(sql_text):
    """Tipo de evento debe incluir model_drift_detected (Addendum 002)."""
    assert "'model_drift_detected'" in sql_text, \
        "Falta 'model_drift_detected' en CHECK de catastro_eventos.tipo"


def test_sql_indexes_pgvector(sql_text):
    """Índice ivfflat para semantic search debe estar."""
    assert "USING ivfflat (embedding vector_cosine_ops)" in sql_text


def test_sql_triggers_updated_at(sql_text):
    assert "trg_catastro_set_updated_at" in sql_text
    assert "BEFORE UPDATE ON catastro_modelos" in sql_text
    assert "BEFORE UPDATE ON catastro_curadores" in sql_text


def test_sql_quorum_alcanzado_default_false(sql_text):
    """quorum_alcanzado debe ser BOOLEAN NOT NULL DEFAULT false."""
    assert re.search(
        r"quorum_alcanzado BOOLEAN NOT NULL DEFAULT false",
        sql_text,
    ), "quorum_alcanzado mal declarado"


def test_sql_fuentes_evidencia_jsonb(sql_text):
    """fuentes_evidencia debe ser JSONB con default '[]'."""
    assert "fuentes_evidencia JSONB NOT NULL DEFAULT '[]'" in sql_text


# ============================================================================
# B) Tests de los Pydantic models
# ============================================================================

def test_imports_kernel_catastro():
    """El módulo kernel.catastro debe exponer los 12 nombres declarados."""
    from kernel import catastro
    expected = {
        "EstadoModelo", "TipoLicencia", "Macroarea", "DominioInteligencia",
        "PrioridadEvento", "TipoEvento", "RolCurador",
        "CatastroModelo", "CatastroHistorial", "CatastroEvento",
        "CatastroNota", "CatastroCurador", "FuenteEvidencia",
    }
    for name in expected:
        assert hasattr(catastro, name), f"kernel.catastro no exporta {name}"


def test_enum_estado_valores():
    from kernel.catastro import EstadoModelo
    expected = {"production", "beta", "open-source", "deprecated", "alpha", "preview"}
    actual = {e.value for e in EstadoModelo}
    assert actual == expected, f"Enum EstadoModelo tiene {actual}, esperado {expected}"


def test_enum_tipo_evento_incluye_drift():
    from kernel.catastro import TipoEvento
    assert TipoEvento.MODEL_DRIFT_DETECTED.value == "model_drift_detected"


def test_modelo_valido_minimo():
    """Modelo construible con campos mínimos obligatorios."""
    from kernel.catastro import (
        CatastroModelo, Macroarea, EstadoModelo, TipoLicencia,
    )
    m = CatastroModelo(
        id="gpt-5-5-mini",
        nombre="GPT-5.5 Mini",
        proveedor="OpenAI",
        macroarea=Macroarea.INTELIGENCIA,
        dominios=["llm_frontier"],
    )
    assert m.id == "gpt-5-5-mini"
    assert m.estado == EstadoModelo.PRODUCTION
    assert m.tipo == TipoLicencia.PROPIETARIO
    assert m.confidence == 0.50
    assert m.quorum_alcanzado is False


def test_modelo_slug_format_invalido():
    """slug con uppercase o underscores debe fallar."""
    from kernel.catastro import CatastroModelo, Macroarea
    from pydantic import ValidationError

    for bad_id in ["GPT-5-5", "gpt_5_5_mini", "gpt 5.5"]:
        with pytest.raises(ValidationError):
            CatastroModelo(
                id=bad_id,
                nombre="x",
                proveedor="y",
                macroarea=Macroarea.INTELIGENCIA,
                dominios=["llm_frontier"],
            )


def test_modelo_dominios_vacios_fail():
    from kernel.catastro import CatastroModelo, Macroarea
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        CatastroModelo(
            id="claude-opus-4-7",
            nombre="Claude Opus 4.7",
            proveedor="Anthropic",
            macroarea=Macroarea.INTELIGENCIA,
            dominios=[],
        )


def test_curador_hitl_auto_corrige():
    """Si trust_score < 0.70, requiere_hitl debe auto-set a True."""
    from kernel.catastro import CatastroCurador, Macroarea
    c = CatastroCurador(
        id="claude-opus-4-7-inteligencia",
        macroarea=Macroarea.INTELIGENCIA,
        modelo_llm="claude-opus-4-7",
        proveedor="Anthropic",
        trust_score=0.65,
        requiere_hitl=False,  # mal puesto, debe auto-corregir
    )
    assert c.requiere_hitl is True, \
        f"trust_score=0.65 debe forzar requiere_hitl=True, got {c.requiere_hitl}"


def test_curador_trust_alto_no_hitl():
    from kernel.catastro import CatastroCurador, Macroarea
    c = CatastroCurador(
        id="gpt-5-5-pro-inteligencia",
        macroarea=Macroarea.INTELIGENCIA,
        modelo_llm="gpt-5-5-pro",
        proveedor="OpenAI",
        trust_score=0.95,
    )
    assert c.requiere_hitl is False


def test_fuente_evidencia_completa():
    from kernel.catastro import FuenteEvidencia
    f = FuenteEvidencia(
        url="https://artificialanalysis.ai/data/llms/models",
        fetched_at=datetime.utcnow(),
        payload_hash="abc12345",
        curador="claude-opus-4-7-inteligencia",
        tipo_dato="precio_input",
    )
    assert f.tipo_dato == "precio_input"


def test_evento_drift_construible():
    from kernel.catastro import CatastroEvento, TipoEvento, PrioridadEvento
    e = CatastroEvento(
        tipo=TipoEvento.MODEL_DRIFT_DETECTED,
        prioridad=PrioridadEvento.IMPORTANTE,
        descripcion="Drift detectado en clasificador del Radar",
        contexto={"old_model": "claude-sonnet-3-5", "new_model_recomendado": "claude-opus-4-7"},
    )
    assert e.tipo == TipoEvento.MODEL_DRIFT_DETECTED
    assert e.notificado is False


# ============================================================================
# C) Tests de integridad SQL ↔ Pydantic
# ============================================================================

def test_integridad_estados_sql_vs_pydantic(sql_text):
    """Los valores de EstadoModelo deben aparecer todos en el SQL."""
    from kernel.catastro import EstadoModelo
    for e in EstadoModelo:
        assert f"'{e.value}'" in sql_text, \
            f"EstadoModelo.{e.name}={e.value!r} no está en el SQL"


def test_integridad_tipos_evento_sql_vs_pydantic(sql_text):
    from kernel.catastro import TipoEvento
    for t in TipoEvento:
        assert f"'{t.value}'" in sql_text, \
            f"TipoEvento.{t.name}={t.value!r} no está en el SQL"


def test_integridad_prioridad_evento_sql_vs_pydantic(sql_text):
    from kernel.catastro import PrioridadEvento
    for p in PrioridadEvento:
        assert f"'{p.value}'" in sql_text, \
            f"PrioridadEvento.{p.name}={p.value!r} no está en el SQL"


def test_integridad_rol_curador_sql_vs_pydantic(sql_text):
    from kernel.catastro import RolCurador
    for r in RolCurador:
        assert f"'{r.value}'" in sql_text, \
            f"RolCurador.{r.name}={r.value!r} no está en el SQL"
