#!/usr/bin/env python3.11
"""
propose_improvements.py — Motor de Propuesta de Mejoras Automáticas
====================================================================
Analiza el historial de consultas y propone mejoras concretas:
- Ajustes de timeouts basados en latencia real
- Cambios de modelo si un sabio degrada
- Ajustes de prompts si cobertura/consenso bajan
- Nuevas reglas de quality gate
- Optimizaciones de contexto

Uso:
    python3.11 propose_improvements.py [--min-runs 5] [--output proposals.json]

Creado: 2026-04-08 (P2 auditoría sabios)
"""

import argparse
import asyncio
import json
import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyze_history import analyze
from conector_sabios import consultar_sabio
from config_loader import get_config
from db_store import query_improvements, save_improvement


async def propose_improvements(min_runs: int = 5) -> list:
    """
    Analiza historial y genera propuestas de mejora.

    Returns:
        list de propuestas, cada una con:
        - improvement_id, tipo, descripcion, prioridad, diff, confianza
    """
    analysis = analyze(last_n=100)
    proposals = []

    if analysis["runs_analizados"] < min_runs:
        print(f"⚠️  Solo {analysis['runs_analizados']} runs (mínimo: {min_runs}). Insuficiente para propuestas.")
        return proposals

    print(f"📊 Analizando {analysis['runs_analizados']} runs para propuestas de mejora...")

    # ─── 1. Propuestas basadas en reglas ──────────────────────
    proposals.extend(_rule_based_proposals(analysis))

    # ─── 2. Propuestas basadas en LLM ────────────────────────
    llm_proposals = await _llm_based_proposals(analysis)
    proposals.extend(llm_proposals)

    # ─── 3. Deduplicar contra mejoras ya propuestas ──────────
    existing = query_improvements()
    existing_descs = {i.get("descripcion", "").lower() for i in existing}
    proposals = [p for p in proposals if p["descripcion"].lower() not in existing_descs]

    # ─── 4. Persistir propuestas ─────────────────────────────
    for p in proposals:
        p["improvement_id"] = f"imp_{uuid.uuid4().hex[:8]}"
        p["estado"] = "propuesta"
        p["fuente"] = f"analyze_{analysis['runs_analizados']}_runs"
        save_improvement(p)

    print(f"\n✅ {len(proposals)} propuestas generadas")
    for p in proposals:
        print(f"  [{p['prioridad']}] {p['tipo']}: {p['descripcion']}")

    return proposals


