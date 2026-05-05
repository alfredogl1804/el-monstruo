"""
Sprint 87.2 Bloque 1 — Tests para kernel/e2e/deploy/real_deploy.py

Coverage:
1. Render HTML produce 4 archivos esperados
2. Tracking script se inyecta en index.html con run_id correcto
3. Validación PII bloquea SSN, credit cards, API keys
4. Slug normalization funciona
5. Heuristic preview se usa cuando no hay GITHUB_TOKEN
6. Heuristic preview tiene fallback_reason explícito
7. Render maneja state vacío (fallback a frase_input)
8. RealDeployResult Pydantic valida estructura
9. Brand DNA en errores
"""
from __future__ import annotations

import asyncio
import os

import pytest

from kernel.e2e.deploy.real_deploy import (
    DeployTarget,
    E2EDeployValidationFailed,
    RealDeployResult,
    _slugify,
    _validate_no_pii,
    render_landing_html,
    run_real_deploy,
)


# ── 1. Render produce 4 archivos ─────────────────────────────────────────────


def test_render_landing_produces_expected_files():
    state = {
        "frase_input": "Pintura al óleo artesanal",
        "creativo": {
            "output_payload": {
                "nombre": "Forja Pinturas",
                "tagline": "Óleo hecho a mano en Mérida",
                "body_copy": "Cada cuadro nace de pigmentos puros y horas de paciencia.",
                "cta_text": "Pedí tu primer cuadro",
            }
        },
    }
    files = render_landing_html(
        state=state, run_id="e2e_test_001", ingest_url="https://api.test/ingest"
    )
    assert set(files.keys()) == {"index.html", "style.css", "monstruo-tracking.js", ".nojekyll"}
    assert "Forja Pinturas" in files["index.html"]
    assert "Pedí tu primer cuadro" in files["index.html"]


# ── 2. Tracking script se inyecta correctamente ──────────────────────────────


def test_render_injects_tracking_with_run_id():
    state = {"frase_input": "test"}
    files = render_landing_html(
        state=state, run_id="e2e_999_abc", ingest_url="https://x/ingest"
    )
    assert 'window.__MONSTRUO_RUN_ID__ = "e2e_999_abc"' in files["index.html"]
    assert 'window.__MONSTRUO_INGEST_URL__ = "https://x/ingest"' in files["index.html"]
    assert 'src="/monstruo-tracking.js"' in files["index.html"]
    # El script independiente también está presente y es no-trivial
    assert len(files["monstruo-tracking.js"]) > 1000


# ── 3. Validación PII rechaza patrones obvios ────────────────────────────────


def test_validate_no_pii_blocks_ssn():
    with pytest.raises(E2EDeployValidationFailed, match="PII pattern detectado"):
        _validate_no_pii("<html>SSN: 123-45-6789</html>")


def test_validate_no_pii_blocks_visa():
    with pytest.raises(E2EDeployValidationFailed):
        _validate_no_pii("<html>Card: 4111-1111-1111-1111</html>")


def test_validate_no_pii_blocks_api_key():
    with pytest.raises(E2EDeployValidationFailed):
        _validate_no_pii("<html>key: sk-proj-abc123def456ghi789jkl0_xy</html>")


def test_validate_no_pii_passes_clean_html():
    # No debe lanzar
    _validate_no_pii("<html><body>Producto premium hecho a mano.</body></html>")


# ── 4. Slug normalization ────────────────────────────────────────────────────


def test_slugify_handles_accents_and_spaces():
    # \w en Python incluye unicode word chars (tildes), eso está bien para repos GitHub.
    result = _slugify("Forja Pinturas Mérida")
    assert result.startswith("forja-pinturas")
    assert _slugify("Hola Mundo!") == "hola-mundo"
    assert _slugify("") == "monstruo-site"


def test_slugify_truncates_long_names():
    long_name = "esta es una frase muy larga que debe ser cortada en algun punto razonable"
    result = _slugify(long_name, max_length=20)
    assert len(result) <= 20


# ── 5. Heuristic preview cuando no hay GITHUB_TOKEN ──────────────────────────


def test_run_real_deploy_falls_back_when_no_token(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    state = {"frase_input": "test landing", "creativo": {"output_payload": {}}}

    result = asyncio.run(run_real_deploy(state=state, run_id="e2e_test_pre"))

    assert isinstance(result, RealDeployResult)
    assert result.deploy_target == DeployTarget.HEURISTIC_PREVIEW
    assert result.fallback_reason == "no_github_token"
    assert "preview.el-monstruo.dev" in result.deploy_url
    assert result.real_deploy_pending is True


# ── 6. Explicit preview target ───────────────────────────────────────────────


def test_run_real_deploy_explicit_preview_target(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "fake_token")
    state = {"frase_input": "test"}

    result = asyncio.run(
        run_real_deploy(
            state=state, run_id="e2e_explicit_pre", target=DeployTarget.HEURISTIC_PREVIEW
        )
    )
    assert result.deploy_target == DeployTarget.HEURISTIC_PREVIEW
    assert result.fallback_reason == "explicit_preview_target"


# ── 7. Render maneja state vacío ─────────────────────────────────────────────


def test_render_with_empty_state_uses_frase_input():
    state = {"frase_input": "Hacé una landing"}
    files = render_landing_html(state=state, run_id="e2e_x", ingest_url="https://i")
    # Debe haber contenido aunque no haya creativo/ventas
    assert len(files["index.html"]) > 500
    assert "El Monstruo" in files["index.html"]


# ── 8. RealDeployResult Pydantic ─────────────────────────────────────────────


def test_real_deploy_result_pydantic_strict():
    r = RealDeployResult(
        deploy_url="https://x.io",
        deploy_target=DeployTarget.GITHUB_PAGES,
        deploy_provider="github_pages",
        deploy_at="2026-05-05T18:00:00+00:00",
    )
    assert r.deploy_target == DeployTarget.GITHUB_PAGES
    # extra='forbid' debe rechazar campos extra
    with pytest.raises(Exception):
        RealDeployResult(
            deploy_url="x",
            deploy_target=DeployTarget.GITHUB_PAGES,
            deploy_provider="x",
            deploy_at="2026",
            campo_extra="no_permitido",
        )


# ── 9. Brand DNA en errores ──────────────────────────────────────────────────


def test_brand_dna_error_codes():
    from kernel.e2e.deploy.real_deploy import (
        E2EDeployError,
        E2EDeployProviderFailed,
        E2EDeployRenderFailed,
        E2EDeployValidationFailed,
    )

    assert E2EDeployError.code == "e2e_deploy_failed"
    assert E2EDeployValidationFailed.code == "e2e_deploy_validation_failed"
    assert E2EDeployRenderFailed.code == "e2e_deploy_render_failed"
    assert E2EDeployProviderFailed.code == "e2e_deploy_provider_failed"
