# kernel/transversales/seo/__init__.py
"""
Capa Transversal: SEO y Descubrimiento (Obj #9).

Genera recomendaciones estructurales de schema.org markup, hreflang, geo
targeting, robots/indexing, URL patterns, canonical strategy, y required
disclosures regulatorias per vertical.

IMPORTANTE — separacion estructura vs copy:
    Esta Capa devuelve DATA ESTRUCTURAL (schema types, geo targets,
    URL patterns, slots de meta-tag). NO devuelve texto final de meta-titles
    ni descriptions ni body copy. El copy final lo llena el plugin
    `brand-voice` o se revisa por humano.

IMPORTANTE — magna validation:
    Keywords que convierten en mayo 2026, ranking factors vigentes de Google,
    competidores AI Overview/SGE coverage — todo eso esta fuera del cutoff
    de Cowork. Cualquier claim de keyword research o algorithm guidance
    se etiqueta `[NEEDS_PERPLEXITY_VALIDATION]`.

Origen: AGENTS.md Regla Dura #2 (Capa 2 de las 7 Transversales),
DSC-G-002.
"""
from __future__ import annotations

from typing import Any

from kernel.transversales.base import (
    BusinessModelArchetype,
    GeoRegion,
    RestrictedVerticalError,
    TransversalContext,
    TransversalLayer,
    TransversalRecommendation,
    TransversalRecommendations,
    VerticalId,
)
from kernel.transversales.seo._canonical_constraints import (
    SEO_CANONICAL_PER_VERTICAL,
    is_commercial,
    require_commercial,
)


