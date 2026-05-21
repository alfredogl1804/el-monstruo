"""
Unit Tests — B2 Claim Verification Gate
Anti-Dory FORGE v3.0 — Batch 005 Célula C

Tests with mocked Anchor Store. No external side effects.
"""

from unittest.mock import MagicMock

import pytest

from kernel.anti_dory.b2_claim_vg import (
    Claim,
    ClaimExtractor,
    ClaimVerdict,
    ClaimVerificationGate,
    GateResult,
    VerificationResult,
)


@pytest.fixture
def mock_anchor_reader():
    reader = MagicMock()
    return reader


@pytest.fixture
def extractor():
    return ClaimExtractor()


@pytest.fixture
def gate(mock_anchor_reader):
    return ClaimVerificationGate(anchor_reader=mock_anchor_reader)


@pytest.fixture
def gate_no_store():
    return ClaimVerificationGate(anchor_reader=None)


class TestClaimExtractor:
    def test_extract_claims_from_text(self, extractor):
        text = "El Monstruo es soberano. Los datos son privados."
        claims = extractor.extract(text)
        assert len(claims) >= 1
        assert all(isinstance(c, Claim) for c in claims)

    def test_extract_empty_text(self, extractor):
        assert extractor.extract("") == []
        assert extractor.extract("   ") == []

    def test_extract_no_claims(self, extractor):
        text = "Hola mundo"
        claims = extractor.extract(text)
        assert claims == []

    def test_extract_multiple_claims(self, extractor):
        text = "El sistema es seguro. Siempre valida claims. Nunca expone secrets."
        claims = extractor.extract(text)
        assert len(claims) >= 2

    def test_claim_indicators_detected(self, extractor):
        for indicator in ["es", "siempre", "nunca", "obligatorio", "prohibido"]:
            text = f"El sistema {indicator} correcto"
            claims = extractor.extract(text)
            assert len(claims) >= 1, f"Failed for indicator: {indicator}"


class TestClaimVerificationGate:
    def test_empty_text_passes(self, gate):
        result = gate.verify_text("")
        assert result.overall_verdict == ClaimVerdict.PASS
        assert result.total == 0

    def test_claim_with_matching_anchor_passes(self, gate, mock_anchor_reader):
        mock_anchor = MagicMock()
        mock_anchor.concept = "soberania_datos"
        mock_anchor_reader.search_anchors.return_value = [mock_anchor]

        claims = [Claim(text="Los datos son soberanos")]
        result = gate.verify_claims(claims)
        assert result.overall_verdict == ClaimVerdict.PASS
        assert result.pass_count == 1

    def test_claim_without_anchor_escalates(self, gate, mock_anchor_reader):
        mock_anchor_reader.search_anchors.return_value = []

        claims = [Claim(text="Novel claim without anchor")]
        result = gate.verify_claims(claims)
        assert result.overall_verdict == ClaimVerdict.ESCALATE
        assert result.escalate_count == 1

    def test_no_store_escalates_all(self, gate_no_store):
        claims = [Claim(text="Any claim")]
        result = gate_no_store.verify_claims(claims)
        assert result.overall_verdict == ClaimVerdict.ESCALATE

    def test_error_on_exception(self, gate, mock_anchor_reader):
        mock_anchor_reader.search_anchors.side_effect = Exception("DB error")
        claims = [Claim(text="Claim that causes error")]
        result = gate.verify_claims(claims)
        assert result.results[0].verdict == ClaimVerdict.ERROR

    def test_reject_overrides_escalate(self, gate, mock_anchor_reader):
        """If any claim is rejected, overall is REJECT."""
        # First claim passes, second escalates
        mock_anchor = MagicMock()
        mock_anchor.concept = "test"
        mock_anchor_reader.search_anchors.side_effect = [
            [mock_anchor],  # first claim matches
            [],  # second claim no match
        ]
        claims = [
            Claim(text="Aligned claim"),
            Claim(text="Novel claim"),
        ]
        result = gate.verify_claims(claims)
        # Should be ESCALATE (no rejects, but has escalations)
        assert result.overall_verdict == ClaimVerdict.ESCALATE

    def test_all_pass(self, gate, mock_anchor_reader):
        mock_anchor = MagicMock()
        mock_anchor.concept = "anchor_1"
        mock_anchor_reader.search_anchors.return_value = [mock_anchor]

        claims = [Claim(text="Claim 1"), Claim(text="Claim 2")]
        result = gate.verify_claims(claims)
        assert result.overall_verdict == ClaimVerdict.PASS
        assert result.pass_count == 2


class TestGateResult:
    def test_total_property(self):
        result = GateResult(
            overall_verdict=ClaimVerdict.PASS,
            results=[
                VerificationResult(claim=Claim(text="a"), verdict=ClaimVerdict.PASS, reason="ok"),
                VerificationResult(claim=Claim(text="b"), verdict=ClaimVerdict.PASS, reason="ok"),
            ],
            pass_count=2,
        )
        assert result.total == 2

    def test_empty_result(self):
        result = GateResult(overall_verdict=ClaimVerdict.PASS)
        assert result.total == 0
        assert result.pass_count == 0


class TestVerifyText:
    def test_full_pipeline(self, gate, mock_anchor_reader):
        mock_anchor = MagicMock()
        mock_anchor.concept = "seguridad"
        mock_anchor_reader.search_anchors.return_value = [mock_anchor]

        text = "El sistema es seguro. Siempre valida inputs."
        result = gate.verify_text(text)
        assert result.overall_verdict == ClaimVerdict.PASS
        assert result.total >= 1
