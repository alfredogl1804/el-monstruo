#!/usr/bin/env python3.11
"""
fallback_manager.py — Fallbacks Automáticos por Rol Crítico
=============================================================
Cuando un sabio primario falla, selecciona automáticamente
un reemplazo basado en el rol que necesita cubrirse.

Lógica:
    1. Cada sabio tiene roles en los que es fuerte
    2. Si falla, se busca el mejor reemplazo disponible
    3. Se reintenta con el reemplazo usando el mismo prompt
    4. Se registra el fallback en telemetría

Creado: 2026-04-08 (P3 auditoría sabios)
"""

import os
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@dataclass
class FallbackResult:
    """Resultado de un intento de fallback."""
    sabio_original: str
    sabio_reemplazo: str
    rol: str
    razon: str
    exito: bool = False


# Capacidades de cada sabio (0-1, qué tan bueno es en cada rol)
SABIO_CAPABILITIES = {
    "gpt54": {
        "orquestacion": 0.95,
        "estrategia": 0.90,
        "codigo": 0.85,
        "legal": 0.80,
        "creatividad": 0.75,
        "investigacion": 0.85,
        "documentacion": 0.85,
        "analisis_riesgo": 0.80,
    },
    "claude": {
        "orquestacion": 0.85,
        "estrategia": 0.85,
        "codigo": 0.80,
        "legal": 0.90,
        "creatividad": 0.70,
        "investigacion": 0.80,
        "documentacion": 0.95,
        "analisis_riesgo": 0.90,
    },
    "gemini": {
        "orquestacion": 0.75,
        "estrategia": 0.75,
        "codigo": 0.90,
        "legal": 0.70,
        "creatividad": 0.80,
        "investigacion": 0.90,
        "documentacion": 0.80,
        "analisis_riesgo": 0.70,
    },
    "grok": {
        "orquestacion": 0.70,
        "estrategia": 0.80,
        "codigo": 0.75,
        "legal": 0.65,
        "creatividad": 0.95,
        "investigacion": 0.75,
        "documentacion": 0.70,
        "analisis_riesgo": 0.75,
    },
    "deepseek": {
        "orquestacion": 0.70,
        "estrategia": 0.65,
        "codigo": 0.95,
        "legal": 0.60,
        "creatividad": 0.50,
        "investigacion": 0.80,
        "documentacion": 0.75,
        "analisis_riesgo": 0.65,
    },
    "perplexity": {
        "orquestacion": 0.50,
        "estrategia": 0.65,
        "codigo": 0.60,
        "legal": 0.70,
        "creatividad": 0.45,
        "investigacion": 0.95,
        "documentacion": 0.60,
        "analisis_riesgo": 0.60,
    },
}

# Cadena de fallback por defecto (si no hay rol específico)
DEFAULT_FALLBACK_CHAIN = {
    "gpt54": ["claude", "gemini", "grok"],
    "claude": ["gpt54", "gemini", "grok"],
    "gemini": ["gpt54", "deepseek", "claude"],
    "grok": ["gpt54", "gemini", "claude"],
    "deepseek": ["gemini", "gpt54", "claude"],
    "perplexity": ["gemini", "gpt54", "claude"],
}


