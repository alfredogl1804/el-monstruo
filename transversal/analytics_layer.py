"""
analytics_layer.py — Capa de Analytics Transversal
====================================================
Capa Transversal #5 del Objetivo #9 (Transversalidad Universal).

PROPÓSITO: Genera configuraciones de analytics y tracking para los proyectos
que El Monstruo crea. Cada proyecto nace con observabilidad de negocio desde
el primer día — sin configuración manual.

Componentes:
  1. Taxonomía de eventos estandarizada (EventTaxonomy)
  2. Analizador de retención de usuarios (RetentionAnalyzer)
  3. Scorer de engagement (EngagementScorer)
  4. Configuración de PostHog por tipo de proyecto
  5. Funnel analysis templates

Soberanía:
  - Analytics: PostHog → alternativa: Mixpanel, Amplitude, o implementación propia
  - Retention: cálculo en Python puro → sin dependencia externa
  - Funnels: PostHog Funnels API → alternativa: SQL analytics en Supabase

Sprint 58 — "La Fortaleza Completa"
Obj #9 — Capa 5: Analytics
"""
import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum

logger = structlog.get_logger("transversal.analytics_layer")


# ─── Errores con identidad (Brand Check #2) ──────────────────────────────────

class AnalyticsLayerError(Exception):
    """Error base de la Capa de Analytics Transversal."""
    pass


class ANALYTICS_LAYER_EVENTO_INVALIDO(AnalyticsLayerError):
    """El nombre del evento no sigue la convención snake_case requerida."""
    pass


class ANALYTICS_LAYER_POSTHOG_NO_CONFIGURADO(AnalyticsLayerError):
    """PostHog no está configurado. Proporciona POSTHOG_API_KEY y POSTHOG_HOST."""
    pass


# ─── Enums con naming de identidad (Brand Check #1) ──────────────────────────

class CategoriaEvento(Enum):
    """Categoría de evento según la taxonomía estándar de El Monstruo."""
    ADQUISICION = "adquisicion"       # Cómo llegó el usuario
    ACTIVACION = "activacion"         # Primera acción de valor
    RETENCION = "retencion"           # Vuelve a usar el producto
    REFERIDO = "referido"             # Invita a otros
    INGRESO = "ingreso"               # Genera dinero
    SOPORTE = "soporte"               # Pide ayuda
    TECNICO = "tecnico"               # Eventos de sistema


class TipoFunnel(Enum):
    """Tipo de funnel de conversión."""
    REGISTRO = "registro"
    ACTIVACION = "activacion"
    COMPRA = "compra"
    ONBOARDING = "onboarding"


# ─── Dataclasses ─────────────────────────────────────────────────────────────

@dataclass
class EventoAnalytics:
    """
    Evento de analytics estandarizado según taxonomía de El Monstruo.

    Attributes:
        nombre: Nombre del evento en snake_case (e.g., "usuario_registro").
        categoria: Categoría AARRR del evento.
        descripcion: Descripción humana del evento.
        propiedades: Propiedades que se deben capturar con el evento.
        es_conversion: Si este evento representa una conversión clave.
        valor_negocio: Descripción del valor de negocio que representa.
    """
    nombre: str
    categoria: CategoriaEvento
    descripcion: str
    propiedades: list[str] = field(default_factory=list)
    es_conversion: bool = False
    valor_negocio: str = ""


@dataclass
class MetricasRetencion:
    """
    Métricas de retención calculadas para un cohorte de usuarios.

    Attributes:
        cohorte_fecha: Fecha del cohorte analizado.
        usuarios_iniciales: Usuarios que iniciaron en el cohorte.
        retencion_dia_1: % de usuarios que volvieron al día 1.
        retencion_dia_7: % de usuarios que volvieron al día 7.
        retencion_dia_30: % de usuarios que volvieron al día 30.
        churn_rate: Tasa de abandono del cohorte.
    """
    cohorte_fecha: str
    usuarios_iniciales: int
    retencion_dia_1: float = 0.0
    retencion_dia_7: float = 0.0
    retencion_dia_30: float = 0.0
    churn_rate: float = 0.0


