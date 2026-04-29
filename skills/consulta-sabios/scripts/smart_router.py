#!/usr/bin/env python3.11
"""
smart_router.py — Routing Adaptativo por Tipo de Consulta
===========================================================
Analiza el prompt y selecciona la configuración óptima de sabios:
- Qué sabios consultar (no siempre los 6)
- Qué rol asignar a cada uno
- Qué timeout usar
- Si necesita investigación pre-consulta
- Si necesita condensación de contexto

Tipos de consulta detectados:
    - tecnica: código, arquitectura, infra → priorizar Gemini, GPT-5.4, DeepSeek
    - estrategica: negocio, inversión, plan → priorizar GPT-5.4, Claude, Grok
    - legal: regulación, compliance → priorizar Claude, GPT-5.4 + investigación obligatoria
    - creativa: naming, branding, copy → priorizar Grok, GPT-5.4, Gemini
    - investigacion: estado del arte, comparativas → todos + investigación profunda
    - operativa: procesos, SOP, flujos → priorizar GPT-5.4, Claude, DeepSeek

Creado: 2026-04-08 (P3 auditoría sabios)
"""

import os
import re
import sys
from dataclasses import dataclass, field
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@dataclass
class RouteConfig:
    """Configuración de routing para una consulta."""
    tipo_consulta: str
    sabios_primarios: list  # Sabios que DEBEN responder
    sabios_secundarios: list  # Sabios opcionales (nice to have)
    sabios_excluidos: list  # Sabios que NO aportan valor aquí
    necesita_investigacion: bool  # Pre-consulta obligatoria
    investigacion_profundidad: str  # "basica", "media", "profunda"
    necesita_condensacion: bool  # Si el contexto es muy largo
    timeout_factor: float  # Multiplicador del timeout base (1.0 = normal)
    min_sabios_exito: int  # Mínimo de sabios que deben responder
    roles: dict = field(default_factory=dict)  # Rol asignado a cada sabio
    notas: str = ""


# ═══════════════════════════════════════════════════════════════
# CLASIFICADOR DE CONSULTAS
# ═══════════════════════════════════════════════════════════════

KEYWORDS = {
    "tecnica": [
        "código", "code", "api", "sdk", "framework", "arquitectura", "deploy",
        "docker", "kubernetes", "database", "sql", "python", "javascript",
        "typescript", "react", "backend", "frontend", "microservicio", "infra",
        "devops", "ci/cd", "git", "debug", "error", "bug", "performance",
        "algoritmo", "estructura de datos", "sistema", "servidor",
    ],
    "estrategica": [
        "negocio", "business", "inversión", "investment", "plan", "estrategia",
        "strategy", "mercado", "market", "competencia", "revenue", "modelo de negocio",
        "business model", "pitch", "fundraising", "venture", "startup", "escalar",
        "crecimiento", "growth", "monetización", "pricing", "go to market",
    ],
    "legal": [
        "regulación", "regulation", "ley", "law", "legal", "compliance",
        "licencia", "license", "contrato", "contract", "jurisdicción",
        "fiscal", "tax", "impuesto", "constitución", "sociedad", "stichting",
        "fundación", "foundation", "sec", "cnbv", "fintech", "kyc", "aml",
        "gdpr", "privacidad", "privacy", "token", "security token",
    ],
    "creativa": [
        "nombre", "naming", "marca", "brand", "branding", "logo", "diseño",
        "design", "copy", "copywriting", "slogan", "tagline", "narrativa",
        "storytelling", "contenido", "content", "video", "tiktok", "viral",
        "creativo", "creative", "campaña", "campaign",
    ],
    "investigacion": [
        "investigar", "research", "estado del arte", "state of the art",
        "comparar", "compare", "benchmark", "análisis", "analysis",
        "tendencia", "trend", "panorama", "landscape", "estudio",
        "paper", "whitepaper", "reporte", "report", "datos", "data",
        "estadística", "statistics", "encuesta", "survey",
    ],
    "operativa": [
        "proceso", "process", "sop", "flujo", "workflow", "operación",
        "operation", "automatizar", "automate", "procedimiento", "procedure",
        "checklist", "manual", "guía", "guide", "paso a paso", "step by step",
        "implementar", "implement", "ejecutar", "execute", "sprint",
    ],
}

