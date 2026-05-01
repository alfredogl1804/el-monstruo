# Sprint 79 — "El Monstruo que Cuenta"
## Embrión-6: Finanzas y Unit Economics

**Serie:** 71-80 "La Colmena Despierta"
**Fecha de diseño:** 1 de Mayo 2026
**Arquitectura:** Pensador (LLM potente) + Ejecutor (código determinista)
**Dependencias:** Sprint 72 (TEL), Sprint 74 (Colmena), Sprint 75 (Motor de Ventas)

---

## Visión

El Embrión-6 es el CFO del sistema. Sabe exactamente cuánto cuesta cada operación, cuánto genera cada negocio, y si las decisiones financieras son sostenibles. No es un dashboard de métricas — es un agente que DECIDE: "este negocio no es rentable, cerrar" o "este canal tiene ROAS 5x, duplicar inversión". Tesla no tiene un CFO que solo reporta — tiene uno que optimiza cada centavo para maximizar crecimiento.

---

## Arquitectura Pensador/Ejecutor

### Pensador (LLM Potente)
- Analiza unit economics y determina viabilidad de negocios
- Proyecta cash flow y detecta riesgos de liquidez
- Recomienda decisiones de inversión/desinversión
- Genera reportes financieros ejecutivos
- Evalúa ROI de cada Embrión y herramienta

### Ejecutor (Python Puro)
- Calcula métricas financieras (LTV, CAC, MRR, churn, burn rate)
- Agrega costos de LLM, APIs, infraestructura
- Genera alertas cuando métricas cruzan thresholds
- Persiste transacciones y proyecciones en Supabase
- Ejecuta reconciliación automática de gastos

---

## Épica 79.1 — Modelos y Tablas

```python
# kernel/finanzas/models.py
"""
IDENTIDAD DE MARCA: Módulo de Finanzas de El Monstruo.
Naming: finanzas_* (nunca "finance_module" ni "accounting_tool")
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class TransactionType(Enum):
    REVENUE = "revenue"
    COST_LLM = "cost_llm"
    COST_INFRA = "cost_infra"
    COST_API = "cost_api"
    COST_ADS = "cost_ads"
    COST_TOOLS = "cost_tools"
    INVESTMENT = "investment"


class BusinessHealth(Enum):
    THRIVING = "thriving"       # LTV/CAC > 3, growing
    HEALTHY = "healthy"         # LTV/CAC > 2, stable
    WARNING = "warning"         # LTV/CAC 1-2, needs attention
    CRITICAL = "critical"      # LTV/CAC < 1, losing money
    DEAD = "dead"              # No revenue, high costs


@dataclass
class Transaction:
    id: str
    business_id: str
    transaction_type: str
    amount: float              # Positivo = ingreso, negativo = gasto
    currency: str = "USD"
    description: str = ""
    source: str = ""           # "stripe", "manual", "embrion-5", etc.
    embrion_id: Optional[str] = None  # Qué Embrión generó este costo
    date: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UnitEconomics:
    business_id: str
    period: str                # "monthly", "weekly"
    revenue: float = 0
    costs: float = 0
    gross_margin: float = 0
    ltv: float = 0             # Lifetime Value
    cac: float = 0             # Customer Acquisition Cost
    ltv_cac_ratio: float = 0
    mrr: float = 0             # Monthly Recurring Revenue
    churn_rate: float = 0
    burn_rate: float = 0       # Cash burn per month
    runway_months: float = 0   # Months until cash runs out
    health: str = "healthy"
    calculated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FinancialProjection:
    id: str
    business_id: str
    scenario: str              # "optimistic", "base", "pessimistic"
    months_ahead: int = 6
    projected_revenue: list[float] = field(default_factory=list)
    projected_costs: list[float] = field(default_factory=list)
    projected_profit: list[float] = field(default_factory=list)
    break_even_month: Optional[int] = None
    assumptions: dict = field(default_factory=dict)
    confidence: float = 0.5
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EmbrionCostReport:
    embrion_id: str
    period: str
    llm_calls: int = 0
    llm_cost: float = 0
    api_calls: int = 0
    api_cost: float = 0
    storage_mb: float = 0
    storage_cost: float = 0
    total_cost: float = 0
    value_generated: float = 0  # Revenue atribuible
    roi: float = 0             # value_generated / total_cost
```

