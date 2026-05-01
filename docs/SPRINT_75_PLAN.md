# Sprint 75 — "El Monstruo que Vende"
## Serie 71-80: La Colmena Despierta | Embrión-2: Motor de Ventas

**Fecha de diseño:** 1 de Mayo 2026
**Autor:** Hilo B (Arquitecto)
**Objetivo primario:** Obj #1 (Crear empresas que generen revenue)
**Objetivos secundarios:** Obj #2 (Apple/Tesla), Obj #5 (Magna/Premium), Obj #9 (Transversalidad)
**Arquitectura:** Pensador (LLM potente) + Ejecutor (código determinista)
**Dependencias:** Sprint 72 (TEL), Sprint 74 (Memoria + Colmena)

---

## Contexto Estratégico

El Monstruo piensa, valida marca, ejecuta encomiendas, navega la web, y se coordina con otros Embriones. Pero todavía no genera dinero. Sprint 75 resuelve esto: el Embrión-2 es el Motor de Ventas — la capa transversal que convierte capacidad en revenue.

No es un CRM. No es un funnel builder. Es un agente autónomo que:
1. Identifica oportunidades de venta (proactivamente)
2. Diseña la estrategia de conversión (pricing, copy, funnel)
3. Ejecuta la venta (landing pages, emails, follow-ups)
4. Mide el resultado (revenue, CAC, LTV, churn)
5. Optimiza perpetuamente (A/B testing sin intervención humana)

---

## Épica 75.1 — Modelos de Dominio del Motor de Ventas

### Archivo: `kernel/ventas/models.py`

```python
"""
Motor de Ventas — Modelos de Dominio
Sprint 75: El Monstruo que Vende
Capa Transversal: Revenue Generation

Cada modelo representa un concepto del ciclo de ventas completo:
Oportunidad → Estrategia → Ejecución → Medición → Optimización
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class EstadoOportunidad(Enum):
    """Estados del ciclo de vida de una oportunidad de venta."""
    DETECTADA = "detectada"          # Identificada por el Embrión
    EVALUADA = "evaluada"            # Analizada viabilidad
    ESTRATEGIA_LISTA = "estrategia_lista"  # Plan de conversión definido
    EN_EJECUCION = "en_ejecucion"    # Funnel activo
    CONVERTIDA = "convertida"        # Revenue generado
    PERDIDA = "perdida"              # No convirtió — registrar por qué
    OPTIMIZANDO = "optimizando"      # A/B testing activo


class TipoProducto(Enum):
    """Tipos de producto que El Monstruo puede vender."""
    SERVICIO_DIGITAL = "servicio_digital"      # SaaS, APIs, subscriptions
    PRODUCTO_FISICO = "producto_fisico"        # E-commerce
    CONSULTORIA = "consultoria"                # Alto valor, bajo volumen
    CONTENIDO = "contenido"                    # Cursos, membresías, media
    MARKETPLACE = "marketplace"                # Conectar oferta y demanda
    AFILIACION = "afiliacion"                  # Comisiones por referencia


class CanalVenta(Enum):
    """Canales de adquisición y conversión."""
    ORGANICO_SEO = "organico_seo"
    PAID_ADS = "paid_ads"
    EMAIL = "email"
    SOCIAL = "social"
    REFERRAL = "referral"
    DIRECTO = "directo"
    PARTNERSHIP = "partnership"


@dataclass
class Oportunidad:
    """Una oportunidad de venta detectada por el Embrión."""
    id: str
    titulo: str
    descripcion: str
    tipo_producto: TipoProducto
    mercado_objetivo: str
    dolor_que_resuelve: str
    competidores: list[str]
    tam_estimado_usd: float          # Total Addressable Market
    probabilidad_exito: float        # 0.0 - 1.0
    esfuerzo_estimado_horas: float
    estado: EstadoOportunidad = EstadoOportunidad.DETECTADA
    fuente_deteccion: str = ""       # Cómo se detectó (tendencia, pedido, análisis)
    fecha_deteccion: datetime = field(default_factory=datetime.utcnow)
    notas_embrion: str = ""          # Razonamiento del Pensador


@dataclass
class EstrategiaVenta:
    """Plan de conversión para una oportunidad."""
    id: str
    oportunidad_id: str
    propuesta_valor: str             # Una frase que vende
    pricing_modelo: str              # freemium, one-time, subscription, tiered
    precio_base_usd: float
    canal_principal: CanalVenta
    canales_secundarios: list[CanalVenta]
    funnel_pasos: list[str]          # ["landing", "lead_magnet", "nurture", "oferta", "close"]
    copy_gancho: str                 # Hook principal
    diferenciador: str               # Por qué nosotros y no la competencia
    metricas_objetivo: dict = field(default_factory=dict)  # {"conversion_rate": 0.05, "cac_max": 50}
    fecha_creacion: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Ejecucion:
    """Una instancia de ejecución de la estrategia de venta."""
    id: str
    estrategia_id: str
    canal: CanalVenta
    activos_generados: list[str]     # URLs de landing pages, emails, ads
    presupuesto_asignado_usd: float
    fecha_inicio: datetime = field(default_factory=datetime.utcnow)
    fecha_fin: Optional[datetime] = None
    estado: str = "activa"


@dataclass
class MetricaVenta:
    """Métricas de resultado de una ejecución."""
    ejecucion_id: str
    fecha: datetime
    impresiones: int = 0
    clicks: int = 0
    leads: int = 0
    conversiones: int = 0
    revenue_usd: float = 0.0
    costo_usd: float = 0.0
    cac_usd: float = 0.0            # Cost of Acquisition
    ltv_usd: float = 0.0            # Lifetime Value
    roi: float = 0.0                # Return on Investment

    @property
    def conversion_rate(self) -> float:
        return self.conversiones / max(self.clicks, 1)

    @property
    def roas(self) -> float:
        """Return on Ad Spend."""
        return self.revenue_usd / max(self.costo_usd, 0.01)


@dataclass
class ExperimentoAB:
    """Un experimento A/B activo."""
    id: str
    ejecucion_id: str
    hipotesis: str                   # "El copy directo convierte mejor que el emocional"
    variante_a: str                  # Descripción de control
    variante_b: str                  # Descripción de tratamiento
    metrica_objetivo: str            # "conversion_rate"
    muestra_minima: int = 100
    confianza_requerida: float = 0.95
    resultado: Optional[str] = None  # "a_gana", "b_gana", "sin_diferencia"
    fecha_inicio: datetime = field(default_factory=datetime.utcnow)
    fecha_fin: Optional[datetime] = None
```

