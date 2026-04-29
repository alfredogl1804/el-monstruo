#!/usr/bin/env python3.11
"""
quality_gate.py — Filtro de Calidad para Respuestas de los Sabios
==================================================================
Evalúa cada respuesta y la clasifica en: ok, weak, poor, insufficient.
Las respuestas poor/insufficient se excluyen o se reducen en peso
durante la síntesis final.

Criterios:
    1. Longitud mínima útil
    2. Presencia de estructura (headers, listas, párrafos)
    3. Densidad informativa (ratio contenido/relleno)
    4. Detección de evasión ("no puedo responder", "como modelo de IA")
    5. Alineación básica con la pregunta (keywords compartidos)
    6. Detección de repetición excesiva

Uso:
    from quality_gate import evaluate_response, evaluate_all, filter_quality

    score = evaluate_response(respuesta_text, pregunta_text)
    # score = {"grade": "ok", "score": 0.85, "reasons": [...], ...}

    results = evaluate_all(resultados_sabios, pregunta_text)
    filtered = filter_quality(resultados_sabios, pregunta_text, min_grade="weak")

Creado: 2026-04-08 (P0 auditoría sabios)
"""

import re
from typing import Optional


# ═══════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════

# Longitud mínima para considerar una respuesta útil (caracteres)
MIN_LENGTH_OK = 500
MIN_LENGTH_WEAK = 200

# Patrones de evasión
EVASION_PATTERNS = [
    r"no puedo responder",
    r"como modelo de (?:ia|lenguaje|inteligencia artificial)",
    r"as an ai",
    r"i cannot",
    r"i'm not able to",
    r"no tengo acceso",
    r"no tengo la capacidad",
    r"fuera de mi alcance",
    r"no me es posible",
    r"lamento no poder",
    r"sorry,? i can'?t",
    r"i don'?t have (?:access|the ability)",
]

# Patrones de relleno/padding
FILLER_PATTERNS = [
    r"(?:es importante|cabe (?:destacar|mencionar|señalar|notar))",
    r"(?:en este sentido|en este contexto|en este orden de ideas)",
    r"(?:sin lugar a dudas|sin duda alguna)",
    r"(?:como se mencionó anteriormente|como ya se dijo)",
    r"(?:es fundamental|es crucial|es esencial) (?:tener en cuenta|considerar|mencionar)",
]

# Grades y sus umbrales
GRADE_THRESHOLDS = {
    "ok": 0.60,
    "weak": 0.35,
    "poor": 0.15,
    # below 0.15 = "insufficient"
}


# ═══════════════════════════════════════════════════════════════════
# EVALUACIÓN INDIVIDUAL
# ═══════════════════════════════════════════════════════════════════

