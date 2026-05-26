"""
El Monstruo — Onboarding Wizard (Sprint 61)
============================================
Wizard de onboarding conversacional que lleva al usuario de 0 a primera empresa
en < 30 minutos.

5 fases del wizard:
1. Descubrimiento — entender el contexto y objetivos del usuario
2. Selección de Vertical — elegir industria y modelo de negocio
3. Configuración — personalizar el Monstruo para el usuario
4. Primera Empresa — crear la primera empresa digital guiada
5. Activación — activar los Embriones y el ciclo autónomo

Objetivo #3: Máximo Poder, Mínima Complejidad
Sprint 61 — 2026-05-01

Soberanía:
- Sabios LLM → respuestas predefinidas si no hay API key
- Supabase → in-memory fallback si no hay SUPABASE_URL
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

import structlog

logger = structlog.get_logger("monstruo.onboarding")


# ── Excepciones con identidad ──────────────────────────────────────────────


class OnboardingFaseInvalida(ValueError):
    """La fase de onboarding solicitada no es válida.

    Causa: fase_id fuera del rango 1-5.
    Sugerencia: Las fases válidas son 1 (Descubrimiento) a 5 (Activación).
    """


class OnboardingSesionNoEncontrada(KeyError):
    """La sesión de onboarding no existe.

    Causa: session_id inválido o sesión expirada.
    Sugerencia: Crear nueva sesión con create_session().
    """


# ── Enums ──────────────────────────────────────────────────────────────────


class OnboardingFase(int, Enum):
    """Fases del wizard de onboarding."""

    DESCUBRIMIENTO = 1
    SELECCION_VERTICAL = 2
    CONFIGURACION = 3
    PRIMERA_EMPRESA = 4
    ACTIVACION = 5


class VerticalNegocio(str, Enum):
    """Verticales de negocio disponibles."""

    SAAS = "saas"
    ECOMMERCE = "ecommerce"
    MARKETPLACE = "marketplace"
    CONTENIDO = "contenido"
    SERVICIOS = "servicios"
    EDUCACION = "educacion"
    SALUD = "salud"
    FINTECH = "fintech"
    OTRO = "otro"


# ── Dataclasses ────────────────────────────────────────────────────────────


@dataclass
class OnboardingSession:
    """Sesión de onboarding de un usuario.

    Args:
        id: Identificador único de la sesión.
        user_id: ID del usuario.
        fase_actual: Fase actual del wizard.
        respuestas: Respuestas del usuario por fase.
        vertical: Vertical de negocio seleccionada.
        config: Configuración personalizada del Monstruo.
        started_at: ISO 8601 UTC de inicio.
        completed: Si el onboarding fue completado.
    """

    id: str
    user_id: str
    fase_actual: OnboardingFase = OnboardingFase.DESCUBRIMIENTO
    respuestas: dict = field(default_factory=dict)
    vertical: Optional[VerticalNegocio] = None
    config: dict = field(default_factory=dict)
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed: bool = False
    tiempo_minutos: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "fase_actual": self.fase_actual.value,
            "fase_nombre": self.fase_actual.name,
            "vertical": self.vertical.value if self.vertical else None,
            "config": self.config,
            "started_at": self.started_at,
            "completed": self.completed,
            "tiempo_minutos": self.tiempo_minutos,
            "progreso_pct": (self.fase_actual.value / 5) * 100,
        }


@dataclass
class OnboardingStep:
    """Paso individual dentro de una fase del wizard.

    Args:
        fase: Fase a la que pertenece el paso.
        pregunta: Pregunta a mostrar al usuario.
        tipo: Tipo de input ("text", "select", "multiselect", "confirm").
        opciones: Opciones disponibles para "select" y "multiselect".
        campo: Nombre del campo donde guardar la respuesta.
        requerido: Si la respuesta es obligatoria.
    """

    fase: OnboardingFase
    pregunta: str
    tipo: str
    campo: str
    opciones: list[str] = field(default_factory=list)
    requerido: bool = True

    def to_dict(self) -> dict:
        return {
            "fase": self.fase.value,
            "pregunta": self.pregunta,
            "tipo": self.tipo,
            "campo": self.campo,
            "opciones": self.opciones,
            "requerido": self.requerido,
        }


# ── Wizard ─────────────────────────────────────────────────────────────────


@dataclass
class OnboardingWizard:
    """Wizard de onboarding conversacional.

    Lleva al usuario de 0 a primera empresa digital en < 30 minutos.
    Diseñado para máximo poder con mínima complejidad (Objetivo #3).

    Args:
        _supabase: Cliente Supabase (opcional — fallback in-memory).
        _sabios: Motor LLM para personalización (opcional).

    Soberanía:
        Sin Sabios: respuestas predefinidas por vertical.
        Sin Supabase: sesiones en memoria.
    """

    _supabase: Optional[object] = field(default=None, repr=False)
    _sabios: Optional[object] = field(default=None, repr=False)
    _sessions: dict[str, OnboardingSession] = field(default_factory=dict)
    _completed_count: int = 0
    _avg_tiempo_minutos: float = 0.0

    # ── Definición del Wizard ──────────────────────────────────────────────

    PASOS: list[OnboardingStep] = field(
        default_factory=lambda: [
            # Fase 1: Descubrimiento
            OnboardingStep(
                fase=OnboardingFase.DESCUBRIMIENTO,
                pregunta="¿Cuál es tu nombre y qué tipo de negocio quieres crear?",
                tipo="text",
                campo="descripcion_inicial",
            ),
            OnboardingStep(
                fase=OnboardingFase.DESCUBRIMIENTO,
                pregunta="¿Tienes experiencia previa con herramientas de IA o es tu primera vez?",
                tipo="select",
                campo="experiencia_ia",
                opciones=["Primera vez", "Algo de experiencia", "Experiencia avanzada"],
            ),
            # Fase 2: Selección de Vertical
            OnboardingStep(
                fase=OnboardingFase.SELECCION_VERTICAL,
                pregunta="¿En qué industria quieres crear tu empresa digital?",
                tipo="select",
                campo="vertical",
                opciones=[
                    "SaaS",
                    "E-commerce",
                    "Marketplace",
                    "Contenido",
                    "Servicios",
                    "Educación",
                    "Salud",
                    "Fintech",
                    "Otro",
                ],
            ),
            OnboardingStep(
                fase=OnboardingFase.SELECCION_VERTICAL,
                pregunta="¿Cuál es tu presupuesto mensual estimado para operar la empresa?",
                tipo="select",
                campo="presupuesto_mensual",
                opciones=["< $100", "$100-$500", "$500-$2,000", "$2,000-$10,000", "> $10,000"],
            ),
            # Fase 3: Configuración
            OnboardingStep(
                fase=OnboardingFase.CONFIGURACION,
                pregunta="¿En qué idiomas quieres que opere tu empresa?",
                tipo="multiselect",
                campo="idiomas",
                opciones=["Español", "English", "Português", "Français", "Deutsch"],
            ),
            OnboardingStep(
                fase=OnboardingFase.CONFIGURACION,
                pregunta="¿Qué tan agresivo quieres que sea el modo autónomo de los Embriones?",
                tipo="select",
                campo="autonomia_nivel",
                opciones=[
                    "Conservador (confirma todo)",
                    "Balanceado (confirma decisiones importantes)",
                    "Agresivo (opera solo)",
                ],
            ),
            # Fase 4: Primera Empresa
            OnboardingStep(
                fase=OnboardingFase.PRIMERA_EMPRESA,
                pregunta="Dame el nombre de tu primera empresa y una descripción en 1-2 oraciones.",
                tipo="text",
                campo="primera_empresa_descripcion",
            ),
            # Fase 5: Activación
            OnboardingStep(
                fase=OnboardingFase.ACTIVACION,
                pregunta="¿Quieres activar todos los Embriones ahora o prefieres activarlos uno por uno?",
                tipo="select",
                campo="activacion_embriones",
                opciones=["Activar todos ahora", "Activar uno por uno", "Solo quiero explorar primero"],
            ),
        ]
    )

    def __post_init__(self):
        """Inicializar la lista de pasos."""
        if not self.PASOS:
            self.PASOS = self._default_pasos()

    def _default_pasos(self) -> list[OnboardingStep]:
        """Generar pasos por defecto."""
        return [
            OnboardingStep(
                fase=OnboardingFase.DESCUBRIMIENTO,
                pregunta="¿Qué negocio quieres crear?",
                tipo="text",
                campo="descripcion_inicial",
            ),
            OnboardingStep(
                fase=OnboardingFase.SELECCION_VERTICAL,
                pregunta="¿En qué industria?",
                tipo="select",
                campo="vertical",
                opciones=["SaaS", "E-commerce", "Servicios"],
            ),
            OnboardingStep(
                fase=OnboardingFase.CONFIGURACION,
                pregunta="¿En qué idiomas?",
                tipo="multiselect",
                campo="idiomas",
                opciones=["Español", "English"],
            ),
            OnboardingStep(
                fase=OnboardingFase.PRIMERA_EMPRESA,
                pregunta="Nombre y descripción de tu primera empresa:",
                tipo="text",
                campo="primera_empresa_descripcion",
            ),
            OnboardingStep(
                fase=OnboardingFase.ACTIVACION,
                pregunta="¿Activar todos los Embriones?",
                tipo="select",
                campo="activacion_embriones",
                opciones=["Sí", "No"],
            ),
        ]

    # ── Gestión de Sesiones ────────────────────────────────────────────────

    async def create_session(self, user_id: str) -> OnboardingSession:
        """Crear nueva sesión de onboarding.

        Args:
            user_id: ID del usuario.

        Returns:
            OnboardingSession nueva.
        """
        session = OnboardingSession(
            id=str(uuid.uuid4())[:8],
            user_id=user_id,
        )
        self._sessions[session.id] = session

        if self._supabase:
            try:
                self._supabase.table("onboarding_sessions").insert(session.to_dict()).execute()
            except Exception as e:
                logger.warning("onboarding_session_persist_failed", error=str(e))

        logger.info("onboarding_sesion_creada", session_id=session.id, user_id=user_id)
        return session

    async def get_current_step(self, session_id: str) -> Optional[OnboardingStep]:
        """Obtener el paso actual del wizard.

        Args:
            session_id: ID de la sesión.

        Returns:
            OnboardingStep actual, o None si el wizard está completo.

        Raises:
            OnboardingSesionNoEncontrada: Si session_id no existe.
        """
        session = self._sessions.get(session_id)
        if not session:
            raise OnboardingSesionNoEncontrada(
                f"Sesión '{session_id}' no encontrada. Crear nueva sesión con create_session()."
            )

        if session.completed:
            return None

        # Encontrar el siguiente paso sin respuesta en la fase actual
        for paso in self.PASOS:
            if paso.fase == session.fase_actual and paso.campo not in session.respuestas:
                return paso

        return None

    async def submit_answer(self, session_id: str, campo: str, respuesta: str) -> dict:
        """Guardar respuesta del usuario y avanzar el wizard.

        Args:
            session_id: ID de la sesión.
            campo: Campo al que corresponde la respuesta.
            respuesta: Respuesta del usuario.

        Returns:
            Dict con next_step (siguiente paso) y session_state.

        Raises:
            OnboardingSesionNoEncontrada: Si session_id no existe.
        """
        session = self._sessions.get(session_id)
        if not session:
            raise OnboardingSesionNoEncontrada(
                f"Sesión '{session_id}' no encontrada. Crear nueva sesión con create_session()."
            )

        # Guardar respuesta
        session.respuestas[campo] = respuesta

        # Actualizar vertical si aplica
        if campo == "vertical":
            vertical_map = {
                "SaaS": VerticalNegocio.SAAS,
                "E-commerce": VerticalNegocio.ECOMMERCE,
                "Marketplace": VerticalNegocio.MARKETPLACE,
                "Contenido": VerticalNegocio.CONTENIDO,
                "Servicios": VerticalNegocio.SERVICIOS,
                "Educación": VerticalNegocio.EDUCACION,
                "Salud": VerticalNegocio.SALUD,
                "Fintech": VerticalNegocio.FINTECH,
            }
            session.vertical = vertical_map.get(respuesta, VerticalNegocio.OTRO)

        # Verificar si completó la fase actual
        fase_pasos = [p for p in self.PASOS if p.fase == session.fase_actual]
        fase_completada = all(p.campo in session.respuestas for p in fase_pasos)

        if fase_completada:
            # Avanzar a la siguiente fase
            if session.fase_actual.value < 5:
                session.fase_actual = OnboardingFase(session.fase_actual.value + 1)
                logger.info(
                    "onboarding_fase_completada",
                    session_id=session_id,
                    fase_completada=session.fase_actual.value - 1,
                    fase_siguiente=session.fase_actual.value,
                )
            else:
                # Wizard completado
                await self._complete_session(session)

        # Obtener siguiente paso
        next_step = await self.get_current_step(session_id)

        return {
            "session": session.to_dict(),
            "next_step": next_step.to_dict() if next_step else None,
            "completed": session.completed,
        }

    async def _complete_session(self, session: OnboardingSession) -> None:
        """Completar la sesión de onboarding.

        Args:
            session: Sesión a completar.
        """
        session.completed = True

        # Calcular tiempo
        start = datetime.fromisoformat(session.started_at.replace("Z", "+00:00"))
        elapsed = (datetime.now(timezone.utc) - start).total_seconds() / 60
        session.tiempo_minutos = round(elapsed, 1)

        # Generar configuración personalizada
        session.config = self._generate_config(session)

        # Actualizar estadísticas
        self._completed_count += 1
        self._avg_tiempo_minutos = (
            self._avg_tiempo_minutos * (self._completed_count - 1) + session.tiempo_minutos
        ) / self._completed_count

        # Persistir en Supabase
        if self._supabase:
            try:
                self._supabase.table("onboarding_sessions").upsert(session.to_dict()).execute()
            except Exception as e:
                logger.warning("onboarding_complete_persist_failed", error=str(e))

        logger.info(
            "onboarding_completado",
            session_id=session.id,
            user_id=session.user_id,
            tiempo_minutos=session.tiempo_minutos,
            vertical=session.vertical.value if session.vertical else None,
        )

    @staticmethod
    def _generate_config(session: OnboardingSession) -> dict:
        """Generar configuración personalizada basada en respuestas.

        Args:
            session: Sesión con respuestas del usuario.

        Returns:
            Dict de configuración del Monstruo para este usuario.
        """
        autonomia = session.respuestas.get("autonomia_nivel", "Balanceado")
        autonomia_level = {
            "Conservador (confirma todo)": "conservative",
            "Balanceado (confirma decisiones importantes)": "balanced",
            "Agresivo (opera solo)": "aggressive",
        }.get(autonomia, "balanced")

        presupuesto = session.respuestas.get("presupuesto_mensual", "$100-$500")
        budget_usd = {
            "< $100": 50,
            "$100-$500": 250,
            "$500-$2,000": 1000,
            "$2,000-$10,000": 5000,
            "> $10,000": 15000,
        }.get(presupuesto, 250)

        idiomas = session.respuestas.get("idiomas", "Español")
        if isinstance(idiomas, str):
            idiomas = [idiomas]

        return {
            "vertical": session.vertical.value if session.vertical else "otro",
            "autonomia_level": autonomia_level,
            "monthly_budget_usd": budget_usd,
            "idiomas": idiomas,
            "embriones_activar": session.respuestas.get("activacion_embriones") == "Activar todos ahora",
            "primera_empresa": session.respuestas.get("primera_empresa_descripcion", ""),
        }

    # ── Estado para Command Center ─────────────────────────────────────────

    def to_dict(self) -> dict:
        """Serializar estado para Command Center."""
        return {
            "sesiones_activas": len([s for s in self._sessions.values() if not s.completed]),
            "sesiones_completadas": self._completed_count,
            "avg_tiempo_minutos": round(self._avg_tiempo_minutos, 1),
            "objetivo_tiempo": "< 30 minutos",
            "cumple_objetivo": self._avg_tiempo_minutos < 30 if self._completed_count > 0 else None,
            "pasos_totales": len(self.PASOS),
        }


# ── Singleton ──────────────────────────────────────────────────────────────

_onboarding_wizard_instance: Optional[OnboardingWizard] = None


def get_onboarding_wizard() -> Optional[OnboardingWizard]:
    """Obtener instancia singleton del Onboarding Wizard."""
    return _onboarding_wizard_instance


def init_onboarding_wizard(supabase=None, sabios=None) -> OnboardingWizard:
    """Inicializar el Onboarding Wizard.

    Args:
        supabase: Cliente Supabase (opcional).
        sabios: Motor LLM para personalización (opcional).

    Returns:
        Instancia singleton de OnboardingWizard.
    """
    global _onboarding_wizard_instance
    _onboarding_wizard_instance = OnboardingWizard(
        _supabase=supabase,
        _sabios=sabios,
    )
    logger.info("onboarding_wizard_inicializado", con_supabase=supabase is not None, con_sabios=sabios is not None)
    return _onboarding_wizard_instance