class SeoLayer(TransversalLayer):
    """Implementacion de la Capa SEO."""

    layer_name = "seo"

    def diagnose(self, ctx: TransversalContext) -> dict[str, Any]:
        require_commercial(ctx.vertical)
        canonical = SEO_CANONICAL_PER_VERTICAL.get(ctx.vertical, {})
        return {
            "vertical": ctx.vertical.value,
            "archetype": ctx.archetype.value,
            "is_commercial": True,
            "is_indexable": canonical.get("robots_indexable", False),
            "indexable_blocker": canonical.get(
                "robots_indexable_blocker_reason"
            ),
            "schema_types_count": len(canonical.get("schema_org_types", [])),
            "hreflang_count": len(canonical.get("hreflang", [])),
            "has_canonical_constraints": bool(canonical),
            "deep_diagnostics_status": "pending_implementation",
        }

    def recommend(self, ctx: TransversalContext) -> TransversalRecommendations:
        require_commercial(ctx.vertical)
        canonical = SEO_CANONICAL_PER_VERTICAL.get(ctx.vertical, {})
        recs: list[TransversalRecommendation] = []
        validation_tags: list[str] = []

        is_indexable = canonical.get("robots_indexable", True)
        recs.append(
            TransversalRecommendation(
                layer_name="seo",
                rule_id="seo.robots.indexable",
                severity="must",
                value={
                    "indexable": is_indexable,
                    "blocker_reason": canonical.get(
                        "robots_indexable_blocker_reason"
                    ),
                    "robots_meta": "index,follow" if is_indexable else "noindex,nofollow",
                },
                rationale=(
                    "Indexability gate. Bloqueado si DSC regulatorio "
                    "lo exige hasta resolver constraint."
                ),
                source_dsc=canonical.get("source_dscs", []),
            )
        )

        schema_types = canonical.get("schema_org_types", [])
        if schema_types:
            recs.append(
                TransversalRecommendation(
                    layer_name="seo",
                    rule_id="seo.schema_org.types",
                    severity="must",
                    value={
                        "types": schema_types,
                        "required_fields": (
                            canonical.get("required_schema_fields_event")
                            or canonical.get("required_schema_fields_application")
                            or []
                        ),
                        "json_ld_injection_required": True,
                    },
                    rationale=(
                        f"Schema.org types canonicos para {ctx.vertical.value}. "
                        "Vocabulary estable, no requiere validacion magna."
                    ),
                    source_dsc=canonical.get("source_dscs", []),
                )
            )

        geo_target = canonical.get("geo_target")
        hreflang = canonical.get("hreflang", [])
        if geo_target or hreflang:
            recs.append(
                TransversalRecommendation(
                    layer_name="seo",
                    rule_id="seo.geo.targeting",
                    severity="must",
                    value={
                        "geo_target": geo_target,
                        "geo_target_states": canonical.get(
                            "geo_target_states", []
                        ),
                        "hreflang_locales": hreflang,
                        "expansion_phase_2_locales": canonical.get(
                            "hreflang_expansion_phase_2", []
                        ),
                    },
                    rationale=(
                        "Geo targeting derivado de DSC del vertical. "
                        "Expansion fuera de phase 1 requiere decision explicita."
                    ),
                    source_dsc=canonical.get("source_dscs", []),
                )
            )

        url_pattern = canonical.get("url_pattern_template")
        if url_pattern:
            recs.append(
                TransversalRecommendation(
                    layer_name="seo",
                    rule_id="seo.url_structure",
                    severity="must",
                    value={
                        "url_pattern_template": url_pattern,
                        "canonical_strategy": canonical.get(
                            "canonical_url_strategy", "self_canonical"
                        ),
                        "ssr_required": canonical.get(
                            "ssr_required_for_event_pages", False
                        ),
                    },
                    rationale=(
                        "URL pattern y canonical strategy estables. "
                        "SSR requerido si el archetype tiene paginas con "
                        "datos dinamicos (ej. eventos LikeTickets)."
                    ),
                    source_dsc=canonical.get("source_dscs", []),
                )
            )

        disclosures = canonical.get("required_disclosures", [])
        if disclosures:
            recs.append(
                TransversalRecommendation(
                    layer_name="seo",
                    rule_id="seo.disclosures.required",
                    severity="must",
                    value={
                        "disclosures": disclosures,
                        "placement": "above_fold_or_footer_per_page",
                    },
                    rationale=(
                        "Disclosures regulatorias derivadas de DSCs del "
                        "vertical. Bloqueante en paginas indexables."
                    ),
                    source_dsc=canonical.get("source_dscs", []),
                )
            )

        recs.append(
            TransversalRecommendation(
                layer_name="seo",
                rule_id="seo.keywords.research_pending",
                severity="should",
                value={
                    "differentiator_keywords": canonical.get(
                        "differentiator_keywords", []
                    ),
                    "research_pending": True,
                },
                rationale=(
                    "Keywords convertentes en mayo 2026 estan fuera del "
                    "cutoff de Cowork. Differentiator keywords listados son "
                    "estables (de DSCs canonicos), pero keyword research "
                    "completo requiere validacion via Perplexity."
                ),
                needs_validation_tags=[
                    f"[NEEDS_PERPLEXITY_VALIDATION] keyword_research_2026:"
                    f"{ctx.vertical.value}",
                    f"[NEEDS_PERPLEXITY_VALIDATION] competitor_seo_2026:"
                    f"{ctx.archetype.value}",
                    "[NEEDS_PERPLEXITY_VALIDATION] google_ranking_factors_2026",
                ],
                source_dsc=canonical.get("source_dscs", []),
            )
        )
        validation_tags.extend([
            f"[NEEDS_PERPLEXITY_VALIDATION] keyword_research_2026:"
            f"{ctx.vertical.value}",
            f"[NEEDS_PERPLEXITY_VALIDATION] competitor_seo_2026:"
            f"{ctx.archetype.value}",
            "[NEEDS_PERPLEXITY_VALIDATION] google_ranking_factors_2026",
        ])

        return TransversalRecommendations(
            layer_name="seo",
            vertical=ctx.vertical,
            archetype=ctx.archetype,
            recommendations=recs,
            diagnostics=self.diagnose(ctx),
            aggregated_validation_tags=validation_tags,
        )

    def implement(
        self, recommendations: TransversalRecommendations
    ) -> dict[str, Any]:
        raise NotImplementedError(
            "SeoLayer.implement pendiente Sprint TRANSVERSAL-001. "
            "Requiere render integration (meta tags, JSON-LD injection, "
            "sitemap generation, robots.txt). "
            "Tag: [NEEDS_PERPLEXITY_VALIDATION] render_pipeline_2026"
        )

    def monitor(self, ctx: TransversalContext) -> dict[str, Any]:
        raise NotImplementedError(
            "SeoLayer.monitor pendiente Sprint TRANSVERSAL-001. "
            "Requiere Search Console API + crawl error monitoring. "
            "Tag: [NEEDS_PERPLEXITY_VALIDATION] search_console_api_2026"
        )


__all__ = ["SeoLayer"]