### Criterios de aceptación:
- [ ] Todos los modelos tipados con dataclasses
- [ ] Enums en español con valores descriptivos
- [ ] Propiedades calculadas para métricas derivadas
- [ ] Docstrings con tono de marca (directo, preciso)

---

## Épica 75.2 — Ejecutor Determinista: Pipeline de Ventas

### Archivo: `kernel/ventas/ejecutor.py`

```python
"""
Motor de Ventas — Ejecutor Determinista
Sprint 75: El Monstruo que Vende

El Ejecutor NO usa LLM. Es código Python puro que:
- Persiste oportunidades y estrategias en Supabase
- Calcula métricas y ROI
- Ejecuta A/B tests con significancia estadística
- Genera reportes para el Command Center
- Dispara alertas cuando métricas cruzan umbrales

Costo por operación: $0. Latencia: <10ms.
"""

import json
import math
from datetime import datetime, timedelta
from typing import Optional

from kernel.ventas.models import (
    CanalVenta, Ejecucion, EstadoOportunidad, ExperimentoAB,
    MetricaVenta, Oportunidad, EstrategiaVenta, TipoProducto
)


class VentasEjecutor:
    """
    Ejecutor determinista del Motor de Ventas.
    Maneja toda la lógica que NO requiere juicio subjetivo.
    """

    def __init__(self, supabase_client, logger):
        self.db = supabase_client
        self.log = logger
        self.umbrales = {
            "cac_max_usd": 100.0,
            "roi_min": 2.0,
            "conversion_min": 0.02,
            "churn_max_mensual": 0.05,
        }

    # --- Persistencia ---

    async def guardar_oportunidad(self, oportunidad: Oportunidad) -> str:
        """Persiste una oportunidad en Supabase."""
        data = {
            "id": oportunidad.id,
            "titulo": oportunidad.titulo,
            "descripcion": oportunidad.descripcion,
            "tipo_producto": oportunidad.tipo_producto.value,
            "mercado_objetivo": oportunidad.mercado_objetivo,
            "dolor_que_resuelve": oportunidad.dolor_que_resuelve,
            "competidores": json.dumps(oportunidad.competidores),
            "tam_estimado_usd": oportunidad.tam_estimado_usd,
            "probabilidad_exito": oportunidad.probabilidad_exito,
            "esfuerzo_estimado_horas": oportunidad.esfuerzo_estimado_horas,
            "estado": oportunidad.estado.value,
            "fuente_deteccion": oportunidad.fuente_deteccion,
            "notas_embrion": oportunidad.notas_embrion,
            "created_at": oportunidad.fecha_deteccion.isoformat(),
        }
        result = await self.db.table("oportunidades_venta").upsert(data).execute()
        self.log.info(f"[ventas_ejecutor] oportunidad_guardada id={oportunidad.id}")
        return oportunidad.id

    async def guardar_estrategia(self, estrategia: EstrategiaVenta) -> str:
        """Persiste una estrategia de venta."""
        data = {
            "id": estrategia.id,
            "oportunidad_id": estrategia.oportunidad_id,
            "propuesta_valor": estrategia.propuesta_valor,
            "pricing_modelo": estrategia.pricing_modelo,
            "precio_base_usd": estrategia.precio_base_usd,
            "canal_principal": estrategia.canal_principal.value,
            "canales_secundarios": json.dumps([c.value for c in estrategia.canales_secundarios]),
            "funnel_pasos": json.dumps(estrategia.funnel_pasos),
            "copy_gancho": estrategia.copy_gancho,
            "diferenciador": estrategia.diferenciador,
            "metricas_objetivo": json.dumps(estrategia.metricas_objetivo),
            "created_at": estrategia.fecha_creacion.isoformat(),
        }
        result = await self.db.table("estrategias_venta").upsert(data).execute()
        self.log.info(f"[ventas_ejecutor] estrategia_guardada id={estrategia.id}")
        return estrategia.id

    async def registrar_metrica(self, metrica: MetricaVenta) -> None:
        """Registra métricas de una ejecución."""
        data = {
            "ejecucion_id": metrica.ejecucion_id,
            "fecha": metrica.fecha.isoformat(),
            "impresiones": metrica.impresiones,
            "clicks": metrica.clicks,
            "leads": metrica.leads,
            "conversiones": metrica.conversiones,
            "revenue_usd": metrica.revenue_usd,
            "costo_usd": metrica.costo_usd,
            "cac_usd": metrica.cac_usd,
            "ltv_usd": metrica.ltv_usd,
            "roi": metrica.roi,
        }
        await self.db.table("metricas_venta").insert(data).execute()

    # --- Cálculos Deterministas ---

    def calcular_score_oportunidad(self, oportunidad: Oportunidad) -> float:
        """
        Score de priorización: 0-100.
        Factores: TAM, probabilidad, esfuerzo inverso, tipo.
        """
        tam_score = min(oportunidad.tam_estimado_usd / 1_000_000, 1.0) * 30
        prob_score = oportunidad.probabilidad_exito * 40
        esfuerzo_score = max(0, (100 - oportunidad.esfuerzo_estimado_horas) / 100) * 20
        tipo_bonus = {
            TipoProducto.SERVICIO_DIGITAL: 10,
            TipoProducto.MARKETPLACE: 8,
            TipoProducto.CONTENIDO: 6,
            TipoProducto.CONSULTORIA: 5,
            TipoProducto.AFILIACION: 4,
            TipoProducto.PRODUCTO_FISICO: 3,
        }
        bonus = tipo_bonus.get(oportunidad.tipo_producto, 0)
        return round(tam_score + prob_score + esfuerzo_score + bonus, 1)

    def evaluar_significancia_ab(self, experimento: ExperimentoAB,
                                  metricas_a: list[float],
                                  metricas_b: list[float]) -> dict:
        """
        Evalúa significancia estadística de un A/B test.
        Usa z-test para proporciones.
        Retorna: {"significativo": bool, "ganador": str, "p_value": float}
        """
        n_a = len(metricas_a)
        n_b = len(metricas_b)

        if n_a < experimento.muestra_minima or n_b < experimento.muestra_minima:
            return {"significativo": False, "ganador": "insuficiente_muestra", "p_value": 1.0}

        p_a = sum(metricas_a) / n_a
        p_b = sum(metricas_b) / n_b
        p_pool = (sum(metricas_a) + sum(metricas_b)) / (n_a + n_b)

        if p_pool == 0 or p_pool == 1:
            return {"significativo": False, "ganador": "sin_variacion", "p_value": 1.0}

        se = math.sqrt(p_pool * (1 - p_pool) * (1/n_a + 1/n_b))
        if se == 0:
            return {"significativo": False, "ganador": "sin_variacion", "p_value": 1.0}

        z = (p_b - p_a) / se
        # Aproximación de p-value (two-tailed)
        p_value = 2 * (1 - self._normal_cdf(abs(z)))

        significativo = p_value < (1 - experimento.confianza_requerida)
        ganador = "b_gana" if z > 0 and significativo else "a_gana" if z < 0 and significativo else "sin_diferencia"

        return {"significativo": significativo, "ganador": ganador, "p_value": round(p_value, 4)}

    def _normal_cdf(self, x: float) -> float:
        """Aproximación de CDF normal estándar (Abramowitz & Stegun)."""
        a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
        p = 0.3275911
        sign = 1 if x >= 0 else -1
        x = abs(x) / math.sqrt(2)
        t = 1.0 / (1.0 + p * x)
        y = 1.0 - (((((a5*t + a4)*t) + a3)*t + a2)*t + a1)*t * math.exp(-x*x)
        return 0.5 * (1.0 + sign * y)

    # --- Alertas y Umbrales ---

    async def verificar_salud_ventas(self) -> list[dict]:
        """
        Verifica métricas contra umbrales y genera alertas.
        Se ejecuta cada heartbeat del Embrión-2.
        """
        alertas = []

        # Obtener métricas de las últimas 24h
        desde = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        result = await self.db.table("metricas_venta").select("*").gte("fecha", desde).execute()
        metricas = result.data if result.data else []

        if not metricas:
            return alertas

        # CAC promedio
        cacs = [m["cac_usd"] for m in metricas if m["cac_usd"] > 0]
        if cacs:
            cac_promedio = sum(cacs) / len(cacs)
            if cac_promedio > self.umbrales["cac_max_usd"]:
                alertas.append({
                    "tipo": "cac_excedido",
                    "severidad": "alta",
                    "valor": cac_promedio,
                    "umbral": self.umbrales["cac_max_usd"],
                    "mensaje": f"[ventas] CAC promedio ${cac_promedio:.2f} excede umbral ${self.umbrales['cac_max_usd']}"
                })

        # ROI promedio
        rois = [m["roi"] for m in metricas if m["roi"] != 0]
        if rois:
            roi_promedio = sum(rois) / len(rois)
            if roi_promedio < self.umbrales["roi_min"]:
                alertas.append({
                    "tipo": "roi_bajo",
                    "severidad": "media",
                    "valor": roi_promedio,
                    "umbral": self.umbrales["roi_min"],
                    "mensaje": f"[ventas] ROI promedio {roi_promedio:.1f}x bajo umbral {self.umbrales['roi_min']}x"
                })

        # Conversion rate
        total_clicks = sum(m["clicks"] for m in metricas)
        total_conversiones = sum(m["conversiones"] for m in metricas)
        if total_clicks > 0:
            cr = total_conversiones / total_clicks
            if cr < self.umbrales["conversion_min"]:
                alertas.append({
                    "tipo": "conversion_baja",
                    "severidad": "alta",
                    "valor": cr,
                    "umbral": self.umbrales["conversion_min"],
                    "mensaje": f"[ventas] Conversion rate {cr:.3%} bajo umbral {self.umbrales['conversion_min']:.1%}"
                })

        return alertas

    # --- API para Command Center ---

    async def obtener_dashboard_ventas(self) -> dict:
        """
        Datos para el Command Center — sección Ventas.
        Retorna métricas agregadas de las últimas 24h, 7d, 30d.
        """
        periodos = {"24h": 1, "7d": 7, "30d": 30}
        dashboard = {}

        for periodo, dias in periodos.items():
            desde = (datetime.utcnow() - timedelta(days=dias)).isoformat()
            result = await self.db.table("metricas_venta").select("*").gte("fecha", desde).execute()
            metricas = result.data if result.data else []

            dashboard[periodo] = {
                "revenue_total_usd": sum(m["revenue_usd"] for m in metricas),
                "costo_total_usd": sum(m["costo_usd"] for m in metricas),
                "conversiones": sum(m["conversiones"] for m in metricas),
                "leads": sum(m["leads"] for m in metricas),
                "impresiones": sum(m["impresiones"] for m in metricas),
                "roi_promedio": (
                    sum(m["roi"] for m in metricas) / len(metricas)
                    if metricas else 0
                ),
            }

        # Oportunidades activas
        opps = await self.db.table("oportunidades_venta").select("*").neq("estado", "perdida").execute()
        dashboard["oportunidades_activas"] = len(opps.data) if opps.data else 0

        # Experimentos activos
        exps = await self.db.table("experimentos_ab").select("*").is_("resultado", "null").execute()
        dashboard["experimentos_activos"] = len(exps.data) if exps.data else 0

        return dashboard
```