# Configuraciones por tipo
ROUTE_CONFIGS = {
    "tecnica": RouteConfig(
        tipo_consulta="tecnica",
        sabios_primarios=["gpt54", "gemini", "deepseek"],
        sabios_secundarios=["claude", "grok"],
        sabios_excluidos=["perplexity"],
        necesita_investigacion=True,
        investigacion_profundidad="media",
        necesita_condensacion=False,
        timeout_factor=1.0,
        min_sabios_exito=3,
        roles={
            "gpt54": "Arquitecto principal — diseña la solución",
            "gemini": "Ingeniero de implementación — código y detalles técnicos",
            "deepseek": "Revisor técnico — encuentra edge cases y bugs",
            "claude": "Documentador — claridad y estructura",
            "grok": "Challenger — cuestiona decisiones técnicas",
        },
    ),
    "estrategica": RouteConfig(
        tipo_consulta="estrategica",
        sabios_primarios=["gpt54", "claude", "grok"],
        sabios_secundarios=["gemini", "perplexity"],
        sabios_excluidos=["deepseek"],
        necesita_investigacion=True,
        investigacion_profundidad="profunda",
        necesita_condensacion=False,
        timeout_factor=1.2,
        min_sabios_exito=3,
        roles={
            "gpt54": "Estratega principal — diseña el plan",
            "claude": "Analista de riesgos — identifica vulnerabilidades",
            "grok": "Visionario — perspectivas no convencionales",
            "gemini": "Analista de datos — valida con números",
            "perplexity": "Investigador — datos de mercado actuales",
        },
    ),
    "legal": RouteConfig(
        tipo_consulta="legal",
        sabios_primarios=["claude", "gpt54"],
        sabios_secundarios=["perplexity", "gemini"],
        sabios_excluidos=["deepseek", "grok"],
        necesita_investigacion=True,
        investigacion_profundidad="profunda",
        necesita_condensacion=False,
        timeout_factor=1.5,
        min_sabios_exito=2,
        roles={
            "claude": "Analista legal principal — interpreta regulaciones",
            "gpt54": "Asesor estratégico-legal — implicaciones prácticas",
            "perplexity": "Investigador legal — regulaciones vigentes",
            "gemini": "Comparador jurisdiccional — análisis multi-país",
        },
        notas="SIEMPRE requiere investigación profunda. Las leyes cambian constantemente.",
    ),
    "creativa": RouteConfig(
        tipo_consulta="creativa",
        sabios_primarios=["grok", "gpt54", "gemini"],
        sabios_secundarios=["claude"],
        sabios_excluidos=["deepseek", "perplexity"],
        necesita_investigacion=False,
        investigacion_profundidad="basica",
        necesita_condensacion=False,
        timeout_factor=0.8,
        min_sabios_exito=2,
        roles={
            "grok": "Director creativo — ideas disruptivas",
            "gpt54": "Copywriter — refinamiento y tono",
            "gemini": "Diseñador conceptual — visualización",
            "claude": "Editor — coherencia y claridad",
        },
    ),
    "investigacion": RouteConfig(
        tipo_consulta="investigacion",
        sabios_primarios=["gpt54", "claude", "gemini", "grok", "deepseek", "perplexity"],
        sabios_secundarios=[],
        sabios_excluidos=[],
        necesita_investigacion=True,
        investigacion_profundidad="profunda",
        necesita_condensacion=True,
        timeout_factor=1.5,
        min_sabios_exito=4,
        roles={
            "gpt54": "Orquestador — sintetiza todo",
            "claude": "Analista profundo — matices y contradicciones",
            "gemini": "Investigador técnico — papers y datos",
            "grok": "Pensador lateral — conexiones inesperadas",
            "deepseek": "Verificador — valida consistencia",
            "perplexity": "Buscador — datos más recientes",
        },
        notas="Usa TODOS los sabios. Investigación pre-consulta obligatoria y profunda.",
    ),
    "operativa": RouteConfig(
        tipo_consulta="operativa",
        sabios_primarios=["gpt54", "claude", "deepseek"],
        sabios_secundarios=["gemini"],
        sabios_excluidos=["grok", "perplexity"],
        necesita_investigacion=False,
        investigacion_profundidad="basica",
        necesita_condensacion=False,
        timeout_factor=1.0,
        min_sabios_exito=2,
        roles={
            "gpt54": "Diseñador de procesos — flujo óptimo",
            "claude": "Documentador — SOPs claros y completos",
            "deepseek": "Optimizador — eficiencia y automatización",
            "gemini": "Integrador — conexiones con herramientas",
        },
    ),
}


