"""
Sprint 87.2 Bloque 3 — Tests para kernel/e2e/critic_visual/gemini_vision.py

Coverage:
1. Sin screenshot → fallback heurístico inmediato
2. Sin GEMINI_API_KEY → fallback heurístico
3. Screenshot inexistente → fallback con razón
4. Screenshot demasiado grande → fallback con razón
5. Pydantic strict
6. Brand DNA error codes
7. Heuristic fallback siempre devuelve score 60 + veredicto rework
8. Mock Gemini call exitoso → score real parsing
9. Mock Gemini call falla → fallback con razón
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from kernel.e2e.critic_visual.gemini_vision import (
    CriticVisualReport,
    CriticVisualSubScores,
    GeminiVisionAPIFailed,
    GeminiVisionFailed,
    GeminiVisionImageTooLarge,
    GeminiVisionMissingKey,
    _heuristic_fallback,
    _read_image_bytes,
    evaluate_landing,
)


# ── 1. Sin screenshot → fallback ────────────────────────────────────────────


def test_no_screenshot_uses_fallback():
    result = asyncio.run(
        evaluate_landing(
            deploy_url="https://x.io/run1",
            screenshot_path=None,
            brief_ctx={"frase_input": "test"},
            modelo_elegido="gemini-3-1-pro-preview",
        )
    )
    assert result.source == "heuristic_fallback"
    assert result.score == 60
    assert result.fallback_reason == "screenshot_no_disponible"


# ── 2. Sin GEMINI_API_KEY → fallback ────────────────────────────────────────


def test_no_api_key_uses_fallback(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    fake_png = tmp_path / "fake.png"
    fake_png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"X" * 100)

    result = asyncio.run(
        evaluate_landing(
            deploy_url="https://x.io",
            screenshot_path=str(fake_png),
            brief_ctx={"nombre": "X"},
            modelo_elegido="gemini-3-1-pro-preview",
        )
    )
    assert result.source == "heuristic_fallback"
    assert result.fallback_reason == "critic_visual_evaluate_missing_key"


# ── 3. Screenshot inexistente → fallback ────────────────────────────────────


def test_missing_screenshot_file_uses_fallback(monkeypatch):
    result = asyncio.run(
        evaluate_landing(
            deploy_url="https://x.io",
            screenshot_path="/tmp/inexistente_xyz_999.png",
            brief_ctx={},
            modelo_elegido="m1",
        )
    )
    assert result.source == "heuristic_fallback"
    assert "no existe" in (result.fallback_reason or "") or "critic_visual" in (
        result.fallback_reason or ""
    )


# ── 4. Screenshot demasiado grande → error→ fallback ────────────────────────


def test_image_too_large(tmp_path):
    huge = tmp_path / "huge.png"
    huge.write_bytes(b"X" * (6 * 1024 * 1024))
    with pytest.raises(GeminiVisionImageTooLarge):
        _read_image_bytes(str(huge))


# ── 5. Pydantic strict ──────────────────────────────────────────────────────


def test_critic_visual_report_strict():
    r = CriticVisualReport(
        score=85,
        sub_scores=CriticVisualSubScores(
            estetica=85, cta_claridad=80, jerarquia_visual=90, profesionalismo=85
        ),
        razones_aprobacion=["clean"],
        razones_mejora=[],
        veredicto="comercializable",
        deploy_url="https://x.io",
        modelo_consultado="gemini-2.5-pro",
        source="gemini_vision",
        evaluated_at="2026-05-05T18:00:00+00:00",
        duration_ms=1234,
    )
    assert r.score == 85
    with pytest.raises(Exception):
        CriticVisualReport(
            score=85,
            sub_scores=CriticVisualSubScores(
                estetica=85, cta_claridad=80, jerarquia_visual=90, profesionalismo=85
            ),
            veredicto="x",
            deploy_url="x",
            modelo_consultado="x",
            source="x",
            evaluated_at="x",
            duration_ms=0,
            extra="nope",
        )


# ── 6. Brand DNA error codes ────────────────────────────────────────────────


def test_brand_dna_error_codes():
    assert GeminiVisionFailed.code == "critic_visual_evaluate_failed"
    assert GeminiVisionMissingKey.code == "critic_visual_evaluate_missing_key"
    assert GeminiVisionImageTooLarge.code == "critic_visual_evaluate_image_too_large"
    assert GeminiVisionAPIFailed.code == "critic_visual_evaluate_api_failed"


# ── 7. Heuristic fallback determinístico ─────────────────────────────────────


def test_heuristic_fallback_shape():
    import time

    started = time.perf_counter()
    r = _heuristic_fallback(
        deploy_url="https://x.io",
        modelo="m1",
        reason="test_reason",
        started=started,
    )
    assert r.score == 60
    assert r.veredicto == "rework"
    assert r.source == "heuristic_fallback"
    assert r.fallback_reason == "test_reason"
    assert r.sub_scores.estetica == 60


# ── 8. Mock Gemini call exitoso ──────────────────────────────────────────────


def test_mock_gemini_success(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake")
    fake_png = tmp_path / "fake.png"
    fake_png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"X" * 100)

    fake_response = {
        "score": 88,
        "sub_scores": {
            "estetica": 90,
            "cta_claridad": 85,
            "jerarquia_visual": 88,
            "profesionalismo": 88,
        },
        "razones_aprobacion": ["jerarquía clara", "CTA visible"],
        "razones_mejora": ["agregar testimoniales"],
        "veredicto": "comercializable",
        "_model_used": "gemini-2.5-pro",
    }

    async def _fake_call(*args, **kwargs):
        return fake_response

    with patch(
        "kernel.e2e.critic_visual.gemini_vision._call_gemini_vision",
        new=_fake_call,
    ):
        result = asyncio.run(
            evaluate_landing(
                deploy_url="https://x.io/r",
                screenshot_path=str(fake_png),
                brief_ctx={"nombre": "X"},
                modelo_elegido="gemini-3-1-pro-preview",
            )
        )
    assert result.source == "gemini_vision"
    assert result.score == 88
    assert result.veredicto == "comercializable"
    assert result.modelo_consultado == "gemini-2.5-pro"


# ── 9. Mock Gemini call falla → fallback ────────────────────────────────────


def test_mock_gemini_failure_falls_back(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake")
    fake_png = tmp_path / "fake.png"
    fake_png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"X" * 100)

    fake = AsyncMock(
        side_effect=GeminiVisionAPIFailed("critic_visual_evaluate_api_failed: fake")
    )
    with patch(
        "kernel.e2e.critic_visual.gemini_vision._call_gemini_vision", new=fake
    ):
        result = asyncio.run(
            evaluate_landing(
                deploy_url="https://x.io",
                screenshot_path=str(fake_png),
                brief_ctx={},
                modelo_elegido="m1",
            )
        )
    assert result.source == "heuristic_fallback"
    assert result.fallback_reason == "critic_visual_evaluate_api_failed"