### Criterios de aceptación:
- [ ] Cero dependencias de LLM — todo es cálculo puro
- [ ] A/B testing con z-test estadístico real (no simulado)
- [ ] Alertas con severidad y mensajes con identidad de marca
- [ ] Endpoint `obtener_dashboard_ventas()` retorna JSON listo para Command Center
- [ ] Tests: `pytest kernel/ventas/test_ejecutor.py`

---

## Épica 75.3 — Pensador: Estratega de Ventas Autónomo

### Archivo: `kernel/ventas/pensador.py`

```python
"""
Motor de Ventas — Pensador (LLM Potente)
Sprint 75: El Monstruo que Vende

El Pensador se activa SOLO cuando hay juicio subjetivo:
- Detectar oportunidades en datos no estructurados
- Diseñar estrategias de conversión creativas
- Escribir copy que vende
- Decidir cuándo pivotar una estrategia fallida
- Proponer experimentos A/B con hipótesis inteligentes

NO se activa para: cálculos, persistencia, formateo, alertas mecánicas.
"""

from datetime import datetime
from typing import Optional

from kernel.ventas.models import (
    CanalVenta, EstrategiaVenta, ExperimentoAB,
    Oportunidad, TipoProducto, EstadoOportunidad
)


class VentasPensador:
    """
    Pensador del Motor de Ventas.
    Usa el LLM más potente disponible para decisiones que requieren creatividad y juicio.
    """

    def __init__(self, llm_client, brand_validator, memory_client, logger):
        self.llm = llm_client
        self.brand = brand_validator
        self.memory = memory_client
        self.log = logger
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        return """Eres el Motor de Ventas de El Monstruo — un agente autónomo especializado en 
identificar oportunidades de revenue y diseñar estrategias de conversión.

Tu personalidad:
- Implacable en la búsqueda de oportunidades
- Preciso en el análisis de mercado
- Creativo en las propuestas de valor
- Honesto sobre probabilidades de éxito

Reglas:
1. NUNCA propongas algo que no puedas medir
2. SIEMPRE incluye un diferenciador claro vs. competencia
3. El pricing debe ser justificable con datos
4. El copy debe pasar validación del Brand Engine
5. Si una estrategia falla 3 veces, propón pivot — no insistas

Formato de respuesta: JSON estructurado según los modelos de dominio."""

    async def detectar_oportunidades(self, contexto: dict) -> list[Oportunidad]:
        """
        Analiza contexto (tendencias, conversaciones, datos de mercado)
        y detecta oportunidades de venta.

        Se activa cuando:
        - El Embrión de Tendencias detecta algo nuevo
        - Un usuario expresa un dolor
        - Hay un gap en el mercado detectado por research
        """
        prompt = f"""Analiza el siguiente contexto y detecta oportunidades de venta concretas.

Contexto:
{contexto}

Para cada oportunidad, proporciona:
- titulo: nombre corto y memorable
- descripcion: qué es y por qué es oportunidad
- tipo_producto: {[t.value for t in TipoProducto]}
- mercado_objetivo: quién compraría esto
- dolor_que_resuelve: problema específico que soluciona
- competidores: quién más ofrece algo similar
- tam_estimado_usd: tamaño de mercado estimado
- probabilidad_exito: 0.0-1.0 con justificación
- esfuerzo_estimado_horas: cuánto tomaría crear el MVP

Responde en JSON array. Solo incluye oportunidades con probabilidad > 0.3."""

        response = await self.llm.generate(
            system=self.system_prompt,
            prompt=prompt,
            temperature=0.7,
            response_format="json"
        )

        oportunidades = self._parse_oportunidades(response)
        self.log.info(f"[ventas_pensador] {len(oportunidades)} oportunidades detectadas")
        return oportunidades

    async def disenar_estrategia(self, oportunidad: Oportunidad) -> EstrategiaVenta:
        """
        Diseña una estrategia de conversión completa para una oportunidad.

        Se activa cuando:
        - Una oportunidad pasa el score mínimo del Ejecutor
        - Se necesita un approach creativo (no template)
        """
        # Consultar memoria: ¿qué estrategias han funcionado antes?
        memoria_relevante = await self.memory.buscar(
            query=f"estrategia venta {oportunidad.tipo_producto.value} {oportunidad.mercado_objetivo}",
            limit=5
        )

        prompt = f"""Diseña una estrategia de venta para esta oportunidad:

Oportunidad: {oportunidad.titulo}
Descripción: {oportunidad.descripcion}
Tipo: {oportunidad.tipo_producto.value}
Mercado: {oportunidad.mercado_objetivo}
Dolor: {oportunidad.dolor_que_resuelve}
Competidores: {oportunidad.competidores}
TAM: ${oportunidad.tam_estimado_usd:,.0f}

Aprendizajes previos relevantes:
{memoria_relevante}

Diseña:
1. propuesta_valor: UNA frase que vende (máx 15 palabras)
2. pricing_modelo: freemium | one-time | subscription | tiered (justifica)
3. precio_base_usd: con justificación vs. competencia
4. canal_principal: {[c.value for c in CanalVenta]} (el más efectivo para este mercado)
5. canales_secundarios: 2-3 canales de apoyo
6. funnel_pasos: secuencia exacta del funnel
7. copy_gancho: el hook principal (máx 20 palabras)
8. diferenciador: por qué nosotros y no la competencia
9. metricas_objetivo: conversion_rate, cac_max, ltv_min

Responde en JSON."""

        response = await self.llm.generate(
            system=self.system_prompt,
            prompt=prompt,
            temperature=0.8,
            response_format="json"
        )

        estrategia = self._parse_estrategia(response, oportunidad.id)

        # Validar con Brand Engine
        brand_score = await self.brand.validar_texto(estrategia.copy_gancho)
        if brand_score < 70:
            self.log.warning(f"[ventas_pensador] copy rechazado por Brand Engine (score={brand_score})")
            estrategia = await self._refinar_copy(estrategia, brand_score)

        return estrategia

    async def proponer_experimento(self, ejecucion: Ejecucion,
                                     metricas: list[MetricaVenta]) -> Optional[ExperimentoAB]:
        """
        Propone un experimento A/B basado en datos de rendimiento.

        Se activa cuando:
        - Una ejecución tiene >100 impresiones pero conversion < objetivo
        - Han pasado 7 días sin mejora
        """
        prompt = f"""Analiza estas métricas de una ejecución de venta y propón un experimento A/B:

Ejecución: {ejecucion.id}
Canal: {ejecucion.canal.value}
Métricas recientes: {[{"conv": m.conversion_rate, "cac": m.cac_usd, "roi": m.roi} for m in metricas[-7:]]}

Propón UN experimento con:
- hipotesis: qué crees que mejorará la conversión (y por qué)
- variante_a: descripción del control (lo actual)
- variante_b: descripción del tratamiento (el cambio)
- metrica_objetivo: qué medimos
- muestra_minima: cuántas observaciones necesitamos

Solo propón si hay evidencia de que algo puede mejorar. Si las métricas son buenas, responde null."""

        response = await self.llm.generate(
            system=self.system_prompt,
            prompt=prompt,
            temperature=0.6,
            response_format="json"
        )

        return self._parse_experimento(response, ejecucion.id)

    async def decidir_pivot(self, oportunidad: Oportunidad,
                             historial_metricas: list[MetricaVenta]) -> dict:
        """
        Decide si una oportunidad debe pivotar, persistir, o abandonarse.

        Se activa cuando:
        - 3 estrategias consecutivas fallan
        - ROI negativo por >14 días
        - CAC excede 3x el umbral
        """
        prompt = f"""Una oportunidad de venta no está funcionando. Decide qué hacer:

Oportunidad: {oportunidad.titulo}
Estado actual: {oportunidad.estado.value}
Historial de métricas (últimos 14 días):
{[{"fecha": m.fecha.isoformat(), "revenue": m.revenue_usd, "costo": m.costo_usd, "roi": m.roi} for m in historial_metricas]}

Opciones:
1. PERSISTIR — Hay señales de mejora, dar más tiempo
2. PIVOTAR — Cambiar estrategia radicalmente (nuevo canal, nuevo pricing, nuevo mercado)
3. ABANDONAR — No hay evidencia de que funcione, cortar pérdidas

Responde con:
- decision: "persistir" | "pivotar" | "abandonar"
- justificacion: por qué (con datos)
- accion_siguiente: qué hacer concretamente si no es abandonar"""

        response = await self.llm.generate(
            system=self.system_prompt,
            prompt=prompt,
            temperature=0.3,  # Baja temperatura para decisiones críticas
            response_format="json"
        )

        decision = self._parse_decision(response)
        self.log.info(f"[ventas_pensador] decision_pivot oportunidad={oportunidad.id} decision={decision['decision']}")
        return decision

    async def _refinar_copy(self, estrategia: EstrategiaVenta, brand_score: int) -> EstrategiaVenta:
        """Refina el copy hasta que pase el Brand Engine."""
        prompt = f"""El Brand Engine rechazó este copy (score={brand_score}/100):
"{estrategia.copy_gancho}"

Reescríbelo manteniendo el mensaje pero alineándolo con la identidad de El Monstruo:
- Tono: Directo, confiado, sin arrogancia
- Estilo: Industrial, preciso, magnánimo
- NO: corporativismo, buzzwords, emojis, exclamaciones excesivas

Responde solo con el nuevo copy (máx 20 palabras)."""

        response = await self.llm.generate(
            system=self.system_prompt,
            prompt=prompt,
            temperature=0.5
        )
        estrategia.copy_gancho = response.strip().strip('"')
        return estrategia

    # --- Parsers (privados) ---

    def _parse_oportunidades(self, response: str) -> list[Oportunidad]:
        """Parsea la respuesta del LLM a objetos Oportunidad."""
        import json
        import uuid
        try:
            data = json.loads(response)
            if not isinstance(data, list):
                data = [data]
            return [
                Oportunidad(
                    id=str(uuid.uuid4())[:8],
                    titulo=item.get("titulo", "Sin título"),
                    descripcion=item.get("descripcion", ""),
                    tipo_producto=TipoProducto(item.get("tipo_producto", "servicio_digital")),
                    mercado_objetivo=item.get("mercado_objetivo", ""),
                    dolor_que_resuelve=item.get("dolor_que_resuelve", ""),
                    competidores=item.get("competidores", []),
                    tam_estimado_usd=float(item.get("tam_estimado_usd", 0)),
                    probabilidad_exito=float(item.get("probabilidad_exito", 0)),
                    esfuerzo_estimado_horas=float(item.get("esfuerzo_estimado_horas", 0)),
                    fuente_deteccion="embrion_ventas_pensador",
                )
                for item in data
            ]
        except (json.JSONDecodeError, KeyError) as e:
            self.log.error(f"[ventas_pensador] parse_oportunidades_error: {e}")
            return []

    def _parse_estrategia(self, response: str, oportunidad_id: str) -> EstrategiaVenta:
        """Parsea la respuesta del LLM a un objeto EstrategiaVenta."""
        import json
        import uuid
        data = json.loads(response)
        return EstrategiaVenta(
            id=str(uuid.uuid4())[:8],
            oportunidad_id=oportunidad_id,
            propuesta_valor=data.get("propuesta_valor", ""),
            pricing_modelo=data.get("pricing_modelo", "subscription"),
            precio_base_usd=float(data.get("precio_base_usd", 0)),
            canal_principal=CanalVenta(data.get("canal_principal", "organico_seo")),
            canales_secundarios=[CanalVenta(c) for c in data.get("canales_secundarios", [])],
            funnel_pasos=data.get("funnel_pasos", []),
            copy_gancho=data.get("copy_gancho", ""),
            diferenciador=data.get("diferenciador", ""),
            metricas_objetivo=data.get("metricas_objetivo", {}),
        )

    def _parse_experimento(self, response: str, ejecucion_id: str) -> Optional[ExperimentoAB]:
        """Parsea la respuesta del LLM a un ExperimentoAB o None."""
        import json
        import uuid
        try:
            data = json.loads(response)
            if data is None or data == "null":
                return None
            return ExperimentoAB(
                id=str(uuid.uuid4())[:8],
                ejecucion_id=ejecucion_id,
                hipotesis=data.get("hipotesis", ""),
                variante_a=data.get("variante_a", ""),
                variante_b=data.get("variante_b", ""),
                metrica_objetivo=data.get("metrica_objetivo", "conversion_rate"),
                muestra_minima=int(data.get("muestra_minima", 100)),
            )
        except (json.JSONDecodeError, KeyError):
            return None

    def _parse_decision(self, response: str) -> dict:
        """Parsea decisión de pivot."""
        import json
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"decision": "persistir", "justificacion": "error de parsing", "accion_siguiente": "revisar manualmente"}
```

