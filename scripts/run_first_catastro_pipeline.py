"""
Sprint 86 Bloque 6 — Primer run productivo del Catastro

Orquestador del primer run REAL del pipeline contra Supabase production.
Diseñado para ser invocado UNA vez (manual) cuando el Hilo Ejecutor confirme:

  1. Migrations 016 + 018 + 019 ejecutadas en Supabase production
  2. SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY exportadas
  3. ARTIFICIAL_ANALYSIS_API_KEY exportada (recomendado para data fresca 2026)
  4. OPENROUTER_API_KEY + HF_TOKEN exportadas (opcionales pero deseables)
  5. fastmcp 3.x instalado (pip install fastmcp==3.2.4) [no bloqueante]

FLUJO:

  [1] Pre-flight Memento (opcional, degraded si library/endpoint caídos)
  [2] Verificación de env vars (required + recommended + optional)
  [3] Construir CatastroPipeline(dry_run=False, skip_persist=False)
  [4] await pipeline.run()
  [5] Llamar catastro_recompute_trono_all() vía RPC (recalcular Trono Score
      tras persistencia de modelos)
  [6] Verificación post-run con SELECT count(*) por tabla (sin filtros)
  [7] Reportar tabla detallada Markdown (modelos por macroárea, eventos,
      trust deltas, top 5 trono por dominio, error_categories observadas)
  [8] Exit code: 0 OK, 1 degradado (<2 fuentes ó persist failure_rate alto),
      2 error fatal

USO:

  # Modo producción (Railway o local con env vars seteadas):
  python3 scripts/run_first_catastro_pipeline.py

  # Modo dry_run (sin red, validar el orquestador):
  CATASTRO_DRY_RUN=true python3 scripts/run_first_catastro_pipeline.py

  # Modo skip-preflight (si Memento aún no está vivo):
  CATASTRO_SKIP_MEMENTO_PREFLIGHT=true python3 scripts/run_first_catastro_pipeline.py

ENV VARS (mismas que kernel/catastro/cron.py):

  SUPABASE_URL                    obligatorio para persistir
  SUPABASE_SERVICE_ROLE_KEY       obligatorio para persistir
  ARTIFICIAL_ANALYSIS_API_KEY     recomendado (data fresca 2026)
  OPENROUTER_API_KEY              opcional
  HF_TOKEN                        opcional
  CATASTRO_DRY_RUN                opcional, default false
  CATASTRO_SKIP_PERSIST           opcional, default false
  CATASTRO_FAILURE_RATE_THRESHOLD opcional, default 0.10
  MONSTRUO_API_KEY                opcional, requerido SOLO si Memento preflight
                                  está activado y el endpoint es público
  CATASTRO_SKIP_MEMENTO_PREFLIGHT opcional, default false. Si true, se omite
                                  el pre-flight Memento (útil en dev / si el
                                  endpoint Memento todavía no está vivo)

EXIT CODES:

  0 — Run exitoso (>=2 fuentes OK, failure_rate <= threshold)
  1 — Run degradado (1 sola fuente OK, ó failure_rate > threshold)
  2 — Error fatal (excepción no controlada, env vars críticas missing,
      Supabase no accesible)

[Hilo Manus Catastro] · Sprint 86 Bloque 6 · 2026-05-04
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Optional

# Asegurar que el repo está en el path
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)


# ============================================================================
# COLORES Y FORMATO (sin dependencias externas)
# ============================================================================

class C:
    RESET = "\033[0m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    OK = "\033[92m"
    WARN = "\033[93m"
    ERR = "\033[91m"
    INFO = "\033[94m"
    HEAD = "\033[95m"


def header(label: str) -> None:
    bar = "=" * 78
    print(f"\n{C.HEAD}{bar}\n  {label}\n{bar}{C.RESET}")


def section(label: str) -> None:
    print(f"\n{C.BOLD}── {label}{C.RESET}")


def ok(msg: str) -> None: print(f"  {C.OK}✓{C.RESET} {msg}")
def warn(msg: str) -> None: print(f"  {C.WARN}⚠{C.RESET} {msg}")
def err(msg: str) -> None: print(f"  {C.ERR}✗{C.RESET} {msg}")
def info(msg: str) -> None: print(f"  {C.INFO}·{C.RESET} {msg}")


# ============================================================================
# PASO 1 — PRE-FLIGHT MEMENTO (OPCIONAL, GRACEFUL)
# ============================================================================

def memento_preflight() -> tuple[bool, Optional[str]]:
    """
    Ejecuta el pre-flight Memento si la library está disponible y el flag
    CATASTRO_SKIP_MEMENTO_PREFLIGHT no está activo.

    Returns:
        (ok, reason) — ok=True si pre-flight pasó o se omitió correctamente.
                       reason solo se llena si ok=False.
    """
    if os.environ.get("CATASTRO_SKIP_MEMENTO_PREFLIGHT", "").lower() in ("true", "1", "yes"):
        warn("Memento pre-flight OMITIDO (CATASTRO_SKIP_MEMENTO_PREFLIGHT=true)")
        return True, None

    try:
        from tools.memento_preflight import preflight_check, MementoPreflightError
    except ImportError as exc:
        warn(f"tools.memento_preflight no disponible ({exc!r}); continuando sin pre-flight")
        return True, None

    try:
        result = preflight_check(
            operation="catastro_first_run_pipeline",
            context_used={
                "sprint": "86",
                "bloque": "6",
                "hilo": "manus_catastro",
                "intent": "primer_run_productivo_catastro",
                "fecha": datetime.now(timezone.utc).isoformat(),
            },
            hilo_id=os.environ.get("MEMENTO_HILO_ID", "manus_catastro"),
            intent_summary="Ejecutar primer run productivo del pipeline Catastro",
            fallback_policy="warn",  # No bloquear si Memento caído
        )
        if getattr(result, "approved", True):
            ok(f"Memento pre-flight APROBADO (cache={getattr(result, 'from_cache', '?')})")
            return True, None
        else:
            err(f"Memento pre-flight RECHAZADO: {getattr(result, 'reason', 'unknown')}")
            return False, "memento_preflight_rejected"
    except MementoPreflightError as exc:
        warn(f"Memento pre-flight ERROR ({exc!r}); continuando con fallback warn")
        return True, None
    except Exception as exc:  # noqa: BLE001
        warn(f"Memento pre-flight CRASH inesperado ({exc!r}); continuando")
        return True, None


# ============================================================================
# PASO 2 — VERIFICACIÓN DE ENV VARS
# ============================================================================

REQUIRED_FOR_PERSISTENCE = ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY")
RECOMMENDED_FOR_FETCH = ("ARTIFICIAL_ANALYSIS_API_KEY",)
OPTIONAL_FOR_FETCH = ("OPENROUTER_API_KEY", "HF_TOKEN")


def check_env() -> dict[str, Any]:
    """Verifica env vars y reporta estado granular."""
    dry_run = os.environ.get("CATASTRO_DRY_RUN", "").lower() in ("true", "1", "yes")
    skip_persist = os.environ.get("CATASTRO_SKIP_PERSIST", "").lower() in ("true", "1", "yes")

    required_missing = [v for v in REQUIRED_FOR_PERSISTENCE if not os.environ.get(v)]
    recommended_missing = [v for v in RECOMMENDED_FOR_FETCH if not os.environ.get(v)]
    optional_missing = [v for v in OPTIONAL_FOR_FETCH if not os.environ.get(v)]

    persistence_ok = (not required_missing) or dry_run or skip_persist
    fetch_ok = len(recommended_missing) == 0 or dry_run

    return {
        "dry_run": dry_run,
        "skip_persist": skip_persist,
        "required_missing": required_missing,
        "recommended_missing": recommended_missing,
        "optional_missing": optional_missing,
        "persistence_ok": persistence_ok,
        "fetch_ok": fetch_ok,
    }


# ============================================================================
# PASO 5 — RECOMPUTE TRONO VIA RPC
# ============================================================================

def recompute_trono_via_rpc(env_status: dict[str, Any]) -> dict[str, Any]:
    """
    Llama a la función PL/pgSQL catastro_recompute_trono_all() vía RPC.

    Returns:
        dict con counts por dominio recalculado, o degraded reason.
    """
    if env_status["dry_run"] or env_status["skip_persist"]:
        return {"skipped": True, "reason": "dry_run_or_skip_persist_active"}
    if env_status["required_missing"]:
        return {"skipped": True, "reason": "supabase_env_vars_missing"}

    try:
        from supabase import create_client
    except ImportError:
        return {"skipped": True, "reason": "supabase_py_not_installed"}

    try:
        client = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        )
        # La función PL/pgSQL catastro_recompute_trono_all() devuelve un JSONB
        # con conteos por dominio recalculado.
        resp = client.rpc("catastro_recompute_trono_all", {}).execute()
        return {"skipped": False, "rpc_response": resp.data}
    except Exception as exc:  # noqa: BLE001
        return {
            "skipped": False,
            "error": str(exc),
            "error_type": type(exc).__name__,
        }


# ============================================================================
# PASO 6 — VERIFICACIÓN POST-RUN (SELECT COUNT POR TABLA)
# ============================================================================

CATASTRO_TABLES = (
    "catastro_modelos",
    "catastro_eventos",
    "catastro_curadores",
    "catastro_quorum_log",
    "catastro_run_metrics",
)


def verify_post_run_counts(env_status: dict[str, Any]) -> dict[str, Any]:
    """SELECT count(*) por cada tabla del Catastro."""
    if env_status["dry_run"] or env_status["required_missing"]:
        return {"skipped": True, "reason": "dry_run_or_env_missing"}

    try:
        from supabase import create_client
    except ImportError:
        return {"skipped": True, "reason": "supabase_py_not_installed"}

    try:
        client = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        )
        counts: dict[str, Any] = {}
        for tbl in CATASTRO_TABLES:
            try:
                # Supabase: select head=true + count='exact' devuelve solo el count
                resp = client.table(tbl).select("*", count="exact", head=True).execute()
                counts[tbl] = resp.count if hasattr(resp, "count") else "?"
            except Exception as exc:  # noqa: BLE001
                counts[tbl] = f"ERROR: {type(exc).__name__}: {exc}"
        return {"skipped": False, "counts": counts}
    except Exception as exc:  # noqa: BLE001
        return {"skipped": False, "error": str(exc), "error_type": type(exc).__name__}


# ============================================================================
# PASO 7 — REPORTE DETALLADO ESTILO COWORK
# ============================================================================

def render_summary_table(summary: dict[str, Any]) -> None:
    """Imprime tabla detallada Markdown del resumen del run."""
    section("Fuentes")
    print(f"  Fuentes OK:    {summary.get('fuentes_ok', [])}")
    print(f"  Fuentes ERROR: {summary.get('fuentes_error', {})}")

    section("Modelos")
    print(f"  Modelos procesados:   {summary.get('modelos_total', 0)}")
    print(f"  Modelos persistibles: {summary.get('modelos_persistibles', 0)}")

    section("Trust deltas (por fuente)")
    for fuente, delta in (summary.get("trust_deltas") or {}).items():
        sign = "+" if delta >= 0 else ""
        color = C.OK if delta >= 0 else C.ERR
        print(f"  {fuente:30s} {color}{sign}{delta:.4f}{C.RESET}")

    section("Trono Summary (Bloque 4)")
    trono = summary.get("trono_summary", {})
    print(f"  Dominios calculados:    {trono.get('dominios', 0)}")
    print(f"  Modelos calculados:     {trono.get('modelos_calculados', 0)}")
    modos = trono.get("modos", {})
    print(f"  Modo z_score: {modos.get('z_score', 0)}, neutral: {modos.get('neutral', 0)}")

    section("Persistencia")
    persist = summary.get("persist_summary", {})
    print(f"  OK:        {persist.get('ok', 0)}")
    print(f"  Dry-run:   {persist.get('dry_run', 0)}")
    print(f"  Failed:    {persist.get('failed', 0)}")
    print(f"  Skipped:   {persist.get('skipped', False)}")
    fr = persist.get("failure_rate_observed", 0.0) or 0.0
    fr_color = C.OK if fr <= 0.10 else C.ERR
    print(f"  Failure rate: {fr_color}{fr:.2%}{C.RESET}")
    cats = persist.get("error_categories", {}) or {}
    if cats:
        print(f"  Error categories:")
        for cat, n in cats.items():
            print(f"    · {cat}: {n}")


def render_macroarea_breakdown(modelos_persistibles: dict[str, dict[str, Any]]) -> None:
    """Tabla Markdown: modelos persistidos agrupados por macroárea."""
    if not modelos_persistibles:
        warn("No hay modelos persistibles para desglosar por macroárea")
        return

    by_macro: dict[str, list[str]] = {}
    for slug, mdata in modelos_persistibles.items():
        macro = mdata.get("macroarea") or "unknown"
        by_macro.setdefault(macro, []).append(slug)

    section("Modelos persistidos por macroárea")
    for macro, slugs in sorted(by_macro.items()):
        print(f"  {C.BOLD}{macro}{C.RESET} ({len(slugs)} modelos)")
        for slug in slugs[:10]:  # cap para legibilidad
            info(slug)
        if len(slugs) > 10:
            info(f"... y {len(slugs) - 10} más")


def render_top5_trono(trono_results: dict[str, list[Any]]) -> None:
    """Top 5 por dominio (Trono Score descendente)."""
    if not trono_results:
        warn("No hay resultados Trono para reportar Top 5")
        return

    section("Top 5 Trono Score por dominio")
    for dominio, results in sorted(trono_results.items()):
        ranked = sorted(results, key=lambda r: r.trono_new, reverse=True)[:5]
        print(f"  {C.BOLD}{dominio}{C.RESET}")
        for i, r in enumerate(ranked, 1):
            mode_tag = f"[{r.mode}]"
            print(f"    {i}. {r.modelo_id:40s} trono={r.trono_new:6.2f}  Δ={r.trono_delta:+.2f}  {mode_tag}")


# ============================================================================
# PASO 8 — EXIT CODE DETERMINATION
# ============================================================================

def determine_exit_code(summary: dict[str, Any], env_status: dict[str, Any]) -> int:
    """0 OK, 1 degradado, 2 fatal."""
    if not summary.get("is_success"):
        return 1

    persist = summary.get("persist_summary", {})
    fr = persist.get("failure_rate_observed", 0.0) or 0.0
    threshold = float(os.environ.get("CATASTRO_FAILURE_RATE_THRESHOLD", "0.10"))
    if fr > threshold and not persist.get("skipped"):
        return 1

    return 0


# ============================================================================
# MAIN
# ============================================================================

async def _run_async() -> int:
    started = datetime.now(timezone.utc)
    header(f"CATASTRO · Primer Run Productivo (Sprint 86 Bloque 6)")
    print(f"  Inicio: {started.isoformat()}")
    print(f"  Host:   {os.environ.get('RAILWAY_SERVICE_NAME', 'local')}")

    # ── PASO 1 ─────────────────────────────────────────────────────
    section("Paso 1 · Memento pre-flight")
    pf_ok, pf_reason = memento_preflight()
    if not pf_ok:
        err(f"Memento pre-flight bloqueó el run: {pf_reason}")
        return 2

    # ── PASO 2 ─────────────────────────────────────────────────────
    section("Paso 2 · Verificación de env vars")
    env_status = check_env()
    info(f"dry_run:               {env_status['dry_run']}")
    info(f"skip_persist:          {env_status['skip_persist']}")
    info(f"required_missing:      {env_status['required_missing']}")
    info(f"recommended_missing:   {env_status['recommended_missing']}")
    info(f"optional_missing:      {env_status['optional_missing']}")

    if env_status["required_missing"] and not env_status["dry_run"] and not env_status["skip_persist"]:
        err(
            f"BLOQUEADO: faltan env vars required {env_status['required_missing']}.\n"
            "  Para correr en modo dry_run:    CATASTRO_DRY_RUN=true python3 scripts/run_first_catastro_pipeline.py\n"
            "  Para correr sin persistir:      CATASTRO_SKIP_PERSIST=true python3 scripts/run_first_catastro_pipeline.py"
        )
        return 2
    if env_status["recommended_missing"] and not env_status["dry_run"]:
        warn(
            f"Recommended missing: {env_status['recommended_missing']}. "
            "El run será degradado (Artificial Analysis fuente principal estará caída)."
        )

    # ── PASO 3+4 ───────────────────────────────────────────────────
    section("Paso 3+4 · Construir + ejecutar pipeline")
    try:
        from kernel.catastro.pipeline import CatastroPipeline
    except Exception as exc:  # noqa: BLE001
        err(f"No pude importar CatastroPipeline: {exc!r}")
        return 2

    pipeline = CatastroPipeline(
        dry_run=env_status["dry_run"],
        skip_persist=env_status["skip_persist"],
    )

    try:
        result = await pipeline.run()
    except Exception as exc:  # noqa: BLE001
        err(f"Pipeline CRASH: {type(exc).__name__}: {exc}")
        import traceback
        traceback.print_exc()
        return 2

    summary = result.summary()

    # ── PASO 5 ─────────────────────────────────────────────────────
    section("Paso 5 · Recompute Trono via RPC")
    trono_recompute = recompute_trono_via_rpc(env_status)
    if trono_recompute.get("skipped"):
        warn(f"Recompute Trono OMITIDO: {trono_recompute.get('reason')}")
    elif trono_recompute.get("error"):
        err(f"Recompute Trono ERROR: {trono_recompute.get('error_type')}: {trono_recompute.get('error')}")
    else:
        ok(f"Recompute Trono OK: {trono_recompute.get('rpc_response')}")

    # ── PASO 6 ─────────────────────────────────────────────────────
    section("Paso 6 · Verificación post-run (SELECT count por tabla)")
    counts = verify_post_run_counts(env_status)
    if counts.get("skipped"):
        warn(f"Verificación OMITIDA: {counts.get('reason')}")
    elif counts.get("error"):
        err(f"Verificación ERROR: {counts.get('error_type')}: {counts.get('error')}")
    else:
        for tbl, n in (counts.get("counts") or {}).items():
            color = C.OK if isinstance(n, int) and n > 0 else (C.ERR if isinstance(n, str) else C.WARN)
            print(f"    {tbl:32s} {color}{n}{C.RESET}")

    # ── PASO 7 ─────────────────────────────────────────────────────
    header("RESUMEN DETALLADO DEL RUN")
    print(f"  Run ID:         {summary['run_id']}")
    print(f"  Started at:     {summary['started_at']}")
    print(f"  Finished at:    {summary['finished_at']}")
    print(f"  Duration:       {summary['duration_seconds']:.2f}s" if summary.get("duration_seconds") else "  Duration: ?")
    print(f"  is_success:     {summary['is_success']}")

    render_summary_table(summary)
    render_macroarea_breakdown(result.modelos_persistibles)
    render_top5_trono(result.trono_results)

    # JSON full para captura en logs
    section("JSON full (para captura en logs Railway)")
    print(json.dumps({"catastro_first_run_summary": summary}, default=str, indent=2))

    # ── PASO 8 ─────────────────────────────────────────────────────
    code = determine_exit_code(summary, env_status)
    finished = datetime.now(timezone.utc)
    elapsed = (finished - started).total_seconds()

    header(f"FIN · exit code = {code} · elapsed = {elapsed:.1f}s")
    if code == 0:
        ok("Run completo OK")
    elif code == 1:
        warn("Run DEGRADADO (1 sola fuente o failure_rate alto)")
    else:
        err("Run FATAL")

    return code


def main() -> int:
    try:
        return asyncio.run(_run_async())
    except KeyboardInterrupt:
        err("Interrumpido por usuario")
        return 130


if __name__ == "__main__":
    sys.exit(main())
