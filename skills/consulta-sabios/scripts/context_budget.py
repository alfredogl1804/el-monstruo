#!/usr/bin/env python3.11
"""
context_budget.py — Presupuesto Automático de Contexto por Sabio
=================================================================
Estima tokens y gestiona el presupuesto de contexto para cada sabio,
evitando truncados y errores de context_overflow.

Funciones públicas:
    - estimate_tokens_accurate(text) → int (mejor estimación)
    - get_budget(sabio_id) → dict con límites
    - check_fits(sabio_id, text) → (bool, info)
    - prepare_context(sabio_id, prompt, dossier, extras) → str optimizado
    - budget_report(texts_by_sabio) → str reporte

Creado: 2026-04-08 (P1 auditoría sabios)
"""

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_loader import get_context_budget, get_sabio_config


# ═══════════════════════════════════════════════════════════════
# ESTIMACIÓN DE TOKENS
# ═══════════════════════════════════════════════════════════════

# Ratios chars/token por idioma/tipo de contenido
RATIOS = {
    "english": 4.0,
    "spanish": 3.5,
    "mixed": 3.75,
    "code": 3.2,
    "json": 3.0,
    "markdown": 3.6,
}


def detect_content_type(text: str) -> str:
    """Detecta el tipo de contenido para mejor estimación."""
    if not text:
        return "mixed"
    
    sample = text[:5000]
    
    # Detectar código
    code_indicators = ['def ', 'class ', 'import ', 'function ', 'const ', 'var ', '```']
    code_count = sum(1 for ind in code_indicators if ind in sample)
    if code_count >= 3:
        return "code"
    
    # Detectar JSON
    if sample.strip().startswith(("{", "[")) or '```json' in sample:
        return "json"
    
    # Detectar idioma predominante
    spanish_words = ['que', 'los', 'las', 'del', 'para', 'con', 'por', 'una', 'como', 'más']
    english_words = ['the', 'and', 'for', 'that', 'with', 'this', 'from', 'have', 'are', 'not']
    
    words = re.findall(r'\b\w+\b', sample.lower())
    es_count = sum(1 for w in words if w in spanish_words)
    en_count = sum(1 for w in words if w in english_words)
    
    if es_count > en_count * 1.5:
        return "spanish"
    elif en_count > es_count * 1.5:
        return "english"
    
    # Detectar markdown
    if re.search(r'^#{1,3}\s', sample, re.MULTILINE):
        return "markdown"
    
    return "mixed"


def estimate_tokens_accurate(text: str) -> int:
    """
    Estimación mejorada de tokens considerando tipo de contenido.
    Más precisa que la simple len/3.75 de telemetry.py.
    """
    if not text:
        return 0
    
    content_type = detect_content_type(text)
    ratio = RATIOS.get(content_type, 3.75)
    
    base_estimate = len(text) / ratio
    
    # Ajuste por caracteres especiales (consumen más tokens)
    special_chars = len(re.findall(r'[^\w\s]', text))
    special_adjustment = special_chars * 0.3  # ~30% extra por char especial
    
    # Ajuste por newlines (cada newline es ~1 token)
    newlines = text.count('\n')
    
    total = base_estimate + special_adjustment + newlines
    
    # Margen de seguridad del 10%
    return int(total * 1.10)


# ═══════════════════════════════════════════════════════════════
# PRESUPUESTO POR SABIO
# ═══════════════════════════════════════════════════════════════

# Reservas fijas (tokens)
RESERVE_SYSTEM_PROMPT = 2000   # System prompt del sabio
RESERVE_OUTPUT = 8000          # Espacio para la respuesta
RESERVE_SAFETY = 5000          # Margen de seguridad


def get_budget(sabio_id: str) -> dict:
    """
    Retorna el presupuesto completo de contexto para un sabio.
    
    Returns:
        dict con: max_tokens, max_chars, usable_tokens, usable_chars,
                  grupo, reservas
    """
    config = get_sabio_config(sabio_id)
    max_tokens = config.get("contexto_tokens", 128000)
    max_chars = config.get("contexto_chars", 420000)
    grupo = config.get("grupo", "condensado")
    
    reservas = RESERVE_SYSTEM_PROMPT + RESERVE_OUTPUT + RESERVE_SAFETY
    usable_tokens = max_tokens - reservas
    
    # Convertir tokens usables a chars estimados
    usable_chars = int(usable_tokens * 3.75)
    
    return {
        "sabio_id": sabio_id,
        "nombre": config.get("nombre", sabio_id),
        "grupo": grupo,
        "max_tokens": max_tokens,
        "max_chars": max_chars,
        "reservas_tokens": reservas,
        "usable_tokens": usable_tokens,
        "usable_chars": usable_chars,
    }


