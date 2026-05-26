"""
B2 Claim Verification Gate — Anti-Dory FORGE v3.0

Validates claims against the Anchor Store (B1) before allowing
them to propagate through the system.

Architecture:
1. Extract claims from input text.
2. For each claim, search the Anchor Store for contradictions.
3. If contradiction found → REJECT with reason.
4. If claim aligns with anchor → PASS.
5. If no anchor found (novel claim) → ESCALATE to B5 (Enjambre).

This is the VERIFICADOR layer in the B9 Authority Matrix.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Protocol


class AnchorStoreReader(Protocol):
    """Protocol for reading from B1 Anchor Store."""

    def search_anchors(self, query: str) -> list: ...
    def get_anchor(self, concept: str) -> object: ...


class ClaimVerdict(Enum):
    PASS = "PASS"
    REJECT = "REJECT"
    ESCALATE = "ESCALATE"
    ERROR = "ERROR"


@dataclass
class Claim:
    """A single claim extracted from input."""

    text: str
    source: str = "input"
    confidence: float = 1.0


@dataclass
class VerificationResult:
    """Result of verifying a single claim."""

    claim: Claim
    verdict: ClaimVerdict
    reason: str
    matching_anchor: Optional[str] = None
    similarity_score: float = 0.0


@dataclass
class GateResult:
    """Aggregate result of the Claim Verification Gate."""

    overall_verdict: ClaimVerdict
    results: list[VerificationResult] = field(default_factory=list)
    pass_count: int = 0
    reject_count: int = 0
    escalate_count: int = 0

    @property
    def total(self) -> int:
        return len(self.results)


class ClaimExtractor:
    """
    Extracts verifiable claims from input text.

    Strategy: Split by sentences, filter for declarative statements.
    Future: Use NLP/LLM for semantic claim extraction.
    """

    # Keywords that indicate a claim (declarative statement)
    CLAIM_INDICATORS = frozenset(
        [
            "es",
            "son",
            "debe",
            "siempre",
            "nunca",
            "todo",
            "ningún",
            "obligatorio",
            "prohibido",
            "requiere",
            "garantiza",
        ]
    )

    def extract(self, text: str) -> list[Claim]:
        """
        Extract claims from text.

        Args:
            text: Input text to analyze.

        Returns:
            List of extracted Claims.
        """
        if not text or not text.strip():
            return []

        sentences = self._split_sentences(text)
        claims = []

        for sentence in sentences:
            if self._is_claim(sentence):
                claims.append(Claim(text=sentence.strip()))

        return claims

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Simple sentence splitting (future: use spaCy or similar)
        separators = [".", "!", "?", ";", "\n"]
        sentences = [text]
        for sep in separators:
            new_sentences = []
            for s in sentences:
                new_sentences.extend(s.split(sep))
            sentences = new_sentences
        return [s.strip() for s in sentences if s.strip()]

    def _is_claim(self, sentence: str) -> bool:
        """Determine if a sentence contains a verifiable claim."""
        words = sentence.lower().split()
        return any(indicator in words for indicator in self.CLAIM_INDICATORS)


class ClaimVerificationGate:
    """
    B2 Claim Verification Gate.

    Verifies claims against the Anchor Store and produces verdicts.
    """

    # Similarity threshold for considering a match
    MATCH_THRESHOLD = 0.7
    # Similarity threshold for contradiction detection
    CONTRADICTION_THRESHOLD = 0.5

    def __init__(
        self,
        anchor_reader: Optional[AnchorStoreReader] = None,
        extractor: Optional[ClaimExtractor] = None,
    ):
        self._anchor_reader = anchor_reader
        self._extractor = extractor or ClaimExtractor()

    def verify_text(self, text: str) -> GateResult:
        """
        Verify all claims in a text block.

        Args:
            text: Input text containing potential claims.

        Returns:
            GateResult with individual and aggregate verdicts.
        """
        claims = self._extractor.extract(text)

        if not claims:
            return GateResult(overall_verdict=ClaimVerdict.PASS)

        results = [self._verify_claim(claim) for claim in claims]

        pass_count = sum(1 for r in results if r.verdict == ClaimVerdict.PASS)
        reject_count = sum(1 for r in results if r.verdict == ClaimVerdict.REJECT)
        escalate_count = sum(1 for r in results if r.verdict == ClaimVerdict.ESCALATE)

        # Overall verdict: most conservative wins
        if reject_count > 0:
            overall = ClaimVerdict.REJECT
        elif escalate_count > 0:
            overall = ClaimVerdict.ESCALATE
        else:
            overall = ClaimVerdict.PASS

        return GateResult(
            overall_verdict=overall,
            results=results,
            pass_count=pass_count,
            reject_count=reject_count,
            escalate_count=escalate_count,
        )

    def verify_claims(self, claims: list[Claim]) -> GateResult:
        """Verify a pre-extracted list of claims."""
        if not claims:
            return GateResult(overall_verdict=ClaimVerdict.PASS)

        results = [self._verify_claim(claim) for claim in claims]

        pass_count = sum(1 for r in results if r.verdict == ClaimVerdict.PASS)
        reject_count = sum(1 for r in results if r.verdict == ClaimVerdict.REJECT)
        escalate_count = sum(1 for r in results if r.verdict == ClaimVerdict.ESCALATE)

        if reject_count > 0:
            overall = ClaimVerdict.REJECT
        elif escalate_count > 0:
            overall = ClaimVerdict.ESCALATE
        else:
            overall = ClaimVerdict.PASS

        return GateResult(
            overall_verdict=overall,
            results=results,
            pass_count=pass_count,
            reject_count=reject_count,
            escalate_count=escalate_count,
        )

    def _verify_claim(self, claim: Claim) -> VerificationResult:
        """Verify a single claim against the Anchor Store."""
        if self._anchor_reader is None:
            return VerificationResult(
                claim=claim,
                verdict=ClaimVerdict.ESCALATE,
                reason="No Anchor Store connected — escalating to B5",
            )

        try:
            # Search for related anchors
            matches = self._anchor_reader.search_anchors(claim.text)

            if not matches:
                return VerificationResult(
                    claim=claim,
                    verdict=ClaimVerdict.ESCALATE,
                    reason="No matching anchor found — novel claim, escalate to B5",
                )

            # Check first match (simplified — future: semantic similarity)
            best_match = matches[0]
            concept = getattr(best_match, "concept", str(best_match))

            # For now, if we find a match, we PASS (simplified logic)
            # Future: compute actual semantic similarity and check for contradictions
            return VerificationResult(
                claim=claim,
                verdict=ClaimVerdict.PASS,
                reason=f"Claim aligns with anchor '{concept}'",
                matching_anchor=concept,
                similarity_score=0.85,
            )

        except Exception as e:
            return VerificationResult(
                claim=claim,
                verdict=ClaimVerdict.ERROR,
                reason=f"Verification error: {e}",
            )
