"""
Sprint Memento Bloque 5 Fase 1 — UPSERT idempotente de 2 nuevas ops.

Agrega `kernel_admin_call` y `external_api_call` a la tabla
memento_critical_operations en Supabase production. UPSERT idempotente:
si ya existen, las actualiza con los valores actuales del YAML.

Uso:
    python3 scripts/_upsert_memento_ops_b5_fase1.py
"""
from __future__ import annotations

import os
import sys
import json

import psycopg2
from psycopg2.extras import Json


def main() -> int:
    db_url = os.environ.get("SUPABASE_DB_URL")
    if not db_url:
        print("ERROR: SUPABASE_DB_URL no está seteada.", file=sys.stderr)
        return 1

    new_ops = [
        {
            "id": "kernel_admin_call",
            "nombre": "Kernel Admin Call",
            "descripcion": "Llamada autenticada a endpoints administrativos del kernel (ej. /v1/error-memory/seed, /v1/memento/validate, /v1/admin/*). No requiere validación contra fuente externa pero queda auditada en memento_validations.",
            "triggers": ["kernel_admin_endpoint_call", "requires_monstruo_api_key"],
            "requires_validation": True,
            "requires_confirmation": "api_key_present",
            "source_of_truth_ids": [],
            "activo": True,
            "version": 1,
        },
        {
            "id": "external_api_call",
            "nombre": "External API Call",
            "descripcion": "Llamada a APIs externas desde tools del Embrión (ej. /v1/browser/render, OpenRouter, ArtificialAnalysis). Auditoría de uso y rate limiting; no compara contra fuente de verdad.",
            "triggers": ["tool_external_api_call", "third_party_endpoint"],
            "requires_validation": True,
            "requires_confirmation": "tool_authorized_in_registry",
            "source_of_truth_ids": [],
            "activo": True,
            "version": 1,
        },
    ]

    print(f"Conectando a Supabase production...")
    conn = psycopg2.connect(db_url)
    conn.autocommit = False

    upsert_sql = """
        INSERT INTO memento_critical_operations
            (id, nombre, descripcion, triggers, requires_validation,
             requires_confirmation, source_of_truth_ids, activo, version)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            nombre = EXCLUDED.nombre,
            descripcion = EXCLUDED.descripcion,
            triggers = EXCLUDED.triggers,
            requires_validation = EXCLUDED.requires_validation,
            requires_confirmation = EXCLUDED.requires_confirmation,
            source_of_truth_ids = EXCLUDED.source_of_truth_ids,
            activo = EXCLUDED.activo,
            version = EXCLUDED.version,
            actualizado_en = NOW()
        RETURNING id, version, activo
    """

    try:
        with conn.cursor() as cur:
            for op in new_ops:
                cur.execute(upsert_sql, (
                    op["id"],
                    op["nombre"],
                    op["descripcion"],
                    Json(op["triggers"]),
                    op["requires_validation"],
                    op["requires_confirmation"],
                    op["source_of_truth_ids"],
                    op["activo"],
                    op["version"],
                ))
                row = cur.fetchone()
                print(f"  UPSERT OK: id={row[0]} version={row[1]} activo={row[2]}")

            # Verificación: contar total ops activas
            cur.execute("SELECT COUNT(*) FROM memento_critical_operations WHERE activo = TRUE")
            total = cur.fetchone()[0]
            print(f"\nTotal ops activas: {total} (esperado: 6)")

            # Verificar las 2 nuevas
            cur.execute("""
                SELECT id, nombre, source_of_truth_ids, activo
                FROM memento_critical_operations
                WHERE id IN ('kernel_admin_call', 'external_api_call')
                ORDER BY id
            """)
            for row in cur.fetchall():
                print(f"  Verificación: id={row[0]} nombre='{row[1]}' source_ids={row[2]} activo={row[3]}")

        conn.commit()
        print("\n[OK] Catalogo actualizado en Supabase production.")
        return 0

    except Exception as exc:
        conn.rollback()
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