def _rule_based_proposals(analysis: dict) -> list:
    """Genera propuestas basadas en reglas determinísticas."""
    proposals = []
    config = get_config()

    # Regla 1: Sabio con success rate < 60% → proponer timeout mayor o modelo alternativo
    for sid, metrics in analysis.get("metricas_por_sabio", {}).items():
        sr = metrics.get("success_rate", 1)
        total = metrics.get("total_consultas", 0)

        if sr < 0.6 and total >= 3:
            # Analizar tipo de error predominante
            errores = metrics.get("errores", {})
            if errores.get("timeout", 0) > errores.get("rate_limit", 0):
                proposals.append(
                    {
                        "tipo": "config",
                        "descripcion": f"Aumentar timeout de {sid} (success rate: {sr:.0%}, errores predominantes: timeout)",
                        "prioridad": "alta",
                        "diff": {
                            "file": "config/skill_config.yaml",
                            "cambio": f"timeouts.{sid}: aumentar 50%",
                        },
                        "confianza": 0.85,
                        "basado_en": f"{total} consultas, {sr:.0%} success rate",
                    }
                )
            elif errores.get("context_overflow", 0) > 0:
                proposals.append(
                    {
                        "tipo": "config",
                        "descripcion": f"Reducir presupuesto de contexto para {sid} (context_overflow frecuente)",
                        "prioridad": "alta",
                        "diff": {
                            "file": "config/skill_config.yaml",
                            "cambio": f"contexto.presupuesto_por_sabio.{sid}: reducir 20%",
                        },
                        "confianza": 0.90,
                        "basado_en": f"{errores.get('context_overflow', 0)} context overflows",
                    }
                )

    # Regla 2: Latencia p95 > 5 min → proponer timeout más agresivo
    p95 = analysis.get("metricas_globales", {}).get("duracion_p95_ms", 0)
    if p95 > 300000:
        proposals.append(
            {
                "tipo": "config",
                "descripcion": f"Reducir timeout global (p95 actual: {p95 / 1000:.0f}s, objetivo: <300s)",
                "prioridad": "media",
                "diff": {
                    "file": "config/skill_config.yaml",
                    "cambio": "timeouts: reducir proporcionalmente",
                },
                "confianza": 0.70,
                "basado_en": f"p95={p95 / 1000:.0f}s",
            }
        )

    # Regla 3: Tendencia degradante → alerta y propuesta de investigación
    tendencias = analysis.get("tendencias", {})
    if tendencias.get("success_rate_tendencia") == "degradando":
        proposals.append(
            {
                "tipo": "workflow",
                "descripcion": "Investigar causa de degradación de success rate (tendencia negativa detectada)",
                "prioridad": "alta",
                "diff": {
                    "accion": "Ejecutar diagnóstico detallado por sabio",
                },
                "confianza": 0.95,
                "basado_en": f"SR: {tendencias.get('success_rate_primera_mitad', 0):.0%} → {tendencias.get('success_rate_segunda_mitad', 0):.0%}",
            }
        )

    # Regla 4: Error recurrente específico → propuesta específica
    for error_type, count in analysis.get("errores_frecuentes", {}).items():
        if count >= 5:
            if error_type == "rate_limit":
                proposals.append(
                    {
                        "tipo": "config",
                        "descripcion": f"Reducir concurrencia (rate_limit ocurrió {count} veces)",
                        "prioridad": "media",
                        "diff": {
                            "file": "config/skill_config.yaml",
                            "cambio": "concurrencia: reducir valores",
                        },
                        "confianza": 0.80,
                        "basado_en": f"{count} rate limits",
                    }
                )

    return proposals


async def _llm_based_proposals(analysis: dict) -> list:
    """Usa GPT-5.4 para generar propuestas más sofisticadas."""
    proposals = []

    # Preparar resumen para el LLM
    summary = json.dumps(
        {
            "metricas_globales": analysis.get("metricas_globales", {}),
            "metricas_por_sabio": analysis.get("metricas_por_sabio", {}),
            "tendencias": analysis.get("tendencias", {}),
            "errores_frecuentes": analysis.get("errores_frecuentes", {}),
            "alertas": [a["mensaje"] for a in analysis.get("alertas", [])],
        },
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""Analiza estas métricas del sistema "consulta-sabios" y propón mejoras concretas.

MÉTRICAS:
{summary}

Propón mejoras CONCRETAS y ACCIONABLES. Cada propuesta debe ser:
- Específica (qué cambiar exactamente)
- Medible (cómo saber si funcionó)
- Realizable (cambio en config, prompt, o script)

Responde SOLO con JSON:
```json
[
  {{
    "tipo": "config|prompt|script|workflow",
    "descripcion": "descripción concreta",
    "prioridad": "alta|media|baja",
    "diff": {{"file": "archivo", "cambio": "qué cambiar"}},
    "confianza": 0.0-1.0,
    "metrica_objetivo": "qué métrica mejorar"
  }}
]
```"""

    try:
        resultado = await consultar_sabio(
            sabio_id="gpt54",
            prompt=prompt,
            system="Eres un ingeniero de ML/Ops experto en optimización de sistemas multi-agente. Responde solo con JSON.",
            reintentos=1,
        )
        if resultado["exito"]:
            from json_parser import parse_json

            data = parse_json(resultado["respuesta"])
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "descripcion" in item:
                        item["origen"] = "llm"
                        proposals.append(item)
    except Exception as e:
        print(f"⚠️  Error generando propuestas LLM: {e}")

    return proposals


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════


async def main():
    parser = argparse.ArgumentParser(description="Proponer mejoras automáticas")
    parser.add_argument("--min-runs", type=int, default=5)
    parser.add_argument("--output", default=None)

    args = parser.parse_args()
    proposals = await propose_improvements(args.min_runs)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(proposals, f, ensure_ascii=False, indent=2, default=str)
        print(f"📁 Propuestas guardadas en: {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
