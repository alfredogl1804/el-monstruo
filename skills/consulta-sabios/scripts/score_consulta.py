#!/usr/bin/env python3.11
"""
score_consulta.py — Scoring Avanzado de Consultas
===================================================
Calcula métricas de calidad para un run completo:
- Score por sabio (quality_gate)
- Factualidad (basada en informe_validacion.md)
- Cobertura (qué % de temas del prompt fueron abordados)
- Consenso (nivel de acuerdo entre sabios)
- Contradicciones (afirmaciones mutuamente excluyentes)
- Score de síntesis

Uso:
    python3.11 score_consulta.py \\
        --run-dir /ruta/al/run/ \\
        --prompt-original /ruta/prompt.md

Creado: 2026-04-08 (P1 auditoría sabios)
"""

import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conector_sabios import consultar_sabio
from telemetry import write_run_artifact, estimate_tokens


# ═══════════════════════════════════════════════════════════════
# SCORING ENGINE
# ═══════════════════════════════════════════════════════════════

async def score_consulta(
    run_dir: str,
    prompt_original: str = None,
) -> dict:
    """
    Calcula scores completos para un run.
    
    Returns:
        dict con scores: factualidad, cobertura, consenso, contradicciones,
        sintesis_quality, score_global, detalle_por_sabio
    """
    run_dir = Path(run_dir)
    scores = {
        "timestamp": datetime.now().isoformat(),
        "factualidad": 0.0,
        "cobertura": 0.0,
        "consenso": 0.0,
        "contradicciones": 0,
        "sintesis_quality": 0.0,
        "score_global": 0.0,
        "detalle_por_sabio": {},
        "metodo": "hybrid",  # heuristic + llm
    }

    # ─── 1. Cargar artefactos del run ─────────────────────────
    output_dir = run_dir / "output"
    
    # Respuestas individuales
    respuestas = {}
    for f in sorted(output_dir.glob("resp_*.md")) if output_dir.exists() else []:
        sabio_id = f.stem.replace("resp_", "")
        respuestas[sabio_id] = f.read_text(encoding="utf-8")
    
    # Buscar también en JSON
    for f in sorted(output_dir.glob("resp_*.json")) if output_dir.exists() else []:
        sabio_id = f.stem.replace("resp_", "")
        if sabio_id not in respuestas:
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                respuestas[sabio_id] = data.get("respuesta", "")
            except Exception:
                pass

    if not respuestas:
        # Intentar desde el directorio raíz del run
        for f in sorted(run_dir.glob("resp_*.md")):
            sabio_id = f.stem.replace("resp_", "")
            respuestas[sabio_id] = f.read_text(encoding="utf-8")

    informe_validacion = ""
    for candidate in [output_dir / "informe_validacion.md", run_dir / "informe_validacion.md"]:
        if candidate.exists():
            informe_validacion = candidate.read_text(encoding="utf-8")
            break

    sintesis = ""
    for candidate in [output_dir / "sintesis_final.md", run_dir / "sintesis_final.md"]:
        if candidate.exists():
            sintesis = candidate.read_text(encoding="utf-8")
            break

    prompt_text = ""
    if prompt_original and Path(prompt_original).exists():
        prompt_text = Path(prompt_original).read_text(encoding="utf-8")
    else:
        for candidate in [run_dir / "input" / "prompt.md", run_dir / "prompt.md"]:
            if candidate.exists():
                prompt_text = candidate.read_text(encoding="utf-8")
                break

    if not respuestas:
        print("⚠️  No se encontraron respuestas de sabios en el run")
        return scores

    print(f"📊 Scoring run: {run_dir.name}")
    print(f"   Sabios con respuesta: {len(respuestas)} ({', '.join(respuestas.keys())})")
    print(f"   Informe validación: {'✅' if informe_validacion else '❌'}")
    print(f"   Síntesis: {'✅' if sintesis else '❌'}")

    # ─── 2. Factualidad (basada en informe de validación) ─────
    if informe_validacion:
        scores["factualidad"] = _score_factualidad(informe_validacion)
    else:
        scores["factualidad"] = -1  # No evaluable

    # ─── 3. Cobertura (temas del prompt abordados) ────────────
    if prompt_text and respuestas:
        scores["cobertura"] = await _score_cobertura(prompt_text, respuestas)

    # ─── 4. Consenso y contradicciones ────────────────────────
    if len(respuestas) >= 2:
        consenso_result = await _score_consenso(respuestas, prompt_text)
        scores["consenso"] = consenso_result.get("consenso", 0.0)
        scores["contradicciones"] = consenso_result.get("contradicciones", 0)

    # ─── 5. Score de síntesis ─────────────────────────────────
    if sintesis:
        scores["sintesis_quality"] = _score_sintesis_heuristic(sintesis, respuestas)

    # ─── 6. Detalle por sabio ─────────────────────────────────
    for sabio_id, resp in respuestas.items():
        scores["detalle_por_sabio"][sabio_id] = {
            "chars": len(resp),
            "tokens_est": estimate_tokens(resp),
            "tiene_estructura": bool(re.search(r'^#{1,3}\s', resp, re.MULTILINE)),
            "tiene_listas": bool(re.search(r'^[\-\*\d]+[\.\)]\s', resp, re.MULTILINE)),
            "tiene_tablas": '|' in resp and '---' in resp,
            "tiene_codigo": '```' in resp,
            "densidad_info": _densidad_informativa(resp),
        }

    # ─── 7. Score global ─────────────────────────────────────
    componentes = []
    pesos = []
    
    if scores["factualidad"] >= 0:
        componentes.append(scores["factualidad"])
        pesos.append(0.30)
    
    if scores["cobertura"] > 0:
        componentes.append(scores["cobertura"])
        pesos.append(0.25)
    
    if scores["consenso"] > 0:
        componentes.append(scores["consenso"])
        pesos.append(0.20)
    
    if scores["sintesis_quality"] > 0:
        componentes.append(scores["sintesis_quality"])
        pesos.append(0.25)

    if componentes:
        total_peso = sum(pesos)
        scores["score_global"] = round(
            sum(c * p for c, p in zip(componentes, pesos)) / total_peso, 3
        )

    # ─── 8. Persistir ────────────────────────────────────────
    write_run_artifact(run_dir, "scores.json", scores)
    
    # Generar reporte legible
    report = _generar_reporte(scores, respuestas)
    write_run_artifact(run_dir, "output/score_report.md", report)

    print(f"\n📊 SCORES FINALES:")
    print(f"   Factualidad:    {scores['factualidad']:.2f}" if scores['factualidad'] >= 0 else "   Factualidad:    N/A")
    print(f"   Cobertura:      {scores['cobertura']:.2f}")
    print(f"   Consenso:       {scores['consenso']:.2f}")
    print(f"   Contradicciones: {scores['contradicciones']}")
    print(f"   Síntesis:       {scores['sintesis_quality']:.2f}")
    print(f"   ═══════════════════")
    print(f"   SCORE GLOBAL:   {scores['score_global']:.2f}")

    return scores


# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE SCORING
# ═══════════════════════════════════════════════════════════════

def _score_factualidad(informe: str) -> float:
    """
    Extrae tasa de factualidad del informe de validación.
    Busca patrones como "X/Y verificadas", "X% correctas", etc.
    """
    # Buscar patrón "N de M" o "N/M"
    matches = re.findall(r'(\d+)\s*(?:de|/)\s*(\d+)\s*(?:verificad|correct|confirm|valid)', informe, re.IGNORECASE)
    if matches:
        total_ok = sum(int(m[0]) for m in matches)
        total = sum(int(m[1]) for m in matches)
        if total > 0:
            return round(total_ok / total, 3)

    # Buscar porcentaje directo
    pct_matches = re.findall(r'(\d+(?:\.\d+)?)\s*%\s*(?:verificad|correct|factual|confirm)', informe, re.IGNORECASE)
    if pct_matches:
        return round(float(pct_matches[0]) / 100, 3)

    # Heurística: contar ✅ vs ❌ vs ⚠️
    ok = informe.count('✅') + informe.count('confirmad') + informe.count('verificad')
    fail = informe.count('❌') + informe.count('incorrect') + informe.count('falso')
    warn = informe.count('⚠️') + informe.count('parcial')
    
    total = ok + fail + warn
    if total > 0:
        return round((ok + warn * 0.5) / total, 3)

    return 0.5  # Default neutral si no se puede determinar