def check_fits(sabio_id: str, text: str) -> tuple:
    """
    Verifica si un texto cabe en el contexto de un sabio.
    
    Returns:
        (fits: bool, info: dict)
    """
    budget = get_budget(sabio_id)
    tokens_est = estimate_tokens_accurate(text)
    chars = len(text)
    
    fits = tokens_est <= budget["usable_tokens"]
    
    info = {
        "sabio_id": sabio_id,
        "fits": fits,
        "tokens_estimados": tokens_est,
        "tokens_disponibles": budget["usable_tokens"],
        "uso_porcentaje": round(tokens_est / budget["usable_tokens"] * 100, 1) if budget["usable_tokens"] > 0 else 999,
        "chars_texto": chars,
        "exceso_tokens": max(0, tokens_est - budget["usable_tokens"]),
        "necesita_condensar": not fits,
    }
    
    return fits, info


def prepare_context(
    sabio_id: str,
    prompt: str,
    dossier: str = "",
    system: str = "",
    max_usage_pct: float = 0.90,
) -> dict:
    """
    Prepara el contexto optimizado para un sabio específico.
    Si excede el presupuesto, recorta inteligentemente.
    
    Returns:
        dict con: prompt_final, dossier_final, recortado, info
    """
    budget = get_budget(sabio_id)
    target_tokens = int(budget["usable_tokens"] * max_usage_pct)
    target_chars = int(target_tokens * 3.75)
    
    # Calcular espacio usado por system prompt
    system_tokens = estimate_tokens_accurate(system) if system else 0
    available_tokens = target_tokens - system_tokens
    available_chars = int(available_tokens * 3.75)
    
    prompt_tokens = estimate_tokens_accurate(prompt)
    dossier_tokens = estimate_tokens_accurate(dossier) if dossier else 0
    total_tokens = prompt_tokens + dossier_tokens
    
    result = {
        "prompt_final": prompt,
        "dossier_final": dossier,
        "recortado": False,
        "tokens_originales": total_tokens,
        "tokens_finales": total_tokens,
        "info": {
            "sabio": sabio_id,
            "budget_tokens": target_tokens,
            "system_tokens": system_tokens,
            "available_tokens": available_tokens,
        }
    }
    
    if total_tokens <= available_tokens:
        return result
    
    # Necesita recortar — priorizar prompt sobre dossier
    result["recortado"] = True
    
    # Estrategia: dar 70% al prompt, 30% al dossier
    prompt_budget = int(available_chars * 0.70)
    dossier_budget = int(available_chars * 0.30)
    
    if len(prompt) > prompt_budget:
        # Recortar prompt preservando inicio y final
        keep_start = int(prompt_budget * 0.7)
        keep_end = int(prompt_budget * 0.3)
        result["prompt_final"] = (
            prompt[:keep_start] +
            f"\n\n[... {len(prompt) - prompt_budget:,} caracteres omitidos por límite de contexto ...]\n\n" +
            prompt[-keep_end:]
        )
    
    if dossier and len(dossier) > dossier_budget:
        result["dossier_final"] = dossier[:dossier_budget] + \
            f"\n\n[... Dossier truncado a {dossier_budget:,} chars por límite de contexto ...]"
    
    result["tokens_finales"] = estimate_tokens_accurate(
        result["prompt_final"] + result["dossier_final"]
    )
    
    return result


def budget_report(sabios: list = None) -> str:
    """Genera un reporte de presupuesto para todos los sabios."""
    if sabios is None:
        sabios = ["gpt54", "claude", "gemini", "grok", "deepseek", "perplexity"]
    
    lines = [
        "# Presupuesto de Contexto por Sabio\n",
        "| Sabio | Max Tokens | Reservas | Usable | Usable Chars | Grupo |",
        "|-------|-----------|----------|--------|-------------|-------|",
    ]
    
    for sid in sabios:
        b = get_budget(sid)
        lines.append(
            f"| {b['nombre']} | {b['max_tokens']:,} | {b['reservas_tokens']:,} | "
            f"{b['usable_tokens']:,} | {b['usable_chars']:,} | {b['grupo']} |"
        )
    
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    print("📐 Context Budget — consulta-sabios\n")
    print(budget_report())
    
    # Test con texto de ejemplo
    test_text = "Hola mundo " * 10000  # ~110K chars
    for sid in ["gpt54", "deepseek"]:
        fits, info = check_fits(sid, test_text)
        status = "✅ Cabe" if fits else "❌ No cabe"
        print(f"\n{sid}: {status}")
        print(f"  Tokens est: {info['tokens_estimados']:,} / {info['tokens_disponibles']:,} ({info['uso_porcentaje']}%)")
    
    print("\n✅ Context Budget operativo")
