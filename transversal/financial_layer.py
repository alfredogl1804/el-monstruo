"""
financial_layer.py — Capa Financiera Transversal
=================================================
Capa Transversal #3 del Objetivo #9.
Dashboard financiero inyectado en cada proyecto.

Componentes:
  1. UnitEconomics: CAC, LTV, ARPU, churn, margins, payback, LTV/CAC
  2. MonthlySnapshot: revenue, costs, users por mes
  3. FinancialLayer: proyecciones, runway, alertas de burn rate
  4. Integración con Stripe para revenue real

Sprint 57 — "Las Capas Transversales"
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("financial_layer")


# ── Data models ───────────────────────────────────────────────────────────────

@dataclass
class UnitEconomics:
    """Métricas de unit economics para un proyecto."""
    cac: float = 0.0           # Customer Acquisition Cost
    ltv: float = 0.0           # Lifetime Value
    arpu: float = 0.0          # Average Revenue Per User
    churn_rate: float = 0.0    # Monthly churn rate (0.0-1.0)
    gross_margin: float = 0.0  # Gross margin (0.0-1.0)
    payback_months: float = 0.0  # Months to recover CAC
    ltv_cac_ratio: float = 0.0   # LTV/CAC ratio

    def calculate_derived(self) -> None:
        """Calcular métricas derivadas."""
        if self.cac > 0:
            self.ltv_cac_ratio = self.ltv / self.cac if self.ltv > 0 else 0
            self.payback_months = self.cac / self.arpu if self.arpu > 0 else 0
        if self.churn_rate > 0 and self.churn_rate < 1:
            self.ltv = self.arpu / self.churn_rate

    @property
    def health_grade(self) -> str:
        """Evaluar salud financiera basada en LTV/CAC ratio."""
        if self.ltv_cac_ratio >= 3.0:
            return "excellent"
        elif self.ltv_cac_ratio >= 2.0:
            return "good"
        elif self.ltv_cac_ratio >= 1.0:
            return "warning"
        else:
            return "critical"


@dataclass
class MonthlySnapshot:
    """Snapshot financiero mensual."""
    month: str  # YYYY-MM
    revenue: float = 0.0
    costs: float = 0.0
    users: int = 0
    new_users: int = 0
    churned_users: int = 0

    @property
    def net_income(self) -> float:
        return self.revenue - self.costs

    @property
    def burn_rate(self) -> float:
        """Monthly burn rate (negative = burning cash)."""
        return self.revenue - self.costs


# ── FinancialLayer ────────────────────────────────────────────────────────────

class FinancialLayer:
    """Capa financiera transversal — dashboard para cada proyecto."""

    # Alertas de burn rate
    BURN_RATE_THRESHOLDS = {
        "critical": 3,   # < 3 meses de runway
        "warning": 6,    # < 6 meses de runway
        "healthy": 12,   # >= 12 meses de runway
    }

    def __init__(self, project_id: str, db=None):
        self._project_id = project_id
        self._db = db
        self._snapshots: list[MonthlySnapshot] = []
        self._unit_economics = UnitEconomics()

    async def setup_for_project(self, initial_data: dict = None) -> dict:
        """Configurar dashboard financiero para un proyecto."""
        if initial_data:
            self._unit_economics = UnitEconomics(
                cac=initial_data.get("cac", 0),
                arpu=initial_data.get("arpu", 0),
                churn_rate=initial_data.get("churn_rate", 0.05),
                gross_margin=initial_data.get("gross_margin", 0.70),
            )
            self._unit_economics.calculate_derived()

        return {
            "project_id": self._project_id,
            "unit_economics": {
                "cac": self._unit_economics.cac,
                "ltv": self._unit_economics.ltv,
                "ltv_cac_ratio": self._unit_economics.ltv_cac_ratio,
                "health_grade": self._unit_economics.health_grade,
            },
            "status": "configured",
        }

    def record_monthly_snapshot(self, snapshot: MonthlySnapshot) -> None:
        """Registrar snapshot financiero mensual."""
        self._snapshots.append(snapshot)
        logger.info(
            "monthly_snapshot_recorded",
            month=snapshot.month,
            revenue=snapshot.revenue,
            burn=snapshot.burn_rate,
        )

    def project_revenue(self, months_ahead: int = 12, growth_rate: float = 0.10) -> list[dict]:
        """Proyectar revenue futuro basado en growth rate."""
        if not self._snapshots:
            return [{"month": i, "projected_revenue": 0} for i in range(months_ahead)]

        last = self._snapshots[-1]
        projections = []
        current_revenue = last.revenue
        current_users = last.users

        for i in range(1, months_ahead + 1):
            current_users = int(
                current_users * (1 + growth_rate) * (1 - self._unit_economics.churn_rate)
            )
            current_revenue = current_users * self._unit_economics.arpu

            projections.append({
                "month": i,
                "projected_users": current_users,
                "projected_revenue": round(current_revenue, 2),
                "projected_costs": round(last.costs * (1 + 0.03 * i), 2),  # 3% cost growth
            })

        return projections

    def calculate_runway(self, cash_balance: float) -> dict:
        """Calcular runway basado en burn rate actual."""
        if not self._snapshots:
            return {"runway_months": "unknown", "status": "no_data"}

        last = self._snapshots[-1]
        monthly_burn = abs(last.burn_rate) if last.burn_rate < 0 else 0

        if monthly_burn == 0:
            return {"runway_months": "infinite", "status": "profitable"}

        runway = cash_balance / monthly_burn

        if runway < self.BURN_RATE_THRESHOLDS["critical"]:
            status = "critical"
        elif runway < self.BURN_RATE_THRESHOLDS["warning"]:
            status = "warning"
        else:
            status = "healthy"

        return {
            "runway_months": round(runway, 1),
            "monthly_burn": round(monthly_burn, 2),
            "cash_balance": cash_balance,
            "status": status,
            "alert": (
                f"ALERT: Only {runway:.1f} months of runway!" if status == "critical" else None
            ),
        }

    def get_financial_report(self) -> dict:
        """Generar reporte financiero completo."""
        return {
            "project_id": self._project_id,
            "unit_economics": {
                "cac": self._unit_economics.cac,
                "ltv": self._unit_economics.ltv,
                "arpu": self._unit_economics.arpu,
                "churn_rate": self._unit_economics.churn_rate,
                "gross_margin": self._unit_economics.gross_margin,
                "ltv_cac_ratio": self._unit_economics.ltv_cac_ratio,
                "payback_months": self._unit_economics.payback_months,
                "health_grade": self._unit_economics.health_grade,
            },
            "snapshots": len(self._snapshots),
            "latest_snapshot": self._snapshots[-1].__dict__ if self._snapshots else None,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_benchmarks_by_vertical(self, vertical: str) -> dict:
        """Retornar benchmarks de unit economics por vertical."""
        benchmarks = {
            "saas": {
                "ltv_cac_ratio": {"good": 3.0, "excellent": 5.0},
                "gross_margin": {"good": 0.70, "excellent": 0.85},
                "churn_rate": {"good": 0.05, "excellent": 0.02},
                "payback_months": {"good": 12, "excellent": 6},
            },
            "ecommerce": {
                "ltv_cac_ratio": {"good": 2.0, "excellent": 4.0},
                "gross_margin": {"good": 0.40, "excellent": 0.60},
                "churn_rate": {"good": 0.20, "excellent": 0.10},
                "payback_months": {"good": 6, "excellent": 3},
            },
            "marketplace": {
                "ltv_cac_ratio": {"good": 4.0, "excellent": 8.0},
                "gross_margin": {"good": 0.80, "excellent": 0.95},
                "churn_rate": {"good": 0.10, "excellent": 0.05},
                "payback_months": {"good": 18, "excellent": 9},
            },
        }
        return benchmarks.get(vertical.lower(), benchmarks["saas"])


# ── Factory ───────────────────────────────────────────────────────────────────

def create_financial_layer(project_id: str, db=None) -> FinancialLayer:
    """Factory para crear un FinancialLayer para un proyecto."""
    return FinancialLayer(project_id=project_id, db=db)