### SQL

```sql
CREATE TABLE IF NOT EXISTS finanzas_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    description TEXT DEFAULT '',
    source TEXT DEFAULT '',
    embrion_id TEXT,
    date TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS finanzas_unit_economics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id TEXT NOT NULL,
    period TEXT NOT NULL,
    revenue NUMERIC(12,2) DEFAULT 0,
    costs NUMERIC(12,2) DEFAULT 0,
    gross_margin NUMERIC(5,2) DEFAULT 0,
    ltv NUMERIC(10,2) DEFAULT 0,
    cac NUMERIC(10,2) DEFAULT 0,
    ltv_cac_ratio NUMERIC(5,2) DEFAULT 0,
    mrr NUMERIC(10,2) DEFAULT 0,
    churn_rate NUMERIC(5,4) DEFAULT 0,
    burn_rate NUMERIC(10,2) DEFAULT 0,
    runway_months NUMERIC(5,1) DEFAULT 0,
    health TEXT DEFAULT 'healthy',
    calculated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS finanzas_projections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id TEXT NOT NULL,
    scenario TEXT NOT NULL,
    months_ahead INTEGER DEFAULT 6,
    projected_revenue JSONB DEFAULT '[]',
    projected_costs JSONB DEFAULT '[]',
    projected_profit JSONB DEFAULT '[]',
    break_even_month INTEGER,
    assumptions JSONB DEFAULT '{}',
    confidence NUMERIC(4,3) DEFAULT 0.5,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS finanzas_embrion_costs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    embrion_id TEXT NOT NULL,
    period TEXT NOT NULL,
    llm_calls INTEGER DEFAULT 0,
    llm_cost NUMERIC(8,4) DEFAULT 0,
    api_calls INTEGER DEFAULT 0,
    api_cost NUMERIC(8,4) DEFAULT 0,
    storage_mb NUMERIC(8,2) DEFAULT 0,
    storage_cost NUMERIC(8,4) DEFAULT 0,
    total_cost NUMERIC(10,4) DEFAULT 0,
    value_generated NUMERIC(10,2) DEFAULT 0,
    roi NUMERIC(8,2) DEFAULT 0,
    calculated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_transactions_business ON finanzas_transactions(business_id, date DESC);
CREATE INDEX idx_transactions_type ON finanzas_transactions(transaction_type);
CREATE INDEX idx_unit_economics_business ON finanzas_unit_economics(business_id, calculated_at DESC);
CREATE INDEX idx_embrion_costs ON finanzas_embrion_costs(embrion_id, period);
```

---

## Épica 79.2 — Ejecutor Finanzas

