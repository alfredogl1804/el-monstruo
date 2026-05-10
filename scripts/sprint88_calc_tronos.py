#!/usr/bin/env python3
"""
Sprint 88 — Cálculo de tronos por dominio.

Trono = producto con mayor score técnico-operativo por dominio.

Score:
  + 30 si tier_seed=1 (top-5 del dominio)
  + 15 si multi_swarm_capable
  + 10 si tiene_sandbox
  + 10 si acceso_filesystem
  + 10 si acceso_internet
  + 10 si multi_step_capable
  + 10 si persistencia_memoria='external_db'
  +  5 si estado='production'

Desempate: open_weights DESC, tier_seed ASC, id ASC.

Resultado: lista de 9 tronos (uno por dominio) que se devuelven y se persisten
en una vista materializada catastro_tronos_agentes.
"""
import os
import sys
import psycopg

SCORE_SQL = """
SELECT
    id, nombre, dominio, tier_seed, open_weights, estado,
    (
        (CASE WHEN tier_seed = 1 THEN 30 ELSE 0 END)
      + (CASE WHEN multi_swarm_capable THEN 15 ELSE 0 END)
      + (CASE WHEN tiene_sandbox THEN 10 ELSE 0 END)
      + (CASE WHEN acceso_filesystem THEN 10 ELSE 0 END)
      + (CASE WHEN acceso_internet THEN 10 ELSE 0 END)
      + (CASE WHEN multi_step_capable THEN 10 ELSE 0 END)
      + (CASE WHEN persistencia_memoria = 'external_db' THEN 10 ELSE 0 END)
      + (CASE WHEN estado = 'production' THEN 5 ELSE 0 END)
    ) AS score
FROM catastro_agentes
ORDER BY dominio, score DESC, open_weights DESC, tier_seed ASC, id ASC
"""

PERSIST_VIEW_SQL = """
DROP MATERIALIZED VIEW IF EXISTS catastro_tronos_agentes CASCADE;

CREATE MATERIALIZED VIEW catastro_tronos_agentes AS
SELECT DISTINCT ON (dominio)
    dominio,
    id AS trono_id,
    nombre AS trono_nombre,
    tier_seed,
    open_weights,
    estado,
    (
        (CASE WHEN tier_seed = 1 THEN 30 ELSE 0 END)
      + (CASE WHEN multi_swarm_capable THEN 15 ELSE 0 END)
      + (CASE WHEN tiene_sandbox THEN 10 ELSE 0 END)
      + (CASE WHEN acceso_filesystem THEN 10 ELSE 0 END)
      + (CASE WHEN acceso_internet THEN 10 ELSE 0 END)
      + (CASE WHEN multi_step_capable THEN 10 ELSE 0 END)
      + (CASE WHEN persistencia_memoria = 'external_db' THEN 10 ELSE 0 END)
      + (CASE WHEN estado = 'production' THEN 5 ELSE 0 END)
    ) AS score,
    now() AS calculado_at
FROM catastro_agentes
ORDER BY dominio,
         (
            (CASE WHEN tier_seed = 1 THEN 30 ELSE 0 END)
          + (CASE WHEN multi_swarm_capable THEN 15 ELSE 0 END)
          + (CASE WHEN tiene_sandbox THEN 10 ELSE 0 END)
          + (CASE WHEN acceso_filesystem THEN 10 ELSE 0 END)
          + (CASE WHEN acceso_internet THEN 10 ELSE 0 END)
          + (CASE WHEN multi_step_capable THEN 10 ELSE 0 END)
          + (CASE WHEN persistencia_memoria = 'external_db' THEN 10 ELSE 0 END)
          + (CASE WHEN estado = 'production' THEN 5 ELSE 0 END)
         ) DESC,
         open_weights DESC, tier_seed ASC, id ASC;

CREATE UNIQUE INDEX idx_catastro_tronos_agentes_dominio
    ON catastro_tronos_agentes (dominio);

COMMENT ON MATERIALIZED VIEW catastro_tronos_agentes IS
    'Trono por dominio (Sprint 88). Producto top según score técnico-operativo. '
    'Refrescar con: REFRESH MATERIALIZED VIEW catastro_tronos_agentes;';
"""


def main() -> int:
    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL not set", file=sys.stderr)
        return 1

    try:
        with psycopg.connect(dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Crear vista materializada de tronos
                print("Creando vista materializada catastro_tronos_agentes...")
                cur.execute(PERSIST_VIEW_SQL)
                print("OK: catastro_tronos_agentes creada.\n")

                # Listar los 9 tronos
                cur.execute("""
                    SELECT dominio, trono_id, trono_nombre, score, tier_seed, open_weights, estado
                    FROM catastro_tronos_agentes
                    ORDER BY dominio
                """)
                tronos = cur.fetchall()

                print(f"=== {len(tronos)} TRONOS POR DOMINIO ===\n")
                for d, tid, tnom, sc, ts, ow, est in tronos:
                    ow_str = "OSS" if ow else "CLOSED"
                    print(f"  [{d:<32s}] -> {tnom:<35s} (id={tid}, score={sc}, tier={ts}, {ow_str}, {est})")

                # Mostrar también los top-3 por dominio para auditoria
                print("\n=== TOP-3 POR DOMINIO (para audit) ===\n")
                cur.execute(f"""
                    WITH scored AS ({SCORE_SQL}),
                    ranked AS (
                        SELECT *, ROW_NUMBER() OVER (PARTITION BY dominio ORDER BY score DESC, open_weights DESC, tier_seed ASC, id ASC) AS rk
                        FROM scored
                    )
                    SELECT dominio, rk, id, nombre, score
                    FROM ranked
                    WHERE rk <= 3
                    ORDER BY dominio, rk
                """)
                current_dom = None
                for d, rk, _id, nom, sc in cur.fetchall():
                    if d != current_dom:
                        print(f"\n  {d}:")
                        current_dom = d
                    marker = "👑" if rk == 1 else "  "
                    print(f"    {marker} #{rk} {nom} (score={sc}, id={_id})")

        print(f"\nTRONOS_OK: {len(tronos)} tronos persistidos en catastro_tronos_agentes")
        return 0
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
