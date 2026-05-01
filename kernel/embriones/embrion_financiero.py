"""
El Monstruo — Embrión-Financiero (Sprint 60)
=============================================
6to Embrión especializado. Dominio: Finanzas, unit economics, runway.

Hereda: EmbrionLoop (Sprint 54)
Hermanos: Ventas(57), Técnico(58), Vigía(58), Creativo(59), Estratega(59)
Herramienta: FinancialLayer (Sprint 57.4)

Responsabilidades:
- Calcular y monitorear unit economics (CAC, LTV, LTV/CAC ratio)
- Alertar cuando runway < 3 meses
- Generar snapshots mensuales para el board
- Calibrar el CausalSimulatorV2 con datos reales

Objetivo cubierto: #9 Capa 6 — Finanzas Transversal
Sprint 60 — 2026-05-01

Soberanía: Funciona sin Supabase — persiste en memoria si no hay DB.
           Alternativa: CSV local para snapshots financieros.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import structlog

logger = structlog.get_logger("monstruo.embrion.financiero")


# ── Errores con identidad ────────────────────────────────────────────────────

class EmbrionFinancieroError(Exception):
    """Error base del Embrión-Financiero."""


EMBRION_FINANCIERO_SIN_DATOS = (
    "EMBRION_FINANCIERO_SIN_DATOS: "
    "No hay datos financieros disponibles para calcular unit economics. "
    "Sugerencia: Llama update_financials() con los datos actuales del proyecto."
)

EMBRION_FINANCIERO_RUNWAY_CRITICO = (
    "EMBRION_FINANCIERO_RUNWAY_CRITICO: "
    "Runway del proyecto '{proyecto}' es {meses:.1f} meses — por debajo del umbral de 3 meses. "
    "Acción requerida: Reducir burn rate o aumentar ingresos inmediatamente."
)


# ── Dataclasses ──────────────────────────────────────────────────────────────

@dataclass
class UnitEconomics:
    """
    Unit economics de un proyecto.

    Args:
        proyecto_id: ID del proyecto.
        mrr: Monthly Recurring Revenue en USD.
        clientes: Número de clientes activos.
        cac: Customer Acquisition Cost en USD.
        ltv: Lifetime Value en USD.
        ltv_cac_ratio: Ratio LTV/CAC (>3 es saludable).
        churn_rate: Tasa de churn mensual (0.0 a 1.0).
        burn_rate: Burn rate mensual en USD.
        cash_disponible: Cash disponible en USD.
        runway_meses: Meses de runway con el cash actual.
        calculado_en: ISO timestamp del cálculo.
    """
    proyecto_id: str
    mrr: float
    clientes: int
    cac: float
    ltv: float
    ltv_cac_ratio: float
    churn_rate: float
    burn_rate: float
    cash_disponible: float
    runway_meses: float
    calculado_en: str

    @property
    def es_saludable(self) -> bool:
        """True si los unit economics son saludables."""
        return (
            self.ltv_cac_ratio >= 3.0
            and self.runway_meses >= 6.0
            and self.churn_rate <= 0.05
        )

    def to_dict(self) -> dict:
        """Serializar para el Command Center."""
        return {
            "proyecto_id": self.proyecto_id,
            "mrr": round(self.mrr, 2),
            "clientes": self.clientes,
            "cac": round(self.cac, 2),
            "ltv": round(self.ltv, 2),
            "ltv_cac_ratio": round(self.ltv_cac_ratio, 2),
            "churn_rate": round(self.churn_rate, 4),
            "burn_rate": round(self.burn_rate, 2),
            "cash_disponible": round(self.cash_disponible, 2),
            "runway_meses": round(self.runway_meses, 1),
            "es_saludable": self.es_saludable,
            "calculado_en": self.calculado_en,
        }


@dataclass
class EmbrionFinanciero:
    """
    Embrión especializado en finanzas y unit economics.

    Monitorea la salud financiera de todos los proyectos activos,
    alerta sobre runway crítico, y calibra el CausalSimulatorV2
    con datos reales para predicciones más precisas.

    Args:
        _sabios: Interfaz a los Sabios para análisis financiero (opcional).
        _supabase: Cliente Supabase para persistencia (opcional).
        _simulator_v2: CausalSimulatorV2 para calibración (opcional).
        budget_daily_usd: Presupuesto diario máximo en USD.

    Soberanía: Funciona sin Sabios y sin Supabase.
               Alternativa: CSV local para snapshots, heurísticas para análisis.
    """

    _sabios: Optional[object] = field(default=None, repr=False)
    _supabase: Optional[object] = field(default=None, repr=False)
    _simulator_v2: Optional[object] = field(default=None, repr=False)
    budget_daily_usd: float = 0.5
    _spent_today: float = 0.0
    _unit_economics_cache: dict[str, UnitEconomics] = field(default_factory=dict)
    _ciclos_ejecutados: int = 0
    _alertas_emitidas: int = 0

    DEFAULT_TASKS = {
        "daily_financial_review": {
            "description": "Revisar unit economics de todos los proyectos activos",
            "interval_hours": 24,
            "handler": "run_daily_financial_review",
        },
        "runway_monitor": {
            "description": "Monitorear runway y alertar si < 3 meses",
            "interval_hours": 6,
            "handler": "monitor_runway",
        },
        "monthly_snapshot": {
            "description": "Generar snapshot financiero mensual para el board",
            "interval_hours": 720,
            "handler": "generate_monthly_snapshot",
        },
        "simulator_calibration": {
            "description": "Calibrar CausalSimulatorV2 con datos financieros reales",
            "interval_hours": 168,  # Semanal
            "handler": "calibrate_simulator",
        },
    }

    def calculate_unit_economics(
        self,
        proyecto_id: str,
        mrr: float,
        clientes: int,
        total_marketing_spend: float,
        nuevos_clientes_mes: int,
        avg_contract_months: float = 24.0,
        monthly_churn_rate: float = 0.05,
        burn_rate: float = 5000.0,
        cash_disponible: float = 60000.0,
    ) -> UnitEconomics:
        """
        Calcular unit economics completos de un proyecto.

        Args:
            proyecto_id: ID del proyecto.
            mrr: Monthly Recurring Revenue en USD.
            clientes: Número de clientes activos.
            total_marketing_spend: Gasto total en marketing este mes en USD.
            nuevos_clientes_mes: Nuevos clientes adquiridos este mes.
            avg_contract_months: Duración promedio del contrato en meses.
            monthly_churn_rate: Tasa de churn mensual (0.0 a 1.0).
            burn_rate: Burn rate mensual en USD.
            cash_disponible: Cash disponible en USD.

        Returns:
            UnitEconomics calculados.
        """
        arpu = mrr / max(1, clientes)
        cac = total_marketing_spend / max(1, nuevos_clientes_mes)
        ltv = arpu * avg_contract_months * (1 - monthly_churn_rate)
        ltv_cac_ratio = ltv / max(1, cac)
        runway_meses = cash_disponible / max(1, burn_rate)

        ue = UnitEconomics(
            proyecto_id=proyecto_id,
            mrr=mrr,
            clientes=clientes,
            cac=cac,
            ltv=ltv,
            ltv_cac_ratio=ltv_cac_ratio,
            churn_rate=monthly_churn_rate,
            burn_rate=burn_rate,
            cash_disponible=cash_disponible,
            runway_meses=runway_meses,
            calculado_en=datetime.now(timezone.utc).isoformat(),
        )

        self._unit_economics_cache[proyecto_id] = ue

        if runway_meses < 3:
            logger.error(
                "runway_critico",
                proyecto=proyecto_id,
                runway_meses=round(runway_meses, 1),
                accion_requerida="Reducir burn rate o aumentar ingresos",
            )
            self._alertas_emitidas += 1

        logger.info(
            "unit_economics_calculados",
            proyecto=proyecto_id,
            mrr=round(mrr, 2),
            ltv_cac=round(ltv_cac_ratio, 2),
            runway_meses=round(runway_meses, 1),
            saludable=ue.es_saludable,
        )

        return ue

    async def run_daily_financial_review(self) -> dict:
        """
        Tarea autónoma: revisar unit economics de todos los proyectos.

        Returns:
            Dict con resumen del review diario.
        """
        self._ciclos_ejecutados += 1
        proyectos_saludables = sum(1 for ue in self._unit_economics_cache.values() if ue.es_saludable)
        proyectos_criticos = [
            pid for pid, ue in self._unit_economics_cache.items()
            if ue.runway_meses < 3
        ]

        result = {
            "ciclo": self._ciclos_ejecutados,
            "proyectos_monitoreados": len(self._unit_economics_cache),
            "proyectos_saludables": proyectos_saludables,
            "proyectos_criticos": proyectos_criticos,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if proyectos_criticos and self._sabios:
            try:
                prompt = f"""Financial emergency analysis:
