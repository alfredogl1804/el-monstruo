"""
seo_layer.py — Capa SEO Transversal
=====================================
Capa Transversal #2 del Objetivo #9.
SEO técnico inyectado desde el diseño.

Componentes:
  1. Schema markup (JSON-LD) automático
  2. Sitemap XML generation
  3. Meta tags optimizados
  4. Keyword research via Perplexity
  5. Auditoría técnica via Lighthouse

Sprint 57 — "Las Capas Transversales"
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("seo_layer")


# ── Data models ───────────────────────────────────────────────────────────────


@dataclass
class SEOConfig:
    """Configuración SEO para un proyecto."""

    project_id: str
    site_name: str
    site_url: str
    description: str
    locale: str = "en_US"
    twitter_handle: Optional[str] = None
    og_image_url: Optional[str] = None
    keywords: list[str] = field(default_factory=list)
    schema_types: list[str] = field(default_factory=lambda: ["WebSite", "Organization"])


# ── SEOLayer ──────────────────────────────────────────────────────────────────


class SEOLayer:
    """Capa SEO transversal — inyectada en cada proyecto."""

    def __init__(self, config: SEOConfig, search_fn=None):
        self._config = config
        self._search = search_fn
        self._schema_gen = SchemaGenerator(config)
        self._meta_gen = MetaTagEngine(config)
        self._sitemap_gen = SitemapGenerator(config)

    async def setup_for_project(self, pages: list[dict]) -> dict:
        """Configurar SEO completo para un proyecto."""
        # 1. Generate schema markup for each page
        schemas = [self._schema_gen.generate_page_schema(p) for p in pages]

        # 2. Generate meta tags for each page
        metas = [self._meta_gen.generate_meta_tags(p) for p in pages]

        # 3. Generate sitemap
        sitemap = self._sitemap_gen.generate(pages)

        # 4. Generate robots.txt
        robots = self._generate_robots_txt()

        # 5. Generate organization schema
        org_schema = self._schema_gen.generate_organization_schema()

        return {
            "project_id": self._config.project_id,
            "schemas": schemas,
            "organization_schema": org_schema,
            "meta_tags": metas,
            "sitemap_xml": sitemap,
            "robots_txt": robots,
            "pages_optimized": len(pages),
            "status": "configured",
        }

    async def research_keywords(self, topic: str, intent: str = "informational") -> dict:
        """Investigar keywords relevantes via Perplexity."""
        if not self._search:
            return {"error": "Search function not available", "topic": topic}

        query = f"top keywords for {topic} {intent} intent 2026 search volume competition"
        try:
            result = await self._search(query, context=f"Keyword research for {topic}")
            return {
                "topic": topic,
                "intent": intent,
                "keywords": result.get("answer", ""),
                "citations": result.get("citations", []),
                "confidence": "magna_validated",
            }
        except Exception as e:
            logger.warning("keyword_research_failed", topic=topic, error=str(e))
            return {"error": str(e), "topic": topic}

    def _generate_robots_txt(self) -> str:
        """Generar robots.txt optimizado."""
        return f"""User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin/
