"""
Tests del Sprint 86 Bloque 3 — Persistencia atómica del Catastro.

Cobertura:
  - Serialización CatastroModelo / CatastroEvento / deltas
  - Resolución de credenciales lazy (anti-cache de os.environ)
  - dry_run automático (sin keys) + explícito (constructor)
  - Mock client_factory (sin tocar supabase real)
  - Parseo de respuesta RPC: dict, list, string JSON, None
  - Manejo de error RPC (excepción del cliente HTTP)
  - persist_many con mix de éxito y fallo
  - Identidad de marca: códigos catastro_persist_*
  - Integración con pipeline (persistence inyectada en run)
  - Disciplina os.environ: nunca cachea entre llamadas
  - Test opt-in real con SUPABASE_INTEGRATION_TESTS=true (skip default)

[Hilo Manus Catastro] · Sprint 86 Bloque 3 · 2026-05-04
"""
from __future__ import annotations

import os
import asyncio
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from kernel.catastro import (
    CatastroEvento,
    CatastroModelo,
    CatastroPersistence,
    CatastroPersistError,
    CatastroPersistMissingClient,
    CatastroPersistRpcFailure,
    CatastroPipeline,
    PersistResult,
    PrioridadEvento,
    TipoEvento,
    build_modelo_from_pipeline_persistible,
    __version__,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def modelo_minimo() -> CatastroModelo:
    """Modelo Pydantic mínimo válido para tests."""
    return CatastroModelo(
        id="gpt-test-mini",
        nombre="GPT Test Mini",
        proveedor="openai",
        dominios=["llm_frontier"],
        quality_score=85.0,
        precio_input_per_million=1.5,
        precio_output_per_million=5.0,
    )


@pytest.fixture
def evento_minimo() -> CatastroEvento:
    return CatastroEvento(
        tipo=TipoEvento.NEW_MODEL,
        prioridad=PrioridadEvento.INFO,
        modelo_id="gpt-test-mini",
        descripcion="Test event",
    )


@pytest.fixture
def trust_deltas_sample() -> dict[str, float]:
    return {
        "artificial_analysis": 0.0,
        "openrouter": -0.05,
        "lmarena": 0.0,
    }


@pytest.fixture
def env_clean(monkeypatch):
    """Limpia env vars de Supabase para que dry_run se active."""
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    yield


@pytest.fixture
def env_with_keys(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
    yield


def _make_mock_client(rpc_response_data, rpc_raises: Exception = None):
    """Construye un mock de supabase Client con .rpc().execute()."""
    client = MagicMock()
    rpc_chain = MagicMock()
    if rpc_raises is not None:
        rpc_chain.execute.side_effect = rpc_raises
    else:
        response = MagicMock()
        response.data = rpc_response_data
        rpc_chain.execute.return_value = response
    client.rpc.return_value = rpc_chain
    return client


# ============================================================================
# 1. Versionado y exports
# ============================================================================

class TestVersionado:
    def test_version_es_0_86_3(self):
        assert __version__ == "0.86.3"

    def test_persistence_exportada(self):
        from kernel.catastro import CatastroPersistence as CP
        assert CP is CatastroPersistence

    def test_helper_exportado(self):
        from kernel.catastro import build_modelo_from_pipeline_persistible as bm
        assert callable(bm)


# ============================================================================
# 2. Serialización
# ============================================================================

class TestSerializacion:
    def test_serialize_modelo_devuelve_dict(self, modelo_minimo):
        data = CatastroPersistence._serialize_modelo(modelo_minimo)
        assert isinstance(data, dict)
        assert data["id"] == "gpt-test-mini"
        assert data["proveedor"] == "openai"

    def test_serialize_modelo_excluye_embedding(self, modelo_minimo):
        data = CatastroPersistence._serialize_modelo(modelo_minimo)
        assert "embedding" not in data

    def test_serialize_evento_incluye_tipo_string(self, evento_minimo):
        data = CatastroPersistence._serialize_evento(evento_minimo)
        # Pydantic v2 mode="json" serializa Enums como su valor string
        assert data["tipo"] == "new_model"
        assert data["prioridad"] == "info"

    def test_serialize_deltas_normaliza_floats(self):
        result = CatastroPersistence._serialize_deltas({"a": 0.1, "b": -0.05})
        assert result == {"a": 0.1, "b": -0.05}
        assert all(isinstance(v, float) for v in result.values())

    def test_serialize_deltas_none_devuelve_dict_vacio(self):
        assert CatastroPersistence._serialize_deltas(None) == {}

    def test_serialize_deltas_dict_vacio_devuelve_dict_vacio(self):
        assert CatastroPersistence._serialize_deltas({}) == {}


# ============================================================================
# 3. Resolución de credenciales / dry_run
# ============================================================================

class TestCredenciales:
    def test_sin_env_vars_es_dry_run(self, env_clean):
        p = CatastroPersistence()
        assert p._is_dry_run() is True

    def test_con_env_vars_no_es_dry_run(self, env_with_keys):
        p = CatastroPersistence()
        assert p._is_dry_run() is False

    def test_dry_run_explicito_overridea_env_vars(self, env_with_keys):
        p = CatastroPersistence(dry_run=True)
        assert p._is_dry_run() is True

    def test_credenciales_explicitas_sobrescriben_env(self, env_clean):
        p = CatastroPersistence(
            supabase_url="https://x.supabase.co",
            supabase_key="explicit-key",
        )
        url, key = p._resolve_credentials()
        assert url == "https://x.supabase.co"
        assert key == "explicit-key"

    def test_credenciales_no_se_cachean_a_nivel_modulo(self, env_clean, monkeypatch):
        """Disciplina os.environ: cambios entre llamadas se reflejan."""
        p = CatastroPersistence()
        assert p._is_dry_run() is True
        monkeypatch.setenv("SUPABASE_URL", "https://x.supabase.co")
        monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "k")
        # Sin re-instanciar, _is_dry_run debe reflejar el nuevo estado
        assert p._is_dry_run() is False


# ============================================================================
# 4. Persist en modo dry_run
# ============================================================================

class TestPersistDryRun:
    def test_dry_run_devuelve_success_true_y_dry_true(
        self, env_clean, modelo_minimo, evento_minimo, trust_deltas_sample
    ):
        p = CatastroPersistence()
        result = p.persist(
            modelo=modelo_minimo,
            evento=evento_minimo,
            trust_deltas=trust_deltas_sample,
        )
        assert result.success is True
        assert result.dry_run is True
        assert result.modelo_id == "gpt-test-mini"
        assert result.error_code is None

    def test_dry_run_no_toca_red(self, env_clean, modelo_minimo):
        p = CatastroPersistence(client_factory=lambda u, k: pytest.fail("no debería instanciar"))
        result = p.persist(modelo=modelo_minimo)
        assert result.dry_run is True

    def test_dry_run_genera_evento_default_si_falta(self, env_clean, modelo_minimo):
        p = CatastroPersistence()
        result = p.persist(modelo=modelo_minimo)
        # Preview debe contener el evento autogenerado con tipo new_model
        assert result.rpc_params_preview["p_evento"]["tipo"] == "new_model"


# ============================================================================
# 5. Persist con mock client (RPC OK)
# ============================================================================

class TestPersistConMockOk:
    def test_rpc_dict_response_se_parsea(
        self, env_with_keys, modelo_minimo, evento_minimo
    ):
        rpc_data = {
            "modelo_id": "gpt-test-mini",
            "evento_id": "11111111-1111-1111-1111-111111111111",
            "curadores_actualizados": 2,
            "aplicado_at": "2026-05-04T12:00:00+00:00",
        }
        client = _make_mock_client(rpc_data)
        p = CatastroPersistence(client_factory=lambda u, k: client)
        result = p.persist(modelo=modelo_minimo, evento=evento_minimo)
        assert result.success is True
        assert result.dry_run is False
        assert result.evento_id == "11111111-1111-1111-1111-111111111111"
        assert result.curadores_actualizados == 2

    def test_rpc_list_response_toma_primer_elemento(
        self, env_with_keys, modelo_minimo
    ):
        rpc_data = [
            {"modelo_id": "gpt-test-mini", "curadores_actualizados": 1, "evento_id": None, "aplicado_at": "2026-05-04T12:00:00+00:00"},
        ]
        client = _make_mock_client(rpc_data)
        p = CatastroPersistence(client_factory=lambda u, k: client)
        result = p.persist(modelo=modelo_minimo)
        assert result.success is True
        assert result.curadores_actualizados == 1

    def test_rpc_string_json_se_parsea(self, env_with_keys, modelo_minimo):
        rpc_data = '{"modelo_id":"gpt-test-mini","curadores_actualizados":3,"evento_id":null,"aplicado_at":"2026-05-04T12:00:00+00:00"}'
        client = _make_mock_client(rpc_data)
        p = CatastroPersistence(client_factory=lambda u, k: client)
        result = p.persist(modelo=modelo_minimo)
        assert result.success is True
        assert result.curadores_actualizados == 3

    def test_rpc_llamada_con_nombre_funcion_correcto(
        self, env_with_keys, modelo_minimo
    ):
        client = _make_mock_client({"modelo_id": "gpt-test-mini"})
        p = CatastroPersistence(client_factory=lambda u, k: client)
        p.persist(modelo=modelo_minimo)
        # Verificar que se llamó client.rpc("catastro_apply_quorum_outcome", params)
        assert client.rpc.called
        args, _ = client.rpc.call_args
        assert args[0] == "catastro_apply_quorum_outcome"
        params = args[1]
        assert "p_modelo" in params
        assert "p_evento" in params
        assert "p_trust_deltas" in params
        assert params["p_modelo"]["id"] == "gpt-test-mini"


# ============================================================================
# 6. Persist con mock client (errores)
# ============================================================================

class TestPersistConMockError:
    def test_rpc_excepcion_devuelve_persist_failure(
        self, env_with_keys, modelo_minimo
    ):
        client = _make_mock_client(None, rpc_raises=RuntimeError("PostgREST 500"))
        p = CatastroPersistence(client_factory=lambda u, k: client)
        result = p.persist(modelo=modelo_minimo)
        assert result.success is False
        assert result.error_code == CatastroPersistRpcFailure.code
        assert "PostgREST 500" in result.error_message

    def test_rpc_response_data_none_devuelve_failure(
        self, env_with_keys, modelo_minimo
    ):
        client = _make_mock_client(None)
        p = CatastroPersistence(client_factory=lambda u, k: client)
        result = p.persist(modelo=modelo_minimo)
        assert result.success is False
        assert "vacía o no parseable" in result.error_message

    def test_falta_supabase_lib_lanza_missing_client(
        self, env_with_keys, modelo_minimo, monkeypatch
    ):
        """Si no se pasa client_factory y supabase no está instalado."""
        # Forzamos que el import falle
        import sys
        original_modules = sys.modules.copy()
        sys.modules["supabase"] = None  # Hace que `from supabase import ...` falle

        try:
            p = CatastroPersistence()  # sin client_factory
            with pytest.raises(CatastroPersistMissingClient):
                p._get_client()
        finally:
            # Restaurar
            sys.modules.clear()
            sys.modules.update(original_modules)


# ============================================================================
# 7. persist_many
# ============================================================================

class TestPersistMany:
    def test_persist_many_dry_run_todos_ok(self, env_clean):
        p = CatastroPersistence()
        items = [
            {"modelo": CatastroModelo(id=f"model-{i}", nombre=f"M{i}", proveedor="x", dominios=["llm_frontier"])}
            for i in range(3)
        ]
        results = p.persist_many(items)
        assert len(results) == 3
        assert all(r.success and r.dry_run for r in results)

    def test_persist_many_continua_aunque_uno_falle(self, env_with_keys):
        # Cliente que falla SOLO en la 2da llamada
        call_count = {"n": 0}

        class FlakyClient:
            def rpc(self, name, params):
                call_count["n"] += 1
                chain = MagicMock()
                if call_count["n"] == 2:
                    chain.execute.side_effect = RuntimeError("boom")
                else:
                    response = MagicMock()
                    response.data = {"modelo_id": params["p_modelo"]["id"], "curadores_actualizados": 0, "evento_id": None, "aplicado_at": "2026-05-04T12:00:00+00:00"}
                    chain.execute.return_value = response
                return chain

        p = CatastroPersistence(client_factory=lambda u, k: FlakyClient())
        items = [
            {"modelo": CatastroModelo(id=f"m-{i}", nombre=f"M{i}", proveedor="x", dominios=["llm_frontier"])}
            for i in range(3)
        ]
        results = p.persist_many(items)
        assert len(results) == 3
        assert results[0].success is True
        assert results[1].success is False  # boom
        assert results[2].success is True


# ============================================================================
# 8. Identidad de marca en errores
# ============================================================================

class TestIdentidadMarca:
    def test_error_codes_tienen_prefijo_catastro_persist(self):
        assert CatastroPersistError.code.startswith("catastro_persist_")
        assert CatastroPersistRpcFailure.code.startswith("catastro_persist_")
        assert CatastroPersistMissingClient.code.startswith("catastro_persist_")

    def test_rpc_failure_y_missing_client_son_distinguibles(self):
        assert CatastroPersistRpcFailure.code != CatastroPersistMissingClient.code


# ============================================================================
# 9. build_modelo_from_pipeline_persistible
# ============================================================================

class TestBuildModeloHelper:
    def test_construye_modelo_valido_con_minimo(self):
        persistible = {
            "slug": "claude-opus-4-7",
            "fields": {
                "organization": "anthropic",
                "pricing.input_per_million": 15.0,
                "pricing.output_per_million": 75.0,
            },
            "presence_confidence": 1.0,
            "confirming_sources": ["artificial_analysis", "openrouter", "lmarena"],
        }
        modelo = build_modelo_from_pipeline_persistible(
            slug="claude-opus-4-7",
            persistible=persistible,
            quorum_results=[],
        )
        assert modelo.id == "claude-opus-4-7"
        assert modelo.proveedor == "anthropic"
        assert modelo.precio_input_per_million == 15.0
        assert modelo.precio_output_per_million == 75.0
        assert modelo.confidence == 1.0
        assert modelo.quorum_alcanzado is True
        assert len(modelo.fuentes_evidencia) == 3


# ============================================================================
# 10. Integración con pipeline (sin red)
# ============================================================================

class TestIntegracionPipeline:
    def test_pipeline_acepta_persistence_inyectada(self):
        custom_p = CatastroPersistence(dry_run=True)
        pipeline = CatastroPipeline(dry_run=True, persistence=custom_p)
        assert pipeline.persistence is custom_p

    def test_pipeline_construye_persistence_default_si_no_pasa(self):
        pipeline = CatastroPipeline(dry_run=True)
        assert isinstance(pipeline.persistence, CatastroPersistence)

    def test_pipeline_run_dry_invoca_persistence_y_no_falla(self):
        pipeline = CatastroPipeline(dry_run=True)
        result = asyncio.run(pipeline.run())
        # Con sources dry_run, las fuentes pueden devolver fakes — verificamos
        # que el pipeline NO crashee y que persist_results sea una lista
        assert isinstance(result.persist_results, list)
        # Si hay persistibles, todos deben estar en dry_run
        for pr in result.persist_results:
            assert pr.dry_run is True


# ============================================================================
# 11. Test opt-in real (skip default)
# ============================================================================

@pytest.mark.skipif(
    os.environ.get("SUPABASE_INTEGRATION_TESTS", "").lower() != "true",
    reason="opt-in: setea SUPABASE_INTEGRATION_TESTS=true + SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY"
)
class TestIntegracionRealOptIn:
    def test_rpc_real_smoke(self, modelo_minimo):
        """Smoke test contra Supabase real. Solo corre con flag explícita."""
        p = CatastroPersistence()
        result = p.persist(
            modelo=modelo_minimo,
            trust_deltas={"artificial_analysis": 0.0},
        )
        assert result.dry_run is False
        # Debería haber tenido success o error de RPC concreto
        assert result.success or result.error_code == CatastroPersistRpcFailure.code
