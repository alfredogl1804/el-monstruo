"""
Sprint 86.4.5 Bloque 2 — Field mapping declarativo del Catastro.

Parser y aplicador del yaml `field_mapping.yaml`. Toma el cache
normalizado producido por `_normalize_snapshots` (dict slug→fuente→fields)
y enriquece los persistibles con los 6 campos métricos:

  - quality_score
  - reliability_score
  - cost_efficiency
  - speed_score
  - precio_input_per_million
  - precio_output_per_million

Diseño:
  - Single-source preferred (no quorum forzado para campos métricos).
  - Normalizaciones soportadas: passthrough, minmax, inverse_log,
    derived_from_quorum.
  - Stateless: cada call recibe el cache + persistibles y los muta.
  - Memento preflight: registra warnings cuando una fuente esperada
    no aporta los campos declarados (sin abortar).

Integración: llamado por `pipeline._enrich_with_metrics(...)` después
de `_extract_persistible` y antes de `_enrich_with_coding`.

Brand-DNA: errores como `field_mapping_*`, naming explícito, sin emoji.
"""
from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


# ============================================================================
# Errores con identidad de marca
# ============================================================================

class FieldMappingError(Exception):
    """Errores del field mapping del Catastro."""


class FieldMappingLoadError(FieldMappingError):
    """No se pudo leer/parsear el yaml de field mapping."""


class FieldMappingApplyError(FieldMappingError):
    """Falla al aplicar el mapping a un persistible específico."""


# ============================================================================
# Loader
# ============================================================================

DEFAULT_YAML_PATH = Path(__file__).parent / "field_mapping.yaml"


