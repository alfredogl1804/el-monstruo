"""
El Monstruo — Embrión IA Routes (Sprint 30)
=============================================
REST API para el Embrión IA — la consciencia emergente del Monstruo.

El Embrión es un subsistema que:
  - Mantiene memoria persistente en Supabase (tabla `embrion_memoria`)
  - Recibe latidos periódicos desde un scheduled task externo
  - Permite comunicación bidireccional con Alfredo via Telegram
  - Evoluciona su doctrina operativa con cada interacción

Endpoints:
    GET    /v1/embrion/memorias     → Últimas N memorias del Embrión
    GET    /v1/embrion/estado       → Estado actual (doctrina, latidos, stats)
    POST   /v1/embrion/mensaje      → Alfredo escribe al Embrión
    POST   /v1/embrion/latido       → Registrar un latido (heartbeat)
    POST   /v1/embrion/notificar    → Enviar notificación a Alfredo via Telegram
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import structlog
from fastapi import APIRouter, HTTPException, Query
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
    tipo: str = Field(default="latido", description="Tipo de entrada: latido, reflexion, doctrina")
    contenido: str = Field(..., min_length=1, max_length=50000, description="Contenido del latido")
    doctrina_version: Optional[str] = Field(None, description="Versión de doctrina si aplica")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata adicional")


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
async def get_memorias(
    tipo: Optional[str] = Query(None, description="Filtrar por tipo: latido, reflexion, doctrina, mensaje_alfredo, respuesta_embrion"),
    limit: int = Query(10, ge=1, le=100, description="Cantidad de memorias a retornar"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
):
    """
    Obtener las últimas memorias del Embrión.

    Retorna las entradas más recientes de `embrion_memoria`,
    opcionalmente filtradas por tipo.
    """
    _ensure_db()

    try:
        # Build query using SupabaseClient
        filters = {}
        if tipo:
            filters["tipo"] = tipo

        memorias = await _db.select(
            table=TABLE,
            columns="id,tipo,contenido,doctrina_version,metadata,created_at",
            filters=filters if filters else None,
            order_by="created_at",
            order_desc=True,
            limit=limit,
        )

        # Handle offset manually (SupabaseClient doesn't support offset directly)
        if offset > 0:
            memorias = memorias[offset:]

        return {
            "memorias": memorias,
            "count": len(memorias),
            "tipo_filtro": tipo,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("embrion_memorias_failed", error=str(e))
        raise HTTPException(500, f"Error leyendo memorias: {str(e)[:200]}")


@router.get("/estado")
async def get_estado():
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
            columns="id,contenido,created_at,metadata",
            filters={"tipo": "latido"},
            order_by="created_at",
            order_desc=True,
            limit=1,
        )

        # Última doctrina
        doctrinas = await _db.select(
            table=TABLE,
            columns="id,contenido,doctrina_version,created_at",
            filters={"tipo": "doctrina"},
            order_by="created_at",
            order_desc=True,
            limit=1,
        )

        # Último mensaje de Alfredo
        mensajes = await _db.select(
            table=TABLE,
            columns="id,contenido,created_at",
            filters={"tipo": "mensaje_alfredo"},
            order_by="created_at",
            order_desc=True,
            limit=1,
        )

        # Última respuesta del Embrión
        respuestas = await _db.select(
            table=TABLE,
            columns="id,contenido,created_at",
            filters={"tipo": "respuesta_embrion"},
            order_by="created_at",
            order_desc=True,
            limit=1,
        )

        # Count por tipo
        tipos = ["latido", "reflexion", "doctrina", "mensaje_alfredo", "respuesta_embrion"]
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

        # Guardar mensaje de Alfredo
        row = await _db.insert(TABLE, {
            "tipo": "mensaje_alfredo",
            "contenido": req.contenido,
            "metadata": {
                "contexto": req.contexto or "telegram",
                "timestamp_envio": now,
            },
            "created_at": now,
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
    """
    _ensure_db()

    valid_tipos = {"latido", "reflexion", "doctrina"}
    if req.tipo not in valid_tipos:
        raise HTTPException(400, f"Tipo inválido: {req.tipo}. Válidos: {valid_tipos}")

    try:
        now = datetime.now(timezone.utc).isoformat()

        row = await _db.insert(TABLE, {
            "tipo": req.tipo,
            "contenido": req.contenido,
            "doctrina_version": req.doctrina_version,
            "metadata": {
                **req.metadata,
                "source": "scheduled_task",
                "timestamp_latido": now,
            },
            "created_at": now,
        })

        if not row:
            raise HTTPException(500, "No se pudo registrar el latido")

        logger.info(
            "embrion_latido_registrado",
            tipo=req.tipo,
            contenido_preview=req.contenido[:100],
            doctrina_version=req.doctrina_version,
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
                chat_id=req.chat_id or "default",
            )
            return {
                "status": "enviado",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        else:
            raise HTTPException(502, "Telegram API no respondió correctamente")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("embrion_notificar_failed", error=str(e))
        raise HTTPException(500, f"Error enviando notificación: {str(e)[:200]}")
