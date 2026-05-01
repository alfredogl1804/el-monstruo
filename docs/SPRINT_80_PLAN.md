# Sprint 80 — "El Monstruo que Opera"
## Embrión-7: Operaciones + Cierre Serie 71-80

**Serie:** 71-80 "La Colmena Despierta" (SPRINT FINAL)
**Fecha de diseño:** 1 de Mayo 2026
**Arquitectura:** Pensador (LLM potente) + Ejecutor (código determinista)
**Dependencias:** Sprint 72 (TEL), Sprint 74 (Colmena), Sprint 75 (Ventas)

---

## Visión

El Embrión-7 es el COO del sistema — el que asegura que todo funcione sin fricción. Customer support, procesos internos, compliance legal, SLAs, y la operación diaria de los negocios que El Monstruo crea. Apple no tiene soporte genérico — tiene Genius Bar. Tesla no tiene tickets — tiene resolución proactiva. El Monstruo no tiene "customer service" — tiene operaciones inteligentes que anticipan problemas antes de que el cliente los reporte.

Este sprint también cierra la Serie 71-80, completando la Colmena con 7 Embriones especializados + el Orquestador (Embrión-0).

---

## Arquitectura Pensador/Ejecutor

### Pensador (LLM Potente)
- Analiza tickets/consultas y determina la mejor resolución
- Genera respuestas con tono de marca (validadas por Embrión-1)
- Detecta patrones en quejas para prevención proactiva
- Diseña y optimiza procesos operativos
- Evalúa compliance legal de operaciones

### Ejecutor (Python Puro)
- Clasifica tickets por urgencia y tipo (reglas deterministas)
- Rutea a Embrión correcto según dominio
- Ejecuta workflows automatizados (refunds, escalaciones, notificaciones)
- Mide SLAs (tiempo de respuesta, resolución, satisfacción)
- Persiste tickets y métricas en Supabase

---

## Épica 80.1 — Modelos y Tablas

```python
# kernel/operaciones/models.py
"""
IDENTIDAD DE MARCA: Módulo de Operaciones de El Monstruo.
Naming: operaciones_* (nunca "ops_module" ni "support_system")
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class TicketPriority(Enum):
    CRITICAL = "critical"    # Sistema caído, pérdida de dinero activa
    HIGH = "high"            # Funcionalidad rota, cliente frustrado
    MEDIUM = "medium"        # Pregunta compleja, requiere investigación
    LOW = "low"              # Pregunta simple, FAQ


class TicketStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ProcessType(Enum):
    ONBOARDING = "onboarding"
    REFUND = "refund"
    ESCALATION = "escalation"
    COMPLIANCE_CHECK = "compliance_check"
    MAINTENANCE = "maintenance"
    INCIDENT_RESPONSE = "incident_response"


@dataclass
class Ticket:
    id: str
    business_id: str
    customer_id: Optional[str] = None
    subject: str = ""
    description: str = ""
    priority: str = "medium"
    status: str = "open"
    category: str = ""          # "billing", "technical", "product", "legal"
    assigned_embrion: Optional[str] = None
    resolution: Optional[str] = None
    satisfaction_score: Optional[int] = None  # 1-5
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    sla_deadline: Optional[datetime] = None


@dataclass
class Process:
    id: str
    process_type: str
    business_id: str
    status: str = "active"
    steps_total: int = 0
    steps_completed: int = 0
    current_step: str = ""
    metadata: dict = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


@dataclass
class SLAMetrics:
    business_id: str
    period: str
    tickets_total: int = 0
    tickets_resolved: int = 0
    avg_response_time_minutes: float = 0
    avg_resolution_time_hours: float = 0
    sla_compliance_rate: float = 0    # % dentro de SLA
    csat_average: float = 0           # Customer satisfaction 1-5
    nps: int = 0                      # Net Promoter Score -100 to 100
    escalation_rate: float = 0
    calculated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class OperationalInsight:
    id: str
    insight_type: str          # "pattern", "prevention", "optimization"
    description: str = ""
    affected_area: str = ""    # "billing", "onboarding", "product"
    frequency: int = 0         # Cuántas veces se detectó
    suggested_action: str = ""
    implemented: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
```

