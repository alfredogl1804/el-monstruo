"""
Semilla #38 — Schema authority único: Pydantic generado desde SQL como fuente de verdad

Materializa la heurística H4 candidata (semilla 37) en infraestructura
permanente y auto-validada. Donde la semilla 37 propuso "validar columnas
implícitas en funciones PL/pgSQL", esta semilla cierra el loop completo:
las definiciones Pydantic dejan de ser declaraciones manuales que un Hilo
recuerda y pasan a ser un **espejo bit-perfect del SQL productivo,
generado automáticamente y validado en cada commit**.

Origen:
  Mini-Sprint 86.4.5 pre-B2 (2026-05-05). Cowork detectó después del
  Bloque 1 que 3 bugs estructurales del mismo tipo aparecieron en una
  pasada (`SUPABASE_SERVICE_ROLE_KEY` vs `_KEY`, `last_validated_at`
  vs `ultima_validacion`, `dominio` vs `dominios`). Los 3 son drift
  entre código Python y schema SQL real.

  Manus propuso documentar el schema como markdown estático. Cowork
  rechazó la idea: markdown se desactualiza igual de silenciosamente
  que el código. Aprobó modificada: Pydantic-from-SQL como única
  fuente de verdad, con drift detection automático en CI.

Lección:
  Las definiciones de modelos Python que espejan tablas SQL son una
  fuente PERMANENTE de drift estructural. Mantenerlas a mano garantiza
  bugs intermitentes que escapan a tests mock-based, smoke locales y
  reviews superficiales. La única solución duradera es **generar
  Pydantic desde el SQL DDL como artefacto reproducible**, con audit
  automático que falla en CI ante cualquier divergencia nueva.

Caso real (Mini-Sprint 86.4.5 pre-B2 · 2026-05-05):
  Las migrations 016 + 018 + 019 + 019.1 declaran 5 tablas del Catastro
  con 78 columnas totales. El archivo manual `kernel/catastro/schema.py`
  espejaba 5 modelos Pydantic con 76 campos. Drift latente:
    - `catastro_modelos.validated_by` (de migration 019.1 hotfix)
       NO estaba en el manual.
    - `catastro_curadores.curator_alias` (de migration 016)
       NO estaba en el manual.
  Estos drifts fueron INVISIBLES hasta que el generator nuevo los
  detectó automáticamente. Si el manual hubiera sido la fuente de
  verdad para una nueva query, habrían producido bugs como los del
  Bloque 1 (3 bugs de ese tipo en una sola pasada).

Patrón ganador (infraestructura desplegada en este mini-sprint):
  1. `scripts/_gen_catastro_pydantic_from_sql.py`
     Parsea las migrations PostgreSQL con sqlglot (no-deps, multi-
     dialecto, mantenido). Extrae todas las CREATE TABLE + ALTER
     TABLE ADD COLUMN. Emite `kernel/catastro/schema_generated.py`
     con Pydantic models espejo bit-perfect del SQL. Idempotente.
     Modo `--check` para CI: exit 1 si el archivo está desincronizado.

  2. `scripts/_audit_catastro_schema_drift.py`
     Compara `schema_generated.py` (verdad SQL) vs `schema.py` (manual
     legacy). Mantiene un `BASELINE_DRIFT` con drifts conocidos y
     justificados. Falla en CI cuando aparece un drift NUEVO o cuando
     un drift baseline se vuelve obsoleto. Salida JSON disponible
     para integración programática.

  3. `tests/test_catastro_schema_drift.py`
     12 tests pytest que corren en cada `make test`:
       - El generator existe y es ejecutable.
       - schema_generated.py existe e importa sin errores.
       - Las 5 tablas están todas presentes.
       - `validated_by` está reflejada (caso 019.1).
       - Nombres canónicos correctos (`ultima_validacion`, `dominios`).
       - Pydantic models instanciables.
       - `--check` del generator pasa (no drift contra migrations).
       - Audit drift no detecta drifts NUEVOS.
       - Output JSON del audit es válido.
       - TABLE_COLUMNS coincide con campos Pydantic uno a uno.

  4. `kernel/catastro/schema_generated.py` (artefacto generado)
     Contiene `__SOURCE_HASH__` (sha256 de las migrations) para
     detectar drift sin re-parsear. Contiene `TABLE_COLUMNS` para
     introspección runtime: pre-flight de cualquier query SQL puede
     consultar este dict y validar que las columnas referenciadas
     existen ANTES de invocar al cliente Supabase real.

  5. Doctrina deployment-friendly: `schema.py` manual NO se borra
     todavía. El plan de Cowork es deprecarlo gradualmente (Sprint
     86.5/86.6) cuando haya más migrations cubiertas y más confianza
     en el generator. Mientras tanto, el manual queda como contrato
     externo público (los nombres no rompen consumers existentes)
     y el generated queda como fuente de verdad interna.

Anti-patrón evitado:
  - Documentar el schema en markdown (BrandDNA propuso esto, Cowork
    rechazó porque markdown nadie lo mantiene).
  - Generar Pydantic UNA vez y dejarlo (drift garantizado en 1 mes).
  - Confiar en que el desarrollador "se acuerde" de los nombres reales
    (los 3 bugs del Bloque 1 son la evidencia).
  - Validar solo en runtime (los bugs sólo aparecen en producción
    con datos reales, ver semilla 37).

Diferencias con semilla 37 (que motivó esta semilla):
  - Semilla 37 propone test de paridad SCHEMA ↔ FUNCIÓN para detectar
    columnas inventadas DENTRO de funciones PL/pgSQL.
  - Esta semilla 38 cubre el caso adyacente: drift entre Python (que
    consume la tabla) y SQL (que la define). Las dos semillas son
    complementarias y forman el cinturón de seguridad estructural
    completo del Catastro.

Disciplina específica activada con esta semilla:
  - Toda nueva migration que toque tablas del Catastro debe ir
    seguida de `python3 scripts/_gen_catastro_pydantic_from_sql.py`
    en el mismo commit (regenera schema_generated.py).
  - Si el audit detecta drift NUEVO, el PR no merge hasta que se
    actualice BASELINE_DRIFT con justificación o se sincronice
    schema.py manual.
  - Cuando el manual se deprecue oficialmente, el audit se simplifica
    a comparar solo `schema_generated.py` vs `information_schema.columns`
    de la base productiva (Supabase introspection).

7 Objetivos Maestros que satisface esta semilla:
  Obj #2  Apple/Tesla calidad — bugs estructurales nunca llegan a prod.
  Obj #3  Mínima Complejidad — sqlglot + 200 LOC vs introspection runtime.
  Obj #4  No Equivocarse 2x — los 3 bugs del Bloque 1 nunca repiten.
  Obj #5  Magna/Premium documentación — el schema_generated incluye
          metadata: source_hash, generated_at, migrations parseadas.
  Obj #7  No Inventar Rueda — sqlglot resuelve el parser, no lo escribimos.
  Obj #9  Transversalidad — TABLE_COLUMNS expone el schema a otros
          módulos para pre-flight (Memento H4, Embriones DBA, etc.).
  Obj #12 Soberanía — la fuente de verdad es nuestro SQL, no Supabase
          metadata API que podría cambiar.

Para sembrar al endpoint /v1/error-memory/seed:
  $ python3 scripts/seed_38_schema_authority_unico_pydantic_from_sql.py

Sin red disponible, este archivo solo imprime el JSON sin invocar HTTP.
"""
from __future__ import annotations
import json
import os
import sys
import urllib.request
import urllib.error

