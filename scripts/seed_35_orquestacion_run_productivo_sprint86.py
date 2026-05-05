"""
Semilla #35 — Orquestación de runs productivos con coordinación inter-hilo
              (Sprint 86 Bloque 6 — Catastro)

Lección a sembrar en la base error_memory:
  Cuando un dominio del Monstruo (Catastro, Memento, Magna, etc.) llega a
  su primer run productivo contra infra real (Supabase, Railway, APIs
  externas), el orquestador del run NO debe asumir que las dependencias
  externas están listas. Debe validarlas en runtime, degradar
  graciosamente si falta algo, y reportar un bloqueo accionable al hilo
  responsable de cada dependencia. El orquestador del Hilo Diseñador NO
  ejecuta el primer run; ENTREGA herramientas listas y reporta el
  bloqueo al Hilo Ejecutor (mismo patrón que Memento Bloque 4).

Patrón ganador (Catastro Bloque 6):

  scripts/run_first_<dominio>_pipeline.py   ← Orquestador del primer run
    1. Pre-flight Memento (graceful: skip flag, ImportError handling,
       fallback warn si endpoint caído).
    2. Verificación de env vars: required (BLOQUEA), recommended (WARN
       degradado), optional (INFO).
    3. Modo dry_run / skip_persist liberan el bloqueo de required
       (validar el orquestador sin tocar BD).
    4. Construir y ejecutar pipeline.run().
    5. Post-run hooks específicos del dominio (recompute Trono via RPC,
       SELECT count(*) por tabla para validación).
    6. Reporte detallado Markdown con tablas: fuentes, modelos por
       macroárea, trust deltas, top N por métrica, error_categories.
    7. Exit codes claros: 0 OK, 1 degradado, 2 fatal.

  scripts/setup_railway_cron_<dominio>.sh   ← Instrucciones, NO ejecuta
    Bash que solo imprime el manual de configuración del cron en Railway
    Dashboard / CLI / GitHub Actions. NUNCA ejecuta automáticamente
    porque requiere autenticación humana, crea recursos con costo, y
    necesita confirmación antes del primer run productivo.

  scripts/_smoke_<dominio>_first_run.py     ← Smoke E2E contra prod
    Cliente HTTP minimalista (urllib stdlib, cero deps externas) que
    valida POST-RUN: status healthy, recommend devuelve modelos reales,
    get_modelo retorna ficha completa, dominios poblados.

Disciplina de coordinación inter-hilo:

  - El Hilo Diseñador (B) ENTREGA las 3 herramientas listas, validadas
    con tests mock + smoke local.
  - El Hilo Diseñador NUNCA ejecuta el primer run real desde su sandbox
    si:
      a) faltan secrets críticos (SUPABASE_SERVICE_ROLE_KEY, etc.)
      b) las migrations relevantes no están confirmadas en producción
      c) la infra externa (fastmcp, ARTIFICIAL_ANALYSIS_API_KEY) no está
         configurada
  - El Hilo Diseñador documenta el bloqueo en el reporte de cierre del
    bloque, con tabla específica de pendientes asignados a cada hilo.
  - El Hilo Ejecutor (A) corre el primer run cuando todos los pendientes
    están cerrados, captura el log JSON estructurado y lo reporta al
    bridge.
  - El audit Cowork del bloque queda condicionado a que el primer run
    real haya corrido (Fase 2 audit).

Salvaguardas obligatorias (anti-autoboicot):

  - Memento preflight con `fallback_policy="warn"` (NO "block") en runs
    productivos del Catastro: si el endpoint Memento se cae, el
    Catastro no debe quedar bloqueado.
  - http_call usando solo stdlib (urllib.request) en el smoke E2E para
    evitar dependencia httpx/requests que podría no estar instalada en
    el entorno del Hilo Ejecutor.
  - Recompute Trono via RPC SOLO se invoca si dry_run=False y skip_persist=False
    y env vars supabase presentes; en cualquier otro caso retorna
    {skipped: True, reason: ...}.
  - SELECT count(*) post-run usa head=true para no transferir filas; solo
    el conteo. Evita timeouts en tablas grandes.
  - Render functions (summary_table, macroarea_breakdown, top5_trono)
    aceptan dicts/listas vacías sin crashear (Cowork mejora #1: unhappy
    paths cubiertos).

Anti-patrón evitado:

  El Hilo Diseñador NO debe ejecutar `python scripts/run_first_*.py`
  desde su sandbox usando credenciales que "tomó prestadas" del proyecto.
  Esto:
    - Crea registros con autoría incorrecta (catastro_eventos.curador_id
      ó pipeline_run_metrics.run_id apuntan al hilo equivocado).
    - Bypassa el acuerdo inter-hilo de quién es responsable del run.
    - Genera dudas si el run real (cuando llegue) producirá los mismos
      resultados o si hay leak de estado entre runs sandboxeados.
    - Viola la división de responsabilidades de la Regla Dura #5
      AGENTS.md (Fase 1: Hilo B diseña, Hilo A ejecuta).

Patrón de reporte de bloqueo (en bridge/manus_to_cowork.md):

  ```
  ## Bloque <N> — Estado: HERRAMIENTAS LISTAS, RUN PENDIENTE

  Las 3 herramientas del Bloque <N> están entregadas y validadas:
    - scripts/run_first_<dominio>_pipeline.py
    - scripts/setup_railway_cron_<dominio>.sh
    - scripts/_smoke_<dominio>_first_run.py

  Tests: <X>/<X> PASS + smoke local en dry_run PASS.

  Pendiente para Hilo Ejecutor (BLOQUEA primer run real):
    [ ] Migration <NNN> ejecutada en Supabase production
    [ ] <CRED_NAME> exportada en Railway
    [ ] <library>=<version> instalada en Railway

  Una vez cerrados, ejecutar:
    railway run python3 scripts/run_first_<dominio>_pipeline.py
    python3 scripts/_smoke_<dominio>_first_run.py
  ```

Caveats menores (deuda agendada al siguiente bloque):
  - Test de paridad Python ↔ PL/pgSQL para el cálculo Trono
    (Cowork audit B4 caveat menor) — agendado para Bloque 7+ con función
    PostgREST `catastro_compute_trono_python_parity()`.
  - Endpoint admin /v1/catastro/cron/trigger para alternativa GitHub
    Actions si Railway cron añade costo no deseado — agendado Bloque 7+.

ARN: catastro_first_run_pattern_v1
Origen: Sprint 86 Bloque 6 (commit pendiente)
Aplicabilidad: TODOS los dominios del Monstruo que necesiten primer run
               productivo coordinado entre hilos.
"""
import json
import os
import sys
import urllib.request