async def _score_cobertura(prompt: str, respuestas: dict) -> float:
    """
    Usa GPT-5.4 para evaluar qué % de los temas del prompt fueron cubiertos.
    """
    respuestas_concat = "\n\n---\n\n".join(
        f"**{sid}:** {resp[:2000]}" for sid, resp in respuestas.items()
    )

    eval_prompt = f"""Evalúa la COBERTURA de las respuestas respecto a la pregunta original.

PREGUNTA ORIGINAL:
{prompt[:3000]}

RESUMEN DE RESPUESTAS (primeros 2000 chars de cada una):
{respuestas_concat[:8000]}

Responde SOLO con un JSON:
```json
{{"cobertura": 0.XX, "temas_cubiertos": N, "temas_totales": M, "temas_faltantes": ["tema1", "tema2"]}}
```

Donde cobertura es un float entre 0.0 y 1.0."""

    try:
        resultado = await consultar_sabio(
            sabio_id="gpt54",
            prompt=eval_prompt,
            system="Eres un evaluador de calidad. Responde solo con JSON válido.",
            reintentos=1,
        )
        if resultado["exito"]:
            data = _parse_json_safe(resultado["respuesta"])
            if data and "cobertura" in data:
                return round(float(data["cobertura"]), 3)
    except Exception as e:
        print(f"⚠️  Error evaluando cobertura con LLM: {e}")

    # Fallback heurístico
    return _cobertura_heuristica(prompt, respuestas)


def _cobertura_heuristica(prompt: str, respuestas: dict) -> float:
    """Heurística de cobertura basada en keywords del prompt."""
    # Extraer palabras clave del prompt (>5 chars, no stopwords)
    stopwords = {"sobre", "entre", "desde", "hasta", "para", "como", "cuando", "donde",
                 "porque", "cuáles", "cuales", "cuánto", "cuanto", "tiene", "tienen",
                 "puede", "pueden", "deben", "debería", "which", "about", "their"}
    words = set(
        w.lower() for w in re.findall(r'\b\w{5,}\b', prompt)
        if w.lower() not in stopwords
    )
    
    if not words:
        return 0.5

    all_resp = " ".join(respuestas.values()).lower()
    found = sum(1 for w in words if w in all_resp)
    return round(found / len(words), 3)


async def _score_consenso(respuestas: dict, prompt: str) -> dict:
    """
    Evalúa nivel de consenso y contradicciones entre sabios.
    """
    sabios_text = "\n\n---\n\n".join(
        f"**{sid}:** {resp[:3000]}" for sid, resp in respuestas.items()
    )

    eval_prompt = f"""Analiza el CONSENSO y CONTRADICCIONES entre estas respuestas de diferentes IAs.

PREGUNTA:
{prompt[:2000]}

RESPUESTAS (primeros 3000 chars):
{sabios_text[:12000]}

Responde SOLO con JSON:
```json
{{"consenso": 0.XX, "contradicciones": N, "puntos_consenso": ["punto1"], "puntos_divergencia": ["punto1"]}}
```

Donde consenso es 0.0 (total desacuerdo) a 1.0 (acuerdo total)."""

    try:
        resultado = await consultar_sabio(
            sabio_id="gpt54",
            prompt=eval_prompt,
            system="Eres un evaluador de consenso. Responde solo con JSON válido.",
            reintentos=1,
        )
        if resultado["exito"]:
            data = _parse_json_safe(resultado["respuesta"])
            if data and "consenso" in data:
                return {
                    "consenso": round(float(data["consenso"]), 3),
                    "contradicciones": int(data.get("contradicciones", 0)),
                }
    except Exception as e:
        print(f"⚠️  Error evaluando consenso con LLM: {e}")

    # Fallback: consenso neutral
    return {"consenso": 0.5, "contradicciones": 0}


