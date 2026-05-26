#!/usr/bin/env python3
"""
AliExpress Review Authenticity Analyzer
Analyzes a list of reviews and flags suspicious patterns.
Usage: python analyze_reviews.py <reviews_file.json>

Input JSON format:
[
  {
    "rating": 5,
    "text": "Great product!",
    "date": "2025-01-15",
    "has_photo": true,
    "buyer_country": "MX",
    "buyer_order_count": 3,
    "text_length": 15
  },
  ...
]
"""

import json
import os
import sys
from collections import Counter

# Common generic phrases that indicate fake/low-effort reviews
GENERIC_PHRASES_EN = [
    "good product",
    "nice product",
    "great product",
    "excellent product",
    "very good",
    "fast shipping",
    "good quality",
    "as described",
    "recommend",
    "perfect",
    "love it",
    "amazing",
    "wonderful",
    "five stars",
    "5 stars",
    "best product",
]

GENERIC_PHRASES_ES = [
    "buen producto",
    "excelente producto",
    "muy bueno",
    "recomendado",
    "todo bien",
    "perfecto",
    "me encanta",
    "buena calidad",
    "como se describe",
    "envío rápido",
    "5 estrellas",
]

GENERIC_PHRASES_PT = [
    "bom produto",
    "excelente",
    "muito bom",
    "recomendo",
    "perfeito",
    "ótimo",
    "chegou rápido",
]


