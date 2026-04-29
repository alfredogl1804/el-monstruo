#!/usr/bin/env python3.11
"""
config_loader.py — Carga centralizada de configuración
========================================================
Lee skill_config.yaml y model_registry.yaml.
Provee funciones para acceder a cualquier parámetro de configuración.

Uso:
    from config_loader import get_config, get_model_registry, get_sabio_config
"""

import os
from pathlib import Path
from functools import lru_cache

try:
    import yaml
except ImportError:
    # Fallback: parseo básico si PyYAML no está instalado
    yaml = None

CONFIG_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent / "config"
SKILL_CONFIG = CONFIG_DIR / "skill_config.yaml"
MODEL_REGISTRY = CONFIG_DIR / "model_registry.yaml"


def _load_yaml(path: Path) -> dict:
    """Carga un archivo YAML."""
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        if yaml:
            return yaml.safe_load(f) or {}
        else:
            # Fallback muy básico — solo para emergencias
            import json
            content = f.read()
            # Intentar JSON como último recurso
            try:
                return json.loads(content)
            except Exception:
                return {}


@lru_cache(maxsize=1)
def get_config() -> dict:
    """Retorna la configuración completa de skill_config.yaml."""
    return _load_yaml(SKILL_CONFIG)


@lru_cache(maxsize=1)
def get_model_registry() -> dict:
    """Retorna el registro de modelos completo."""
    return _load_yaml(MODEL_REGISTRY)


def get_sabio_config(sabio_id: str) -> dict:
    """Retorna la configuración de un sabio específico del registry."""
    registry = get_model_registry()
    sabios = registry.get("sabios", {})
    return sabios.get(sabio_id, {})


def get_timeout(key: str) -> int:
    """Retorna un timeout específico de la configuración."""
    config = get_config()
    return config.get("timeouts", {}).get(key, 300)


def get_concurrency(key: str) -> int:
    """Retorna un límite de concurrencia."""
    config = get_config()
    return config.get("concurrencia", {}).get(key, 4)


def get_quality_gate_config() -> dict:
    """Retorna la configuración del quality gate."""
    config = get_config()
    return config.get("quality_gate", {})


def get_context_budget(sabio_id: str) -> int:
    """Retorna el presupuesto de caracteres para un sabio."""
    config = get_config()
    budgets = config.get("contexto", {}).get("presupuesto_por_sabio", {})
    return budgets.get(sabio_id, 420000)  # Default conservador


def get_routing_config() -> dict:
    """Retorna la configuración de routing adaptativo."""
    config = get_config()
    return config.get("routing", {})


def get_cache_config() -> dict:
    """Retorna la configuración de caché."""
    config = get_config()
    return config.get("cache", {})


def get_retention_config() -> dict:
    """Retorna la configuración de retención y privacidad."""
    config = get_config()
    return config.get("retencion", {})


def get_experiment_config() -> dict:
    """Retorna la configuración de experimentación."""
    config = get_config()
    return config.get("experimentacion", {})


def get_modo_sabios(modo: str) -> list:
    """Retorna la lista de sabios para un modo de consulta."""
    config = get_config()
    modo_config = config.get("modos", {}).get(modo, {})
    return modo_config.get("sabios", ["gpt54", "claude", "gemini", "grok", "deepseek", "perplexity"])


def get_prompt_version(role: str = "orquestador") -> str:
    """Lee el prompt versionado para un rol específico."""
    config = get_config()
    version = config.get("sintesis", {}).get("prompt_version", "v1")
    prompt_file = CONFIG_DIR / "prompt_versions" / f"{version}_{role}.md"
    if prompt_file.exists():
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()
    return None


if __name__ == "__main__":
    print("📋 Config Loader — consulta-sabios")
    config = get_config()
    print(f"   Versión: {config.get('version', 'unknown')}")
    print(f"   Modo default: {config.get('modo_default', 'enjambre')}")
    registry = get_model_registry()
    sabios = registry.get("sabios", {})
    print(f"   Sabios registrados: {len(sabios)}")
    for sid, s in sabios.items():
        print(f"     {sid}: {s.get('nombre')} ({s.get('proveedor')}) — {s.get('contexto_tokens'):,} tokens")
    print(f"   Prompt orquestador v1: {'✅' if get_prompt_version('orquestador') else '❌'}")
    print("✅ Config operativa")
