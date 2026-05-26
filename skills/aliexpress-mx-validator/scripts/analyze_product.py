#!/usr/bin/env python3
"""
AliExpress Product Analyzer for Mexico
Extracts and analyzes product data from AliExpress product pages.
Usage: python analyze_product.py <product_url_or_html_file>

This script processes saved HTML or extracted data to generate a safety report.
It can work with:
  1. A JSON file with pre-extracted product data
  2. Raw text/markdown extracted from an AliExpress product page
"""

import json
import os
import sys
from datetime import datetime


def calculate_risk_score(data: dict) -> dict:
    """Calculate a risk score (0-100) based on multiple factors.
    0 = very safe, 100 = very risky.
    """
    score = 50  # Start neutral
    reasons = []
    green_flags = []

    # --- Seller Rating Analysis ---
    positive_feedback = data.get("seller_positive_feedback_pct", None)
    if positive_feedback is not None:
        if positive_feedback >= 98:
            score -= 15
            green_flags.append(f"Feedback positivo excelente: {positive_feedback}%")
        elif positive_feedback >= 95:
            score -= 10
            green_flags.append(f"Feedback positivo bueno: {positive_feedback}%")
        elif positive_feedback >= 90:
            score -= 3
        elif positive_feedback >= 80:
            score += 10
            reasons.append(f"Feedback positivo bajo: {positive_feedback}%")
        else:
            score += 25
            reasons.append(f"Feedback positivo muy bajo: {positive_feedback}% — ALERTA ROJA")

    # --- Store Age ---
    store_age_years = data.get("store_age_years", None)
    if store_age_years is not None:
        if store_age_years >= 5:
            score -= 10
            green_flags.append(f"Tienda veterana: {store_age_years} años")
        elif store_age_years >= 3:
            score -= 7
            green_flags.append(f"Tienda establecida: {store_age_years} años")
        elif store_age_years >= 1:
            score -= 3
        elif store_age_years < 0.5:
            score += 15
            reasons.append(f"Tienda muy nueva: {store_age_years:.1f} años — riesgo elevado")
        else:
            score += 8
            reasons.append(f"Tienda relativamente nueva: {store_age_years:.1f} años")

    # --- Order Count ---
    orders = data.get("total_orders", None)
    if orders is not None:
        if orders >= 1000:
            score -= 10
            green_flags.append(f"Alto volumen de ventas: {orders:,} órdenes")
        elif orders >= 500:
            score -= 7
            green_flags.append(f"Buen volumen de ventas: {orders:,} órdenes")
        elif orders >= 100:
            score -= 3
        elif orders >= 10:
            score += 5
        elif orders < 10:
            score += 15
            reasons.append(f"Muy pocas ventas: {orders} órdenes — posible tienda fantasma")

    # --- Detailed Ratings (Communication, Shipping, Quality) ---
    for metric_key, metric_name in [
        ("rating_item_as_described", "Producto como se describe"),
        ("rating_communication", "Comunicación"),
        ("rating_shipping_speed", "Velocidad de envío"),
    ]:
        val = data.get(metric_key, None)
        if val is not None:
            if val >= 4.7:
                score -= 3
                green_flags.append(f"{metric_name}: {val}/5.0 — excelente")
            elif val >= 4.3:
                score -= 1
            elif val >= 4.0:
                pass
            elif val >= 3.5:
                score += 5
                reasons.append(f"{metric_name}: {val}/5.0 — por debajo del promedio")
            else:
                score += 12
                reasons.append(f"{metric_name}: {val}/5.0 — ALERTA")

    # --- Shipping Analysis ---
    shipping_method = data.get("shipping_method", "").lower()
    shipping_cost_usd = data.get("shipping_cost_usd", None)
    product_price_usd = data.get("product_price_usd", None)
    has_tracking = data.get("has_tracking", None)

    if has_tracking is False:
        score += 10
        reasons.append("Envío SIN rastreo — riesgo de pérdida sin recurso")
    elif has_tracking is True:
        score -= 5
        green_flags.append("Envío con rastreo incluido")

    if shipping_cost_usd is not None and product_price_usd is not None:
        if product_price_usd > 0:
            ratio = shipping_cost_usd / product_price_usd
            if ratio > 1.5:
                score += 15
                reasons.append(
                    f"Costo de envío (${shipping_cost_usd:.2f}) es {ratio:.1f}x el precio del producto — posible sobrecargo"
                )
            elif ratio > 0.8:
                score += 8
                reasons.append(
                    f"Costo de envío alto relativo al producto: ${shipping_cost_usd:.2f} vs ${product_price_usd:.2f}"
                )
        if shipping_cost_usd == 0 and product_price_usd < 2:
            score += 8
            reasons.append("Envío gratis en producto muy barato — posible señuelo")

    # Trusted shipping methods
    trusted_methods = ["aliexpress standard", "cainiao", "aliexpress direct", "dhl", "fedex", "ups", "ems"]
    if shipping_method:
        if any(m in shipping_method for m in trusted_methods):
            score -= 5
            green_flags.append(f"Método de envío confiable: {shipping_method}")
        elif "china post" in shipping_method or "yanwen" in shipping_method:
            score += 3
            reasons.append(f"Método de envío lento/menos confiable: {shipping_method}")

    # --- Estimated delivery time ---
    delivery_days = data.get("estimated_delivery_days", None)
    if delivery_days is not None:
        if delivery_days > 90:
            score += 10
            reasons.append(f"Tiempo de entrega excesivo: {delivery_days} días")
        elif delivery_days > 60:
            score += 5
            reasons.append(f"Tiempo de entrega largo: {delivery_days} días")

    # --- Mexico Import Tax ---
    includes_import_tax = data.get("includes_import_tax", None)
    if includes_import_tax is True:
        green_flags.append("Impuesto de importación incluido en el precio")
    elif includes_import_tax is False:
        reasons.append("Impuesto de importación NO incluido — esperar ~20% adicional en aduanas")

    # --- Review Analysis ---
    total_reviews = data.get("total_reviews", 0)
    reviews_with_photos = data.get("reviews_with_photos", 0)
    avg_review_rating = data.get("avg_review_rating", None)

    if total_reviews == 0:
        score += 15
        reasons.append("Sin reseñas — imposible verificar calidad")
    elif total_reviews < 5:
        score += 10
        reasons.append(f"Muy pocas reseñas: {total_reviews}")
    elif total_reviews >= 50:
        score -= 5
        green_flags.append(f"Cantidad sólida de reseñas: {total_reviews}")

    if total_reviews > 0 and reviews_with_photos > 0:
        photo_ratio = reviews_with_photos / total_reviews
        if photo_ratio >= 0.3:
            score -= 5
            green_flags.append(
                f"{reviews_with_photos} reseñas con fotos ({photo_ratio:.0%}) — buena verificación visual"
            )
        elif photo_ratio >= 0.1:
            score -= 2

    if avg_review_rating is not None:
        if avg_review_rating >= 4.8:
            # Suspiciously high can be fake
            if total_reviews > 100:
                score += 3
                reasons.append(
                    f"Calificación sospechosamente perfecta: {avg_review_rating}/5 con {total_reviews} reseñas"
                )
        elif avg_review_rating >= 4.5:
            score -= 5
            green_flags.append(f"Buena calificación promedio: {avg_review_rating}/5")
        elif avg_review_rating >= 4.0:
            score -= 2
        elif avg_review_rating < 3.5:
            score += 15
            reasons.append(f"Calificación baja: {avg_review_rating}/5 — ALERTA")

    # --- Suspicious Patterns ---
    description_flags = data.get("description_red_flags", [])
    for flag in description_flags:
        score += 8
        reasons.append(f"Palabra sospechosa en descripción: '{flag}'")

    multiple_categories = data.get("sells_unrelated_categories", False)
    if multiple_categories:
        score += 10
        reasons.append("Tienda vende categorías no relacionadas — posible tienda clonada")

    # Clamp score
    score = max(0, min(100, score))

    # Determine verdict
    if score <= 20:
        verdict = "SEGURO"
        emoji = "🟢"
        recommendation = "Compra con confianza. Este producto y vendedor muestran señales sólidas de legitimidad."
    elif score <= 40:
        verdict = "PROBABLEMENTE SEGURO"
        emoji = "🟡"
        recommendation = "La compra parece razonable, pero revisa las observaciones antes de proceder."
    elif score <= 60:
        verdict = "PRECAUCIÓN"
        emoji = "🟠"
        recommendation = "Existen señales de riesgo. Considera buscar alternativas o investiga más a fondo."
    elif score <= 80:
        verdict = "RIESGOSO"
        emoji = "🔴"
        recommendation = "Múltiples señales de alerta. Se recomienda NO comprar este producto."
    else:
        verdict = "MUY RIESGOSO"
        emoji = "🔴🔴"
        recommendation = "ALERTA MÁXIMA. Altísima probabilidad de estafa. No comprar."

    return {
        "risk_score": score,
        "verdict": verdict,
        "emoji": emoji,
        "recommendation": recommendation,
        "red_flags": reasons,
        "green_flags": green_flags,
    }


