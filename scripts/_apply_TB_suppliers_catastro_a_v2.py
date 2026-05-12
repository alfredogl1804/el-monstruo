"""TB — Aplicar INSERT idempotente de 6 suppliers reales + 24 placeholders.

Sprint CATASTRO-A v2 (post-S89 v2 Opción B).
Aprobado por Cowork T2-A 2026-05-12 (luz verde sobre las 5 decisiones).
Ejecutar via: `railway run python3 scripts/_apply_TB_suppliers_catastro_a_v2.py`

Idempotente: ON CONFLICT (key) DO NOTHING en cada INSERT.
Doctrina: DSC-V-002 (validación realtime), DSC-S-006 (RLS), DSC-S-001 (PII metadata-only).
"""

from __future__ import annotations

import os
import sys

import psycopg2


REALES_SQL = """
INSERT INTO public.catastro_suppliers_humanos
  (key, name, role, availability, skills, contact, active, last_active)
VALUES
  ('supplier_notario_5_navarrete',
   'José Eduardo Navarrete Herrera',
   'notario',
   'on_demand',
   ARRAY['fe_publica','protocolizacion','poderes','testamentos','contratos_inmobiliarios'],
   '{"verification_url":"https://www.notariadoyucateco.org.mx/notarios.php","notaria_num":5,"preferred_method":"email_via_official_directory","city":"Mérida","state":"Yucatán","verification_source":"Colegio Notarial de Yucatán","verified_at":"2026-05-12","validation_status":"verified_real_official"}'::jsonb,
   true, NULL),
  ('supplier_notario_16_evia',
   'Carlos Alfredo Evia Salazar',
   'notario',
   'on_demand',
   ARRAY['fe_publica','protocolizacion','poderes','testamentos','contratos_inmobiliarios'],
   '{"verification_url":"https://www.notariadoyucateco.org.mx/notarios.php","notaria_num":16,"preferred_method":"email_via_official_directory","city":"Mérida","state":"Yucatán","verification_source":"Colegio Notarial de Yucatán","verified_at":"2026-05-12","validation_status":"verified_real_official"}'::jsonb,
   true, NULL),
  ('supplier_notario_18_priego',
   'Sergio Iván Priego Cárdenas',
   'notario',
   'on_demand',
   ARRAY['fe_publica','protocolizacion','poderes','testamentos','contratos_inmobiliarios'],
   '{"verification_url":"https://www.notariadoyucateco.org.mx/notarios.php","notaria_num":18,"preferred_method":"email_via_official_directory","city":"Mérida","state":"Yucatán","verification_source":"Colegio Notarial de Yucatán","verified_at":"2026-05-12","validation_status":"verified_real_official"}'::jsonb,
   true, NULL),
  ('supplier_notario_19_vales',
   'Fernando Vales Tenreiro',
   'notario',
   'on_demand',
   ARRAY['fe_publica','protocolizacion','poderes','testamentos','contratos_inmobiliarios'],
   '{"verification_url":"https://www.notariadoyucateco.org.mx/notarios.php","notaria_num":19,"preferred_method":"email_via_official_directory","city":"Mérida","state":"Yucatán","verification_source":"Colegio Notarial de Yucatán","verified_at":"2026-05-12","validation_status":"verified_real_official"}'::jsonb,
   true, NULL),
  ('supplier_ing_civil_euan_gongora',
   'Ing. Germán Gabriel Euán Góngora',
   'ingeniero_civil',
   'on_demand',
   ARRAY['estructural','peritaje','dictamenes','obra_civil'],
   '{"verification_url":"http://www.cicyucatan.mx/consejo-directivo","colegio":"CICY","cargo":"Presidente XXXV Consejo Directivo 2026-2028","preferred_method":"email_via_official_directory","city":"Mérida","state":"Yucatán","verification_source":"CICY","verified_at":"2026-05-12","validation_status":"verified_real_official"}'::jsonb,
   true, NULL),
  ('supplier_ing_civil_montalvo',
   'Ing. Víctor Manuel Montalvo Alcocer',
   'ingeniero_civil',
   'on_demand',
   ARRAY['estructural','peritaje','dictamenes','obra_civil'],
   '{"verification_url":"http://www.cicyucatan.mx/consejo-directivo","colegio":"CICY","cargo":"Tesorero XXXV Consejo Directivo 2026-2028","preferred_method":"email_via_official_directory","city":"Mérida","state":"Yucatán","verification_source":"CICY","verified_at":"2026-05-12","validation_status":"verified_real_official"}'::jsonb,
   true, NULL)
ON CONFLICT (key) DO NOTHING;
"""