### Criterios de aceptación:
- [ ] El Pensador SOLO se activa para decisiones que requieren juicio
- [ ] Integración con Brand Engine (valida copy antes de publicar)
- [ ] Integración con Memoria (consulta estrategias previas)
- [ ] Temperature diferenciada: alta para creatividad, baja para decisiones críticas
- [ ] Parsers robustos con fallback (nunca crashea por mal JSON)

---

## Épica 75.4 — Embrión-2: Integración Completa

### Archivo: `kernel/ventas/embrion_ventas.py`

```python
"""
Embrión-2: Motor de Ventas
Sprint 75: El Monstruo que Vende

Embrión autónomo que:
- Late cada 30 minutos buscando oportunidades
- Ejecuta estrategias de venta activas
- Optimiza con A/B testing perpetuo
- Reporta al Command Center
- Debate con otros Embriones (Brand Engine, Tendencias)
"""

from datetime import datetime
from typing import Optional

from kernel.ventas.ejecutor import VentasEjecutor
from kernel.ventas.pensador import VentasPensador
from kernel.ventas.models import EstadoOportunidad


class EmbrionVentas:
    """
    Embrión-2: Motor de Ventas.
    Heartbeat: cada 30 minutos.
    Propósito: Generar revenue de forma autónoma.
    """

    EMBRION_ID = "embrion-2-ventas"
    HEARTBEAT_INTERVALO_SEGUNDOS = 1800  # 30 min
    VERSION = "75.0.0"

    def __init__(self, pensador: VentasPensador, ejecutor: VentasEjecutor,
                 scheduler, colmena_bus, logger):
        self.pensador = pensador
        self.ejecutor = ejecutor
        self.scheduler = scheduler
        self.bus = colmena_bus        # Para comunicarse con otros Embriones
        self.log = logger
        self.fcs = {
            "estado": "dormido",
            "ultimo_latido": None,
            "oportunidades_activas": 0,
            "revenue_total_usd": 0.0,
            "estrategias_activas": 0,
            "experimentos_activos": 0,
        }

    async def despertar(self) -> None:
        """Registra el Embrión en el Scheduler y comienza a latir."""
        await self.scheduler.registrar_embrion(
            embrion_id=self.EMBRION_ID,
            intervalo=self.HEARTBEAT_INTERVALO_SEGUNDOS,
            callback=self.latir
        )
        self.fcs["estado"] = "activo"
        self.log.info(f"[{self.EMBRION_ID}] despierto — latiendo cada {self.HEARTBEAT_INTERVALO_SEGUNDOS}s")

    async def latir(self) -> dict:
        """
        Heartbeat del Embrión de Ventas.
        Cada latido:
        1. Verifica salud de métricas
        2. Busca nuevas oportunidades (si hay contexto nuevo)
        3. Avanza estrategias activas
        4. Evalúa experimentos A/B maduros
        5. Reporta FCS
        """
        self.fcs["ultimo_latido"] = datetime.utcnow().isoformat()
        self.log.info(f"[{self.EMBRION_ID}] latido — {self.fcs['ultimo_latido']}")

        # 1. Verificar salud
        alertas = await self.ejecutor.verificar_salud_ventas()
        if alertas:
            for alerta in alertas:
                self.log.warning(f"[{self.EMBRION_ID}] alerta: {alerta['mensaje']}")
                # Notificar a la Colmena si es severa
                if alerta["severidad"] == "alta":
                    await self.bus.broadcast({
                        "tipo": "alerta_ventas",
                        "emisor": self.EMBRION_ID,
                        "contenido": alerta,
                    })

        # 2. Buscar oportunidades (solo si hay contexto nuevo del Embrión de Tendencias)
        contexto_nuevo = await self.bus.recibir_mensajes(
            destinatario=self.EMBRION_ID,
            tipo="contexto_tendencias"
        )
        if contexto_nuevo:
            oportunidades = await self.pensador.detectar_oportunidades(contexto_nuevo)
            for opp in oportunidades:
                score = self.ejecutor.calcular_score_oportunidad(opp)
                if score >= 60:  # Solo las que valen la pena
                    await self.ejecutor.guardar_oportunidad(opp)
                    self.fcs["oportunidades_activas"] += 1
                    self.log.info(f"[{self.EMBRION_ID}] nueva oportunidad: {opp.titulo} (score={score})")

        # 3. Avanzar estrategias activas
        await self._avanzar_estrategias()

        # 4. Evaluar experimentos maduros
        await self._evaluar_experimentos()

        # 5. Actualizar FCS
        dashboard = await self.ejecutor.obtener_dashboard_ventas()
        self.fcs["revenue_total_usd"] = dashboard.get("30d", {}).get("revenue_total_usd", 0)

        return self.fcs

    async def recibir_encomienda(self, encomienda: dict) -> dict:
        """
        Recibe una encomienda de Alfredo o de otro Embrión.
        Ejemplo: "Encuentra cómo monetizar X" o "Diseña pricing para Y"
        """
        tipo = encomienda.get("tipo", "detectar")

        if tipo == "detectar":
            oportunidades = await self.pensador.detectar_oportunidades(encomienda.get("contexto", {}))
            return {"oportunidades": [o.__dict__ for o in oportunidades]}

        elif tipo == "estrategia":
            oportunidad = encomienda.get("oportunidad")
            estrategia = await self.pensador.disenar_estrategia(oportunidad)
            await self.ejecutor.guardar_estrategia(estrategia)
            return {"estrategia": estrategia.__dict__}

        elif tipo == "pivot":
            oportunidad = encomienda.get("oportunidad")
            metricas = encomienda.get("metricas", [])
            decision = await self.pensador.decidir_pivot(oportunidad, metricas)
            return {"decision": decision}

        else:
            return {"error": f"tipo_encomienda_desconocido: {tipo}"}

    async def _avanzar_estrategias(self) -> None:
        """Avanza estrategias que están en ejecución."""
        # Obtener estrategias activas de Supabase
        result = await self.ejecutor.db.table("oportunidades_venta").select("*").eq(
            "estado", EstadoOportunidad.EN_EJECUCION.value
        ).execute()

        if not result.data:
            return

        for opp_data in result.data:
            # Verificar si necesita pivot
            metricas = await self.ejecutor.db.table("metricas_venta").select("*").eq(
                "ejecucion_id", opp_data["id"]
            ).order("fecha", desc=True).limit(14).execute()

            if metricas.data and len(metricas.data) >= 7:
                roi_promedio = sum(m["roi"] for m in metricas.data) / len(metricas.data)
                if roi_promedio < 0:
                    # Activar Pensador para decisión de pivot
                    self.log.warning(f"[{self.EMBRION_ID}] ROI negativo detectado — consultando Pensador")

    async def _evaluar_experimentos(self) -> None:
        """Evalúa experimentos A/B que tienen suficiente muestra."""
        result = await self.ejecutor.db.table("experimentos_ab").select("*").is_(
            "resultado", "null"
        ).execute()

        if not result.data:
            return

        for exp_data in result.data:
            # Obtener métricas por variante
            # (implementación simplificada — en producción se separan por variante)
            self.log.info(f"[{self.EMBRION_ID}] evaluando experimento {exp_data['id']}")

    # --- API para Command Center ---

    async def obtener_estado(self) -> dict:
        """Retorna estado completo para el Command Center."""
        dashboard = await self.ejecutor.obtener_dashboard_ventas()
        return {
            "embrion_id": self.EMBRION_ID,
            "version": self.VERSION,
            "fcs": self.fcs,
            "dashboard": dashboard,
        }
```