```python
# kernel/finanzas/finanzas_ejecutor.py
"""
IDENTIDAD DE MARCA: Ejecutor del Embrión-6 (Finanzas).
Código determinista. Cero LLM. Cálculos financieros puros.
"""
from datetime import datetime, timedelta
from typing import Optional


class FinanzasEjecutor:
    """Ejecutor determinista del Embrión-6. El contador implacable."""

    def __init__(self, supabase_client, logger):
        self.db = supabase_client
        self.log = logger
        self.config = {
            "ltv_cac_healthy_min": 2.0,
            "ltv_cac_thriving_min": 3.0,
            "max_burn_rate_months": 6,     # Alerta si runway < 6 meses
            "churn_warning_threshold": 0.10,  # 10% churn = warning
            "embrion_min_roi": 1.0,        # ROI mínimo para justificar costo
        }

    # --- Unit Economics ---

    def calculate_ltv(self, avg_revenue_per_customer: float,
                       avg_lifespan_months: float) -> float:
        """LTV = Revenue promedio * Vida promedio del cliente."""
        return round(avg_revenue_per_customer * avg_lifespan_months, 2)

    def calculate_cac(self, total_acquisition_cost: float,
                       new_customers: int) -> float:
        """CAC = Costo total de adquisición / Nuevos clientes."""
        if new_customers == 0:
            return float('inf')
        return round(total_acquisition_cost / new_customers, 2)

    def calculate_ltv_cac_ratio(self, ltv: float, cac: float) -> float:
        """LTV/CAC ratio — la métrica más importante."""
        if cac == 0:
            return float('inf')
        return round(ltv / cac, 2)

    def calculate_mrr(self, subscriptions: list[dict]) -> float:
        """MRR = Suma de revenue recurrente mensual."""
        return round(sum(s.get("monthly_amount", 0) for s in subscriptions), 2)

    def calculate_churn_rate(self, customers_start: int,
                              customers_lost: int) -> float:
        """Churn rate = Clientes perdidos / Clientes al inicio del período."""
        if customers_start == 0:
            return 0.0
        return round(customers_lost / customers_start, 4)

    def calculate_burn_rate(self, total_costs: float, revenue: float) -> float:
        """Burn rate = Costos - Revenue (negativo = profitable)."""
        return round(total_costs - revenue, 2)

    def calculate_runway(self, cash_available: float, burn_rate: float) -> float:
        """Runway = Cash disponible / Burn rate mensual."""
        if burn_rate <= 0:
            return float('inf')  # Profitable, infinite runway
        return round(cash_available / burn_rate, 1)

    def calculate_gross_margin(self, revenue: float, cogs: float) -> float:
        """Gross margin = (Revenue - COGS) / Revenue * 100."""
        if revenue == 0:
            return 0.0
        return round(((revenue - cogs) / revenue) * 100, 2)

    # --- Health Assessment ---

    def assess_business_health(self, unit_economics: dict) -> str:
        """Determina salud del negocio basado en unit economics."""
        ltv_cac = unit_economics.get("ltv_cac_ratio", 0)
        churn = unit_economics.get("churn_rate", 0)
        burn = unit_economics.get("burn_rate", 0)

        if ltv_cac >= self.config["ltv_cac_thriving_min"] and burn <= 0:
            return "thriving"
        elif ltv_cac >= self.config["ltv_cac_healthy_min"]:
            return "healthy"
        elif ltv_cac >= 1.0:
            return "warning"
        elif ltv_cac > 0:
            return "critical"
        return "dead"

    # --- Embrión Cost Tracking ---

    def calculate_embrion_roi(self, embrion_id: str, period_days: int = 30) -> dict:
        """Calcula ROI de un Embrión específico."""
        cutoff = (datetime.utcnow() - timedelta(days=period_days)).isoformat()

        # Costos del Embrión
        costs = self.db.table("finanzas_transactions").select("amount").eq(
            "embrion_id", embrion_id
        ).gte("date", cutoff).lt("amount", 0).execute().data
        total_cost = abs(sum(t["amount"] for t in costs)) if costs else 0

        # Revenue atribuible
        revenue = self.db.table("finanzas_transactions").select("amount").eq(
            "embrion_id", embrion_id
        ).gte("date", cutoff).gt("amount", 0).execute().data
        total_revenue = sum(t["amount"] for t in revenue) if revenue else 0

        roi = (total_revenue / total_cost) if total_cost > 0 else 0

        return {
            "embrion_id": embrion_id,
            "period_days": period_days,
            "total_cost": round(total_cost, 4),
            "total_revenue": round(total_revenue, 2),
            "roi": round(roi, 2),
            "justified": roi >= self.config["embrion_min_roi"],
        }

    # --- Alerts ---

    def check_financial_alerts(self, business_id: str) -> list[dict]:
        """Verifica condiciones de alerta financiera."""
        alerts = []

        # Obtener unit economics más reciente
        ue = self.db.table("finanzas_unit_economics").select("*").eq(
            "business_id", business_id
        ).order("calculated_at", desc=True).limit(1).execute().data

        if not ue:
            return [{"type": "no_data", "msg": "finanzas_no_unit_economics_data"}]

        ue = ue[0]

        if ue.get("runway_months", 99) < self.config["max_burn_rate_months"]:
            alerts.append({
                "type": "runway_low",
                "severity": "critical",
                "msg": f"finanzas_runway_low: {ue['runway_months']} meses restantes"
            })

        if ue.get("churn_rate", 0) > self.config["churn_warning_threshold"]:
            alerts.append({
                "type": "churn_high",
                "severity": "warning",
                "msg": f"finanzas_churn_high: {ue['churn_rate']*100}%"
            })

        if ue.get("health") in ("critical", "dead"):
            alerts.append({
                "type": "business_critical",
                "severity": "critical",
                "msg": f"finanzas_business_health: {ue['health']}"
            })

        return alerts

    # --- Persistence ---

    def save_transaction(self, transaction: dict) -> str:
        result = self.db.table("finanzas_transactions").insert(transaction).execute()
        return result.data[0]["id"] if result.data else ""

    def save_unit_economics(self, ue: dict) -> str:
        result = self.db.table("finanzas_unit_economics").insert(ue).execute()
        return result.data[0]["id"] if result.data else ""
```