Projects with critical runway (<3 months): {proyectos_criticos}
Unit economics data: {json.dumps({pid: self._unit_economics_cache[pid].to_dict() for pid in proyectos_criticos}, indent=2)}

Provide 3 specific, actionable recommendations to extend runway.
Focus on: revenue acceleration, cost reduction, and pricing optimization.
Respond in JSON: {{"recommendations": ["...", "...", "..."]}}"""

                response = await self._sabios.ask(prompt)
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0]
                recommendations = json.loads(response.strip())
                result["recomendaciones_emergencia"] = recommendations.get("recommendations", [])
            except Exception as e:
                logger.warning("sabios_financial_analysis_fallido", error=str(e))

        return result

    async def monitor_runway(self) -> list[dict]:
        """
        Tarea autónoma: monitorear runway y emitir alertas.

        Returns:
            Lista de alertas emitidas.
        """
        alertas = []
        for pid, ue in self._unit_economics_cache.items():
            if ue.runway_meses < 3:
                alertas.append({
                    "tipo": "RUNWAY_CRITICO",
                    "proyecto": pid,
                    "runway_meses": round(ue.runway_meses, 1),
                    "burn_rate": round(ue.burn_rate, 2),
                    "cash_disponible": round(ue.cash_disponible, 2),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                self._alertas_emitidas += 1

        if alertas:
            logger.warning("alertas_runway_emitidas", cantidad=len(alertas))

        return alertas

    def generate_monthly_snapshot(self) -> dict:
        """
        Generar snapshot financiero mensual para el board.

        Returns:
            Dict con resumen financiero del mes.
        """
        total_mrr = sum(ue.mrr for ue in self._unit_economics_cache.values())
        total_clientes = sum(ue.clientes for ue in self._unit_economics_cache.values())
        avg_ltv_cac = (
            sum(ue.ltv_cac_ratio for ue in self._unit_economics_cache.values())
            / max(1, len(self._unit_economics_cache))
        )

        snapshot = {
            "periodo": datetime.now(timezone.utc).strftime("%Y-%m"),
            "total_mrr_usd": round(total_mrr, 2),
            "total_clientes": total_clientes,
            "proyectos_activos": len(self._unit_economics_cache),
            "avg_ltv_cac_ratio": round(avg_ltv_cac, 2),
            "proyectos_saludables": sum(1 for ue in self._unit_economics_cache.values() if ue.es_saludable),
            "proyectos_en_riesgo": sum(1 for ue in self._unit_economics_cache.values() if ue.runway_meses < 6),
            "alertas_emitidas_ciclo": self._alertas_emitidas,
            "generado_en": datetime.now(timezone.utc).isoformat(),
        }

        logger.info("monthly_snapshot_generado", mrr_total=round(total_mrr, 2), clientes=total_clientes)
        return snapshot

    def calibrate_simulator(self) -> dict:
        """
        Calibrar CausalSimulatorV2 con los datos financieros reales actuales.

        Returns:
            Dict con confirmación de calibración.
        """
        if not self._simulator_v2:
            return {"calibrado": False, "razon": "CausalSimulatorV2 no disponible"}

        if not self._unit_economics_cache:
            return {"calibrado": False, "razon": "Sin datos financieros en caché"}

        # Usar el proyecto con más MRR como referencia
        proyecto_ref = max(self._unit_economics_cache.values(), key=lambda ue: ue.mrr)

        financial_data = {
            "mrr_actual": proyecto_ref.mrr,
            "clientes_actuales": proyecto_ref.clientes,
            "cac": proyecto_ref.cac,
            "ltv": proyecto_ref.ltv,
            "burn_rate": proyecto_ref.burn_rate,
            "runway_meses": proyecto_ref.runway_meses,
        }

        self._simulator_v2.calibrate_from_financials(financial_data)

        logger.info(
            "simulator_calibrado_desde_financiero",
            proyecto_ref=proyecto_ref.proyecto_id,
            mrr=round(proyecto_ref.mrr, 2),
        )

        return {
            "calibrado": True,
            "proyecto_referencia": proyecto_ref.proyecto_id,
            "mrr_usado": round(proyecto_ref.mrr, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def to_dict(self) -> dict:
        """
        Serializar estado para el Command Center.

        Returns:
            Dict con estado del Embrión-Financiero.
        """
        return {
            "modulo": "embrion_financiero",
            "sprint": "60.4",
            "objetivo": "Obj #9 Capa 6 — Finanzas Transversal",
            "ciclos_ejecutados": self._ciclos_ejecutados,
            "alertas_emitidas": self._alertas_emitidas,
            "proyectos_monitoreados": len(self._unit_economics_cache),
            "proyectos_saludables": sum(1 for ue in self._unit_economics_cache.values() if ue.es_saludable),
            "total_mrr_usd": round(sum(ue.mrr for ue in self._unit_economics_cache.values()), 2),
            "simulator_calibrado": self._simulator_v2 is not None,
            "unit_economics": {
                pid: ue.to_dict()
                for pid, ue in list(self._unit_economics_cache.items())[:5]
            },
        }


# ── Singleton ────────────────────────────────────────────────────────────────

_embrion_financiero: Optional[EmbrionFinanciero] = None


def get_embrion_financiero() -> Optional[EmbrionFinanciero]:
    """Obtener la instancia singleton del EmbrionFinanciero."""
    return _embrion_financiero


def init_embrion_financiero(sabios=None, supabase=None, simulator_v2=None) -> EmbrionFinanciero:
    """
    Inicializar el EmbrionFinanciero como singleton.

    Args:
        sabios: Interfaz a los Sabios para análisis (opcional).
        supabase: Cliente Supabase para persistencia (opcional).
        simulator_v2: CausalSimulatorV2 para calibración (opcional).

    Returns:
        Instancia inicializada del EmbrionFinanciero.
    """
    global _embrion_financiero
    _embrion_financiero = EmbrionFinanciero(
        _sabios=sabios,
        _supabase=supabase,
        _simulator_v2=simulator_v2,
    )
    logger.info("embrion_financiero_inicializado", con_simulator=simulator_v2 is not None)
    return _embrion_financiero
