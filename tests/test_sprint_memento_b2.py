"""
Tests del Sprint Memento Bloque 2 — MementoValidator + lectores de fuentes.

Cubre:
    - Modelos Pydantic (validación de shape)
    - read_credential_source() con fixture local
    - SourceCache TTL + invalidate
    - MementoValidator: ok / discrepancy / unknown_operation / source_unavailable
    - Mocks de fetchers para simular Railway sin llamadas reales
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from kernel.memento.models import (
    CriticalOperation,
    Discrepancy,
    MementoValidationRequest,
    SourceOfTruth,
    ValidationResult,
    ValidationStatus,
)
from kernel.memento.sources import (
    SourceCache,
    _hash_content,
    read_credential_source,
)
from kernel.memento.validator import MementoValidator


FIXTURE_PATH = "tests/fixtures/credentials_md_sample.md"


# ===========================================================================
# Fixtures comunes
# ===========================================================================

@pytest.fixture(autouse=True)
def _set_repo_root(monkeypatch):
    """Apunta MEMENTO_REPO_ROOT al root del repo donde corren los tests."""
    repo_root = Path(__file__).resolve().parent.parent
    monkeypatch.setenv("MEMENTO_REPO_ROOT", str(repo_root))


@pytest.fixture
def critical_op_sql():
    return CriticalOperation(
        id="sql_against_production",
        nombre="SQL Against Production",
        descripcion="Test op",
        triggers=["host_matches_production_pattern"],
        requires_validation=True,
        requires_confirmation="pre_flight_credentials_md",
        source_of_truth_ids=["ticketlike_credentials"],
        activo=True,
    )


@pytest.fixture
def critical_op_inactive():
    return CriticalOperation(
        id="legacy_op",
        nombre="Legacy",
        descripcion="Inactive",
        triggers=[],
        activo=False,
    )


@pytest.fixture
def source_ticketlike():
    return SourceOfTruth(
        id="ticketlike_credentials",
        nombre="Ticketlike Credentials",
        descripcion="Test source",
        source_type="repo_file",
        location=FIXTURE_PATH,
        parser_id="credentials_md_v1",
        cache_ttl_seconds=60,
    )


@pytest.fixture
def validator(critical_op_sql, source_ticketlike):
    return MementoValidator(
        critical_operations={critical_op_sql.id: critical_op_sql},
        sources_of_truth={source_ticketlike.id: source_ticketlike},
    )


# ===========================================================================
# Tests de modelos
# ===========================================================================

class TestModels:
    def test_validation_status_enum(self):
        assert ValidationStatus.OK.value == "ok"
        assert ValidationStatus.DISCREPANCY_DETECTED.value == "discrepancy_detected"
        assert ValidationStatus.UNKNOWN_OPERATION.value == "unknown_operation"
        assert ValidationStatus.SOURCE_UNAVAILABLE.value == "source_unavailable"

    def test_validation_result_minimal(self):
        result = ValidationResult(
            validation_status=ValidationStatus.OK,
            proceed=True,
            validation_id="mv_2026-05-04_a1b2c3",
        )
        assert result.proceed is True
        assert result.context_freshness_seconds == 0
        assert result.discrepancy is None

    def test_discrepancy_shape(self):
        disc = Discrepancy(
            field="host",
            context_used="gateway01.us-east-1.prod.aws.tidbcloud.com",
            source_of_truth="gateway05.us-east-1.prod.aws.tidbcloud.com",
            source="skills/ticketlike-ops/references/credentials.md",
        )
        assert disc.field == "host"
        assert disc.source_last_updated is None

    def test_request_validation(self):
        req = MementoValidationRequest(
            hilo_id="hilo_manus_ticketlike",
            operation="sql_against_production",
            context_used={"host": "x", "user": "y"},
        )
        assert req.intent_summary is None

    def test_request_rejects_empty_hilo_id(self):
        with pytest.raises(Exception):
            MementoValidationRequest(
                hilo_id="",
                operation="sql_against_production",
                context_used={},
            )

    def test_critical_operation_default_active(self):
        op = CriticalOperation(
            id="x",
            nombre="X",
            descripcion="d",
            triggers=[],
        )
        assert op.activo is True
        assert op.requires_validation is True

    def test_source_of_truth_invalid_type(self):
        with pytest.raises(Exception):
            SourceOfTruth(
                id="x",
                nombre="X",
                descripcion="d",
                source_type="invalid_type",
                location="x",
            )


# ===========================================================================
# Tests de read_credential_source
# ===========================================================================

class TestCredentialSource:
    def test_reads_fixture(self):
        result = read_credential_source(FIXTURE_PATH)
        assert "value" in result
        assert "fetched_at" in result
        assert "source_id" in result
        assert "raw_hash" in result

    def test_parses_host_field(self):
        result = read_credential_source(FIXTURE_PATH)
        assert result["value"]["host"] == "gateway05.us-east-1.prod.aws.tidbcloud.com"

    def test_parses_credential_hash(self):
        result = read_credential_source(FIXTURE_PATH)
        assert result["value"]["credential_hash_first_8"] == "4N6caSwp"

    def test_parses_user_and_db(self):
        result = read_credential_source(FIXTURE_PATH)
        assert result["value"]["user"] == "37Hy7adB53QmFW4.root"
        assert result["value"]["db"] == "R5HMD5sAyPAWW34dhuZc9u"

    def test_raises_on_missing_file(self):
        with pytest.raises(FileNotFoundError):
            read_credential_source("tests/fixtures/does_not_exist.md")

    def test_hash_is_deterministic(self):
        a = read_credential_source(FIXTURE_PATH)
        b = read_credential_source(FIXTURE_PATH)
        assert a["raw_hash"] == b["raw_hash"]


# ===========================================================================
# Tests del SourceCache
# ===========================================================================

class TestSourceCache:
    @pytest.mark.asyncio
    async def test_cache_miss_calls_fetcher(self):
        cache = SourceCache()
        calls = {"n": 0}

        def fetcher():
            calls["n"] += 1
            return {"value": {"x": 1}, "fetched_at": datetime.now(timezone.utc), "source_id": "s", "raw_hash": "h"}

        result = await cache.get_or_fetch(source_id="s", ttl_seconds=60, fetcher=fetcher)
        assert result["value"]["x"] == 1
        assert calls["n"] == 1

    @pytest.mark.asyncio
    async def test_cache_hit_does_not_call_fetcher(self):
        cache = SourceCache()
        calls = {"n": 0}

        def fetcher():
            calls["n"] += 1
            return {"value": {"x": 1}, "fetched_at": datetime.now(timezone.utc), "source_id": "s", "raw_hash": "h"}

        await cache.get_or_fetch(source_id="s", ttl_seconds=60, fetcher=fetcher)
        await cache.get_or_fetch(source_id="s", ttl_seconds=60, fetcher=fetcher)
        assert calls["n"] == 1

    @pytest.mark.asyncio
    async def test_invalidate_forces_refetch(self):
        cache = SourceCache()
        calls = {"n": 0}

        def fetcher():
            calls["n"] += 1
            return {"value": {"x": calls["n"]}, "fetched_at": datetime.now(timezone.utc), "source_id": "s", "raw_hash": "h"}

        await cache.get_or_fetch(source_id="s", ttl_seconds=60, fetcher=fetcher)
        await cache.invalidate("s")
        await cache.get_or_fetch(source_id="s", ttl_seconds=60, fetcher=fetcher)
        assert calls["n"] == 2

    @pytest.mark.asyncio
    async def test_get_freshness_none_if_not_cached(self):
        cache = SourceCache()
        assert await cache.get_freshness("nonexistent") is None

    @pytest.mark.asyncio
    async def test_get_freshness_returns_age(self):
        cache = SourceCache()

        def fetcher():
            return {"value": {}, "fetched_at": datetime.now(timezone.utc), "source_id": "s", "raw_hash": "h"}

        await cache.get_or_fetch(source_id="s", ttl_seconds=60, fetcher=fetcher)
        await asyncio.sleep(0.01)
        age = await cache.get_freshness("s")
        assert age is not None
        assert age >= 0

    @pytest.mark.asyncio
    async def test_async_fetcher_is_awaited(self):
        cache = SourceCache()

        async def afetcher():
            await asyncio.sleep(0.001)
            return {"value": {"async": True}, "fetched_at": datetime.now(timezone.utc), "source_id": "s", "raw_hash": "h"}

        result = await cache.get_or_fetch(source_id="s", ttl_seconds=60, fetcher=afetcher)
        assert result["value"]["async"] is True

    @pytest.mark.asyncio
    async def test_clear_removes_all(self):
        cache = SourceCache()

        def fetcher():
            return {"value": {}, "fetched_at": datetime.now(timezone.utc), "source_id": "s", "raw_hash": "h"}

        await cache.get_or_fetch(source_id="s", ttl_seconds=60, fetcher=fetcher)
        await cache.clear()
        assert await cache.get_freshness("s") is None

    @pytest.mark.asyncio
    async def test_invalid_fetcher_shape_raises(self):
        cache = SourceCache()

        def bad_fetcher():
            return "not a dict"

        with pytest.raises(RuntimeError, match="source_fetcher_invalid_shape"):
            await cache.get_or_fetch(source_id="s", ttl_seconds=60, fetcher=bad_fetcher)


# ===========================================================================
# Tests del MementoValidator
# ===========================================================================

class TestMementoValidator:
    @pytest.mark.asyncio
    async def test_validate_ok_when_context_matches(self, validator):
        # Contexto que coincide con la fixture
        result = await validator.validate(
            operation="sql_against_production",
            context_used={
                "host": "gateway05.us-east-1.prod.aws.tidbcloud.com",
                "user": "37Hy7adB53QmFW4.root",
                "credential_hash_first_8": "4N6caSwp",
            },
            hilo_id="hilo_test",
        )
        assert result.proceed is True
        assert result.validation_status == ValidationStatus.OK
        assert result.discrepancy is None
        assert result.validation_id.startswith("mv_")

    @pytest.mark.asyncio
    async def test_validate_discrepancy_when_host_stale(self, validator):
        # Contexto con host viejo (gateway01) — el incidente TiDB del 2026-05-04
        result = await validator.validate(
            operation="sql_against_production",
            context_used={
                "host": "gateway01.us-east-1.prod.aws.tidbcloud.com",
                "user": "37Hy7adB53QmFW4.root",
                "credential_hash_first_8": "4N6caSwp",
            },
            hilo_id="hilo_test",
        )
        assert result.proceed is False
        assert result.validation_status == ValidationStatus.DISCREPANCY_DETECTED
        assert result.discrepancy is not None
        assert result.discrepancy.field == "host"
        assert "gateway01" in str(result.discrepancy.context_used)
        assert "gateway05" in str(result.discrepancy.source_of_truth)
        assert "context_stale_or_contaminated" in (result.remediation or "")

    @pytest.mark.asyncio
    async def test_validate_unknown_operation(self, validator):
        result = await validator.validate(
            operation="never_registered_operation",
            context_used={},
            hilo_id="hilo_test",
        )
        assert result.proceed is False
        assert result.validation_status == ValidationStatus.UNKNOWN_OPERATION
        assert "operation_not_in_catalog" in (result.remediation or "")

    @pytest.mark.asyncio
    async def test_validate_inactive_operation_treated_as_unknown(self, critical_op_inactive, source_ticketlike):
        v = MementoValidator(
            critical_operations={critical_op_inactive.id: critical_op_inactive},
            sources_of_truth={source_ticketlike.id: source_ticketlike},
        )
        result = await v.validate(
            operation="legacy_op",
            context_used={},
        )
        assert result.proceed is False
        assert result.validation_status == ValidationStatus.UNKNOWN_OPERATION

    @pytest.mark.asyncio
    async def test_validate_source_unavailable(self, critical_op_sql, source_ticketlike):
        # source con location apuntando a archivo inexistente
        broken_source = source_ticketlike.model_copy(update={"location": "tests/fixtures/missing.md"})
        v = MementoValidator(
            critical_operations={critical_op_sql.id: critical_op_sql},
            sources_of_truth={broken_source.id: broken_source},
        )
        result = await v.validate(
            operation="sql_against_production",
            context_used={"host": "x"},
        )
        assert result.proceed is False
        assert result.validation_status == ValidationStatus.SOURCE_UNAVAILABLE
        assert "source_read_failed" in (result.remediation or "")

    @pytest.mark.asyncio
    async def test_validate_with_injected_mock_fetcher(self, critical_op_sql, source_ticketlike):
        captured = {"called": 0}

        def mock_fetcher():
            captured["called"] += 1
            return {
                "value": {"host": "mocked-host.example.com", "user": "mock-user"},
                "fetched_at": datetime.now(timezone.utc),
                "source_id": source_ticketlike.id,
                "raw_hash": "mockhash",
            }

        v = MementoValidator(
            critical_operations={critical_op_sql.id: critical_op_sql},
            sources_of_truth={source_ticketlike.id: source_ticketlike},
            source_fetchers={source_ticketlike.id: mock_fetcher},
        )

        # OK case con valor del mock
        ok = await v.validate(
            operation="sql_against_production",
            context_used={"host": "mocked-host.example.com", "user": "mock-user"},
        )
        assert ok.proceed is True
        assert captured["called"] == 1

    @pytest.mark.asyncio
    async def test_validate_partial_context_only_compares_overlap(self, validator):
        # context_used solo trae 'host' — los demás campos no se comparan
        result = await validator.validate(
            operation="sql_against_production",
            context_used={"host": "gateway05.us-east-1.prod.aws.tidbcloud.com"},
        )
        assert result.proceed is True

    @pytest.mark.asyncio
    async def test_validate_op_without_sources_passes(self, source_ticketlike):
        op = CriticalOperation(
            id="op_sin_fuentes",
            nombre="X",
            descripcion="d",
            triggers=[],
            source_of_truth_ids=[],
            activo=True,
        )
        v = MementoValidator(
            critical_operations={op.id: op},
            sources_of_truth={source_ticketlike.id: source_ticketlike},
        )
        result = await v.validate(operation="op_sin_fuentes", context_used={})
        assert result.proceed is True
        assert result.validation_status == ValidationStatus.OK

    @pytest.mark.asyncio
    async def test_invalidate_cache_forces_refetch(self, validator):
        await validator.validate(
            operation="sql_against_production",
            context_used={"host": "gateway05.us-east-1.prod.aws.tidbcloud.com"},
        )
        f1 = await validator.get_freshness("ticketlike_credentials")
        assert f1 is not None
        await validator.invalidate_cache("ticketlike_credentials")
        f2 = await validator.get_freshness("ticketlike_credentials")
        assert f2 is None

    @pytest.mark.asyncio
    async def test_validation_id_format(self, validator):
        result = await validator.validate(
            operation="sql_against_production",
            context_used={"host": "gateway05.us-east-1.prod.aws.tidbcloud.com"},
        )
        # mv_<isoZ>_<hex6>
        parts = result.validation_id.split("_")
        assert parts[0] == "mv"
        assert len(parts[-1]) == 6
        # parts[1:-1] forman el timestamp
        ts_part = "_".join(parts[1:-1])
        assert "T" in ts_part

    @pytest.mark.asyncio
    async def test_two_validations_have_different_ids(self, validator):
        r1 = await validator.validate(
            operation="sql_against_production",
            context_used={"host": "gateway05.us-east-1.prod.aws.tidbcloud.com"},
        )
        r2 = await validator.validate(
            operation="sql_against_production",
            context_used={"host": "gateway05.us-east-1.prod.aws.tidbcloud.com"},
        )
        assert r1.validation_id != r2.validation_id


# ===========================================================================
# Tests de regresión específicos del incidente TiDB del 2026-05-04
# ===========================================================================

class TestRegresionFalsoPositivoTiDB:
    """
    Reproduce el incidente del 2026-05-04 ("Falso Positivo TiDB"):
    Hilo Manus ticketlike usó host fantasma `gateway01` heredado de su
    contexto compactado en lugar de leer credentials.md fresh.

    Estos tests verifican que la Capa Memento detecta y rechaza
    exactamente ese tipo de discrepancia.
    """

    @pytest.mark.asyncio
    async def test_rechaza_gateway01_fantasma(self, validator):
        result = await validator.validate(
            operation="sql_against_production",
            context_used={"host": "gateway01.us-east-1.prod.aws.tidbcloud.com"},
            hilo_id="hilo_manus_ticketlike",
            intent_summary="Run E2E test post Stripe rotation",
        )
        assert result.proceed is False
        assert result.discrepancy is not None
        assert result.discrepancy.field == "host"

    @pytest.mark.asyncio
    async def test_acepta_gateway05_real(self, validator):
        result = await validator.validate(
            operation="sql_against_production",
            context_used={"host": "gateway05.us-east-1.prod.aws.tidbcloud.com"},
            hilo_id="hilo_manus_ticketlike",
        )
        assert result.proceed is True

    @pytest.mark.asyncio
    async def test_rechaza_credential_hash_obsoleto(self, validator):
        # Hash heredado de un commit anterior — patrón "credenciales heredadas
        # de contexto compactado de Manus" (semilla 30).
        result = await validator.validate(
            operation="sql_against_production",
            context_used={
                "host": "gateway05.us-east-1.prod.aws.tidbcloud.com",
                "credential_hash_first_8": "OLD_HASH",
            },
            hilo_id="hilo_manus_ticketlike",
        )
        assert result.proceed is False
        assert result.discrepancy is not None
        assert result.discrepancy.field == "credential_hash_first_8"