def analyze_reviews(reviews: list) -> dict:
    """Analyze a list of reviews for authenticity signals."""
    total = len(reviews)
    if total == 0:
        return {
            "total_reviews": 0,
            "verdict": "Sin reseñas para analizar",
            "authenticity_score": 0,
            "details": {},
            "suspicious_patterns": ["No hay reseñas — imposible verificar"],
            "real_review_candidates": [],
        }

    # --- Metrics ---
    ratings = [r.get("rating", 0) for r in reviews]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    # Rating distribution
    rating_dist = Counter(ratings)
    five_star_pct = rating_dist.get(5, 0) / total * 100 if total > 0 else 0
    one_star_pct = rating_dist.get(1, 0) / total * 100 if total > 0 else 0

    # Reviews with photos
    with_photos = sum(1 for r in reviews if r.get("has_photo", False))
    photo_pct = with_photos / total * 100 if total > 0 else 0

    # Text length analysis
    text_lengths = [len(r.get("text", "")) for r in reviews]
    avg_text_length = sum(text_lengths) / len(text_lengths) if text_lengths else 0
    very_short = sum(1 for l in text_lengths if l < 10)
    very_short_pct = very_short / total * 100 if total > 0 else 0

    # Generic phrase detection
    all_generic = GENERIC_PHRASES_EN + GENERIC_PHRASES_ES + GENERIC_PHRASES_PT
    generic_count = 0
    for r in reviews:
        text_lower = r.get("text", "").lower()
        if any(phrase in text_lower for phrase in all_generic):
            if len(text_lower) < 30:  # Short + generic = likely fake
                generic_count += 1
    generic_pct = generic_count / total * 100 if total > 0 else 0

    # Country diversity
    countries = [r.get("buyer_country", "unknown") for r in reviews]
    country_dist = Counter(countries)
    unique_countries = len(country_dist)

    # Date clustering (many reviews on same day = suspicious)
    dates = [r.get("date", "") for r in reviews if r.get("date")]
    date_dist = Counter(dates)
    max_same_day = max(date_dist.values()) if date_dist else 0
    date_clustering_suspicious = max_same_day > max(5, total * 0.2)

    # Mexico-specific reviews
    mx_reviews = [r for r in reviews if r.get("buyer_country", "").upper() in ("MX", "MEXICO", "MÉXICO")]

    # --- Authenticity Score (0-100, higher = more authentic) ---
    auth_score = 50

    # Rating distribution analysis
    if five_star_pct > 90 and total > 20:
        auth_score -= 15  # Suspiciously all 5-star
    elif five_star_pct > 80 and total > 20:
        auth_score -= 8
    if one_star_pct > 0 and one_star_pct < 15:
        auth_score += 5  # Some negative reviews = more realistic

    # Photo analysis
    if photo_pct >= 30:
        auth_score += 15
    elif photo_pct >= 15:
        auth_score += 8
    elif photo_pct >= 5:
        auth_score += 3
    elif photo_pct == 0 and total > 20:
        auth_score -= 10

    # Text quality
    if avg_text_length > 50:
        auth_score += 10
    elif avg_text_length > 20:
        auth_score += 5
    if very_short_pct > 60:
        auth_score -= 10

    # Generic phrases
    if generic_pct > 50:
        auth_score -= 15
    elif generic_pct > 30:
        auth_score -= 8

    # Country diversity
    if unique_countries >= 10:
        auth_score += 10
    elif unique_countries >= 5:
        auth_score += 5
    elif unique_countries <= 1 and total > 10:
        auth_score -= 10

    # Date clustering
    if date_clustering_suspicious:
        auth_score -= 15

    # Volume
    if total >= 100:
        auth_score += 5
    elif total >= 50:
        auth_score += 3

    auth_score = max(0, min(100, auth_score))

    # --- Identify suspicious patterns ---
    suspicious = []
    if five_star_pct > 90 and total > 20:
        suspicious.append(f"{five_star_pct:.0f}% de reseñas son 5 estrellas — distribución sospechosamente perfecta")
    if generic_pct > 40:
        suspicious.append(f"{generic_pct:.0f}% de reseñas son genéricas y cortas — posible manipulación")
    if date_clustering_suspicious:
        suspicious.append(f"Hasta {max_same_day} reseñas en un solo día — posible compra de reseñas")
    if photo_pct == 0 and total > 20:
        suspicious.append("Ninguna reseña incluye fotos — difícil verificar producto real")
    if very_short_pct > 60:
        suspicious.append(f"{very_short_pct:.0f}% de reseñas tienen menos de 10 caracteres — baja calidad")
    if unique_countries <= 1 and total > 10:
        suspicious.append("Todas las reseñas son del mismo país — posible manipulación regional")

    # --- Identify likely real reviews ---
    real_candidates = []
    for r in reviews:
        score = 0
        text = r.get("text", "")
        if len(text) > 40:
            score += 2
        if r.get("has_photo"):
            score += 3
        if r.get("rating", 5) < 5:
            score += 1  # Non-perfect ratings more likely real
        if len(text) > 80:
            score += 2
        text_lower = text.lower()
        if not any(p in text_lower for p in all_generic):
            score += 1
        # Mentions specific details
        if any(word in text_lower for word in ["size", "color", "talla", "tamaño", "material", "peso", "weight"]):
            score += 2
        r["_authenticity_score"] = score
        if score >= 4:
            real_candidates.append(r)

    real_candidates.sort(key=lambda x: x["_authenticity_score"], reverse=True)

    # --- Verdict ---
    if auth_score >= 70:
        verdict = "Reseñas mayormente auténticas"
    elif auth_score >= 50:
        verdict = "Mezcla de reseñas reales y sospechosas"
    elif auth_score >= 30:
        verdict = "Muchas reseñas parecen falsas o manipuladas"
    else:
        verdict = "Reseñas altamente sospechosas — probable manipulación masiva"

    return {
        "total_reviews": total,
        "avg_rating": round(avg_rating, 2),
        "rating_distribution": dict(rating_dist),
        "five_star_pct": round(five_star_pct, 1),
        "reviews_with_photos": with_photos,
        "photo_pct": round(photo_pct, 1),
        "avg_text_length": round(avg_text_length, 1),
        "generic_review_pct": round(generic_pct, 1),
        "unique_countries": unique_countries,
        "country_distribution": dict(country_dist.most_common(10)),
        "mx_reviews_count": len(mx_reviews),
        "date_clustering_suspicious": date_clustering_suspicious,
        "authenticity_score": auth_score,
        "verdict": verdict,
        "suspicious_patterns": suspicious,
        "real_review_candidates": [
            {
                "rating": r.get("rating"),
                "text": r.get("text", "")[:200],
                "has_photo": r.get("has_photo", False),
                "country": r.get("buyer_country", "N/D"),
            }
            for r in real_candidates[:10]
        ],
    }


def main():
    if len(sys.argv) < 2:
        print("Uso: python analyze_reviews.py <reviews_file.json>")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"Error: No se encontró '{filepath}'")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        reviews = json.load(f)

    result = analyze_reviews(reviews)

    output_path = filepath.replace(".json", "_analysis.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n--- Análisis guardado en: {output_path} ---")


if __name__ == "__main__":
    main()
