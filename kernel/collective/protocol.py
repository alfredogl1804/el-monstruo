"""
El Monstruo — Collective Intelligence Protocol (Sprint 61)
===========================================================
Protocolo de comunicación e inteligencia colectiva entre Embriones.

3 niveles de coordinación:
1. Mensajería — pub/sub inter-embrión con tópicos
2. Debate — sesiones estructuradas con síntesis LLM
3. Votación — decisiones colectivas con mayoría calificada

Objetivo #8: Inteligencia Emergente Colectiva
Sprint 61 — 2026-05-01

Soberanía:
- Supabase Realtime → in-memory fallback si no hay SUPABASE_URL
- Sabios (LLM) → síntesis heurística si no hay API key
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

import structlog

logger = structlog.get_logger("monstruo.collective")


# ── Excepciones con identidad ──────────────────────────────────────────────


class ColectivaMensajeInvalido(ValueError):
    """El mensaje enviado al protocolo colectivo tiene campos inválidos.

    Causa: sender, type o topic vacíos.
    Sugerencia: Verificar que el Embrión emisor tiene nombre registrado.
    """


class ColectivaDebateNoEncontrado(KeyError):
    """El debate solicitado no existe o ya fue cerrado.

    Causa: debate_id inválido o debate expirado.
    Sugerencia: Verificar el ID con get_active_debates().
    """


class ColectivaVotacionCerrada(RuntimeError):
    """Intento de votar en una sesión ya cerrada.

    Causa: La votación ya fue tallied.
    Sugerencia: Abrir una nueva votación con call_vote().
    """


# ── Enums ──────────────────────────────────────────────────────────────────


class MessageType(str, Enum):
    """Tipos de mensajes inter-embrión."""

    INSIGHT = "insight"  # Compartir descubrimiento
    REQUEST = "request"  # Solicitar acción a otro embrión
    RESPONSE = "response"  # Respuesta a un request
    ALERT = "alert"  # Alerta crítica
    DEBATE_OPEN = "debate_open"  # Invitación a debate
    DEBATE_ARG = "debate_arg"  # Argumento en debate
    VOTE_CALL = "vote_call"  # Convocatoria a votación
    VOTE_CAST = "vote_cast"  # Voto emitido


class DecisionMethod(str, Enum):
    """Métodos de decisión colectiva."""

    MAJORITY_VOTE = "majority_vote"  # >50%
    QUALIFIED_MAJORITY = "qualified_majority"  # >60%
    CONSENSUS = "consensus"  # 100%


# ── Dataclasses ────────────────────────────────────────────────────────────


@dataclass
class EmbrionMessage:
    """Mensaje inter-embrión.

    Args:
        id: Identificador único del mensaje.
        sender: Nombre del embrión emisor.
        type: Tipo de mensaje (MessageType).
        topic: Canal/tópico del mensaje.
        content: Payload del mensaje (dict serializable).
        recipients: Lista de embriones destinatarios (vacío = broadcast).
        requires_response: Si el emisor espera respuesta.
        timestamp: ISO 8601 UTC.
    """

    id: str
    sender: str
    type: MessageType
    topic: str
    content: dict
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    recipients: list[str] = field(default_factory=list)
    requires_response: bool = False

    def to_dict(self) -> dict:
        """Serializar para Supabase o Command Center."""
        return {
            "id": self.id,
            "sender": self.sender,
            "type": self.type.value,
            "topic": self.topic,
            "content": self.content,
            "recipients": self.recipients,
            "requires_response": self.requires_response,
            "timestamp": self.timestamp,
        }


@dataclass
class DebateSession:
    """Sesión de debate entre embriones.

    Args:
        id: Identificador único del debate.
        topic: Tema del debate.
        context: Contexto adicional para los participantes.
        participants: Lista de embriones participantes.
        rounds: Número de rondas de argumentación.
    """

    id: str
    topic: str
    context: str
    participants: list[str]
    rounds: int = 2
    arguments: list[dict] = field(default_factory=list)
    current_round: int = 0
    synthesis: Optional[str] = None
    status: str = "open"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "topic": self.topic,
            "participants": self.participants,
            "rounds": self.rounds,
            "arguments_count": len(self.arguments),
            "current_round": self.current_round,
            "synthesis": self.synthesis,
            "status": self.status,
        }


@dataclass
class VoteSession:
    """Sesión de votación colectiva.

    Args:
        id: Identificador único de la votación.
        topic: Tema de la votación.
        question: Pregunta a responder.
        options: Opciones disponibles.
        method: Método de decisión (DecisionMethod).
        initiator: Embrión que convocó la votación.
    """

    id: str
    topic: str
    question: str
    options: list[str]
    method: DecisionMethod
    initiator: str
    votes: dict = field(default_factory=dict)
    result: Optional[dict] = None
    status: str = "open"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "topic": self.topic,
            "question": self.question,
            "options": self.options,
            "method": self.method.value,
            "initiator": self.initiator,
            "votes_count": len(self.votes),
            "result": self.result,
            "status": self.status,
        }


# ── Motor principal ────────────────────────────────────────────────────────


@dataclass
class ColectivaProtocol:
    """Motor de inteligencia colectiva entre Embriones.

    Orquesta 3 niveles de coordinación:
    1. Mensajería pub/sub con persistencia Supabase
    2. Debates estructurados con síntesis LLM
    3. Votaciones con múltiples métodos de decisión

    Args:
        _supabase: Cliente Supabase (opcional — fallback in-memory).
        _sabios: Motor LLM para síntesis de debates (opcional).

    Soberanía:
        Sin Supabase: mensajes en memoria (se pierden al reiniciar).
        Sin Sabios: síntesis heurística basada en argumentos.
    """

    _supabase: Optional[object] = field(default=None, repr=False)
    _sabios: Optional[object] = field(default=None, repr=False)
    _embriones: dict = field(default_factory=dict)
    _active_debates: dict[str, DebateSession] = field(default_factory=dict)
    _active_votes: dict[str, VoteSession] = field(default_factory=dict)
    _message_buffer: list[EmbrionMessage] = field(default_factory=list)

    # ── Registro de Embriones ──────────────────────────────────────────────

    def register_embrion(self, name: str, capabilities: list[str]) -> None:
        """Registrar un embrión en el protocolo colectivo.

        Args:
            name: Nombre único del embrión (ej: "ventas", "tecnico").
            capabilities: Lista de capacidades del embrión.
        """
        self._embriones[name] = {
            "name": name,
            "capabilities": capabilities,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "messages_sent": 0,
            "messages_received": 0,
        }
        logger.info("embrion_registrado", name=name, capabilities=capabilities)

    # ── Nivel 1: Mensajería ────────────────────────────────────────────────

    async def publish(self, message: EmbrionMessage) -> None:
        """Publicar mensaje en el bus colectivo.

        Args:
            message: Mensaje a publicar.

        Raises:
            ColectivaMensajeInvalido: Si sender, type o topic están vacíos.
        """
        if not message.sender or not message.topic:
            raise ColectivaMensajeInvalido(
                f"Mensaje inválido: sender='{message.sender}' topic='{message.topic}'. "
                "Verificar que el Embrión emisor tiene nombre registrado."
            )

        # Actualizar contador del emisor
        if message.sender in self._embriones:
            self._embriones[message.sender]["messages_sent"] += 1

        # Persistir en Supabase
        if self._supabase:
            try:
                self._supabase.table("embrion_messages").insert(message.to_dict()).execute()
            except Exception as e:
                logger.warning("supabase_publish_failed", error=str(e))
                self._message_buffer.append(message)
        else:
            self._message_buffer.append(message)

        logger.info(
            "mensaje_publicado", id=message.id, sender=message.sender, topic=message.topic, type=message.type.value
        )

    async def receive(self, embrion_name: str, topic: str = None, since_hours: int = 24) -> list[EmbrionMessage]:
        """Recibir mensajes para un embrión.

        Args:
            embrion_name: Nombre del embrión receptor.
            topic: Filtrar por tópico (opcional).
            since_hours: Ventana temporal en horas.

        Returns:
            Lista de mensajes dirigidos al embrión.
        """
        # Actualizar contador del receptor
        if embrion_name in self._embriones:
            self._embriones[embrion_name]["messages_received"] += 1

        if not self._supabase:
            # Fallback: filtrar buffer en memoria
            msgs = [
                m
                for m in self._message_buffer
                if (not m.recipients or embrion_name in m.recipients) and (not topic or m.topic == topic)
            ]
            return msgs[-50:]  # Últimos 50

        try:
            from datetime import timedelta

            since = (datetime.now(timezone.utc) - timedelta(hours=since_hours)).isoformat()

            query = (
                self._supabase.table("embrion_messages")
                .select("*")
                .gte("created_at", since)
                .order("created_at", desc=True)
                .limit(50)
            )

            if topic:
                query = query.eq("topic", topic)

            result = query.execute()

            messages = []
            for row in result.data:
                recipients = row.get("recipients") or []
                if not recipients or embrion_name in recipients:
                    messages.append(
                        EmbrionMessage(
                            id=row["id"],
                            sender=row["sender"],
                            type=MessageType(row["type"]),
                            topic=row["topic"],
                            content=json.loads(row["content"]) if isinstance(row["content"], str) else row["content"],
                            timestamp=row["created_at"],
                            recipients=recipients,
                            requires_response=row.get("requires_response", False),
                        )
                    )
            return messages

        except Exception as e:
            logger.warning("supabase_receive_failed", error=str(e))
            return []

    # ── Nivel 2: Debate ────────────────────────────────────────────────────

    async def open_debate(self, topic: str, context: str, participants: list[str], rounds: int = 2) -> DebateSession:
        """Abrir una sesión de debate entre embriones.

        Args:
            topic: Tema del debate.
            context: Contexto adicional para los participantes.
            participants: Lista de nombres de embriones participantes.
            rounds: Número de rondas de argumentación (default: 2).

        Returns:
            DebateSession con ID único.
        """
        session = DebateSession(
            id=str(uuid.uuid4())[:8],
            topic=topic,
            context=context,
            participants=participants,
            rounds=rounds,
        )
        self._active_debates[session.id] = session

        # Notificar participantes
        await self.publish(
            EmbrionMessage(
                id=f"debate-open-{session.id}",
                sender="collective",
                type=MessageType.DEBATE_OPEN,
                topic="debates",
                content={"debate_id": session.id, "topic": topic, "context": context},
                recipients=participants,
                requires_response=True,
            )
        )

        logger.info("debate_abierto", id=session.id, topic=topic, participants=participants, rounds=rounds)
        return session

    async def submit_argument(
        self, debate_id: str, embrion: str, position: str, reasoning: str, evidence: list[str] = None
    ) -> None:
        """Embrión submite argumento en un debate.

        Args:
            debate_id: ID del debate activo.
            embrion: Nombre del embrión argumentando.
            position: Posición del embrión (favor/contra/neutral + texto).
            reasoning: Razonamiento detrás de la posición.
            evidence: Lista de evidencias de soporte (opcional).

        Raises:
            ColectivaDebateNoEncontrado: Si el debate no existe o está cerrado.
        """
        session = self._active_debates.get(debate_id)
        if not session or session.status != "open":
            raise ColectivaDebateNoEncontrado(
                f"Debate '{debate_id}' no encontrado o ya cerrado. Verificar el ID con get_active_debates()."
            )

        session.arguments.append(
            {
                "embrion": embrion,
                "position": position,
                "reasoning": reasoning,
                "evidence": evidence or [],
                "round": session.current_round,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        # Verificar si todos los participantes argumentaron esta ronda
        round_args = [a for a in session.arguments if a["round"] == session.current_round]
        if len(round_args) >= len(session.participants):
            session.current_round += 1
            if session.current_round >= session.rounds:
                await self._close_debate(session)

    async def _close_debate(self, session: DebateSession) -> None:
        """Cerrar debate y generar síntesis.

        Args:
            session: Sesión de debate a cerrar.
        """
        session.status = "closed"

        if self._sabios:
            args_text = "\n".join(
                [
                    f"[{a['embrion']}] Posición: {a['position']}\nRazonamiento: {a['reasoning']}"
                    for a in session.arguments
                ]
            )

            prompt = f"""Eres el moderador de un debate entre agentes de IA especializados.
