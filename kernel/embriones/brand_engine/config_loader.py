"""Config loader del Brand Engine — Pydantic schema + YAML reader.

Lee ``kernel/embriones/brand_engine_config.yaml`` (o ruta custom) y lo
valida contra schema canónico. Permite a Alfredo editar el YAML y recargar
la config sin redeploy (`BrandEngine` instancia nueva por request).

Spec: bridge/sprint_PAR_BICEFALO_001_brand_engine_spec_2026_05_11.md (T5).
DSC aplicables: DSC-G-004 (naming canónico).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field, field_validator


# ── Schema canónico ────────────────────────────────────────────────────────

class DimensionConfig(BaseModel):
    """Configuración de una dimensión individual del Brand Engine."""

    enabled: bool = True
    umbral_pass: float = Field(ge=0.0, le=1.0)
    criterios: list[str] = Field(min_length=1)


class DimensionesConfig(BaseModel):
    """Las 4 dimensiones canónicas del Brand Engine."""

    D1_brand_tono: DimensionConfig
    D2_honestidad_pura: DimensionConfig
    D3_consistencia_doctrina: DimensionConfig
    D4_calidad_apple_tesla: DimensionConfig


class BrandEngineConfig(BaseModel):
    """Configuración runtime completa del Brand Engine.

    Cargada vía ``load_brand_engine_config(path)``. Permite reload por
    request — instancia nueva de ``BrandEngine`` por validación si
    Alfredo edita el YAML.
    """

    enabled: bool = False
    mode: str = Field(default="shadow")
    evaluator_llm: str = "claude-opus-4-7"
    evaluator_fallback: str = "claude-opus-4-6"
    max_reintentos_embrion_1: int = Field(default=2, ge=0, le=5)
    budget_diario_usd: float = Field(default=10.0, ge=0.0)
    budget_alerta_telegram_usd: float = Field(default=8.0, ge=0.0)
    budget_kill_switch_usd: float = Field(default=12.0, ge=0.0)
    dimensiones: DimensionesConfig

    @field_validator("mode")
    @classmethod
    def _validate_mode(cls, v: str) -> str:
        allowed = {"shadow", "enforce"}
        if v not in allowed:
            raise ValueError(f"mode debe ser uno de {allowed}, recibido: {v!r}")
        return v

    @field_validator("evaluator_llm")
    @classmethod
    def _validate_evaluator(cls, v: str) -> str:
        # Whitelist de modelos verificados vía API Anthropic 2026-05-11.
        # Si Alfredo quiere un modelo nuevo, agregar aquí + DSC de actualización.
        whitelist = {
            "claude-opus-4-7",
            "claude-opus-4-6",
            "claude-opus-4-5-20251101",
            "claude-sonnet-4-6",
            "gpt-5.5-pro",
            "gpt-5.5",
        }
        if v not in whitelist:
            raise ValueError(
                f"evaluator_llm {v!r} no está en whitelist canónica {whitelist}. "
                "Agregar al schema + DSC si se quiere ampliar."
            )
        return v


# ── Loader ────────────────────────────────────────────────────────────────

DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "brand_engine_config.yaml"


def load_brand_engine_config(path: Optional[str] = None) -> BrandEngineConfig:
    """Lee y valida el YAML del Brand Engine.

    Parameters
    ----------
    path : ruta absoluta o relativa al YAML. Si None, usa
        ``kernel/embriones/brand_engine_config.yaml`` (ubicación canónica).

    Returns
    -------
    BrandEngineConfig validado.

    Raises
    ------
    FileNotFoundError
        Si el archivo no existe.
    ValidationError
        Si el YAML no cumple el schema (mode inválido, modelo no whitelist, etc.).
    """
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not config_path.exists():
        raise FileNotFoundError(
            f"Brand Engine config no encontrado en {config_path!s}. "
            "Crear con template canónico de spec PAR_BICEFALO_001."
        )

    with open(config_path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict) or "brand_engine_v1" not in raw:
        raise ValueError(
            "Brand Engine config inválido: debe tener root key 'brand_engine_v1'"
        )

    return BrandEngineConfig.model_validate(raw["brand_engine_v1"])


# ── Override por env vars (para CI / testing) ─────────────────────────────

def apply_env_overrides(config: BrandEngineConfig) -> BrandEngineConfig:
    """Aplica overrides desde env vars sin mutar el archivo.

    Útil para CI/testing — permite forzar ``BRAND_ENGINE_ENABLED=true`` sin
    editar el YAML. Documentado en spec PAR_BICEFALO_001.
    """
    overrides = {}
    if "BRAND_ENGINE_ENABLED" in os.environ:
        overrides["enabled"] = os.environ["BRAND_ENGINE_ENABLED"].lower() in {"1", "true", "yes"}
    if "BRAND_ENGINE_MODE" in os.environ:
        overrides["mode"] = os.environ["BRAND_ENGINE_MODE"]

    if not overrides:
        return config

    data = config.model_dump()
    data.update(overrides)
    return BrandEngineConfig.model_validate(data)