Disallow: /_next/
Disallow: /private/
Disallow: /*.json$

Sitemap: {self._config.site_url}/sitemap.xml
"""

    def generate_htaccess_redirects(self, redirects: list[dict]) -> str:
        """Generar reglas de redirección para .htaccess."""
        lines = ["RewriteEngine On"]
        for r in redirects:
            lines.append(f"Redirect 301 {r['from']} {r['to']}")
        return "\n".join(lines)


# ── SchemaGenerator ───────────────────────────────────────────────────────────


class SchemaGenerator:
    """Generador de JSON-LD schema markup."""

    def __init__(self, config: SEOConfig):
        self._config = config

    def generate_page_schema(self, page: dict) -> dict:
        """Generar schema JSON-LD para una página."""
        schema: dict = {
            "@context": "https://schema.org",
            "@type": page.get("schema_type", "WebPage"),
            "name": page.get("title", self._config.site_name),
            "description": page.get("description", self._config.description),
            "url": f"{self._config.site_url}{page.get('path', '/')}",
            "inLanguage": self._config.locale[:2],
            "isPartOf": {
                "@type": "WebSite",
                "name": self._config.site_name,
                "url": self._config.site_url,
            },
        }

        schema_type = page.get("schema_type", "WebPage")

        if schema_type == "Product":
            schema.update(
                {
                    "offers": {
                        "@type": "Offer",
                        "price": page.get("price", 0),
                        "priceCurrency": page.get("currency", "USD"),
                        "availability": "https://schema.org/InStock",
                    },
                }
            )
        elif schema_type == "Article":
            schema.update(
                {
                    "author": {
                        "@type": "Person",
                        "name": page.get("author", "El Monstruo"),
                    },
                    "datePublished": page.get("published_at", datetime.now(timezone.utc).isoformat()),
                    "dateModified": page.get("updated_at", datetime.now(timezone.utc).isoformat()),
                }
            )
        elif schema_type == "FAQPage":
            faqs = page.get("faqs", [])
            schema["mainEntity"] = [
                {
                    "@type": "Question",
                    "name": faq.get("question", ""),
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": faq.get("answer", ""),
                    },
                }
                for faq in faqs
            ]

        return schema

    def generate_organization_schema(self) -> dict:
        """Generar schema de organización."""
        schema: dict = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": self._config.site_name,
            "url": self._config.site_url,
            "description": self._config.description,
        }
        if self._config.og_image_url:
            schema["logo"] = self._config.og_image_url
        return schema

    def to_script_tag(self, schema: dict) -> str:
        """Convertir schema a script tag HTML."""
        return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'


# ── MetaTagEngine ─────────────────────────────────────────────────────────────


class MetaTagEngine:
    """Motor de meta tags optimizados."""

    MAX_TITLE_LENGTH = 60
    MAX_DESCRIPTION_LENGTH = 160

    def __init__(self, config: SEOConfig):
        self._config = config

    def generate_meta_tags(self, page: dict) -> dict:
        """Generar meta tags completos para una página."""
        title = page.get("title", self._config.site_name)
        description = page.get("description", self._config.description)

        # Truncar description a 160 chars para SEO
        if len(description) > self.MAX_DESCRIPTION_LENGTH:
            description = description[: self.MAX_DESCRIPTION_LENGTH - 3] + "..."

        full_title = f"{title} | {self._config.site_name}"
        if len(full_title) > self.MAX_TITLE_LENGTH:
            full_title = title[: self.MAX_TITLE_LENGTH - 3] + "..."

        return {
            "title": full_title,
            "meta": {
                "description": description,
                "keywords": ", ".join(page.get("keywords", self._config.keywords)),
                "robots": page.get("robots", "index, follow"),
                "viewport": "width=device-width, initial-scale=1",
                "theme-color": page.get("theme_color", "#000000"),
            },
            "og": {
                "og:title": title,
                "og:description": description,
                "og:type": page.get("og_type", "website"),
                "og:url": f"{self._config.site_url}{page.get('path', '/')}",
                "og:image": page.get("og_image", self._config.og_image_url or ""),
                "og:site_name": self._config.site_name,
                "og:locale": self._config.locale,
            },
            "twitter": {
                "twitter:card": "summary_large_image",
                "twitter:title": title,
                "twitter:description": description,
                "twitter:site": self._config.twitter_handle or "",
                "twitter:image": page.get("og_image", self._config.og_image_url or ""),
            },
            "canonical": f"{self._config.site_url}{page.get('path', '/')}",
        }

    def to_html_tags(self, meta_tags: dict) -> str:
        """Convertir meta tags dict a HTML tags."""
        lines = [f"<title>{meta_tags['title']}</title>"]

        for name, content in meta_tags.get("meta", {}).items():
            if content:
                lines.append(f'<meta name="{name}" content="{content}">')

        for prop, content in meta_tags.get("og", {}).items():
            if content:
                lines.append(f'<meta property="{prop}" content="{content}">')

        for name, content in meta_tags.get("twitter", {}).items():
            if content:
                lines.append(f'<meta name="{name}" content="{content}">')

        if meta_tags.get("canonical"):
            lines.append(f'<link rel="canonical" href="{meta_tags["canonical"]}">')

        return "\n".join(lines)


# ── SitemapGenerator ──────────────────────────────────────────────────────────


class SitemapGenerator:
    """Generador de sitemaps XML."""

    def __init__(self, config: SEOConfig):
        self._config = config

    def generate(self, pages: list[dict]) -> str:
        """Generar sitemap XML."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        urls = []
        for page in pages:
            priority = page.get("priority", "0.5")
            changefreq = page.get("changefreq", "weekly")
            path = page.get("path", "/")

            urls.append(f"""  <url>
    <loc>{self._config.site_url}{path}</loc>
    <lastmod>{now}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>""")

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""

    def generate_index(self, sitemaps: list[str]) -> str:
        """Generar sitemap index para sitios grandes."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        entries = []
        for sitemap_url in sitemaps:
            entries.append(f"""  <sitemap>
    <loc>{sitemap_url}</loc>
    <lastmod>{now}</lastmod>
  </sitemap>""")

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(entries)}
</sitemapindex>"""


# ── Factory ───────────────────────────────────────────────────────────────────


def create_seo_layer(
    project_id: str,
    site_name: str,
    site_url: str,
    description: str,
    search_fn=None,
    **kwargs,
) -> SEOLayer:
    """Factory para crear un SEOLayer configurado para un proyecto."""
    config = SEOConfig(
        project_id=project_id,
        site_name=site_name,
        site_url=site_url,
        description=description,
        **kwargs,
    )
    return SEOLayer(config=config, search_fn=search_fn)