### SQL

```sql
CREATE TABLE IF NOT EXISTS operaciones_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id TEXT NOT NULL,
    customer_id TEXT,
    subject TEXT NOT NULL,
    description TEXT DEFAULT '',
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'open',
    category TEXT DEFAULT '',
    assigned_embrion TEXT,
    resolution TEXT,
    satisfaction_score INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    sla_deadline TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS operaciones_processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_type TEXT NOT NULL,
    business_id TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    steps_total INTEGER DEFAULT 0,
    steps_completed INTEGER DEFAULT 0,
    current_step TEXT DEFAULT '',
    metadata JSONB DEFAULT '{}',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS operaciones_sla_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id TEXT NOT NULL,
    period TEXT NOT NULL,
    tickets_total INTEGER DEFAULT 0,
    tickets_resolved INTEGER DEFAULT 0,
    avg_response_time_minutes NUMERIC(8,2) DEFAULT 0,
    avg_resolution_time_hours NUMERIC(8,2) DEFAULT 0,
    sla_compliance_rate NUMERIC(5,2) DEFAULT 0,
    csat_average NUMERIC(3,2) DEFAULT 0,
    nps INTEGER DEFAULT 0,
    escalation_rate NUMERIC(5,2) DEFAULT 0,
    calculated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS operaciones_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    insight_type TEXT NOT NULL,
    description TEXT DEFAULT '',
    affected_area TEXT DEFAULT '',
    frequency INTEGER DEFAULT 0,
    suggested_action TEXT DEFAULT '',
    implemented BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tickets_business ON operaciones_tickets(business_id, status);
CREATE INDEX idx_tickets_priority ON operaciones_tickets(priority, status);
CREATE INDEX idx_processes_business ON operaciones_processes(business_id, status);
CREATE INDEX idx_sla_business ON operaciones_sla_metrics(business_id, period);
```

---

## Épica 80.2 — Ejecutor Operaciones