SEED = {
    "id": "seed_35_orquestacion_run_productivo_v1",
    "version": "1.0",
    "sprint": "86",
    "bloque": "6",
    "categoria": "orquestacion_inter_hilo",
    "titulo": "Orquestación de runs productivos con coordinación inter-hilo",
    "descripcion": (
        "Patrón ganador para el primer run productivo de un dominio del Monstruo: "
        "el Hilo Diseñador entrega herramientas listas (orquestador + setup_cron + "
        "smoke E2E) y delega la ejecución real al Hilo Ejecutor cuando todos los "
        "pendientes externos (migrations, secrets, libraries) están cerrados. "
        "Memento preflight con fallback warn, env vars verificadas en runtime, "
        "modo dry_run/skip_persist libera bloqueos para validar sin tocar BD."
    ),
    "patron_ganador": "Orquestador con verificación runtime + reporte bloqueo accionable",
    "anti_patron_evitado": (
        "Hilo Diseñador ejecuta primer run desde su sandbox con credenciales prestadas, "
        "creando registros con autoría incorrecta y violando división de responsabilidades."
    ),
    "salvaguardas_obligatorias": [
        "Memento preflight fallback_policy=warn (no block) en runs productivos",
        "http_call con urllib.request (stdlib, cero deps externas)",
        "Recompute Trono via RPC SOLO si dry_run=False AND skip_persist=False AND env OK",
        "SELECT count(*) post-run con head=true (no transferir filas)",
        "Render functions aceptan dicts/listas vacías sin crashear",
    ],
    "exit_codes": {
        "0": "Run exitoso (>=2 fuentes OK, failure_rate <= threshold)",
        "1": "Run degradado (1 sola fuente OK, ó failure_rate > threshold)",
        "2": "Error fatal (excepción no controlada, env vars críticas missing)",
    },
    "ejemplo_minimo": (
        "scripts/run_first_<dominio>_pipeline.py: orquestador con 8 pasos\n"
        "scripts/setup_railway_cron_<dominio>.sh: instrucciones bash, no ejecuta\n"
        "scripts/_smoke_<dominio>_first_run.py: smoke E2E con urllib stdlib"
    ),
    "objetivos_maestros_satisfechos": [
        "#3 Mínima Complejidad: 3 archivos pequeños vs 1 monolito",
        "#4 No Equivocarse 2x: validación runtime de cada dependencia externa",
        "#7 No Inventar Rueda: usa tools/memento_preflight + supabase-py + urllib",
        "#9 Transversalidad: patrón aplicable a TODO dominio del Monstruo",
        "#12 Soberanía: smoke con stdlib, sin dependencia externa adicional",
    ],
    "tests_obligatorios": [
        "check_env: dry_run / skip_persist liberan required (sin set explícito)",
        "memento_preflight: skip flag + ImportError + endpoint down todos graceful",
        "render_functions: dicts vacíos no crashean",
        "determine_exit_code: 0/1/2 cubiertos + caso skipped con failure_rate alto",
        "main async dry_run e2e: ejecuta sin errores con CATASTRO_DRY_RUN=true",
    ],
    "deuda_para_siguiente_bloque": [
        "Test de paridad Python ↔ PL/pgSQL para cálculo Trono (caveat audit B4)",
        "Endpoint admin /v1/<dominio>/cron/trigger para GitHub Actions alternativa",
    ],
}


def main() -> int:
    """POST la semilla al endpoint /v1/error-memory/seed."""
    kernel_url = os.environ.get("KERNEL_URL", "https://el-monstruo-mvp.up.railway.app").rstrip("/")
    api_key = os.environ.get("MONSTRUO_API_KEY", "")
    if not api_key:
        print("ERROR: MONSTRUO_API_KEY no configurada. Abortando.")
        print("export MONSTRUO_API_KEY='<tu-key>' && python3 scripts/seed_35_*.py")
        return 1

    url = f"{kernel_url}/v1/error-memory/seed"
    data = json.dumps({"seed": SEED}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            print(f"OK status {resp.status}: {payload}")
            return 0
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: {type(e).__name__}: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