SEED = {
    "id": "catastro-schema-authority-unico-pydantic-from-sql",
    "categoria": "infraestructura_anti_drift",
    "severidad": "alta",
    "titulo": (
        "Schema authority unico: Pydantic generado desde SQL como fuente de verdad"
    ),
    "lección": (
        "Las definiciones Pydantic que espejan tablas SQL deben generarse "
        "automaticamente desde las migrations DDL, no escribirse a mano. "
        "Mantener Pydantic manual garantiza drift estructural permanente "
        "que produce bugs invisibles a tests mock-based y smoke locales. "
        "Solo se descubren en runtime con datos reales (ver semilla 37). "
        "Mitigacion: generador SQL->Pydantic con drift detection automatico "
        "en CI mediante baseline conocido. Cualquier drift nuevo falla el "
        "build hasta que se justifique en el baseline o se sincronice."
    ),
    "evidencia": (
        "Mini-Sprint 86.4.5 pre-B2 (2026-05-05). Las migrations del Catastro "
        "declaran 78 columnas en 5 tablas. El archivo manual schema.py espejaba "
        "76 campos: faltaban catastro_modelos.validated_by (migration 019.1) y "
        "catastro_curadores.curator_alias (migration 016). Drifts INVISIBLES "
        "hasta que el generator nuevo los detecto automaticamente con audit. "
        "Los 3 bugs del Bloque 1 86.4.5 (SUPABASE_SERVICE_ROLE_KEY/_KEY, "
        "last_validated_at/ultima_validacion, dominio/dominios) son del mismo "
        "patron y habrian sido detectados pre-deploy con esta infraestructura."
    ),
    "patron_ganador": (
        "1) scripts/_gen_catastro_pydantic_from_sql.py parsea migrations con "
        "sqlglot y emite kernel/catastro/schema_generated.py. Idempotente. "
        "Modo --check para CI. 2) scripts/_audit_catastro_schema_drift.py "
        "compara generated vs manual con BASELINE_DRIFT conocido; falla solo "
        "ante drifts NUEVOS. 3) tests/test_catastro_schema_drift.py corre los "
        "checks en cada pytest run. 4) schema_generated.py incluye TABLE_COLUMNS "
        "para introspeccion runtime usable por pre-flight de queries (Memento "
        "H4, Embrion-DBA, etc.)."
    ),
    "anti_patron_evitado": (
        "Documentar el schema en markdown estatico (nadie lo mantiene). "
        "Generar Pydantic una vez y dejarlo (drift garantizado en 1 mes). "
        "Confiar en que el desarrollador se acuerde de los nombres reales "
        "(los 3 bugs del Bloque 1 son la evidencia). Validar solo en runtime "
        "(bugs aparecen en produccion con datos reales)."
    ),
    "objetivos_satisfechos": [2, 3, 4, 5, 7, 9, 12],
    "sprint": "86.4.5 (mini-sprint pre-B2)",
    "bloque": "Schema Canonico Auto-validado",
    "version": "0.84.8",
    "fecha": "2026-05-05",
    "autor": "Hilo Manus Catastro",
    "co_autor": "Hilo Cowork (audit + aprobacion modificada de propuesta)",
    "complementaria_de": "semilla #37 (validar columnas implicitas en funciones RPC)",
}


