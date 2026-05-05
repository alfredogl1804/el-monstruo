"""
Semilla #37 — Validar columnas implícitas en funciones RPC PL/pgSQL antes del primer commit
              (Sprint 86 Standby — Catastro · post-mortem migration 019)

Lección a sembrar en la base error_memory:
  Las funciones PL/pgSQL son **lazy-validated**: PostgreSQL parsea su
  cuerpo en `CREATE OR REPLACE FUNCTION` pero NO valida que las columnas
  referenciadas existan en las tablas hasta el primer EXECUTE real con
  un row de datos. Esto significa que una función puede pasar el commit,
  pasar todos los tests unitarios mock-based del dominio, pasar el
  smoke local con FakeClient, ser desplegada a producción, y solo
  fallar cuando el cron real intenta procesar el primer dato verdadero.

Caso real (Catastro · primer run productivo · 2026-05-04):
  Migration 019 reescribió `catastro_apply_quorum_outcome` para soportar
  `curator_alias`. En la transcripción del INSERT/UPSERT, el Hilo
  Catastro inventó una columna `validated_by` (3 referencias en el
  cuerpo de la función) que NUNCA fue declarada en migration 016
  (schema base) ni en ninguna migration posterior. El código Pydantic
  `kernel/catastro/schema.py` tampoco tiene ese campo. La función pasó
  todos los tests mock-based del Bloque 3 (32 tests + 1 opt-in) porque
  el cliente Supabase mockeado nunca ejecuta SQL real, y pasó el smoke
  local del Bloque 6 (orquestador con FakeClient) por la misma razón.
  Solo cuando el Hilo Ejecutor corrió el primer pipeline productivo
  contra Supabase real con 921 modelos scrappeados (37 persistibles),
  los 37 modelos fallaron con APIError 42703 (undefined column).
  Hotfix `019_1_hotfix_validated_by_column.sql` aplicado por Cowork:
    ALTER TABLE catastro_modelos
      ADD COLUMN IF NOT EXISTS validated_by TEXT;
    CREATE INDEX IF NOT EXISTS idx_validated_by_partial
      ON catastro_modelos (validated_by) WHERE validated_by IS NOT NULL;
  Reproducer técnico: `scripts/_debug_catastro_rpc_failure.py`.

Patrón ganador (mitigación obligatoria desde Sprint 86.5+):

  1. Test de paridad SCHEMA ↔ FUNCIÓN obligatorio
     Para cada migration que CREATE OR REPLACE FUNCTION con INSERT/
     UPDATE/UPSERT, agregar test que extraiga columnas referenciadas
     de la función (regex sobre el cuerpo SQL) y compare con
     `information_schema.columns` de la tabla destino. El test FALLA
     antes del commit si hay columnas referenciadas que no existen.

  2. Migration test runner con base PostgreSQL local
     CI debe levantar PostgreSQL ephemeral (Docker), aplicar TODAS las
     migrations en orden, y EJECUTAR cada función RPC con un payload
     sintético mínimo que ejercite todos los paths de INSERT/UPDATE.
     Esto detecta bugs lazy-validated antes de producción. Costo:
     ~5min CI extra. Beneficio: cero bugs como validated_by en prod.

  3. Validación de columnas en code review obligatoria
     Cuando un Hilo escriba o modifique una función PL/pgSQL que toca
     una tabla, el reviewer DEBE leer la lista completa de columnas
     referenciadas y compararlas contra el schema actual (no contra el
     schema "que el Hilo recuerda"). Cowork actuó como red de seguridad
     en este caso, pero no debió haber tenido que.

  4. EXPLAIN o PREPARE en migration tests
     Para validación más liviana sin levantar PostgreSQL completo,
     usar `PREPARE stmt AS <body de la función>` o `EXPLAIN <query>`
     que valida sintaxis y referencias en parse-time. Limitado: solo
     funciona para funciones simples sin variables locales o branches.

  5. Schema delta diff explícito en cada migration
     Cualquier migration que toque una función debe incluir un comentario
     header listando explícitamente las columnas que la función usa,
     con check visual de que cada una existe en una migration previa.
     Ejemplo:
       -- COLUMNAS USADAS POR catastro_apply_quorum_outcome:
       --   catastro_modelos: id, slug, dominios, quality_score,
       --     trono_global, validated_by ← VERIFICAR EN 016
     Si validated_by no aparece en 016, la migration 019 debe
     declararlo o el reviewer debe rechazar el PR.

Anti-patrón evitado (lo que SÍ hicimos en Catastro Bloque 4):
  - Confiar en tests mock-based como prueba de funcionalidad SQL real.
  - Asumir que CREATE OR REPLACE FUNCTION valida referencias.
  - Transcribir cuerpos de funciones sin diff contra el schema base.
  - Saltarse el dry-run real porque "los tests pasan".

Disciplina específica del Catastro tras Sprint 86.7:
  - Agregar `tests/test_catastro_migration_parity.py` que parse el SQL
    de cada `019*.sql`, `018*.sql`, `016*.sql`, extraiga columnas
    referenciadas en INSERT/UPDATE/UPSERT, y valide contra el schema
    de cada tabla declarado en migrations previas.
  - Agregar a CI un job `catastro-migrations-pg-test` con servicio
    PostgreSQL 16 que aplica las migrations y ejecuta `SELECT
    catastro_apply_quorum_outcome(<payload sintético>)`.
  - Agregar al pre-commit hook (cuando se establezca) la regla
    "si modificas un *.sql en scripts/ que toca CREATE FUNCTION,
    debes documentar columnas usadas en el header".

6 Objetivos Maestros que satisface esta semilla:
  Obj #2  Apple/Tesla calidad — bugs en producción son inadmisibles.
  Obj #3  Mínima Complejidad — el test de paridad es ~50 líneas.
  Obj #4  No Equivocarse 2x — esta semilla previene recurrencia.
  Obj #5  Magna/Premium documentación — la lección queda capitalizada.
  Obj #7  No Inventar Rueda — usa pg local en CI, no inventa nada.
  Obj #12 Soberanía — reduce dependencia de "atrape Cowork al vuelo".

Para sembrar al endpoint /v1/error-memory/seed:
  $ python3 scripts/seed_37_validar_columnas_implicitas_funciones_rpc_sprint86.py

Sin red disponible, este archivo solo imprime el JSON sin invocar HTTP.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error


SEED = {
    "id": "catastro-validar-columnas-implicitas-funciones-rpc",
    "categoria": "anti_patron_sql",
    "severidad": "alta",
    "titulo": (
        "Validar columnas implicitas en funciones PL/pgSQL antes del primer commit"
    ),
    "lección": (
        "Las funciones PL/pgSQL son lazy-validated: PostgreSQL acepta CREATE OR "
        "REPLACE FUNCTION con referencias a columnas inexistentes y solo falla en "
        "EXECUTE real con datos. Tests mock-based no detectan este bug porque el "
        "cliente Supabase mockeado nunca ejecuta SQL. Solo se descubre en el "
        "primer run productivo. Mitigacion: test de paridad schema-funcion + "
        "migration test runner con PostgreSQL local en CI + documentacion "
        "explicita de columnas usadas en el header de cada migration."
    ),
    "evidencia": (
        "Catastro · primer run productivo 2026-05-04: 37/37 modelos persistibles "
        "fallaron con APIError 42703 (undefined column validated_by) porque "
        "migration 019 referencia columna nunca declarada en 016. Hotfix 019.1 "
        "aplicado en produccion por Hilo Cowork. Reproducer en "
        "scripts/_debug_catastro_rpc_failure.py."
    ),
    "patron_ganador": (
        "1) tests/test_catastro_migration_parity.py que parse SQL y compara con "
        "information_schema. 2) CI job con PostgreSQL 16 ephemeral que aplica "
        "migrations y ejecuta funciones RPC con payload sintetico. 3) Header "
        "obligatorio en cada migration listando columnas usadas por las "
        "funciones declaradas. 4) Code review explicito de columnas en PRs SQL."
    ),
    "anti_patron_evitado": (
        "Confiar en tests mock-based como prueba de funcionalidad SQL real. "
        "Asumir que CREATE OR REPLACE FUNCTION valida referencias en parse time. "
        "Transcribir cuerpos de funciones sin diff contra schema base."
    ),
    "objetivos_satisfechos": [2, 3, 4, 5, 7, 12],
    "sprint": "86 (post-mortem)",
    "bloque": "Standby Activo",
    "version": "0.86.7",
    "fecha": "2026-05-04",
    "autor": "Hilo Manus Catastro",
    "co_autor": "Hilo Cowork (detector + hotfix)",
}


def main() -> int:
    endpoint = os.environ.get(
        "MONSTRUO_SEED_ENDPOINT",
        "https://el-monstruo-mvp.up.railway.app/v1/error-memory/seed",
    )
    api_key = os.environ.get("MONSTRUO_API_KEY", "").strip()

    print("=" * 76)
    print("SEMILLA #37 - Validar columnas implicitas en funciones RPC PL/pgSQL")
    print("=" * 76)
    print(json.dumps(SEED, indent=2, ensure_ascii=False))
    print("=" * 76)

    if not api_key:
        print(
            "[INFO] MONSTRUO_API_KEY no presente en el entorno. "
            "Mostrando JSON solamente. No se invoca HTTP."
        )
        return 0

    payload = json.dumps(SEED).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            print(f"[OK] HTTP {resp.status}")
            print(body)
            return 0
    except urllib.error.HTTPError as exc:
        print(f"[ERR] HTTP {exc.code}: {exc.reason}")
        try:
            print(exc.read().decode("utf-8"))
        except Exception:  # noqa: BLE001
            pass
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"[ERR] {type(exc).__name__}: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