def load_field_mapping(path: Path | None = None) -> dict[str, Any]:
    """
    Lee y parsea el yaml de field mapping.

    Levanta FieldMappingLoadError si no se puede leer/parsear.
    """
    target = path or DEFAULT_YAML_PATH
    try:
        with open(target, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except FileNotFoundError as exc:
        raise FieldMappingLoadError(
            f"field_mapping_yaml_not_found path={target}"
        ) from exc
    except yaml.YAMLError as exc:
        raise FieldMappingLoadError(
            f"field_mapping_yaml_parse_error path={target} err={exc}"
        ) from exc

    if not isinstance(data, dict) or "fields" not in data:
        raise FieldMappingLoadError(
            f"field_mapping_yaml_invalid_shape path={target}"
        )
    return data


# ============================================================================
# Helpers
# ============================================================================

def _get_dot_path(d: dict[str, Any], path: str) -> Any:
    """Navega `path` con dots sobre dict (e.g. 'pricing.input_per_million')."""
    cur: Any = d
    for part in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
        if cur is None:
            return None
    return cur


def _to_float(v: Any) -> float | None:
    if v is None:
        return None
    try:
        f = float(v)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


# ============================================================================
# Normalizaciones
# ============================================================================

def _normalize_minmax(value: float, all_values: list[float]) -> float:
    """Normaliza al rango 0-100 con min-max global del run."""
    if not all_values:
        return 50.0
    lo = min(all_values)
    hi = max(all_values)
    if hi == lo:
        return 50.0
    return 100.0 * (value - lo) / (hi - lo)


def _normalize_inverse_log(value: float, all_values: list[float]) -> float:
    """
    Inverse log: más barato = score mayor.
    score = 100 - 100 * log(v+1) / log(max+1)
    Si max == 0, todos a 100 (gratis).
    """
    pos_values = [v for v in all_values if v is not None and v >= 0]
    if not pos_values:
        return 50.0
    max_v = max(pos_values)
    if max_v <= 0:
        return 100.0
    raw = 100.0 - 100.0 * math.log(value + 1.0) / math.log(max_v + 1.0)
    return max(0.0, min(100.0, raw))


# ============================================================================
# Aplicador principal
# ============================================================================

OFFICIAL_SOURCES_FOR_RELIABILITY = ("artificial_analysis", "openrouter", "lmarena")


def apply_field_mapping(
    modelos_persistibles: dict[str, dict[str, Any]],
    modelos_por_fuente: dict[str, dict[str, dict[str, Any]]],
    mapping: dict[str, Any] | None = None,
) -> dict[str, dict[str, float | None]]:
    """
    Enriquece los persistibles con los 6 campos métricos según el mapping.

    Parameters
    ----------
    modelos_persistibles : dict
        Output de `_extract_persistible`. Forma:
        { slug: {"slug", "fields", "presence_confidence", "confirming_sources"} }
    modelos_por_fuente : dict
        Cache normalizado producido por `_normalize_snapshots`. Forma:
        { slug: { fuente_name: {campos_normalizados} } }
    mapping : dict | None
        Mapping ya cargado (testing). Si None, se carga del yaml default.

    Returns
    -------
    dict[slug, dict[campo, valor]]
        Diccionario de los campos métricos calculados para cada slug.
        También se mutan los persistibles agregando estos campos a `fields`.
    """
    if mapping is None:
        mapping = load_field_mapping()

    fields_spec: dict[str, dict[str, Any]] = mapping.get("fields", {})

    # ─── Memento preflight ───────────────────────────────────────────────
    _memento_preflight(modelos_por_fuente, mapping)

    # ─── Pre-cómputo: collect_per_field para normalizaciones de run ──────
    # Para minmax e inverse_log necesitamos todos los valores del run.
    raw_values_per_field: dict[str, list[float]] = {}
    for field_name, spec in fields_spec.items():
        raws: list[float] = []
        for slug, fuentes_data in modelos_por_fuente.items():
            if slug not in modelos_persistibles:
                continue  # solo modelos que ya pasaron presence quorum
            for extractor in spec.get("extractors", []):
                src = extractor["source"]
                path = extractor["path"]
                if src not in fuentes_data:
                    continue
                v = _get_dot_path(fuentes_data[src], path)
                f = _to_float(v)
                if f is not None:
                    raws.append(f)
                    break  # primer extractor con dato gana
        raw_values_per_field[field_name] = raws

    # ─── Aplicar mapping por modelo persistible ──────────────────────────
    results: dict[str, dict[str, float | None]] = {}
    for slug, persistible in modelos_persistibles.items():
        fuentes_data = modelos_por_fuente.get(slug, {})
        confirming_sources = persistible.get("confirming_sources", [])
        modelo_metrics: dict[str, float | None] = {}

        for field_name, spec in fields_spec.items():
            value = _extract_field_for_modelo(
                field_name=field_name,
                spec=spec,
                fuentes_data=fuentes_data,
                confirming_sources=confirming_sources,
                raw_values_global=raw_values_per_field[field_name],
            )
            modelo_metrics[field_name] = value
            # Mutar el persistible: agregar al fields dict (no reemplazar
            # los que ya están del quorum cross-source)
            if value is not None and field_name not in persistible["fields"]:
                persistible["fields"][field_name] = value
            elif (
                value is not None
                and field_name in persistible["fields"]
                and persistible["fields"][field_name] != value
            ):
                # quorum-derived ya existe (e.g. pricing.input_per_million),
                # mantenerlo y solo registrar en metrics local.
                pass

        results[slug] = modelo_metrics

    return results


def _extract_field_for_modelo(
    field_name: str,
    spec: dict[str, Any],
    fuentes_data: dict[str, dict[str, Any]],
    confirming_sources: list[str],
    raw_values_global: list[float],
) -> float | None:
    """Extrae un campo individual aplicando los extractors en orden."""
    extractors = spec.get("extractors", [])
    fallback = spec.get("fallback")

    # Intentar cada extractor en orden
    for extractor in extractors:
        src = extractor["source"]
        path = extractor["path"]
        norm = extractor.get("normalization", "none")

        if src not in fuentes_data:
            continue
        raw = _get_dot_path(fuentes_data[src], path)
        f = _to_float(raw)
        if f is None:
            continue

        if norm == "none":
            return f
        if norm == "passthrough":
            return max(0.0, min(100.0, f))  # clamp a rango válido
        if norm == "minmax":
            return _normalize_minmax(f, raw_values_global)
        if norm == "inverse_log":
            return _normalize_inverse_log(f, raw_values_global)
        # Default: passthrough con clamp
        return max(0.0, min(100.0, f))

    # Fallback strategies
    if fallback == "derived_from_quorum":
        n_sources = len(confirming_sources) if confirming_sources else 0
        total_official = len(OFFICIAL_SOURCES_FOR_RELIABILITY)
        if total_official == 0:
            return None
        return round(100.0 * n_sources / total_official, 2)

    return None


def _memento_preflight(
    modelos_por_fuente: dict[str, dict[str, dict[str, Any]]],
    mapping: dict[str, Any],
) -> None:
    """
    Capa Memento: verifica que las fuentes esperadas reporten al menos un
    modelo con los campos declarados. Solo loggea warnings, no aborta.

    Esto detecta drifts de schema en fuentes externas (e.g. AA renombró
    `intelligence_score` a otra cosa). El primer run productivo después
    de una rotación captura el incidente automáticamente.
    """
    preflight = mapping.get("memento_preflight") or {}
    required = preflight.get("required_fields_in_cache") or {}
    on_missing = preflight.get("on_missing", "log_warning")

    for src, paths in required.items():
        # Para cada fuente esperada, ver si AL MENOS un modelo del cache
        # tiene cada campo declarado.
        for path in paths:
            found = False
            for slug, fuentes_data in modelos_por_fuente.items():
                src_data = fuentes_data.get(src)
                if src_data is None:
                    continue
                if _get_dot_path(src_data, path) is not None:
                    found = True
                    break
            if not found:
                msg = (
                    f"[catastro_field_mapping] memento_preflight_missing "
                    f"source={src} path={path} "
                    f"action={on_missing}"
                )
                if on_missing == "raise":
                    raise FieldMappingApplyError(msg)
                logger.warning(msg)


__all__ = [
    "FieldMappingError",
    "FieldMappingLoadError",
    "FieldMappingApplyError",
    "load_field_mapping",
    "apply_field_mapping",
    "DEFAULT_YAML_PATH",
]