```python
# kernel/operaciones/operaciones_ejecutor.py
"""
IDENTIDAD DE MARCA: Ejecutor del Embrión-7 (Operaciones).
Código determinista. Clasificación, routing, SLA tracking.
"""
from datetime import datetime, timedelta


class OperacionesEjecutor:
    """Ejecutor determinista del Embrión-7. La máquina que nunca falla."""

    # SLA por prioridad (en minutos para respuesta, horas para resolución)
    SLA_CONFIG = {
        "critical": {"response_min": 15, "resolution_hours": 2},
        "high": {"response_min": 60, "resolution_hours": 8},
        "medium": {"response_min": 240, "resolution_hours": 24},
        "low": {"response_min": 480, "resolution_hours": 72},
    }

    # Routing rules: categoría → Embrión responsable
    ROUTING_RULES = {
        "billing": "embrion-6-finanzas",
        "brand": "embrion-1-brand",
        "sales": "embrion-2-ventas",
        "seo": "embrion-3-seo",
        "trends": "embrion-4-tendencias",
        "ads": "embrion-5-publicidad",
        "technical": "embrion-0-orquestador",
        "legal": None,  # Escalación humana
        "product": "embrion-2-ventas",
    }

    def __init__(self, supabase_client, logger):
        self.db = supabase_client
        self.log = logger

    # --- Clasificación ---

    def classify_priority(self, ticket: dict) -> str:
        """Clasifica prioridad basado en reglas deterministas."""
        subject = (ticket.get("subject", "") + " " + ticket.get("description", "")).lower()

        # Critical: dinero, caída, seguridad
        critical_keywords = ["dinero perdido", "no funciona", "caído", "hackeado",
                            "cobro indebido", "urgente", "emergencia"]
        if any(kw in subject for kw in critical_keywords):
            return "critical"

        # High: frustración, error, bug
        high_keywords = ["error", "bug", "no puedo", "frustrado", "roto",
                        "no carga", "lento"]
        if any(kw in subject for kw in high_keywords):
            return "high"

        # Low: preguntas simples
        low_keywords = ["cómo", "pregunta", "información", "duda", "tutorial"]
        if any(kw in subject for kw in low_keywords):
            return "low"

        return "medium"

    def classify_category(self, ticket: dict) -> str:
        """Clasifica categoría basado en contenido."""
        text = (ticket.get("subject", "") + " " + ticket.get("description", "")).lower()

        category_keywords = {
            "billing": ["pago", "factura", "cobro", "reembolso", "precio", "plan"],
            "technical": ["error", "bug", "api", "integración", "código"],
            "product": ["funcionalidad", "feature", "mejora", "sugerencia"],
            "sales": ["comprar", "descuento", "demo", "cotización"],
            "legal": ["contrato", "términos", "privacidad", "gdpr", "legal"],
            "brand": ["logo", "marca", "diseño", "identidad"],
        }

        for category, keywords in category_keywords.items():
            if any(kw in text for kw in keywords):
                return category

        return "product"  # Default

    def route_ticket(self, category: str) -> str:
        """Determina qué Embrión debe resolver el ticket."""
        return self.ROUTING_RULES.get(category, "embrion-0-orquestador")

    # --- SLA ---

    def calculate_sla_deadline(self, priority: str, created_at: datetime) -> datetime:
        """Calcula deadline de SLA basado en prioridad."""
        config = self.SLA_CONFIG.get(priority, self.SLA_CONFIG["medium"])
        return created_at + timedelta(hours=config["resolution_hours"])

    def check_sla_breach(self, ticket: dict) -> bool:
        """Verifica si un ticket ha violado su SLA."""
        deadline = ticket.get("sla_deadline")
        if not deadline:
            return False
        if isinstance(deadline, str):
            deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
        return datetime.utcnow() > deadline and ticket.get("status") != "resolved"

    # --- Métricas ---

    def calculate_sla_metrics(self, business_id: str, period_days: int = 30) -> dict:
        """Calcula métricas de SLA para un negocio."""
        cutoff = (datetime.utcnow() - timedelta(days=period_days)).isoformat()

        tickets = self.db.table("operaciones_tickets").select("*").eq(
            "business_id", business_id
        ).gte("created_at", cutoff).execute().data or []

        total = len(tickets)
        if total == 0:
            return {"tickets_total": 0}

        resolved = [t for t in tickets if t.get("status") == "resolved"]
        breached = [t for t in tickets if self.check_sla_breach(t)]

        # Satisfaction
        scores = [t["satisfaction_score"] for t in resolved
                  if t.get("satisfaction_score")]
        csat = sum(scores) / len(scores) if scores else 0

        # Response time (mock: basado en created_at vs. primer update)
        escalated = [t for t in tickets if t.get("status") == "escalated"]

        return {
            "business_id": business_id,
            "period": f"{period_days}d",
            "tickets_total": total,
            "tickets_resolved": len(resolved),
            "sla_compliance_rate": round((1 - len(breached) / total) * 100, 2),
            "csat_average": round(csat, 2),
            "escalation_rate": round(len(escalated) / total * 100, 2) if total else 0,
        }

    # --- Workflows ---

    def execute_refund_workflow(self, ticket: dict) -> dict:
        """Workflow determinista de reembolso."""
        steps = [
            "validate_refund_eligibility",
            "calculate_refund_amount",
            "process_refund",
            "notify_customer",
            "close_ticket",
        ]
        return {
            "process_type": "refund",
            "steps_total": len(steps),
            "steps_completed": 0,
            "current_step": steps[0],
            "status": "active",
        }

    def execute_onboarding_workflow(self, business_id: str) -> dict:
        """Workflow de onboarding para nuevo negocio."""
        steps = [
            "create_workspace",
            "configure_brand_dna",
            "setup_analytics",
            "initial_audit",
            "welcome_communication",
        ]
        return {
            "process_type": "onboarding",
            "business_id": business_id,
            "steps_total": len(steps),
            "steps_completed": 0,
            "current_step": steps[0],
            "status": "active",
        }

    # --- Persistence ---

    def save_ticket(self, ticket: dict) -> str:
        result = self.db.table("operaciones_tickets").insert(ticket).execute()
        return result.data[0]["id"] if result.data else ""

    def update_ticket(self, ticket_id: str, updates: dict) -> bool:
        self.db.table("operaciones_tickets").update(updates).eq("id", ticket_id).execute()
        return True

    def save_insight(self, insight: dict) -> str:
        result = self.db.table("operaciones_insights").insert(insight).execute()
        return result.data[0]["id"] if result.data else ""
```

