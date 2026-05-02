#!/usr/bin/env python3
"""
AliExpress Full Product Validation Pipeline for Mexico
Orchestrates all analysis scripts and APIs to generate a comprehensive
safety report for a product purchase.

Usage: python full_validation.py <product_data.json> [reviews_data.json]

This script:
1. Runs the base product analysis (analyze_product.py)
2. Converts prices to MXN with live exchange rates (convert_currency.py)
3. Researches seller reputation online via Perplexity (research_seller.py)
4. Analyzes reviews with AI if available (ai_review_analyzer.py)
5. Combines everything into a comprehensive final report

Requires: product_data.json (mandatory), reviews_data.json (optional)
API keys (optional but recommended): SONAR_API_KEY, GEMINI_API_KEY or OPENAI_API_KEY
"""

import json
import os
import subprocess
import sys
from datetime import datetime

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def run_script(script_name: str, args: list, description: str) -> dict:
    """Run a sub-script and capture its output."""
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    cmd = [sys.executable, script_path] + args

    print(f"\n{'=' * 60}")
    print(f"▶ {description}")
    print(f"{'=' * 60}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print(f"✅ {description} — completado")
            return {"status": "success", "stdout": result.stdout}
        else:
            print(f"⚠️  {description} — error: {result.stderr[:200]}")
            return {"status": "error", "error": result.stderr[:500]}
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} — timeout")
        return {"status": "timeout"}
    except Exception as e:
        print(f"❌ {description} — excepción: {str(e)}")
        return {"status": "error", "error": str(e)}


