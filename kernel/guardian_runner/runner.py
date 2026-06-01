"""
Guardian Runner — orquestador del ciclo evaluativo diario.

Sprint: GUARDIAN-AUTONOMO-001 (T1)
Owner: Hilo Ejecutor 2 (manus_hilo_b)

Responsabilidades:
  1. Invocar `kernel.guardian_runner.scoring.compute_all_scores()` para producir
     el audit de los 15 Objetivos Maestros.
  2. Persistir cada audit en la tabla `public.guardian_audit_log` (migración 0021).
  3. Comparar contra baseline anterior y detectar degradaciones >= 10pp.
  4. Si hay degradaciones críticas y `GUARDIAN_TELEGRAM_ALERTS=true`, invocar
     alertador Telegram (T3, requiere firma humana antes de activar en prod).
  5. Emitir log estructurado para observabilidad.

Diseño anti-Goodhart (DSC-G-008 v2):
  - Las métricas son producidas por evidencia auditable (SQL, filesystem, git).
  - El runner sólo orquesta; NO inventa scores.
  - Si una rúbrica falla por error de I/O, el resultado tiene `status=error`
    y NO se promueve a `passing`. Fail-closed para evitar falsos positivos.

DSCs honrados:
  - DSC-MO-006: No tocar Guardian existente (kernel/guardian.py intacto).
  - DSC-S-006 v1.1: Tabla con RLS por defecto.
  - DSC-G-008 v2: Rúbrica + evidencia + falsadores.
  - DSC-G-017: Audit log auditable y firmable.
  - Anti-autoboicot: validar versión del LLM si se invoca (no aplica aquí).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import socket
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Path setup para import absoluto desde scripts CLI
_KERNEL_ROOT = Path(__file__).resolve().parents[2]
if str(_KERNEL_ROOT) not in sys.path:
    sys.path.insert(0, str(_KERNEL_ROOT))

from kernel.guardian_runner import scoring  # noqa: E402

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────
#  Constantes
# ─────────────────────────────────────────────────────────────────────────

# Umbral de degradación (puntos porcentuales) para emitir alerta crítica
DEGRADATION_ALERT_THRESHOLD_PP = 10.0

# Trigger types canónicos
TRIGGER_TYPES = ("cron", "manual", "post_deploy", "post_pr_merge")


# ─────────────────────────────────────────────────────────────────────────
#  Result dataclass
# ─────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AuditCycleResult:
    """Resultado de un ciclo completo de audit (15 objetivos)."""

    run_id: str
    trigger: str
    started_at: str
    finished_at: str
    duration_ms: int
    total_score_pct: float
    passing_count: int
    warning_count: int
    critical_count: int
    emergency_count: int
    degradations_pp: dict[int, float] = field(default_factory=dict)
    error: str | None = None
    # Sprint GUARDIAN-AUTONOMO-001 T4: detalle por objetivo para el dashboard.
    # Mapeo str(objective_id) -> {score_pct, level, objective_name, rationale, ...}.
    # Keys str por compatibilidad JSON. Default {} mantiene backward-compat.
    objective_scores: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serializar el dataclass a dict (uso interno y por el dashboard)."""
        return {
            "run_id": self.run_id,
            "trigger": self.trigger,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_ms": self.duration_ms,
            "total_score_pct": self.total_score_pct,
            "passing_count": self.passing_count,
            "warning_count": self.warning_count,
            "critical_count": self.critical_count,
            "emergency_count": self.emergency_count,
            "degradations_pp": self.degradations_pp,
            "objective_scores": self.objective_scores,
            "error": self.error,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────────────────
#  Helpers SQL
# ─────────────────────────────────────────────────────────────────────────


def _get_db_url() -> str | None:
    """Resolver URL de Supabase. Prioridad: SUPABASE_DB_URL > DATABASE_URL."""
    return os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")


def _persist_audit(
    *,
    run_id: str,
    objective_id: int,
    objective_name: str,
    rubrica_version: str,
    score_pct: float,
    status: str,
    evidence: list[dict[str, Any]],
    notes: str | None = None,
    sprint_id: str | None = None,
    hilo_origen: str = "guardian_cron",
) -> bool:
    """
    Insertar una fila en guardian_audit_log. Retorna True si se persistió OK.

    Si no hay DB URL (entorno dev sin secrets), loguea WARNING y retorna False.
    """
    db_url = _get_db_url()
    if not db_url:
        logger.warning("guardian_persist_skipped_no_db_url", extra={"run_id": run_id})
        return False

    try:
        import psycopg  # psycopg v3 (requirements.txt: psycopg[binary]==3.3.3)
    except ImportError:
        logger.warning("guardian_persist_skipped_no_psycopg", extra={"run_id": run_id})
        return False

    sql = """
        INSERT INTO public.guardian_audit_log (
            id, run_id, objective_id, objective_name, rubrica_version,
            score_pct, status, evidence_json, notes, sprint_id,
            hilo_origen, created_at
        ) VALUES (
            gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, NOW()
        )
    """

    try:
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        run_id,
                        objective_id,
                        objective_name,
                        rubrica_version,
                        score_pct,
                        status,
                        json.dumps(evidence, ensure_ascii=False),
                        notes,
                        sprint_id,
                        hilo_origen,
                    ),
                )
            conn.commit()
        return True
    except Exception as exc:
        logger.error(
            "guardian_persist_failed",
            extra={"run_id": run_id, "objective_id": objective_id, "error": str(exc)},
        )
        return False


