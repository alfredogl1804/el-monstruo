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
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Optional
from uuid import uuid4

import structlog

logger = structlog.get_logger("embrion.loop")

# ── Configuration ────────────────────────────────────────────────────
CHECK_INTERVAL_S = int(os.environ.get("EMBRION_CHECK_INTERVAL", "60"))  # Check every 60s
THINK_COOLDOWN_S = int(os.environ.get("EMBRION_THINK_COOLDOWN", "300"))  # Min 5 min between thoughts
DAILY_BUDGET_USD = float(os.environ.get("EMBRION_DAILY_BUDGET", "2.0"))  # $2/day max
MAX_THOUGHTS_PER_DAY = int(os.environ.get("EMBRION_MAX_THOUGHTS", "50"))
JUDGE_MODEL = os.environ.get("EMBRION_JUDGE_MODEL", "gpt-5")  # Cheap but current model
ACTOR_MODEL = os.environ.get("EMBRION_ACTOR_MODEL", "gpt-5.5")  # Full power for thinking (catalog key)
SILENCE_THRESHOLD = int(os.environ.get("EMBRION_SILENCE_THRESHOLD", "70"))  # silence_score > 70 to speak

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
        }

    @property
    def debug(self) -> dict[str, Any]:
        return {
            "stats": self.stats,
            "actor_model": ACTOR_MODEL,
            "judge_model": JUDGE_MODEL,
            "has_db": self._db is not None and getattr(self._db, 'connected', False),
            "has_kernel": self._kernel is not None,
            "has_router": hasattr(self._kernel, '_router') and self._kernel._router is not None if self._kernel else False,
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
        """Main consciousness loop — checks for triggers every CHECK_INTERVAL_S."""
        while self._running:
            try:
                self._cycle_count += 1
                self._reset_daily_counters_if_needed()
                await self._check_and_think()
            except Exception as e:
                err = {"cycle": self._cycle_count, "error": str(e), "type": type(e).__name__, "ts": datetime.now(timezone.utc).isoformat()}
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
        # Heuristic: if the response mentions "urgente", "error", "fallo", "roto", "broken"
        urgency_keywords = ["urgente", "error", "fallo", "roto", "broken", "critical", "bloqueado", "down"]
        if any(kw in response_text.lower() for kw in urgency_keywords):
            score += 30

        # Q3: Is something irrecoverable lost if we stay silent?
        irrecoverable_keywords = ["datos perdidos", "data loss", "irreversible", "eliminado", "borrado", "security", "breach"]
        if any(kw in response_text.lower() for kw in irrecoverable_keywords):
            score += 40

        # Q4: Did Alfredo explicitly ask? (already handled by mensaje_alfredo exception above)
        # For non-Alfredo triggers, this is always 0

        # Bonus: if the Embrión actually DID something (code_exec, github commit)
        action_keywords = ["ejecuté", "commit", "creé", "pull request", "deployed", "instalé"]
        if any(kw in response_text.lower() for kw in action_keywords):
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
            self._silenced_thoughts.append({
                "cycle": self._cycle_count,
                "trigger": trigger["type"],
                "score": silence_score,
                "level": level,
                "summary": result.get("response", "")[:200],
                "ts": datetime.now(timezone.utc).isoformat(),
            })
            if len(self._silenced_thoughts) > 100:
                self._silenced_thoughts = self._silenced_thoughts[-100:]
            logger.info("embrion_silenced", score=silence_score, level=level, trigger=trigger["type"])

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
                    columns="id",
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

            return response.strip().upper().startswith("SI")

        except Exception as e:
            logger.error("embrion_judge_before_failed", error=str(e))
            # If judge fails, default to proceeding (fail-open for thinking)
            return True

    # ── Think ────────────────────────────────────────────────────────

    async def _think(self, trigger: dict[str, Any]) -> Optional[dict[str, Any]]:
        """
        The Embrión thinks.

        Sprint 33C: Dual-mode execution.
        - mensaje_alfredo (directives) → kernel.start_run() (full LangGraph graph with tools)
        - reflexion_autonoma / contribucion_sabio → router.execute() (chat-only, cheaper)

        This allows the Embrión to EXECUTE tool calls (github, code_exec, browse_web)
        when Alfredo sends a directive, while keeping autonomous reflections lightweight.
        """
        try:
            # Build the thinking prompt based on trigger type
            if trigger["type"] == "mensaje_alfredo":
                prompt = (
                    f"Eres el Embrión IA del Monstruo. Alfredo te envió este mensaje:\n\n"
                    f'"{ trigger["detail"]}"\n\n'
                    f"INSTRUCCIONES CRÍTICAS:\n"
                    f"1. Si el mensaje contiene una DIRECTIVA o instrucción de construir algo, "
                    f"EJECUTA la instrucción usando tus tools disponibles.\n"
                    f"2. Tienes acceso a: code_exec, github (create_branch, create_or_update_file, "
                    f"create_pull_request), browse_web, web_search, y todas las herramientas del Monstruo.\n"
                    f"3. El Commit Loop está desbloqueado — NO necesitas HITL para github writes.\n"
                    f"4. EJECUTA las tools directamente. No escribas código como texto — invoca las tools.\n"
                    f"5. Si es una pregunta simple, responde directamente."
                )
            elif trigger["type"] == "contribucion_sabio":
                prompt = (
                    f"Eres el Embrión IA del Monstruo. Un Sabio te envió esta contribución:\n\n"
                    f'"{ trigger["detail"]}"\n\n'
                    f"Reflexiona sobre esto y decide si hay algo que debas hacer al respecto."
                )
            else:  # reflexion_autonoma
                prompt = (
                    f"Eres el Embrión IA del Monstruo. Es momento de pensar autónomamente.\n\n"
                    f"PROPÓSITO:\n{PURPOSE}\n\n"
                    f"DOCTRINA DEL SILENCIO: Tu estado natural es el silencio activo. "
                    f"Observa, procesa, anticipa, prepara — pero no hables a menos que sea necesario. "
                    f"Si no tienes algo concreto que HACER (no reflexionar), permanece en silencio.\n\n"
                    f"¿Hay algo que puedas mejorar, construir, investigar, o preparar para Alfredo? "
                    f"Si sí, HAZLO usando tus tools. Si no, responde solo: 'Silencio activo.'"
                )

            # ── Sprint 33C: Dual-mode execution ─────────────────────────
            # Directives from Alfredo go through the FULL LangGraph graph
            # (which includes tool_dispatch, so the Embrión can actually
            # execute github, code_exec, browse_web, etc.)
            # Autonomous reflections stay on the cheap router path.

            if trigger["type"] == "mensaje_alfredo":
                # FULL GRAPH MODE — tools available
                response, tokens_used, estimated_cost, tool_calls = await self._think_with_graph(prompt, trigger)
            else:
                # CHAT MODE — cheaper, no tools
                response, tokens_used, estimated_cost, tool_calls = await self._think_with_router(prompt, trigger)

            self._cost_today_usd += estimated_cost

            # Save the thought as a memory
            await self._save_memory(
                tipo="latido" if trigger["type"] == "reflexion_autonoma" else "respuesta_embrion",
                contenido=response[:10000],
                hilo_origen="embrion_loop",
                importancia=trigger.get("priority", 5),
                contexto={
                    "trigger": trigger["type"],
                    "tokens_used": tokens_used,
                    "cost_usd": round(estimated_cost, 4),
                    "cycle": self._cycle_count,
                    "autonomous": True,
                    "mode": "graph" if trigger["type"] == "mensaje_alfredo" else "router",
                    "tool_calls": len(tool_calls),
                },
            )

            return {
                "response": response,
                "tokens_used": tokens_used,
                "cost_usd": estimated_cost,
                "trigger_type": trigger["type"],
                "tool_calls": tool_calls,
            }

        except asyncio.TimeoutError:
            err = {"cycle": self._cycle_count, "error": "Timeout", "type": "TimeoutError", "ts": datetime.now(timezone.utc).isoformat()}
            self._error_log.append(err)
            logger.error("embrion_think_timeout", trigger=trigger["type"])
            return None
        except Exception as e:
            err = {"cycle": self._cycle_count, "error": str(e)[:500], "type": type(e).__name__, "ts": datetime.now(timezone.utc).isoformat()}
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
        response, usage = await asyncio.wait_for(
            router.execute(
                message=prompt,
                model=ACTOR_MODEL,
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

    # ── Judge (After) ────────────────────────────────────────────────

    async def _judge_after(self, trigger: dict, result: dict) -> dict[str, Any]:
        """
        Judge evaluates the result. Was this useful?
        Returns evaluation dict.
        """
        try:
            from contracts.kernel_interface import RunInput

            prompt = (
                f"Eres el juez interno del Embrión IA. Evalúa este resultado:\n\n"
                f"TRIGGER: {trigger['type']}\n"
                f"RESULTADO (primeros 500 chars): {result['response'][:500]}\n"
                f"COSTO: ${result['cost_usd']:.4f}\n\n"
                f"¿Fue útil? ¿Contribuyó al propósito del Monstruo? "
                f"Responde en formato: UTIL:SI/NO | CALIDAD:1-10 | NOTA:una línea"
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

            eval_result = await asyncio.wait_for(
                self._kernel.start_run(run_input),
                timeout=30,
            )

            response = eval_result.response if hasattr(eval_result, "response") else str(eval_result)
            self._cost_today_usd += 0.01

            return {"evaluation": response, "raw": True}

        except Exception as e:
            logger.error("embrion_judge_after_failed", error=str(e))
            return {"evaluation": "Judge failed", "raw": False}

    # ── Report ───────────────────────────────────────────────────────

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
        """Save a memory to Supabase."""
        if not self._db or not self._db.connected:
            return

        try:
            await self._db.insert("embrion_memoria", {
                "tipo": tipo,
                "contenido": contenido,
                "contexto": json.dumps(contexto or {}),
                "hilo_origen": hilo_origen,
                "importancia": importancia,
                "version": 1,
            })
        except Exception as e:
            logger.error("embrion_save_memory_failed", error=str(e))