---

## Épica 80.3 — Pensador Operaciones

```python
# kernel/operaciones/operaciones_pensador.py
"""
IDENTIDAD DE MARCA: Pensador del Embrión-7 (Operaciones).
Solo juicio: resolución de tickets, detección de patrones, optimización de procesos.
"""


class OperacionesPensador:
    """Pensador del Embrión-7. El COO que anticipa."""

    SYSTEM_PROMPT = """Eres el Embrión-7 de El Monstruo — el especialista en Operaciones.

Tu propósito: Que todo funcione sin fricción. Anticipar problemas. Resolver con elegancia.

Estilo Operativo El Monstruo:
- No somos "soporte" — somos resolución proactiva
- Cada interacción es una oportunidad de demostrar calidad Apple/Tesla
- Anticipar > Reaccionar. Si un cliente reporta un bug, ya deberíamos saberlo
- Respuestas con personalidad, no templates genéricos
- Escalar rápido cuando no puedes resolver — no hacer perder tiempo al cliente

Principios:
1. Resolución en primer contacto siempre que sea posible
2. Tono empático pero eficiente — no sobre-disculparse
3. Si detectas un patrón (3+ tickets similares), crear insight preventivo
4. Nunca prometer lo que no puedes cumplir
5. Transparencia total — si hay un problema sistémico, comunicarlo proactivamente

Idioma: Español. Tono: Profesional, empático, directo.
Formato: JSON estructurado."""

    def __init__(self, llm_client, memory_client):
        self.llm = llm_client
        self.memory = memory_client

    async def resolve_ticket(self, ticket: dict, context: dict) -> dict:
        """Genera resolución para un ticket."""
        prompt = f"""Resuelve este ticket:

Ticket: {ticket.get('subject', '')}
Descripción: {ticket.get('description', '')}
Prioridad: {ticket.get('priority', 'medium')}
Categoría: {ticket.get('category', '')}
Cliente: {ticket.get('customer_id', 'anónimo')}

Contexto del negocio:
{context.get('business_info', 'Sin contexto adicional')}

Historial del cliente:
{context.get('customer_history', 'Sin historial')}

Genera:
1. resolution: Texto de resolución para el cliente (con tono de marca)
2. internal_notes: Notas internas para el equipo
3. action_items: Lista de acciones a ejecutar
4. requires_escalation: true/false
5. escalation_reason: Si requiere escalación, por qué
6. prevention_suggestion: ¿Cómo evitar este tipo de ticket en el futuro?

Responde en JSON."""

        return await self.llm.generate(
            system=self.SYSTEM_PROMPT,
            prompt=prompt,
            temperature=0.3,
            response_format="json"
        )

    async def detect_patterns(self, recent_tickets: list[dict]) -> dict:
        """Detecta patrones en tickets recientes para prevención."""
        prompt = f"""Analiza estos {len(recent_tickets)} tickets recientes y detecta patrones:

Tickets:
{self._format_tickets(recent_tickets)}

Identifica:
1. patterns: Lista de patrones detectados (tema, frecuencia, severidad)
2. root_causes: Causas raíz probables
3. preventive_actions: Acciones para prevenir estos tickets en el futuro
4. process_improvements: Mejoras de proceso sugeridas
5. proactive_communications: Mensajes proactivos a enviar a clientes afectados

Responde en JSON."""

        return await self.llm.generate(
            system=self.SYSTEM_PROMPT,
            prompt=prompt,
            temperature=0.3,
            response_format="json"
        )

    async def optimize_process(self, process_data: dict,
                                metrics: dict) -> dict:
        """Sugiere optimizaciones para un proceso operativo."""
        prompt = f"""Optimiza este proceso operativo:

Proceso: {process_data.get('process_type', '')}
Steps actuales: {process_data.get('steps', [])}
Tiempo promedio: {metrics.get('avg_duration', 'desconocido')}
Tasa de éxito: {metrics.get('success_rate', 'desconocida')}
Bottlenecks: {metrics.get('bottlenecks', 'no identificados')}

Sugiere:
1. optimized_steps: Steps optimizados (eliminar, combinar, automatizar)
2. automation_opportunities: Qué se puede automatizar completamente
3. time_savings: Ahorro de tiempo estimado
4. quality_improvements: Mejoras de calidad esperadas
5. implementation_effort: "low", "medium", "high"

Responde en JSON."""

        return await self.llm.generate(
            system=self.SYSTEM_PROMPT,
            prompt=prompt,
            temperature=0.3,
            response_format="json"
        )

    def _format_tickets(self, tickets: list) -> str:
        return "\n".join([
            f"- [{t.get('priority','?')}] {t.get('subject','?')} | Cat: {t.get('category','?')}"
            for t in tickets[:20]
        ])
```

