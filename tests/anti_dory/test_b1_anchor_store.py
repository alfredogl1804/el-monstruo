"""
Unit Tests — B1 Anchor Store Adapter
Anti-Dory FORGE v3.0 — Batch 005 Célula A

Tests with mocked Supabase client. No real DB writes.
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from kernel.anti_dory.b1_anchor_store import (
    Anchor,
    AnchorDuplicateError,
    AnchorInsertRequest,
    AnchorNotFoundError,
    AnchorSignatureError,
    AnchorStoreAdapter,
    AnchorStoreError,
)


@pytest.fixture
def mock_client():
    """Create a mock Supabase client."""
    client = MagicMock()
    return client


@pytest.fixture
def adapter(mock_client):
    """Create an AnchorStoreAdapter with mock client."""
    return AnchorStoreAdapter(client=mock_client)


@pytest.fixture
def sample_row():
    """Sample database row."""
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "concept": "soberania_datos",
        "definition": "Los datos del Monstruo pertenecen exclusivamente a T1.",
        "canon_source": "SOP v3.0",
        "canon_date": "2026-05-20T12:00:00+00:00",
        "t1_signature": "T1_SIGNED_2026-05-20",
        "created_at": "2026-05-20T12:00:00+00:00",
    }


class TestGetAnchor:
    def test_get_existing_anchor(self, adapter, mock_client, sample_row):
        mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
            MagicMock(data=[sample_row])
        )
        result = adapter.get_anchor("soberania_datos")
        assert isinstance(result, Anchor)
        assert result.concept == "soberania_datos"
        assert result.t1_signature == "T1_SIGNED_2026-05-20"

    def test_get_nonexistent_anchor(self, adapter, mock_client):
        mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
            MagicMock(data=[])
        )
        with pytest.raises(AnchorNotFoundError, match="not found"):
            adapter.get_anchor("nonexistent")


class TestListAnchors:
    def test_list_returns_anchors(self, adapter, mock_client, sample_row):
        mock_chain = mock_client.table.return_value.select.return_value
        mock_chain.order.return_value.range.return_value.execute.return_value = MagicMock(data=[sample_row, sample_row])
        result = adapter.list_anchors(limit=10)
        assert len(result) == 2
        assert all(isinstance(a, Anchor) for a in result)

    def test_list_empty(self, adapter, mock_client):
        mock_chain = mock_client.table.return_value.select.return_value
        mock_chain.order.return_value.range.return_value.execute.return_value = MagicMock(data=[])
        result = adapter.list_anchors()
        assert result == []


class TestSearchAnchors:
    def test_search_finds_matches(self, adapter, mock_client, sample_row):
        mock_client.table.return_value.select.return_value.or_.return_value.order.return_value.execute.return_value = (
            MagicMock(data=[sample_row])
        )
        result = adapter.search_anchors("soberania")
        assert len(result) == 1
        assert result[0].concept == "soberania_datos"

    def test_search_no_matches(self, adapter, mock_client):
        mock_client.table.return_value.select.return_value.or_.return_value.order.return_value.execute.return_value = (
            MagicMock(data=[])
        )
        result = adapter.search_anchors("nonexistent_query")
        assert result == []


class TestInsertAnchor:
    def test_insert_valid_anchor(self, adapter, mock_client, sample_row):
        mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[sample_row])
        request = AnchorInsertRequest(
            concept="soberania_datos",
            definition="Los datos del Monstruo pertenecen exclusivamente a T1.",
            canon_source="SOP v3.0",
            t1_signature="T1_SIGNED_2026-05-20",
        )
        result = adapter.insert_anchor(request)
        assert isinstance(result, Anchor)
        assert result.concept == "soberania_datos"

    def test_insert_without_signature_raises(self, adapter):
        request = AnchorInsertRequest(
            concept="test",
            definition="test def",
            canon_source=None,
            t1_signature="",
        )
        with pytest.raises(AnchorSignatureError, match="T1 signature is required"):
            adapter.insert_anchor(request)

    def test_insert_whitespace_signature_raises(self, adapter):
        request = AnchorInsertRequest(
            concept="test",
            definition="test def",
            canon_source=None,
            t1_signature="   ",
        )
        with pytest.raises(AnchorSignatureError):
            adapter.insert_anchor(request)

    def test_insert_duplicate_raises(self, adapter, mock_client):
        mock_client.table.return_value.insert.return_value.execute.side_effect = Exception(
            "duplicate key value violates unique constraint"
        )
        request = AnchorInsertRequest(
            concept="existing",
            definition="already exists",
            canon_source=None,
            t1_signature="T1_SIGNED",
        )
        with pytest.raises(AnchorDuplicateError, match="already exists"):
            adapter.insert_anchor(request)


class TestCountAnchors:
    def test_count_returns_number(self, adapter, mock_client):
        mock_client.table.return_value.select.return_value.execute.return_value = MagicMock(count=42)
        result = adapter.count_anchors()
        assert result == 42

    def test_count_returns_zero(self, adapter, mock_client):
        mock_client.table.return_value.select.return_value.execute.return_value = MagicMock(count=0)
        result = adapter.count_anchors()
        assert result == 0


class TestNoClientError:
    def test_no_client_raises_on_operation(self):
        adapter = AnchorStoreAdapter(client=None)
        with pytest.raises(AnchorStoreError, match="not initialized"):
            adapter.get_anchor("test")


class TestRowToAnchor:
    def test_conversion(self, sample_row):
        anchor = AnchorStoreAdapter._row_to_anchor(sample_row)
        assert anchor.id == "550e8400-e29b-41d4-a716-446655440000"
        assert anchor.concept == "soberania_datos"
        assert isinstance(anchor.canon_date, datetime)
        assert isinstance(anchor.created_at, datetime)

    def test_none_canon_source(self, sample_row):
        sample_row["canon_source"] = None
        anchor = AnchorStoreAdapter._row_to_anchor(sample_row)
        assert anchor.canon_source is None
