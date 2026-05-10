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

    from kernel import __version__ as _kernel_version  # Sprint Memento B7 hotfix: dejar de hardcodear

    diagnostics = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": _kernel_version,
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



# ╔═══════════════════════════════════════════════════════════════════════╗
# ║ Sprint EMBRION-NEEDS-001 — Tarea 3 — Write Policy con HITL real      ║
# ║                                                                       ║
# ║ Endpoints HTTP para la cola de proposals de escritura del embrión.   ║
# ║ Cada proposal requiere aprobación humana antes de ejecutarse.        ║
# ║                                                                       ║
# ║ Lógica viva en kernel/embrion_write_policy.py.                       ║
# ╚═══════════════════════════════════════════════════════════════════════╝

from kernel import embrion_write_policy as _wp


class _DbToWritePolicyAdapter:
    """Adaptador que envuelve el cliente async `_db` (memory.supabase_client.
    SupabaseClient) y expone la firma sync que espera `embrion_write_policy`
    (select(table, params), insert(table, payload), update(table, params, payload)).

    Implementación: traduce los filtros estilo PostgREST (`eq.X`, `gte.X`, ...)
    a los kwargs nativos del SupabaseClient async y bloquea con asyncio.run en
    el thread del request handler. Para endpoints FastAPI usaremos el handler
    async directo y NO este adaptador; el adaptador queda disponible para
    invocaciones síncronas desde scripts auxiliares.
    """
    # Reservado para uso futuro (cron/script). Los handlers async usan _db
    # directamente vía las funciones helper más abajo.


def _parse_postgrest_filter(value: str):
    """Convierte 'eq.X' / 'gte.Y' / 'lte.Z' a (operator, raw_value)."""
    if not isinstance(value, str):
        return ("eq", value)
    for op in ("gte.", "lte.", "gt.", "lt.", "eq.", "in."):
        if value.startswith(op):
            return (op[:-1], value[len(op):])
    return ("eq", value)


# ── Helpers async que llaman al embrion_write_policy reusando las primitivas
# del SupabaseClient global (_db).

WRITE_PROPOSALS_TABLE = "embrion_write_proposals"


async def _wp_select_pending(limit: int = 20) -> list[dict]:
    """Wrapper async sobre list_pending() usando el _db inyectado."""
    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).isoformat()
    rows = await _db.select(
        table=WRITE_PROPOSALS_TABLE,
        columns="*",
        filters={"approval_status": "pending"},
        order_by="created_at",
        order_desc=False,
        limit=limit,
    )
    # Filtro de expiración en memoria (SupabaseClient no expone gte directo)
    return [r for r in (rows or []) if (r.get("expires_at") or "") >= now_iso]


async def _wp_get_proposal(proposal_id: str) -> Optional[dict]:
    rows = await _db.select(
        table=WRITE_PROPOSALS_TABLE,
        columns="*",
        filters={"id": proposal_id},
        limit=1,
    )
    return rows[0] if rows else None


async def _wp_insert_proposal(row: dict) -> Optional[dict]:
    return await _db.insert(WRITE_PROPOSALS_TABLE, row)


async def _wp_update_proposal(proposal_id: str, expected_status: str, update: dict) -> Optional[dict]:
    """UPDATE con optimistic concurrency: verifica status ANTES de actualizar."""
    current = await _wp_get_proposal(proposal_id)
    if not current:
        return None
    if current["approval_status"] != expected_status:
        return None  # race: alguien lo cambió
    return await _db.update(
        table=WRITE_PROPOSALS_TABLE,
        data=update,
        filters={"id": proposal_id},
    )


# ── Pydantic models

class ProposeRequest(BaseModel):
    proposal_type: str = Field(..., description="code_commit | db_write | external_api_call | other")
    summary: str = Field(..., min_length=1, max_length=500)
    payload: dict = Field(..., description="Payload arbitrario JSON-serializable")
    proposed_by: str = Field(default="embrion_loop")
    cycle_id: Optional[int] = None
    latido_id: Optional[str] = None
    risk_level: str = Field(default="medium", description="low | medium | high | critical")
    expires_in_hours: Optional[int] = Field(default=None, ge=0, le=168)
    idempotency_key: Optional[str] = None


class ApproveRequest(BaseModel):
    approved_by: str = Field(..., min_length=1, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=1000)


class RejectRequest(BaseModel):
    approved_by: str = Field(..., min_length=1, max_length=100)
    reason: str = Field(..., min_length=1, max_length=1000)


# ── Endpoints