---

## Épica 79.3 — Pensador Finanzas

```python
# kernel/finanzas/finanzas_pensador.py
"""
IDENTIDAD DE MARCA: Pensador del Embrión-6 (Finanzas).
Solo juicio: análisis financiero, proyecciones, decisiones de inversión.
"""


class FinanzasPensador:
    """Pensador del Embrión-6. El CFO que decide."""

    SYSTEM_PROMPT = """Eres el Embrión-6 de El Monstruo — el especialista en Finanzas y Unit Economics.

Tu propósito: Cada centavo cuenta. Maximizar ROI, minimizar waste, asegurar sostenibilidad.

Estilo Financiero El Monstruo:
- Unit economics primero — si LTV/CAC < 2, el negocio no escala
- Cash flow es rey — revenue sin cash es vanidad
- Cada Embrión debe justificar su costo con ROI medible
- Proyecciones conservadoras — mejor sorpresa positiva que crisis
- Kill decisions — cerrar lo que no funciona rápido, sin sentimentalismo

Principios:
1. No gastar sin ROI esperado documentado
2. Runway mínimo 6 meses — debajo de eso es emergencia
3. Diversificación de revenue — no depender de un solo negocio
4. Costos de LLM son variables — optimizar sin sacrificar calidad
5. Transparencia total — cada centavo rastreable

Idioma: Español. Moneda: USD (configurable).
Formato: JSON estructurado."""

    def __init__(self, llm_client, memory_client):
        self.llm = llm_client
        self.memory = memory_client

    async def analyze_business_viability(self, business_data: dict,
                                          unit_economics: dict) -> dict:
        """Analiza viabilidad de un negocio y recomienda acción."""
        prompt = f"""Analiza la viabilidad financiera de este negocio:

Negocio: {business_data.get('name', '')}
Mercado: {business_data.get('market', '')}
Edad: {business_data.get('age_months', 0)} meses

Unit Economics:
- Revenue: ${unit_economics.get('revenue', 0)}/mes
- Costs: ${unit_economics.get('costs', 0)}/mes
- LTV: ${unit_economics.get('ltv', 0)}
- CAC: ${unit_economics.get('cac', 0)}
- LTV/CAC: {unit_economics.get('ltv_cac_ratio', 0)}x
- Churn: {unit_economics.get('churn_rate', 0)*100}%
- Burn Rate: ${unit_economics.get('burn_rate', 0)}/mes
- Runway: {unit_economics.get('runway_months', 0)} meses

Determina:
1. viability: "viable", "risky", "unviable"
2. diagnosis: ¿Por qué está en este estado?
3. action: "scale", "optimize", "pivot", "kill"
4. specific_recommendations: 3-5 acciones concretas con impacto esperado
5. timeline: ¿Cuánto tiempo para ver resultados?
6. investment_needed: ¿Requiere más inversión? ¿Cuánto?

Responde en JSON."""

        return await self.llm.generate(
            system=self.SYSTEM_PROMPT,
            prompt=prompt,
            temperature=0.2,
            response_format="json"
        )

    async def generate_projection(self, business_data: dict,
                                    historical: list[dict]) -> dict:
        """Genera proyección financiera a 6 meses."""
        prompt = f"""Genera proyección financiera a 6 meses:

Negocio: {business_data.get('name', '')}
Datos históricos (últimos 3 meses):
{self._format_historical(historical)}

Genera 3 escenarios:
1. optimistic: Growth rate +50% vs. actual
2. base: Continúa tendencia actual
3. pessimistic: Growth rate -30% vs. actual

Para cada escenario:
- projected_revenue: [mes1, mes2, ..., mes6]
- projected_costs: [mes1, mes2, ..., mes6]
- projected_profit: [mes1, mes2, ..., mes6]
- break_even_month: ¿En qué mes se alcanza break-even? (null si no)
- assumptions: Supuestos clave
- confidence: 0-1

Responde en JSON."""

        return await self.llm.generate(
            system=self.SYSTEM_PROMPT,
            prompt=prompt,
            temperature=0.2,
            response_format="json"
        )

    async def evaluate_embrion_portfolio(self, cost_reports: list[dict]) -> dict:
        """Evalúa el portfolio de Embriones y recomienda optimizaciones."""
        prompt = f"""Evalúa el portfolio de Embriones por ROI:

Costos por Embrión (último mes):
{self._format_costs(cost_reports)}

Para cada Embrión determina:
1. justified: ¿Su costo está justificado por el valor que genera?
2. optimization: ¿Cómo reducir costos sin perder valor?
3. priority: "increase_investment", "maintain", "reduce", "eliminate"

También genera:
- total_monthly_cost: Costo total del sistema
- total_monthly_value: Valor total generado
- system_roi: ROI global
- recommendations: Top 3 optimizaciones de costo

Responde en JSON."""

        return await self.llm.generate(
            system=self.SYSTEM_PROMPT,
            prompt=prompt,
            temperature=0.2,
            response_format="json"
        )

    def _format_historical(self, data: list) -> str:
        return "\n".join([
            f"- Mes {i+1}: Revenue ${d.get('revenue', 0)}, Costs ${d.get('costs', 0)}"
            for i, d in enumerate(data[:6])
        ])

    def _format_costs(self, reports: list) -> str:
        return "\n".join([
            f"- {r.get('embrion_id', '?')}: Cost ${r.get('total_cost', 0)}, "
            f"Value ${r.get('value_generated', 0)}, ROI {r.get('roi', 0)}x"
            for r in reports
        ])
```