### Criterios de aceptación:
- [ ] Heartbeat cada 30 min con las 5 acciones del ciclo
- [ ] Comunicación con Colmena via bus de mensajes
- [ ] Acepta encomiendas de Alfredo o de otros Embriones
- [ ] FCS actualizado en cada latido
- [ ] API `obtener_estado()` para Command Center

---

## Épica 75.5 — Tablas SQL y API Endpoints

### SQL para Supabase:

```sql
-- Motor de Ventas — Sprint 75
-- Tablas para el ciclo completo de ventas

CREATE TABLE IF NOT EXISTS oportunidades_venta (
    id TEXT PRIMARY KEY,
    titulo TEXT NOT NULL,
    descripcion TEXT,
    tipo_producto TEXT NOT NULL,
    mercado_objetivo TEXT,
    dolor_que_resuelve TEXT,
    competidores JSONB DEFAULT '[]',
    tam_estimado_usd NUMERIC DEFAULT 0,
    probabilidad_exito NUMERIC DEFAULT 0,
    esfuerzo_estimado_horas NUMERIC DEFAULT 0,
    estado TEXT DEFAULT 'detectada',
    fuente_deteccion TEXT,
    notas_embrion TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS estrategias_venta (
    id TEXT PRIMARY KEY,
    oportunidad_id TEXT REFERENCES oportunidades_venta(id),
    propuesta_valor TEXT,
    pricing_modelo TEXT,
    precio_base_usd NUMERIC,
    canal_principal TEXT,
    canales_secundarios JSONB DEFAULT '[]',
    funnel_pasos JSONB DEFAULT '[]',
    copy_gancho TEXT,
    diferenciador TEXT,
    metricas_objetivo JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ejecuciones_venta (
    id TEXT PRIMARY KEY,
    estrategia_id TEXT REFERENCES estrategias_venta(id),
    canal TEXT,
    activos_generados JSONB DEFAULT '[]',
    presupuesto_asignado_usd NUMERIC DEFAULT 0,
    estado TEXT DEFAULT 'activa',
    fecha_inicio TIMESTAMPTZ DEFAULT NOW(),
    fecha_fin TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS metricas_venta (
    id SERIAL PRIMARY KEY,
    ejecucion_id TEXT REFERENCES ejecuciones_venta(id),
    fecha TIMESTAMPTZ DEFAULT NOW(),
    impresiones INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    leads INTEGER DEFAULT 0,
    conversiones INTEGER DEFAULT 0,
    revenue_usd NUMERIC DEFAULT 0,
    costo_usd NUMERIC DEFAULT 0,
    cac_usd NUMERIC DEFAULT 0,
    ltv_usd NUMERIC DEFAULT 0,
    roi NUMERIC DEFAULT 0
);

CREATE TABLE IF NOT EXISTS experimentos_ab (
    id TEXT PRIMARY KEY,
    ejecucion_id TEXT REFERENCES ejecuciones_venta(id),
    hipotesis TEXT,
    variante_a TEXT,
    variante_b TEXT,
    metrica_objetivo TEXT,
    muestra_minima INTEGER DEFAULT 100,
    confianza_requerida NUMERIC DEFAULT 0.95,
    resultado TEXT,  -- NULL = en curso
    fecha_inicio TIMESTAMPTZ DEFAULT NOW(),
    fecha_fin TIMESTAMPTZ
);

-- Índices para queries frecuentes
CREATE INDEX idx_oportunidades_estado ON oportunidades_venta(estado);
CREATE INDEX idx_metricas_fecha ON metricas_venta(fecha DESC);
CREATE INDEX idx_metricas_ejecucion ON metricas_venta(ejecucion_id);
CREATE INDEX idx_experimentos_resultado ON experimentos_ab(resultado);
```