PLACEHOLDERS_TEMPLATE = """
INSERT INTO public.catastro_suppliers_humanos
  (key, name, role, availability, skills, contact, active, last_active)
SELECT
  'supplier_placeholder_{slug}_' || lpad(g::text, 2, '0'),
  '{display} Sureste MX — placeholder ' || lpad(g::text, 2, '0'),
  '{role}',
  NULL,
  ARRAY[]::TEXT[],
  jsonb_build_object(
    'validation_status','pending_realtime_verification',
    'needs_research', true,
    'target_source','{target}',
    'created_at','2026-05-12'
  ),
  false, NULL
FROM generate_series(1, {n}) g
ON CONFLICT (key) DO NOTHING;
"""

PLACEHOLDER_SPECS = [
    {"slug": "arq", "display": "Arquitecto", "role": "arquitecto", "target": "CIDEY|CICY-Arq", "n": 6},
    {"slug": "valuador", "display": "Valuador", "role": "valuador", "target": "Colegio Valuadores Yucatán", "n": 4},
    {"slug": "fotografo", "display": "Fotógrafo arquitectura", "role": "fotografo_arquitectura", "target": "Recomendación profesional", "n": 4},
    {"slug": "contratista", "display": "Contratista", "role": "contratista", "target": "CMIC Yucatán", "n": 6},
    {"slug": "abogado", "display": "Abogado", "role": "abogado", "target": "Barra Mexicana Yucatán", "n": 4},
]


def main() -> int:
    dsn = os.environ.get("SUPABASE_DB_URL") or os.environ.get("DATABASE_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL / DATABASE_URL no presentes", file=sys.stderr)
        return 1

    conn = psycopg2.connect(dsn)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        # Pre-count
        cur.execute("SELECT count(*) FROM public.catastro_suppliers_humanos")
        before = cur.fetchone()[0]
        print(f"BEFORE rows: {before}")

        # 1. INSERT 6 reales
        cur.execute(REALES_SQL)
        print(f"INSERT reales: rowcount={cur.rowcount}")

        # 2. INSERT 24 placeholders (5 batches)
        total_placeholder = 0
        for spec in PLACEHOLDER_SPECS:
            sql = PLACEHOLDERS_TEMPLATE.format(**spec)
            cur.execute(sql)
            print(f"INSERT placeholder {spec['slug']} (n={spec['n']}): rowcount={cur.rowcount}")
            total_placeholder += cur.rowcount

        # 3. Post-count
        cur.execute("SELECT count(*) FROM public.catastro_suppliers_humanos")
        after = cur.fetchone()[0]
        print(f"AFTER rows: {after} (delta: +{after - before})")

        # 4. Verificar reales con validation_status='verified_real_official'
        cur.execute("""
            SELECT count(*) FROM public.catastro_suppliers_humanos
            WHERE active = true
              AND contact->>'validation_status' = 'verified_real_official'
        """)
        reales_count = cur.fetchone()[0]
        print(f"Reales activos (validation=verified_real_official): {reales_count}")

        # 5. Verificar placeholders con active=false
        cur.execute("""
            SELECT count(*) FROM public.catastro_suppliers_humanos
            WHERE active = false
              AND contact->>'validation_status' = 'pending_realtime_verification'
        """)
        placeholders_count = cur.fetchone()[0]
        print(f"Placeholders inactivos (validation=pending): {placeholders_count}")

        # 6. Distribución por rol
        cur.execute("""
            SELECT role, count(*), bool_or(active) as has_active
            FROM public.catastro_suppliers_humanos
            GROUP BY role
            ORDER BY role
        """)
        print("\nDistribución por role:")
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]} (algún activo: {row[2]})")

        # Commit transaction
        conn.commit()
        print("\n" + "=" * 60)
        print("TB APPLIED VERDE — transaction committed")
        print("=" * 60)
        return 0

    except Exception as exc:
        conn.rollback()
        print(f"ERROR — rolled back: {exc}", file=sys.stderr)
        return 2
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