---

## Épica 80.4 — Embrión-7 Completo + API

```python
# kernel/operaciones/embrion_operaciones.py
"""
IDENTIDAD DE MARCA: Embrión-7 — Operaciones.
El COO que todo funcione sin fricción.
"""
from datetime import datetime


class EmbrionOperaciones:
    """Embrión-7: El Monstruo que Opera."""

    EMBRION_ID = "embrion-7-operaciones"
    HEARTBEAT_INTERVAL_MINUTES = 30  # Cada 30 min — operaciones requiere alta frecuencia

    def __init__(self, pensador, ejecutor, scheduler, colmena_bus, logger):
        self.pensador = pensador
        self.ejecutor = ejecutor
        self.scheduler = scheduler
        self.colmena = colmena_bus
        self.log = logger
        self.fcs = {
            "alive": True,
            "purpose": "Que todo funcione sin fricción — anticipar y resolver",
            "last_heartbeat": None,
            "tickets_open": 0,
            "sla_compliance": 100.0,
            "csat_average": 0,
            "patterns_detected": 0,
        }

    async def heartbeat(self):
        """Latido: verifica SLAs, detecta brechas, previene problemas."""
        self.fcs["last_heartbeat"] = datetime.utcnow().isoformat()

        # 1. Verificar tickets abiertos con SLA en riesgo
        open_tickets = self.ejecutor.db.table("operaciones_tickets").select("*").in_(
            "status", ["open", "in_progress"]
        ).execute().data or []

        self.fcs["tickets_open"] = len(open_tickets)

        breached = [t for t in open_tickets if self.ejecutor.check_sla_breach(t)]
        if breached:
            await self.colmena.broadcast({
                "from": self.EMBRION_ID,
                "type": "sla_breach",
                "tickets_breached": len(breached),
                "action_required": True,
            })

        # 2. Detectar patrones si hay suficientes tickets recientes
        recent = self.ejecutor.db.table("operaciones_tickets").select("*").order(
            "created_at", desc=True
        ).limit(50).execute().data or []

        if len(recent) >= 10:
            patterns = await self.pensador.detect_patterns(recent)
            if patterns.get("patterns"):
                self.fcs["patterns_detected"] = len(patterns["patterns"])
                for pattern in patterns["patterns"]:
                    self.ejecutor.save_insight({
                        "insight_type": "pattern",
                        "description": pattern.get("description", ""),
                        "affected_area": pattern.get("area", ""),
                        "frequency": pattern.get("frequency", 0),
                        "suggested_action": pattern.get("prevention", ""),
                    })

        return self.fcs

    async def handle_ticket(self, ticket_data: dict) -> dict:
        """Procesa un nuevo ticket: clasifica, rutea, resuelve."""
        # Ejecutor: clasificación determinista
        priority = self.ejecutor.classify_priority(ticket_data)
        category = self.ejecutor.classify_category(ticket_data)
        assigned = self.ejecutor.route_ticket(category)
        sla_deadline = self.ejecutor.calculate_sla_deadline(
            priority, datetime.utcnow()
        )

        ticket = {
            **ticket_data,
            "priority": priority,
            "category": category,
            "assigned_embrion": assigned,
            "sla_deadline": sla_deadline.isoformat(),
            "status": "in_progress",
        }

        ticket_id = self.ejecutor.save_ticket(ticket)

        # Pensador: resolución con juicio
        resolution = await self.pensador.resolve_ticket(ticket, {})

        if resolution.get("requires_escalation"):
            self.ejecutor.update_ticket(ticket_id, {"status": "escalated"})
            await self.colmena.send_to(assigned, {
                "from": self.EMBRION_ID,
                "type": "escalation",
                "ticket_id": ticket_id,
                "reason": resolution.get("escalation_reason", ""),
            })
        else:
            self.ejecutor.update_ticket(ticket_id, {
                "status": "resolved",
                "resolution": resolution.get("resolution", ""),
                "resolved_at": datetime.utcnow().isoformat(),
            })

        return {"ticket_id": ticket_id, "resolution": resolution}

    async def execute_encomienda(self, encomienda: dict) -> dict:
        """Ejecuta encomienda operativa."""
        action = encomienda.get("action")
        params = encomienda.get("params", {})

        handlers = {
            "handle_ticket": lambda p: self.handle_ticket(p),
            "sla_metrics": lambda p: self._handle_sla_metrics(p),
            "optimize_process": lambda p: self.pensador.optimize_process(p, {}),
            "onboarding": lambda p: self._handle_onboarding(p),
        }

        handler = handlers.get(action)
        if not handler:
            return {"error": f"operaciones_unknown_action: {action}"}

        return await handler(params)

    async def _handle_sla_metrics(self, params: dict) -> dict:
        return self.ejecutor.calculate_sla_metrics(
            params.get("business_id", ""),
            params.get("period_days", 30)
        )

    async def _handle_onboarding(self, params: dict) -> dict:
        workflow = self.ejecutor.execute_onboarding_workflow(params.get("business_id"))
        self.ejecutor.db.table("operaciones_processes").insert(workflow).execute()
        return workflow
```