@router.post("/propose")
async def crear_proposal(req: ProposeRequest):
    """
    El Embrión propone una escritura que requiere aprobación humana.

    Flujo:
      1. Validar inputs (proposal_type, risk_level, payload).
      2. Calcular idempotency_key (sha256) si no se provee.
      3. Si ya existe una proposal con ese key → retornarla (no duplicar).
      4. Insertar pending con TTL (default 24h).
      5. Notificar HITL vía cowork_bridge (insert a embrion_memoria importancia=10).

    Returns:
      proposal_id, created (bool), status, expires_at, summary, risk_level
    """
    _ensure_db()

    # Validaciones del módulo (lanzan ValueError → 400)
    if req.proposal_type not in _wp.PROPOSAL_TYPES:
        raise HTTPException(400, f"proposal_type inválido: {req.proposal_type}")
    if req.risk_level not in _wp.RISK_LEVELS:
        raise HTTPException(400, f"risk_level inválido: {req.risk_level}")

    try:
        idempotency_key = req.idempotency_key or _wp.compute_idempotency_key(
            req.proposal_type, req.payload
        )

        # 1) Verificar idempotency
        existing_rows = await _db.select(
            table=WRITE_PROPOSALS_TABLE,
            columns="*",
            filters={"idempotency_key": idempotency_key},
            limit=1,
        )
        if existing_rows:
            e = existing_rows[0]
            logger.info("embrion_propose_idempotent_hit", proposal_id=e["id"])
            return {
                "proposal_id": str(e["id"]),
                "created": False,
                "status": e["approval_status"],
                "expires_at": e["expires_at"],
                "summary": e["summary"],
                "risk_level": e["risk_level"],
            }

        # 2) Insert
        from datetime import datetime, timedelta, timezone
        ttl_hours = (
            req.expires_in_hours
            if req.expires_in_hours is not None
            else _wp.DEFAULT_EXPIRATION_HOURS
        )
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=ttl_hours)).isoformat()

        row_payload = {
            "proposed_by": req.proposed_by,
            "cycle_id": req.cycle_id,
            "latido_id": req.latido_id,
            "idempotency_key": idempotency_key,
            "proposal_type": req.proposal_type,
            "summary": req.summary.strip(),
            "payload_json": req.payload,
            "risk_level": req.risk_level,
            "approval_status": "pending",
            "expires_at": expires_at,
        }
        inserted = await _wp_insert_proposal(row_payload)
        if not inserted:
            raise HTTPException(500, "No se pudo insertar la proposal")

        proposal_id = str(inserted["id"])

        # 3) Notificación HITL multi-canal (Tarea 4 — 2026-05-10)
        # Doctrina: 2 canales independientes garantizan resiliencia.
        # cowork_bridge (insert a embrion_memoria) + telegram (botones inline).
        notify_text = (
            f"[HITL EMBRION] Proposal {proposal_id[:8]} requiere aprobación.\n"
            f"Tipo: {req.proposal_type} | Riesgo: {req.risk_level}\n"
            f"Resumen: {req.summary}\n"
            f"Expira: {expires_at}\n"
            f"Aprobar: POST /v1/embrion/approve/{proposal_id}\n"
            f"Listar pending: GET /v1/embrion/proposals"
        )
        notified_channels: list[str] = []

        # Canal 1: cowork_bridge (insert a embrion_memoria)
        try:
            await _db.insert(TABLE, {
                "tipo": "respuesta_embrion",
                "hilo_origen": "embrion_write_policy",
                "contenido": notify_text,
                "importancia": 10,
                "contexto": json.dumps({
                    "kind": "hitl_proposal_pending",
                    "proposal_id": proposal_id,
                    "proposal_type": req.proposal_type,
                    "risk_level": req.risk_level,
                }),
            })
            notified_channels.append("cowork_bridge")
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "embrion_propose_notify_cowork_bridge_failed",
                proposal_id=proposal_id,
                error=str(exc),
            )

        # Canal 2: telegram (botones inline Aprobar/Rechazar) — Tarea 4
        # Firma de send_proposal_for_hitl (PR #44 final, post-audit Cowork):
        #   (proposal_id, action_type, risk_level, target, reason,
        #    cost_estimate_usd=0.0, expires_at="", chat_id=None)
        try:
            from kernel.runner.telegram_notifier import TelegramNotifier  # noqa: PLC0415
            tg_notifier = TelegramNotifier()
            if tg_notifier.enabled:
                # `target` y `cost_estimate_usd` se derivan del payload si los provee el embrión;
                # si no, fallback a strings/numbers seguros.
                tg_target = str(
                    req.payload.get("target")
                    or req.payload.get("resource")
                    or req.payload.get("table")
                    or req.payload.get("endpoint")
                    or "unspecified"
                )
                tg_cost = float(req.payload.get("cost_estimate_usd") or 0.0)
                tg_result = await tg_notifier.send_proposal_for_hitl(
                    proposal_id=proposal_id,
                    action_type=req.proposal_type,
                    risk_level=req.risk_level,
                    target=tg_target,
                    reason=req.summary,
                    cost_estimate_usd=tg_cost,
                    expires_at=expires_at,
                )
                if tg_result and tg_result.get("ok"):
                    notified_channels.append("telegram")
                else:
                    logger.warning(
                        "embrion_propose_notify_telegram_send_failed",
                        proposal_id=proposal_id,
                        result=tg_result,
                    )
            else:
                logger.info(
                    "embrion_propose_notify_telegram_disabled",
                    proposal_id=proposal_id,
                    hint="TELEGRAM_BOT_TOKEN/CHAT_ID not set",
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "embrion_propose_notify_telegram_failed",
                proposal_id=proposal_id,
                error=str(exc),
            )

        # Persist which channels succeeded
        if notified_channels:
            try:
                await _db.update(
                    table=WRITE_PROPOSALS_TABLE,
                    data={
                        "notified_at": datetime.now(timezone.utc).isoformat(),
                        "notified_via": ",".join(notified_channels),
                    },
                    filters={"id": proposal_id},
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "embrion_propose_mark_notified_failed",
                    proposal_id=proposal_id,
                    error=str(exc),
                )
        else:
            logger.error(
                "embrion_propose_all_channels_failed",
                proposal_id=proposal_id,
            )

        logger.info(
            "embrion_proposed",
            proposal_id=proposal_id,
            proposal_type=req.proposal_type,
            risk_level=req.risk_level,
            cycle_id=req.cycle_id,
        )

        return {
            "proposal_id": proposal_id,
            "created": True,
            "status": "pending",
            "expires_at": expires_at,
            "summary": req.summary.strip(),
            "risk_level": req.risk_level,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("embrion_propose_failed", error=str(e))
        raise HTTPException(500, f"Error creando proposal: {str(e)[:200]}")


@router.post("/approve/{proposal_id}")
async def aprobar_proposal(proposal_id: str, req: ApproveRequest):
    """
    Aprobar una proposal pending. Solo permitido sobre status='pending'.

    El worker de ejecución (cron o trigger) tomará la proposal aprobada
    y la ejecutará vía execute_next() del módulo write_policy.
    """
    _ensure_db()

    try:
        from datetime import datetime, timezone
        current = await _wp_get_proposal(proposal_id)
        if not current:
            raise HTTPException(404, f"proposal {proposal_id} no encontrada")
        if current["approval_status"] != "pending":
            raise HTTPException(
                409,
                f"proposal {proposal_id} no está pending "
                f"(status actual: {current['approval_status']})"
            )

        update = {
            "approval_status": "approved",
            "approved_by": req.approved_by,
            "approved_at": datetime.now(timezone.utc).isoformat(),
        }
        if req.notes:
            update["result_json"] = {"approval_notes": req.notes}

        updated = await _wp_update_proposal(proposal_id, "pending", update)
        if not updated:
            raise HTTPException(
                409,
                "race condition: status cambió mientras aprobábamos"
            )

        logger.info(
            "embrion_proposal_approved",
            proposal_id=proposal_id,
            approved_by=req.approved_by,
        )
        return {
            "proposal_id": proposal_id,
            "status": "approved",
            "approved_by": req.approved_by,
            "approved_at": update["approved_at"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("embrion_approve_failed", proposal_id=proposal_id, error=str(e))
        raise HTTPException(500, f"Error aprobando proposal: {str(e)[:200]}")


@router.post("/reject/{proposal_id}")
async def rechazar_proposal(proposal_id: str, req: RejectRequest):
    """Rechazar una proposal pending con razón explícita (queda en log)."""
    _ensure_db()

    try:
        from datetime import datetime, timezone
        current = await _wp_get_proposal(proposal_id)
        if not current:
            raise HTTPException(404, f"proposal {proposal_id} no encontrada")
        if current["approval_status"] != "pending":
            raise HTTPException(
                409,
                f"proposal {proposal_id} no está pending "
                f"(status actual: {current['approval_status']})"
            )

        update = {
            "approval_status": "rejected",
            "approved_by": req.approved_by,
            "approved_at": datetime.now(timezone.utc).isoformat(),
            "rejection_reason": req.reason.strip(),
        }
        updated = await _wp_update_proposal(proposal_id, "pending", update)
        if not updated:
            raise HTTPException(409, "race condition durante reject")

        logger.info(
            "embrion_proposal_rejected",
            proposal_id=proposal_id,
            approved_by=req.approved_by,
        )
        return {
            "proposal_id": proposal_id,
            "status": "rejected",
            "reason": req.reason.strip(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("embrion_reject_failed", proposal_id=proposal_id, error=str(e))
        raise HTTPException(500, f"Error rechazando proposal: {str(e)[:200]}")


@router.get("/proposals")
async def listar_proposals(
    status: str = Query(default="pending", description="pending|approved|rejected|expired|executed|failed|all"),
    limit: int = Query(default=20, ge=1, le=200),
):
    """
    Lista proposals filtradas por status.

    - 'pending'   → solo pending no expiradas (ordenadas por created_at ASC).
    - 'all'       → todas (sin filtro de status).
    - cualquier otro → exact match.
    """
    _ensure_db()

    try:
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).isoformat()

        if status == "all":
            rows = await _db.select(
                table=WRITE_PROPOSALS_TABLE,
                columns="*",
                order_by="created_at",
                order_desc=True,
                limit=limit,
            )
        elif status == "pending":
            rows = await _db.select(
                table=WRITE_PROPOSALS_TABLE,
                columns="*",
                filters={"approval_status": "pending"},
                order_by="created_at",
                order_desc=False,
                limit=limit,
            )
            rows = [r for r in (rows or []) if (r.get("expires_at") or "") >= now_iso]
        else:
            if status not in _wp.APPROVAL_STATUSES:
                raise HTTPException(400, f"status inválido: {status}")
            rows = await _db.select(
                table=WRITE_PROPOSALS_TABLE,
                columns="*",
                filters={"approval_status": status},
                order_by="created_at",
                order_desc=True,
                limit=limit,
            )

        return {
            "status_filter": status,
            "count": len(rows or []),
            "proposals": rows or [],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("embrion_list_proposals_failed", error=str(e))
        raise HTTPException(500, f"Error listando proposals: {str(e)[:200]}")



# ════════════════════════════════════════════════════════════════════
# Tarea 4 — Telegram Webhook for HITL approval flow
# ════════════════════════════════════════════════════════════════════
# Endpoint: POST /v1/embrion/telegram/webhook
#   Receives callback_query updates from Telegram when Alfredo presses
#   the "Aprobar" or "Rechazar" button on an HITL proposal message.
#
# Security model:
#   1. X-Telegram-Bot-Api-Secret-Token header MUST match TELEGRAM_WEBHOOK_SECRET
#      env var. If env var is unset, webhook is DISABLED (returns 503).
#   2. callback_query.from.id MUST match TELEGRAM_CHAT_ID env var.
#      Only Alfredo can approve/reject. Other users get 200/denied.
#   3. callback_data MUST match strict pattern: ^(approve|reject):<uuid>$
# ════════════════════════════════════════════════════════════════════


@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """Receive Telegram callback_query for HITL approval/rejection.

    See module-level comment block for security and flow details.
    """
    import os  # noqa: PLC0415

    # 1) Verify secret token (defense against forged requests)
    expected_secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "").strip()
    if not expected_secret:
        logger.warning(
            "telegram_webhook_disabled",
            reason="TELEGRAM_WEBHOOK_SECRET unset",
        )
        raise HTTPException(503, "Telegram webhook is disabled (missing secret config)")

    received_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if received_secret != expected_secret:
        logger.warning(
            "telegram_webhook_secret_mismatch",
            received_len=len(received_secret),
        )
        raise HTTPException(401, "Invalid X-Telegram-Bot-Api-Secret-Token header")

    # 2) Parse update body
    try:
        update = await request.json()
    except Exception as e:  # noqa: BLE001
        logger.warning("telegram_webhook_bad_json", error=str(e))
        raise HTTPException(400, "Body is not valid JSON")

    if not isinstance(update, dict):
        raise HTTPException(400, "Update must be a JSON object")

    callback_query = update.get("callback_query")
    if not callback_query:
        update_type = next(
            (k for k in update if k not in ("update_id",)),
            "unknown",
        )
        logger.info(
            "telegram_webhook_ignored_update",
            update_id=update.get("update_id"),
            update_type=update_type,
        )
        return {"ok": True, "ignored": True, "type": update_type}

    callback_id = callback_query.get("id", "")
    callback_data = callback_query.get("data", "")
    from_user = callback_query.get("from", {}) or {}
    from_user_id = str(from_user.get("id", ""))
    message = callback_query.get("message", {}) or {}
    chat_id = str((message.get("chat") or {}).get("id", ""))
    message_id = message.get("message_id")

    # 3) Verify the user is Alfredo
    expected_chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if expected_chat_id and from_user_id != expected_chat_id:
        logger.warning(
            "telegram_webhook_unauthorized_user",
            from_user_id=from_user_id,
            expected_chat_id=expected_chat_id,
        )
        try:
            from kernel.runner.telegram_notifier import TelegramNotifier  # noqa: PLC0415
            await TelegramNotifier().answer_callback(
                callback_id, text="No autorizado.", show_alert=True,
            )
        except Exception:  # noqa: BLE001
            pass
        return {"ok": True, "denied": True, "reason": "unauthorized"}

    # 4) Parse callback_data
    if ":" not in callback_data:
        logger.warning("telegram_webhook_bad_callback_data", data=callback_data[:100])
        return {"ok": True, "ignored": True, "reason": "bad_callback_data"}

    action, _, proposal_id = callback_data.partition(":")
    action = action.strip().lower()
    proposal_id = proposal_id.strip()

    if action not in {"approve", "reject"}:
        logger.warning("telegram_webhook_unknown_action", action=action)
        return {"ok": True, "ignored": True, "reason": "unknown_action"}

    if len(proposal_id) < 8 or len(proposal_id) > 64:
        logger.warning("telegram_webhook_bad_proposal_id", length=len(proposal_id))
        return {"ok": True, "ignored": True, "reason": "bad_proposal_id"}

    _ensure_db()

    # 5) Apply action (reuse existing approve/reject logic from write_policy module)
    actor_id = f"telegram:{from_user_id}"
    result_summary: str
    success: bool = False

    try:
        current = await _wp_get_proposal(proposal_id)
        if not current:
            result_summary = f"Proposal `{proposal_id[:8]}` no encontrada."
        elif current["approval_status"] != "pending":
            result_summary = (
                f"Proposal `{proposal_id[:8]}` ya esta en estado "
                f"*{current['approval_status']}* — no se puede {action}."
            )
        elif action == "approve":
            update_payload = {
                "approval_status": "approved",
                "approved_by": actor_id,
                "approved_at": datetime.now(timezone.utc).isoformat(),
            }
            updated = await _wp_update_proposal(proposal_id, "pending", update_payload)
            if updated:
                success = True
                result_summary = (
                    f"Aprobada por Alfredo (via Telegram)\nID: `{proposal_id[:8]}`"
                )
                logger.info(
                    "embrion_proposal_approved_via_telegram",
                    proposal_id=proposal_id,
                    actor=actor_id,
                )
            else:
                result_summary = f"Race condition aprobando `{proposal_id[:8]}` — reintenta."
        else:
            update_payload = {
                "approval_status": "rejected",
                "approved_by": actor_id,
                "approved_at": datetime.now(timezone.utc).isoformat(),
                "rejection_reason": "Rechazada via Telegram (sin razon explicita)",
            }
            updated = await _wp_update_proposal(proposal_id, "pending", update_payload)
            if updated:
                success = True
                result_summary = (
                    f"Rechazada por Alfredo (via Telegram)\nID: `{proposal_id[:8]}`"
                )
                logger.info(
                    "embrion_proposal_rejected_via_telegram",
                    proposal_id=proposal_id,
                    actor=actor_id,
                )
            else:
                result_summary = f"Race condition rechazando `{proposal_id[:8]}` — reintenta."
    except Exception as e:  # noqa: BLE001
        logger.error(
            "telegram_webhook_action_exception",
            action=action,
            proposal_id=proposal_id,
            error=str(e),
        )
        result_summary = f"Error procesando `{proposal_id[:8]}`: {str(e)[:100]}"

    # 6) Answer callback + edit message (best-effort, non-fatal)
    try:
        from kernel.runner.telegram_notifier import TelegramNotifier  # noqa: PLC0415
        notifier = TelegramNotifier()

        if success and action == "approve":
            toast_text = "Aprobada"
        elif success and action == "reject":
            toast_text = "Rechazada"
        else:
            toast_text = "Sin efecto"
        await notifier.answer_callback(callback_id, text=toast_text, show_alert=False)

        if chat_id and message_id:
            await notifier.edit_message_text(
                chat_id=chat_id,
                message_id=int(message_id),
                text=result_summary,
                parse_mode="Markdown",
                remove_keyboard=True,
            )
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "telegram_webhook_post_action_notify_failed",
            error=str(e),
        )

    return {
        "ok": True,
        "action": action,
        "proposal_id": proposal_id,
        "success": success,
    }
