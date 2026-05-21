"""
Unit Tests — B4 Memento Integration
Anti-Dory FORGE v3.0 — Batch 005 Célula D

Tests with mocked Memento store. No production reads/writes.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from kernel.anti_dory.b4_memento import (
    Memory,
    MemoryStatus,
    MemoryValidation,
    MementoContext,
    MementoIntegration,
    compute_content_hash,
)


@pytest.fixture
def mock_store():
    return MagicMock()


@pytest.fixture
def integration(mock_store):
    return MementoIntegration(store=mock_store)


@pytest.fixture
def integration_no_store():
    return MementoIntegration(store=None)


@pytest.fixture
def valid_memory():
    content = "El Monstruo es soberano"
    return Memory(
        id="mem-001",
        content=content,
        content_hash=compute_content_hash(content),
        source="SOP",
        created_at=datetime.utcnow() - timedelta(hours=1),
        ttl_hours=720,
        metadata={},
    )


@pytest.fixture
def expired_memory():
    content = "Old doctrine"
    return Memory(
        id="mem-002",
        content=content,
        content_hash=compute_content_hash(content),
        source="legacy",
        created_at=datetime.utcnow() - timedelta(days=60),
        ttl_hours=24,
        metadata={},
    )


@pytest.fixture
def corrupted_memory():
    return Memory(
        id="mem-003",
        content="Tampered content",
        content_hash="wrong_hash_value",
        source="unknown",
        created_at=datetime.utcnow() - timedelta(hours=1),
        ttl_hours=720,
        metadata={},
    )


@pytest.fixture
def stale_memory():
    content = "Very old memory"
    return Memory(
        id="mem-004",
        content=content,
        content_hash=compute_content_hash(content),
        source="archive",
        created_at=datetime.utcnow() - timedelta(days=100),
        ttl_hours=None,  # No explicit TTL
        metadata={},
    )


class TestComputeContentHash:
    def test_deterministic(self):
        h1 = compute_content_hash("test")
        h2 = compute_content_hash("test")
        assert h1 == h2

    def test_different_content_different_hash(self):
        h1 = compute_content_hash("content A")
        h2 = compute_content_hash("content B")
        assert h1 != h2

    def test_sha256_length(self):
        h = compute_content_hash("test")
        assert len(h) == 64


class TestValidateMemory:
    def test_valid_memory_passes(self, integration, valid_memory):
        result = integration.validate_memory(valid_memory)
        assert result.status == MemoryStatus.VALID
        assert result.is_valid is True

    def test_expired_memory_detected(self, integration, expired_memory):
        result = integration.validate_memory(expired_memory)
        assert result.status == MemoryStatus.EXPIRED
        assert result.is_valid is False

    def test_corrupted_hash_detected(self, integration, corrupted_memory):
        result = integration.validate_memory(corrupted_memory)
        assert result.status == MemoryStatus.CORRUPTED
        assert result.is_valid is False
        assert "Hash mismatch" in result.reason

    def test_empty_content_corrupted(self, integration):
        memory = Memory(
            id="mem-empty", content="", content_hash="",
            source="test", created_at=datetime.utcnow(),
            ttl_hours=720, metadata={},
        )
        result = integration.validate_memory(memory)
        assert result.status == MemoryStatus.CORRUPTED
        assert "Empty content" in result.reason

    def test_stale_memory_detected(self, integration, stale_memory):
        result = integration.validate_memory(stale_memory)
        assert result.status == MemoryStatus.STALE
        assert result.is_valid is False


class TestIsMemoryExpired:
    def test_fresh_memory_not_expired(self, integration, valid_memory):
        assert integration.is_memory_expired(valid_memory) is False

    def test_old_memory_expired(self, integration, expired_memory):
        assert integration.is_memory_expired(expired_memory) is True

    def test_default_ttl_used_when_none(self, integration):
        memory = Memory(
            id="m", content="x", content_hash="", source="",
            created_at=datetime.utcnow() - timedelta(hours=100),
            ttl_hours=None, metadata={},
        )
        # Default TTL is 720h (30 days), 100h < 720h → not expired
        assert integration.is_memory_expired(memory) is False


class TestFetchContext:
    def test_no_store_returns_empty(self, integration_no_store):
        ctx = integration_no_store.fetch_context("query")
        assert isinstance(ctx, MementoContext)
        assert ctx.memories == []
        assert ctx.valid_count == 0

    def test_fetch_and_validate(self, integration, mock_store):
        content = "Test memory"
        mock_store.fetch_memories.return_value = [
            {
                "id": "mem-001",
                "content": content,
                "content_hash": compute_content_hash(content),
                "source": "test",
                "created_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                "ttl_hours": 720,
                "metadata": {},
            }
        ]
        ctx = integration.fetch_context("test query")
        assert len(ctx.memories) == 1
        assert ctx.valid_count == 1
        assert ctx.health_ratio == 1.0


class TestCheckDrift:
    def test_all_valid(self, integration, valid_memory):
        results = integration.check_drift([valid_memory, valid_memory])
        assert all(v.is_valid for v in results)

    def test_mixed_results(self, integration, valid_memory, corrupted_memory):
        results = integration.check_drift([valid_memory, corrupted_memory])
        assert results[0].is_valid is True
        assert results[1].is_valid is False


class TestMementoContext:
    def test_health_ratio_all_valid(self):
        ctx = MementoContext(
            memories=[], validations=[
                MemoryValidation("m1", MemoryStatus.VALID, "ok", True),
                MemoryValidation("m2", MemoryStatus.VALID, "ok", True),
            ],
            valid_count=2, stale_count=0, corrupted_count=0,
        )
        assert ctx.health_ratio == 1.0

    def test_health_ratio_half(self):
        ctx = MementoContext(
            memories=[], validations=[
                MemoryValidation("m1", MemoryStatus.VALID, "ok", True),
                MemoryValidation("m2", MemoryStatus.CORRUPTED, "bad", False),
            ],
            valid_count=1, stale_count=0, corrupted_count=1,
        )
        assert ctx.health_ratio == 0.5

    def test_health_ratio_empty(self):
        ctx = MementoContext(
            memories=[], validations=[],
            valid_count=0, stale_count=0, corrupted_count=0,
        )
        assert ctx.health_ratio == 1.0