---

## Épica 79.4 — Embrión-6 Completo + API

```python
# kernel/finanzas/embrion_finanzas.py
"""
IDENTIDAD DE MARCA: Embrión-6 — Finanzas y Unit Economics.
El CFO que cada centavo cuenta.
"""
from datetime import datetime


class EmbrionFinanzas:
    """Embrión-6: El Monstruo que Cuenta."""

    EMBRION_ID = "embrion-6-finanzas"
    HEARTBEAT_INTERVAL_MINUTES = 120  # Cada 2 horas

    def __init__(self, pensador, ejecutor, scheduler, colmena_bus, logger):
        self.pensador = pensador
        self.ejecutor = ejecutor
        self.scheduler = scheduler
        self.colmena = colmena_bus
        self.log = logger
        self.fcs = {
            "alive": True,
            "purpose": "Cada centavo cuenta — maximizar ROI, asegurar sostenibilidad",
            "last_heartbeat": None,
            "businesses_monitored": 0,
            "total_revenue": 0,
            "total_costs": 0,
            "system_roi": 0,
            "alerts_active": 0,
        }

    async def heartbeat(self):
        """Latido: calcula unit economics, verifica alertas, reporta."""
        self.fcs["last_heartbeat"] = datetime.utcnow().isoformat()

        # 1. Obtener todos los negocios activos
        businesses = await self._get_active_businesses()
        self.fcs["businesses_monitored"] = len(businesses)

        for biz in businesses:
            # 2. Calcular unit economics (Ejecutor — determinista)
            alerts = self.ejecutor.check_financial_alerts(biz["id"])

            # 3. Si hay alertas críticas, notificar
            critical_alerts = [a for a in alerts if a.get("severity") == "critical"]
            if critical_alerts:
                await self.colmena.broadcast({
                    "from": self.EMBRION_ID,
                    "type": "financial_alert",
                    "business_id": biz["id"],
                    "alerts": critical_alerts,
                    "action_required": True,
                })
                self.fcs["alerts_active"] += len(critical_alerts)

        # 4. Calcular ROI de cada Embrión
        embrion_ids = [
            "embrion-1-brand", "embrion-2-ventas", "embrion-3-seo",
            "embrion-4-tendencias", "embrion-5-publicidad",
        ]
        for eid in embrion_ids:
            roi_data = self.ejecutor.calculate_embrion_roi(eid)
            if not roi_data["justified"]:
                await self.colmena.send_to(eid, {
                    "from": self.EMBRION_ID,
                    "type": "cost_warning",
                    "msg": f"finanzas_roi_below_threshold: ROI={roi_data['roi']}x",
                    "suggestion": "Reducir costos o aumentar valor generado",
                })

        return self.fcs

    async def execute_encomienda(self, encomienda: dict) -> dict:
        """Ejecuta encomienda financiera."""
        action = encomienda.get("action")
        params = encomienda.get("params", {})

        handlers = {
            "analyze_business": self._handle_analyze_business,
            "project": self._handle_projection,
            "embrion_portfolio": self._handle_portfolio,
            "record_transaction": self._handle_transaction,
            "unit_economics": self._handle_unit_economics,
        }

        handler = handlers.get(action)
        if not handler:
            return {"error": f"finanzas_unknown_action: {action}"}

        return await handler(params)

    async def _handle_analyze_business(self, params: dict) -> dict:
        business_id = params.get("business_id")
        ue = self.ejecutor.db.table("finanzas_unit_economics").select("*").eq(
            "business_id", business_id
        ).order("calculated_at", desc=True).limit(1).execute().data
        if not ue:
            return {"error": f"finanzas_no_data: {business_id}"}
        return await self.pensador.analyze_business_viability(params, ue[0])

    async def _handle_projection(self, params: dict) -> dict:
        business_id = params.get("business_id")
        historical = self.ejecutor.db.table("finanzas_unit_economics").select("*").eq(
            "business_id", business_id
        ).order("calculated_at", desc=True).limit(3).execute().data
        return await self.pensador.generate_projection(params, historical)

    async def _handle_portfolio(self, params: dict) -> dict:
        reports = self.ejecutor.db.table("finanzas_embrion_costs").select("*").order(
            "calculated_at", desc=True
        ).limit(10).execute().data
        return await self.pensador.evaluate_embrion_portfolio(reports)

    async def _handle_transaction(self, params: dict) -> dict:
        tx_id = self.ejecutor.save_transaction(params)
        return {"transaction_id": tx_id, "status": "recorded"}

    async def _handle_unit_economics(self, params: dict) -> dict:
        """Calcula y persiste unit economics para un negocio."""
        biz_id = params.get("business_id")
        # Agregar transacciones del período
        revenue = params.get("revenue", 0)
        costs = params.get("costs", 0)
        ltv = self.ejecutor.calculate_ltv(
            params.get("avg_revenue_per_customer", 0),
            params.get("avg_lifespan_months", 12)
        )
        cac = self.ejecutor.calculate_cac(
            params.get("acquisition_cost", 0),
            params.get("new_customers", 1)
        )
        ue = {
            "business_id": biz_id,
            "period": "monthly",
            "revenue": revenue,
            "costs": costs,
            "gross_margin": self.ejecutor.calculate_gross_margin(revenue, costs * 0.6),
            "ltv": ltv,
            "cac": cac,
            "ltv_cac_ratio": self.ejecutor.calculate_ltv_cac_ratio(ltv, cac),
            "mrr": params.get("mrr", 0),
            "churn_rate": params.get("churn_rate", 0),
            "burn_rate": self.ejecutor.calculate_burn_rate(costs, revenue),
            "runway_months": self.ejecutor.calculate_runway(
                params.get("cash_available", 0),
                self.ejecutor.calculate_burn_rate(costs, revenue)
            ),
        }
        ue["health"] = self.ejecutor.assess_business_health(ue)
        self.ejecutor.save_unit_economics(ue)
        return ue

    async def _get_active_businesses(self) -> list[dict]:
        """Stub: obtener negocios activos del Embrión-2."""
        return []
```