def _fetch_previous_scores(*, max_age_hours: int = 48) -> dict[int, float]:
    """
    Obtener el score más reciente (por objetivo) de las últimas N horas.
    Retorna `{objective_id: score_pct}`. Si no hay DB, retorna dict vacío.
    """
    db_url = _get_db_url()
    if not db_url:
        return {}

    try:
        import psycopg  # psycopg v3
    except ImportError:
        return {}

    sql = """
        SELECT DISTINCT ON (objective_id) objective_id, score_pct
        FROM public.guardian_audit_log
        WHERE created_at > NOW() - INTERVAL '%s hours'
        ORDER BY objective_id, created_at DESC
    """

    try:
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (max_age_hours,))
                rows = cur.fetchall()
        return {int(oid): float(score) for oid, score in rows}
    except Exception as exc:
        logger.error("guardian_fetch_previous_failed", extra={"error": str(exc)})
        return {}


# ─────────────────────────────────────────────────────────────────────────
#  Núcleo: run_audit
# ─────────────────────────────────────────────────────────────────────────


def run_audit(
    *,
    trigger: str = "cron",
    sprint_id: str | None = None,
    persist: bool = True,
    alert_on_degradation: bool = False,
) -> AuditCycleResult:
    """
    Ejecutar un ciclo completo de audit de los 15 Objetivos Maestros.

    Args:
        trigger: tipo de invocación (cron|manual|post_deploy|post_pr_merge).
        sprint_id: opcional, ID del sprint que disparó el audit (para post_pr_merge).
        persist: si False, NO escribe a Supabase (modo dry-run).
        alert_on_degradation: si True y hay degradaciones, dispara alerta Telegram (T3).

    Returns:
        AuditCycleResult con métricas agregadas del ciclo.
    """
    if trigger not in TRIGGER_TYPES:
        raise ValueError(f"trigger inválido: {trigger}. Permitidos: {TRIGGER_TYPES}")

    run_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc)

    logger.info(
        "guardian_audit_started",
        extra={"run_id": run_id, "trigger": trigger, "sprint_id": sprint_id},
    )

    # 1. Computar scores de los 15 objetivos
    try:
        scores_by_id = scoring.compute_all_objectives_scores()
        all_scores = list(scores_by_id.values())
    except Exception as exc:
        finished_at = datetime.now(timezone.utc)
        duration_ms = int((finished_at - started_at).total_seconds() * 1000)
        logger.exception("guardian_audit_failed_in_scoring", extra={"run_id": run_id})
        return AuditCycleResult(
            run_id=run_id,
            trigger=trigger,
            started_at=started_at.isoformat(),
            finished_at=finished_at.isoformat(),
            duration_ms=duration_ms,
            total_score_pct=0.0,
            passing_count=0,
            warning_count=0,
            critical_count=0,
            emergency_count=0,
            error=str(exc),
        )

    # 2. Obtener scores previos para detectar degradaciones
    previous_scores = _fetch_previous_scores(max_age_hours=48)

    # 3. Persistir + agregar estadísticas
    passing = warning = critical = emergency = 0
    total_score = 0.0
    degradations: dict[int, float] = {}

    for objective_score in all_scores:
        oid = objective_score.objective_id

        # Persistir
        if persist:
            _persist_audit(
                run_id=run_id,
                objective_id=oid,
                objective_name=objective_score.objective_name,
                rubrica_version=objective_score.rubrica_version,
                score_pct=objective_score.score_pct,
                status=objective_score.status,
                evidence=[
                    {
                        "metric_key": e.metric_key,
                        "observed_value": e.observed_value,
                        "threshold_min": e.threshold_min,
                        "threshold_max": e.threshold_max,
                        # EvidenceResult no expone weight (es propiedad de la
                        # rubrica YAML, no del resultado); default 1.0 preserva
                        # el schema esperado por guardian_audit_log.
                        "weight": getattr(e, "weight", 1.0),
                        "passed": e.passed,
                    }
                    for e in objective_score.evidence
                ],
                notes=f"trigger={trigger}",
                sprint_id=sprint_id,
                hilo_origen="guardian_cron" if trigger == "cron" else f"guardian_{trigger}",
            )

        # Agregar
        total_score += objective_score.score_pct
        # Normalizar status del scoring engine (que usa 'ok') al vocabulario
        # del Guardian/dashboard (que usa 'passing'). Cualquier status
        # desconocido degrada a 'critical' por safety (fail-closed).
        status_counter = {
            "ok": "passing",  # scoring engine canon
            "passing": "passing",  # alias defensivo
            "warning": "warning",
            "critical": "critical",
            "emergency": "emergency",
            "error": "critical",  # error degrada a critical para safety
        }.get(objective_score.status, "critical")

        if status_counter == "passing":
            passing += 1
        elif status_counter == "warning":
            warning += 1
        elif status_counter == "critical":
            critical += 1
        elif status_counter == "emergency":
            emergency += 1

        # Detectar degradación
        prev = previous_scores.get(oid)
        if prev is not None:
            delta = prev - objective_score.score_pct
            if delta >= DEGRADATION_ALERT_THRESHOLD_PP:
                degradations[oid] = delta

    total_score_pct = total_score / max(len(all_scores), 1)
    finished_at = datetime.now(timezone.utc)
    duration_ms = int((finished_at - started_at).total_seconds() * 1000)

    # Sprint GUARDIAN-AUTONOMO-001 T4: detalle por objetivo para el dashboard.
    # Keys str para serializacion JSON limpia (asyncpg JSONB).
    objective_scores_dict: dict[str, dict[str, Any]] = {}
    for objective_score in all_scores:
        oid = objective_score.objective_id
        objective_scores_dict[str(oid)] = {
            "score_pct": round(objective_score.score_pct, 2),
            "level": objective_score.status,
            "objective_name": objective_score.objective_name,
            "rubrica_version": objective_score.rubrica_version,
            "rationale": getattr(objective_score, "rationale", "") or "",
            "evidence_count": len(objective_score.evidence),
            "evidence_passed": sum(1 for e in objective_score.evidence if e.passed),
        }

    result = AuditCycleResult(
        run_id=run_id,
        trigger=trigger,
        started_at=started_at.isoformat(),
        finished_at=finished_at.isoformat(),
        duration_ms=duration_ms,
        total_score_pct=round(total_score_pct, 2),
        passing_count=passing,
        warning_count=warning,
        critical_count=critical,
        emergency_count=emergency,
        degradations_pp={oid: round(delta, 2) for oid, delta in degradations.items()},
        objective_scores=objective_scores_dict,
    )

    logger.info(
        "guardian_audit_finished",
        extra={
            "run_id": run_id,
            "total_score_pct": result.total_score_pct,
            "passing": passing,
            "warning": warning,
            "critical": critical,
            "emergency": emergency,
            "degradations": len(degradations),
            "duration_ms": duration_ms,
        },
    )

    # 4. T3 placeholder: alerting Telegram (firma humana requerida antes de prod)
    if alert_on_degradation and degradations and os.getenv("GUARDIAN_TELEGRAM_ALERTS") == "true":
        try:
            _emit_telegram_alert(result)
        except Exception:
            logger.exception("guardian_telegram_alert_failed", extra={"run_id": run_id})

    return result


