"""Capa Transversal: Tendencias y Adaptacion (Obj #9)."""

from __future__ import annotations

from typing import Any

from kernel.transversales.base import (
    RestrictedVerticalError,
    TransversalContext,
    TransversalLayer,
    TransversalRecommendation,
    TransversalRecommendations,
)
from kernel.transversales.tendencias._canonical_constraints import (
    MONITORING_CADENCES,
    SUPPORTED_DATA_SOURCES,
    TENDENCIAS_CANONICAL_PER_VERTICAL,
    is_commercial,
    require_commercial,
)


class TendenciasLayer(TransversalLayer):
    layer_name = "tendencias"

    def diagnose(self, ctx: TransversalContext) -> dict[str, Any]:
        require_commercial(ctx.vertical)
        canonical = TENDENCIAS_CANONICAL_PER_VERTICAL.get(ctx.vertical, {})
        return {
            "vertical": ctx.vertical.value,
            "archetype": ctx.archetype.value,
            "is_commercial": True,
            "data_sources_count": len(canonical.get("data_sources", [])),
            "monitoring_cadence": canonical.get("monitoring_cadence"),
            "signal_types_count": len(canonical.get("signal_types_priorizados", [])),
            "deep_diagnostics_status": "pending_implementation",
        }

    def recommend(self, ctx: TransversalContext) -> TransversalRecommendations:
        require_commercial(ctx.vertical)
        canonical = TENDENCIAS_CANONICAL_PER_VERTICAL.get(ctx.vertical, {})
        recs: list[TransversalRecommendation] = []
        validation_tags: list[str] = []

        data_sources = canonical.get("data_sources", [])
        if data_sources:
            recs.append(
                TransversalRecommendation(
                    layer_name="tendencias",
                    rule_id="tendencias.data_sources",
                    severity="must",
                    value={
                        "data_sources": data_sources,
                        "geo_focus": canonical.get("geo_focus"),
                    },
                    rationale=(
                        "Data sources canonicas per archetype + vertical. "
                        "Adicion fuera de SUPPORTED_DATA_SOURCES requiere DSC."
                    ),
                    source_dsc=canonical.get("source_dscs", []),
                )
            )

        cadence = canonical.get("monitoring_cadence")
        critical_cadence = canonical.get("monitoring_cadence_critical_signals")
        if cadence:
            recs.append(
                TransversalRecommendation(
                    layer_name="tendencias",
                    rule_id="tendencias.monitoring_cadence",
                    severity="must",
                    value={"cadence": cadence, "cadence_critical_signals": critical_cadence},
                    rationale="Cadence derivada del archetype.",
                    source_dsc=canonical.get("source_dscs", []),
                )
            )

        signals = canonical.get("signal_types_priorizados", [])
        if signals:
            recs.append(
                TransversalRecommendation(
                    layer_name="tendencias",
                    rule_id="tendencias.signal_types",
                    severity="should",
                    value={"signal_types_priorizados": signals},
                    rationale="Signal types derivados de DSCs canonicos.",
                    needs_validation_tags=[
                        f"[NEEDS_PERPLEXITY_VALIDATION] trend_signals_active_2026:{ctx.vertical.value}",
                    ],
                    source_dsc=canonical.get("source_dscs", []),
                )
            )
            validation_tags.append(f"[NEEDS_PERPLEXITY_VALIDATION] trend_signals_active_2026:{ctx.vertical.value}")

        validation_tags.append("[NEEDS_PERPLEXITY_VALIDATION] data_source_apis_vigentes_2026")

        return TransversalRecommendations(
            layer_name="tendencias",
            vertical=ctx.vertical,
            archetype=ctx.archetype,
            recommendations=recs,
            diagnostics=self.diagnose(ctx),
            aggregated_validation_tags=validation_tags,
        )

    def implement(self, recommendations: TransversalRecommendations) -> dict[str, Any]:
        """
        Genera el plan canonico de captura de senales de tendencias:
        - mapping data_source -> collector (perplexity_sonar / rss_feed_scraper
          / polygon_api / cron_job_X)
        - schema del row a insertar en trend_signals (tabla creada por
          migration 0013)
        - cadence operativa (real_time / hourly / daily / weekly / monthly)
        - signal_types priorizados

        NO ejecuta llamadas a red. El collector real corre en un script
        operativo bajo HITL cuando los API keys de las data sources esten
        configurados.
        """
        import os

        rules = {r.rule_id: r.value for r in recommendations.recommendations}
        data_sources = rules.get("tendencias.data_sources", {}).get("data_sources", [])
        cadence_rule = rules.get("tendencias.monitoring_cadence", {})
        signal_types = rules.get("tendencias.signal_types", {}).get("signal_types_priorizados", [])

        # Mapeo canonico data_source -> collector. Las claves son
        # SUPPORTED_DATA_SOURCES; los collectors son ejecutores reales que
        # deben implementarse en scripts/_collect_trend_signals_*.py.
        collector_map = {
            "blockchain_analytics": "polygon_api",
            "real_estate_market_reports": "rss_feed_scraper",
            "regulatory_feeds": "rss_feed_scraper",
            "events_calendar": "rss_feed_scraper",
            "sports_leagues_feeds": "rss_feed_scraper",
            "social_trends": "perplexity_sonar",
            "tourism_data": "perplexity_sonar",
            "weather_feeds": "openweather_api",
            "industry_reports_b2b": "perplexity_sonar",
            "tech_news": "rss_feed_scraper",
            "github_trending": "github_api",
            "ai_research_feeds": "rss_feed_scraper",
            "ecommerce_trends": "perplexity_sonar",
            "enterprise_tech_news": "rss_feed_scraper",
            "competitor_pricing_scrape": "playwright_scraper",
            "search_trend_signals": "google_trends_api",
        }

        # Envs canonicos requeridos por collector.
        envs_required_by_collector = {
            "polygon_api": ["POLYGON_API_KEY"],
            "rss_feed_scraper": [],  # publico sin auth
            "perplexity_sonar": ["SONAR_API_KEY"],
            "openweather_api": ["OPENWEATHER_API_KEY"],
            "github_api": ["GITHUB_TOKEN"],
            "playwright_scraper": [],  # requiere chromium, no env
            "google_trends_api": ["GOOGLE_TRENDS_API_KEY"],
        }

        collectors_plan: list[dict[str, Any]] = []
        all_pending_envs: set[str] = set()
        for src in data_sources:
            collector = collector_map.get(src, "perplexity_sonar")
            required_envs = envs_required_by_collector.get(collector, [])
            pending = [e for e in required_envs if not os.environ.get(e)]
            all_pending_envs.update(pending)
            collectors_plan.append(
                {
                    "source": src,
                    "collector": collector,
                    "required_envs": required_envs,
                    "pending_envs": pending,
                    "ready": not pending,
                }
            )

        # Schema canonico del row trend_signals (migration 0013).
        trend_signals_row_template = {
            "vertical": recommendations.vertical.value,
            "source": "{{SOURCE_SLOT}}",
            "signal_type": "{{SIGNAL_TYPE_SLOT}}",
            "score": "{{SCORE_SLOT}}",
            "payload": "{{PAYLOAD_JSONB_SLOT}}",
            "observed_at_unix": "{{OBSERVED_AT_UNIX_SLOT}}",
            "ttl_seconds": "{{TTL_SECONDS_SLOT}}",
            "collector": "{{COLLECTOR_SLOT}}",
        }

        return {
            "vertical": recommendations.vertical.value,
            "collectors_plan": collectors_plan,
            "cadence": cadence_rule.get("cadence"),
            "cadence_critical_signals": cadence_rule.get("cadence_critical_signals"),
            "signal_types_priorizados": signal_types,
            "trend_signals_table": "trend_signals",
            "trend_signals_migration": "0013_trend_signals.sql",
            "trend_signals_row_template": trend_signals_row_template,
            "pending_envs": sorted(all_pending_envs),
            "dry_run": True,
            "dry_run_reason": (
                "Push real (collector execution + table insert) requiere firma de Alfredo via DSC-G-002 (HITL)."
            ),
            "validation_log_anchors": [
                {"claim_type": "data_source_apis_vigentes_2026", "row_id": 29},
                {"claim_type": "alerting_stack_2026", "row_id": 30},
            ],
            "validation_tags_pending": list(recommendations.aggregated_validation_tags),
        }

    def monitor(self, ctx: TransversalContext) -> dict[str, Any]:
        """
        Health-check estructural + signal_count desde trend_signals.

        Sin red. Lee trend_signals si el cliente Supabase esta inyectado
        en kernel.validation (set_default_storage()); de lo contrario
        retorna stub.
        """
        require_commercial(ctx.vertical)
        recommendations = self.recommend(ctx)
        impl_artifacts = self.implement(recommendations)

        warnings: list[str] = []
        blockers: list[str] = []

        # Stub signal_count: si hay storage Supabase inyectado, hace conteo
        # real; sino, retorna placeholder con flag pending_storage.
        signal_count_24h: int | None = None
        signal_count_status = "pending_storage_injection"
        try:
            from kernel.validation import _DEFAULT_STORAGE  # type: ignore

            storage = _DEFAULT_STORAGE
        except ImportError:
            storage = None

        if storage is not None and hasattr(storage, "client"):
            try:
                import time as _time

                cutoff = _time.time() - 86400
                resp = (
                    storage.client.table("trend_signals")
                    .select("id", count="exact")
                    .eq("vertical", ctx.vertical.value)
                    .gte("observed_at_unix", cutoff)
                    .execute()
                )
                signal_count_24h = getattr(resp, "count", None) or len(resp.data or [])
                signal_count_status = "counted"
            except Exception as e:  # pragma: no cover
                signal_count_status = f"storage_error:{type(e).__name__}"

        # Warnings.
        if not impl_artifacts["collectors_plan"]:
            blockers.append("No hay data_sources configuradas para este vertical.")
        not_ready = [c for c in impl_artifacts["collectors_plan"] if not c["ready"]]
        if not_ready:
            warnings.append(
                f"{len(not_ready)} de {len(impl_artifacts['collectors_plan'])} "
                f"collectors no estan ready (faltan envs: "
                f"{', '.join(impl_artifacts['pending_envs'])})."
            )
        if impl_artifacts["validation_tags_pending"]:
            warnings.append(
                f"{len(impl_artifacts['validation_tags_pending'])} tags "
                f"Perplexity pendientes de resolver via DSC-V-001."
            )

        return {
            "vertical": ctx.vertical.value,
            "structural_health": {
                "collectors_count": len(impl_artifacts["collectors_plan"]),
                "collectors_ready_count": (len(impl_artifacts["collectors_plan"]) - len(not_ready)),
                "signal_types_count": len(impl_artifacts["signal_types_priorizados"]),
                "cadence": impl_artifacts["cadence"],
                "dry_run": impl_artifacts["dry_run"],
            },
            "trend_signals_health": {
                "table": "trend_signals",
                "signal_count_24h": signal_count_24h,
                "status": signal_count_status,
            },
            "warnings": warnings,
            "blockers": blockers,
            "validation_log_anchors": impl_artifacts["validation_log_anchors"],
        }


__all__ = ["TendenciasLayer"]
