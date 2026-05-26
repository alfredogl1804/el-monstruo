#!/usr/bin/env python3.11
"""
json_parser.py — Parser JSON Robusto con Schema Validation
============================================================
Reemplaza el frágil split("```json") con múltiples estrategias
de extracción y validación de schema.

Funciones públicas:
    - parse_json(text, schema=None) → dict | list | None
    - validate_schema(data, schema) → (bool, errors)

Estrategias de extracción (en orden):
    1. JSON puro (el texto completo es JSON válido)
    2. Bloque ```json ... ``` en markdown
    3. Bloque ``` ... ``` genérico
    4. Primer objeto/array JSON encontrado con balance de llaves
    5. Reparación de JSON común (trailing commas, single quotes, etc.)

Creado: 2026-04-08 (P1 auditoría sabios)
"""

import json
import re
from typing import Any, Optional

# ═══════════════════════════════════════════════════════════════
# SCHEMAS PREDEFINIDOS
# ═══════════════════════════════════════════════════════════════

SCHEMA_INVESTIGACION = {
    "type": "object",
    "required": ["temas"],
    "properties": {
        "temas": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["tema", "prioridad"],
                "properties": {
                    "tema": {"type": "string"},
                    "prioridad": {"type": "string", "enum": ["ALTA", "MEDIA", "BAJA"]},
                    "query": {"type": "string"},
                },
            },
        },
        "sensibilidad_temporal": {"type": "string"},
    },
}

SCHEMA_VALIDACION = {
    "type": "object",
    "required": ["afirmaciones"],
    "properties": {
        "afirmaciones": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["afirmacion", "sabio"],
                "properties": {
                    "afirmacion": {"type": "string"},
                    "sabio": {"type": "string"},
                    "query": {"type": "string"},
                },
            },
        }
    },
}

SCHEMA_COBERTURA = {
    "type": "object",
    "required": ["cobertura"],
    "properties": {
        "cobertura": {"type": "number"},
        "temas_cubiertos": {"type": "integer"},
        "temas_totales": {"type": "integer"},
        "temas_faltantes": {"type": "array"},
    },
}

SCHEMA_CONSENSO = {
    "type": "object",
    "required": ["consenso"],
    "properties": {
        "consenso": {"type": "number"},
        "contradicciones": {"type": "integer"},
        "puntos_consenso": {"type": "array"},
        "puntos_divergencia": {"type": "array"},
    },
}


# ═══════════════════════════════════════════════════════════════
# PARSER PRINCIPAL
# ═══════════════════════════════════════════════════════════════


def parse_json(text: str, schema: dict = None) -> Optional[Any]:
    """
    Extrae JSON de texto usando múltiples estrategias.
    Opcionalmente valida contra un schema.

    Args:
        text: Texto que contiene JSON (puede tener markdown, etc.)
        schema: Schema opcional para validación

    Returns:
        dict/list parseado, o None si falla todo
    """
    if not text or not text.strip():
        return None

    strategies = [
        _strategy_pure_json,
        _strategy_markdown_json_block,
        _strategy_markdown_generic_block,
        _strategy_brace_matching,
        _strategy_repair_and_parse,
    ]

    for strategy in strategies:
        try:
            result = strategy(text)
            if result is not None:
                if schema:
                    valid, errors = validate_schema(result, schema)
                    if valid:
                        return result
                    # Si no pasa schema, intentar siguiente estrategia
                    continue
                return result
        except Exception:
            continue

    return None


def validate_schema(data: Any, schema: dict) -> tuple:
    """
    Validación básica de schema sin dependencias externas.

    Returns:
        (is_valid: bool, errors: list[str])
    """
    errors = []

    if schema.get("type") == "object":
        if not isinstance(data, dict):
            return False, [f"Expected object, got {type(data).__name__}"]

        for field in schema.get("required", []):
            if field not in data:
                errors.append(f"Missing required field: {field}")

        for field, field_schema in schema.get("properties", {}).items():
            if field in data:
                value = data[field]
                expected_type = field_schema.get("type")

                if expected_type == "string" and not isinstance(value, str):
                    errors.append(f"Field '{field}' should be string, got {type(value).__name__}")
                elif expected_type == "number" and not isinstance(value, (int, float)):
                    errors.append(f"Field '{field}' should be number, got {type(value).__name__}")
                elif expected_type == "integer" and not isinstance(value, int):
                    # Allow float that is whole number
                    if isinstance(value, float) and value == int(value):
                        data[field] = int(value)
                    else:
                        errors.append(f"Field '{field}' should be integer, got {type(value).__name__}")
                elif expected_type == "array" and not isinstance(value, list):
                    errors.append(f"Field '{field}' should be array, got {type(value).__name__}")
                elif expected_type == "object" and not isinstance(value, dict):
                    errors.append(f"Field '{field}' should be object, got {type(value).__name__}")

                if "enum" in field_schema and value not in field_schema["enum"]:
                    errors.append(f"Field '{field}' value '{value}' not in enum {field_schema['enum']}")

    elif schema.get("type") == "array":
        if not isinstance(data, list):
            return False, [f"Expected array, got {type(data).__name__}"]

    return len(errors) == 0, errors