def evaluate_response(
    respuesta: str,
    pregunta: str = "",
    sabio_id: str = "unknown",
) -> dict:
    """
    Evalúa una respuesta individual y retorna un score detallado.

    Returns:
        dict con: sabio_id, grade, score (0-1), subscores, reasons, recommendation
    """
    if not respuesta or not respuesta.strip():
        return {
            "sabio_id": sabio_id,
            "grade": "insufficient",
            "score": 0.0,
            "subscores": {},
            "reasons": ["Respuesta vacía"],
            "recommendation": "exclude",
        }

    subscores = {}
    reasons = []

    # 1. Longitud
    length = len(respuesta.strip())
    if length >= MIN_LENGTH_OK * 3:
        subscores["length"] = 1.0
    elif length >= MIN_LENGTH_OK:
        subscores["length"] = 0.7
    elif length >= MIN_LENGTH_WEAK:
        subscores["length"] = 0.4
        reasons.append(f"Respuesta corta ({length} chars)")
    else:
        subscores["length"] = 0.1
        reasons.append(f"Respuesta muy corta ({length} chars)")

    # 2. Estructura
    headers = len(re.findall(r"^#{1,4}\s", respuesta, re.MULTILINE))
    lists = len(re.findall(r"^[\s]*[-*\d+\.]\s", respuesta, re.MULTILINE))
    paragraphs = len([p for p in respuesta.split("\n\n") if len(p.strip()) > 50])
    tables = len(re.findall(r"\|.*\|.*\|", respuesta))
    code_blocks = len(re.findall(r"```", respuesta)) // 2

    structure_signals = headers + lists // 3 + paragraphs + tables + code_blocks
    if structure_signals >= 8:
        subscores["structure"] = 1.0
    elif structure_signals >= 4:
        subscores["structure"] = 0.7
    elif structure_signals >= 2:
        subscores["structure"] = 0.4
    else:
        subscores["structure"] = 0.2
        reasons.append("Poca estructura (sin headers, listas o tablas)")

    # 3. Evasión
    evasion_count = 0
    for pattern in EVASION_PATTERNS:
        evasion_count += len(re.findall(pattern, respuesta, re.IGNORECASE))

    if evasion_count == 0:
        subscores["evasion"] = 1.0
    elif evasion_count <= 1:
        subscores["evasion"] = 0.6
        reasons.append("Posible evasión parcial detectada")
    else:
        subscores["evasion"] = 0.1
        reasons.append(f"Evasión detectada ({evasion_count} patrones)")

    # 4. Densidad (ratio contenido vs relleno)
    filler_count = 0
    for pattern in FILLER_PATTERNS:
        filler_count += len(re.findall(pattern, respuesta, re.IGNORECASE))

    words = len(respuesta.split())
    filler_ratio = filler_count / max(words / 100, 1)  # fillers per 100 words
    if filler_ratio < 1:
        subscores["density"] = 1.0
    elif filler_ratio < 3:
        subscores["density"] = 0.7
    elif filler_ratio < 6:
        subscores["density"] = 0.4
        reasons.append("Exceso de relleno/padding")
    else:
        subscores["density"] = 0.2
        reasons.append("Relleno excesivo, baja densidad informativa")

    # 5. Alineación con la pregunta
    if pregunta:
        pregunta_words = set(
            w.lower() for w in re.findall(r"\b\w{4,}\b", pregunta)
        )
        respuesta_words = set(
            w.lower() for w in re.findall(r"\b\w{4,}\b", respuesta)
        )
        if pregunta_words:
            overlap = len(pregunta_words & respuesta_words) / len(pregunta_words)
            subscores["alignment"] = min(1.0, overlap * 2)  # 50% overlap = 1.0
            if overlap < 0.15:
                reasons.append("Baja alineación con la pregunta")
        else:
            subscores["alignment"] = 0.5
    else:
        subscores["alignment"] = 0.5  # No se puede evaluar sin pregunta

    # 6. Repetición
    sentences = [s.strip() for s in re.split(r"[.!?]\s", respuesta) if len(s.strip()) > 20]
    if sentences:
        unique_ratio = len(set(sentences)) / len(sentences)
        subscores["repetition"] = unique_ratio
        if unique_ratio < 0.7:
            reasons.append(f"Repetición excesiva ({1-unique_ratio:.0%} duplicado)")
    else:
        subscores["repetition"] = 0.5

    # Score final (promedio ponderado)
    weights = {
        "length": 0.15,
        "structure": 0.15,
        "evasion": 0.25,
        "density": 0.15,
        "alignment": 0.15,
        "repetition": 0.15,
    }

    score = sum(subscores.get(k, 0.5) * w for k, w in weights.items())

    # Determinar grade
    if score >= GRADE_THRESHOLDS["ok"]:
        grade = "ok"
    elif score >= GRADE_THRESHOLDS["weak"]:
        grade = "weak"
    elif score >= GRADE_THRESHOLDS["poor"]:
        grade = "poor"
    else:
        grade = "insufficient"

    # Recomendación
    if grade == "ok":
        recommendation = "include"
    elif grade == "weak":
        recommendation = "include_reduced_weight"
    elif grade == "poor":
        recommendation = "exclude_from_synthesis"
    else:
        recommendation = "exclude"

    if not reasons:
        reasons.append("Respuesta de calidad aceptable")

    return {
        "sabio_id": sabio_id,
        "grade": grade,
        "score": round(score, 3),
        "subscores": {k: round(v, 3) for k, v in subscores.items()},
        "reasons": reasons,
        "recommendation": recommendation,
        "chars": length,
        "words": words,
    }


# ═══════════════════════════════════════════════════════════════════
# EVALUACIÓN BATCH
# ═══════════════════════════════════════════════════════════════════

