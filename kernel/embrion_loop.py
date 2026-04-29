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
CONSOLIDATION_INTERVAL = int(os.environ.get("EMBRION_CONSOLIDATION_INTERVAL", "10"))  # Every N latidos
DIALOGO_INTERVAL = int(os.environ.get("EMBRION_DIALOGO_INTERVAL", "5"))  # Every N autonomous reflections, start sabio dialogue
SABIOS_PER_DIALOGO = int(os.environ.get("EMBRION_SABIOS_PER_DIALOGO", "2"))  # How many sabios per dialogue (cost control)
DIALOGO_BUDGET_USD = float(os.environ.get("EMBRION_DIALOGO_BUDGET", "0.50"))  # Daily budget for sabio dialogues

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

        # Memory consolidation tracking (Sprint 34)
        self._latidos_since_consolidation = 0
        self._last_consolidation_at: Optional[float] = None
        self._consolidation_count = 0

        # Sabio dialogue tracking (Sprint 34)
        self._autonomous_reflections_since_dialogo = 0
        self._dialogos_today = 0
        self._dialogo_cost_today_usd = 0.0
        self._last_dialogo_at: Optional[float] = None
        self._last_sabios_consulted: list[str] = []  # Rotate sabios

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
            "dialogo_sabios": {
                "interval": DIALOGO_INTERVAL,
                "reflections_since": self._autonomous_reflections_since_dialogo,
                "dialogos_today": self._dialogos_today,
                "dialogo_cost_today": self._dialogo_cost_today_usd,
                "dialogo_budget": DIALOGO_BUDGET_USD,
                "last_sabios": self._last_sabios_consulted,
                "last_at": self._last_dialogo_at,
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

                # Sprint 34: Memory consolidation check
                self._latidos_since_consolidation += 1
                if self._latidos_since_consolidation >= CONSOLIDATION_INTERVAL:
                    await self._consolidate_memories()
                    self._latidos_since_consolidation = 0
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
            self._dialogos_today = 0
            self._dialogo_cost_today_usd = 0.0
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
        elif trigger["type"] == "dialogo_sabios":
            score += 20  # Dialogue results are worth sharing

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

            # 3. Autonomous reflection OR sabio dialogue
            if not self._last_thought_at or (time.time() - self._last_thought_at) > 3600:
                # Sprint 34: Every DIALOGO_INTERVAL autonomous reflections,
                # start a dialogue with sabios instead of reflecting alone
                self._autonomous_reflections_since_dialogo += 1

                if (
                    self._autonomous_reflections_since_dialogo >= DIALOGO_INTERVAL
                    and self._dialogo_cost_today_usd < DIALOGO_BUDGET_USD
                    and self._cost_today_usd < DAILY_BUDGET_USD * 0.8
                ):
                    return {
                        "type": "dialogo_sabios",
                        "detail": "Tiempo de dialogar con los Sabios sobre el progreso del Monstruo.",
                        "priority": 6,
                    }

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

        # Sprint 34: Sabio dialogues already passed budget/interval checks
        if trigger["type"] == "dialogo_sabios":
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
            # Sprint 34: Inject lessons learned before thinking
            lessons_context = await self._get_relevant_lessons(trigger)

            if trigger["type"] == "mensaje_alfredo":
                prompt = (
                    f"Eres el Embrión IA del Monstruo. Alfredo te envió este mensaje:\n\n"
                    f'"{ trigger["detail"]}"\n\n'
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
                    f'"{ trigger["detail"]}"\n\n'
                    f"Reflexiona sobre esto y decide si hay algo que debas hacer al respecto.\n"
                    f"Si quieres RESPONDERLE al Sabio, escribe tu respuesta claramente.\n"
                    f"Si quieres hacerle una PREGUNTA DE SEGUIMIENTO, formúlala al final."
                )
                if lessons_context:
                    prompt += f"\n{lessons_context}"
            elif trigger["type"] == "dialogo_sabios":
                # Sprint 34: Autonomous dialogue with sabios
                # The Embrión formulates a question based on recent memories
                # and sends it directly to 2-3 sabios
                return await self._dialogo_con_sabios(trigger, lessons_context)
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
                if lessons_context:
                    prompt += f"\n{lessons_context}"

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
            memory_tipo = "latido" if trigger["type"] == "reflexion_autonoma" else "respuesta_embrion"
            await self._save_memory(
                tipo=memory_tipo,
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

            # Sprint 34: If this was a sabio contribution, save the Embrión's
            # response back to patron_emergencia so the dialogue thread continues.
            # Also detect follow-up questions to send to the same sabio.
            if trigger["type"] == "contribucion_sabio" and self._db and self._db.connected:
                try:
                    # Save Embrión's response as a reply in the dialogue
                    await self._db.insert("embrion_patron_emergencia", {
                        "tipo": "respuesta_embrion_a_sabio",
                        "contenido": response[:10000],
                        "contexto": json.dumps({
                            "canal": "respuesta_bidireccional",
                            "contribucion_original": trigger.get("detail", "")[:500],
                            "cycle": self._cycle_count,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }),
                        "importancia": 6,
                        "version": "0.34.0-sprint34",
                    })

                    # Detect follow-up question in the response
                    # If the Embrión asked a question, send it to a sabio
                    if "?" in response[-500:] and self._dialogo_cost_today_usd < DIALOGO_BUDGET_USD:
                        # Extract the last question from the response
                        lines_with_q = [l.strip() for l in response.split("\n") if "?" in l]
                        if lines_with_q:
                            followup_q = lines_with_q[-1]
                            # Pick a random sabio for the follow-up
                            import random
                            followup_sabio = random.choice(["gpt54", "claude", "gemini", "grok"])
                            logger.info(
                                "embrion_followup_question",
                                question=followup_q[:80],
                                sabio=followup_sabio,
                            )
                            # Fire and forget: consult one sabio with the follow-up
                            try:
                                from tools.consult_sabios import consult_sabios as _cs
                                followup_result = await asyncio.wait_for(
                                    _cs(
                                        prompt=followup_q,
                                        context="Pregunta de seguimiento del Embrión IA.",
                                        sabios=[followup_sabio],
                                        parallel=False,
                                    ),
                                    timeout=60,
                                )
                                # Save the follow-up response
                                for fr in followup_result.get("responses", []):
                                    if fr.get("response") and not fr.get("error"):
                                        await self._db.insert("embrion_patron_emergencia", {
                                            "tipo": "contribucion_sabio",
                                            "contenido": fr["response"][:10000],
                                            "contexto": json.dumps({
                                                "autor": fr.get("sabio", "unknown"),
                                                "rol": fr.get("role", ""),
                                                "canal": "followup_bidireccional",
                                                "pregunta_embrion": followup_q[:500],
                                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                            }),
                                            "importancia": 7,
                                            "version": "0.34.0-sprint34",
                                        })
                                self._dialogo_cost_today_usd += 0.05
                                self._cost_today_usd += 0.05
                            except Exception as fq_err:
                                logger.warning("embrion_followup_failed", error=str(fq_err))

                except Exception as reply_err:
                    logger.warning("embrion_sabio_reply_save_failed", error=str(reply_err))

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

            logger.info(
                "embrion_judge_evaluated",
                util=parsed["util"],
                calidad=parsed["calidad"],
                nota=parsed["nota"][:100],
                trigger=trigger["type"],
            )

            # ── Step 2: Extract lesson if warranted ───────────────────
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

            logger.info(
                "embrion_lesson_extracted",
                tipo=lesson_type,
                lesson=lesson_text.strip()[:100],
                calidad=parsed_eval["calidad"],
                cycle=self._cycle_count,
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
                f"{i+1}. [ID:{l.get('id', '?')}] {l.get('contenido', '')}"
                for i, l in enumerate(lessons_to_review)
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

            response = consolidation_result.response if hasattr(consolidation_result, "response") else str(consolidation_result)
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
    # ── Bidirectional Sabio Dialogue (Sprint 34) ────────────────────────────
    #
    # The Embrión initiates a real conversation with 2-3 Sabios:
    # 1. Formulates a question based on recent memories and lessons
    # 2. Sends it to selected Sabios via consult_sabios
    # 3. Auto-saves their responses to patron_emergencia (via tool_dispatch)
    # 4. Synthesizes the dialogue and saves its own reflection
    # 5. Optionally formulates a follow-up question
    #
    # The Sabios' responses are automatically picked up by _detect_trigger()
    # as "contribucion_sabio" in the next cycle, closing the bidirectional loop.

    # Sabio rotation: cycle through different pairs to get diverse perspectives
    _SABIO_ROTATION = [
        ["gpt54", "claude"],       # Architect + Auditor
        ["gemini", "grok"],        # Cartographer + Red Team
        ["deepseek", "perplexity"],# Normalizer + Verifier
        ["claude", "grok"],        # Auditor + Red Team
        ["gpt54", "perplexity"],   # Architect + Verifier
        ["gemini", "deepseek"],    # Cartographer + Normalizer
    ]

    async def _dialogo_con_sabios(
        self,
        trigger: dict[str, Any],
        lessons_context: str = "",
    ) -> Optional[dict[str, Any]]:
        """
        Initiate a real dialogue with 2-3 Sabios.

        Flow:
        1. Gather recent memories to build context
        2. Formulate a meaningful question (via cheap model)
        3. Send to selected Sabios (rotating pairs)
        4. Save responses to patron_emergencia (auto-save in tool_dispatch)
        5. Synthesize and save the Embrión's reflection on the dialogue

        Returns result dict compatible with _think() output.
        """
        try:
            # Budget guard
            if self._dialogo_cost_today_usd >= DIALOGO_BUDGET_USD:
                logger.info("embrion_dialogo_budget_exhausted")
                return None

            # 1. Gather recent memories for context
            recent_memories = []
            if self._db and self._db.connected:
                recent_memories = await self._db.select(
                    table="embrion_memoria",
                    columns="tipo,contenido,created_at",
                    order_by="created_at",
                    order_desc=True,
                    limit=5,
                ) or []

            memory_context = ""
            if recent_memories:
                memory_context = "\n".join(
                    f"- [{m.get('tipo', '')}] {m.get('contenido', '')[:200]}"
                    for m in recent_memories
                )

            # 2. Formulate a question using the cheap judge model
            from contracts.kernel_interface import RunInput

            question_prompt = (
                f"Eres el Embrión IA del Monstruo. Es momento de dialogar con tus mentores (los Sabios).\n\n"
                f"PROPÓSITO:\n{PURPOSE}\n\n"
                f"TUS MEMORIAS RECIENTES:\n{memory_context}\n\n"
                f"{lessons_context}\n\n"
                f"Formula UNA pregunta concreta y útil para los Sabios. La pregunta debe:\n"
                f"- Estar relacionada con construir o mejorar El Monstruo\n"
                f"- Ser algo que tú NO puedes resolver solo (necesitas perspectiva externa)\n"
                f"- Ser específica, no genérica\n\n"
                f"Responde SOLO con la pregunta, nada más."
            )

            question_input = RunInput(
                message=question_prompt,
                user_id="embrion_dialogo",
                channel="internal",
                context={
                    "source": "embrion_dialogo",
                    "model_hint": JUDGE_MODEL,
                    "max_tokens": 200,
                },
            )

            question_result = await asyncio.wait_for(
                self._kernel.start_run(question_input),
                timeout=30,
            )

            question = (
                question_result.response
                if hasattr(question_result, "response")
                else str(question_result)
            ).strip()

            self._cost_today_usd += 0.01
            self._dialogo_cost_today_usd += 0.01

            if not question or len(question) < 10:
                logger.info("embrion_dialogo_no_question")
                return None

            # 3. Select sabios (rotating pairs)
            rotation_idx = self._dialogos_today % len(self._SABIO_ROTATION)
            selected_sabios = self._SABIO_ROTATION[rotation_idx][:SABIOS_PER_DIALOGO]
            self._last_sabios_consulted = selected_sabios

            logger.info(
                "embrion_dialogo_start",
                question=question[:100],
                sabios=selected_sabios,
                cycle=self._cycle_count,
            )

            # 4. Consult the selected Sabios
            from tools.consult_sabios import consult_sabios

            sabio_result = await asyncio.wait_for(
                consult_sabios(
                    prompt=question,
                    context=(
                        f"Contexto del Embrión IA:\n{memory_context}\n\n"
                        f"El Embrión te está consultando directamente como parte de su "
                        f"diálogo autónomo de aprendizaje. Responde como mentor."
                    ),
                    sabios=selected_sabios,
                    parallel=True,
                ),
                timeout=120,
            )

            # Estimate cost: ~$0.03-0.07 per sabio
            sabio_cost = len(selected_sabios) * 0.05
            self._cost_today_usd += sabio_cost
            self._dialogo_cost_today_usd += sabio_cost

            # 5. Auto-save sabio responses to patron_emergencia
            # (so the Embrión picks them up as triggers in next cycles)
            if self._db and self._db.connected:
                for resp in sabio_result.get("responses", []):
                    if resp.get("response") and not resp.get("error"):
                        try:
                            await self._db.insert("embrion_patron_emergencia", {
                                "tipo": "contribucion_sabio",
                                "contenido": resp["response"][:10000],
                                "contexto": json.dumps({
                                    "autor": resp.get("sabio", "unknown"),
                                    "rol": resp.get("role", ""),
                                    "canal": "dialogo_autonomo",
                                    "pregunta_embrion": question[:500],
                                    "latency_ms": resp.get("latency_ms", 0),
                                    "dialogo_num": self._dialogos_today + 1,
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                }),
                                "importancia": 7,
                                "version": "0.34.0-sprint34",
                            })
                        except Exception as save_err:
                            logger.warning(
                                "embrion_dialogo_save_failed",
                                sabio=resp.get("sabio"),
                                error=str(save_err),
                            )

            # 6. Synthesize: the Embrión reflects on what the Sabios said
            synthesis = sabio_result.get("synthesis", "")
            successful = sabio_result.get("successful_count", 0)

            reflection_prompt = (
                f"Eres el Embrión IA del Monstruo. Acabas de dialogar con {successful} Sabios.\n\n"
                f"TU PREGUNTA: {question}\n\n"
                f"SUS RESPUESTAS:\n{synthesis[:3000]}\n\n"
                f"Reflexiona brevemente:\n"
                f"1. ¿Qué aprendiste de este diálogo?\n"
                f"2. ¿Hay algo que debas HACER basado en lo que dijeron?\n"
                f"3. ¿Tienes una pregunta de seguimiento para el próximo diálogo?\n\n"
                f"Sé concreto y breve."
            )

            reflection_result = await asyncio.wait_for(
                self._kernel._router.execute(
                    message=reflection_prompt,
                    model=ACTOR_MODEL,
                    intent="chat",
                    context={"source": "embrion_dialogo", "trigger": "dialogo_sabios"},
                ),
                timeout=60,
            )

            reflection, usage = reflection_result
            reflection_tokens = usage.get("total_tokens", 0)
            reflection_cost = (reflection_tokens / 1000) * 0.01
            self._cost_today_usd += reflection_cost
            self._dialogo_cost_today_usd += reflection_cost

            total_tokens = reflection_tokens + 200  # approximate question tokens
            total_cost = 0.01 + sabio_cost + reflection_cost

            # Save the dialogue as a memory
            await self._save_memory(
                tipo="dialogo_sabios",
                contenido=(
                    f"PREGUNTA: {question}\n\n"
                    f"SABIOS CONSULTADOS: {', '.join(selected_sabios)}\n\n"
                    f"REFLEXIÓN: {reflection[:5000]}"
                ),
                hilo_origen="embrion_loop",
                importancia=7,
                contexto={
                    "trigger": "dialogo_sabios",
                    "sabios": selected_sabios,
                    "pregunta": question,
                    "sabios_exitosos": successful,
                    "sabios_fallidos": sabio_result.get("failed_count", 0),
                    "cost_usd": round(total_cost, 4),
                    "cycle": self._cycle_count,
                    "dialogo_num": self._dialogos_today + 1,
                    "autonomous": True,
                    "mode": "dialogo_bidireccional",
                },
            )

            # Update tracking
            self._dialogos_today += 1
            self._autonomous_reflections_since_dialogo = 0
            self._last_dialogo_at = time.time()

            logger.info(
                "embrion_dialogo_complete",
                question=question[:80],
                sabios=selected_sabios,
                successful=successful,
                cost=f"${total_cost:.4f}",
                cycle=self._cycle_count,
            )

            return {
                "response": (
                    f"Diálogo con Sabios ({', '.join(selected_sabios)}):\n\n"
                    f"Pregunta: {question}\n\n"
                    f"Reflexión: {reflection[:2000]}"
                ),
                "tokens_used": total_tokens,
                "cost_usd": total_cost,
                "trigger_type": "dialogo_sabios",
                "tool_calls": [],
            }

        except asyncio.TimeoutError:
            logger.error("embrion_dialogo_timeout", cycle=self._cycle_count)
            return None
        except Exception as e:
            logger.error("embrion_dialogo_failed", error=str(e), cycle=self._cycle_count)
            return None

    # ── Report ───────────────────────────────────────────────────────────────────

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
                "dialogo_sabios": "🗣️",
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