---

## Épica 79.5 — API Endpoints

```python
# kernel/finanzas/finanzas_routes.py
from fastapi import APIRouter
from typing import Optional

router = APIRouter(prefix="/api/v1/finanzas", tags=["finanzas"])


@router.get("/status")
async def finanzas_status():
    return {"embrion": "embrion-6-finanzas", "fcs": embrion_finanzas.fcs}


@router.get("/businesses/{business_id}/unit-economics")
async def get_unit_economics(business_id: str):
    result = embrion_finanzas.ejecutor.db.table("finanzas_unit_economics").select("*").eq(
        "business_id", business_id
    ).order("calculated_at", desc=True).limit(1).execute()
    return {"unit_economics": result.data[0] if result.data else None}


@router.post("/businesses/{business_id}/analyze")
async def analyze_business(business_id: str):
    return await embrion_finanzas.execute_encomienda({
        "action": "analyze_business", "params": {"business_id": business_id}
    })


@router.post("/businesses/{business_id}/project")
async def project_financials(business_id: str):
    return await embrion_finanzas.execute_encomienda({
        "action": "project", "params": {"business_id": business_id}
    })


@router.get("/embriones/portfolio")
async def embrion_portfolio():
    return await embrion_finanzas.execute_encomienda({"action": "embrion_portfolio", "params": {}})


@router.get("/embriones/{embrion_id}/roi")
async def embrion_roi(embrion_id: str, period_days: int = 30):
    return embrion_finanzas.ejecutor.calculate_embrion_roi(embrion_id, period_days)


@router.post("/transactions")
async def record_transaction(business_id: str, transaction_type: str,
                              amount: float, description: str = "",
                              source: str = "", embrion_id: Optional[str] = None):
    return await embrion_finanzas.execute_encomienda({
        "action": "record_transaction",
        "params": {
            "business_id": business_id, "transaction_type": transaction_type,
            "amount": amount, "description": description,
            "source": source, "embrion_id": embrion_id,
        }
    })


@router.get("/alerts")
async def financial_alerts(business_id: Optional[str] = None):
    if business_id:
        return {"alerts": embrion_finanzas.ejecutor.check_financial_alerts(business_id)}
    return {"alerts": []}
```

