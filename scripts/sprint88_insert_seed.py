#!/usr/bin/env python3
"""
Sprint 88 - INSERT batch de los 84 productos seed a catastro_agentes (Supabase prod).

Ejecutar via:
    railway run --service el-monstruo-kernel python3 scripts/sprint88_insert_seed.py

Idempotente: usa ON CONFLICT (id) DO UPDATE para re-corridas.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import psycopg

# Importar el seed
sys.path.insert(0, str(Path(__file__).parent))
from sprint88_seed_85_productos import attach_tier_seed


def main() -> int:
    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL not set", file=sys.stderr)
        return 1

    productos = attach_tier_seed()
    print(f"Inserting {len(productos)} productos to catastro_agentes...")

    inserted = 0
    updated = 0
    errors = []

    try:
        with psycopg.connect(dsn, autocommit=False) as conn:
            with conn.cursor() as cur:
                for p in productos:
                    try:
                        # Construir INSERT con todos los campos
                        cur.execute(
                            """
                            INSERT INTO catastro_agentes (
                                id, nombre, proveedor, macroarea, dominio,
                                subcapacidades, llm_base_id, llm_bases_alternativos,
                                tiene_sandbox, acceso_filesystem, acceso_internet,
                                multi_step_capable, multi_swarm_capable,
                                persistencia_memoria, costo_por_uso_tipico,
                                tools_nativas, casos_de_uso_primarios,
                                estado, open_weights, api_endpoint,
                                fortalezas, debilidades, limitaciones,
                                fuentes_evidencia, quorum_alcanzado, confidence,
                                curador_responsable, validacion_adversarial,
                                tier_seed, data_extra, schema_version
                            )
                            VALUES (
                                %s, %s, %s, 'agentes', %s,
                                %s, %s, %s,
                                %s, %s, %s,
                                %s, %s,
                                %s, %s,
                                %s, %s,
                                %s, %s, %s,
                                %s, %s, %s,
                                %s, %s, %s,
                                %s, %s,
                                %s, %s, 1
                            )
                            ON CONFLICT (id) DO UPDATE SET
                                nombre = EXCLUDED.nombre,
                                proveedor = EXCLUDED.proveedor,
                                dominio = EXCLUDED.dominio,
                                subcapacidades = EXCLUDED.subcapacidades,
                                llm_base_id = EXCLUDED.llm_base_id,
                                llm_bases_alternativos = EXCLUDED.llm_bases_alternativos,
                                tiene_sandbox = EXCLUDED.tiene_sandbox,
                                acceso_filesystem = EXCLUDED.acceso_filesystem,
                                acceso_internet = EXCLUDED.acceso_internet,
                                multi_step_capable = EXCLUDED.multi_step_capable,
                                multi_swarm_capable = EXCLUDED.multi_swarm_capable,
                                persistencia_memoria = EXCLUDED.persistencia_memoria,
                                costo_por_uso_tipico = EXCLUDED.costo_por_uso_tipico,
                                casos_de_uso_primarios = EXCLUDED.casos_de_uso_primarios,
                                estado = EXCLUDED.estado,
                                open_weights = EXCLUDED.open_weights,
                                fortalezas = EXCLUDED.fortalezas,
                                tier_seed = EXCLUDED.tier_seed,
                                data_extra = EXCLUDED.data_extra,
                                updated_at = now()
                            RETURNING (xmax = 0) AS inserted
                            """,
                            (
                                p["id"],
                                p["nombre"],
                                p["proveedor"],
                                p["dominio"],
                                p.get("subcapacidades", []),
                                p.get("llm_base_id"),
                                p.get("llm_bases_alternativos", []),
                                p.get("tiene_sandbox", False),
                                p.get("acceso_filesystem", False),
                                p.get("acceso_internet", False),
                                p.get("multi_step_capable", False),
                                p.get("multi_swarm_capable", False),
                                p.get("persistencia_memoria", "none"),
                                p.get("costo_por_uso_tipico"),
                                p.get("tools_nativas", []),
                                p.get("casos_de_uso_primarios", []),
                                p.get("estado", "production"),
                                p.get("open_weights", False),
                                p.get("api_endpoint"),
                                p.get("fortalezas", []),
                                p.get("debilidades", []),
                                p.get("limitaciones", []),
                                json.dumps(p.get("fuentes_evidencia", [])),
                                p.get("quorum_alcanzado", False),
                                p.get("confidence", 0.50),
                                p.get("curador_responsable"),
                                json.dumps(p.get("validacion_adversarial", {})),
                                p["tier_seed"],
                                json.dumps(p.get("data_extra", {})),
                            ),
                        )
                        result = cur.fetchone()
                        was_inserted = result[0] if result else None
                        if was_inserted:
                            inserted += 1
                        else:
                            updated += 1
                    except Exception as e:
                        errors.append((p["id"], str(e)))
                        print(f"  ERROR on {p['id']}: {type(e).__name__}: {e}", file=sys.stderr)
                        # Rollback for this row, continue with next
                        conn.rollback()
                        # Reabrir transaccion implicit con next execute
                        continue

                conn.commit()

                # Verificación final
                cur.execute("SELECT COUNT(*) FROM catastro_agentes")
                total = cur.fetchone()[0]
                cur.execute("SELECT dominio, COUNT(*) FROM catastro_agentes GROUP BY dominio ORDER BY dominio")
                by_dom = cur.fetchall()

        print(f"\nINSERT_OK: {inserted} insertados, {updated} actualizados, {len(errors)} errores")
        print(f"TOTAL_EN_TABLA: {total}")
        print("DISTRIBUCION:")
        for d, c in by_dom:
            print(f"  {d}: {c}")

        if errors:
            print("\nERRORES:")
            for eid, emsg in errors:
                print(f"  {eid}: {emsg}")
            return 1

        return 0
    except Exception as e:
        print(f"FATAL: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