def _emit_telegram_alert(result: AuditCycleResult) -> None:
    """
    Emite alerta a Telegram. PAUSADO en T3 hasta firma humana de Alfredo
    (canal, hora, contenido). Esta función queda como stub registrado para
    que el ciclo no falle, pero no envía nada hasta que `GUARDIAN_TELEGRAM_ALERTS=true`
    Y exista canal autorizado en `TELEGRAM_GUARDIAN_CHAT_ID`.

    Hand-off T3: Alfredo debe firmar `bridge/DSC_TELEGRAM_GUARDIAN_AUTH.md` con:
      - chat_id autorizado
      - ventana de alerta (e.g., 03:00–08:00 UTC, no spam)
      - rate-limit (e.g., 1 alerta por degradación >= 10pp, máx 5/día)
      - formato de mensaje (resumen + link al log)
    """
    chat_id = os.getenv("TELEGRAM_GUARDIAN_CHAT_ID")
    if not chat_id:
        logger.warning(
            "guardian_telegram_alert_skipped_no_chat_id",
            extra={"run_id": result.run_id},
        )
        return

    logger.info(
        "guardian_telegram_alert_would_emit",
        extra={
            "run_id": result.run_id,
            "chat_id": chat_id,
            "degradations": result.degradations_pp,
        },
    )
    # NO IMPLEMENTAR ENVÍO REAL hasta firma humana T3.