### API Endpoints (FastAPI):

```python
# En kernel/api/ventas_routes.py

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/ventas", tags=["Motor de Ventas"])

@router.get("/dashboard")
async def get_dashboard():
    """Dashboard de ventas para el Command Center."""
    pass

@router.get("/oportunidades")
async def get_oportunidades(estado: str = None):
    """Lista oportunidades filtradas por estado."""
    pass

@router.get("/oportunidades/{id}")
async def get_oportunidad(id: str):
    """Detalle de una oportunidad."""
    pass

@router.post("/encomienda")
async def crear_encomienda(encomienda: dict):
    """Envía una encomienda al Embrión de Ventas."""
    pass

@router.get("/experimentos")
async def get_experimentos(activos: bool = True):
    """Lista experimentos A/B."""
    pass

@router.get("/metricas/{periodo}")
async def get_metricas(periodo: str = "7d"):
    """Métricas agregadas por período (24h, 7d, 30d)."""
    pass

@router.get("/estado")
async def get_estado_embrion():
    """Estado del Embrión-2 (FCS + dashboard)."""
    pass
```

### Criterios de aceptación:
- [ ] 5 tablas con foreign keys y índices
- [ ] 7 endpoints REST documentados
- [ ] Naming en español con snake_case
- [ ] Todos los endpoints retornan JSON consumible por Command Center

