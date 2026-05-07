"""Tests del decorator @requires_perplexity_validation (DSC-V-001)."""
from __future__ import annotations

import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kernel.validation import (  # noqa: E402
    ClaimRecord,
    StaleClaimError,
    record_validation,
    requires_perplexity_validation,
)
from kernel.validation.perplexity_decorator import (  # noqa: E402
    LocalFileStorage,
    set_default_storage,
)


def _fresh_storage() -> LocalFileStorage:
    f = tempfile.NamedTemporaryFile(
        "w", suffix=".jsonl", delete=False, encoding="utf-8"
    )
    f.close()
    return LocalFileStorage(Path(f.name))


def test_claim_sin_registro_levanta_stale():
    storage = _fresh_storage()
    set_default_storage(storage)

    @requires_perplexity_validation(claim_type="cpc_benchmark_2026:saas_b2b")
    def get_cpc() -> float:
        return 12.50

    try:
        get_cpc()
        raise AssertionError("debio levantar StaleClaimError")
    except StaleClaimError as e:
        assert "DSC-V-001" in str(e)
        assert "cpc_benchmark_2026:saas_b2b" in str(e)


def test_claim_con_registro_vigente_ejecuta_normal():
    storage = _fresh_storage()
    set_default_storage(storage)

    record_validation(
        claim_type="model_availability_top_llm",
        claim_value="claude-opus-4-7",
        validator="perplexity",
        evidence_url="https://perplexity.ai/abc123",
        ttl_hours=24,
        storage=storage,
    )

    @requires_perplexity_validation(
        claim_type="model_availability_top_llm",
        storage=storage,
    )
    def get_llm() -> str:
        return "claude-opus-4-7"

    result = get_llm()
    assert result == "claude-opus-4-7"


def test_claim_con_registro_expirado_levanta_stale():
    storage = _fresh_storage()

    expired = ClaimRecord(
        claim_type="cpc_benchmark_2026:saas_b2b",
        claim_fingerprint="abc",
        claim_value="$12.50",
        validator="perplexity",
        evidence_url=None,
        timestamp_unix=time.time() - (10 * 3600),
        ttl_seconds=3600,
    )
    storage.insert(expired)

    @requires_perplexity_validation(
        claim_type="cpc_benchmark_2026:saas_b2b",
        storage=storage,
    )
    def get_cpc() -> float:
        return 12.50

    try:
        get_cpc()
        raise AssertionError("debio levantar StaleClaimError por expiracion")
    except StaleClaimError as e:
        assert "VENCIDO" in str(e) or "vencido" in str(e).lower()
        assert "Re-validar" in str(e) or "re-validar" in str(e).lower()


def test_record_validation_returns_record_with_fingerprint():
    storage = _fresh_storage()
    rec = record_validation(
        claim_type="audience_size_2026:cip",
        claim_value="50000_inversionistas_yucatecos",
        validator="manus_realtime",
        ttl_hours=12,
        storage=storage,
    )
    assert rec.claim_type == "audience_size_2026:cip"
    assert rec.validator == "manus_realtime"
    assert rec.ttl_seconds == 12 * 3600
    assert len(rec.claim_fingerprint) == 32

    found = storage.find_latest("audience_size_2026:cip")
    assert found is not None
    assert found.claim_fingerprint == rec.claim_fingerprint


def test_decorator_attribute_introspection():
    @requires_perplexity_validation(claim_type="x", ttl_hours=48)
    def f() -> int:
        return 1

    meta = getattr(f, "__perplexity_validation__")
    assert meta["claim_type"] == "x"
    assert meta["ttl_hours"] == 48


def test_supabase_storage_interface_mocked():
    from kernel.validation._storage_supabase import SupabaseStorage

    inserted_payloads: list[dict] = []

    class _MockChain:
        def __init__(self, table_name: str, store: list):
            self._table = table_name
            self._store = store
            self._filter_claim_type = None
            self._filter_fingerprint = None

        def select(self, *_a, **_kw): return self
        def eq(self, col, val):
            if col == "claim_type":
                self._filter_claim_type = val
            elif col == "claim_fingerprint":
                self._filter_fingerprint = val
            return self
        def order(self, *_a, **_kw): return self
        def limit(self, _n): return self

        def execute(self):
            class _R: pass
            r = _R()
            rows = self._store
            if self._filter_claim_type:
                rows = [x for x in rows if x.get("claim_type") == self._filter_claim_type]
            if self._filter_fingerprint:
                rows = [x for x in rows if x.get("claim_fingerprint") == self._filter_fingerprint]
            r.data = sorted(rows, key=lambda x: -x["timestamp_unix"])
            return r

        def insert(self, payload):
            inserted_payloads.append(payload)
            self._store.append(payload)
            return self

    class _MockClient:
        def __init__(self):
            self._store = []
        def table(self, name):
            return _MockChain(name, self._store)

    client = _MockClient()
    storage = SupabaseStorage(client)

    rec = ClaimRecord(
        claim_type="cpc_benchmark_2026:saas_b2b",
        claim_fingerprint="abc1234567890",
        claim_value="$12.50",
        validator="perplexity",
        evidence_url=None,
        timestamp_unix=time.time(),
        ttl_seconds=3600,
    )
    storage.insert(rec)
    assert len(inserted_payloads) == 1
    assert inserted_payloads[0]["claim_type"] == "cpc_benchmark_2026:saas_b2b"

    found = storage.find_latest("cpc_benchmark_2026:saas_b2b")
    assert found is not None
    assert found.claim_fingerprint == "abc1234567890"


def test_no_record_for_different_claim_type_levanta():
    storage = _fresh_storage()
    record_validation(
        claim_type="claim_type_A",
        claim_value="A",
        validator="perplexity",
        storage=storage,
    )

    @requires_perplexity_validation(claim_type="claim_type_B", storage=storage)
    def f() -> str:
        return "B"

    try:
        f()
        raise AssertionError("debio levantar StaleClaimError")
    except StaleClaimError:
        pass


if __name__ == "__main__":
    test_claim_sin_registro_levanta_stale()
    test_claim_con_registro_vigente_ejecuta_normal()
    test_claim_con_registro_expirado_levanta_stale()
    test_record_validation_returns_record_with_fingerprint()
    test_decorator_attribute_introspection()
    test_supabase_storage_interface_mocked()
    test_no_record_for_different_claim_type_levanta()
    print("\n[ok] Los 7 tests del decorator @requires_perplexity_validation pasaron.")