# ─────────────────────────────────────────────────────────────────────────
#  Handler async para EmbrionScheduler
# ─────────────────────────────────────────────────────────────────────────


async def daily_guardian_audit_handler(**kwargs: Any) -> dict[str, Any]:
    """
    Handler async registrado en EmbrionScheduler como `daily_guardian_audit`.

    Llamado por el scheduler con kwargs `task_id`, `task_name`, etc.
    Ejecuta el audit en thread pool (es CPU+IO bound, no async-native).

    Returns:
        dict con métricas agregadas. El scheduler lo persiste en su own log.
    """
    sprint_id = kwargs.get("sprint_id")

    # Ejecutar audit en thread pool (psycopg sync no es async)
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: run_audit(
            trigger="cron",
            sprint_id=sprint_id,
            persist=True,
            alert_on_degradation=False,  # T3 pausado hasta firma
        ),
    )

    return {
        "run_id": result.run_id,
        "total_score_pct": result.total_score_pct,
        "passing": result.passing_count,
        "warning": result.warning_count,
        "critical": result.critical_count,
        "emergency": result.emergency_count,
        "degradations": len(result.degradations_pp),
        "duration_ms": result.duration_ms,
        "error": result.error,
        "host": socket.gethostname(),
    }


# ─────────────────────────────────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────────────────────────────────


def main() -> int:
    """CLI: `python -m kernel.guardian_runner.runner --trigger manual --no-persist`."""
    import argparse

    parser = argparse.ArgumentParser(description="Guardian Audit Runner CLI")
    parser.add_argument("--trigger", choices=TRIGGER_TYPES, default="manual")
    parser.add_argument("--sprint-id", default=None)
    parser.add_argument("--no-persist", action="store_true", help="Dry-run: no escribe a Supabase")
    parser.add_argument("--alert", action="store_true", help="Activa alerting Telegram (T3)")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    result = run_audit(
        trigger=args.trigger,
        sprint_id=args.sprint_id,
        persist=not args.no_persist,
        alert_on_degradation=args.alert,
    )

    print(result.to_json())
    return 0 if result.error is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