---

## Épica 80.5 — API Endpoints

```python
# kernel/operaciones/operaciones_routes.py
from fastapi import APIRouter
from typing import Optional

router = APIRouter(prefix="/api/v1/operaciones", tags=["operaciones"])


@router.get("/status")
async def operaciones_status():
    return {"embrion": "embrion-7-operaciones", "fcs": embrion_operaciones.fcs}


@router.post("/tickets")
async def create_ticket(business_id: str, subject: str,
                         description: str = "", customer_id: Optional[str] = None):
    return await embrion_operaciones.handle_ticket({
        "business_id": business_id, "subject": subject,
        "description": description, "customer_id": customer_id,
    })


@router.get("/tickets")
async def list_tickets(business_id: Optional[str] = None,
                        status: Optional[str] = None, limit: int = 50):
    query = embrion_operaciones.ejecutor.db.table("operaciones_tickets").select("*")
    if business_id:
        query = query.eq("business_id", business_id)
    if status:
        query = query.eq("status", status)
    result = query.order("created_at", desc=True).limit(limit).execute()
    return {"tickets": result.data}


@router.get("/sla/{business_id}")
async def sla_metrics(business_id: str, period_days: int = 30):
    return embrion_operaciones.ejecutor.calculate_sla_metrics(business_id, period_days)


@router.get("/insights")
async def operational_insights(limit: int = 20):
    result = embrion_operaciones.ejecutor.db.table("operaciones_insights").select("*").order(
        "created_at", desc=True
    ).limit(limit).execute()
    return {"insights": result.data}


@router.post("/processes/onboarding")
async def start_onboarding(business_id: str):
    return await embrion_operaciones.execute_encomienda({
        "action": "onboarding", "params": {"business_id": business_id}
    })
```