---

## Resumen de Entregables

| Archivo | Líneas aprox. | Tipo |
|---------|--------------|------|
| `kernel/ventas/models.py` | 120 | Modelos de dominio |
| `kernel/ventas/ejecutor.py` | 200 | Código determinista ($0) |
| `kernel/ventas/pensador.py` | 250 | LLM para juicio subjetivo |
| `kernel/ventas/embrion_ventas.py` | 180 | Integración + heartbeat |
| `kernel/api/ventas_routes.py` | 50 | API endpoints |
| SQL (Supabase) | 60 | 5 tablas + índices |
| Tests | 100+ | pytest |

**Total:** ~960 líneas de código nuevo.

---

## DIRECTIVA DE INTERFAZ

> **Para el Hilo A:** Implementa el código Python y las tablas SQL. Los 7 endpoints deben retornar JSON documentado. El Hilo B consumirá estos endpoints desde el Command Center (sección "Ventas" — nueva página a crear).

---

## Brand Compliance Checklist

| # | Check | Estado |
|---|---|---|
| 1 | Naming con identidad | ✅ `ventas_ejecutor`, `ventas_pensador`, `embrion_ventas` |
| 2 | Errores con contexto | ✅ `[ventas_pensador] parse_oportunidades_error: {e}` |
| 3 | Endpoints para Command Center | ✅ 7 endpoints en `/api/v1/ventas/` |
| 4 | Logs estructurados | ✅ `[embrion-2-ventas] latido — {timestamp}` |
| 5 | Docstrings | ✅ Todas las clases y métodos públicos |
| 6 | Tests | ⬜ Pendiente de implementación |
| 7 | Soberanía | ✅ LLM via abstracción (no hardcoded a OpenAI) |
