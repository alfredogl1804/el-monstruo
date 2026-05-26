#!/usr/bin/env python3
"""TRANSVERSAL-001 T9 — Batch resolver de tags NEEDS_PERPLEXITY_VALIDATION.

Para cada claim_type unico detectado por tools/check_perplexity_tags.py,
consulta la API de Perplexity (Sonar) y persiste el resultado en
`validation_log` con validator='perplexity', evidence_url=citations,
ttl_seconds=86400, metadata con el raw_response.

USO:
    python scripts/_resolve_perplexity_tags.py --dry-run           # imprime queries sin llamar
    python scripts/_resolve_perplexity_tags.py                     # ejecuta batch real
    python scripts/_resolve_perplexity_tags.py --only TYPE [TYPE]  # resolver solo claim_types listados

ENV requerido:
    SONAR_API_KEY  - Perplexity API key (env del sandbox del agente)

PERSISTENCIA:
    Inserta cada row en `validation_log` via psycopg2/Management API.
    Si esta corriendo desde la Mac sin DB_URL, requiere flag --emit-sql para
    generar el SQL en stdout para que sb_sql.py lo aplique.

EXIT CODES:
    0 = batch completo (todos los tags resueltos + persistidos)
    1 = error API o persistencia
    2 = error de uso (env faltante, etc.)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import requests  # type: ignore[import-untyped]

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_TAGS = REPO_ROOT / "tools" / "check_perplexity_tags.py"

PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_MODEL = "sonar-pro"  # sonar-reasoning-pro is more powerful but slower


# Mapeo claim_type -> prompt magna ejecutable. Estos prompts estan diseniados
# para retornar respuestas estructuradas que sirven como validacion real
# para las capas transversales (Ventas, SEO, Publicidad, Tendencias, Operaciones,
# Finanzas). El TTL es 24h porque el mercado cambia rapido en 2026.
PROMPT_TEMPLATES: dict[str, str] = {
    "hubspot_api_2026": (
        "Cual es la version vigente y stable de HubSpot CRM API en mayo 2026? "
        "Lista los 3 endpoints mas usados para gestion de leads/deals y el formato "
        "de auth (OAuth vs API key). Responde estructurado, max 200 palabras."
    ),
    "stripe_api_2026": (
        "Cual es la version vigente de Stripe Payment API en mayo 2026? "
        "Lista los 3 endpoints clave para checkout/subscriptions y el modelo "
        "de pricing actual (transaction fees Mexico). Max 200 palabras."
    ),
    "pricing_benchmark_2026": (
        "Benchmark de pricing strategies SaaS B2B Latinoamerica 2026: "
        "rangos tipicos por tier (Starter/Pro/Enterprise), conversion rates "
        "freemium-to-paid, dinamicas de elasticidad. Max 250 palabras."
    ),
    "kpi_benchmark_2026": (
        "Benchmark de KPIs operativos SaaS 2026: CAC, LTV, churn mensual, "
        "MRR growth rate, payback period. Cita fuentes ChartMogul/SaaStr 2026. "
        "Max 250 palabras."
    ),
    "industry_unit_economics_benchmark_2026": (
        "Unit economics tipicos SaaS B2B (Mexico/LATAM) 2026: CAC promedio, "
        "LTV/CAC ratio, gross margin, magic number. Max 200 palabras."
    ),
    "keyword_research_2026": (
        "Mejores herramientas SEO keyword research 2026 con APIs: "
        "Ahrefs API, SEMrush API, Google Search Console API. Pricing y "
        "rate limits actuales. Max 200 palabras."
    ),
    "competitor_seo_2026": (
        "Tecnicas de competitor SEO analysis 2026: SERP analysis, content gap, "
        "backlink intelligence. Herramientas con API publica. Max 200 palabras."
    ),
    "google_ranking_factors_2026": (
        "Top 10 ranking factors de Google search en mayo 2026: AI Overview impact, "
        "E-E-A-T, Core Web Vitals 2026 thresholds. Cita Google Webmaster Blog 2026. "
        "Max 250 palabras."
    ),
    "ad_platform_api_2026": (
        "Versiones vigentes de Meta Marketing API, Google Ads API, LinkedIn "
        "Marketing API en mayo 2026. Limites de uso y deprecaciones recientes. "
        "Max 250 palabras."
    ),
    "ad_reporting_api_2026": (
        "Endpoints de reporting analytics para Meta Ads y Google Ads vigentes "
        "en mayo 2026: insights/metrics endpoints, latencia tipica de datos. "
        "Max 200 palabras."
    ),
    "ad_formats_2026": (
        "Formatos de ads con mayor performance en mayo 2026: video corto, "
        "carousel, collection, AI-generated. Benchmarks CTR y CVR. "
        "Max 200 palabras."
    ),
    "cpc_benchmark_2026": (
        "Benchmarks CPC Mexico 2026 por industria SaaS B2B en Google Ads "
        "y Meta Ads. Cita WordStream/Statista 2026. Max 200 palabras."
    ),
    "audience_size_2026": (
        "Tamano de audiencias targeting B2B en Meta y LinkedIn Mexico 2026: "
        "CMO, CTO, founders SaaS. Estimaciones reach. Max 150 palabras."
    ),
    "platform_policy_2026": (
        "Cambios recientes (Q1-Q2 2026) en politicas de Meta, Google, LinkedIn "
        "sobre advertising compliance, data privacy, AI content disclosure. "
        "Max 250 palabras."
    ),
    "trend_signals_active_2026": (
        "Que fuentes de senales de tendencia (signals) son canonicas en 2026 "
        "para detectar nichos emergentes: Google Trends, X/Twitter trending, "
        "Reddit r/technology, Polygon, Common Crawl. APIs vigentes. "
        "Max 250 palabras."
    ),
    "data_source_apis_vigentes_2026": (
        "APIs vigentes para data sources de tendencias en mayo 2026: "
        "Polygon (financial), Google Trends, RSS feeds top tech blogs, "
        "Reddit API. Rate limits y pricing. Max 250 palabras."
    ),
    "helpdesk_api_2026": (
        "APIs vigentes de helpdesk 2026: Intercom v2, Front API, Zendesk Support API. "
        "Endpoints clave de conversations y tickets. Max 200 palabras."
    ),
    "sla_metrics_pipeline_2026": (
        "Metricas SLA standard helpdesk SaaS 2026: first-response time, "
        "resolution time, CSAT. Benchmarks B2B. Max 200 palabras."
    ),
    "regulatory_landscape_2026": (
        "Cambios regulatorios relevantes para SaaS en Mexico (mayo 2026): "
        "LFPDPPP, CFDI 4.x facturacion, GDPR cross-border. Max 250 palabras."
    ),
    "accounting_stack_2026": (
        "Stack contable vigente para SaaS Mexico 2026: Contpaq i, QuickBooks, "
        "Xero. CFDI 4.x integraciones SAT via PAC. Max 250 palabras."
    ),
    "tax_rates_2026": ("Tasas impositivas vigentes Mexico 2026: ISR persona moral, IVA, ISN nomina. Max 150 palabras."),
    "alerting_stack_2026": (
        "Stack canonico de alerting/observability 2026 para SaaS production: "
        "Prometheus + Grafana vs Datadog vs Honeycomb. Pricing comparado. "
        "Max 200 palabras."
    ),
    "finops_dashboard_2026": (
        "Tools de FinOps dashboard 2026 para cloud cost monitoring: CloudHealth, "
        "Vantage, Spot.io, CloudZero. Pricing. Max 200 palabras."
    ),
    "integration_pattern_2026": (
        "Patrones de integracion canonicos 2026 para SaaS B2B: webhooks, "
        "event-driven (Kafka/Redpanda), iPaaS (Workato/Tray). Max 200 palabras."
    ),
}


@dataclass
class ResolvedTag:
    claim_type: str
    claim_value: str
    citations: list[str]
    raw_response: dict
    timestamp_unix: float


def _extract_unique_claim_types() -> list[str]:
    """Corre check_perplexity_tags.py y extrae claim_types unicos."""
    proc = subprocess.run(
        [sys.executable, str(TOOL_TAGS)],
        capture_output=True,
        text=True,
        timeout=15,
        cwd=str(REPO_ROOT),
    )
    output = proc.stdout + proc.stderr
    types: set[str] = set()
    for match in re.finditer(r"NEEDS_PERPLEXITY_VALIDATION\]\s+([a-z_0-9]+)", output):
        types.add(match.group(1))
    return sorted(types)


def _call_perplexity(claim_type: str, prompt: str, api_key: str) -> ResolvedTag:
    """Invoca Perplexity Sonar API y retorna ResolvedTag estructurado."""
    response = requests.post(
        PERPLEXITY_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": PERPLEXITY_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a research assistant. Provide accurate, source-cited answers. Be concise but complete."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 600,
        },
        timeout=45,
    )
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    citations = data.get("citations") or data.get("search_results") or []
    if citations and isinstance(citations[0], dict):
        citation_urls = [c.get("url", "") for c in citations if c.get("url")]
    else:
        citation_urls = [str(c) for c in citations if c]

    return ResolvedTag(
        claim_type=claim_type,
        claim_value=content[:500],  # truncar para validation_log
        citations=citation_urls[:5],
        raw_response=data,
        timestamp_unix=time.time(),
    )


def _build_insert_sql(resolved: list[ResolvedTag]) -> str:
    """Construye un INSERT SQL atomico para validation_log."""
    values_parts = []
    for r in resolved:
        fingerprint = hashlib.sha256(f"{r.claim_type}:{r.claim_value}".encode()).hexdigest()[:32]
        # Escapar single quotes y newlines en claim_value
        claim_value_escaped = r.claim_value.replace("'", "''").replace("\n", " ").replace("\r", "")
        evidence_url = r.citations[0] if r.citations else ""
        evidence_url_escaped = evidence_url.replace("'", "''")
        metadata = {
            "sprint": "TRANSVERSAL-001",
            "tarea": "T9",
            "agente": "manus_hilo_ejecutor_2",
            "citations": r.citations,
            "model": PERPLEXITY_MODEL,
        }
        metadata_json = json.dumps(metadata).replace("'", "''")
        values_parts.append(
            f"("
            f"'{r.claim_type}', "
            f"'{fingerprint}', "
            f"'{claim_value_escaped}', "
            f"'perplexity', "
            f"'{evidence_url_escaped}', "
            f"{r.timestamp_unix}, "
            f"86400, "
            f"'{metadata_json}'::jsonb"
            f")"
        )
    return (
        "INSERT INTO validation_log ("
        "claim_type, claim_fingerprint, claim_value, validator, "
        "evidence_url, timestamp_unix, ttl_seconds, metadata"
        ") VALUES " + ",\n".join(values_parts) + "\nRETURNING id, claim_type, validator, timestamp_unix;"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="No llama Perplexity, imprime los prompts.",
    )
    parser.add_argument(
        "--only",
        nargs="*",
        default=None,
        help="Solo resolver los claim_types listados (default: todos los detectados).",
    )
    parser.add_argument(
        "--emit-sql",
        type=Path,
        default=None,
        help="Path donde escribir el INSERT SQL generado (para sb_sql.py).",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=None,
        help="Path donde guardar el JSON raw de las respuestas Perplexity.",
    )
    args = parser.parse_args()

    api_key = os.environ.get("SONAR_API_KEY", "")
    if not args.dry_run and not api_key:
        print(
            "[ERR] SONAR_API_KEY no esta en env. Requerido para batch real.",
            file=sys.stderr,
        )
        return 2

    detected = _extract_unique_claim_types()
    if not detected:
        print(
            "[ERR] check_perplexity_tags.py no detecto ningun tag. Algo cambio en el repo.",
            file=sys.stderr,
        )
        return 1

    if args.only:
        to_process = [t for t in args.only if t in detected]
    else:
        to_process = [t for t in detected if t in PROMPT_TEMPLATES]

    missing_templates = [t for t in to_process if t not in PROMPT_TEMPLATES]
    if missing_templates:
        print(
            f"[ERR] {len(missing_templates)} claim_types sin prompt template: {missing_templates}",
            file=sys.stderr,
        )
        return 1

    print(f"[info] {len(detected)} claim_types detectados en codigo.")
    print(f"[info] {len(to_process)} a procesar este run.")

    if args.dry_run:
        for ct in to_process:
            print(f"\n=== {ct} ===")
            print(PROMPT_TEMPLATES[ct])
        return 0

    resolved: list[ResolvedTag] = []
    for i, claim_type in enumerate(to_process, 1):
        print(f"[{i}/{len(to_process)}] resolving {claim_type}...", flush=True)
        try:
            r = _call_perplexity(claim_type, PROMPT_TEMPLATES[claim_type], api_key)
            resolved.append(r)
            print(f"  OK {len(r.claim_value)}chars, {len(r.citations)} citations")
        except Exception as e:
            print(f"  FAIL {type(e).__name__}: {str(e)[:200]}", file=sys.stderr)
            return 1
        time.sleep(0.5)  # rate-limit gentil

    print(f"\n[info] {len(resolved)}/{len(to_process)} resolved OK.")

    if args.output_json:
        args.output_json.write_text(
            json.dumps(
                [
                    {
                        "claim_type": r.claim_type,
                        "claim_value": r.claim_value,
                        "citations": r.citations,
                        "timestamp_unix": r.timestamp_unix,
                    }
                    for r in resolved
                ],
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        print(f"[ok] raw JSON saved: {args.output_json}")

    insert_sql = _build_insert_sql(resolved)
    if args.emit_sql:
        args.emit_sql.write_text(insert_sql, encoding="utf-8")
        print(f"[ok] INSERT SQL emitted: {args.emit_sql}")
        print(f"     Aplicar con: python ~/.monstruo/sb_sql.py sql -f {args.emit_sql}")
    else:
        print("\n=== INSERT SQL ===")
        print(insert_sql)

    return 0


if __name__ == "__main__":
    sys.exit(main())