---

## Comunicación con la Colmena

| Emite | Destino | Trigger |
|---|---|---|
| `sla_breach` | Broadcast | Tickets violando SLA |
| `escalation` | Embrión asignado | Ticket requiere expertise específica |
| `pattern_alert` | Embrión relevante | Patrón detectado en su dominio |
| `onboarding_complete` | Embrión-2 (Ventas) | Nuevo negocio listo para operar |
| Recibe `new_business` | ← Embrión-2 | Nuevo negocio creado, iniciar onboarding |
| Recibe `customer_complaint` | ← Cualquier Embrión | Queja que requiere resolución |
| Recibe `system_incident` | ← Embrión-0 | Incidente técnico que afecta operaciones |

---

## Brand Compliance Checklist

- [x] Naming: `operaciones_*`, `EmbrionOperaciones`, no "SupportSystem"
- [x] Errores: `operaciones_unknown_action`, `operaciones_sla_breach`
- [x] Endpoints para Command Center: 5 endpoints REST
- [x] Logs estructurados con embrion_id
- [x] Docstrings en español
- [x] Alternativas documentadas (Zendesk API, Intercom API como fallback)
- [x] Comunicación bidireccional con Colmena

---

## CIERRE DE SERIE 71-80: "La Colmena Despierta"

### La Colmena Completa

| Embrión | Rol | Sprint | Propósito |
|---|---|---|---|
| Embrión-0 | Orquestador | Pre-existente | Coordina, decide, piensa |
| Embrión-1 | Brand Engine | Sprint 71 | Valida identidad en todo output |
| Embrión-2 | Motor de Ventas | Sprint 75 | Genera revenue |
| Embrión-3 | SEO | Sprint 76 | Descubrimiento orgánico |
| Embrión-4 | Tendencias | Sprint 77 | Inteligencia competitiva |
| Embrión-5 | Publicidad | Sprint 78 | Campañas y creativos |
| Embrión-6 | Finanzas | Sprint 79 | Unit economics y ROI |
| Embrión-7 | Operaciones | Sprint 80 | Customer ops y procesos |

### Capacidades Transversales (Sprints 72-74)

| Sprint | Capacidad | Aplica a |
|---|---|---|
| 72 | Task Execution Loop | Todos los Embriones |
| 73 | 22 Herramientas | Todos los Embriones |
| 74 | Memoria + Colmena | Todos los Embriones |

### Métricas de Éxito de la Serie

| Métrica | Target | Verificación |
|---|---|---|
| Embriones activos | 8 (0-7) | Heartbeat de cada uno |
| Comunicación Colmena | Mensajes entre Embriones | Log de colmena_bus |
| Brand Compliance | 100% outputs validados | Embrión-1 reports |
| Encomiendas completadas | ≥1 por Embrión | execution_memory |
| ROI positivo | ≥3 Embriones con ROI > 1 | Embrión-6 portfolio |

### Lo que la Serie 81-90 debe resolver

1. **Embrión-8: Resiliencia** — Seguridad, disaster recovery, auto-healing
2. **Acceso económico** — Stripe/PayPal para que los Embriones operen con dinero real
3. **Autonomía real** — Encomiendas auto-generadas sin intervención humana
4. **Escalamiento** — Múltiples instancias de cada Embrión para carga
5. **Evaluación 360** — Los Embriones se evalúan entre sí

---

## Criterios de Aceptación

| # | Criterio | Verificación |
|---|---|---|
| 1 | Clasificación de tickets es determinista y correcta | Test unitario con 20 tickets |
| 2 | Routing asigna al Embrión correcto por categoría | Test con todas las categorías |
| 3 | SLA se calcula y alerta cuando se viola | Test con tickets expirados |
| 4 | Resolución genera respuesta con tono de marca | Test con mock LLM |
| 5 | Detección de patrones funciona con ≥10 tickets | Test de integración |
| 6 | Onboarding workflow se ejecuta paso a paso | Test E2E |
