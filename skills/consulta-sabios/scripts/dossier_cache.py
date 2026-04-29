#!/usr/bin/env python3.11
"""
dossier_cache.py — Caché de Dossier con Fingerprint y TTL
===========================================================
Evita re-investigar temas que ya fueron investigados recientemente.
Usa fingerprint del prompt para detectar consultas similares.

Funciones públicas:
    - get_or_create_dossier(prompt, investigar_fn) → str
    - invalidate(fingerprint) → bool
    - cleanup() → int (registros eliminados)
    - stats() → dict

Creado: 2026-04-08 (P2 auditoría sabios)
"""

import hashlib
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_loader import get_cache_config
from db_store import cache_dossier, get_cached_dossier, cleanup_expired_cache, get_db


def fingerprint(text: str) -> str:
    """
    Genera fingerprint de un prompt para caché.
    Normaliza el texto antes de hashear para agrupar consultas similares.
    """
    # Normalizar: lowercase, remover espacios extra, remover timestamps
    import re
    normalized = text.lower().strip()
    normalized = re.sub(r'\s+', ' ', normalized)
    # Remover fechas y timestamps que cambian entre consultas
    normalized = re.sub(r'\d{4}-\d{2}-\d{2}', 'DATE', normalized)
    normalized = re.sub(r'\d{2}:\d{2}:\d{2}', 'TIME', normalized)
    # Tomar solo los primeros 2000 chars para el hash (el core del prompt)
    normalized = normalized[:2000]
    
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


async def get_or_create_dossier(
    prompt: str,
    investigar_fn,
    ttl_hours: int = None,
    force_refresh: bool = False,
) -> tuple:
    """
    Busca dossier en caché o lo crea con la función de investigación.
    
    Args:
        prompt: El prompt original de la consulta
        investigar_fn: Función async que genera el dossier
        ttl_hours: TTL en horas (None = usar config)
        force_refresh: Si True, ignora caché
    
    Returns:
        (dossier_text: str, from_cache: bool)
    """
    config = get_cache_config()
    if ttl_hours is None:
        ttl_hours = config.get("ttl_horas", 24)
    
    enabled = config.get("habilitado", True)
    
    fp = fingerprint(prompt)
    
    if enabled and not force_refresh:
        cached = get_cached_dossier(fp)
        if cached:
            print(f"📦 Dossier encontrado en caché (fingerprint: {fp})")
            return cached, True
    
    # Generar nuevo dossier
    print(f"🔍 Generando nuevo dossier (fingerprint: {fp})...")
    dossier = await investigar_fn(prompt)
    
    # Guardar en caché
    if enabled and dossier:
        tema = prompt[:200]  # Primeros 200 chars como descripción
        cache_dossier(fp, tema, dossier, ttl_hours)
        print(f"   💾 Dossier guardado en caché (TTL: {ttl_hours}h)")
    
    return dossier, False


def invalidate(fp: str) -> bool:
    """Invalida un dossier específico del caché."""
    with get_db() as conn:
        result = conn.execute(
            "DELETE FROM dossier_cache WHERE fingerprint = ?", (fp,)
        )
        return result.rowcount > 0


def cleanup() -> int:
    """Limpia dossiers expirados."""
    return cleanup_expired_cache()


def stats() -> dict:
    """Estadísticas del caché."""
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) as c FROM dossier_cache").fetchone()["c"]
        active = conn.execute(
            "SELECT COUNT(*) as c FROM dossier_cache WHERE expires_at > datetime('now')"
        ).fetchone()["c"]
        expired = total - active
        total_hits = conn.execute(
            "SELECT COALESCE(SUM(hit_count), 0) as h FROM dossier_cache"
        ).fetchone()["h"]
        total_chars = conn.execute(
            "SELECT COALESCE(SUM(chars), 0) as c FROM dossier_cache"
        ).fetchone()["c"]
    
    return {
        "total": total,
        "activos": active,
        "expirados": expired,
        "hits_totales": total_hits,
        "chars_totales": total_chars,
    }


if __name__ == "__main__":
    print("📦 Dossier Cache — consulta-sabios\n")
    s = stats()
    print(f"   Total: {s['total']}")
    print(f"   Activos: {s['activos']}")
    print(f"   Expirados: {s['expirados']}")
    print(f"   Hits totales: {s['hits_totales']}")
    print(f"   Chars totales: {s['chars_totales']:,}")
    
    # Test fingerprint
    fp1 = fingerprint("¿Cuál es el estado de la tokenización inmobiliaria en México?")
    fp2 = fingerprint("¿cuál es el estado de la tokenización inmobiliaria en méxico?")
    fp3 = fingerprint("¿Cómo funciona la inteligencia artificial?")
    print(f"\n   Test fingerprint:")
    print(f"   fp1 == fp2 (misma pregunta, case diff): {fp1 == fp2}")
    print(f"   fp1 == fp3 (preguntas diferentes): {fp1 == fp3}")
    print("✅ Dossier Cache operativo")