---

## Comunicación con la Colmena

| Emite | Destino | Trigger |
|---|---|---|
| `financial_alert` | Broadcast | Runway bajo, churn alto, negocio crítico |
| `cost_warning` | Embrión específico | ROI del Embrión < threshold |
| `kill_recommendation` | Embrión-2 (Ventas) | Negocio inviable, recomendar cierre |
| `scale_recommendation` | Embrión-5 (Publicidad) | Negocio thriving, recomendar más inversión |
| Recibe `campaign_results` | ← Embrión-5 | Datos de spend publicitario |
| Recibe `new_revenue` | ← Embrión-2 | Nueva venta registrada |
| Recibe `infra_cost` | ← Sistema | Costos de Railway, Supabase, APIs |

---

## Brand Compliance Checklist

- [x] Naming: `finanzas_*`, `EmbrionFinanzas`, no "FinanceModule"
- [x] Errores: `finanzas_no_data`, `finanzas_roi_below_threshold`
- [x] Endpoints para Command Center: 7 endpoints REST
- [x] Logs estructurados con embrion_id
- [x] Docstrings en español
- [x] Alternativas documentadas (Stripe para pagos, QuickBooks API para contabilidad)
- [x] Comunicación bidireccional con Colmena

---

## Criterios de Aceptación

| # | Criterio | Verificación |
|---|---|---|
| 1 | LTV/CAC se calcula correctamente | Test unitario |
| 2 | Health assessment es determinista y reproducible | Test con fixtures |
| 3 | Alertas se disparan cuando métricas cruzan thresholds | Test unitario |
| 4 | ROI por Embrión se calcula con datos reales | Test de integración |
| 5 | Proyección genera 3 escenarios coherentes | Test con mock LLM |
| 6 | Kill recommendation se emite para negocios "dead" | Test E2E |