Tema: {session.topic}
Contexto: {session.context}

Argumentos presentados:
{args_text}

Sintetiza el debate en una recomendación final que:
1. Reconozca los puntos más fuertes de cada perspectiva
2. Identifique áreas de acuerdo
3. Resuelva conflictos con razonamiento claro
4. Proporcione una recomendación accionable final

Responde en JSON: {{"synthesis": "...", "key_agreements": [...], "resolved_conflicts": [...], "recommendation": "..."}}"""

            try:
                response = await self._sabios.ask(prompt)
                session.synthesis = response
            except Exception as e:
                logger.warning("debate_synthesis_failed", error=str(e))
                # Síntesis heurística fallback
                session.synthesis = json.dumps(
                    {
                        "synthesis": f"Debate sobre '{session.topic}' con {len(session.arguments)} argumentos.",
                        "key_agreements": [],
                        "resolved_conflicts": [],
                        "recommendation": "Revisar argumentos manualmente.",
                    }
                )
        else:
            # Síntesis heurística sin LLM
            session.synthesis = json.dumps(
                {
                    "synthesis": f"Debate sobre '{session.topic}' completado con {len(session.participants)} participantes.",
                    "arguments_count": len(session.arguments),
                    "recommendation": "Análisis LLM no disponible — revisar argumentos manualmente.",
                }
            )

        # Persistir en Supabase
        if self._supabase:
            try:
                self._supabase.table("debate_sessions").insert(
                    {
                        "id": session.id,
                        "topic": session.topic,
                        "context": session.context,
                        "participants": session.participants,
                        "arguments": session.arguments,
                        "rounds": session.rounds,
                        "synthesis": session.synthesis,
                        "status": session.status,
                    }
                ).execute()
            except Exception as e:
                logger.warning("debate_persist_failed", error=str(e))

        logger.info("debate_cerrado", id=session.id, arguments=len(session.arguments))

    # ── Nivel 3: Votación ──────────────────────────────────────────────────

    async def call_vote(
        self,
        topic: str,
        question: str,
        options: list[str],
        initiator: str,
        method: DecisionMethod = DecisionMethod.QUALIFIED_MAJORITY,
        voters: list[str] = None,
    ) -> VoteSession:
        """Convocar una votación colectiva.

        Args:
            topic: Tema de la votación.
            question: Pregunta específica a responder.
            options: Lista de opciones disponibles.
            initiator: Embrión que convoca la votación.
            method: Método de decisión (default: QUALIFIED_MAJORITY 60%).
            voters: Lista de embriones votantes (None = todos registrados).

        Returns:
            VoteSession con ID único.
        """
        session = VoteSession(
            id=str(uuid.uuid4())[:8],
            topic=topic,
            question=question,
            options=options,
            method=method,
            initiator=initiator,
        )
        self._active_votes[session.id] = session

        # Notificar votantes
        await self.publish(
            EmbrionMessage(
                id=f"vote-call-{session.id}",
                sender=initiator,
                type=MessageType.VOTE_CALL,
                topic="votes",
                content={"vote_id": session.id, "question": question, "options": options},
                recipients=voters or list(self._embriones.keys()),
                requires_response=True,
            )
        )

        logger.info("votacion_convocada", id=session.id, question=question, method=method.value, options=options)
        return session

    async def cast_vote(self, vote_id: str, embrion: str, option: str, reasoning: str, weight: float = 1.0) -> None:
        """Embrión emite su voto.

        Args:
            vote_id: ID de la votación activa.
            embrion: Nombre del embrión votante.
            option: Opción elegida (debe estar en session.options).
            reasoning: Razonamiento del voto.
            weight: Peso del voto (default: 1.0).

        Raises:
            ColectivaVotacionCerrada: Si la votación ya fue cerrada.
        """
        session = self._active_votes.get(vote_id)
        if not session or session.status != "open":
            raise ColectivaVotacionCerrada(
                f"Votación '{vote_id}' no encontrada o ya cerrada. Abrir una nueva votación con call_vote()."
            )

        session.votes[embrion] = {
            "option": option,
            "weight": weight,
            "reasoning": reasoning,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Verificar si todos los votantes esperados han votado
        expected_voters = len(self._embriones)
        if len(session.votes) >= expected_voters:
            await self._tally_votes(session)

    async def _tally_votes(self, session: VoteSession) -> None:
        """Contar votos y determinar resultado.

        Args:
            session: Sesión de votación a cerrar.
        """
        session.status = "closed"

        # Contar votos ponderados
        option_scores: dict[str, float] = {}
        for vote in session.votes.values():
            option = vote["option"]
            weight = vote["weight"]
            option_scores[option] = option_scores.get(option, 0) + weight

        total_weight = sum(v["weight"] for v in session.votes.values())

        # Determinar ganador según método
        if not option_scores:
            session.result = {"winner": None, "passed": False, "error": "Sin votos"}
            return

        winner = max(option_scores, key=option_scores.get)
        winner_pct = option_scores[winner] / total_weight if total_weight > 0 else 0

        threshold = {
            DecisionMethod.MAJORITY_VOTE: 0.5,
            DecisionMethod.QUALIFIED_MAJORITY: 0.6,
            DecisionMethod.CONSENSUS: 1.0,
        }.get(session.method, 0.5)

        passed = winner_pct >= threshold

        session.result = {
            "winner": winner,
            "percentage": round(winner_pct * 100, 1),
            "passed": passed,
            "threshold": threshold * 100,
            "breakdown": option_scores,
            "voter_count": len(session.votes),
        }

        # Persistir en Supabase
        if self._supabase:
            try:
                self._supabase.table("vote_sessions").insert(
                    {
                        "id": session.id,
                        "topic": session.topic,
                        "question": session.question,
                        "options": session.options,
                        "method": session.method.value,
                        "initiator": session.initiator,
                        "votes": session.votes,
                        "result": session.result,
                        "status": session.status,
                    }
                ).execute()
            except Exception as e:
                logger.warning("vote_persist_failed", error=str(e))

        logger.info("votacion_tallied", id=session.id, winner=winner, pct=session.result["percentage"], passed=passed)

    # ── Detección de Emergencia ────────────────────────────────────────────

    async def detect_emergence(self) -> list[dict]:
        """Detectar patrones de comportamiento emergente.

        Returns:
            Lista de patrones emergentes detectados con tipo, evidencia y significancia.
        """
        emergent_patterns = []

        if not self._supabase:
            # Detectar desde buffer en memoria
            if len(self._message_buffer) > 5:
                spontaneous = [m for m in self._message_buffer if m.type == MessageType.INSIGHT]
                if len(spontaneous) > 3:
                    emergent_patterns.append(
                        {
                            "type": "spontaneous_collaboration",
                            "evidence": f"{len(spontaneous)} insights espontáneos en buffer",
                            "significance": "Embriones comparten insights sin ser invocados",
                        }
                    )
            return emergent_patterns

        try:
            from datetime import timedelta

            since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()

            result = (
                self._supabase.table("embrion_messages")
                .select("id", count="exact")
                .eq("type", "insight")
                .gte("created_at", since)
                .execute()
            )

            spontaneous_count = result.count or 0
            if spontaneous_count > 5:
                emergent_patterns.append(
                    {
                        "type": "spontaneous_collaboration",
                        "evidence": f"{spontaneous_count} mensajes espontáneos en 24h",
                        "significance": "Embriones inician comunicación sin trigger externo",
                    }
                )
        except Exception as e:
            logger.warning("emergence_detection_failed", error=str(e))

        return emergent_patterns

    # ── Estado para Command Center ─────────────────────────────────────────

    def to_dict(self) -> dict:
        """Serializar estado para el Command Center.

        Returns:
            Dict con embriones registrados, debates y votaciones activas.
        """
        return {
            "embriones_registrados": len(self._embriones),
            "embriones": list(self._embriones.keys()),
            "debates_activos": len([d for d in self._active_debates.values() if d.status == "open"]),
            "votaciones_activas": len([v for v in self._active_votes.values() if v.status == "open"]),
            "mensajes_en_buffer": len(self._message_buffer),
            "debates": [d.to_dict() for d in list(self._active_debates.values())[-5:]],
            "votaciones": [v.to_dict() for v in list(self._active_votes.values())[-5:]],
        }

    def get_active_debates(self) -> list[DebateSession]:
        """Obtener debates activos."""
        return [d for d in self._active_debates.values() if d.status == "open"]

    def get_active_votes(self) -> list[VoteSession]:
        """Obtener votaciones activas."""
        return [v for v in self._active_votes.values() if v.status == "open"]


# ── Singleton ──────────────────────────────────────────────────────────────

_colectiva_instance: Optional[ColectivaProtocol] = None


def get_colectiva_protocol() -> Optional[ColectivaProtocol]:
    """Obtener instancia singleton del protocolo colectivo."""
    return _colectiva_instance


def init_colectiva_protocol(supabase=None, sabios=None) -> ColectivaProtocol:
    """Inicializar el protocolo colectivo.

    Args:
        supabase: Cliente Supabase (opcional).
        sabios: Motor LLM para síntesis (opcional).

    Returns:
        Instancia singleton de ColectivaProtocol.
    """
    global _colectiva_instance
    _colectiva_instance = ColectivaProtocol(
        _supabase=supabase,
        _sabios=sabios,
    )
    logger.info("colectiva_protocol_inicializado", con_supabase=supabase is not None, con_sabios=sabios is not None)
    return _colectiva_instance
