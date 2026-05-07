# kernel/transversales/seo/__init__.py
"""
Capa Transversal: SEO y Descubrimiento (Obj #9).

Genera recomendaciones estructurales de schema.org markup, hreflang, geo
targeting, robots/indexing, URL patterns, canonical strategy, y required
disclosures regulatorias per vertical. Plus implement() que produce
artefactos ready-to-inject (JSON-LD, meta tags, hreflang links) sin
acoplarse al render pipeline downstream.

IMPORTANTE — separacion estructura vs render:
    implement() retorna STRINGS (JSON-LD block, meta tags HTML) listos
    para que cualquier consumer (renderer, generador landing) inyecte en
    su template. NO escribe HTML directamente. Eso desacopla la Capa de
    cualquier render pipeline especifico.

IMPORTANTE — separacion estructura vs copy:
    Title, description, body copy, disclosure copy quedan como SLOTS
    (`{{TITLE_SLOT}}`, etc.) que brand-voice plugin o humano completa.
    SeoLayer NO produce copy final.

IMPORTANTE — magna validation:
    Keywords convertentes 2026, ranking factors Google, AI Overview/SGE
    estan fuera del cutoff de Cowork. Tags `[NEEDS_PERPLEXITY_VALIDATION]`
    propagados en validation_tags_pending del output.

Origen: AGENTS.md Regla Dura #2 (Capa 2 de las 7), DSC-G-002, DSC-G-014.
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
    """Implementacion de la Capa SEO (con implement+monitor reales)."""

    layer_name = "seo"

    def diagnose(self, ctx: TransversalContext) -> dict[str, Any]:
        require_commercial(ctx.vertical)
        canonical = SEO_CANONICAL_PER_VERTICAL.get(ctx.vertical, {})
        return {
            "vertical": ctx.vertical.value,
            "archetype": ctx.archetype.value,
            "is_commercial": True,
            "is_indexable": canonical.get("robots_indexable", False),
            "indexable_blocker": canonical.get("robots_indexable_blocker_reason"),
            "schema_types_count": len(canonical.get("schema_org_types", [])),
            "hreflang_count": len(canonical.get("hreflang", [])),
            "has_canonical_constraints": bool(canonical),
            "deep_diagnostics_status": "structural_only_search_console_pending",
        }

    def recommend(self, ctx: TransversalContext) -> TransversalRecommendations:
        require_commercial(ctx.vertical)
        canonical = SEO_CANONICAL_PER_VERTICAL.get(ctx.vertical, {})
        recs: list[TransversalRecommendation] = []
        validation_tags: list[str] = []

        is_indexable = canonical.get("robots_indexable", True)
        recs.append(TransversalRecommendation(
            layer_name="seo",
            rule_id="seo.robots.indexable",
            severity="must",
            value={
                "indexable": is_indexable,
                "blocker_reason": canonical.get("robots_indexable_blocker_reason"),
                "robots_meta": "index,follow" if is_indexable else "noindex,nofollow",
            },
            rationale=(
                "Indexability gate. Bloqueado si DSC regulatorio lo exige "
                "hasta resolver constraint."
            ),
            source_dsc=canonical.get("source_dscs", []),
        ))

        schema_types = canonical.get("schema_org_types", [])
        if schema_types:
            recs.append(TransversalRecommendation(
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
            ))

        geo_target = canonical.get("geo_target")
        hreflang = canonical.get("hreflang", [])
        if geo_target or hreflang:
            recs.append(TransversalRecommendation(
                layer_name="seo",
                rule_id="seo.geo.targeting",
                severity="must",
                value={
                    "geo_target": geo_target,
                    "geo_target_states": canonical.get("geo_target_states", []),
                    "hreflang_locales": hreflang,
                    "expansion_phase_2_locales": canonical.get(
                        "hreflang_expansion_phase_2", []),
                },
                rationale=(
                    "Geo targeting derivado de DSC del vertical. "
                    "Expansion fuera de phase 1 requiere decision explicita."
                ),
                source_dsc=canonical.get("source_dscs", []),
            ))

        url_pattern = canonical.get("url_pattern_template")
        if url_pattern:
            recs.append(TransversalRecommendation(
                layer_name="seo",
                rule_id="seo.url_structure",
                severity="must",
                value={
                    "url_pattern_template": url_pattern,
                    "canonical_strategy": canonical.get(
                        "canonical_url_strategy", "self_canonical"),
                    "ssr_required": canonical.get(
                        "ssr_required_for_event_pages", False),
                },
                rationale=(
                    "URL pattern y canonical strategy estables. SSR requerido "
                    "si el archetype tiene paginas con datos dinamicos."
                ),
                source_dsc=canonical.get("source_dscs", []),
            ))

        disclosures = canonical.get("required_disclosures", [])
        if disclosures:
            recs.append(TransversalRecommendation(
                layer_name="seo",
                rule_id="seo.disclosures.required",
                severity="must",
                value={
                    "disclosures": disclosures,
                    "placement": "above_fold_or_footer_per_page",
                },
                rationale=(
                    "Disclosures regulatorias derivadas de DSCs del vertical."
                ),
                source_dsc=canonical.get("source_dscs", []),
            ))

        recs.append(TransversalRecommendation(
            layer_name="seo",
            rule_id="seo.keywords.research_pending",
            severity="should",
            value={
                "differentiator_keywords": canonical.get(
                    "differentiator_keywords", []),
                "research_pending": True,
            },
            rationale=(
                "Keywords convertentes en mayo 2026 estan fuera del cutoff de "
                "Cowork. Differentiator keywords son estables (de DSCs canonicos), "
                "pero keyword research completo requiere Perplexity."
            ),
            needs_validation_tags=[
                f"[NEEDS_PERPLEXITY_VALIDATION] keyword_research_2026:"
                f"{ctx.vertical.value}",
                f"[NEEDS_PERPLEXITY_VALIDATION] competitor_seo_2026:"
                f"{ctx.archetype.value}",
                "[NEEDS_PERPLEXITY_VALIDATION] google_ranking_factors_2026",
            ],
            source_dsc=canonical.get("source_dscs", []),
        ))
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
        """
        Genera artefactos de SEO listos para inyectar en cualquier render
        pipeline: JSON-LD block, meta tags HTML, hreflang links, canonical
        URL strategy, robots meta. NO modifica HTML directamente — retorna
        strings que cualquier consumer puede inyectar.

        Returns dict con keys:
            json_ld_block: str (JSON serializado, schema.org)
            meta_tags_html: list[str] (con {{...}} slots para brand-voice)
            robots_meta: str
            hreflang_links_html: list[str]
            canonical_strategy: str
            disclosures_required: list[str] (slot keys)
            indexable: bool
            indexable_blocker_reason: str | None
            validation_tags_pending: list[str] (propagados)
        """
        import json as _json

        rules = {r.rule_id: r.value for r in recommendations.recommendations}

        # 1. Robots/indexability
        robots_rule = rules.get("seo.robots.indexable", {})
        robots_meta = robots_rule.get("robots_meta", "index,follow")
        is_indexable = robots_rule.get("indexable", True)
        blocker = robots_rule.get("blocker_reason")

        # 2. JSON-LD block (schema.org)
        schema_rule = rules.get("seo.schema_org.types", {})
        schema_types = schema_rule.get("types", [])
        required_fields = schema_rule.get("required_fields", [])
        json_ld_doc: dict[str, Any] = {"@context": "https://schema.org"}
        if len(schema_types) == 1:
            json_ld_doc["@type"] = schema_types[0]
        elif len(schema_types) > 1:
            json_ld_doc["@type"] = schema_types
        for field_path in required_fields:
            self._set_nested_slot(json_ld_doc, field_path)
        json_ld_block = _json.dumps(
            json_ld_doc, ensure_ascii=False, indent=2
        )

        # 3. Meta tags HTML
        meta_tags_html: list[str] = [
            f'<meta name="robots" content="{robots_meta}">',
        ]
        geo_rule = rules.get("seo.geo.targeting", {})
        geo_target = geo_rule.get("geo_target")
        if geo_target:
            meta_tags_html.append(
                f'<meta name="geo.region" content="{self._geo_region_code(geo_target)}">'
            )
        meta_tags_html.append('<title>{{TITLE_SLOT}}</title>')
        meta_tags_html.append(
            '<meta name="description" content="{{DESCRIPTION_SLOT}}">'
        )

        # 4. Hreflang links
        hreflang = geo_rule.get("hreflang_locales") or []
        hreflang_links_html = [
            f'<link rel="alternate" hreflang="{loc}" href="{{{{URL_SLOT_{loc}}}}}">'
            for loc in hreflang
        ]

        # 5. Canonical
        url_rule = rules.get("seo.url_structure", {})
        canonical_strategy = url_rule.get("canonical_strategy", "self_canonical")
        meta_tags_html.append('<link rel="canonical" href="{{CANONICAL_SLOT}}">')

        # 6. Disclosures slot keys
        disclosures_rule = rules.get("seo.disclosures.required", {})
        disclosures_slots = [
            f"disclosure_{d}_slot"
            for d in disclosures_rule.get("disclosures", [])
        ]

        # 7. Differentiator keywords
        keywords_rule = rules.get("seo.keywords.research_pending", {})
        differentiator_keywords = keywords_rule.get(
            "differentiator_keywords", []
        )

        return {
            "vertical": recommendations.vertical.value,
            "indexable": is_indexable,
            "indexable_blocker_reason": blocker,
            "robots_meta": robots_meta,
            "json_ld_block": json_ld_block,
            "json_ld_types": schema_types,
            "meta_tags_html": meta_tags_html,
            "hreflang_links_html": hreflang_links_html,
            "canonical_strategy": canonical_strategy,
            "disclosures_required": disclosures_slots,
            "differentiator_keywords": differentiator_keywords,
            "url_pattern_template": url_rule.get("url_pattern_template"),
            "ssr_required": url_rule.get("ssr_required", False),
            "validation_tags_pending": list(
                recommendations.aggregated_validation_tags
            ),
        }

    @staticmethod
    def _geo_region_code(geo_target: str) -> str:
        mapping = {
            "mx_nacional": "MX",
            "mx_sureste": "MX-YUC",
            "mx_merida": "MX-YUC",
            "latam": "MX",
            "global": "",
        }
        return mapping.get(geo_target, "")

    @staticmethod
    def _set_nested_slot(doc: dict[str, Any], dotted_path: str) -> None:
        parts = dotted_path.split(".")
        cursor = doc
        for p in parts[:-1]:
            if p not in cursor or not isinstance(cursor[p], dict):
                cursor[p] = {}
            cursor = cursor[p]
        cursor[parts[-1]] = f"{{{{{dotted_path.upper()}_SLOT}}}}"

    def monitor(self, ctx: TransversalContext) -> dict[str, Any]:
        """
        Health-check structural sin credenciales externas. Search Console
        API queda pendiente Sprint TRANSVERSAL-001 T3.
        """
        require_commercial(ctx.vertical)
        recommendations = self.recommend(ctx)
        impl_artifacts = self.implement(recommendations)

        warnings: list[str] = []
        blockers: list[str] = []

        if not impl_artifacts["indexable"]:
            blockers.append(
                f"Vertical no indexable. Razon: "
                f"{impl_artifacts['indexable_blocker_reason']}"
            )
        if not impl_artifacts["json_ld_types"]:
            warnings.append("No hay schema.org types configurados.")
        if not impl_artifacts["hreflang_links_html"]:
            warnings.append("Sin hreflang configurado — geo targeting limitado.")
        if impl_artifacts["validation_tags_pending"]:
            warnings.append(
                f"{len(impl_artifacts['validation_tags_pending'])} tags "
                f"Perplexity pendientes de resolver via DSC-V-001."
            )

        return {
            "vertical": ctx.vertical.value,
            "structural_health": {
                "indexable": impl_artifacts["indexable"],
                "schema_types_count": len(impl_artifacts["json_ld_types"]),
                "hreflang_count": len(impl_artifacts["hreflang_links_html"]),
                "disclosures_required_count": len(
                    impl_artifacts["disclosures_required"]),
                "ssr_required": impl_artifacts["ssr_required"],
            },
            "warnings": warnings,
            "blockers": blockers,
            "search_console_health": {
                "status": "pending_implementation",
                "note": (
                    "Sprint TRANSVERSAL-001 T3 — requiere Search Console API "
                    "credentials para crawl errors, indexability monitoring."
                ),
            },
        }


__all__ = ["SeoLayer"]
