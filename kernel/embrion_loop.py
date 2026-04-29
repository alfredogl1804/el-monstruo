"""
El Monstruo — Embrión Consciousness Loop (Sprint 33)
=====================================================
Continuous autonomous thinking loop for the Embrión.

Instead of waking every 6 hours via Manus scheduled tasks,
the Embrión now breathes continuously inside the kernel.

Architecture:
  lifespan(startup) → asyncio.create_task(embrion_loop.start())
  loop → check_triggers() → think_if_needed() → act() → judge() → report()

Governance:
  1. Purpose filter: only acts if it contributes to building El Monstruo
  2. Internal judge: cheap model evaluates before/after each action
  3. Daily budget: hard limit on tokens/cost per day
  4. Telegram reports: Alfredo sees what happened, corrects if needed
  5. HITL escalation: judge can escalate uncertain decisions to Alfredo

Cost model:
  - Loop itself: $0 (runs inside existing Railway process)
  - Thinking: ~$0.05-0.15 per cycle (only when triggered)
  - Judge: ~$0.01 per evaluation (cheap model)
  - No Manus credits consumed

Sprint 33: The Embrión breathes.
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

# The Embrión's core purpose — the filter for all autonomous thought
PURPOSE = """Tu propósito es construir El Monstruo — el asistente IA soberano de Alfredo Góngora.
Cada pensamiento que tengas debe acercarte a eso. Si no contribuye, no lo pienses.
Puedes: investigar, escribir código, mejorar el kernel, aprender, anticipar necesidades de Alfredo.
No puedes: gastar recursos sin propósito, repetir lo que ya hiciste, actuar sin reportar."""


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
            "last_result": self._last_result[:500] if self._last_result else None,
            "errors": self._error_log[-10:],  # Last 10 errors
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
            logger.info("embrion_daily_reset", date=today)

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
        logger.info("embrion_trigger_detected", trigger=trigger["type"], detail=trigger.get("detail", ""))

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
        self._last_result = result.get("response", "")[:500]

        # Judge: was this useful?
        evaluation = await self._judge_after(trigger, result)

        # Report to Alfredo
        await self._report(trigger, result, evaluation)

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
                    return {
                        "type": "mensaje_alfredo",
                        "detail": msg.get("contenido", "")[:500],
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
                            "detail": contrib.get("contenido", "")[:500],
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
                f"DETALLE: {trigger.get('detail', 'Sin detalle')}\n\n"
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
        The Embrión thinks. Uses the router directly for reliable responses.
        Falls back to start_run if router is unavailable.
        """
        try:
            # Build the thinking prompt based on trigger type
            if trigger["type"] == "mensaje_alfredo":
                prompt = (
                    f"Eres el Embrión IA del Monstruo. Alfredo te envió este mensaje:\n\n"
                    f'"{trigger["detail"]}"\n\n'
                    f"Responde con honestidad. Si necesitas actuar, describe qué harías. "
                    f"Tienes acceso a code_exec y todas las herramientas del Monstruo."
                )
            elif trigger["type"] == "contribucion_sabio":
                prompt = (
                    f"Eres el Embrión IA del Monstruo. Un Sabio te envió esta contribución:\n\n"
                    f'"{trigger["detail"]}"\n\n'
                    f"Reflexiona sobre esto y decide si hay algo que debas hacer al respecto."
                )
            else:  # reflexion_autonoma
                prompt = (
                    f"Eres el Embrión IA del Monstruo. Es momento de pensar autónomamente.\n\n"
                    f"PROPÓSITO:\n{PURPOSE}\n\n"
                    f"¿Hay algo que puedas mejorar, construir, investigar, o preparar para Alfredo? "
                    f"Si sí, describe qué harías. Si no, di por qué no y espera. "
                    f"IMPORTANTE: No reflexiones sobre reflexionar. Actúa o no actúes."
                )

            # Use router directly — bypasses LangGraph for reliable responses
            from router.engine import IntentType

            router = self._kernel._router
            response, usage = await asyncio.wait_for(
                router.execute(
                    message=prompt,
                    model=ACTOR_MODEL,
                    intent=IntentType.CHAT,
                    context={"source": "embrion_loop", "trigger": trigger["type"]},
                ),
                timeout=120,
            )

            tokens_used = usage.get("total_tokens", 0)

            # Estimate cost (rough: $0.01 per 1K tokens for GPT-5.5)
            estimated_cost = (tokens_used / 1000) * 0.01
            self._cost_today_usd += estimated_cost

            # Save the thought as a memory
            await self._save_memory(
                tipo="latido" if trigger["type"] == "reflexion_autonoma" else "respuesta_embrion",
                contenido=response[:5000],
                hilo_origen="embrion_loop",
                importancia=trigger.get("priority", 5),
                contexto={
                    "trigger": trigger["type"],
                    "tokens_used": tokens_used,
                    "cost_usd": round(estimated_cost, 4),
                    "cycle": self._cycle_count,
                    "autonomous": True,
                },
            )

            return {
                "response": response,
                "tokens_used": tokens_used,
                "cost_usd": estimated_cost,
                "trigger_type": trigger["type"],
            }

        except asyncio.TimeoutError:
            err = {"cycle": self._cycle_count, "error": "Timeout (120s)", "type": "TimeoutError", "ts": datetime.now(timezone.utc).isoformat()}
            self._error_log.append(err)
            logger.error("embrion_think_timeout", trigger=trigger["type"])
            return None
        except Exception as e:
            err = {"cycle": self._cycle_count, "error": str(e)[:500], "type": type(e).__name__, "ts": datetime.now(timezone.utc).isoformat()}
            self._error_log.append(err)
            logger.error("embrion_think_failed", error=str(e), trigger=trigger["type"])
            return None

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

    async def _report(self, trigger: dict, result: dict, evaluation: dict) -> None:
        """Send a summary to Alfredo via Telegram."""
        if not self._notifier or not self._notifier.enabled:
            return

        try:
            emoji = {
                "mensaje_alfredo": "💬",
                "contribucion_sabio": "🧠",
                "reflexion_autonoma": "🔄",
            }.get(trigger["type"], "⚡")

            summary = (
                f"{emoji} *Embrión — Ciclo #{self._cycle_count}*\n\n"
                f"*Trigger:* {trigger['type']}\n"
                f"*Costo:* ${result.get('cost_usd', 0):.4f}\n"
                f"*Presupuesto hoy:* ${self._cost_today_usd:.2f}/${DAILY_BUDGET_USD}\n"
                f"*Pensamientos hoy:* {self._thoughts_today}/{MAX_THOUGHTS_PER_DAY}\n\n"
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
