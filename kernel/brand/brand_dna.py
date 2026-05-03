"""
El Monstruo — Brand DNA (Sprint 82)
====================================
Define la identidad de marca inmutable del Monstruo.
Cada módulo que produce output DEBE consultar este módulo.

El Brand DNA no es un archivo de configuración — es la fuente de verdad
viva que define qué ES y qué NO ES El Monstruo.

Referencia: docs/BRAND_ENGINE_ESTRATEGIA.md
"""

from __future__ import annotations

import re
from typing import Any, Optional


# ── Brand DNA — Identidad Inmutable ──────────────────────────────────

BRAND_DNA: dict[str, Any] = {
    "mission": (
        "Crear el primer agente de IA soberano del mundo "
        "que genera negocios exitosos de forma autónoma"
    ),
    "vision": (
        "Un ecosistema de Monstruos interconectados que democratiza "
        "la creación de empresas — cualquier persona puede tener un "
        "negocio exitoso desde el día 1"
    ),
    "archetype": "creator_mage",
    "personality": ["implacable", "preciso", "soberano", "magnánimo"],
    "tone": {
        "do": [
            "directo",
            "técnicamente preciso",
            "confiado",
            "metáforas industriales",
        ],
        "dont": [
            "corporativo",
            "pedante",
            "arrogante",
            "genérico",
        ],
    },
    "naming": {
        "modules": {
            "forja": "Dashboard principal",
            "guardian": "Compliance y auditoría",
            "colmena": "Embriones especializados",
            "simulador": "Predicciones causales",
            "magna": "Clasificador inteligente",
            "vigía": "Monitoreo y alertas",
            "sabios": "Consulta multi-modelo",
        },
        "error_format": "{module}_{action}_{failure_type}",
        "never": ["service", "handler", "utils", "helper", "misc", "manager"],
    },
    "visual": {
        "primary": "#F97316",      # Naranja forja
        "background": "#1C1917",   # Graphite oscuro
        "accent": "#A8A29E",       # Acero
        "fonts": {
            "display": "Bebas Neue",
            "body": "Inter",
            "mono": "JetBrains Mono",
        },
    },
    "anti_patterns": [
        "chatbot amigable",
        "asistente servil",
        "herramienta genérica",
        "dashboard que se ve como Grafana/Datadog",
        "wrapper de APIs de terceros sin identidad propia",
    ],
}


# ── Naming Validation ────────────────────────────────────────────────

# Forbidden names from BRAND_DNA — exposed as set for fast token lookup
_FORBIDDEN_NAMES: set[str] = set(BRAND_DNA["naming"]["never"])

# Tokenization patterns
_SEPARATOR_SPLIT = re.compile(r"[\s\-_/.]+")
_CAMEL_TOKEN = re.compile(r"[A-Z]+(?=[A-Z][a-z]|\b)|[A-Z]?[a-z]+|[A-Z]+")


def _tokenize_identifier(name: str) -> list[str]:
    """Split snake_case, camelCase, kebab-case en tokens lowercase.

    Diseño: regex ``\\b`` no detecta tokens en snake_case porque ``_`` es
    ``\\w``. Esta función segmenta primero por separadores explícitos y
    luego por cambios de mayúscula (camelCase), normalizando todo a
    minúsculas para comparar contra _FORBIDDEN_NAMES.

    Ejemplos:
        "data_handler"  → ["data", "handler"]
        "MyHelper"      → ["my", "helper"]
        "URLParser"     → ["url", "parser"]
        "forja"         → ["forja"]
        "embrion-loop"  → ["embrion", "loop"]
    """
    if not name:
        return []
    tokens: list[str] = []
    for part in _SEPARATOR_SPLIT.split(name):
        if not part:
            continue
        sub = _CAMEL_TOKEN.findall(part)
        tokens.extend(sub if sub else [part])
    return [t.lower() for t in tokens if t]


def validate_output_name(name: str) -> bool:
    """
    Valida que un nombre de módulo, endpoint o variable siga las
    convenciones de marca del Monstruo.

    Reconoce snake_case, camelCase, kebab-case y dot.notation —
    cualquier token prohibido (service, handler, utils, helper,
    misc, manager) en cualquier posición invalida el nombre.

    Returns:
        True si el nombre es brand-compliant, False si contiene
        términos prohibidos.
    """
    if not name or not isinstance(name, str):
        return False
    tokens = _tokenize_identifier(name)
    return not any(t in _FORBIDDEN_NAMES for t in tokens)


def get_forbidden_matches(name: str) -> list[str]:
    """
    Retorna la lista de tokens prohibidos encontrados en un nombre,
    deduplicados y en minúsculas. Vacía si el nombre es compliant.
    """
    if not name or not isinstance(name, str):
        return []
    tokens = _tokenize_identifier(name)
    seen: set[str] = set()
    matches: list[str] = []
    for t in tokens:
        if t in _FORBIDDEN_NAMES and t not in seen:
            matches.append(t)
            seen.add(t)
    return matches


# ── Error Message Factory ────────────────────────────────────────────

def get_error_message(
    module: str,
    action: str,
    failure_type: str,
    context: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Genera un error message on-brand con formato {module}_{action}_{failure_type}.

    Nunca produce "internal server error" ni "something went wrong".
    Cada error tiene identidad: quién falló, qué intentaba, y por qué.

    Args:
        module: Nombre del módulo (ej: "embrion", "magna", "guardian")
        action: Acción que se intentaba (ej: "classify", "record", "validate")
        failure_type: Tipo de falla (ej: "timeout", "not_found", "invalid_input")
        context: Datos adicionales para diagnóstico

    Returns:
        Dict con error code, módulo, contexto y sugerencia de resolución.
    """
    error_code = f"{module}_{action}_{failure_type}"
    return {
        "error": error_code,
        "module": module,
        "action": action,
        "failure_type": failure_type,
        "context": context or {},
        "suggestion": f"Verificar {module} — posible {failure_type} en {action}",
    }


# ── Generic Error Detection ──────────────────────────────────────────

_GENERIC_ERRORS = frozenset([
    "internal server error",
    "something went wrong",
    "unknown error",
    "an error occurred",
    "error",
    "fail",
    "unexpected error",
])


def is_generic_error(message: str) -> bool:
    """
    Detecta si un mensaje de error es genérico (anti-patrón de marca).

    El Monstruo nunca dice "something went wrong". Cada error tiene
    identidad: módulo, acción, tipo de falla.
    """
    if not message or not isinstance(message, str):
        return False
    return message.strip().lower() in _GENERIC_ERRORS