def evaluate_all(resultados: list, pregunta: str = "") -> list:
    """
    Evalúa todas las respuestas de los sabios.

    Args:
        resultados: Lista de dicts con 'sabio_id', 'respuesta', 'exito'
        pregunta: Texto de la pregunta original

    Returns:
        Lista de evaluaciones
    """
    evaluaciones = []
    for r in resultados:
        if not r.get("exito"):
            evaluaciones.append({
                "sabio_id": r.get("sabio_id", "unknown"),
                "grade": "insufficient",
                "score": 0.0,
                "subscores": {},
                "reasons": [f"No respondió: {r.get('error', 'Error desconocido')[:100]}"],
                "recommendation": "exclude",
                "chars": 0,
                "words": 0,
            })
        else:
            evaluaciones.append(evaluate_response(
                respuesta=r.get("respuesta", ""),
                pregunta=pregunta,
                sabio_id=r.get("sabio_id", "unknown"),
            ))
    return evaluaciones


def filter_quality(
    resultados: list,
    pregunta: str = "",
    min_grade: str = "weak",
) -> list:
    """
    Filtra resultados por calidad mínima.

    Args:
        resultados: Lista de resultados de sabios
        pregunta: Texto de la pregunta
        min_grade: Grade mínimo para incluir ("ok", "weak", "poor")

    Returns:
        Lista filtrada de resultados que pasan el quality gate
    """
    grade_order = ["insufficient", "poor", "weak", "ok"]
    min_idx = grade_order.index(min_grade)

    evaluaciones = evaluate_all(resultados, pregunta)
    filtered = []

    for r, ev in zip(resultados, evaluaciones):
        grade_idx = grade_order.index(ev["grade"])
        if grade_idx >= min_idx:
            filtered.append(r)

    return filtered


def quality_summary(evaluaciones: list) -> str:
    """Genera un resumen legible de las evaluaciones de calidad."""
    lines = ["# Quality Gate — Evaluación de Respuestas\n"]

    grades_count = {"ok": 0, "weak": 0, "poor": 0, "insufficient": 0}
    for ev in evaluaciones:
        grades_count[ev["grade"]] += 1

    lines.append(f"**Total:** {len(evaluaciones)} respuestas evaluadas")
    lines.append(f"- OK: {grades_count['ok']}")
    lines.append(f"- Weak: {grades_count['weak']}")
    lines.append(f"- Poor: {grades_count['poor']}")
    lines.append(f"- Insufficient: {grades_count['insufficient']}")
    lines.append("")

    lines.append("| Sabio | Grade | Score | Chars | Recomendación | Razones |")
    lines.append("|-------|-------|-------|-------|---------------|---------|")
    for ev in evaluaciones:
        grade_icon = {"ok": "✅", "weak": "⚠️", "poor": "🔶", "insufficient": "❌"}
        icon = grade_icon.get(ev["grade"], "?")
        reasons_short = "; ".join(ev["reasons"][:2])
        lines.append(
            f"| {ev['sabio_id']} | {icon} {ev['grade']} | {ev['score']:.2f} | "
            f"{ev.get('chars', 0):,} | {ev['recommendation']} | {reasons_short} |"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    # Test rápido con ejemplo
    test_response = """
# Análisis de la Arquitectura

## 1. Fortalezas

La arquitectura presenta varios puntos fuertes:
- Separación clara de responsabilidades
- Conectores inmutables y probados
- Capa de investigación en tiempo real

## 2. Debilidades

Sin embargo, hay áreas de mejora:
- Falta telemetría estructurada
- El parseo JSON es frágil
- No hay quality gate para respuestas

## 3. Recomendaciones

1. Implementar telemetría desde el día uno
2. Añadir validación de schema JSON
3. Crear un quality gate básico
"""
    test_question = "Audita la skill consulta-sabios y diseña un mecanismo de mejora perpetua"

    result = evaluate_response(test_response, test_question, "test_sabio")
    print(f"Grade: {result['grade']}")
    print(f"Score: {result['score']}")
    print(f"Subscores: {result['subscores']}")
    print(f"Reasons: {result['reasons']}")
    print(f"Recommendation: {result['recommendation']}")