def main() -> int:
    endpoint = os.environ.get(
        "MONSTRUO_SEED_ENDPOINT",
        "https://el-monstruo-kernel-production.up.railway.app/v1/error-memory/seed",
    )
    api_key = os.environ.get("MONSTRUO_API_KEY", "").strip()
    print("=" * 76)
    print("SEMILLA #38 - Schema authority unico (Pydantic-from-SQL)")
    print("=" * 76)
    print(json.dumps(SEED, indent=2, ensure_ascii=False))
    print("=" * 76)
    if not api_key:
        print(
            "[INFO] MONSTRUO_API_KEY no presente en el entorno. "
            "Mostrando JSON solamente. No se invoca HTTP."
        )
        return 0
    # Mapeo al schema actual del endpoint (igual que runner _seed_32_to_36):
    # error_signature ← id
    # sanitized_message ← titulo
    # resolution ← consolidacion del resto
    body = {
        "error_signature": SEED["id"],
        "sanitized_message": SEED["titulo"],
        "resolution": json.dumps({
            "leccion": SEED["lección"],
            "evidencia": SEED["evidencia"],
            "patron_ganador": SEED["patron_ganador"],
            "anti_patron_evitado": SEED["anti_patron_evitado"],
            "categoria": SEED["categoria"],
            "severidad": SEED["severidad"],
            "objetivos_satisfechos": SEED["objetivos_satisfechos"],
            "sprint": SEED["sprint"],
            "bloque": SEED["bloque"],
            "version": SEED["version"],
            "fecha": SEED["fecha"],
            "autor": SEED["autor"],
            "co_autor": SEED["co_autor"],
            "complementaria_de": SEED["complementaria_de"],
        }, ensure_ascii=False),
    }
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body_resp = resp.read().decode("utf-8")
            print(f"[OK] HTTP {resp.status}")
            print(body_resp)
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
