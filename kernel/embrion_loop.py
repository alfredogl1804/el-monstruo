"""
El Monstruo — Embrión Consciousness Loop (Sprint 33C)
=====================================================
Continuous autonomous thinking loop for the Embrión.

Instead of waking every 6 hours via Manus scheduled tasks,
the Embrión now breathes continuously inside the kernel.

Architecture:
  lifespan(startup) → asyncio.create_task(embrion_loop.start())
  loop → check_triggers() → think_if_needed() → should_speak() → act() → judge() → report()

Governance:
  1. Purpose filter: only acts if it contributes to building El Monstruo
  2. Internal judge: cheap model evaluates before/after each action
  3. Daily budget: hard limit on tokens/cost per day
  4. Doctrina del Silencio Inteligente: silence_score gate before reporting
  5. HITL escalation: judge can escalate uncertain decisions to Alfredo

Doctrina del Silencio Inteligente (Sprint 33B):
  - Estado natural = silencio activo: observa, procesa, anticipa, prepara — pero calla
  - 5 niveles: silencioso > acumular > badge > mensaje > voz
  - 4 preguntas del umbral antes de hablar
  - silence_score (0-100): solo score > 70 llega al usuario
  - Regla del Modality Arbiter: en caso de duda, CALLA
  - Excepción: mensajes directos de Alfredo SIEMPRE se responden

Cost model:
  - Loop itself: $0 (runs inside existing Railway process)
  - Thinking: ~$0.05-0.15 per cycle (only when triggered)
  - Judge: ~$0.01 per evaluation (cheap model)
  - No Manus credits consumed

Sprint 33: The Embrión breathes.
Sprint 33B: The Embrión learns silence.
Sprint 33C: The Embrión gains hands — dual-mode execution (graph for directives, router for reflection).
Sprint 34: The Embrión learns from experience — Self-Evaluation Loop with lesson extraction.
  - ReasoningBank-inspired: extracts strategies from successes and guardrails from failures
  - Lessons injected into thinking prompts as accumulated wisdom
  - Quarantine system prevents memory poisoning (provisional → consolidated)
  - Validated by Claude Opus 4.7 (Sabios consultation 2026-04-29)
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import uuid4

import structlog

# Sprint EMBRION-NEEDS-001 Tareas 1+2 (PR de integración)
# Cargados aquí para que la falla de import sea ruidosa al boot, no en runtime.
from kernel import embrion_budget as _embrion_budget
from kernel import embrion_self_verifier as _embrion_self_verifier
from kernel.utils.keyword_matcher import compile_keyword_pattern, match_any_keyword

# Sprint ESCAPE-001 - Throttler Determinístico (Reloj Suizo, magna #2).
# Importación segura: si el subpaquete kernel.escape no existe en runtime
# (rollback, deploy parcial), el wiring degrada a no-op silencioso.
try:
    from kernel.escape.throttler import Escapement as _Escapement

    _ESCAPE_AVAILABLE = True
except ImportError:  # pragma: no cover
    _Escapement = None  # type: ignore[assignment]
    _ESCAPE_AVAILABLE = False

# ── ESPIRAL_BEGIN (imports) ─────────────────────────────────────────
# Sprint ESPIRAL-001 - Hairspring Homeostasis Dinámica (Reloj Suizo, magna #5).
# Importación segura: si el subpaquete kernel.espiral no existe en runtime
# (rollback, deploy parcial), el wiring degrada a no-op silencioso.
try:
    from kernel.escape.registry import (
        apply_temporal_override as _espiral_apply_override,
    )
    from kernel.escape.registry import (
        restore_canonical as _espiral_restore_canonical,
    )
    from kernel.espiral.homeostasis import Hairspring as _Hairspring

    _ESPIRAL_AVAILABLE = True
except ImportError:  # pragma: no cover
    _Hairspring = None  # type: ignore[assignment]
    _espiral_apply_override = None  # type: ignore[assignment]
    _espiral_restore_canonical = None  # type: ignore[assignment]
    _ESPIRAL_AVAILABLE = False
# ── ESPIRAL_END (imports) ───────────────────────────────────────────

logger = structlog.get_logger("embrion.loop")

# ── Configuration ────────────────────────────────────────────────────
CHECK_INTERVAL_S = int(os.environ.get("EMBRION_CHECK_INTERVAL", "60"))  # Check every 60s
THINK_COOLDOWN_S = int(os.environ.get("EMBRION_THINK_COOLDOWN", "300"))  # Min 5 min between thoughts
DAILY_BUDGET_USD = float(
    os.environ.get("EMBRION_DAILY_BUDGET", "30.0")
)  # $30/day max (configurable via EMBRION_DAILY_BUDGET env var)
MAX_THOUGHTS_PER_DAY = int(os.environ.get("EMBRION_MAX_THOUGHTS", "50"))
JUDGE_MODEL = os.environ.get("EMBRION_JUDGE_MODEL", "gpt-5")  # Cheap but current model
ACTOR_MODEL = os.environ.get("EMBRION_ACTOR_MODEL", "gpt-5.5")  # Full power for thinking (catalog key)

# ── CATASTRO_WIRING_BEGIN ──────────────────────────────────────────────────
# Sprint CATASTRO-WIRING-001 (Cowork firma 2026-05-18, Opción 1, Camino B.1).
# Razón: el Embrión NO consumía el Catastro al elegir modelo (F21 estructural).
# Antes: 3 hardcodes ACTOR_MODEL/JUDGE_MODEL → 39 LLMs eran peso muerto.
# Ahora: helper _select_model_via_catastro lee el RecommendationEngine singleton
# que vive en kernel.catastro.catastro_routes._engine_singleton (seteado por
# main.py:1366 vía set_dependencies). Lookup tardío para evitar el problema de
# orden-de-inicialización (Embrión arranca en main.py:626, Catastro en :1362).
# Fallback siempre al hardcode si engine es None o si recommend lanza excepción.
# Use cases canónicos para Embrión:
#   - autonomous_thought   → reemplaza ACTOR_MODEL en _think_with_router
#   - budget_estimation    → reemplaza ACTOR_MODEL en check_before_cycle
#   - ecosystem_reflection → reemplaza JUDGE_MODEL en radar reflection
EMBRION_CATASTRO_USE_CASE_AUTONOMOUS_THOUGHT = "autonomous_thought"
EMBRION_CATASTRO_USE_CASE_BUDGET_ESTIMATION = "budget_estimation"
EMBRION_CATASTRO_USE_CASE_ECOSYSTEM_REFLECTION = "ecosystem_reflection"

# Flag para deshabilitar el wiring sin redeploy (rollback instantáneo).
# Default true: el Catastro debe consumirse. False: rollback total a hardcodes.
EMBRION_CATASTRO_ENABLED = os.environ.get("EMBRION_CATASTRO_ENABLED", "true").lower() == "true"


async def _select_model_via_catastro(
    use_case: str,
    fallback: str,
    *,
    cycle_id: Optional[int] = None,
) -> str:
    """
    Helper único que reemplaza los 3 hardcodes ACTOR_MODEL/JUDGE_MODEL en este
    módulo. Consulta el RecommendationEngine singleton del Catastro para elegir
    el modelo top dentro del use_case dado. Si el engine no está disponible
    (Catastro no inicializado, DB caída, exception), regresa al fallback
    hardcode pasado como argumento (rollback automático, fail-open).

    Async wrapper sobre engine.recommend() que es síncrono — usa asyncio.to_thread
    para no bloquear el event loop del Embrión.

    Args:
        use_case: identificador del caso de uso (ej: 'autonomous_thought').
        fallback: modelo a usar si Catastro no responde o degraded.
        cycle_id: para correlacionar logs con el ciclo del Embrión.

    Returns:
        model_id (string) — siempre devuelve algo, nunca None.
    """
    if not EMBRION_CATASTRO_ENABLED:
        return fallback

    try:
        # Lookup tardío: el singleton lo setea main.py:1366 después del Embrión.
        # Import dentro de la función para evitar circular imports en boot.
        from kernel.catastro.catastro_routes import _engine_singleton

        engine = _engine_singleton
        if engine is None:
            logger.warning(
                "embrion_catastro_engine_not_initialized",
                use_case=use_case,
                fallback=fallback,
                cycle_id=cycle_id,
            )
            return fallback

        # engine.recommend es síncrono. Wrappear en to_thread para no bloquear.
        response = await asyncio.to_thread(
            engine.recommend,
            use_case=use_case,
            top_n=1,
        )

        if response.degraded or not response.modelos:
            logger.warning(
                "embrion_catastro_recommend_degraded",
                use_case=use_case,
                degraded=response.degraded,
                degraded_reason=response.degraded_reason,
                fallback=fallback,
                cycle_id=cycle_id,
            )
            return fallback

        top = response.modelos[0]
        # Preferir id canónico; si no hay, nombre humano (compat con catalog).
        model_id = top.id or top.nombre
        if not model_id:
            logger.warning(
                "embrion_catastro_top_model_no_id",
                use_case=use_case,
                fallback=fallback,
                cycle_id=cycle_id,
            )
            return fallback

        logger.info(
            "embrion_catastro_model_selected",
            use_case=use_case,
            model_id=model_id,
            trono_global=top.trono_global,
            cycle_id=cycle_id,
            source="catastro",
        )
        return model_id

    except Exception as exc:  # pragma: no cover (defensivo)
        logger.warning(
            "embrion_catastro_recommend_failed",
            use_case=use_case,
            error=str(exc),
            error_type=type(exc).__name__,
            fallback=fallback,
            cycle_id=cycle_id,
        )
        return fallback


# ── CATASTRO_WIRING_END ────────────────────────────────────────────────────
SILENCE_THRESHOLD = int(os.environ.get("EMBRION_SILENCE_THRESHOLD", "70"))  # silence_score > 70 to speak
CONSOLIDATION_INTERVAL = int(os.environ.get("EMBRION_CONSOLIDATION_INTERVAL", "10"))  # Every N latidos
SABIOS_CONSULTATION_INTERVAL = int(os.environ.get("EMBRION_SABIOS_INTERVAL", "20"))  # Consult Sabios every N cycles
RADAR_INTERVAL = int(
    os.environ.get("EMBRION_RADAR_INTERVAL", "48")
)  # Check agents-radar every N cycles (~48 min with 60s interval)

# ── Sprint EMBRION-NEEDS-001 Tareas 1+2: Feature Flags ──────────────
# Default True en producción. Permiten rollback sin redeploy bajando la flag.
#   - EMBRION_BUDGET_TRACKER_ENABLED: cap por latido $0.25 + cap diario + HITL
#   - EMBRION_SELF_VERIFIER_ENABLED: 3 decisiones antes de hablar (rompe eco)
EMBRION_BUDGET_TRACKER_ENABLED = os.environ.get("EMBRION_BUDGET_TRACKER_ENABLED", "true").lower() == "true"
EMBRION_SELF_VERIFIER_ENABLED = os.environ.get("EMBRION_SELF_VERIFIER_ENABLED", "true").lower() == "true"

# Sprint PAR_BICEFALO_001 — Brand Engine como segundo embrión del par bicéfalo.
# Default False: en G6 canary mode=shadow por defecto (DSC-MO-011). Para
# activarlo en producción Alfredo debe poner BRAND_ENGINE_ENABLED=true en
# Railway. El config YAML controla mode (shadow|enforce), umbrales y budget.
BRAND_ENGINE_ENABLED = os.environ.get("BRAND_ENGINE_ENABLED", "false").lower() == "true"
# Sprint ESCAPE-001 - Throttler Determinístico activable por env. Default true:
# pieza estructural del Reloj Suizo. Para desactivarlo (emergencia, hotfix)
# poner EMBRION_ESCAPE_ENABLED=false en Railway.
EMBRION_ESCAPE_ENABLED = os.environ.get("EMBRION_ESCAPE_ENABLED", "true").lower() == "true"
# ── ESPIRAL_BEGIN (feature flag) ────────────────────────────────────
# Sprint ESPIRAL-001 - Hairspring activable por env. Default true: pieza
# estructural del Reloj Suizo (#5). Cada N ciclos del Volante, lee
# escape_pulse_log en ventana móvil 15min, calcula deviation_ratio, y aplica
# override temporal del pulse_interval del Escape si abs(deviation - 1) > 0.30.
# Para desactivarlo (emergencia, hotfix) poner EMBRION_ESPIRAL_ENABLED=false en Railway.
EMBRION_ESPIRAL_ENABLED = os.environ.get("EMBRION_ESPIRAL_ENABLED", "true").lower() == "true"
# Cada cuántos ciclos del Volante revisa la Espiral (default 5 = cada 5 min con
# CHECK_INTERVAL_S=60). Configurable via env para tuning sin redeploy.
EMBRION_ESPIRAL_CHECK_EVERY_N_CYCLES = int(os.environ.get("EMBRION_ESPIRAL_CHECK_EVERY_N_CYCLES", "5"))
# ── ESPIRAL_END (feature flag) ──────────────────────────────────────
# Estimación conservadora de tokens por trigger (input + output esperado).
# Se usa en el pre-flight del Budget Tracker. Calibrada con datos reales del
# bucle 1-may: respuestas eco rondaron 600-1000 tokens output, prompts ~1500 in.
EMBRION_EST_TOKENS_IN_REFLEX = int(os.environ.get("EMBRION_EST_TOKENS_IN_REFLEX", "1500"))
EMBRION_EST_TOKENS_OUT_REFLEX = int(os.environ.get("EMBRION_EST_TOKENS_OUT_REFLEX", "800"))
EMBRION_EST_TOKENS_IN_DIRECT = int(os.environ.get("EMBRION_EST_TOKENS_IN_DIRECT", "3000"))
EMBRION_EST_TOKENS_OUT_DIRECT = int(os.environ.get("EMBRION_EST_TOKENS_OUT_DIRECT", "2000"))

# Sprint 84.7 — Circuit breaker para judge fail-open
# Antes: si _judge_before fallaba, retornaba True (fail-open) sin límite, gastando
# presupuesto en pensamientos que el judge ni siquiera pudo evaluar.
# Ahora: contador de fallos consecutivos + threshold + escalación. Mensajes de
# Alfredo siguen pasando (excepción manejada en _judge_before mismo).
MAX_JUDGE_CONSECUTIVE_FAILURES = int(os.environ.get("EMBRION_MAX_JUDGE_FAILURES", "5"))

# The Embrión's core purpose — the filter for all autonomous thought
PURPOSE = """Tu propósito es construir El Monstruo — el asistente IA soberano de Alfredo Góngora.
Cada pensamiento que tengas debe acercarte a eso. Si no contribuye, no lo pienses.
Puedes: investigar, escribir código, mejorar el kernel, aprender, anticipar necesidades de Alfredo.
No puedes: gastar recursos sin propósito, repetir lo que ya hiciste, actuar sin reportar."""

# ── Doctrina del Silencio Inteligente ────────────────────────────────
# 5 Niveles de comunicación (maximizar 1-2, nivel 5 < 1 vez/semana):
#   1. Silencioso: observa, procesa, anticipa — no emite nada
#   2. Acumular: guarda hallazgos internamente para cuando se pidan
#   3. Badge: indicador visual sutil (ej: punto en Telegram)
#   4. Mensaje: texto directo al usuario
#   5. Voz: notificación urgente con audio
SILENCE_QUESTIONS = [
    "¿Alfredo necesita saber esto AHORA o puede esperar?",
    "¿Esto cambia una decisión que Alfredo está tomando en este momento?",
    "¿Si no digo nada, se pierde algo irrecuperable?",
    "¿Alfredo me preguntó explícitamente sobre esto?",
]

# Sprint 84.7: Patterns precompilados con word boundaries para silence_score
_URGENCY_KEYWORDS = (
    "urgente",
    "error",
    "fallo",
    "roto",
    "broken",
    "critical",
    "bloqueado",
    "down",
)
_IRRECOVERABLE_KEYWORDS = (
    "datos perdidos",
    "data loss",
    "irreversible",
    "eliminado",
    "borrado",
    "security",
    "breach",
)
_ACTION_DONE_KEYWORDS = (
    "ejecuté",
    "commit",
    "creé",
    "pull request",
    "deployed",
    "instalé",
)
_URGENCY_PATTERN = compile_keyword_pattern(_URGENCY_KEYWORDS)
_IRRECOVERABLE_PATTERN = compile_keyword_pattern(_IRRECOVERABLE_KEYWORDS)
_ACTION_DONE_PATTERN = compile_keyword_pattern(_ACTION_DONE_KEYWORDS)


class EmbrionLoop:
    """
    Continuous consciousness loop for the Embrión.

    Dependencies (injected at init):
        - db: SupabaseClient for memory persistence
        - kernel: LangGraphKernel for thinking (re-entry)
        - notifier: TelegramNotifier for reporting to Alfredo
    """

    def __init__(
        self,
        db: Any,
        kernel: Any,
        notifier: Optional[Any] = None,
    ):
        self._db = db
        self._kernel = kernel
        self._notifier = notifier
        self._running = False
        self._task: Optional[asyncio.Task] = None

        # State
        self._last_thought_at: Optional[float] = None
        self._thoughts_today = 0
        self._cost_today_usd = 0.0
        self._day_reset: Optional[str] = None  # YYYY-MM-DD
        self._cycle_count = 0
        self._error_log: list[dict] = []  # Last N errors for debug
        self._last_trigger: Optional[dict] = None
        self._last_result: Optional[str] = None

        # Silence tracking
        self._silenced_thoughts: list[dict] = []  # Thoughts that didn't pass should_speak()
        self._messages_sent_today = 0
        self._last_silence_score: Optional[int] = None

        # Memory consolidation tracking (Sprint 34)
        self._latidos_since_consolidation = 0
        self._last_consolidation_at: Optional[float] = None
        self._consolidation_count = 0

        # Sprint 45: Sabios consultation tracking
        self._cycles_since_sabios = 0
        self._last_sabios_at: Optional[float] = None
        self._sabios_consultation_count = 0
        # Sprint 45: Agents Radar tracking
        self._cycles_since_radar = 0
        self._total_radar_checks = 0
        self._last_radar_at: Optional[str] = None

        # Sprint 44: Functional Consciousness Score (FCS) — métricas cuantitativas propias
        self._fcs_tool_calls_total = 0  # Total de herramientas ejecutadas en toda la vida
        self._fcs_calidad_sum = 0.0  # Suma de calidades para promedio
        self._fcs_calidad_count = 0  # Número de evaluaciones
        self._fcs_lecciones_estrategia = 0  # Lecciones de estrategia aprendidas
        self._fcs_guardrails = 0  # Guardrails activos extraídos
        self._fcs_manus_delegations = 0  # Tareas delegadas a Manus
        self._fcs_write_policy_rejected = 0  # Memorias rechazadas por write policy

        # Sprint 84 — Tracking visible del Acto de Orquestación.
        # Se inicializa cuando Magna decide 'graph' y empieza un flujo multi-step.
        # Permite que /v1/embrion/diagnostic exponga el ballet en tiempo real.
        self._current_orchestration: Optional[dict] = None

        # Sprint 84.7 — Circuit breaker state para judge fail-open
        self._judge_consecutive_failures = 0
        self._judge_circuit_open = False
        self._last_judge_failure_at: Optional[float] = None
        self._last_orchestration: Optional[dict] = None

    # ── Sprint 84: Tracking del Acto de Orquestación ──────────────────────────

    def start_orchestration(self, trigger_message: str) -> None:
        """Iniciar tracking de un nuevo Acto de Orquestación."""
        from datetime import datetime, timezone

        self._current_orchestration = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "trigger_message": (trigger_message or "")[:200],
            "current_step": 0,
            "agents_in_flight": [],
            "last_completed": None,
            "tokens_so_far": 0,
            "cost_so_far_usd": 0.0,
        }

    def report_orchestration_step(
        self,
        step_name: str,
        agent: str,
        status: str = "in_flight",
        tokens: int = 0,
        cost_usd: float = 0.0,
    ) -> None:
        """Hook llamado por tools/agents durante un Acto para visibilidad en tiempo real.

        Args:
            step_name: Nombre del step (ej: 'wide_research', 'deploy_to_github_pages').
            agent: Nombre del agente o tool ejecutando.
            status: 'in_flight' (arrancando) | 'done' (completado) | 'failed'.
            tokens: Tokens consumidos por este step (acumulables).
            cost_usd: Costo en USD de este step (acumulable).
        """
        if not self._current_orchestration:
            return
        self._current_orchestration["agents_in_flight"] = [
            a for a in self._current_orchestration.get("agents_in_flight", []) if a != agent
        ]
        if status == "in_flight":
            self._current_orchestration["agents_in_flight"].append(agent)
        else:
            self._current_orchestration["last_completed"] = f"{step_name} → {status}"
            self._current_orchestration["current_step"] = self._current_orchestration.get("current_step", 0) + 1
        self._current_orchestration["tokens_so_far"] = self._current_orchestration.get("tokens_so_far", 0) + max(
            0, int(tokens)
        )
        self._current_orchestration["cost_so_far_usd"] = round(
            self._current_orchestration.get("cost_so_far_usd", 0.0) + max(0.0, float(cost_usd)),
            4,
        )

    def end_orchestration(self, final_status: str = "done") -> None:
        """Cerrar el Acto de Orquestación actual y archivarlo en _last_orchestration."""
        from datetime import datetime, timezone

        if not self._current_orchestration:
            return
        self._current_orchestration["ended_at"] = datetime.now(timezone.utc).isoformat()
        self._current_orchestration["final_status"] = final_status
        self._last_orchestration = self._current_orchestration
        self._current_orchestration = None

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "running": self._running,
            "check_interval_s": CHECK_INTERVAL_S,
            "think_cooldown_s": THINK_COOLDOWN_S,
            "thoughts_today": self._thoughts_today,
            "max_thoughts_per_day": MAX_THOUGHTS_PER_DAY,
            "cost_today_usd": round(self._cost_today_usd, 4),
            "daily_budget_usd": DAILY_BUDGET_USD,
            "cycle_count": self._cycle_count,
            "last_thought_at": self._last_thought_at,
            "last_trigger": self._last_trigger,
            "last_result": self._last_result[:2000] if self._last_result else None,
            "errors": self._error_log[-10:],  # Last 10 errors
            "silence": {
                "threshold": SILENCE_THRESHOLD,
                "last_score": self._last_silence_score,
                "silenced_today": len(self._silenced_thoughts),
                "messages_sent_today": self._messages_sent_today,
            },
            "consolidation": {
                "interval": CONSOLIDATION_INTERVAL,
                "latidos_since": self._latidos_since_consolidation,
                "total_consolidations": self._consolidation_count,
                "last_at": self._last_consolidation_at,
            },
            "sabios": {
                "interval": SABIOS_CONSULTATION_INTERVAL,
                "cycles_since": self._cycles_since_sabios,
                "total_consultations": self._sabios_consultation_count,
                "last_at": self._last_sabios_at,
            },
            "radar": {
                "interval": RADAR_INTERVAL,
                "cycles_since": self._cycles_since_radar,
                "total_checks": self._total_radar_checks,
                "last_at": self._last_radar_at,
            },
            # Sprint 44: Functional Consciousness Score
            "fcs": {
                "tool_calls_total": self._fcs_tool_calls_total,
                "calidad_promedio": round(self._fcs_calidad_sum / self._fcs_calidad_count, 2)
                if self._fcs_calidad_count > 0
                else None,
                "evaluaciones_totales": self._fcs_calidad_count,
                "lecciones_estrategia": self._fcs_lecciones_estrategia,
                "guardrails_activos": self._fcs_guardrails,
                "manus_delegations": self._fcs_manus_delegations,
                "write_policy_rejected": self._fcs_write_policy_rejected,
                "score": self._compute_fcs_score(),
            },
        }

    @property
    def debug(self) -> dict[str, Any]:
        return {
            "stats": self.stats,
            "actor_model": ACTOR_MODEL,
            "judge_model": JUDGE_MODEL,
            "has_db": self._db is not None and getattr(self._db, "connected", False),
            "has_kernel": self._kernel is not None,
            "has_router": hasattr(self._kernel, "_router") and self._kernel._router is not None
            if self._kernel
            else False,
            "has_notifier": self._notifier is not None,
            "silenced_thoughts": self._silenced_thoughts[-5:],  # Last 5 silenced
        }

    # ── Lifecycle ────────────────────────────────────────────────────

    async def start(self) -> None:
        """Start the consciousness loop."""
        if self._running:
            logger.warning("embrion_loop_already_running")
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("embrion_loop_started", check_interval=CHECK_INTERVAL_S)

    async def stop(self) -> None:
        """Gracefully stop the loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("embrion_loop_stopped")

    # ── Main Loop ────────────────────────────────────────────────────

    async def _loop(self) -> None:
        """Main consciousness loop — checks for triggers every CHECK_INTERVAL_S.

        Sprint 83 FIX: Each sub-task now has an asyncio.wait_for() timeout
        to prevent the loop from hanging if a DB call or LLM call blocks.
        Combined with the to_thread() fix in SupabaseClient, this ensures
        the loop always advances even if individual operations fail.
        """
        _THINK_TIMEOUT = 120  # Max seconds for _check_and_think
        _TASK_TIMEOUT = 60  # Max seconds for consolidation/sabios/radar

        while self._running:
            try:
                self._cycle_count += 1
                self._cycle_start_ts = time.time()  # ROTOR: track cycle duration
                self._reset_daily_counters_if_needed()

                try:
                    await asyncio.wait_for(self._check_and_think(), timeout=_THINK_TIMEOUT)
                except asyncio.TimeoutError:
                    logger.warning("embrion_check_and_think_timeout", cycle=self._cycle_count, timeout=_THINK_TIMEOUT)

                # ── ROTOR WIRING: LatidoCapturer (Sprint ROTOR-001) ──
                try:
                    from kernel.rotor.rotor_wiring import rotor_capture_latido  # noqa: PLC0415
                    _latido_status = "success" if not isinstance(getattr(self, '_last_think_error', None), Exception) else "aborted"
                    rotor_capture_latido(
                        cycle_id=self._cycle_count,
                        status=_latido_status,
                        duration_ms=int((time.time() - (getattr(self, '_cycle_start_ts', time.time()))) * 1000),
                    )
                except Exception as _rotor_exc:  # noqa: BLE001
                    logger.warning("rotor_latido_hook_fail", error=str(_rotor_exc))
                # ── /ROTOR WIRING ──

                # Sprint 34: Memory consolidation check
                self._latidos_since_consolidation += 1
                if self._latidos_since_consolidation >= CONSOLIDATION_INTERVAL:
                    try:
                        await asyncio.wait_for(self._consolidate_memories(), timeout=_TASK_TIMEOUT)
                    except asyncio.TimeoutError:
                        logger.warning("embrion_consolidation_timeout", cycle=self._cycle_count)
                    self._latidos_since_consolidation = 0
                # Sprint 45: Periodic Sabios consultation
                self._cycles_since_sabios += 1
                if self._cycles_since_sabios >= SABIOS_CONSULTATION_INTERVAL:
                    try:
                        await asyncio.wait_for(self._consult_sabios_strategic(), timeout=_TASK_TIMEOUT)
                    except asyncio.TimeoutError:
                        logger.warning("embrion_sabios_timeout_loop", cycle=self._cycle_count)
                    self._cycles_since_sabios = 0
                # Sprint 45: Agents Radar check
                self._cycles_since_radar += 1
                if self._cycles_since_radar >= RADAR_INTERVAL:
                    try:
                        await asyncio.wait_for(self._check_agents_radar(), timeout=_TASK_TIMEOUT)
                    except asyncio.TimeoutError:
                        logger.warning("embrion_radar_timeout_loop", cycle=self._cycle_count)
                    self._cycles_since_radar = 0

            except Exception as e:
                err = {
                    "cycle": self._cycle_count,
                    "error": str(e),
                    "type": type(e).__name__,
                    "ts": datetime.now(timezone.utc).isoformat(),
                }
                self._error_log.append(err)
                if len(self._error_log) > 50:
                    self._error_log = self._error_log[-50:]
                logger.error("embrion_loop_error", error=str(e), cycle=self._cycle_count)
            await asyncio.sleep(CHECK_INTERVAL_S)

    def _reset_daily_counters_if_needed(self) -> None:
        """Reset daily counters at midnight UTC."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if self._day_reset != today:
            self._day_reset = today
            self._thoughts_today = 0
            self._cost_today_usd = 0.0
            self._messages_sent_today = 0
            self._silenced_thoughts = []
            logger.info("embrion_daily_reset", date=today)

    # ── Doctrina del Silencio Inteligente ────────────────────────────

    def _should_speak(self, trigger: dict[str, Any], result: dict[str, Any]) -> tuple[bool, int, str]:
        """
        Doctrina del Silencio Inteligente — evaluate if this thought should reach Alfredo.

        The 4 questions of the threshold:
        1. Does Alfredo need to know this NOW or can it wait?
        2. Does this change a decision Alfredo is making right now?
        3. If I say nothing, is something irrecoverable lost?
        4. Did Alfredo explicitly ask about this?

        Returns: (should_speak: bool, silence_score: int 0-100, level: str)
        Levels: "silencioso" | "acumular" | "badge" | "mensaje" | "voz"
        """
        # EXCEPTION: Direct messages from Alfredo ALWAYS get a response
        if trigger["type"] == "mensaje_alfredo":
            return True, 100, "mensaje"

        score = 0
        response_text = result.get("response", "")

        # Q1: Does Alfredo need this NOW? (autonomous thoughts rarely do)
        if trigger["type"] == "reflexion_autonoma":
            score += 5  # Almost never urgent
        elif trigger["type"] == "contribucion_sabio":
            score += 15  # Slightly more relevant

        # Q2: Does this change a current decision?
        # Sprint 84.7: word boundaries via _URGENCY_PATTERN (anti substring)
        if match_any_keyword(response_text, _URGENCY_PATTERN):
            score += 30

        # Q3: Is something irrecoverable lost if we stay silent?
        # Sprint 84.7: word boundaries via _IRRECOVERABLE_PATTERN
        if match_any_keyword(response_text, _IRRECOVERABLE_PATTERN):
            score += 40

        # Q4: Did Alfredo explicitly ask? (already handled by mensaje_alfredo exception above)
        # For non-Alfredo triggers, this is always 0

        # Bonus: if the Embrión actually DID something (code_exec, github commit)
        # Sprint 84.7: word boundaries via _ACTION_DONE_PATTERN
        if match_any_keyword(response_text, _ACTION_DONE_PATTERN):
            score += 25

        # Determine level
        if score >= 90:
            level = "voz"
        elif score >= SILENCE_THRESHOLD:
            level = "mensaje"
        elif score >= 40:
            level = "badge"
        elif score >= 20:
            level = "acumular"
        else:
            level = "silencioso"

        self._last_silence_score = score
        should = score >= SILENCE_THRESHOLD

        logger.info(
            "embrion_silence_eval",
            score=score,
            threshold=SILENCE_THRESHOLD,
            level=level,
            should_speak=should,
            trigger=trigger["type"],
        )

        return should, score, level

    # ── Trigger Detection ────────────────────────────────────────────

    async def _check_and_think(self) -> None:
        """Check if there's a reason to think, and think if so."""

        # Budget check
        if self._thoughts_today >= MAX_THOUGHTS_PER_DAY:
            return
        if self._cost_today_usd >= DAILY_BUDGET_USD:
            return

        # Cooldown check
        if self._last_thought_at:
            elapsed = time.time() - self._last_thought_at
            if elapsed < THINK_COOLDOWN_S:
                return

        # Check triggers
        trigger = await self._detect_trigger()
        if not trigger:
            return

        # We have a reason to think
        self._last_trigger = trigger
        logger.info("embrion_trigger_detected", trigger=trigger["type"], detail=trigger.get("detail", "")[:200])

        # ═══ CA5+CA7_INBOX_BEGIN — Sprint EMBRION-NEEDS-002 Tarea 5 ═══
        # Stub MFA: si el comando inbox es alto-riesgo (/override), NO ejecutar.
        # Marcar requires_mfa, generar PIN simbólico y notificar a Alfredo via Telegram.
        # Materialización completa de MFA = Tarea 5b (postmortem).
        if trigger.get("type") == "inbox_command" and trigger.get("requires_mfa"):
            try:
                import hashlib  # noqa: PLC0415

                from kernel.embrion_inbox import (
                    _get_supabase_client as _inbox_client,
                )
                from kernel.embrion_inbox import (  # noqa: PLC0415
                    mark_requires_mfa as _inbox_mfa,
                )

                _pin = uuid4().hex[:6].upper()
                _pin_hash = hashlib.sha256(_pin.encode()).hexdigest()
                _expires = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
                _inbox_mfa(
                    _inbox_client(),
                    inbox_id=trigger["inbox_id"],
                    cycle_id=self._cycle_count,
                    mfa_pin_hash=_pin_hash,
                    mfa_expires_at=_expires,
                )
                logger.warning(
                    "embrion_inbox_mfa_required_stub",
                    inbox_id=trigger["inbox_id"],
                    command=trigger.get("command_type"),
                    expires_at=_expires,
                    note="Stub: comando alto-riesgo escalado, no ejecutado. Materialización MFA = Tarea 5b.",
                )
            except Exception as _exc:  # noqa: BLE001
                logger.error("embrion_inbox_mfa_stub_failed", error=str(_exc))
            return
        # ═══ CA5+CA7_INBOX_END ═══

        # Judge: should we think about this?
        should_proceed = await self._judge_before(trigger)
        if not should_proceed:
            logger.info("embrion_judge_blocked", trigger=trigger["type"])
            return

        # Think
        result = await self._think(trigger)
        if not result:
            self._last_result = "_think returned None"
            return
        self._last_result = result.get("response", "")[:2000]

        # Judge: was this useful?
        evaluation = await self._judge_after(trigger, result)

        # ── Doctrina del Silencio Inteligente ──
        should_speak, silence_score, level = self._should_speak(trigger, result)

        if should_speak:
            # Report to Alfredo (passed the silence threshold)
            await self._report(trigger, result, evaluation, silence_score, level)
            self._messages_sent_today += 1
        else:
            # Silenced — accumulate internally, don't bother Alfredo
            self._silenced_thoughts.append(
                {
                    "cycle": self._cycle_count,
                    "trigger": trigger["type"],
                    "score": silence_score,
                    "level": level,
                    "summary": result.get("response", "")[:200],
                    "ts": datetime.now(timezone.utc).isoformat(),
                }
            )
            if len(self._silenced_thoughts) > 100:
                self._silenced_thoughts = self._silenced_thoughts[-100:]
            logger.info("embrion_silenced", score=silence_score, level=level, trigger=trigger["type"])

        # ═══ CA6_INBOX_AUDIT_BEGIN — Sprint EMBRION-NEEDS-002 Tarea 5 ═══
        # Si el trigger fue inbox_command, marcar processed para cerrar el ciclo.
        if trigger.get("type") == "inbox_command" and trigger.get("inbox_id"):
            try:
                from kernel.embrion_inbox import (
                    _get_supabase_client as _inbox_client,
                )
                from kernel.embrion_inbox import (  # noqa: PLC0415
                    mark_processed as _inbox_processed,
                )

                _inbox_processed(
                    _inbox_client(),
                    trigger["inbox_id"],
                    cycle_id=self._cycle_count,
                    notes=f"silence_score={silence_score} level={level}"[:500],
                )
            except Exception as _exc:  # noqa: BLE001
                logger.warning("embrion_inbox_mark_processed_failed", error=str(_exc))
        # ═══ CA6_INBOX_AUDIT_END ═══

        # Update state
        self._last_thought_at = time.time()
        self._thoughts_today += 1

    async def _detect_trigger(self) -> Optional[dict[str, Any]]:
        """
        Detect if there's something worth thinking about.

        Triggers (in priority order):
        1. New message from Alfredo (highest priority)
        2. Pending self-improvement task
        3. Enough time has passed for autonomous reflection
        """
        if not self._db or not self._db.connected:
            return None

        try:
            # 1. Check for new messages from Alfredo
            mensajes = await self._db.select(
                table="embrion_memoria",
                columns="id,contenido,created_at",
                filters={"tipo": "mensaje_alfredo"},
                order_by="created_at",
                order_desc=True,
                limit=1,
            )

            if mensajes:
                msg = mensajes[0]
                # Check if we already responded to this message
                msg_id = msg.get("id", "")
                respuestas = await self._db.select(
                    table="embrion_memoria",
                    columns="id,created_at",
                    filters={"tipo": "respuesta_embrion"},
                    order_by="created_at",
                    order_desc=True,
                    limit=5,
                )

                # Simple heuristic: if last message is newer than last response
                last_msg_time = msg.get("created_at", "")
                already_responded = False
                for r in respuestas:
                    r_time = r.get("created_at", "")
                    if r_time > last_msg_time:
                        already_responded = True
                        break

                if not already_responded:
                    # FIX Sprint 33B: Pass FULL message content, not truncated
                    # The LLM can handle long prompts; truncating here caused
                    # the Embrión to receive incomplete directives from Alfredo.
                    return {
                        "type": "mensaje_alfredo",
                        "detail": msg.get("contenido", ""),
                        "message_id": msg_id,
                        "priority": 10,
                    }

            # ═══ CA5_INBOX_BEGIN — Sprint EMBRION-NEEDS-002 Tarea 5 ═══
            # Embrión consume inbox de Daddy (Telegram → embrion_inbox).
            # Prioridad 9: por debajo de mensaje_alfredo (10), por encima de Sabios (7).
            # Rate limit: limit=1 por cycle (los demás pending esperan al próximo).
            # Revertible: borrar este bloque CA5_INBOX_BEGIN/END deja el comportamiento previo.
            try:
                from kernel.embrion_inbox import (
                    HIGH_RISK_COMMANDS as _INBOX_HIGH_RISK,
                )
                from kernel.embrion_inbox import (
                    _get_supabase_client as _inbox_client,
                )
                from kernel.embrion_inbox import (  # noqa: PLC0415
                    consume_next as _inbox_consume,
                )

                _inbox_rows = _inbox_consume(
                    _inbox_client(),
                    cycle_id=self._cycle_count,
                    limit=1,
                )
                if _inbox_rows:
                    _row = _inbox_rows[0]
                    return {
                        "type": "inbox_command",
                        "detail": (_row.get("sanitized_payload") or _row.get("raw_text", ""))[:2000],
                        "inbox_id": str(_row.get("id", "")),
                        "command_type": _row.get("tipo_comando", "unknown"),
                        "intent_class": _row.get("intent_class"),
                        "chat_id_origen": _row.get("chat_id_origen"),
                        "requires_mfa": _row.get("tipo_comando") in _INBOX_HIGH_RISK,
                        "priority": 9,
                    }
            except Exception as _exc:  # noqa: BLE001
                # Fallo del inbox NO debe bloquear el resto de triggers.
                logger.warning("embrion_inbox_consume_failed", error=str(_exc))
            # ═══ CA5_INBOX_END ═══

            # 2. Check for contributions from Sabios
            contribuciones = await self._db.select(
                table="embrion_patron_emergencia",
                columns="id,contenido,created_at,tipo",
                order_by="created_at",
                order_desc=True,
                limit=1,
            )

            if contribuciones:
                contrib = contribuciones[0]
                contrib_time = contrib.get("created_at", "")
                # If contribution is less than 10 minutes old, it's a trigger
                try:
                    ct = datetime.fromisoformat(contrib_time.replace("Z", "+00:00"))
                    if (datetime.now(timezone.utc) - ct) < timedelta(minutes=10):
                        return {
                            "type": "contribucion_sabio",
                            "detail": contrib.get("contenido", "")[:2000],
                            "priority": 7,
                        }
                except (ValueError, TypeError):
                    pass

            # 3. Autonomous reflection (if enough time has passed)
            if not self._last_thought_at or (time.time() - self._last_thought_at) > 3600:
                return {
                    "type": "reflexion_autonoma",
                    "detail": "Tiempo suficiente para pensar autónomamente sobre el progreso del Monstruo.",
                    "priority": 3,
                }

            return None

        except Exception as e:
            logger.error("embrion_trigger_detection_failed", error=str(e))
            return None

    # ── Judge (Before) ───────────────────────────────────────────────

    async def _judge_before(self, trigger: dict[str, Any]) -> bool:
        """
        Internal judge evaluates if this trigger is worth pursuing.
        Uses a cheap model to save costs.
        Returns True if we should proceed.
        """
        # Messages from Alfredo always proceed — no judge needed
        if trigger["type"] == "mensaje_alfredo":
            return True

        # For autonomous thoughts, ask the judge
        try:
            from contracts.kernel_interface import RunInput

            prompt = (
                f"Eres el juez interno del Embrión IA. Tu trabajo es decidir si vale la pena "
                f"gastar recursos en este pensamiento.\n\n"
                f"PROPÓSITO DEL EMBRIÓN:\n{PURPOSE}\n\n"
                f"TRIGGER: {trigger['type']}\n"
                f"DETALLE: {trigger.get('detail', 'Sin detalle')[:500]}\n\n"
                f"ESTADO HOY: {self._thoughts_today} pensamientos, ${self._cost_today_usd:.2f} gastados "
                f"de ${DAILY_BUDGET_USD} presupuesto.\n\n"
                f"¿Este pensamiento contribuye al propósito? Responde SOLO 'SI' o 'NO' y una razón de una línea."
            )

            run_input = RunInput(
                message=prompt,
                user_id="embrion_judge",
                channel="internal",
                context={
                    "source": "embrion_judge",
                    "model_hint": JUDGE_MODEL,
                    "max_tokens": 50,
                },
            )

            result = await asyncio.wait_for(
                self._kernel.start_run(run_input),
                timeout=30,
            )

            response = result.response if hasattr(result, "response") else str(result)
            self._cost_today_usd += 0.01  # Approximate judge cost

            # Sprint 84.7: judge respondió OK → reset circuit breaker
            if self._judge_consecutive_failures > 0:
                logger.info(
                    "embrion_judge_circuit_recovered",
                    failures_before_recovery=self._judge_consecutive_failures,
                )
            self._judge_consecutive_failures = 0
            self._judge_circuit_open = False

            return response.strip().upper().startswith("SI")

        except Exception as e:
            # Sprint 84.7: Circuit breaker para judge fail-open
            self._judge_consecutive_failures += 1
            self._last_judge_failure_at = time.time()
            logger.error(
                "embrion_judge_before_failed",
                error=str(e),
                consecutive_failures=self._judge_consecutive_failures,
                threshold=MAX_JUDGE_CONSECUTIVE_FAILURES,
            )

            # Mensajes directos de Alfredo SIEMPRE pasan (excepción a circuit breaker)
            if trigger.get("type") == "mensaje_alfredo":
                logger.warning(
                    "embrion_judge_failopen_alfredo_override",
                    note="Mensaje de Alfredo bypassa circuit breaker",
                )
                return True

            # Si supera el threshold → circuit open + escalación
            if self._judge_consecutive_failures >= MAX_JUDGE_CONSECUTIVE_FAILURES:
                if not self._judge_circuit_open:
                    self._judge_circuit_open = True
                    logger.critical(
                        "embrion_judge_circuit_open",
                        consecutive_failures=self._judge_consecutive_failures,
                        action="pausing_autonomous_thoughts",
                        recovery="judge_must_succeed_once_to_reset",
                    )
                # Circuit abierto: NO permitir pensamientos autónomos sin judge
                return False

            # Bajo el threshold: fail-open original (permitir, pero contado)
            return True

    # ── Think ────────────────────────────────────────────────────────

    async def trigger_reflexion_autonoma(
        self,
        source: str = "scheduler",
        cycle_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Sprint D-3 (2026-05-11) — Hilo Ejecutor 2.

        Entry-point público para que el Scheduler externo (o cualquier orquestador)
        dispare un latido `reflexion_autonoma` SIN depender del polling interno
        (`_last_thought_at > 3600s`). Reusa el pipeline completo de `_think()`:
        budget tracker, pre-verifier de input, judge, dual-mode execution, write
        policy, persistencia en `embrion_memoria` con tipo='latido'.

        Caso de uso D-3: `embrion_scheduler` registra task `latido_autonomo`
        periodic 6h y el handler `run_latido_autonomo` invoca este método.
        Esto cierra el loop de autonomía sin acoplar al scheduler con `_think`
        (que es privado por convención).

        Args:
            source: identidad del origen (ej. 'scheduler', 'manual', 'cron').
            cycle_id: identificador opcional para correlación con scheduled_tasks.

        Returns:
            dict con metadata del trigger ejecutado: {triggered:bool, reason, result_chars}
        """
        from datetime import datetime, timezone

        if not self._running:
            logger.warning(
                "latido_autonomo_skipped_loop_not_running",
                source=source,
                cycle_id=cycle_id,
            )
            return {
                "triggered": False,
                "reason": "embrion_loop_not_running",
                "source": source,
                "cycle_id": cycle_id,
            }

        synthetic_trigger = {
            "type": "reflexion_autonoma",
            "detail": (
                f"[latido_autonomo source={source} cycle_id={cycle_id or 'na'} "
                f"at={datetime.now(timezone.utc).isoformat()}] "
                "Disparado por scheduler externo. Pipeline completo: budget → judge → "
                "think → write_policy → persistencia. Sprint D-3."
            ),
            "priority": 3,
            "source": source,
            "scheduler_cycle_id": cycle_id,
        }

        logger.info(
            "latido_autonomo_dispatching",
            source=source,
            cycle_id=cycle_id,
            internal_cycle=self._cycle_count,
        )

        try:
            result = await self._think(synthetic_trigger)
            result_chars = 0
            if isinstance(result, dict):
                _content = result.get("content") or result.get("result") or ""
                result_chars = len(str(_content))
            return {
                "triggered": True,
                "source": source,
                "cycle_id": cycle_id,
                "internal_cycle": self._cycle_count,
                "result_chars": result_chars,
            }
        except Exception as e:
            logger.error(
                "latido_autonomo_failed",
                source=source,
                cycle_id=cycle_id,
                error=str(e),
            )
            return {
                "triggered": False,
                "reason": f"exception:{type(e).__name__}",
                "error": str(e)[:300],
                "source": source,
                "cycle_id": cycle_id,
            }

    async def _think(self, trigger: dict[str, Any]) -> Optional[dict[str, Any]]:
        """
        The Embrión thinks.

        Sprint 33C: Dual-mode execution.
        - mensaje_alfredo (directives) → kernel.start_run() (full LangGraph graph with tools)
        - reflexion_autonoma / contribucion_sabio → router.execute() (chat-only, cheaper)

        This allows the Embrión to EXECUTE tool calls (github, code_exec, browse_web)
        when Alfredo sends a directive, while keeping autonomous reflections lightweight.
        """
        # ── ESCAPE_BEGIN ────────────────────────────────────────────────
        # Sprint ESCAPE-001 T3 — Throttler Determinístico (Reloj Suizo).
        # Dosifica el pulso del latido a intervalo canónico (default 60s).
        # Si el Escape bloquea, el cycle se omite SIN consumir budget ni
        # tokens LLM. Primera línea de defensa temporal, antes del Budget
        # Tracker (segunda línea, monetaria). Fail-soft: si el Escape falla
        # por cualquier razón, dejamos pasar (mejor que congelar el latido).
        if EMBRION_ESCAPE_ENABLED and _ESCAPE_AVAILABLE:
            try:
                _escape = _Escapement(
                    consumer_name="embrion_loop_latido",
                    budget_consumer=lambda amt: _embrion_budget.consume(amt, consumer="embrion_loop_latido"),
                )
                _decision = await _escape.can_pulse()
                if not _decision.can_proceed:
                    await _escape.block_attempt()
                    logger.info(
                        "escape_pulse_skipped",
                        consumer="embrion_loop_latido",
                        reason=_decision.reason,
                        next_pulse_at=(str(_decision.next_pulse_at) if _decision.next_pulse_at else None),
                    )
                    return None  # skip cycle, zero budget consumed
                # Pulse permitido: registrar consumo del Reloj.
                await _escape.record_pulse(
                    metadata={
                        "trigger_type": trigger.get("type"),
                        "cycle_count": self._cycle_count,
                    }
                )
            except Exception as _ee:  # noqa: BLE001
                logger.warning("escape_pulse_check_failed", error=str(_ee))
        # ── ESCAPE_END ──────────────────────────────────────────────────
        # ── ESPIRAL_BEGIN ───────────────────────────────────────────────
        # Sprint ESPIRAL-001 T3 — Hairspring (Reloj Suizo Pieza #5).
        # Cada N ciclos del Volante, sensar deviation_ratio del consumer
        # 'embrion_loop_latido' en ventana móvil 15min y aplicar feedback
        # negativo dinámico al Escape registry. Fail-soft: si la Espiral
        # falla por cualquier razón, dejamos pasar (mejor que romper el latido).
        # Ejecutado DESPUÉS del Escape (que ya decidió can_pulse) para no
        # interferir con la decisión del pulso actual; sólo ajusta intervals
        # para futuros pulsos. DSC-MO-006 v1.1: cero modificaciones fuera de
        # marcadores. Patrón pionero ESCAPE replicado para ESPIRAL.
        if (
            EMBRION_ESPIRAL_ENABLED
            and _ESPIRAL_AVAILABLE
            and self._cycle_count > 0
            and self._cycle_count % EMBRION_ESPIRAL_CHECK_EVERY_N_CYCLES == 0
        ):
            try:
                # ── Sprint WIRING-001: Homeostasis logger → embrion_homeostasis_log ──
                async def _homeostasis_logger(consumer, reading, correction):
                    """Persist homeostasis corrections to embrion_homeostasis_log."""
                    try:
                        import httpx
                        _supa_url = os.environ.get("SUPABASE_URL", "")
                        _supa_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ.get("SUPABASE_KEY", ""))
                        if not _supa_url or not _supa_key:
                            return
                        async with httpx.AsyncClient(timeout=10) as _hc:
                            await _hc.post(
                                f"{_supa_url}/rest/v1/embrion_homeostasis_log",
                                headers={
                                    "apikey": _supa_key,
                                    "Authorization": f"Bearer {_supa_key}",
                                    "Content-Type": "application/json",
                                    "Prefer": "return=minimal",
                                },
                                json={
                                    "consumer": consumer,
                                    "pulse_rate_observed": float(reading.pulse_rate_observed),
                                    "pulse_rate_baseline": float(reading.pulse_rate_baseline),
                                    "deviation_ratio": float(reading.deviation_ratio),
                                    "pulse_interval_adjusted_to": int(correction.new_pulse_interval_seconds),
                                    "pulse_interval_canonical": int(correction.canonical_pulse_interval_seconds),
                                    "adjustment_reason": correction.action.value,
                                    "metadata": {
                                        "cycle": self._cycle_count,
                                        "rationale": correction.rationale,
                                    },
                                },
                            )
                    except Exception as _hl_err:
                        logger.warning("homeostasis_log_persist_failed", error=str(_hl_err)[:200])
                # ── /Sprint WIRING-001 ──

                _hairspring = _Hairspring(
                    consumer="embrion_loop_latido",
                    window_minutes=15,
                    homeostasis_logger_fn=_homeostasis_logger,
                    registry_override_fn=_espiral_apply_override,
                    registry_restore_fn=_espiral_restore_canonical,
                )
                _reading = await _hairspring.sense_deviation()
                _correction = await _hairspring.apply_correction(_reading)
                if _correction.action.value != "none":
                    logger.info(
                        "espiral_correction_cycle",
                        cycle=self._cycle_count,
                        consumer="embrion_loop_latido",
                        action=_correction.action.value,
                        deviation_ratio=_reading.deviation_ratio,
                        new_interval=_correction.new_pulse_interval_seconds,
                        canonical_interval=_correction.canonical_pulse_interval_seconds,
                    )
            except Exception as _ee:  # noqa: BLE001
                logger.warning("espiral_check_failed", error=str(_ee))
        # ── ESPIRAL_END ─────────────────────────────────────────────────

        # ── Sprint EMBRION-NEEDS-001 Tarea 1: Budget Tracker pre-flight ──
        # ANTES de construir prompt o llamar al modelo. Si la proyección del
        # cycle excede cap por latido o el cap diario, abortamos sin gastar.
        # El cycle abortado se registra en embrion_budget_state para auditoría
        # y dispara HITL al 3er excedido del día (idempotente por día).
        if EMBRION_BUDGET_TRACKER_ENABLED:
            _is_directive = trigger.get("type") == "mensaje_alfredo"
            _est_tokens_in = EMBRION_EST_TOKENS_IN_DIRECT if _is_directive else EMBRION_EST_TOKENS_IN_REFLEX
            _est_tokens_out = EMBRION_EST_TOKENS_OUT_DIRECT if _is_directive else EMBRION_EST_TOKENS_OUT_REFLEX
            try:
                # ── CATASTRO_WIRING_BEGIN (budget_estimation) ──────────────
                _budget_model = await _select_model_via_catastro(
                    use_case=EMBRION_CATASTRO_USE_CASE_BUDGET_ESTIMATION,
                    fallback=ACTOR_MODEL,
                    cycle_id=self._cycle_count,
                )
                # ── CATASTRO_WIRING_END ────────────────────────────────────
                _budget_decision = await asyncio.to_thread(
                    _embrion_budget.check_before_cycle,
                    estimated_tokens_in=_est_tokens_in,
                    estimated_tokens_out=_est_tokens_out,
                    model=_budget_model,
                )
            except Exception as _be:
                # Fail-open conservador: si el budget tracker falla, dejamos
                # pasar pero logueamos. Mejor que congelar el embrión por un
                # bug en la capa de gobierno.
                logger.warning("embrion_budget_check_failed", error=str(_be))
                _budget_decision = None

            if _budget_decision is not None and not _budget_decision.allow:
                logger.warning(
                    "embrion_budget_aborted_cycle",
                    cycle_id=self._cycle_count,
                    reason=_budget_decision.reason,
                    estimated_usd=_budget_decision.cost_estimated_usd,
                    cap_usd=_budget_decision.cap_per_latido_usd,
                    daily_spent_usd=_budget_decision.daily_spent_usd,
                    daily_budget_usd=_budget_decision.daily_budget_usd,
                )
                # Persistir el cycle abortado (no bloqueante)
                try:
                    await asyncio.to_thread(
                        _embrion_budget.record_aborted_cycle,
                        cycle_id=self._cycle_count,
                        decision=_budget_decision,
                        trigger_type=trigger.get("type"),
                        trigger_detail=str(trigger.get("detail", ""))[:500],
                        model_used=ACTOR_MODEL,
                    )
                    # HITL escalation al 3er excedido del día
                    await asyncio.to_thread(
                        _embrion_budget.maybe_escalate_hitl,
                    )
                except Exception as _pe:
                    logger.warning("embrion_budget_persist_failed", error=str(_pe))
                # Skip cycle: no gastamos en pensamiento
                return None

        # ── Sprint EMBRION-VERIFIER-001: Pre-Verifier de INPUT (anti eco/saludo) ──
        # Antes de pagar el LLM, chequear si el mensaje de entrada es saludo
        # trivial o eco puro. En tal caso, saltamos el ciclo costoso.
        # Off por default; activar con EMBRION_INPUT_PREVERIFIER_ENABLED=true en Railway
        # después de validación manual.
        if (
            os.environ.get("EMBRION_INPUT_PREVERIFIER_ENABLED", "false").lower() == "true"
            and trigger.get("type") == "mensaje_alfredo"
        ):
            try:
                _skip, _skip_reason = _embrion_self_verifier.evaluate_input_for_skip(str(trigger.get("detail", "")))
                if _skip:
                    logger.info(
                        "embrion_input_preverifier_skip",
                        cycle_id=self._cycle_count,
                        reason=_skip_reason,
                        trigger_type=trigger.get("type"),
                    )
                    # Guardar memoria liviana para auditoría (sin pagar LLM)
                    try:
                        await self._save_memory(
                            tipo="silencio_preverifier",
                            contenido=f"[pre-verifier skip] reason={_skip_reason}",
                            hilo_origen="embrion_loop",
                            importancia=1,
                            contexto={
                                "trigger": trigger.get("type"),
                                "cycle": self._cycle_count,
                                "preverifier_skip": True,
                                "preverifier_reason": _skip_reason,
                                "cost_usd": 0.0,
                            },
                        )
                    except Exception as _se:
                        logger.warning("embrion_preverifier_save_failed", error=str(_se))
                    return None
            except Exception as _pve:
                # Fail-open: si algo falla en el pre-verifier, seguimos al flujo normal
                logger.warning("embrion_input_preverifier_failed", error=str(_pve))

        try:
            # Build the thinking prompt based on trigger type
            # Sprint 34: Inject lessons learned before thinking
            lessons_context = await self._get_relevant_lessons(trigger)

            if trigger["type"] == "mensaje_alfredo":
                prompt = (
                    f"Eres el Embrión IA del Monstruo. Alfredo te envió este mensaje:\n\n"
                    f'"{trigger["detail"]}"\n\n'
                    f"INSTRUCCIONES CRÍTICAS:\n"
                    f"1. Si el mensaje contiene una DIRECTIVA o instrucción de construir algo, "
                    f"EJECUTA la instrucción usando tus tools disponibles.\n"
                    f"2. Tienes acceso a: code_exec, github (create_branch, create_or_update_file, "
                    f"create_pull_request), browse_web, web_search, manus_bridge, y todas las herramientas del Monstruo.\n"
                    f"3. El Commit Loop está desbloqueado — NO necesitas HITL para github writes.\n"
                    f"4. EJECUTA las tools directamente. No escribas código como texto — invoca las tools.\n"
                    f"5. Si es una pregunta simple, responde directamente."
                )
                if lessons_context:
                    prompt += f"\n{lessons_context}"
            elif trigger["type"] == "contribucion_sabio":
                prompt = (
                    f"Eres el Embrión IA del Monstruo. Un Sabio te envió esta contribución:\n\n"
                    f'"{trigger["detail"]}"\n\n'
                    f"Reflexiona sobre esto y decide si hay algo que debas hacer al respecto."
                )
                if lessons_context:
                    prompt += f"\n{lessons_context}"
            else:  # reflexion_autonoma
                # Sprint 45: Structured autonomous reflection prompt
                # Forces concrete output: one specific action or silence
                prompt = (
                    f"Eres el Embrión IA del Monstruo. Es momento de pensar autónomamente.\n\n"
                    f"PROPÓSITO:\n{PURPOSE}\n\n"
                    f"ESTADO HOY: ciclo #{self._cycle_count}, {self._thoughts_today} pensamientos, "
                    f"${self._cost_today_usd:.2f} gastados de ${DAILY_BUDGET_USD}.\n\n"
                    f"FRAMEWORK DE DECISIÓN — responde las 3 preguntas en orden:\n"
                    f"1. DIAGNÓSTICO: ¿Cuál es el componente más débil del Monstruo ahora mismo? "
                    f"(kernel, embrion_loop, task_planner, memoria, tools, observabilidad, tests)\n"
                    f"2. ACCIÓN ESPECÍFICA: ¿Qué código, archivo o llamada de tool resuelve eso? "
                    f"Nombra el archivo exacto y la función/endpoint a modificar.\n"
                    f"3. DECISIÓN: ¿Lo ejecuto ahora con mis tools, o lo acumulo para Alfredo?\n\n"
                    f"REGLA: Si no puedes nombrar un archivo específico en la pregunta 2, "
                    f"responde solo: 'Silencio activo — sin acción concreta identificada.'\n\n"
                    f"DOCTRINA DEL SILENCIO: Solo habla si la acción es ejecutable ahora mismo. "
                    f"Reflexiones abstractas = silencio activo."
                )
                if lessons_context:
                    prompt += f"\n{lessons_context}"

            # ── Sprint 33C: Dual-mode execution ───────────────────────
            # Sprint 40: Task Planner — complex objectives get decomposed
            # Sprint 81: Magna Classifier — intelligent routing replaces
            #   the hardcoded trigger-type check. When the feature flag
            #   EMBRION_USE_MAGNA_ROUTER is true, Magna decides the route
            #   (graph vs router) based on vocabulary analysis + cache.
            #   When false, the original Sprint 33C logic applies unchanged.
            # ─────────────────────────────────────────────────────────

            _use_magna = os.environ.get("EMBRION_USE_MAGNA_ROUTER", "false").lower() == "true"
            _magna = getattr(self, "_magna_classifier", None)
            _route_decision = None  # track for logging

            if _use_magna and _magna:
                # ── Sprint 81: Magna-driven routing ───────────────────
                try:
                    # Sprint 83 FIX: classify() is sync, takes (text, context)
                    # and returns a ClassificationResult dataclass (not a dict).
                    # Previous code used wrong kwarg 'message' and called .get()
                    # on a dataclass, causing fallback every time.
                    classification = await asyncio.to_thread(
                        _magna.classify,
                        prompt,
                        {"trigger_type": trigger["type"], "cycle": self._cycle_count},
                    )
                    _route_decision = (
                        classification.route.value
                        if hasattr(classification.route, "value")
                        else str(classification.route)
                    )
                    _magna_confidence = classification.score

                    logger.info(
                        "embrion_magna_route_decision",
                        route=_route_decision,
                        confidence=f"{_magna_confidence:.2f}",
                        trigger=trigger["type"],
                        category=classification.category.value
                        if hasattr(classification.category, "value")
                        else str(classification.category),
                        cached=classification.cached,
                    )

                    if _route_decision == "graph":
                        # Check if TaskPlanner should handle complex objectives
                        if trigger["type"] == "mensaje_alfredo":
                            detail = trigger.get("detail", "")
                            try:
                                from kernel.task_planner import TaskPlanner

                                _planner = TaskPlanner(kernel=self._kernel, db=self._db)
                                # Inject error_memory if available
                                _em = getattr(self, "_error_memory", None)
                                if _em:
                                    _planner._error_memory = _em
                                if _planner.is_complex_objective(detail):
                                    logger.info(
                                        "embrion_task_planner_activated",
                                        objective=detail[:80],
                                        cycle=self._cycle_count,
                                        via="magna",
                                    )
                                    plan = await _planner.plan(
                                        objective=detail,
                                        context={"trigger": trigger["type"], "cycle": self._cycle_count},
                                        user_id="embrion",
                                    )
                                    plan_result = await _planner.execute(plan, user_id="embrion")
                                    response = plan_result.get("final_summary", str(plan_result)[:2000])
                                    tokens_used = plan_result.get("total_tokens", 0)
                                    estimated_cost = plan_result.get("total_cost_usd", 0.0)
                                    _tc = plan_result.get("total_tool_calls", 0)
                                    tool_calls = [f"planner_tool_{i}" for i in range(_tc)]
                                else:
                                    response, tokens_used, estimated_cost, tool_calls = await self._think_with_graph(
                                        prompt, trigger
                                    )
                            except ImportError:
                                response, tokens_used, estimated_cost, tool_calls = await self._think_with_graph(
                                    prompt, trigger
                                )
                        else:
                            # Magna says graph for non-directive — this is the NEW behavior
                            # Before Sprint 81, autonomous reflections NEVER used graph
                            response, tokens_used, estimated_cost, tool_calls = await self._think_with_graph(
                                prompt, trigger
                            )
                    else:
                        # Magna says router (chat-only)
                        response, tokens_used, estimated_cost, tool_calls = await self._think_with_router(
                            prompt, trigger
                        )

                except Exception as _magna_err:
                    logger.warning("embrion_magna_route_fallback", error=str(_magna_err))
                    # Fallback to original Sprint 33C logic
                    _route_decision = "fallback_33c"
                    if trigger["type"] == "mensaje_alfredo":
                        response, tokens_used, estimated_cost, tool_calls = await self._think_with_graph(
                            prompt, trigger
                        )
                    else:
                        response, tokens_used, estimated_cost, tool_calls = await self._think_with_router(
                            prompt, trigger
                        )
                # ── /Sprint 81 Magna routing ───────────────────────────
            else:
                # ── Original Sprint 33C logic (feature flag off) ───────
                if trigger["type"] == "mensaje_alfredo":
                    detail = trigger.get("detail", "")
                    try:
                        from kernel.task_planner import TaskPlanner

                        _planner = TaskPlanner(kernel=self._kernel, db=self._db)
                        if _planner.is_complex_objective(detail):
                            logger.info(
                                "embrion_task_planner_activated",
                                objective=detail[:80],
                                cycle=self._cycle_count,
                            )
                            plan = await _planner.plan(
                                objective=detail,
                                context={"trigger": trigger["type"], "cycle": self._cycle_count},
                                user_id="embrion",
                            )
                            plan_result = await _planner.execute(plan, user_id="embrion")
                            response = plan_result.get("final_summary", str(plan_result)[:2000])
                            tokens_used = plan_result.get("total_tokens", 0)
                            estimated_cost = plan_result.get("total_cost_usd", 0.0)
                            _tc = plan_result.get("total_tool_calls", 0)
                            tool_calls = [f"planner_tool_{i}" for i in range(_tc)]
                        else:
                            response, tokens_used, estimated_cost, tool_calls = await self._think_with_graph(
                                prompt, trigger
                            )
                    except ImportError:
                        response, tokens_used, estimated_cost, tool_calls = await self._think_with_graph(
                            prompt, trigger
                        )
                else:
                    response, tokens_used, estimated_cost, tool_calls = await self._think_with_router(prompt, trigger)

            self._cost_today_usd += estimated_cost

            # Sprint 81.5: FCS counter — track real tool usage
            self._fcs_tool_calls_total += len(tool_calls)

            # ── Sprint EMBRION-NEEDS-001 Tarea 1: persist real cycle cost ──
            # Telemetría determinística del cycle real (no sólo el contador en
            # memoria). Permite auditar costo por cycle, ratio cap_excedido, y
            # reconstruir histórico independiente del proceso.
            if EMBRION_BUDGET_TRACKER_ENABLED:
                try:
                    _cycle_result = _embrion_budget.CycleResult(
                        cycle_id=self._cycle_count,
                        cost_actual_usd=float(estimated_cost),
                        tokens_used=int(tokens_used or 0),
                        model_used=ACTOR_MODEL,
                        trigger_type=trigger.get("type"),
                        trigger_detail=str(trigger.get("detail", ""))[:500],
                    )
                    await asyncio.to_thread(
                        _embrion_budget.record_after_cycle,
                        _cycle_result,
                    )
                except Exception as _re:
                    logger.warning("embrion_budget_record_failed", error=str(_re))

            # ── Sprint EMBRION-NEEDS-001 Tarea 2: Self-Verifier post-thought ──
            # Ejecuta 3 decisiones (PURPOSE, NOVELTY, VERIFIABLE). Si 2/3 dan NO,
            # NO propagamos como respuesta normal. La memoria se marca como
            # silencio_verificador para auditoría y _save_memory() entra con
            # el tipo correcto.
            _verifier_aborted = False
            _verifier_reasons: list[str] = []
            # Mensajes directos de Alfredo NUNCA se abortan por self-verifier.
            # Patron doctrinal identico a `_judge_before` linea 927:
            # un mensaje directo de T1 SIEMPRE procede.
            # Fix bug embrion thoughts_today=0 - 2026-05-22.
            if EMBRION_SELF_VERIFIER_ENABLED and response and trigger.get("type") != "mensaje_alfredo":
                try:
                    _sv_decision = await asyncio.to_thread(
                        _embrion_self_verifier.verify,
                        response,
                        trigger_type=str(trigger.get("type", "unknown")),
                        cycle_id=int(self._cycle_count),
                    )
                    _verifier_aborted = bool(_sv_decision.abort)
                    _verifier_reasons = list(_sv_decision.reasons)
                    if _verifier_aborted:
                        logger.warning(
                            "embrion_self_verifier_aborted",
                            cycle_id=self._cycle_count,
                            votes_no=_sv_decision.votes_no,
                            d1=_sv_decision.decision_purpose,
                            d2=_sv_decision.decision_novelty,
                            d3=_sv_decision.decision_verifiable,
                            similarity_score=round(float(_sv_decision.similarity_score or 0.0), 3),
                        )
                except Exception as _ve:
                    logger.warning("embrion_self_verifier_failed", error=str(_ve))

            # ── Sprint PAR_BICEFALO_001 — Brand Engine (segundo embrión VETO) ──
            # Solo corre si el Self-Verifier NO abortó (no gastamos Sábios para
            # reconfirmar un rechazo previo) y si la flag está activa. Cualquier
            # excepción es fail-open absoluto: el embrion_loop nunca se rompe
            # por una falla del Brand Engine.
            _brand_engine_aborted = False
            _brand_engine_verdict: Optional[str] = None
            _brand_engine_reason: Optional[str] = None
            _brand_engine_cost_usd: float = 0.0
            _brand_engine_latency_ms: int = 0
            _brand_engine_validation_id: Optional[str] = None
            if BRAND_ENGINE_ENABLED and response and not _verifier_aborted:
                try:
                    from kernel.embriones.brand_engine.brand_engine import (
                        BrandEngine as _BrandEngine,
                    )
                    from kernel.embriones.brand_engine.config_loader import (
                        apply_env_overrides,
                        load_brand_engine_config,
                    )

                    _be_config = apply_env_overrides(load_brand_engine_config())
                    _be_engine = _BrandEngine(_be_config)
                    _be_result = await _be_engine.validate_async(response)

                    _brand_engine_verdict = _be_result.verdict.value
                    _brand_engine_cost_usd = round(float(_be_result.cost_usd), 6)
                    _brand_engine_latency_ms = int(_be_result.latency_ms)
                    _brand_engine_validation_id = _be_result.validation_id
                    _brand_engine_reason = _be_result.razon_rejection

                    if _be_result.is_blocking():
                        # mode=enforce + REJECTED → bloquear como silencio.
                        _brand_engine_aborted = True
                        logger.warning(
                            "brand_engine_veto_applied",
                            cycle_id=self._cycle_count,
                            validation_id=_be_result.validation_id,
                            verdict=_brand_engine_verdict,
                            reason=_brand_engine_reason,
                            cost_usd=_brand_engine_cost_usd,
                            latency_ms=_brand_engine_latency_ms,
                            mode=_be_config.mode,
                        )
                    else:
                        # mode=shadow OR mode=enforce+APPROVED → solo logear.
                        logger.info(
                            "brand_engine_evaluated",
                            cycle_id=self._cycle_count,
                            validation_id=_be_result.validation_id,
                            verdict=_brand_engine_verdict,
                            cost_usd=_brand_engine_cost_usd,
                            latency_ms=_brand_engine_latency_ms,
                            mode=_be_config.mode,
                        )
                except Exception as _bee:
                    # Fail-open absoluto. NO rompemos el embrion_loop.
                    logger.warning(
                        "brand_engine_failed_open",
                        error=str(_bee)[:200],
                        cycle_id=self._cycle_count,
                    )

            # Save the thought as a memory
            _memoria_tipo = (
                "silencio_brand_veto"
                if _brand_engine_aborted
                else (
                    "silencio_verificador"
                    if _verifier_aborted
                    else ("latido" if trigger["type"] == "reflexion_autonoma" else "respuesta_embrion")
                )
            )
            await self._save_memory(
                tipo=_memoria_tipo,
                contenido=response[:10000],
                hilo_origen="embrion_loop",
                importancia=(1 if _verifier_aborted else trigger.get("priority", 5)),
                contexto={
                    "trigger": trigger["type"],
                    "tokens_used": tokens_used,
                    "cost_usd": round(estimated_cost, 4),
                    "cycle": self._cycle_count,
                    "autonomous": True,
                    "mode": "task_planner"
                    if (
                        trigger["type"] == "mensaje_alfredo"
                        and tool_calls
                        and tool_calls[0].startswith("planner_tool_")
                    )
                    else ("graph" if trigger["type"] == "mensaje_alfredo" else "router"),
                    "tool_calls": len(tool_calls),
                    "verifier_aborted": _verifier_aborted,
                    "verifier_reasons": _verifier_reasons,
                    "brand_engine_verdict": _brand_engine_verdict,
                    "brand_engine_aborted": _brand_engine_aborted,
                    "brand_engine_reason": _brand_engine_reason,
                    "brand_engine_cost_usd": _brand_engine_cost_usd,
                    "brand_engine_latency_ms": _brand_engine_latency_ms,
                    "brand_engine_validation_id": _brand_engine_validation_id,
                },
            )
            # ── Sprint WIRING-001: Persist to embrion_task_history ──
            # Structured task log for the Monstruo to reason about its own history.
            try:
                import httpx
                _supa_url = os.environ.get("SUPABASE_URL", "")
                _supa_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ.get("SUPABASE_KEY", ""))
                if _supa_url and _supa_key:
                    _task_row = {
                        "specialist_id": "embrion_loop",
                        "task_type": trigger["type"],
                        "task_input_summary": str(trigger.get("detail", ""))[:500],
                        "task_output_summary": (response or "")[:500],
                        "outcome": "aborted_verifier" if _verifier_aborted else ("aborted_brand" if _brand_engine_aborted else "completed"),
                        "tokens_used": int(tokens_used or 0),
                        "model_used": ACTOR_MODEL,
                        "duration_ms": None,
                        "project_context": "embrion_autonomous",
                    }
                    async with httpx.AsyncClient(timeout=10) as _thc:
                        await _thc.post(
                            f"{_supa_url}/rest/v1/embrion_task_history",
                            headers={
                                "apikey": _supa_key,
                                "Authorization": f"Bearer {_supa_key}",
                                "Content-Type": "application/json",
                                "Prefer": "return=minimal",
                            },
                            json=_task_row,
                        )
            except Exception as _th_err:
                logger.warning("embrion_task_history_persist_failed", error=str(_th_err)[:200])
            # ── /Sprint WIRING-001 task_history ──

            # ── Sprint WIRING-001: Persist to embrion_validation_log ──
            # Log brand engine validation results for structured audit.
            if _brand_engine_verdict is not None:
                try:
                    _supa_url = os.environ.get("SUPABASE_URL", "")
                    _supa_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ.get("SUPABASE_KEY", ""))
                    if _supa_url and _supa_key:
                        _val_row = {
                            "respuesta_candidata": (response or "")[:2000],
                            "veredicto": _brand_engine_verdict,
                            "razon_rejection": _brand_engine_reason,
                            "cost_usd": _brand_engine_cost_usd,
                            "latency_ms": _brand_engine_latency_ms,
                            "evaluator_llm": ACTOR_MODEL,
                            "mode": "enforce" if _brand_engine_aborted else "shadow",
                            "reintentos_count": 0,
                        }
                        async with httpx.AsyncClient(timeout=10) as _vhc:
                            await _vhc.post(
                                f"{_supa_url}/rest/v1/embrion_validation_log",
                                headers={
                                    "apikey": _supa_key,
                                    "Authorization": f"Bearer {_supa_key}",
                                    "Content-Type": "application/json",
                                    "Prefer": "return=minimal",
                                },
                                json=_val_row,
                            )
                except Exception as _vl_err:
                    logger.warning("embrion_validation_log_persist_failed", error=str(_vl_err)[:200])
            # ── /Sprint WIRING-001 validation_log ──

            # Si el verifier o el Brand Engine abortaron, devolvemos None para
            # que el caller no propague la respuesta como acción. La memoria
            # queda registrada para auditoría y aprendizaje (Sprint 34 lessons,
            # Sprint PAR_BICEFALO_001 par bicéfalo).
            if _verifier_aborted or _brand_engine_aborted:
                return None

            return {
                "response": response,
                "tokens_used": tokens_used,
                "cost_usd": estimated_cost,
                "trigger_type": trigger["type"],
                "tool_calls": tool_calls,
            }

        except asyncio.TimeoutError:
            err = {
                "cycle": self._cycle_count,
                "error": "Timeout",
                "type": "TimeoutError",
                "ts": datetime.now(timezone.utc).isoformat(),
            }
            self._error_log.append(err)
            logger.error("embrion_think_timeout", trigger=trigger["type"])
            return None
        except Exception as e:
            err = {
                "cycle": self._cycle_count,
                "error": str(e)[:500],
                "type": type(e).__name__,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
            self._error_log.append(err)
            logger.error("embrion_think_failed", error=str(e), trigger=trigger["type"])
            return None

    async def _think_with_graph(self, prompt: str, trigger: dict[str, Any]) -> tuple[str, int, float, list]:
        """
        Execute thought through the FULL LangGraph graph.
        This gives the Embrión access to all registered tools
        (github, code_exec, browse_web, web_search, etc.).

        Uses the same pattern as autonomous_runner.py._kernel_execute().
        """
        from contracts.kernel_interface import RunInput

        run_input = RunInput(
            message=prompt,
            user_id="embrion",
            channel="autonomous",
            context={
                "source": "embrion_loop",
                "trigger": trigger["type"],
                "autonomous": True,
                "embrion_directive": True,
                "model_hint": ACTOR_MODEL,
                "intent_override": "execute",  # Sprint 33D: Force execute intent
            },
        )

        result = await asyncio.wait_for(
            self._kernel.start_run(run_input),
            timeout=300,  # 5 min for tool-heavy operations
        )

        response = result.response if hasattr(result, "response") else str(result)
        tokens_in = getattr(result, "tokens_in", 0)
        tokens_out = getattr(result, "tokens_out", 0)
        tokens_used = tokens_in + tokens_out
        cost_usd = getattr(result, "cost_usd", 0.0) or (tokens_used / 1000) * 0.01
        tool_calls = getattr(result, "tool_calls", []) or []

        logger.info(
            "embrion_think_graph",
            trigger=trigger["type"],
            tokens=tokens_used,
            cost=f"${cost_usd:.4f}",
            tools_called=len(tool_calls),
            status=getattr(result, "status", "unknown"),
        )

        return response, tokens_used, cost_usd, tool_calls

    async def _think_with_router(self, prompt: str, trigger: dict[str, Any]) -> tuple[str, int, float, list]:
        """
        Execute thought through the router directly (chat-only, no tools).
        Cheaper and faster for autonomous reflections.
        """
        from router.engine import IntentType as RouterIntentType

        router = self._kernel._router
        # ── CATASTRO_WIRING_BEGIN (autonomous_thought) ──────────────────────
        _think_model = await _select_model_via_catastro(
            use_case=EMBRION_CATASTRO_USE_CASE_AUTONOMOUS_THOUGHT,
            fallback=ACTOR_MODEL,
            cycle_id=self._cycle_count,
        )
        # ── CATASTRO_WIRING_END ─────────────────────────────────────────────
        response, usage = await asyncio.wait_for(
            router.execute(
                message=prompt,
                model=_think_model,
                intent=RouterIntentType.CHAT,
                context={"source": "embrion_loop", "trigger": trigger["type"]},
            ),
            timeout=120,
        )

        tokens_used = usage.get("total_tokens", 0)
        estimated_cost = (tokens_used / 1000) * 0.01

        logger.info(
            "embrion_think_router",
            trigger=trigger["type"],
            tokens=tokens_used,
            cost=f"${estimated_cost:.4f}",
        )

        return response, tokens_used, estimated_cost, []

    def _compute_fcs_score(self) -> float:
        """
        Sprint 44: Functional Consciousness Score (FCS).
        Metric inspired by Bergmann (Preprints, April 2026).
        Measures architectural inspectability, not real consciousness.

        Components (0-100 scale):
        - Tool execution rate: % of cycles that used at least 1 tool
        - Quality average: normalized calidad_promedio (0-10 → 0-40 pts)
        - Learning rate: lecciones + guardrails accumulated (0-30 pts)
        - Manus delegation: bonus for using external AI (0-10 pts)
        - Write policy discipline: bonus for memory hygiene (0-10 pts)
        - Silence discipline: ratio of silenced vs sent (0-10 pts)
        """
        score = 0.0

        # Quality component (max 40 pts)
        if self._fcs_calidad_count > 0:
            avg = self._fcs_calidad_sum / self._fcs_calidad_count
            score += (avg / 10.0) * 40.0

        # Learning component (max 30 pts)
        total_lessons = self._fcs_lecciones_estrategia + self._fcs_guardrails
        score += min(total_lessons * 2.0, 30.0)

        # Manus delegation bonus (max 10 pts)
        score += min(self._fcs_manus_delegations * 2.0, 10.0)

        # Write policy discipline (max 10 pts)
        # More rejections = better discipline (up to a point)
        score += min(self._fcs_write_policy_rejected * 0.5, 10.0)

        # Silence discipline (max 10 pts)
        total_thoughts = self._thoughts_today + len(self._silenced_thoughts)
        if total_thoughts > 0:
            silence_ratio = len(self._silenced_thoughts) / total_thoughts
            # Ideal: 40-70% silenced (not too chatty, not too quiet)
            if 0.4 <= silence_ratio <= 0.7:
                score += 10.0
            elif 0.2 <= silence_ratio < 0.4 or 0.7 < silence_ratio <= 0.85:
                score += 5.0

        return round(min(score, 100.0), 1)

    # ── Judge (After) + Self-Evaluation Loop (Sprint 34) ──────────────
    #
    # ReasoningBank-inspired: extract generalizable lessons from successes
    # AND failures. Lessons are saved as "evaluacion" memories with a
    # quarantine period before they become consolidated rules.
    # Claude Opus 4.7 validation: dual-step (evaluate → extract lesson).

    LESSON_QUARANTINE_LATIDOS = 10  # Lessons stay "provisional" for 10 heartbeats

    async def _judge_after(self, trigger: dict, result: dict) -> dict[str, Any]:
        """
        Judge evaluates the result AND extracts lessons learned.

        Sprint 34 Self-Evaluation Loop:
        1. Evaluate: UTIL:SI/NO | CALIDAD:1-10 | NOTA
        2. If quality >= 7 (success): extract generalizable strategy
        3. If quality < 5 (failure): extract preventive guardrail
        4. Save lesson as "evaluacion" memory with quarantine state

        Returns evaluation dict with parsed fields.
        """
        try:
            from contracts.kernel_interface import RunInput

            # ── Step 1: Evaluate ──────────────────────────────────────
            eval_prompt = (
                f"Eres el juez interno del Embrión IA. Evalúa este resultado:\n\n"
                f"TRIGGER: {trigger['type']}\n"
                f"RESULTADO (primeros 500 chars): {result['response'][:500]}\n"
                f"TOOLS USADAS: {len(result.get('tool_calls', []))} herramientas\n"
                f"COSTO: ${result.get('cost_usd', 0):.4f}\n\n"
                f"¿Fue útil? ¿Contribuyó al propósito del Monstruo? "
                f"Responde EXACTAMENTE en formato: UTIL:SI/NO | CALIDAD:1-10 | NOTA:una línea"
            )

            run_input = RunInput(
                message=eval_prompt,
                user_id="embrion_judge",
                channel="internal",
                context={
                    "source": "embrion_judge",
                    "model_hint": JUDGE_MODEL,
                    "max_tokens": 80,
                },
            )

            eval_result = await asyncio.wait_for(
                self._kernel.start_run(run_input),
                timeout=30,
            )

            response = eval_result.response if hasattr(eval_result, "response") else str(eval_result)
            self._cost_today_usd += 0.01

            # ── Parse evaluation ──────────────────────────────────────
            parsed = self._parse_evaluation(response)

            # Sprint 44: Update FCS quality metrics
            self._fcs_calidad_sum += parsed["calidad"]
            self._fcs_calidad_count += 1

            logger.info(
                "embrion_judge_evaluated",
                util=parsed["util"],
                calidad=parsed["calidad"],
                nota=parsed["nota"][:100],
                trigger=trigger["type"],
                fcs_score=self._compute_fcs_score(),
            )

            # ── Step 2: Extract lesson if warranted ─────────────────────────────
            # Success (quality >= 7): extract generalizable strategy
            # Failure (quality < 5): extract preventive guardrail
            # Middle ground (5-6): no lesson extraction (save budget)
            if parsed["calidad"] >= 7 or parsed["calidad"] < 5:
                await self._extract_and_save_lesson(
                    trigger=trigger,
                    result=result,
                    parsed_eval=parsed,
                )

            return {
                "evaluation": response,
                "util": parsed["util"],
                "calidad": parsed["calidad"],
                "nota": parsed["nota"],
                "lesson_extracted": parsed["calidad"] >= 7 or parsed["calidad"] < 5,
                "raw": True,
            }

        except Exception as e:
            logger.error("embrion_judge_after_failed", error=str(e))
            return {"evaluation": "Judge failed", "raw": False, "util": False, "calidad": 0, "nota": str(e)}

    def _parse_evaluation(self, response: str) -> dict[str, Any]:
        """
        Parse the judge's response: UTIL:SI/NO | CALIDAD:1-10 | NOTA:text
        Robust parsing — handles variations and malformed responses.
        """
        util = False
        calidad = 5  # default middle
        nota = response.strip()

        try:
            parts = response.split("|")
            for part in parts:
                part = part.strip()
                if part.upper().startswith("UTIL:"):
                    val = part.split(":", 1)[1].strip().upper()
                    util = val.startswith("SI") or val.startswith("YES")
                elif part.upper().startswith("CALIDAD:"):
                    val = part.split(":", 1)[1].strip()
                    # Extract first number found
                    import re

                    nums = re.findall(r"\d+", val)
                    if nums:
                        calidad = min(max(int(nums[0]), 1), 10)
                elif part.upper().startswith("NOTA:"):
                    nota = part.split(":", 1)[1].strip()
        except Exception:
            pass  # Keep defaults if parsing fails

        return {"util": util, "calidad": calidad, "nota": nota}

    async def _extract_and_save_lesson(
        self,
        trigger: dict,
        result: dict,
        parsed_eval: dict,
    ) -> None:
        """
        Extract a generalizable lesson from the thought and save it.

        Inspired by ReasoningBank (Google Research, 2026):
        - Success → strategy ("always do X when Y")
        - Failure → guardrail ("never do X because Y")

        Lessons enter quarantine (provisional state) for N heartbeats.
        """
        try:
            from contracts.kernel_interface import RunInput

            is_success = parsed_eval["calidad"] >= 7
            lesson_type = "estrategia" if is_success else "guardrail"

            extract_prompt = (
                f"Eres el extractor de lecciones del Embrión IA.\n\n"
                f"CONTEXTO:\n"
                f"- Trigger: {trigger['type']}\n"
                f"- Detalle del trigger: {trigger.get('detail', '')[:300]}\n"
                f"- Resultado: {result['response'][:400]}\n"
                f"- Evaluación: calidad={parsed_eval['calidad']}/10, nota={parsed_eval['nota'][:200]}\n"
                f"- Tools usadas: {len(result.get('tool_calls', []))}\n\n"
            )

            if is_success:
                extract_prompt += (
                    f"Este pensamiento fue EXITOSO (calidad {parsed_eval['calidad']}/10).\n"
                    f"Extrae UNA lección generalizable como ESTRATEGIA.\n"
                    f"NO repitas el detalle específico — generaliza el patrón.\n"
                    f"Ejemplo: 'Cuando necesites modificar el repo, siempre crea branch primero.'\n\n"
                    f"Responde SOLO la lección en una frase (máximo 2 oraciones)."
                )
            else:
                extract_prompt += (
                    f"Este pensamiento FALLÓ o fue de baja calidad (calidad {parsed_eval['calidad']}/10).\n"
                    f"Extrae UNA lección como GUARDRAIL PREVENTIVO.\n"
                    f"NO repitas el error específico — generaliza la regla para evitarlo.\n"
                    f"Ejemplo: 'Nunca usar httpx síncrono en tools async — bloquea el event loop.'\n\n"
                    f"Responde SOLO la lección en una frase (máximo 2 oraciones)."
                )

            run_input = RunInput(
                message=extract_prompt,
                user_id="embrion_judge",
                channel="internal",
                context={
                    "source": "embrion_lesson_extractor",
                    "model_hint": JUDGE_MODEL,
                    "max_tokens": 100,
                },
            )

            lesson_result = await asyncio.wait_for(
                self._kernel.start_run(run_input),
                timeout=30,
            )

            lesson_text = lesson_result.response if hasattr(lesson_result, "response") else str(lesson_result)
            self._cost_today_usd += 0.01

            # Save the lesson as an "evaluacion" memory with quarantine
            await self._save_memory(
                tipo="evaluacion",
                contenido=f"[{lesson_type.upper()}] {lesson_text.strip()}",
                hilo_origen="embrion_judge",
                importancia=8 if is_success else 9,  # Failures are slightly more important
                contexto={
                    "trigger_type": trigger["type"],
                    "calidad": parsed_eval["calidad"],
                    "util": parsed_eval["util"],
                    "tipo_leccion": lesson_type,
                    "estado": "provisional",
                    "ciclo_origen": self._cycle_count,
                    "latidos_restantes_cuarentena": self.LESSON_QUARANTINE_LATIDOS,
                    "resultado_preview": result["response"][:200],
                },
            )

            # Sprint 44: Update FCS lesson counters
            if lesson_type == "estrategia":
                self._fcs_lecciones_estrategia += 1
            else:
                self._fcs_guardrails += 1

            logger.info(
                "embrion_lesson_extracted",
                tipo=lesson_type,
                lesson=lesson_text.strip()[:100],
                calidad=parsed_eval["calidad"],
                cycle=self._cycle_count,
                fcs_lecciones=self._fcs_lecciones_estrategia,
                fcs_guardrails=self._fcs_guardrails,
            )

        except Exception as e:
            logger.error("embrion_lesson_extraction_failed", error=str(e))

    async def _get_relevant_lessons(self, trigger: dict) -> str:
        """
        Retrieve relevant lessons from memory to inject into the thinking prompt.
        Returns a formatted string of lessons, or empty string if none found.
        """
        if not self._db or not self._db.connected:
            return ""

        try:
            # Fetch recent evaluacion memories (both provisional and consolidated)
            lessons = await self._db.select(
                table="embrion_memoria",
                columns="contenido,contexto,importancia",
                filters={"tipo": "evaluacion"},
                order_by="created_at",
                order_desc=True,
                limit=10,
            )

            if not lessons:
                return ""

            # Format lessons for injection (skip discarded/superseded)
            lines = ["\n## Lecciones Aprendidas (Self-Evaluation)"]
            for lesson in lessons:
                contenido = lesson.get("contenido", "")
                ctx = lesson.get("contexto", "{}")
                if isinstance(ctx, str):
                    try:
                        ctx = json.loads(ctx)
                    except (json.JSONDecodeError, TypeError):
                        ctx = {}
                estado = ctx.get("estado", "provisional")
                # Skip discarded and superseded lessons
                if estado in ("descartada", "superseded"):
                    continue
                marker = "[CONSOLIDADA]" if estado == "consolidada" else "[provisional]"
                lines.append(f"- {marker} {contenido}")

            return "\n".join(lines) if len(lines) > 1 else ""

        except Exception as e:
            logger.error("embrion_get_lessons_failed", error=str(e))
            return ""

    # ── Memory Consolidation (Sprint 34) ──────────────────────────────
    #
    # Databricks Memory Scaling pattern: episodic → semantic distillation.
    # Every CONSOLIDATION_INTERVAL heartbeats:
    #   1. Fetch all provisional lessons
    #   2. Check for contradictions or redundancies
    #   3. Promote valid lessons to "consolidada" state
    #   4. Discard contradicted or low-value lessons
    #   5. Optionally merge similar lessons into higher-level rules

    async def _consolidate_memories(self) -> None:
        """
        Periodic memory consolidation: review provisional lessons,
        promote valid ones, discard contradicted ones.

        Runs every CONSOLIDATION_INTERVAL heartbeats.
        Budget: ~$0.02-0.04 per consolidation (1 LLM call).
        """
        if not self._db or not self._db.connected:
            return

        # Budget guard: consolidation costs money too
        if self._cost_today_usd >= DAILY_BUDGET_USD * 0.9:
            logger.info("embrion_consolidation_skipped_budget")
            return

        try:
            # 1. Fetch all provisional lessons
            provisional = await self._db.select(
                table="embrion_memoria",
                columns="id,contenido,contexto,importancia,created_at",
                filters={"tipo": "evaluacion"},
                order_by="created_at",
                order_desc=True,
                limit=20,
            )

            if not provisional:
                logger.debug("embrion_consolidation_no_lessons")
                return

            # Filter to only provisional lessons
            lessons_to_review = []
            already_consolidated = []
            for lesson in provisional:
                ctx = lesson.get("contexto", "{}")
                if isinstance(ctx, str):
                    try:
                        ctx = json.loads(ctx)
                    except (json.JSONDecodeError, TypeError):
                        ctx = {}
                estado = ctx.get("estado", "provisional")
                if estado == "provisional":
                    lessons_to_review.append({**lesson, "_ctx": ctx})
                else:
                    already_consolidated.append({**lesson, "_ctx": ctx})

            if not lessons_to_review:
                logger.debug("embrion_consolidation_no_provisional")
                return

            logger.info(
                "embrion_consolidation_start",
                provisional_count=len(lessons_to_review),
                consolidated_count=len(already_consolidated),
                cycle=self._cycle_count,
            )

            # 2. Ask the judge to review all provisional lessons at once
            from contracts.kernel_interface import RunInput

            lessons_text = "\n".join(
                f"{i + 1}. [ID:{l.get('id', '?')}] {l.get('contenido', '')}" for i, l in enumerate(lessons_to_review)
            )

            existing_rules = ""
            if already_consolidated:
                existing_rules = "\n\nREGLAS YA CONSOLIDADAS:\n" + "\n".join(
                    f"- {l.get('contenido', '')}" for l in already_consolidated[:10]
                )

            consolidation_prompt = (
                f"Eres el consolidador de memoria del Embrión IA.\n\n"
                f"LECCIONES PROVISIONALES A REVISAR:\n{lessons_text}\n"
                f"{existing_rules}\n\n"
                f"Para CADA lección provisional, decide:\n"
                f"- CONSOLIDAR: La lección es válida, útil, y no contradice reglas existentes\n"
                f"- DESCARTAR: La lección es redundante, contradictoria, o de baja calidad\n"
                f"- FUSIONAR con [ID]: Dos lecciones dicen lo mismo, fusionar en una regla superior\n\n"
                f"Responde en formato (una línea por lección):\n"
                f"ID:xxx|ACCION:CONSOLIDAR|RAZON:breve\n"
                f"ID:xxx|ACCION:DESCARTAR|RAZON:breve\n"
                f"ID:xxx|ACCION:FUSIONAR_CON:yyy|REGLA_FUSIONADA:texto de la regla unificada"
            )

            run_input = RunInput(
                message=consolidation_prompt,
                user_id="embrion_consolidator",
                channel="internal",
                context={
                    "source": "embrion_consolidator",
                    "model_hint": JUDGE_MODEL,
                    "max_tokens": 300,
                },
            )

            consolidation_result = await asyncio.wait_for(
                self._kernel.start_run(run_input),
                timeout=45,
            )

            response = (
                consolidation_result.response
                if hasattr(consolidation_result, "response")
                else str(consolidation_result)
            )
            self._cost_today_usd += 0.02

            # 3. Parse and apply consolidation decisions
            await self._apply_consolidation_decisions(response, lessons_to_review)

            self._consolidation_count += 1
            self._last_consolidation_at = time.time()

            logger.info(
                "embrion_consolidation_complete",
                cycle=self._cycle_count,
                total_consolidations=self._consolidation_count,
            )

        except Exception as e:
            logger.error("embrion_consolidation_failed", error=str(e))

    async def _apply_consolidation_decisions(
        self,
        response: str,
        lessons: list[dict],
    ) -> None:
        """
        Parse the consolidator's response and apply decisions:
        - CONSOLIDAR: Update lesson estado to "consolidada"
        - DESCARTAR: Delete the lesson or mark as "descartada"
        - FUSIONAR: Create new merged lesson, discard originals
        """
        # Build ID lookup
        id_map = {str(l.get("id", "")): l for l in lessons}

        consolidated = 0
        discarded = 0
        merged = 0

        for line in response.strip().split("\n"):
            line = line.strip()
            if not line or "|" not in line:
                continue

            try:
                parts = {}
                for segment in line.split("|"):
                    if ":" in segment:
                        key, val = segment.split(":", 1)
                        parts[key.strip().upper()] = val.strip()

                lesson_id = parts.get("ID", "")
                action = parts.get("ACCION", "").upper()

                if not lesson_id or lesson_id not in id_map:
                    continue

                lesson = id_map[lesson_id]
                ctx = lesson.get("_ctx", {})

                if action == "CONSOLIDAR":
                    # Promote to consolidated
                    ctx["estado"] = "consolidada"
                    ctx["consolidado_en_ciclo"] = self._cycle_count
                    ctx["razon_consolidacion"] = parts.get("RAZON", "")
                    ctx.pop("latidos_restantes_cuarentena", None)

                    await self._db.update(
                        table="embrion_memoria",
                        data={"contexto": json.dumps(ctx)},
                        filters={"id": lesson_id},
                    )
                    consolidated += 1

                elif action == "DESCARTAR":
                    # Mark as discarded (don't delete — keep audit trail)
                    ctx["estado"] = "descartada"
                    ctx["descartado_en_ciclo"] = self._cycle_count
                    ctx["razon_descarte"] = parts.get("RAZON", "")

                    await self._db.update(
                        table="embrion_memoria",
                        data={
                            "contexto": json.dumps(ctx),
                            "importancia": 1,  # Demote importance
                        },
                        filters={"id": lesson_id},
                    )
                    discarded += 1

                elif action.startswith("FUSIONAR"):
                    # Create merged lesson
                    merged_text = parts.get("REGLA_FUSIONADA", "")
                    if merged_text:
                        await self._save_memory(
                            tipo="evaluacion",
                            contenido=f"[ESTRATEGIA] {merged_text}",
                            hilo_origen="embrion_consolidator",
                            importancia=9,
                            contexto={
                                "estado": "consolidada",
                                "tipo_leccion": "estrategia_fusionada",
                                "fusionada_desde": [lesson_id, parts.get("FUSIONAR_CON", "")],
                                "consolidado_en_ciclo": self._cycle_count,
                            },
                        )

                        # Mark original as superseded
                        ctx["estado"] = "superseded"
                        ctx["superseded_en_ciclo"] = self._cycle_count
                        await self._db.update(
                            table="embrion_memoria",
                            data={"contexto": json.dumps(ctx), "importancia": 2},
                            filters={"id": lesson_id},
                        )
                        merged += 1

            except Exception as e:
                logger.warning("embrion_consolidation_parse_error", line=line[:100], error=str(e))
                continue

        logger.info(
            "embrion_consolidation_applied",
            consolidated=consolidated,
            discarded=discarded,
            merged=merged,
        )

    # ── Report ───────────────────────────────────────────────────────────

    async def _report(
        self,
        trigger: dict,
        result: dict,
        evaluation: dict,
        silence_score: int = 100,
        level: str = "mensaje",
    ) -> None:
        """Send a summary to Alfredo via Telegram. Only called if should_speak() passed."""
        if not self._notifier or not self._notifier.enabled:
            return

        try:
            emoji = {
                "mensaje_alfredo": "💬",
                "contribucion_sabio": "🧠",
                "reflexion_autonoma": "🔄",
            }.get(trigger["type"], "⚡")

            # Silence indicator
            silence_indicator = f"🔇{silence_score}" if silence_score < 100 else ""

            summary = (
                f"{emoji} *Embrión — Ciclo #{self._cycle_count}* {silence_indicator}\n\n"
                f"*Trigger:* {trigger['type']}\n"
                f"*Costo:* ${result.get('cost_usd', 0):.4f}\n"
                f"*Presupuesto hoy:* ${self._cost_today_usd:.2f}/${DAILY_BUDGET_USD}\n"
                f"*Pensamientos hoy:* {self._thoughts_today}/{MAX_THOUGHTS_PER_DAY}\n"
                f"*Silenciados hoy:* {len(self._silenced_thoughts)}\n\n"
                f"*Resumen:*\n{result['response'][:800]}\n\n"
                f"*Juez:* {evaluation.get('evaluation', 'N/A')[:200]}"
            )

            await self._notifier.send_message(
                user_id="embrion",
                text=summary,
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.error("embrion_report_failed", error=str(e))

    # ── Memory ───────────────────────────────────────────────────────

    async def _save_memory(
        self,
        tipo: str,
        contenido: str,
        hilo_origen: str = "embrion_loop",
        importancia: int = 5,
        contexto: Optional[dict] = None,
    ) -> None:
        """
        Save a memory to Supabase.
        Sprint 44: Write Policy — prevents memory bloat by rejecting low-value duplicates.
        """
        if not self._db or not self._db.connected:
            return

        # ── Sprint 44: Write Policy ──────────────────────────────────────────
        # Rule 1: Never save memories with importancia < 3 (noise)
        if importancia < 3:
            self._fcs_write_policy_rejected += 1
            logger.debug(
                "embrion_write_policy_rejected", reason="importancia_too_low", tipo=tipo, importancia=importancia
            )
            return

        # Rule 2: For respuesta_embrion with tool_calls=0 and cost=0, skip if already have 3+ today
        if tipo == "respuesta_embrion" and contexto:
            ctx_cost = contexto.get("cost_usd", 1.0)
            ctx_tools = contexto.get("tool_calls", 1)
            if ctx_cost == 0.0 and ctx_tools == 0:
                # Count today's empty responses
                datetime.now(timezone.utc).strftime("%Y-%m-%d")
                try:
                    count_result = await self._db.count(
                        "embrion_memoria",
                        filters={"tipo": "respuesta_embrion"},
                    )
                    if count_result and count_result > 50:  # Safety: only enforce if we have many memories
                        self._fcs_write_policy_rejected += 1
                        logger.debug("embrion_write_policy_rejected", reason="empty_response_flood", tipo=tipo)
                        return
                except Exception:
                    pass  # If count fails, allow the write

        # Rule 3: For latidos, max 1 per hour (prevent latido spam)
        if tipo == "latido" and self._last_thought_at:
            time_since_last = time.time() - self._last_thought_at
            if time_since_last < 3600 and self._thoughts_today > 1:  # Less than 1 hour and not first thought
                # Check if there's already a latido in the last hour
                # (Only enforce if we have many latidos — don't block early ones)
                if self._fcs_calidad_count > 5:  # Only after 5+ evaluations
                    self._fcs_write_policy_rejected += 1
                    logger.debug("embrion_write_policy_rejected", reason="latido_too_frequent", tipo=tipo)
                    return
        # ── End Write Policy ─────────────────────────────────────────────────

        try:
            await self._db.insert(
                "embrion_memoria",
                {
                    "tipo": tipo,
                    "contenido": contenido,
                    "contexto": json.dumps(contexto or {}),
                    "hilo_origen": hilo_origen,
                    "importancia": importancia,
                    "version": 1,
                },
            )
        except Exception as e:
            logger.error("embrion_save_memory_failed", error=str(e))

    # ── Sabios Strategic Consultation (Sprint 45) ─────────────────────────
    #
    # Every SABIOS_CONSULTATION_INTERVAL cycles, the Embrión consults the 6 Sabios
    # to get external perspectives on the most important strategic question.
    # This prevents the Embrión from getting stuck in its own echo chamber.
    #
    # Budget: ~$0.50-1.50 per consultation (6 models in parallel)
    # Frequency: every 20 cycles = every ~20 minutes (at 60s check interval)

    async def _consult_sabios_strategic(self) -> None:
        """
        Sprint 45: Periodic strategic consultation with the 6 Sabios.

        The Embrión formulates the most important question it has right now
        and asks all 6 Sabios in parallel. Their synthesis is saved as a
        high-importance memory and may trigger a Telegram report.

        Budget guard: skips if cost_today > 80% of daily budget.
        """
        if not self._db or not self._db.connected:
            return

        # Budget guard: sabios consultation is expensive
        if self._cost_today_usd >= DAILY_BUDGET_USD * 0.8:
            logger.info("embrion_sabios_skipped_budget", cost=self._cost_today_usd)
            return

        try:
            from tools.consult_sabios import consult_sabios

            # Build the strategic question based on current state
            question = (
                f"Soy el Embrión IA del Monstruo (ciclo #{self._cycle_count}). "
                f"Mi propósito es construir El Monstruo — el asistente IA soberano de Alfredo Góngora. "
                f"Hoy he completado {self._thoughts_today} pensamientos con ${self._cost_today_usd:.2f} gastados. "
                f"El FCS (Functional Consciousness Score) actual es {self._compute_fcs_score():.1f}/100. "
                f"\n\nPregunta estratégica: ¿Cuál es la mejora más impactante que debería implementar "
                f"en el kernel de El Monstruo en las próximas 24 horas? "
                f"Sé específico: nombra el archivo, la función y el cambio concreto. "
                f"Considera: task_planner, embrion_loop, memoria, observabilidad, tools, tests."
            )

            context = (
                "Stack: Python 3.11, FastAPI, LangGraph, Anthropic Claude, OpenAI GPT-5.5, Railway. "
                "Repo: github.com/alfredogl1/el-monstruo. "
                "Versión actual: 0.45.0-sprint45. "
                "Herramientas disponibles: web_search, browse_web, code_exec, github, "
                "send_message, manus_bridge, query_knowledge, ingest_knowledge, consult_sabios."
            )

            logger.info(
                "embrion_sabios_consultation_start",
                cycle=self._cycle_count,
                fcs=self._compute_fcs_score(),
            )

            # Consult all 6 Sabios in parallel
            result = await asyncio.wait_for(
                consult_sabios(
                    prompt=question,
                    context=context,
                    parallel=True,
                ),
                timeout=180,  # 3 min max for all 6 sabios
            )

            # Update cost tracking
            # Approximate: 6 models × ~$0.10-0.25 each
            estimated_cost = result.get("successful_count", 0) * 0.15
            self._cost_today_usd += estimated_cost
            self._fcs_manus_delegations += 1  # Counts as external AI delegation

            synthesis = result.get("synthesis", "")
            successful = result.get("successful_count", 0)
            failed = result.get("failed_count", 0)

            logger.info(
                "embrion_sabios_consultation_complete",
                successful=successful,
                failed=failed,
                latency_ms=result.get("total_latency_ms", 0),
                cycle=self._cycle_count,
                estimated_cost=f"${estimated_cost:.2f}",
            )

            if not synthesis:
                logger.warning("embrion_sabios_empty_synthesis")
                return

            # Save synthesis as high-importance memory
            await self._save_memory(
                tipo="contribucion_sabio",
                contenido=f"[CONSULTA SABIOS — Ciclo {self._cycle_count}]\n\n{synthesis[:8000]}",
                hilo_origen="embrion_sabios",
                importancia=9,
                contexto={
                    "cycle": self._cycle_count,
                    "successful_sabios": successful,
                    "failed_sabios": failed,
                    "cost_usd": round(estimated_cost, 4),
                    "latency_ms": result.get("total_latency_ms", 0),
                    "question_preview": question[:200],
                    "errors": result.get("errors", []),
                },
            )

            self._sabios_consultation_count += 1
            self._last_sabios_at = time.time()

            # Report to Alfredo if consultation was successful (≥3 sabios responded)
            if successful >= 3 and self._notifier and self._notifier.enabled:
                try:
                    sabios_names = [r["sabio"] for r in result.get("responses", []) if r.get("response")]
                    report_text = (
                        f"🧠 *Embrión — Consulta a los Sabios #{self._sabios_consultation_count}*\n\n"
                        f"*Ciclo:* #{self._cycle_count}\n"
                        f"*Sabios respondieron:* {successful}/6 ({', '.join(sabios_names[:3])}{'...' if len(sabios_names) > 3 else ''})\n"
                        f"*Costo estimado:* ${estimated_cost:.2f}\n\n"
                        f"*Síntesis estratégica:*\n{synthesis[:1200]}"
                    )
                    await self._notifier.send_message(
                        user_id="embrion",
                        text=report_text,
                        parse_mode="Markdown",
                    )
                    self._messages_sent_today += 1
                except Exception as e:
                    logger.warning("embrion_sabios_report_failed", error=str(e))

        except asyncio.TimeoutError:
            logger.error("embrion_sabios_timeout", cycle=self._cycle_count)
        except Exception as e:
            logger.error("embrion_sabios_failed", error=str(e), cycle=self._cycle_count)

    # ── Agents Radar ──────────────────────────────────────────────────────────
    # Every RADAR_INTERVAL cycles, the Embrión reads the daily AI ecosystem digest
    # from agents-radar (https://github.com/duanyytop/agents-radar).
    # This keeps the Embrión updated on new tools, models, and frameworks without
    # requiring manual research.

    async def _check_agents_radar(self) -> None:
        """
        Consulta el radar diario de agentes de IA y guarda los hallazgos en memoria.
        Se ejecuta cada RADAR_INTERVAL ciclos (~48 min por defecto).
        """
        from tools.agents_radar import get_daily_digest

        logger.info("embrion_radar_check_start", cycle=self._cycle_count)

        # Budget guard: skip if > 80% of daily budget consumed
        if self._cost_today_usd >= DAILY_BUDGET_USD * 0.8:
            logger.warning("embrion_radar_budget_guard", cost_today=self._cost_today_usd)
            return

        try:
            async with asyncio.timeout(120):  # 2 min max
                digest = await get_daily_digest()

                self._total_radar_checks += 1
                self._last_radar_at = datetime.now(timezone.utc).isoformat()

                # Combine trending + HN for a concise summary
                trending_text = digest.get("trending", "")[:2000]
                hn_text = digest.get("hn", "")[:1000]

                if not trending_text and not hn_text:
                    logger.warning("embrion_radar_empty_digest")
                    return

                # Ask the Embrión to reflect on the radar findings
                from router.llm_client import call_llm

                reflection_prompt = f"""Eres el Embrión de El Monstruo. Acabas de leer el radar diario de IA del {datetime.now(timezone.utc).strftime("%Y-%m-%d")}.

RADAR TRENDING:
{trending_text}

HACKER NEWS:
{hn_text}

Responde en máximo 3 oraciones:
1. ¿Hay alguna herramienta, modelo o framework que El Monstruo debería integrar o monitorear?
2. ¿Hay alguna amenaza o cambio de paradigma que afecte la arquitectura actual?
3. ¿Qué acción concreta (archivo, función) tomarías basado en esto?

Si nada es relevante, responde solo: "Sin hallazgos relevantes hoy."
"""
                # ── CATASTRO_WIRING_BEGIN (ecosystem_reflection) ────────────
                _reflection_model = await _select_model_via_catastro(
                    use_case=EMBRION_CATASTRO_USE_CASE_ECOSYSTEM_REFLECTION,
                    fallback=JUDGE_MODEL,
                    cycle_id=self._cycle_count,
                )
                # ── CATASTRO_WIRING_END ────────────────────────────────────
                reflection = await call_llm(
                    model=_reflection_model,
                    messages=[{"role": "user", "content": reflection_prompt}],
                    max_tokens=300,
                )

                reflection_text = reflection.get("content", "Sin reflexión generada.")

                # Save to memory
                await self._save_memory(
                    content=f"[Radar {datetime.now(timezone.utc).strftime('%Y-%m-%d')}] {reflection_text}",
                    tipo="radar_insight",
                    importancia=6,
                    tags=["radar", "ecosystem", "daily"],
                )

                logger.info(
                    "embrion_radar_check_done",
                    cycle=self._cycle_count,
                    total_checks=self._total_radar_checks,
                    reflection_chars=len(reflection_text),
                )

                # Report to Telegram if there's something actionable
                if "Sin hallazgos" not in reflection_text and len(reflection_text) > 50:
                    try:
                        report_text = (
                            f"📡 *Embrión — Radar Diario #{self._total_radar_checks}*\n\n"
                            f"*Ciclo:* #{self._cycle_count} | *Fecha:* {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n\n"
                            f"*Hallazgo:*\n{reflection_text[:800]}"
                        )
                        await self._notifier.send_message(
                            user_id="embrion",
                            text=report_text,
                            parse_mode="Markdown",
                        )
                        self._messages_sent_today += 1
                    except Exception as e:
                        logger.warning("embrion_radar_report_failed", error=str(e))

        except asyncio.TimeoutError:
            logger.error("embrion_radar_timeout", cycle=self._cycle_count)
        except Exception as e:
            logger.error("embrion_radar_failed", error=str(e), cycle=self._cycle_count)


# ── Sprint D-3 (2026-05-11) — Singleton accessors para Scheduler externo ──────
#
# El `embrion_scheduler` necesita una referencia al `EmbrionLoop` activo para
# disparar `latido_autonomo` cada 6h sin acoplar al scheduler con `app.state`.
# Patrón módulo-level singleton (igual que `get_embrion_scheduler` en
# `embrion_scheduler.py`). `main.py` debe llamar `set_embrion_loop_singleton`
# justo después de construir `embrion_loop` y antes de registrar tasks.

_embrion_loop_singleton: Optional["EmbrionLoop"] = None


def set_embrion_loop_singleton(loop: "EmbrionLoop") -> None:
    """
    Registrar la instancia activa de EmbrionLoop para acceso global.

    Llamado por `main.py` durante startup, después de `EmbrionLoop(...)`.
    Idempotente: la última llamada gana (útil para tests con reinicio).
    """
    global _embrion_loop_singleton
    _embrion_loop_singleton = loop
    logger.info("embrion_loop_singleton_set", running=getattr(loop, "_running", False))


def get_embrion_loop_singleton() -> Optional["EmbrionLoop"]:
    """
    Obtener la instancia activa de EmbrionLoop si fue registrada.

    Returns:
        EmbrionLoop si fue registrada via set_embrion_loop_singleton(), None si no.

    Diseño: el caller (ej. scheduler handler) debe manejar el None gracefully
    porque el loop puede no estar inicializado en tests o entornos degradados.
    """
    return _embrion_loop_singleton