def _score_sintesis_heuristic(sintesis: str, respuestas: dict) -> float:
    """
    Evalúa calidad de la síntesis con heurísticas.
    """
    score = 0.0
    checks = 0

    # 1. Longitud razonable (al menos 20% del total de respuestas)
    total_resp_chars = sum(len(r) for r in respuestas.values())
    if total_resp_chars > 0:
        ratio = len(sintesis) / total_resp_chars
        if 0.15 <= ratio <= 0.80:
            score += 1.0
        elif ratio > 0.80:
            score += 0.5  # Demasiado larga, posible copy-paste
        else:
            score += 0.3  # Demasiado corta
        checks += 1

    # 2. Estructura (headers, secciones)
    headers = len(re.findall(r'^#{1,3}\s', sintesis, re.MULTILINE))
    if headers >= 5:
        score += 1.0
    elif headers >= 3:
        score += 0.7
    else:
        score += 0.3
    checks += 1

    # 3. Menciona a los sabios / fuentes
    sabios_mencionados = sum(1 for sid in respuestas if sid.lower() in sintesis.lower())
    if sabios_mencionados >= len(respuestas) * 0.5:
        score += 1.0
    elif sabios_mencionados >= 2:
        score += 0.6
    else:
        score += 0.2
    checks += 1

    # 4. Tiene tabla de consenso/divergencia
    if '|' in sintesis and ('consenso' in sintesis.lower() or 'divergen' in sintesis.lower()):
        score += 1.0
    else:
        score += 0.4
    checks += 1

    # 5. Tiene próximos pasos / acción
    if re.search(r'(próximos pasos|next steps|acción|roadmap|recomendacion)', sintesis, re.IGNORECASE):
        score += 1.0
    else:
        score += 0.3
    checks += 1

    return round(score / checks, 3) if checks > 0 else 0.0


def _densidad_informativa(text: str) -> float:
    """Ratio de palabras únicas significativas vs total de palabras."""
    words = re.findall(r'\b\w{4,}\b', text.lower())
    if not words:
        return 0.0
    unique = len(set(words))
    return round(unique / len(words), 3)


def _parse_json_safe(text: str) -> dict:
    """Parser JSON robusto — extrae JSON de texto con markdown."""
    # Intentar extraer de bloque ```json
    json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Intentar extraer objeto JSON directo
    brace_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def _generar_reporte(scores: dict, respuestas: dict) -> str:
    """Genera un reporte Markdown legible de los scores."""
    lines = [
        "# Score Report — Consulta a los Sabios",
        f"\nFecha: {scores['timestamp']}",
        f"\n## Scores Globales\n",
        f"| Métrica | Score |",
        f"|---------|-------|",
        f"| Factualidad | {scores['factualidad']:.2f} |" if scores['factualidad'] >= 0 else "| Factualidad | N/A |",
        f"| Cobertura | {scores['cobertura']:.2f} |",
        f"| Consenso | {scores['consenso']:.2f} |",
        f"| Contradicciones | {scores['contradicciones']} |",
        f"| Calidad Síntesis | {scores['sintesis_quality']:.2f} |",
        f"| **Score Global** | **{scores['score_global']:.2f}** |",
        f"\n## Detalle por Sabio\n",
        f"| Sabio | Chars | Tokens Est. | Estructura | Densidad |",
        f"|-------|-------|-------------|------------|----------|",
    ]

    for sabio_id, detail in scores.get("detalle_por_sabio", {}).items():
        struct = "✅" if detail.get("tiene_estructura") else "❌"
        lines.append(
            f"| {sabio_id} | {detail.get('chars', 0):,} | {detail.get('tokens_est', 0):,} | {struct} | {detail.get('densidad_info', 0):.2f} |"
        )

    return "\n".join(lines) + "\n"


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

async def main():
    parser = argparse.ArgumentParser(description="Score avanzado de consultas a los sabios")
    parser.add_argument("--run-dir", required=True, help="Directorio del run a evaluar")
    parser.add_argument("--prompt-original", default=None, help="Ruta al prompt original")

    args = parser.parse_args()
    scores = await score_consulta(args.run_dir, args.prompt_original)

    if scores["score_global"] > 0:
        print(f"\n✅ Scoring completado: {scores['score_global']:.2f}")
    else:
        print(f"\n⚠️  Scoring incompleto — faltan artefactos")


if __name__ == "__main__":
    asyncio.run(main())
