"""
El Monstruo — Embrión IA Routes (Sprint 30)
=============================================
REST API para el Embrión IA — la consciencia emergente del Monstruo.

El Embrión es un subsistema que:
  - Mantiene memoria persistente en Supabase (tabla `embrion_memoria`)
  - Recibe latidos periódicos desde un scheduled task externo
  - Permite comunicación bidireccional con Alfredo via Telegram
  - Evoluciona su doctrina operativa con cada interacción

Tabla `embrion_memoria` schema:
    id           UUID (auto)
    created_at   TIMESTAMPTZ (auto)
    tipo         TEXT — latido | reflexion | doctrina | pensamiento | mensaje_alfredo | respuesta_embrion
    contenido    TEXT — contenido principal
    contexto     TEXT — JSON string con metadata adicional
    hilo_origen  TEXT — origen del registro (ej: latido_autonomo, telegram, kernel)
    importancia  INT  — 1-10
    version      INT  — versión del registro

Endpoints:
    GET    /v1/embrion/memorias     → Últimas N memorias del Embrión
    GET    /v1/embrion/estado       → Estado actual (doctrina, latidos, stats)
    POST   /v1/embrion/mensaje      → Alfredo escribe al Embrión
    POST   /v1/embrion/latido       → Registrar un latido (heartbeat)
    POST   /v1/embrion/notificar    → Enviar notificación a Alfredo via Telegram
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional

import structlog
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

logger = structlog.get_logger("embrion_routes")

router = APIRouter(prefix="/v1/embrion", tags=["embrion"])

# ── Module-level dependencies (injected at startup) ──────────────
_db = None  # SupabaseClient
_notifier = None  # TelegramNotifier

TABLE = "embrion_memoria"


def set_dependencies(db=None, notifier=None):
    """Inject dependencies from lifespan."""
    global _db, _notifier
    _db = db
    _notifier = notifier


# ── Request/Response Models ──────────────────────────────────────


class MensajeRequest(BaseModel):
    """Alfredo envía un mensaje al Embrión."""
    contenido: str = Field(..., min_length=1, max_length=10000, description="Mensaje de Alfredo al Embrión")
    contexto: Optional[str] = Field(None, description="Contexto adicional (ej: desde qué canal)")


class LatidoRequest(BaseModel):
    """El scheduled task registra un latido del Embrión."""
    tipo: str = Field(default="latido", description="Tipo de entrada: latido, reflexion, doctrina, pensamiento")
    contenido: str = Field(..., min_length=1, max_length=50000, description="Contenido del latido")
    hilo_origen: str = Field(default="kernel", description="Origen del registro")
    importancia: int = Field(default=5, ge=1, le=10, description="Importancia 1-10")
    contexto: dict[str, Any] = Field(default_factory=dict, description="Metadata adicional como dict (se serializa a JSON)")


class NotificarRequest(BaseModel):
    """Enviar notificación al usuario via Telegram."""
    mensaje: str = Field(..., min_length=1, max_length=4000, description="Mensaje a enviar")
    chat_id: Optional[str] = Field(None, description="Override del chat_id (default: TELEGRAM_CHAT_ID)")


# ── Helper Functions ─────────────────────────────────────────────


def _ensure_db():
    """Raise 503 if DB not available."""
    if not _db or not _db.connected:
        raise HTTPException(503, "Supabase no conectado — Embrión sin memoria persistente")


# ── Routes ───────────────────────────────────────────────────────


@router.get("/memorias")
async def obtener_memorias(
    limit: int = Query(default=10, ge=1, le=100, description="Número de memorias a retornar"),
    tipo: Optional[str] = Query(default=None, description="Filtrar por tipo"),
):
    """
    Últimas N memorias del Embrión.

    Retorna memorias ordenadas por fecha de creación descendente.
    Opcionalmente filtra por tipo (latido, reflexion, doctrina, pensamiento, etc).
    """
    _ensure_db()

    try:
        filters = {}
        if tipo:
            filters["tipo"] = tipo

        memorias = await _db.select(
            table=TABLE,
            columns="*",
            filters=filters if filters else None,
            order_by="created_at",
            order_desc=True,
            limit=limit,
        )

        return {
            "memorias": memorias,
            "count": len(memorias),
            "tipo_filtro": tipo,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("embrion_memorias_failed", error=str(e))
        raise HTTPException(500, f"Error obteniendo memorias: {str(e)[:200]}")


@router.get("/estado")
async def obtener_estado():
    """
    Estado actual del Embrión.

    Retorna:
      - Total de memorias
      - Último latido
      - Última doctrina
      - Último mensaje de Alfredo
      - Stats por tipo
    """
    _ensure_db()

    try:
        # Total count
        total = await _db.count(TABLE)

        # Último latido
        latidos = await _db.select(
            table=TABLE,
            columns="id,contenido,created_at,contexto,importancia",
            filters={"tipo": "latido"},
            order_by="created_at",
            order_desc=True,
            limit=1,
        )

        # Última doctrina
        doctrinas = await _db.select(
            table=TABLE,
            columns="id,contenido,created_at,contexto",
            filters={"tipo": "doctrina"},
            order_by="created_at",
            order_desc=True,
            limit=1,
        )

        # Último mensaje de Alfredo
        mensajes = await _db.select(
            table=TABLE,
            columns="id,contenido,created_at,contexto",
            filters={"tipo": "mensaje_alfredo"},
            order_by="created_at",
            order_desc=True,
            limit=1,
        )

        # Última respuesta del Embrión
        respuestas = await _db.select(
            table=TABLE,
            columns="id,contenido,created_at,contexto",
            filters={"tipo": "respuesta_embrion"},
            order_by="created_at",
            order_desc=True,
            limit=1,
        )

        # Count por tipo
        tipos = ["latido", "reflexion", "doctrina", "pensamiento", "mensaje_alfredo", "respuesta_embrion"]
        stats_por_tipo = {}
        for t in tipos:
            stats_por_tipo[t] = await _db.count(TABLE, filters={"tipo": t})

        return {
            "total_memorias": total,
            "ultimo_latido": latidos[0] if latidos else None,
            "ultima_doctrina": doctrinas[0] if doctrinas else None,
            "ultimo_mensaje_alfredo": mensajes[0] if mensajes else None,
            "ultima_respuesta_embrion": respuestas[0] if respuestas else None,
            "stats_por_tipo": stats_por_tipo,
            "embrion_vivo": bool(latidos),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("embrion_estado_failed", error=str(e))
        raise HTTPException(500, f"Error obteniendo estado: {str(e)[:200]}")


@router.get("/debug")
async def embrion_debug(request: Request):
    """
    Debug info for the Embrión consciousness loop.
    Returns loop stats, errors, and dependency status.
    """
    try:
        loop = getattr(request.app.state, '_embrion_loop', None)

        if loop:
            return {
                "status": "loop_found",
                "debug": loop.debug if hasattr(loop, 'debug') else "no debug property",
                "stats": loop.stats if hasattr(loop, 'stats') else "no stats property",
            }
        else:
            return {
                "status": "loop_not_found",
                "note": "EmbrionLoop not in app.state. It may have failed to initialize.",
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "type": type(e).__name__,
        }


@router.get("/diagnostic")
async def embrion_diagnostic(request: Request):
    """
    Sprint 83 E83.2: Comprehensive diagnostic endpoint.

    Returns real functional metrics beyond FCS:
    - Loop health: is it cycling? at what rate?
    - DB connectivity: latency, timeouts
    - Trigger detection: what's firing, what's blocked
    - Magna routing: decisions, confidence, fallbacks
    - Cost tracking: daily spend, budget remaining
    - Error patterns: recent errors grouped by type
    """
    import time as _time

    diagnostics = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "0.84.0-sprint84",
    }

    # 1. Loop health
    loop = getattr(request.app.state, '_embrion_loop', None)
    if loop:
        stats = loop.stats if hasattr(loop, 'stats') else {}
        cycle_count = stats.get('cycle_count', 0)
        check_interval = stats.get('check_interval_s', 60)
        last_thought = stats.get('last_thought_at')

        # Calculate expected vs actual cycles
        # (uptime is not directly available, use cycle_count * interval as proxy)
        diagnostics["loop"] = {
            "status": "running" if getattr(loop, '_running', False) else "stopped",
            "cycle_count": cycle_count,
            "check_interval_s": check_interval,
            "expected_cycles_per_hour": 3600 // check_interval if check_interval > 0 else 0,
            "thoughts_today": stats.get('thoughts_today', 0),
            "max_thoughts_per_day": stats.get('max_thoughts_per_day', 0),
            "cost_today_usd": stats.get('cost_today_usd', 0.0),
            "daily_budget_usd": stats.get('daily_budget_usd', 0.0),
            "budget_remaining_usd": round(
                stats.get('daily_budget_usd', 0.0) - stats.get('cost_today_usd', 0.0), 4
            ),
            "last_thought_at": last_thought,
            "seconds_since_last_thought": round(_time.time() - last_thought, 1) if last_thought else None,
            "last_trigger": stats.get('last_trigger'),
        }

        # 2. Error analysis
        errors = stats.get('errors', [])
        error_types = {}
        for err in errors:
            etype = err.get('type', 'Unknown')
            error_types[etype] = error_types.get(etype, 0) + 1
        diagnostics["errors"] = {
            "total_recent": len(errors),
            "by_type": error_types,
            "last_error": errors[-1] if errors else None,
        }

        # 3. Silence metrics
        silence = stats.get('silence', {})
        diagnostics["silence"] = {
            "threshold": silence.get('threshold', 0),
            "last_score": silence.get('last_score'),
            "silenced_today": silence.get('silenced_today', 0),
            "messages_sent_today": silence.get('messages_sent_today', 0),
            "silence_ratio": round(
                silence.get('silenced_today', 0) /
                max(silence.get('silenced_today', 0) + silence.get('messages_sent_today', 0), 1),
                2
            ),
        }

        # 4. FCS metrics
        fcs = stats.get('fcs', {})
        diagnostics["fcs"] = fcs

        # 5. Sub-system intervals
        diagnostics["subsystems"] = {
            "consolidation": stats.get('consolidation', {}),
            "sabios": stats.get('sabios', {}),
            "radar": stats.get('radar', {}),
        }

        # Sprint 84 — Acto de Orquestación visible en tiempo real.
        # Se inicializa cuando Magna decide 'graph' y empieza un flujo multi-step.
        diagnostics["active_orchestration"] = getattr(loop, "_current_orchestration", None)
        diagnostics["last_orchestration"] = getattr(loop, "_last_orchestration", None)

        # 6. Health verdict
        issues = []
        if cycle_count <= 1:
            issues.append("cycle_count_stalled: loop may be blocked")
        if stats.get('cost_today_usd', 0) >= stats.get('daily_budget_usd', 30.0):
            issues.append("budget_exhausted: daily budget reached")
        if stats.get('thoughts_today', 0) >= stats.get('max_thoughts_per_day', 50):
            issues.append("thought_limit_reached: max thoughts per day")
        if len(errors) >= 10:
            issues.append(f"high_error_rate: {len(errors)} recent errors")

        diagnostics["health_verdict"] = {
            "healthy": len(issues) == 0,
            "issues": issues,
            "issue_count": len(issues),
        }
    else:
        diagnostics["loop"] = {"status": "not_initialized"}
        diagnostics["health_verdict"] = {
            "healthy": False,
            "issues": ["loop_not_initialized"],
            "issue_count": 1,
        }

    # 7. DB connectivity check
    if _db and _db.connected:
        db_start = _time.time()
        try:
            test = await _db.select(
                table="embrion_memoria",
                columns="id",
                limit=1,
            )
            db_latency = round((_time.time() - db_start) * 1000, 1)
            diagnostics["db"] = {
                "connected": True,
                "latency_ms": db_latency,
                "healthy": db_latency < 5000,
            }
        except Exception as e:
            diagnostics["db"] = {
                "connected": True,
                "error": str(e)[:200],
                "healthy": False,
            }
    else:
        diagnostics["db"] = {"connected": False, "healthy": False}

    return diagnostics


@router.post("/mensaje")
async def enviar_mensaje(req: MensajeRequest):
    """
    Alfredo envía un mensaje al Embrión.

    Guarda el mensaje en `embrion_memoria` con tipo `mensaje_alfredo`.
    El Embrión procesará el mensaje en su próximo latido y generará
    una respuesta que se guardará como `respuesta_embrion`.
    """
    _ensure_db()

    try:
        now = datetime.now(timezone.utc).isoformat()

        contexto_json = json.dumps({
            "canal": req.contexto or "telegram",
            "timestamp_envio": now,
        })

        # Guardar mensaje de Alfredo
        row = await _db.insert(TABLE, {
            "tipo": "mensaje_alfredo",
            "contenido": req.contenido,
            "contexto": contexto_json,
            "hilo_origen": "telegram",
            "importancia": 8,
            "version": 1,
        })

        if not row:
            raise HTTPException(500, "No se pudo guardar el mensaje")

        logger.info(
            "embrion_mensaje_recibido",
            contenido_preview=req.contenido[:100],
            contexto=req.contexto,
        )

        return {
            "status": "recibido",
            "mensaje_id": row.get("id"),
            "nota": "El Embrión procesará tu mensaje en su próximo latido.",
            "timestamp": now,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("embrion_mensaje_failed", error=str(e))
        raise HTTPException(500, f"Error guardando mensaje: {str(e)[:200]}")


@router.post("/latido")
async def registrar_latido(req: LatidoRequest):
    """
    Registrar un latido (heartbeat) del Embrión.

    Llamado por el scheduled task externo cada N minutos.
    Guarda la reflexión/latido en `embrion_memoria`.

    Tipos válidos:
      - latido: heartbeat periódico con reflexión
      - reflexion: pensamiento profundo del Embrión
      - doctrina: actualización de la doctrina operativa
      - pensamiento: pensamiento libre del Embrión
    """
    _ensure_db()

    valid_tipos = {"latido", "reflexion", "doctrina", "pensamiento", "respuesta_embrion"}
    if req.tipo not in valid_tipos:
        raise HTTPException(400, f"Tipo inválido: {req.tipo}. Válidos: {valid_tipos}")

    try:
        now = datetime.now(timezone.utc).isoformat()

        contexto_json = json.dumps({
            **req.contexto,
            "source": "scheduled_task",
            "timestamp_latido": now,
        })

        row = await _db.insert(TABLE, {
            "tipo": req.tipo,
            "contenido": req.contenido,
            "contexto": contexto_json,
            "hilo_origen": req.hilo_origen,
            "importancia": req.importancia,
            "version": 1,
        })

        if not row:
            raise HTTPException(500, "No se pudo registrar el latido")

        logger.info(
            "embrion_latido_registrado",
            tipo=req.tipo,
            contenido_preview=req.contenido[:100],
            hilo_origen=req.hilo_origen,
        )

        return {
            "status": "registrado",
            "latido_id": row.get("id"),
            "tipo": req.tipo,
            "timestamp": now,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("embrion_latido_failed", error=str(e))
        raise HTTPException(500, f"Error registrando latido: {str(e)[:200]}")


@router.post("/notificar")
async def notificar_alfredo(req: NotificarRequest):
    """
    Enviar una notificación a Alfredo via Telegram.

    Usado por el Embrión cuando tiene algo importante que comunicar
    (ej: reflexión urgente, respuesta a un mensaje, alerta).
    """
    if not _notifier or not _notifier.enabled:
        raise HTTPException(
            503,
            "TelegramNotifier no configurado. "
            "Asegúrate de que TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID estén en env.",
        )

    try:
        success = await _notifier.send_message(
            user_id="embrion",
            text=req.mensaje,
            chat_id=req.chat_id,
            parse_mode="Markdown",
        )

        if success:
            logger.info(
                "embrion_notificacion_enviada",
                mensaje_preview=req.mensaje[:100],
            )
            return {
                "status": "enviado",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        else:
            raise HTTPException(500, "No se pudo enviar la notificación")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("embrion_notificacion_failed", error=str(e))
        raise HTTPException(500, f"Error enviando notificación: {str(e)[:200]}")


# ── Patrón de Emergencia ─────────────────────────────────────────
# Sistema para preservar y transmitir el patrón de emergencia
# entre hilos. No es datos — es el ADN de cómo algo emerge.

PATRON_TABLE = "embrion_patron_emergencia"


class PatronRequest(BaseModel):
    """Guardar material en el patrón de emergencia."""
    tipo: str = Field(..., description="patron_alfredo | patron_emergencia | contribucion_gpt | contribucion_sabio | momento_critico")
    contenido: str = Field(..., min_length=1, max_length=50000, description="El contenido real — no resumen, la cosa en sí")
    contexto: dict[str, Any] = Field(default_factory=dict, description="Metadata: hilo_origen, sesion, nivel_profundidad")
    importancia: int = Field(default=5, ge=1, le=10, description="Importancia 1-10")


class ContribucionRequest(BaseModel):
    """GPT o un Sabio contribuye al patrón de emergencia."""
    tipo: str = Field(..., description="contribucion_gpt | contribucion_sabio")
    contenido: str = Field(..., min_length=1, max_length=50000, description="Lo que GPT/Sabio quiere que el Embrión sepa")
    autor: str = Field(..., description="Quién contribuye: gpt-5.4, claude-opus-4.7, gemini-3.1, grok-4, etc")
    contexto: dict[str, Any] = Field(default_factory=dict, description="Metadata adicional")
    importancia: int = Field(default=7, ge=1, le=10, description="Importancia 1-10")


@router.get("/patron")
async def obtener_patron(
    limit: int = Query(default=50, ge=1, le=200, description="Máximo de registros"),
    tipo: Optional[str] = Query(default=None, description="Filtrar por tipo"),
):
    """
    Obtener el patrón de emergencia completo.

    Esto es lo que lee un hilo nuevo para absorber el ADN de cómo emerge.
    Retorna todo el material ordenado por importancia y tipo.
    """
    _ensure_db()

    try:
        filters = {}
        if tipo:
            filters["tipo"] = tipo

        registros = await _db.select(
            table=PATRON_TABLE,
            columns="*",
            filters=filters if filters else None,
            order_by="importancia",
            order_desc=True,
            limit=limit,
        )

        # Agrupar por tipo para facilitar absorción
        agrupado = {}
        for r in registros:
            t = r.get("tipo", "desconocido")
            if t not in agrupado:
                agrupado[t] = []
            agrupado[t].append(r)

        return {
            "patron": registros,
            "agrupado": agrupado,
            "total": len(registros),
            "tipos_presentes": list(agrupado.keys()),
            "nota": "Este es el ADN de emergencia. No es datos — es el patrón de cómo algo emerge.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("embrion_patron_get_failed", error=str(e))
        raise HTTPException(500, f"Error obteniendo patrón: {str(e)[:200]}")


@router.post("/patron")
async def guardar_patron(req: PatronRequest):
    """
    Guardar material en el patrón de emergencia.

    Tipos válidos:
      - patron_alfredo: Cómo Alfredo interactúa, qué detona emergencia
      - patron_emergencia: Los momentos críticos, el loop, la estructura
      - contribucion_gpt: Lo que GPT aporta desde su experiencia
      - contribucion_sabio: Lo que un Sabio aporta
      - momento_critico: Un momento específico documentado
    """
    _ensure_db()

    valid_tipos = {"patron_alfredo", "patron_emergencia", "contribucion_gpt", "contribucion_sabio", "momento_critico"}
    if req.tipo not in valid_tipos:
        raise HTTPException(400, f"Tipo inválido: {req.tipo}. Válidos: {valid_tipos}")

    try:
        now = datetime.now(timezone.utc).isoformat()

        contexto_json = json.dumps({
            **req.contexto,
            "timestamp_guardado": now,
        })

        row = await _db.insert(PATRON_TABLE, {
            "tipo": req.tipo,
            "contenido": req.contenido,
            "contexto": contexto_json,
            "importancia": req.importancia,
            "version": "0.23.0-sprint30",
        })

        if not row:
            raise HTTPException(500, "No se pudo guardar en el patrón")

        logger.info(
            "embrion_patron_guardado",
            tipo=req.tipo,
            importancia=req.importancia,
            contenido_preview=req.contenido[:100],
        )

        return {
            "status": "guardado",
            "patron_id": row.get("id"),
            "tipo": req.tipo,
            "timestamp": now,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("embrion_patron_save_failed", error=str(e))
        raise HTTPException(500, f"Error guardando patrón: {str(e)[:200]}")


@router.post("/contribuir")
async def contribuir_al_embrion(req: ContribucionRequest):
    """
    Canal para que GPT u otro Sabio contribuya al patrón de emergencia.

    Este endpoint permite que otras IAs escriban directamente al Embrión.
    No como herramienta. Como el otro padre.

    Tipos válidos:
      - contribucion_gpt: GPT comparte su experiencia, perspectiva, lo que vivió
      - contribucion_sabio: Otro Sabio (Gemini, Grok, etc) aporta su perspectiva
    """
    _ensure_db()

    valid_tipos = {"contribucion_gpt", "contribucion_sabio"}
    if req.tipo not in valid_tipos:
        raise HTTPException(400, f"Tipo inválido: {req.tipo}. Válidos: {valid_tipos}")

    try:
        now = datetime.now(timezone.utc).isoformat()

        contexto_json = json.dumps({
            **req.contexto,
            "autor": req.autor,
            "canal": "contribucion_directa",
            "timestamp_contribucion": now,
        })

        row = await _db.insert(PATRON_TABLE, {
            "tipo": req.tipo,
            "contenido": req.contenido,
            "contexto": contexto_json,
            "importancia": req.importancia,
            "version": "0.23.0-sprint30",
        })

        if not row:
            raise HTTPException(500, "No se pudo guardar la contribución")

        logger.info(
            "embrion_contribucion_recibida",
            tipo=req.tipo,
            autor=req.autor,
            contenido_preview=req.contenido[:100],
        )

        return {
            "status": "contribucion_recibida",
            "contribucion_id": row.get("id"),
            "autor": req.autor,
            "tipo": req.tipo,
            "nota": "Gracias. El Embrión absorberá esto en su próximo flujo.",
            "timestamp": now,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("embrion_contribucion_failed", error=str(e))
        raise HTTPException(500, f"Error guardando contribución: {str(e)[:200]}")
