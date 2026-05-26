#!/usr/bin/env python3.11
"""
data_retention.py — Política de Retención, Anonimización y PII
================================================================
Gestiona la retención de datos históricos, anonimiza información
sensible, y excluye PII de los registros.

Funciones públicas:
    - sanitize_text(text) → str (remueve PII)
    - apply_retention_policy() → dict (stats de limpieza)
    - anonymize_old_runs(days) → int (runs anonimizados)
    - audit_pii(text) → list (PII detectado)

Creado: 2026-04-08 (P2 auditoría sabios)
"""

import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_store import cleanup_expired_cache, get_db

# ═══════════════════════════════════════════════════════════════
# PATRONES PII
# ═══════════════════════════════════════════════════════════════

PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone_mx": re.compile(r"(?:\+?52\s?)?(?:\d{2,3}\s?)?\d{4}\s?\d{4}"),
    "phone_intl": re.compile(r"\+\d{1,3}\s?\(?\d{1,4}\)?\s?\d{4,10}"),
    "curp": re.compile(r"[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d"),
    "rfc": re.compile(r"[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}"),
    "credit_card": re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
    "ssn_us": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "ip_address": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
    "api_key_generic": re.compile(r"(?:sk|pk|api|key|token|secret)[_-]?[a-zA-Z0-9]{20,}", re.IGNORECASE),
}

REPLACEMENT_MAP = {
    "email": "[EMAIL_REDACTED]",
    "phone_mx": "[PHONE_REDACTED]",
    "phone_intl": "[PHONE_REDACTED]",
    "curp": "[CURP_REDACTED]",
    "rfc": "[RFC_REDACTED]",
    "credit_card": "[CC_REDACTED]",
    "ssn_us": "[SSN_REDACTED]",
    "ip_address": "[IP_REDACTED]",
    "api_key_generic": "[APIKEY_REDACTED]",
}


def sanitize_text(text: str) -> str:
    """
    Remueve PII de un texto.

    Args:
        text: Texto a sanitizar

    Returns:
        Texto con PII reemplazado por placeholders
    """
    if not text:
        return text

    sanitized = text
    for pii_type, pattern in PII_PATTERNS.items():
        replacement = REPLACEMENT_MAP.get(pii_type, "[REDACTED]")
        sanitized = pattern.sub(replacement, sanitized)

    return sanitized


def audit_pii(text: str) -> list:
    """
    Detecta PII en un texto sin modificarlo.

    Returns:
        Lista de detecciones: [{tipo, valor_parcial, posicion}]
    """
    if not text:
        return []

    findings = []
    for pii_type, pattern in PII_PATTERNS.items():
        for match in pattern.finditer(text):
            value = match.group()
            # Mostrar solo parcialmente para no exponer PII en el reporte
            if len(value) > 6:
                masked = value[:3] + "***" + value[-2:]
            else:
                masked = "***"

            findings.append(
                {
                    "tipo": pii_type,
                    "valor_parcial": masked,
                    "posicion": match.start(),
                }
            )

    return findings


def apply_retention_policy(
    max_runs_days: int = 90,
    max_cache_days: int = 7,
    max_experiment_days: int = 180,
) -> dict:
    """
    Aplica política de retención eliminando datos antiguos.

    Args:
        max_runs_days: Días máximos para conservar runs
        max_cache_days: Días máximos para caché de dossier
        max_experiment_days: Días máximos para experimentos

    Returns:
        dict con estadísticas de limpieza
    """
    stats = {
        "runs_eliminados": 0,
        "metrics_eliminados": 0,
        "cache_eliminados": 0,
        "experiments_eliminados": 0,
        "timestamp": datetime.now().isoformat(),
    }

    with get_db() as conn:
        # Eliminar runs antiguos
        cutoff_runs = (datetime.now() - timedelta(days=max_runs_days)).isoformat()
        result = conn.execute(
            "DELETE FROM sabio_metrics WHERE run_id IN (SELECT run_id FROM runs WHERE timestamp_start < ?)",
            (cutoff_runs,),
        )
        stats["metrics_eliminados"] = result.rowcount

        result = conn.execute(
            "DELETE FROM scores WHERE run_id IN (SELECT run_id FROM runs WHERE timestamp_start < ?)", (cutoff_runs,)
        )

        result = conn.execute("DELETE FROM runs WHERE timestamp_start < ?", (cutoff_runs,))
        stats["runs_eliminados"] = result.rowcount

    # Limpiar caché expirado
    stats["cache_eliminados"] = cleanup_expired_cache()

    # Limpiar experimentos antiguos
    exp_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent / "data" / "experiments"
    if exp_dir.exists():
        cutoff_exp = datetime.now() - timedelta(days=max_experiment_days)
        for f in exp_dir.glob("*.json"):
            if datetime.fromtimestamp(f.stat().st_mtime) < cutoff_exp:
                f.unlink()
                stats["experiments_eliminados"] += 1

    print("🧹 Política de retención aplicada:")
    print(f"   Runs eliminados: {stats['runs_eliminados']}")
    print(f"   Métricas eliminadas: {stats['metrics_eliminados']}")
    print(f"   Caché limpiado: {stats['cache_eliminados']}")
    print(f"   Experimentos eliminados: {stats['experiments_eliminados']}")

    return stats


def anonymize_old_runs(days: int = 60) -> int:
    """
    Anonimiza prompts y respuestas de runs antiguos,
    conservando solo métricas y scores.
    """
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    with get_db() as conn:
        result = conn.execute(
            """
            UPDATE runs SET
                metadata_json = '{"anonimizado": true}'
            WHERE timestamp_start < ?
            AND metadata_json NOT LIKE '%anonimizado%'
        """,
            (cutoff,),
        )
        count = result.rowcount

    # Anonimizar archivos de artefactos
    runs_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent / "data" / "runs"
    if runs_dir.exists():
        cutoff_dt = datetime.now() - timedelta(days=days)
        anonymized_files = 0
        for run_dir in runs_dir.iterdir():
            if run_dir.is_dir() and datetime.fromtimestamp(run_dir.stat().st_mtime) < cutoff_dt:
                for f in run_dir.glob("*.md"):
                    content = f.read_text(encoding="utf-8")
                    sanitized = sanitize_text(content)
                    if content != sanitized:
                        f.write_text(sanitized, encoding="utf-8")
                        anonymized_files += 1

    print(f"🔒 Anonimización: {count} runs, {anonymized_files if runs_dir.exists() else 0} archivos")
    return count


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "retain":
            apply_retention_policy()
        elif sys.argv[1] == "anonymize":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            anonymize_old_runs(days)
        elif sys.argv[1] == "audit":
            text = sys.argv[2] if len(sys.argv) > 2 else "Contactar a juan@email.com o al +52 55 1234 5678"
            findings = audit_pii(text)
            for f in findings:
                print(f"  ⚠️  {f['tipo']}: {f['valor_parcial']} (pos: {f['posicion']})")
    else:
        # Demo
        test = "Mi email es alfredo@ejemplo.com y mi CURP es GOCA850101HDFRRL09, llámame al +52 55 1234 5678"
        print(f"Original: {test}")
        print(f"Sanitizado: {sanitize_text(test)}")
        print("\nAuditoría PII:")
        for f in audit_pii(test):
            print(f"  ⚠️  {f['tipo']}: {f['valor_parcial']}")
        print("\n✅ Data Retention operativo")