def generate_report(data: dict, analysis: dict) -> str:
    """Generate a Markdown report with the analysis results."""
    report = []
    report.append(f"# {analysis['emoji']} Reporte de Validación AliExpress → México")
    report.append(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("")

    product_name = data.get("product_name", "Producto no identificado")
    report.append(f"## Producto: {product_name}")
    report.append("")

    url = data.get("product_url", "N/A")
    report.append(f"**URL:** {url}")
    report.append("")

    # Verdict box
    report.append("---")
    report.append(f"### Veredicto: {analysis['emoji']} {analysis['verdict']}")
    report.append(f"**Puntuación de riesgo:** {analysis['risk_score']}/100 (0=seguro, 100=peligroso)")
    report.append(f"> {analysis['recommendation']}")
    report.append("---")
    report.append("")

    # Price and shipping summary
    report.append("## Resumen de Costos para México")
    report.append("")
    price = data.get("product_price_usd", "N/D")
    shipping = data.get("shipping_cost_usd", "N/D")
    method = data.get("shipping_method", "N/D")
    delivery = data.get("estimated_delivery_days", "N/D")
    tracking = data.get("has_tracking", "N/D")
    import_tax = data.get("includes_import_tax", "N/D")

    report.append("| Concepto | Valor |")
    report.append("|----------|-------|")
    report.append(f"| Precio del producto | ${price} USD |")
    report.append(f"| Costo de envío | ${shipping} USD |")
    report.append(f"| Método de envío | {method} |")
    report.append(f"| Tiempo estimado de entrega | {delivery} días |")
    report.append(f"| Rastreo incluido | {'Sí' if tracking is True else 'No' if tracking is False else 'N/D'} |")
    report.append(
        f"| Impuesto importación incluido | {'Sí' if import_tax is True else 'No (~20% adicional)' if import_tax is False else 'N/D'} |"
    )

    if isinstance(price, (int, float)) and isinstance(shipping, (int, float)):
        total = price + shipping
        tax_estimate = total * 0.20 if not import_tax else 0
        grand_total = total + tax_estimate
        report.append(f"| **Costo total estimado** | **${grand_total:.2f} USD** |")
    report.append("")

    # Seller analysis
    report.append("## Análisis del Vendedor")
    report.append("")
    store_name = data.get("store_name", "N/D")
    store_age = data.get("store_age_years", "N/D")
    feedback = data.get("seller_positive_feedback_pct", "N/D")
    followers = data.get("store_followers", "N/D")
    orders = data.get("total_orders", "N/D")

    report.append("| Métrica | Valor | Evaluación |")
    report.append("|---------|-------|------------|")
    report.append(f"| Nombre de tienda | {store_name} | — |")

    if isinstance(store_age, (int, float)):
        eval_age = "Excelente" if store_age >= 3 else "Bueno" if store_age >= 1 else "Riesgoso"
        report.append(f"| Antigüedad | {store_age:.1f} años | {eval_age} |")
    else:
        report.append(f"| Antigüedad | {store_age} | — |")

    if isinstance(feedback, (int, float)):
        eval_fb = (
            "Excelente" if feedback >= 98 else "Bueno" if feedback >= 95 else "Regular" if feedback >= 90 else "Malo"
        )
        report.append(f"| Feedback positivo | {feedback}% | {eval_fb} |")
    else:
        report.append(f"| Feedback positivo | {feedback} | — |")

    report.append(f"| Seguidores | {followers} | — |")
    if isinstance(orders, (int, float)):
        eval_ord = (
            "Excelente" if orders >= 1000 else "Bueno" if orders >= 100 else "Bajo" if orders >= 10 else "Muy bajo"
        )
        report.append(f"| Órdenes totales | {orders:,} | {eval_ord} |")
    else:
        report.append(f"| Órdenes totales | {orders} | — |")
    report.append("")

    # Detailed ratings
    for key, label in [
        ("rating_item_as_described", "Producto como se describe"),
        ("rating_communication", "Comunicación"),
        ("rating_shipping_speed", "Velocidad de envío"),
    ]:
        val = data.get(key)
        if val is not None:
            bar = "█" * int(val) + "░" * (5 - int(val))
            report.append(f"- **{label}:** {val}/5.0 [{bar}]")
    report.append("")

    # Review analysis
    report.append("## Análisis de Reseñas")
    report.append("")
    total_rev = data.get("total_reviews", "N/D")
    photo_rev = data.get("reviews_with_photos", "N/D")
    avg_rating = data.get("avg_review_rating", "N/D")

    report.append(f"- **Total de reseñas:** {total_rev}")
    report.append(f"- **Reseñas con fotos:** {photo_rev}")
    report.append(f"- **Calificación promedio:** {avg_rating}/5")
    report.append("")

    # Sample reviews if available
    sample_reviews = data.get("sample_real_reviews", [])
    if sample_reviews:
        report.append("### Reseñas Destacadas (posiblemente reales)")
        report.append("")
        for rev in sample_reviews[:5]:
            stars = "⭐" * int(rev.get("rating", 0))
            report.append(f'> {stars} — *"{rev.get("text", "")}"*')
            if rev.get("has_photo"):
                report.append("> 📷 Incluye foto del producto recibido")
            if rev.get("country"):
                report.append(f"> 🌍 País: {rev['country']}")
            report.append("")

    suspicious_reviews = data.get("suspicious_review_patterns", [])
    if suspicious_reviews:
        report.append("### Patrones Sospechosos en Reseñas")
        report.append("")
        for pattern in suspicious_reviews:
            report.append(f"- ⚠️ {pattern}")
        report.append("")

    # Green flags
    if analysis["green_flags"]:
        report.append("## ✅ Señales Positivas")
        report.append("")
        for flag in analysis["green_flags"]:
            report.append(f"- {flag}")
        report.append("")

    # Red flags
    if analysis["red_flags"]:
        report.append("## 🚩 Señales de Alerta")
        report.append("")
        for flag in analysis["red_flags"]:
            report.append(f"- {flag}")
        report.append("")

    # Recommendations
    report.append("## Recomendaciones")
    report.append("")
    if analysis["risk_score"] <= 40:
        report.append(
            "1. Procede con la compra usando el método de pago de AliExpress (nunca pagues fuera de la plataforma)"
        )
        report.append("2. Toma capturas de pantalla de la descripción del producto antes de comprar")
        report.append("3. Verifica que el método de envío incluya rastreo")
        report.append("4. Recuerda que el impuesto de importación a México es ~20%")
    else:
        report.append("1. **Busca alternativas** con vendedores mejor calificados")
        report.append("2. Si decides comprar, usa SOLO el sistema de pago de AliExpress")
        report.append("3. Toma capturas de pantalla de TODO antes de comprar")
        report.append("4. Abre disputa INMEDIATAMENTE si el tracking no se actualiza en 15 días")
        report.append("5. No cierres disputas aunque el vendedor te lo pida")
    report.append("")

    return "\n".join(report)


def main():
    if len(sys.argv) < 2:
        print("Uso: python analyze_product.py <archivo_datos.json>")
        print("El archivo JSON debe contener los datos extraídos del producto.")
        sys.exit(1)

    filepath = sys.argv[1]

    if not os.path.exists(filepath):
        print(f"Error: No se encontró el archivo '{filepath}'")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    analysis = calculate_risk_score(data)
    report = generate_report(data, analysis)

    # Save report
    output_path = filepath.replace(".json", "_report.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print(f"\n--- Reporte guardado en: {output_path} ---")


if __name__ == "__main__":
    main()
