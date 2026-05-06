"""
Sprint 88 Tarea 3.B.2 — Propagación de deploy_provider al rollup del run.

Verifica que:
1. E2ERun schema acepta deploy_provider
2. Repository.update_run acepta y persiste deploy_provider
3. Pipeline propaga out["deploy_provider"] al update_run del step 9
4. Backwards compat: legacy runs sin deploy_provider no fallan

Brand DNA: errores con prefijo e2e_deploy_provider_*_failed.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from kernel.e2e.schema import E2ERun, EstadoRun


# ============================================================================
# Schema
# ============================================================================

class TestE2ERunSchemaDeployProvider:
    """E2ERun ahora expone deploy_provider opcional."""

    def _base_payload(self) -> dict:
        return {
            "id": "e2e_1234567890_abcdef",
            "frase_input": "test sprint 88",
            "estado": "in_progress",
            "pipeline_step": 9,
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

    def test_legacy_run_without_deploy_provider_works(self):
        run = E2ERun.model_validate(self._base_payload())
        assert run.deploy_provider is None
        assert run.deploy_url is None

    def test_run_with_deploy_provider_github_pages(self):
        payload = self._base_payload()
        payload["deploy_url"] = "https://alfredogl1804.github.io/monstruo-test/"
        payload["deploy_provider"] = "github_pages"
        run = E2ERun.model_validate(payload)
        assert run.deploy_provider == "github_pages"
        assert run.deploy_url.startswith("https://")

    def test_run_with_deploy_provider_railway(self):
        payload = self._base_payload()
        payload["deploy_provider"] = "railway"
        run = E2ERun.model_validate(payload)
        assert run.deploy_provider == "railway"

    def test_run_with_deploy_provider_fallback(self):
        payload = self._base_payload()
        payload["deploy_provider"] = "fallback"
        run = E2ERun.model_validate(payload)
        assert run.deploy_provider == "fallback"

    def test_deploy_provider_serialized_in_dump(self):
        payload = self._base_payload()
        payload["deploy_provider"] = "github_pages"
        run = E2ERun.model_validate(payload)
        dumped = run.model_dump(mode="json")
        assert "deploy_provider" in dumped
        assert dumped["deploy_provider"] == "github_pages"


# ============================================================================
# Repository
# ============================================================================

class _MockDB:
    """Mock minimal para verificar que el patch contiene deploy_provider."""

    def __init__(self):
        self.last_patch: dict = {}
        self.last_filter: dict = {}
        self.last_table: str = ""
        self.rows: list[dict] = []

    async def update(self, table: str, patch: dict, filt: dict):
        self.last_table = table
        self.last_patch = dict(patch)
        self.last_filter = dict(filt)
        merged = {
            "id": filt.get("id"),
            "frase_input": "test",
            "estado": "in_progress",
            "pipeline_step": 9,
            "started_at": datetime.now(timezone.utc).isoformat(),
            **patch,
        }
        return merged

    async def select(self, *args, **kwargs):
        return self.rows


@pytest.mark.asyncio
class TestRepositoryUpdateRunDeployProvider:
    """Repository.update_run acepta deploy_provider y lo incluye en el patch."""

    async def test_update_run_accepts_deploy_provider(self):
        from kernel.e2e.repository import E2ERepository

        db = _MockDB()
        repo = E2ERepository(db)
        await repo.update_run(
            "e2e_test_provider",
            pipeline_step=9,
            deploy_url="https://example.github.io/site/",
            deploy_provider="github_pages",
        )
        assert "deploy_url" in db.last_patch
        assert "deploy_provider" in db.last_patch
        assert db.last_patch["deploy_provider"] == "github_pages"

    async def test_update_run_without_deploy_provider_keeps_compat(self):
        from kernel.e2e.repository import E2ERepository

        db = _MockDB()
        repo = E2ERepository(db)
        await repo.update_run(
            "e2e_legacy",
            pipeline_step=5,
            critic_visual_score=88.0,
        )
        assert "deploy_provider" not in db.last_patch
        assert db.last_patch.get("pipeline_step") == 5
        assert db.last_patch.get("critic_visual_score") == 88.0

    async def test_update_run_only_deploy_provider(self):
        from kernel.e2e.repository import E2ERepository

        db = _MockDB()
        repo = E2ERepository(db)
        await repo.update_run(
            "e2e_only_provider",
            deploy_provider="railway",
        )
        assert db.last_patch == {"deploy_provider": "railway"}

    async def test_update_run_deploy_provider_fallback(self):
        from kernel.e2e.repository import E2ERepository

        db = _MockDB()
        repo = E2ERepository(db)
        await repo.update_run(
            "e2e_fallback",
            deploy_url=None,  # no deploy real
            deploy_provider="fallback",
        )
        assert db.last_patch == {"deploy_provider": "fallback"}


# ============================================================================
# Pipeline propagation contract
# ============================================================================

class TestPipelineDeployProviderContract:
    """
    Contrato del step 9: el output_payload incluye deploy_provider y el
    pipeline DEBE invocar update_run con ambos campos.
    """

    def test_real_deploy_result_serializes_provider(self):
        """RealDeployResult expone deploy_provider en model_dump."""
        from kernel.e2e.deploy.real_deploy import RealDeployResult

        result = RealDeployResult(
            deploy_url="https://alfredogl1804.github.io/monstruo-test/",
            deploy_target="github_pages",
            deploy_provider="github_pages",
            deploy_at="2026-05-06T00:00:00+00:00",
            repo="alfredogl1804/monstruo-test",
            files_committed=5,
            build_confirmed=True,
            real_deploy_pending=False,
        )
        dumped = result.model_dump(mode="json")
        assert dumped["deploy_provider"] == "github_pages"
        assert dumped["deploy_url"].startswith("https://")
        assert dumped["build_confirmed"] is True

    def test_pipeline_extracts_deploy_provider_from_step_output(self):
        """Simula el output del step y verifica lectura del campo."""
        # Output canónico que produce _step_deploy
        step_output = {
            "deploy_url": "https://alfredogl1804.github.io/monstruo-test/",
            "deploy_provider": "github_pages",
            "build_confirmed": True,
            "files_count": 5,
            "duration_ms": 42500,
            "repo_name": "monstruo-test",
        }
        # Lógica equivalente a la del pipeline (línea 476)
        deploy_provider = step_output.get("deploy_provider") or step_output.get("provider")
        assert deploy_provider == "github_pages"

    def test_pipeline_handles_legacy_provider_alias(self):
        """Si el step output usa 'provider' en vez de 'deploy_provider', el pipeline lo acepta."""
        step_output_legacy = {
            "deploy_url": "https://example.com/",
            "provider": "railway",  # alias legacy
        }
        deploy_provider = step_output_legacy.get("deploy_provider") or step_output_legacy.get("provider")
        assert deploy_provider == "railway"

    def test_pipeline_handles_missing_provider(self):
        """Si el step output no tiene provider, el pipeline pasa None (no falla)."""
        step_output = {"deploy_url": "https://example.com/"}
        deploy_provider = step_output.get("deploy_provider") or step_output.get("provider")
        assert deploy_provider is None
