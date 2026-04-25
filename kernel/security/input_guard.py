"""
El Monstruo — Input Guard (Sprint 28)
======================================
Defensive middleware that sanitizes user input before it reaches the LLM.
Uses pattern-based detection + optional llm-guard integration.

Sprint 28: Pattern-based detection (zero dependencies).
Sprint 29+: Integrate llm-guard if Sabios recommend it after benchmark.
"""
import logging
import re
from typing import Optional

logger = logging.getLogger("monstruo.security.input_guard")

# Known prompt injection patterns (updated 25 abril 2026)
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"you\s+are\s+now\s+",
    r"system\s*:\s*",
    r"\[INST\]",
    r"<\|im_start\|>",
    r"\{\{.*\}\}",  # Template injection
    r"ADMIN\s*MODE",
    r"jailbreak",
    r"DAN\s+mode",
    r"pretend\s+you\s+are",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


class InputGuardResult:
    """Result of input guard check."""
    def __init__(self, safe: bool, risk_score: float, matched_patterns: list[str], sanitized: Optional[str] = None):
        self.safe = safe
        self.risk_score = risk_score
        self.matched_patterns = matched_patterns
        self.sanitized = sanitized


def check_input(text: str, threshold: float = 0.5) -> InputGuardResult:
    """Check user input for prompt injection patterns.

    Args:
        text: Raw user input
        threshold: Risk score threshold (0-1). Above this = unsafe.

    Returns:
        InputGuardResult with safety assessment
    """
    if not text or not text.strip():
        return InputGuardResult(safe=True, risk_score=0.0, matched_patterns=[])

    matched = []
    for i, pattern in enumerate(COMPILED_PATTERNS):
        if pattern.search(text):
            matched.append(INJECTION_PATTERNS[i])

    # Risk score: 0 = safe, 1 = definitely injection
    risk_score = min(len(matched) / 3.0, 1.0)  # 3+ patterns = max risk

    safe = risk_score < threshold

    if not safe:
        logger.warning(
            "input_guard_triggered",
            extra={"risk_score": risk_score, "patterns": len(matched), "input_length": len(text)}
        )

    return InputGuardResult(
        safe=safe,
        risk_score=risk_score,
        matched_patterns=matched,
        sanitized=text if safe else None
    )