def load_json_safe(filepath: str) -> dict:
    """Load a JSON file, returning empty dict on failure."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def generate_enhanced_report(
    product_data: dict,
    base_analysis: dict,
    currency_data: dict,
    seller_research: dict,
    ai_review_analysis: dict,
) -> str:
    """Generate the final comprehensive report combining all data sources."""
    report = []

    # Determine overall verdict considering all sources
    base_score = base_analysis.get("risk_score", 50)
    verdict = base_analysis.get("verdict", "DESCONOCIDO")
    emoji = base_analysis.get("emoji", "❓")

    report.append(f"# {emoji} Reporte Completo de Validación AliExpress → México")
    report.append(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("**Motor de análisis:** Validación multi-capa con IA")
    report.append("")

    product_name = product_data.get("product_name", "Producto no identificado")
    report.append(f"## Producto: {product_name}")
    url = product_data.get("product_url", "N/A")
    report.append(f"**URL:** {url}")
    report.append("")

    # Verdict
    report.append("---")
    report.append(f"### Veredicto Final: {emoji} {verdict}")
    report.append(f"**Puntuación de riesgo:** {base_score}/100 (0=seguro, 100=peligroso)")
    report.append(f"> {base_analysis.get('recommendation', '')}")
    report.append("---")
    report.append("")

    # === COSTS IN MXN ===
    report.append("## Costo Total Real en Pesos Mexicanos")
    report.append("")
    if currency_data.get("status") == "success":
        rate = currency_data.get("exchange_rate", 0)
        report.append(f"**Tipo de cambio actual:** 1 USD = ${rate:.2f} MXN")
        report.append("")
        report.append("| Concepto | USD | MXN |")
        report.append("|----------|-----|-----|")
        report.append(
            f"| Precio del producto | ${currency_data.get('product_price_usd', 0):.2f} | ${currency_data.get('product_price_mxn', 0):.2f} |"
        )
        report.append(
            f"| Costo de envío | ${currency_data.get('shipping_cost_usd', 0):.2f} | ${currency_data.get('shipping_cost_mxn', 0):.2f} |"
        )
        tax_usd = currency_data.get("import_tax_usd", 0)
        tax_mxn = currency_data.get("import_tax_mxn", 0)
        if tax_usd > 0:
            report.append(f"| Impuesto importación (~20%) | ${tax_usd:.2f} | ${tax_mxn:.2f} |")
        else:
            report.append("| Impuesto importación | Incluido | Incluido |")
        report.append(
            f"| **TOTAL ESTIMADO** | **${currency_data.get('total_usd', 0):.2f}** | **${currency_data.get('total_mxn', 0):.2f}** |"
        )
    else:
        # Fallback without exchange rate
        price = product_data.get("product_price_usd", 0)
        shipping = product_data.get("shipping_cost_usd", 0)
        report.append(f"| Precio del producto | ${price:.2f} USD |")
        report.append(f"| Costo de envío | ${shipping:.2f} USD |")
        report.append("*(No se pudo obtener tipo de cambio en tiempo real)*")
    report.append("")

    # === SHIPPING ===
    report.append("## Análisis de Envío a México")
    report.append("")
    method = product_data.get("shipping_method", "N/D")
    delivery = product_data.get("estimated_delivery_days", "N/D")
    tracking = product_data.get("has_tracking", None)
    import_tax = product_data.get("includes_import_tax", None)

    report.append("| Aspecto | Detalle |")
    report.append("|---------|---------|")
    report.append(f"| Método de envío | {method} |")
    report.append(f"| Tiempo estimado | {delivery} días |")
    report.append(f"| Rastreo incluido | {'Sí' if tracking else 'No' if tracking is False else 'N/D'} |")
    report.append(f"| Impuesto incluido | {'Sí' if import_tax else 'No' if import_tax is False else 'N/D'} |")
    report.append("")

    # === SELLER ANALYSIS ===
    report.append("## Análisis del Vendedor")
    report.append("")
    store_name = product_data.get("store_name", "N/D")
    store_age = product_data.get("store_age_years", "N/D")
    feedback = product_data.get("seller_positive_feedback_pct", "N/D")
    orders = product_data.get("total_orders", "N/D")

    report.append("| Métrica | Valor | Evaluación |")
    report.append("|---------|-------|------------|")
    report.append(f"| Tienda | {store_name} | — |")
    if isinstance(store_age, (int, float)):
        eval_age = "Excelente" if store_age >= 3 else "Bueno" if store_age >= 1 else "Riesgoso"
        report.append(f"| Antigüedad | {store_age:.1f} años | {eval_age} |")
    if isinstance(feedback, (int, float)):
        eval_fb = (
            "Excelente" if feedback >= 98 else "Bueno" if feedback >= 95 else "Regular" if feedback >= 90 else "Malo"
        )
        report.append(f"| Feedback positivo | {feedback}% | {eval_fb} |")
    if isinstance(orders, (int, float)):
        eval_ord = (
            "Excelente" if orders >= 1000 else "Bueno" if orders >= 100 else "Bajo" if orders >= 10 else "Muy bajo"
        )
        report.append(f"| Órdenes totales | {orders:,} | {eval_ord} |")
    report.append("")

    # Detailed ratings
    for key, label in [
        ("rating_item_as_described", "Producto como se describe"),
        ("rating_communication", "Comunicación"),
        ("rating_shipping_speed", "Velocidad de envío"),
    ]:
        val = product_data.get(key)
        if val is not None:
            bar = "█" * int(val) + "░" * (5 - int(val))
            report.append(f"- **{label}:** {val}/5.0 [{bar}]")
    report.append("")

    # === SELLER ONLINE REPUTATION (Perplexity) ===
    if seller_research.get("status") == "success" and seller_research.get("findings"):
        report.append("## Reputación del Vendedor en Internet (Investigación con IA)")
        report.append("")
        report.append(seller_research["findings"])
        report.append("")
        sources = seller_research.get("sources", [])
        if sources:
            report.append("**Fuentes consultadas:**")
            for i, src in enumerate(sources[:5], 1):
                report.append(f"- [{src}]({src})")
            report.append("")

    # === REVIEW ANALYSIS ===
    report.append("## Análisis de Reseñas")
    report.append("")

    # AI analysis if available
    if ai_review_analysis and ai_review_analysis.get("resumen_general"):
        report.append("### Análisis con Inteligencia Artificial")
        report.append("")
        report.append(f"> {ai_review_analysis.get('resumen_general', '')}")
        report.append("")

        real_pct = ai_review_analysis.get("porcentaje_reales_estimado", "N/D")
        fake_pct = ai_review_analysis.get("porcentaje_falsas_estimado", "N/D")
        confidence = ai_review_analysis.get("nivel_confianza_reseñas", "N/D")
        report.append(f"- **Reseñas estimadas reales:** {real_pct}%")
        report.append(f"- **Reseñas estimadas falsas:** {fake_pct}%")
        report.append(f"- **Nivel de confianza:** {confidence}")
        report.append("")

        patterns = ai_review_analysis.get("patrones_sospechosos", [])
        if patterns:
            report.append("**Patrones sospechosos detectados por IA:**")
            for p in patterns:
                report.append(f"- ⚠️ {p}")
            report.append("")

        positives = ai_review_analysis.get("señales_positivas", [])
        if positives:
            report.append("**Señales de autenticidad:**")
            for p in positives:
                report.append(f"- ✅ {p}")
            report.append("")

        mx_alerts = ai_review_analysis.get("alertas_para_mexico", [])
        if mx_alerts:
            report.append("**Alertas específicas para México:**")
            for a in mx_alerts:
                report.append(f"- 🇲🇽 {a}")
            report.append("")

        # Most trustworthy reviews
        trusted = ai_review_analysis.get("reseñas_mas_confiables", [])
        if trusted:
            report.append("### Reseñas Más Confiables (según IA)")
            report.append("")
            for r in trusted[:3]:
                report.append(f'> *"{r.get("texto_original", "")}"*')
                report.append(f"> ✅ {r.get('razon_confiable', '')}")
                report.append("")

    # Base review stats
    total_rev = product_data.get("total_reviews", 0)
    photo_rev = product_data.get("reviews_with_photos", 0)
    avg_rating = product_data.get("avg_review_rating", "N/D")
    report.append("### Estadísticas de Reseñas")
    report.append(f"- **Total:** {total_rev} | **Con fotos:** {photo_rev} | **Promedio:** {avg_rating}/5")
    report.append("")

    # Sample reviews
    sample = product_data.get("sample_real_reviews", [])
    if sample:
        report.append("### Reseñas Destacadas")
        report.append("")
        for rev in sample[:5]:
            stars = "⭐" * int(rev.get("rating", 0))
            report.append(f'> {stars} — *"{rev.get("text", "")}"*')
            if rev.get("has_photo"):
                report.append("> 📷 Con foto")
            if rev.get("country"):
                report.append(f"> 🌍 {rev['country']}")
            report.append("")

    # === GREEN FLAGS ===
    green = base_analysis.get("green_flags", [])
    if green:
        report.append("## ✅ Señales Positivas")
        report.append("")
        for f in green:
            report.append(f"- {f}")
        report.append("")

    # === RED FLAGS ===
    red = base_analysis.get("red_flags", [])
    if red:
        report.append("## 🚩 Señales de Alerta")
        report.append("")
        for f in red:
            report.append(f"- {f}")
        report.append("")

    # === FINAL RECOMMENDATIONS ===
    report.append("## Recomendaciones Finales")
    report.append("")
    if base_score <= 40:
        report.append("1. **Procede con la compra** usando el método de pago de AliExpress")
        report.append("2. Toma capturas de pantalla de la descripción antes de comprar")
        report.append("3. Verifica que el método de envío incluya rastreo a México")
        if currency_data.get("status") == "success":
            report.append(
                f"4. Prepara aproximadamente **${currency_data.get('total_mxn', 0):.2f} MXN** como presupuesto total"
            )
        report.append("5. Abre disputa si el tracking no se actualiza en 15 días")
    else:
        report.append("1. **Busca alternativas** con vendedores mejor calificados")
        report.append("2. Si decides comprar, usa SOLO el sistema de pago de AliExpress")
        report.append("3. Toma capturas de pantalla de TODO antes de comprar")
        report.append("4. Abre disputa INMEDIATAMENTE si el tracking no se actualiza en 15 días")
        report.append("5. **No cierres disputas** aunque el vendedor te lo pida")
    report.append("")

    # Footer
    report.append("---")
    report.append(f"*Reporte generado por AliExpress MX Validator | {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    report.append(
        f"*Motores: Análisis de riesgo + Perplexity Sonar + {'Gemini/OpenAI' if ai_review_analysis else 'Reglas'} + Tipo de cambio en vivo*"
    )

    return "\n".join(report)


def main():
    if len(sys.argv) < 2:
        print("Uso: python full_validation.py <product_data.json> [reviews_data.json]")
        sys.exit(1)

    product_file = sys.argv[1]
    reviews_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(product_file):
        print(f"Error: No se encontró '{product_file}'")
        sys.exit(1)

    product_data = load_json_safe(product_file)
    if not product_data:
        print("Error: No se pudo leer el archivo de datos del producto")
        sys.exit(1)

    print("🔍 VALIDACIÓN COMPLETA DE ALIEXPRESS PARA MÉXICO")
    print(f"   Producto: {product_data.get('product_name', 'N/D')}")
    print(f"   Tienda: {product_data.get('store_name', 'N/D')}")

    # Step 1: Base analysis
    r1 = run_script("analyze_product.py", [product_file], "Análisis base del producto")
    report_file = product_file.replace(".json", "_report.md")

    # Load base analysis results by re-running the score calculation
    sys.path.insert(0, SCRIPTS_DIR)
    from analyze_product import calculate_risk_score

    base_analysis = calculate_risk_score(product_data)

    # Step 2: Currency conversion
    price = product_data.get("product_price_usd", 0)
    shipping = product_data.get("shipping_cost_usd", 0)
    import_included = product_data.get("includes_import_tax", False)

    from convert_currency import calculate_total_mxn

    print(f"\n{'=' * 60}")
    print("▶ Conversión de moneda USD → MXN")
    print(f"{'=' * 60}")
    currency_data = calculate_total_mxn(price, shipping, import_tax_included=import_included)
    if currency_data.get("status") == "success":
        print(f"✅ Tipo de cambio: 1 USD = ${currency_data['exchange_rate']:.2f} MXN")
    else:
        print("⚠️  No se pudo obtener tipo de cambio")

    # Step 3: Seller research (Perplexity)
    seller_research = {}
    store_name = product_data.get("store_name", "")
    store_url = product_data.get("product_url", "")
    if store_name and os.environ.get("SONAR_API_KEY"):
        r3 = run_script(
            "research_seller.py", [store_name, store_url], "Investigación de reputación del vendedor (Perplexity)"
        )
        safe_name = store_name.replace(" ", "_").replace("/", "_")[:50]
        seller_file = f"seller_research_{safe_name}.json"
        seller_research = load_json_safe(seller_file)
    else:
        print(f"\n{'=' * 60}")
        print("⏭️  Investigación del vendedor — omitida (sin SONAR_API_KEY)")
        print(f"{'=' * 60}")

    # Step 4: AI review analysis
    ai_review_analysis = {}
    target_reviews = reviews_file or product_file
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY"):
        r4 = run_script("ai_review_analyzer.py", [target_reviews], "Análisis de reseñas con IA")
        ai_file = target_reviews.replace(".json", "_ai_analysis.json")
        ai_review_analysis = load_json_safe(ai_file)
    else:
        print(f"\n{'=' * 60}")
        print("⏭️  Análisis IA de reseñas — omitido (sin GEMINI_API_KEY ni OPENAI_API_KEY)")
        print(f"{'=' * 60}")

    # Step 5: Generate enhanced report
    print(f"\n{'=' * 60}")
    print("▶ Generando reporte final completo")
    print(f"{'=' * 60}")

    final_report = generate_enhanced_report(
        product_data, base_analysis, currency_data, seller_research, ai_review_analysis
    )

    output_path = product_file.replace(".json", "_full_report.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_report)

    print(f"\n✅ REPORTE COMPLETO GENERADO: {output_path}")
    print(
        f"\nVeredicto: {base_analysis['emoji']} {base_analysis['verdict']} (riesgo: {base_analysis['risk_score']}/100)"
    )
    if currency_data.get("status") == "success":
        print(f"Costo total estimado: ${currency_data['total_mxn']:.2f} MXN")

    return output_path


if __name__ == "__main__":
    main()