# ═══════════════════════════════════════════════════════════════
# ESTRATEGIAS DE EXTRACCIÓN
# ═══════════════════════════════════════════════════════════════


def _strategy_pure_json(text: str) -> Optional[Any]:
    """Estrategia 1: El texto completo es JSON válido."""
    stripped = text.strip()
    if stripped.startswith(("{", "[")):
        return json.loads(stripped)
    return None


def _strategy_markdown_json_block(text: str) -> Optional[Any]:
    """Estrategia 2: Extraer de bloque ```json ... ```."""
    # Buscar todos los bloques json
    matches = re.findall(r"```json\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    for match in matches:
        try:
            return json.loads(match.strip())
        except json.JSONDecodeError:
            continue
    return None


def _strategy_markdown_generic_block(text: str) -> Optional[Any]:
    """Estrategia 3: Extraer de bloque ``` ... ``` genérico."""
    matches = re.findall(r"```\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    for match in matches:
        stripped = match.strip()
        if stripped.startswith(("{", "[")):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                continue
    return None


def _strategy_brace_matching(text: str) -> Optional[Any]:
    """Estrategia 4: Encontrar JSON con balance de llaves/corchetes."""
    # Buscar inicio de objeto o array
    for start_char, end_char in [("{", "}"), ("[", "]")]:
        start_idx = text.find(start_char)
        if start_idx == -1:
            continue

        depth = 0
        in_string = False
        escape = False

        for i in range(start_idx, len(text)):
            c = text[i]

            if escape:
                escape = False
                continue

            if c == "\\" and in_string:
                escape = True
                continue

            if c == '"' and not escape:
                in_string = not in_string
                continue

            if in_string:
                continue

            if c == start_char:
                depth += 1
            elif c == end_char:
                depth -= 1
                if depth == 0:
                    candidate = text[start_idx : i + 1]
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        break  # Try next occurrence

    return None


def _strategy_repair_and_parse(text: str) -> Optional[Any]:
    """Estrategia 5: Reparar JSON común y parsear."""
    # Buscar candidatos en bloques markdown o texto suelto
    candidates = []

    # Extraer de bloques markdown (raw, sin parsear)
    for m in re.finditer(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL):
        candidates.append(m.group(1).strip())

    # Buscar cualquier cosa que parezca JSON en el texto
    for m in re.finditer(r"[\{\[].*?[\}\]]", text, re.DOTALL):
        candidates.append(m.group(0))

    # Si no hay candidatos, usar el texto completo
    if not candidates:
        candidates = [text.strip()]

    for candidate in candidates:
        # Aplicar reparaciones comunes
        repaired = candidate

        # Trailing commas antes de } o ]
        repaired = re.sub(r",\s*([}\]])", r"\1", repaired)
        # True/False/None de Python
        repaired = re.sub(r"\bTrue\b", "true", repaired)
        repaired = re.sub(r"\bFalse\b", "false", repaired)
        repaired = re.sub(r"\bNone\b", "null", repaired)
        # Comentarios de línea
        repaired = re.sub(r"//[^\n]*", "", repaired)
        # Single quotes → double quotes
        repaired = re.sub(r"(?<=[:,\[{\s])'([^'\n]*)'(?=[,\]}: \n])", r'"\1"', repaired)
        # Claves sin comillas: word:
        repaired = re.sub(r"(?<=[{,])\s*(\w+)\s*:", r' "\1":', repaired)

        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            continue

    return None


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════


def safe_get(data: dict, *keys, default=None):
    """Acceso seguro a claves anidadas."""
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key, default)
        elif isinstance(current, list) and isinstance(key, int) and 0 <= key < len(current):
            current = current[key]
        else:
            return default
    return current


if __name__ == "__main__":
    # Tests
    print("🧪 Testing json_parser.py\n")

    tests = [
        ("JSON puro", '{"key": "value"}', None, True),
        (
            "Markdown block",
            'Aquí va:\n```json\n{"temas": [{"tema": "test", "prioridad": "ALTA"}]}\n```\nFin.',
            SCHEMA_INVESTIGACION,
            True,
        ),
        ("Trailing comma", '{"a": 1, "b": 2,}', None, True),
        ("Single quotes", "{'key': 'value'}", None, True),
        ("Python bools", '{"active": True, "deleted": False}', None, True),
        ("Texto basura", "No hay JSON aquí", None, False),
        ("Nested markdown", 'Respuesta:\n```\n{"consenso": 0.85, "contradicciones": 2}\n```', SCHEMA_CONSENSO, True),
        ("Schema fail", '{"wrong_key": 1}', SCHEMA_CONSENSO, False),
    ]

    passed = 0
    for name, text, schema, should_succeed in tests:
        result = parse_json(text, schema)
        success = (result is not None) == should_succeed
        status = "✅" if success else "❌"
        print(f"  {status} {name}: {'OK' if success else 'FAIL'} → {result}")
        if success:
            passed += 1

    print(f"\n{'✅' if passed == len(tests) else '❌'} {passed}/{len(tests)} tests passed")