def get_fallback(
    failed_sabio: str,
    rol: str = None,
    already_failed: list = None,
    already_responding: list = None,
) -> FallbackResult:
    """
    Determina el mejor reemplazo para un sabio que falló.
    
    Args:
        failed_sabio: ID del sabio que falló
        rol: Rol que necesita cubrirse (None = usar cadena por defecto)
        already_failed: Lista de sabios que ya fallaron (excluir)
        already_responding: Lista de sabios que ya respondieron (excluir)
    
    Returns:
        FallbackResult con el reemplazo seleccionado
    """
    excluded = set(already_failed or []) | set(already_responding or []) | {failed_sabio}
    
    if rol:
        # Buscar por capacidad en el rol específico
        candidates = []
        for sabio_id, caps in SABIO_CAPABILITIES.items():
            if sabio_id not in excluded:
                score = caps.get(rol, 0)
                candidates.append((sabio_id, score))
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        if candidates:
            best = candidates[0]
            return FallbackResult(
                sabio_original=failed_sabio,
                sabio_reemplazo=best[0],
                rol=rol,
                razon=f"Mejor en {rol} (score: {best[1]:.2f}) entre disponibles",
            )
    else:
        # Usar cadena por defecto
        chain = DEFAULT_FALLBACK_CHAIN.get(failed_sabio, [])
        for candidate in chain:
            if candidate not in excluded:
                return FallbackResult(
                    sabio_original=failed_sabio,
                    sabio_reemplazo=candidate,
                    rol="general",
                    razon=f"Siguiente en cadena de fallback de {failed_sabio}",
                )
    
    return FallbackResult(
        sabio_original=failed_sabio,
        sabio_reemplazo="",
        rol=rol or "general",
        razon="No hay reemplazos disponibles",
        exito=False,
    )


def get_fallback_chain(sabio_id: str, rol: str = None) -> list:
    """
    Retorna la cadena completa de fallback para un sabio.
    
    Returns:
        Lista ordenada de sabios de reemplazo
    """
    if rol:
        candidates = []
        for sid, caps in SABIO_CAPABILITIES.items():
            if sid != sabio_id:
                score = caps.get(rol, 0)
                candidates.append((sid, score))
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [c[0] for c in candidates]
    else:
        return DEFAULT_FALLBACK_CHAIN.get(sabio_id, [])


def evaluate_coverage(
    responding_sabios: list,
    required_roles: list,
) -> dict:
    """
    Evalúa si los sabios que respondieron cubren los roles necesarios.
    
    Returns:
        dict con cobertura por rol y gaps
    """
    coverage = {}
    gaps = []
    
    for rol in required_roles:
        best_score = 0
        best_sabio = None
        
        for sabio_id in responding_sabios:
            score = SABIO_CAPABILITIES.get(sabio_id, {}).get(rol, 0)
            if score > best_score:
                best_score = score
                best_sabio = sabio_id
        
        coverage[rol] = {
            "cubierto": best_score >= 0.6,
            "score": best_score,
            "sabio": best_sabio,
        }
        
        if best_score < 0.6:
            gaps.append(rol)
    
    return {
        "cobertura": coverage,
        "gaps": gaps,
        "cobertura_pct": sum(1 for v in coverage.values() if v["cubierto"]) / len(required_roles) if required_roles else 1.0,
    }


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🔄 Fallback Manager — consulta-sabios\n")
    
    # Test 1: Fallback simple
    result = get_fallback("claude", rol="legal")
    print(f"Si Claude falla (rol: legal):")
    print(f"  → Reemplazo: {result.sabio_reemplazo} ({result.razon})")
    
    # Test 2: Fallback con exclusiones
    result = get_fallback("gpt54", rol="orquestacion", already_failed=["claude"])
    print(f"\nSi GPT-5.4 falla (rol: orquestación, Claude ya falló):")
    print(f"  → Reemplazo: {result.sabio_reemplazo} ({result.razon})")
    
    # Test 3: Cadena completa
    chain = get_fallback_chain("deepseek", rol="codigo")
    print(f"\nCadena de fallback para DeepSeek (código): {chain}")
    
    # Test 4: Evaluación de cobertura
    cov = evaluate_coverage(
        responding_sabios=["gpt54", "gemini", "grok"],
        required_roles=["orquestacion", "codigo", "legal", "creatividad"]
    )
    print(f"\nCobertura con [gpt54, gemini, grok]:")
    for rol, info in cov["cobertura"].items():
        status = "✅" if info["cubierto"] else "❌"
        print(f"  {status} {rol}: {info['sabio']} ({info['score']:.2f})")
    print(f"  Gaps: {cov['gaps']}")
    print(f"  Cobertura: {cov['cobertura_pct']:.0%}")
    
    print("\n✅ Fallback Manager operativo")