@dataclass
class PuntuacionEngagement:
    """
    Puntuación de engagement de un usuario.

    Attributes:
        usuario_id: Identificador del usuario.
        puntaje: Puntaje de engagement (0-100).
        nivel: Nivel de engagement (dormido, bajo, medio, alto, campeon).
        sesiones_ultimos_30d: Número de sesiones en los últimos 30 días.
        acciones_clave: Número de acciones clave completadas.
        dias_activo: Días activos en los últimos 30 días.
    """
    usuario_id: str
    puntaje: float
    nivel: str
    sesiones_ultimos_30d: int = 0
    acciones_clave: int = 0
    dias_activo: int = 0


# ─── Clase principal ─────────────────────────────────────────────────────────

class AnalyticsLayer:
    """
    Capa de analytics transversal — genera configuraciones de tracking
    y taxonomías de eventos para proyectos creados por El Monstruo.

    Uso:
        layer = AnalyticsLayer()
        taxonomia = layer.generar_taxonomia("mi-saas")
        config_posthog = layer.generar_config_posthog("mi-saas", "saas")
    """

    # Taxonomía base de eventos AARRR para SaaS
    EVENTOS_BASE_SAAS = [
        EventoAnalytics(
            nombre="usuario_registro",
            categoria=CategoriaEvento.ADQUISICION,
            descripcion="Usuario completó el registro",
            propiedades=["metodo_registro", "fuente", "plan_inicial"],
            es_conversion=True,
            valor_negocio="Nuevo usuario en el sistema",
        ),
        EventoAnalytics(
            nombre="usuario_primera_accion",
            categoria=CategoriaEvento.ACTIVACION,
            descripcion="Usuario completó su primera acción de valor",
            propiedades=["accion_tipo", "tiempo_desde_registro_segundos"],
            es_conversion=True,
            valor_negocio="Usuario activado — llegó al 'aha moment'",
        ),
        EventoAnalytics(
            nombre="sesion_iniciada",
            categoria=CategoriaEvento.RETENCION,
            descripcion="Usuario inició una sesión",
            propiedades=["dispositivo", "plataforma", "dias_desde_ultimo_login"],
            es_conversion=False,
            valor_negocio="Usuario retiene — sigue usando el producto",
        ),
        EventoAnalytics(
            nombre="suscripcion_creada",
            categoria=CategoriaEvento.INGRESO,
            descripcion="Usuario creó una suscripción de pago",
            propiedades=["plan", "monto_usd", "ciclo_facturacion", "metodo_pago"],
            es_conversion=True,
            valor_negocio="Conversión a cliente de pago",
        ),
        EventoAnalytics(
            nombre="invitacion_enviada",
            categoria=CategoriaEvento.REFERIDO,
            descripcion="Usuario invitó a otro usuario",
            propiedades=["canal_invitacion", "invitado_acepto"],
            es_conversion=False,
            valor_negocio="Crecimiento viral orgánico",
        ),
        EventoAnalytics(
            nombre="soporte_ticket_creado",
            categoria=CategoriaEvento.SOPORTE,
            descripcion="Usuario creó un ticket de soporte",
            propiedades=["categoria_problema", "prioridad", "canal"],
            es_conversion=False,
            valor_negocio="Señal de fricción — oportunidad de mejora",
        ),
    ]

    def __init__(self, posthog_client=None):
        # Soberanía: PostHog → alternativa: Mixpanel, Amplitude, o SQL en Supabase
        self._posthog = posthog_client
        logger.info("analytics_layer_inicializado", componente="transversal.analytics_layer")

    def generar_taxonomia(self, proyecto_id: str, tipo: str = "saas") -> list[EventoAnalytics]:
        """
        Generar taxonomía de eventos para el proyecto.

        Args:
            proyecto_id: Identificador único del proyecto.
            tipo: Tipo de proyecto ("saas", "ecommerce", "marketplace").

        Returns:
            Lista de EventoAnalytics con la taxonomía completa del proyecto.
        """
        # Base: eventos AARRR estándar para SaaS
        eventos = list(self.EVENTOS_BASE_SAAS)

        # Eventos específicos por tipo
        if tipo == "ecommerce":
            eventos.extend([
                EventoAnalytics(
                    nombre="producto_visto",
                    categoria=CategoriaEvento.ACTIVACION,
                    descripcion="Usuario vio un producto",
                    propiedades=["producto_id", "categoria", "precio_usd"],
                    es_conversion=False,
                ),
                EventoAnalytics(
                    nombre="carrito_item_agregado",
                    categoria=CategoriaEvento.ACTIVACION,
                    descripcion="Usuario agregó item al carrito",
                    propiedades=["producto_id", "cantidad", "precio_usd"],
                    es_conversion=True,
                ),
                EventoAnalytics(
                    nombre="compra_completada",
                    categoria=CategoriaEvento.INGRESO,
                    descripcion="Usuario completó una compra",
                    propiedades=["orden_id", "total_usd", "items_count", "metodo_pago"],
                    es_conversion=True,
                    valor_negocio="Transacción completada",
                ),
            ])

        logger.info(
            "taxonomia_generada",
            proyecto_id=proyecto_id,
            tipo=tipo,
            eventos_count=len(eventos),
        )
        return eventos

    def calcular_retencion(
        self,
        usuarios_dia_0: set,
        usuarios_dia_1: set,
        usuarios_dia_7: set,
        usuarios_dia_30: set,
        cohorte_fecha: str,
    ) -> MetricasRetencion:
        """
        Calcular métricas de retención para un cohorte.

        Args:
            usuarios_dia_0: Set de user_ids que iniciaron en el cohorte.
            usuarios_dia_1: Set de user_ids activos al día 1.
            usuarios_dia_7: Set de user_ids activos al día 7.
            usuarios_dia_30: Set de user_ids activos al día 30.
            cohorte_fecha: Fecha del cohorte en formato ISO 8601.

        Returns:
            MetricasRetencion con porcentajes calculados.

        Soberanía: Cálculo en Python puro — sin dependencia externa.
        """
        n = max(len(usuarios_dia_0), 1)

        retencion_1 = len(usuarios_dia_0 & usuarios_dia_1) / n * 100
        retencion_7 = len(usuarios_dia_0 & usuarios_dia_7) / n * 100
        retencion_30 = len(usuarios_dia_0 & usuarios_dia_30) / n * 100
        churn = 100 - retencion_30

        metricas = MetricasRetencion(
            cohorte_fecha=cohorte_fecha,
            usuarios_iniciales=len(usuarios_dia_0),
            retencion_dia_1=round(retencion_1, 2),
            retencion_dia_7=round(retencion_7, 2),
            retencion_dia_30=round(retencion_30, 2),
            churn_rate=round(churn, 2),
        )

        logger.info(
            "retencion_calculada",
            cohorte=cohorte_fecha,
            usuarios=len(usuarios_dia_0),
            retencion_30d=metricas.retencion_dia_30,
            churn=metricas.churn_rate,
        )
        return metricas

    def calcular_engagement(
        self,
        usuario_id: str,
        sesiones: int,
        acciones_clave: int,
        dias_activo: int,
    ) -> PuntuacionEngagement:
        """
        Calcular puntuación de engagement de un usuario.

        Args:
            usuario_id: Identificador del usuario.
            sesiones: Número de sesiones en los últimos 30 días.
            acciones_clave: Número de acciones clave completadas.
            dias_activo: Días activos en los últimos 30 días.

        Returns:
            PuntuacionEngagement con puntaje y nivel.

        Soberanía: Cálculo en Python puro — sin dependencia externa.
        """
        # Ponderación: sesiones 30%, acciones 50%, días activos 20%
        puntaje_sesiones = min(sesiones / 20, 1.0) * 30
        puntaje_acciones = min(acciones_clave / 10, 1.0) * 50
        puntaje_dias = min(dias_activo / 20, 1.0) * 20
        puntaje = puntaje_sesiones + puntaje_acciones + puntaje_dias

        if puntaje >= 80:
            nivel = "campeon"
        elif puntaje >= 60:
            nivel = "alto"
        elif puntaje >= 40:
            nivel = "medio"
        elif puntaje >= 20:
            nivel = "bajo"
        else:
            nivel = "dormido"

        return PuntuacionEngagement(
            usuario_id=usuario_id,
            puntaje=round(puntaje, 2),
            nivel=nivel,
            sesiones_ultimos_30d=sesiones,
            acciones_clave=acciones_clave,
            dias_activo=dias_activo,
        )

    def generar_config_posthog(self, proyecto_id: str, tipo: str = "saas") -> dict:
        """
        Generar configuración de PostHog para el proyecto.

        Args:
            proyecto_id: Identificador único del proyecto.
            tipo: Tipo de proyecto para personalizar la configuración.

        Returns:
            Dict con configuración de PostHog lista para inyectar.

        Soberanía: PostHog → alternativa: Mixpanel (pip install mixpanel),
                   Amplitude (pip install amplitude-analytics), o SQL en Supabase.
        """
        taxonomia = self.generar_taxonomia(proyecto_id, tipo)
        eventos_conversion = [e.nombre for e in taxonomia if e.es_conversion]

        return {
            "proyecto_id": proyecto_id,
            "proveedor": "PostHog",
            # Soberanía: alternativa Mixpanel, Amplitude, o SQL analytics en Supabase
            "soberania": "Alternativa: Mixpanel, Amplitude, o SQL analytics en Supabase",
            "env_vars": ["POSTHOG_API_KEY", "POSTHOG_HOST=https://app.posthog.com"],
            "eventos_a_trackear": [e.nombre for e in taxonomia],
            "eventos_conversion": eventos_conversion,
            "funnels": [
                {
                    "nombre": f"{proyecto_id}_funnel_activacion",
                    "pasos": ["usuario_registro", "usuario_primera_accion", "suscripcion_creada"],
                },
            ],
            "feature_flags": [
                f"{proyecto_id}_beta_features",
                f"{proyecto_id}_new_onboarding",
            ],
            "session_recording": tipo != "herramienta_interna",
            "autocapture": False,  # Explícito es mejor que implícito
        }

    def generar_template_tracking(self, proyecto_id: str) -> str:
        """
        Generar código de tracking para el proyecto.

        Args:
            proyecto_id: Identificador único del proyecto.

        Returns:
            String con código Python de tracking listo para inyectar.

        Soberanía: posthog-python → alternativa: requests directo a PostHog API
        """
        return f'''"""
Analytics Tracker — Generado por El Monstruo Analytics Layer
Proyecto: {proyecto_id}
Soberanía: posthog-python → alternativa: requests directo a PostHog API
"""
import os
# Soberanía: posthog-python → alternativa: requests directo a PostHog API
try:
    import posthog
    posthog.api_key = os.environ.get("POSTHOG_API_KEY", "")
    posthog.host = os.environ.get("POSTHOG_HOST", "https://app.posthog.com")
    _POSTHOG_DISPONIBLE = bool(posthog.api_key)
except ImportError:
    _POSTHOG_DISPONIBLE = False


def track(usuario_id: str, evento: str, propiedades: dict = None):
    """Registrar evento de analytics. Graceful degradation si PostHog no disponible."""
    if not _POSTHOG_DISPONIBLE:
        return  # Silencioso — no bloquea el flujo principal
    
    try:
        posthog.capture(
            distinct_id=usuario_id,
            event=evento,
            properties={{
                "proyecto": "{proyecto_id}",
                **(propiedades or {{}})
            }}
        )
    except Exception:
        pass  # Analytics nunca debe romper el flujo principal


def identify(usuario_id: str, propiedades: dict):
    """Identificar usuario con sus propiedades."""
    if not _POSTHOG_DISPONIBLE:
        return
    try:
        posthog.identify(distinct_id=usuario_id, properties=propiedades)
    except Exception:
        pass
'''

    def to_dict(self) -> dict:
        """
        Serializar estado del AnalyticsLayer para el Command Center.

        Returns:
            Dict con estado actual consumible por el Command Center.
        """
        return {
            "componente": "analytics_layer",
            "version": "58.3",
            "eventos_base_saas": len(self.EVENTOS_BASE_SAAS),
            "categorias_evento": [c.value for c in CategoriaEvento],
            "tipos_funnel": [t.value for t in TipoFunnel],
            "posthog_configurado": self._posthog is not None,
            "estado": "activo",
        }


# ─── Singleton factory ────────────────────────────────────────────────────────

_analytics_layer_instance: Optional[AnalyticsLayer] = None


def get_analytics_layer(posthog_client=None) -> AnalyticsLayer:
    """
    Obtener instancia singleton del AnalyticsLayer.

    Args:
        posthog_client: Cliente PostHog opcional.

    Returns:
        Instancia única de AnalyticsLayer.
    """
    global _analytics_layer_instance
    if _analytics_layer_instance is None:
        _analytics_layer_instance = AnalyticsLayer(posthog_client=posthog_client)
    return _analytics_layer_instance