def classify_query(prompt: str) -> str:
    """
    Clasifica una consulta en un tipo.
    
    Returns:
        Tipo de consulta: tecnica, estrategica, legal, creativa, investigacion, operativa
    """
    prompt_lower = prompt.lower()
    scores = {}
    
    for tipo, keywords in KEYWORDS.items():
        score = 0
        for kw in keywords:
            # Contar ocurrencias (case insensitive)
            count = len(re.findall(re.escape(kw), prompt_lower))
            if count > 0:
                score += count * (2 if len(kw) > 8 else 1)  # Palabras largas pesan más
        scores[tipo] = score
    
    if not scores or max(scores.values()) == 0:
        return "investigacion"  # Default: usar todos los sabios
    
    return max(scores, key=scores.get)


def route(prompt: str, force_type: str = None) -> RouteConfig:
    """
    Genera la configuración de routing para un prompt.
    
    Args:
        prompt: El prompt de la consulta
        force_type: Forzar un tipo específico (override)
    
    Returns:
        RouteConfig con la configuración óptima
    """
    tipo = force_type or classify_query(prompt)
    config = ROUTE_CONFIGS.get(tipo, ROUTE_CONFIGS["investigacion"])
    
    return config


def get_sabios_for_route(config: RouteConfig) -> list:
    """Retorna la lista ordenada de sabios a consultar."""
    return config.sabios_primarios + config.sabios_secundarios


def describe_route(config: RouteConfig) -> str:
    """Genera descripción legible del routing."""
    lines = [
        f"📍 Tipo de consulta: {config.tipo_consulta.upper()}",
        f"   Sabios primarios: {', '.join(config.sabios_primarios)}",
        f"   Sabios secundarios: {', '.join(config.sabios_secundarios) or 'ninguno'}",
        f"   Excluidos: {', '.join(config.sabios_excluidos) or 'ninguno'}",
        f"   Investigación: {'SÍ' if config.necesita_investigacion else 'NO'} ({config.investigacion_profundidad})",
        f"   Condensación: {'SÍ' if config.necesita_condensacion else 'NO'}",
        f"   Timeout factor: {config.timeout_factor}x",
        f"   Mínimo sabios: {config.min_sabios_exito}",
    ]
    if config.notas:
        lines.append(f"   ⚠️  {config.notas}")
    
    lines.append("   Roles:")
    for sabio, rol in config.roles.items():
        lines.append(f"     • {sabio}: {rol}")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    tests = [
        "Necesito diseñar la arquitectura de microservicios para el backend de CIP con Python y FastAPI",
        "¿Cuál es la mejor estrategia de go-to-market para una plataforma de inversión inmobiliaria?",
        "¿Qué regulaciones aplican para tokenizar bienes raíces en México bajo la Ley Fintech?",
        "Necesito un nombre creativo para una marca de inversión inmobiliaria fraccionada",
        "Investiga el estado del arte de la tokenización inmobiliaria en 2026",
        "Diseña un SOP para el proceso de onboarding de nuevos inversionistas",
    ]
    
    for test in tests:
        config = route(test)
        print(f"\n{'='*60}")
        print(f"Prompt: {test[:80]}...")
        print(describe_route(config))
    
    print(f"\n✅ Smart Router operativo — {len(ROUTE_CONFIGS)} tipos de consulta configurados")
