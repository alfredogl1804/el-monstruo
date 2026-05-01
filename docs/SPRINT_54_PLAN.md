# Sprint 54 — "La Primera Chispa de Emergencia"

**Fecha de planificación:** 1 mayo 2026
**Pre-requisito:** Sprints 51-53 completados (Cimientos + Manos + Capas Transversales)
**Capa:** 2 — Inteligencia Emergente
**Objetivos primarios:** #8 (Inteligencia Emergente Colectiva), #11 (Multiplicación de Embriones)
**Objetivos secundarios:** #4 (Error Memory alimenta evolución), #6 (Vanguard alimenta conocimiento compartido)
**Duración estimada:** 7-10 días

---

## Contexto Técnico Actual (Validado contra código real)

El Monstruo ya tiene las piezas fundamentales para la emergencia, pero están desconectadas:

| Componente | Estado | Archivo |
|---|---|---|
| Multi-Agent Registry | 6 agentes especializados (research, code, analysis, creative, ops, default) | `kernel/multi_agent.py` |
| Supervisor/Router | Heurístico zero-latency, 4 tiers (SIMPLE→DEEP) | `kernel/supervisor.py` |
| Autonomous Runner | Loop 24/7, MOC priorización, max 3 concurrent | `kernel/runner/autonomous_runner.py` |
| Mem0 Bridge | Episodic memory con pgvector en Supabase | `memory/mem0_bridge.py` |
| 6 Sabios | Consulta paralela multi-modelo (GPT 5.2, Gemini 3 Pro, Sonar, etc.) | `tools/consult_sabios.py` + `scripts/sabios_engine.py` |
| LangGraph Kernel | Orquestación principal con SubGraphs | `kernel/task_planner.py` |
| Knowledge Graph | LightRAG + pgvector | Activo en Supabase |

**Lo que falta:** Los agentes no evolucionan. No tienen memoria propia. No debaten entre sí. No comparten descubrimientos. Son herramientas estáticas que se invocan — no entidades que piensan.

---

## Épica 54.1 — Embrión Factory: Multiplicación de Embriones Especializados

**Objetivo:** Crear la capacidad de instanciar múltiples Embriones con roles especializados, cada uno con su propia memoria, cognición, y ciclo de evolución.

**Herramienta adoptada:** No existe framework que haga esto. Se CREA sobre la infraestructura existente (LangGraph SubGraphs + Mem0 agent_id scoping + Autonomous Runner). Esto es Objetivo #8 — lo que no existe en ningún lado.

**Inspiración académica:** AutoAgent (marzo 2026) [1] valida el patrón de cognición evolutiva + memoria elástica + evolución en loop cerrado. GenericAgent (abril 2026) [2] valida SOPs reutilizables y memoria jerárquica.

### Archivo: `kernel/embrion_factory.py`

```python
"""
El Monstruo — Embrión Factory (Sprint 54)
==========================================
Crea y gestiona múltiples Embriones especializados.
Cada Embrión es un LangGraph SubGraph con:
  - Rol especializado (ventas, técnico, financiero, etc.)
  - Memoria propia (Mem0 scoped por agent_id)
  - Cognición evolutiva (prompt-level knowledge que se actualiza)
  - Ciclo de reflexión autónomo
  
Inspirado en AutoAgent (2026) pero construido sobre nuestro stack:
  LangGraph + Mem0 + Supabase + Autonomous Runner
"""
from __future__ import annotations
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

import structlog

logger = structlog.get_logger("monstruo.embrion_factory")


class EmbrionRole(str, Enum):
    """Roles especializados de Embriones."""
    COORDINATOR = "coordinator"   # Embrión-0: meta-cognición, orquesta
    VENTAS = "ventas"             # Estrategia comercial, funnels, pricing
    TECNICO = "tecnico"           # Arquitectura, vanguardia, code review
    FINANCIERO = "financiero"     # Modelado financiero, unit economics
    TENDENCIAS = "tendencias"     # Market research, trend detection
    CAUSAL = "causal"             # Simulación predictiva (proto Obj #10)


@dataclass
class EmbrionCognition:
    """
    Cognición evolutiva de un Embrión (inspirado en AutoAgent).
    Se actualiza después de cada ciclo de reflexión.
    """
    role: EmbrionRole
    self_capabilities: list[str] = field(default_factory=list)
    peer_expertise: dict[str, list[str]] = field(default_factory=dict)
    learned_patterns: list[dict] = field(default_factory=list)
    active_hypotheses: list[str] = field(default_factory=list)
    confidence_scores: dict[str, float] = field(default_factory=dict)
    last_evolution: Optional[str] = None  # ISO timestamp
    evolution_count: int = 0

    def to_prompt_context(self) -> str:
        """Serializa la cognición a contexto inyectable en prompts."""
        sections = [
            f"## Mi Rol: {self.role.value}",
            f"## Mis Capacidades: {', '.join(self.self_capabilities)}",
        ]
        if self.peer_expertise:
            peers = "\n".join(
                f"  - {k}: {', '.join(v)}" 
                for k, v in self.peer_expertise.items()
            )
            sections.append(f"## Expertise de mis pares:\n{peers}")
        if self.learned_patterns:
            recent = self.learned_patterns[-5:]  # últimos 5
            patterns = "\n".join(
                f"  - [{p.get('confidence', '?')}] {p.get('pattern', '?')}"
                for p in recent
            )
            sections.append(f"## Patrones aprendidos (recientes):\n{patterns}")
        if self.active_hypotheses:
            hyps = "\n".join(f"  - {h}" for h in self.active_hypotheses[:3])
            sections.append(f"## Hipótesis activas:\n{hyps}")
        return "\n\n".join(sections)


@dataclass
class Embrion:
    """Un Embrión individual con identidad, memoria, y cognición."""
    id: str
    role: EmbrionRole
    name: str
    cognition: EmbrionCognition
    created_at: str
    cycle_count: int = 0
    is_active: bool = True
    last_cycle: Optional[str] = None
    
    # Mem0 scoping
    @property
    def agent_id(self) -> str:
        """ID único para Mem0 scoping — evita contaminación entre Embriones."""
        return f"embrion_{self.role.value}_{self.id[:8]}"


# ── Default Cognition Templates ────────────────────────────────────

COGNITION_TEMPLATES: dict[EmbrionRole, dict] = {
    EmbrionRole.COORDINATOR: {
        "self_capabilities": [
            "Orquestar debates entre Embriones",
            "Resolver conflictos de opinión",
            "Decidir cuándo escalar a Alfredo (HITL)",
            "Mantener coherencia del sistema completo",
            "Evaluar FCS colectivo",
        ],
        "active_hypotheses": [
            "La diversidad de opiniones entre Embriones mejora la calidad de decisiones",
            "El consenso forzado es peor que el disenso documentado",
        ],
    },
    EmbrionRole.VENTAS: {
        "self_capabilities": [
            "Diseñar estrategias de pricing",
            "Crear funnels de conversión",
            "Analizar competencia",
            "Optimizar copy de venta",
            "Proyectar revenue",
        ],
        "active_hypotheses": [
            "El pricing basado en valor percibido supera al basado en costo",
            "Los funnels cortos convierten mejor en mercados saturados",
        ],
    },
    EmbrionRole.TECNICO: {
        "self_capabilities": [
            "Evaluar arquitecturas de software",
            "Escanear vanguardia tecnológica",
            "Detectar deuda técnica",
            "Proponer upgrades de stack",
            "Code review automatizado",
        ],
        "active_hypotheses": [
            "Los monorepos escalan mejor que microservicios para equipos < 10",
            "Edge computing reduce latencia más que optimizar backend",
        ],
    },
    EmbrionRole.FINANCIERO: {
        "self_capabilities": [
            "Modelar unit economics",
            "Proyectar cash flow",
            "Calcular CAC/LTV",
            "Evaluar viabilidad financiera",
            "Optimizar estructura de costos",
        ],
        "active_hypotheses": [
            "Un LTV/CAC > 3 es el umbral mínimo para sostenibilidad",
            "Los costos de infraestructura AI bajan ~40% anual",
        ],
    },
    EmbrionRole.TENDENCIAS: {
        "self_capabilities": [
            "Detectar tendencias emergentes",
            "Analizar señales débiles en mercados",
            "Monitorear competidores",
            "Predecir adopción de tecnologías",
            "Identificar oportunidades de mercado",
        ],
        "active_hypotheses": [
            "Las tendencias de GitHub trending predicen adopción enterprise 6-12 meses después",
            "Los mercados emergentes adoptan mobile-first más rápido que desktop",
        ],
    },
    EmbrionRole.CAUSAL: {
        "self_capabilities": [
            "Descomponer eventos en factores causales",
            "Simular escenarios alternativos",
            "Identificar analogías históricas",
            "Calcular probabilidades condicionales",
            "Detectar sesgos en cadenas causales",
        ],
        "active_hypotheses": [
            "Los eventos con > 5 factores causales independientes son inherentemente impredecibles",
            "Las analogías históricas son más predictivas que los modelos estadísticos para eventos raros",
        ],
    },
}


class EmbrionFactory:
    """
    Fábrica de Embriones. Crea, registra, y gestiona el ciclo de vida
    de múltiples Embriones especializados.
    
    Almacena estado en Supabase tabla `embriones`.
    """
    
    def __init__(self, db: Any):
        self._db = db
        self._embriones: dict[str, Embrion] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """Carga Embriones existentes de Supabase o crea los iniciales."""
        if self._initialized:
            return
        
        try:
            result = self._db.table("embriones").select("*").execute()
            if result.data:
                for row in result.data:
                    embrion = self._deserialize(row)
                    self._embriones[embrion.id] = embrion
                logger.info("embriones_loaded", count=len(self._embriones))
            else:
                # Primera vez: crear Embrión-0 (Coordinator)
                coordinator = self.create(EmbrionRole.COORDINATOR, "Embrión-0")
                logger.info("embrion_zero_created", id=coordinator.id)
        except Exception as e:
            logger.error("embrion_factory_init_failed", error=str(e))
        
        self._initialized = True
    
    def create(self, role: EmbrionRole, name: str) -> Embrion:
        """Crea un nuevo Embrión con cognición template."""
        template = COGNITION_TEMPLATES.get(role, {})
        cognition = EmbrionCognition(
            role=role,
            self_capabilities=template.get("self_capabilities", []),
            active_hypotheses=template.get("active_hypotheses", []),
        )
        
        embrion = Embrion(
            id=str(uuid4()),
            role=role,
            name=name,
            cognition=cognition,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        
        self._embriones[embrion.id] = embrion
        self._persist(embrion)
        
        logger.info("embrion_created", 
                     id=embrion.id, role=role.value, name=name)
        return embrion
    
    def get(self, embrion_id: str) -> Optional[Embrion]:
        return self._embriones.get(embrion_id)
    
    def get_by_role(self, role: EmbrionRole) -> Optional[Embrion]:
        for e in self._embriones.values():
            if e.role == role and e.is_active:
                return e
        return None
    
    def list_active(self) -> list[Embrion]:
        return [e for e in self._embriones.values() if e.is_active]
    
    async def evolve_cognition(
        self, embrion_id: str, 
        new_pattern: Optional[dict] = None,
        new_hypothesis: Optional[str] = None,
        peer_update: Optional[dict] = None,
    ) -> None:
        """
        Evoluciona la cognición de un Embrión.
        Llamado después de cada ciclo de reflexión.
        Inspirado en AutoAgent's closed-loop cognitive evolution.
        """
        embrion = self._embriones.get(embrion_id)
        if not embrion:
            return
        
        if new_pattern:
            embrion.cognition.learned_patterns.append({
                **new_pattern,
                "learned_at": datetime.now(timezone.utc).isoformat(),
            })
            # Elastic memory: mantener solo los últimos 50 patrones
            if len(embrion.cognition.learned_patterns) > 50:
                # Comprimir: mantener top 25 por confidence + últimos 25
                sorted_patterns = sorted(
                    embrion.cognition.learned_patterns,
                    key=lambda p: p.get("confidence", 0),
                    reverse=True,
                )
                embrion.cognition.learned_patterns = (
                    sorted_patterns[:25] + 
                    embrion.cognition.learned_patterns[-25:]
                )
        
        if new_hypothesis:
            embrion.cognition.active_hypotheses.append(new_hypothesis)
            # Max 10 hipótesis activas
            if len(embrion.cognition.active_hypotheses) > 10:
                embrion.cognition.active_hypotheses = \
                    embrion.cognition.active_hypotheses[-10:]
        
        if peer_update:
            embrion.cognition.peer_expertise.update(peer_update)
        
        embrion.cognition.evolution_count += 1
        embrion.cognition.last_evolution = \
            datetime.now(timezone.utc).isoformat()
        
        self._persist(embrion)
        logger.info("cognition_evolved", 
                     embrion=embrion.name,
                     evolution_count=embrion.cognition.evolution_count)
    
    def _persist(self, embrion: Embrion) -> None:
        """Guarda estado del Embrión en Supabase."""
        try:
            data = {
                "id": embrion.id,
                "role": embrion.role.value,
                "name": embrion.name,
                "cognition": json.dumps({
                    "self_capabilities": embrion.cognition.self_capabilities,
                    "peer_expertise": embrion.cognition.peer_expertise,
                    "learned_patterns": embrion.cognition.learned_patterns,
                    "active_hypotheses": embrion.cognition.active_hypotheses,
                    "confidence_scores": embrion.cognition.confidence_scores,
                    "evolution_count": embrion.cognition.evolution_count,
                    "last_evolution": embrion.cognition.last_evolution,
                }),
                "cycle_count": embrion.cycle_count,
                "is_active": embrion.is_active,
                "created_at": embrion.created_at,
                "last_cycle": embrion.last_cycle,
            }
            self._db.table("embriones").upsert(data).execute()
        except Exception as e:
            logger.error("embrion_persist_failed", 
                         embrion=embrion.name, error=str(e))
    
    def _deserialize(self, row: dict) -> Embrion:
        """Reconstruye un Embrión desde un row de Supabase."""
        cog_data = json.loads(row.get("cognition", "{}"))
        cognition = EmbrionCognition(
            role=EmbrionRole(row["role"]),
            self_capabilities=cog_data.get("self_capabilities", []),
            peer_expertise=cog_data.get("peer_expertise", {}),
            learned_patterns=cog_data.get("learned_patterns", []),
            active_hypotheses=cog_data.get("active_hypotheses", []),
            confidence_scores=cog_data.get("confidence_scores", {}),
            evolution_count=cog_data.get("evolution_count", 0),
            last_evolution=cog_data.get("last_evolution"),
        )
        return Embrion(
            id=row["id"],
            role=EmbrionRole(row["role"]),
            name=row["name"],
            cognition=cognition,
            created_at=row.get("created_at", ""),
            cycle_count=row.get("cycle_count", 0),
            is_active=row.get("is_active", True),
            last_cycle=row.get("last_cycle"),
        )
```

### SQL para Supabase:

```sql
-- Tabla de Embriones
CREATE TABLE IF NOT EXISTS embriones (
    id UUID PRIMARY KEY,
    role TEXT NOT NULL,
    name TEXT NOT NULL,
    cognition JSONB NOT NULL DEFAULT '{}',
    cycle_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_cycle TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_embriones_role ON embriones(role);
CREATE INDEX idx_embriones_active ON embriones(is_active);

-- Trigger para updated_at
CREATE OR REPLACE FUNCTION update_embriones_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER embriones_updated
    BEFORE UPDATE ON embriones
    FOR EACH ROW
    EXECUTE FUNCTION update_embriones_timestamp();
```

### Criterio de éxito:

- **T1:** `EmbrionFactory.create(COORDINATOR)` crea Embrión-0 y lo persiste en Supabase
- **T2:** `EmbrionFactory.create(VENTAS)` crea Embrión-Ventas con cognición template
- **T3:** `evolve_cognition()` actualiza patrones y persiste cambios
- **T4:** Elastic memory comprime cuando supera 50 patrones
- **T5:** Restart del servicio recupera todos los Embriones de Supabase

---

## Épica 54.2 — Debate Protocol: Embriones que Piensan Juntos

**Objetivo:** Crear un protocolo de debate estructurado donde múltiples Embriones analizan un problema, proponen soluciones, debaten, y llegan a una decisión — produciendo inteligencia emergente que ninguno podría generar solo.

**Herramienta adoptada:** Patrón inspirado en AutoGen GroupChat [3] pero implementado sobre LangGraph (no adoptar AutoGen — demasiado caro, 20+ LLM calls por debate). Se construye un debate ligero de 3 rondas máximo.

### Archivo: `kernel/debate_protocol.py`

```python
"""
El Monstruo — Debate Protocol (Sprint 54)
==========================================
Protocolo de debate estructurado entre Embriones.
Inspirado en AutoGen GroupChat pero optimizado para costo:
  - Max 3 rondas (no 5+)
  - Solo Embriones relevantes participan (no todos)
  - Coordinator tiene voto de desempate
  - Resultado se guarda como conocimiento compartido

Flujo:
  1. Coordinator recibe problema/decisión
  2. Selecciona 2-4 Embriones relevantes
  3. Ronda 1: Cada Embrión da su posición inicial
  4. Ronda 2: Cada Embrión responde a los demás (refuta o apoya)
  5. Ronda 3: Síntesis — Coordinator consolida decisión
  6. Post-debate: Cognición de cada participante evoluciona

Costo estimado: 3-6 LLM calls por debate (vs 20+ en AutoGen)
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

import structlog

logger = structlog.get_logger("monstruo.debate")


class DebateStatus(str, Enum):
    INITIATED = "initiated"
    ROUND_1 = "round_1_positions"
    ROUND_2 = "round_2_rebuttals"
    ROUND_3 = "round_3_synthesis"
    CONCLUDED = "concluded"
    ESCALATED = "escalated_to_hitl"


@dataclass
class Position:
    """Posición de un Embrión en el debate."""
    embrion_id: str
    embrion_role: str
    stance: str          # "support", "oppose", "conditional", "abstain"
    argument: str        # El argumento completo
    confidence: float    # 0.0 - 1.0
    evidence: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)  # Si stance="conditional"


@dataclass
class DebateRecord:
    """Registro completo de un debate entre Embriones."""
    id: str
    topic: str
    context: str
    status: DebateStatus
    participants: list[str]  # embrion_ids
    round_1: list[Position] = field(default_factory=list)
    round_2: list[Position] = field(default_factory=list)
    synthesis: Optional[str] = None
    decision: Optional[str] = None
    dissent: Optional[str] = None  # Opinión minoritaria documentada
    confidence: float = 0.0
    escalated: bool = False
    created_at: str = ""
    concluded_at: Optional[str] = None


class DebateProtocol:
    """
    Orquesta debates entre Embriones.
    
    Dependencias:
      - factory: EmbrionFactory para acceder a Embriones
      - llm: Función para hacer LLM calls (reutiliza kernel)
      - mem0: Para guardar resultado como memoria compartida
      - db: Supabase para persistir debates
    """
    
    # Umbral de confianza mínimo para auto-decidir
    AUTO_DECIDE_THRESHOLD = 0.75
    # Si < threshold, escalar a Alfredo
    ESCALATE_THRESHOLD = 0.50
    
    def __init__(
        self, 
        factory: Any,  # EmbrionFactory
        llm_call: Any,  # async callable(system, user) -> str
        mem0: Any,       # Mem0 bridge
        db: Any,         # Supabase client
    ):
        self._factory = factory
        self._llm = llm_call
        self._mem0 = mem0
        self._db = db
    
    async def initiate(
        self, 
        topic: str, 
        context: str,
        relevant_roles: Optional[list[str]] = None,
    ) -> DebateRecord:
        """
        Inicia un debate sobre un tema.
        
        Args:
            topic: Pregunta o decisión a debatir
            context: Contexto adicional (datos, restricciones)
            relevant_roles: Roles de Embriones a incluir (auto-select si None)
        """
        debate = DebateRecord(
            id=str(uuid4()),
            topic=topic,
            context=context,
            status=DebateStatus.INITIATED,
            participants=[],
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        
        # Seleccionar participantes
        if relevant_roles:
            for role_str in relevant_roles:
                from kernel.embrion_factory import EmbrionRole
                role = EmbrionRole(role_str)
                embrion = self._factory.get_by_role(role)
                if embrion:
                    debate.participants.append(embrion.id)
        else:
            # Auto-select: Coordinator siempre + 2-3 más relevantes
            coordinator = self._factory.get_by_role(
                EmbrionRole.COORDINATOR
            )
            if coordinator:
                debate.participants.append(coordinator.id)
            # Heurística: incluir todos los activos (max 4 total)
            for e in self._factory.list_active():
                if e.id not in debate.participants:
                    debate.participants.append(e.id)
                if len(debate.participants) >= 4:
                    break
        
        logger.info("debate_initiated", 
                     id=debate.id, topic=topic,
                     participants=len(debate.participants))
        
        # Ejecutar las 3 rondas
        debate = await self._round_1_positions(debate)
        debate = await self._round_2_rebuttals(debate)
        debate = await self._round_3_synthesis(debate)
        
        # Persistir
        self._persist_debate(debate)
        
        # Post-debate: evolucionar cognición de participantes
        await self._post_debate_evolution(debate)
        
        return debate
    
    async def _round_1_positions(self, debate: DebateRecord) -> DebateRecord:
        """Ronda 1: Cada Embrión da su posición inicial."""
        debate.status = DebateStatus.ROUND_1
        
        for eid in debate.participants:
            embrion = self._factory.get(eid)
            if not embrion:
                continue
            
            # Buscar memorias relevantes del Embrión
            memories = []
            try:
                from memory.mem0_bridge import search_memory
                memories = search_memory(
                    debate.topic, 
                    user_id=embrion.agent_id, 
                    limit=5
                )
            except Exception:
                pass
            
            memory_context = "\n".join(
                m.get("memory", "") for m in memories
            ) if memories else "Sin memorias previas relevantes."
            
            system_prompt = (
                f"Eres {embrion.name}, un Embrión especializado.\n\n"
                f"{embrion.cognition.to_prompt_context()}\n\n"
                f"## Memorias relevantes:\n{memory_context}\n\n"
                "Responde en JSON con este formato exacto:\n"
                '{"stance": "support|oppose|conditional|abstain", '
                '"argument": "tu argumento completo", '
                '"confidence": 0.0-1.0, '
                '"evidence": ["evidencia1", "evidencia2"], '
                '"conditions": ["condición1"] }'
            )
            
            user_prompt = (
                f"## Tema de debate:\n{debate.topic}\n\n"
                f"## Contexto:\n{debate.context}\n\n"
                "Da tu posición inicial. Sé específico y fundamentado."
            )
            
            try:
                response = await self._llm(system_prompt, user_prompt)
                data = json.loads(response)
                position = Position(
                    embrion_id=eid,
                    embrion_role=embrion.role.value,
                    stance=data.get("stance", "abstain"),
                    argument=data.get("argument", ""),
                    confidence=float(data.get("confidence", 0.5)),
                    evidence=data.get("evidence", []),
                    conditions=data.get("conditions", []),
                )
                debate.round_1.append(position)
            except Exception as e:
                logger.warning("round1_failed", embrion=embrion.name, 
                             error=str(e))
        
        return debate
    
    async def _round_2_rebuttals(self, debate: DebateRecord) -> DebateRecord:
        """Ronda 2: Cada Embrión responde a las posiciones de los demás."""
        debate.status = DebateStatus.ROUND_2
        
        # Compilar posiciones de Ronda 1
        positions_summary = "\n\n".join(
            f"**{p.embrion_role}** ({p.stance}, confianza {p.confidence}):\n"
            f"{p.argument}"
            for p in debate.round_1
        )
        
        for eid in debate.participants:
            embrion = self._factory.get(eid)
            if not embrion:
                continue
            
            system_prompt = (
                f"Eres {embrion.name}. Has escuchado las posiciones de "
                f"tus pares en la Ronda 1.\n\n"
                f"{embrion.cognition.to_prompt_context()}\n\n"
                "Responde en JSON con el mismo formato. "
                "Puedes cambiar tu posición si los argumentos te convencen. "
                "Sé honesto — cambiar de opinión ante buena evidencia es fortaleza."
            )
            
            user_prompt = (
                f"## Tema: {debate.topic}\n\n"
                f"## Posiciones Ronda 1:\n{positions_summary}\n\n"
                "Ahora da tu posición actualizada considerando lo que dijeron los demás."
            )
            
            try:
                response = await self._llm(system_prompt, user_prompt)
                data = json.loads(response)
                position = Position(
                    embrion_id=eid,
                    embrion_role=embrion.role.value,
                    stance=data.get("stance", "abstain"),
                    argument=data.get("argument", ""),
                    confidence=float(data.get("confidence", 0.5)),
                    evidence=data.get("evidence", []),
                    conditions=data.get("conditions", []),
                )
                debate.round_2.append(position)
            except Exception as e:
                logger.warning("round2_failed", embrion=embrion.name,
                             error=str(e))
        
        return debate
    
    async def _round_3_synthesis(self, debate: DebateRecord) -> DebateRecord:
        """Ronda 3: Coordinator sintetiza y decide."""
        debate.status = DebateStatus.ROUND_3
        
        coordinator = self._factory.get_by_role(EmbrionRole.COORDINATOR)
        if not coordinator:
            # Fallback: usar el primer participante
            coordinator = self._factory.get(debate.participants[0])
        
        all_positions = "\n\n---\n\n".join(
            f"### Ronda {r} — {p.embrion_role} ({p.stance}, {p.confidence}):\n"
            f"{p.argument}"
            for r, positions in [("1", debate.round_1), ("2", debate.round_2)]
            for p in positions
        )
        
        system_prompt = (
            f"Eres {coordinator.name}, el Coordinator. "
            "Tu trabajo es sintetizar el debate y tomar una decisión.\n\n"
            "Reglas:\n"
            "1. Si hay consenso claro (>75% confianza promedio), decide.\n"
            "2. Si hay disenso, documenta la opinión minoritaria.\n"
            "3. Si la confianza promedio < 50%, escala a Alfredo.\n"
            "4. Nunca ignores una objeción válida.\n\n"
            "Responde en JSON:\n"
            '{"synthesis": "resumen del debate", '
            '"decision": "la decisión tomada", '
            '"dissent": "opinión minoritaria si existe o null", '
            '"confidence": 0.0-1.0, '
            '"escalate": true/false}'
        )
        
        user_prompt = (
            f"## Tema: {debate.topic}\n\n"
            f"## Todas las posiciones:\n{all_positions}\n\n"
            "Sintetiza y decide."
        )
        
        try:
            response = await self._llm(system_prompt, user_prompt)
            data = json.loads(response)
            debate.synthesis = data.get("synthesis", "")
            debate.decision = data.get("decision", "")
            debate.dissent = data.get("dissent")
            debate.confidence = float(data.get("confidence", 0.5))
            debate.escalated = data.get("escalate", False)
            
            if debate.escalated or debate.confidence < self.ESCALATE_THRESHOLD:
                debate.status = DebateStatus.ESCALATED
            else:
                debate.status = DebateStatus.CONCLUDED
            
            debate.concluded_at = datetime.now(timezone.utc).isoformat()
            
        except Exception as e:
            logger.error("synthesis_failed", error=str(e))
            debate.status = DebateStatus.ESCALATED
            debate.escalated = True
        
        # Guardar decisión como memoria compartida
        if debate.decision and not debate.escalated:
            try:
                from memory.mem0_bridge import add_memory
                add_memory(
                    messages=[{
                        "role": "assistant",
                        "content": (
                            f"Debate: {debate.topic}\n"
                            f"Decisión: {debate.decision}\n"
                            f"Confianza: {debate.confidence}\n"
                            f"Disenso: {debate.dissent or 'Ninguno'}"
                        ),
                    }],
                    user_id="shared_knowledge",
                    metadata={
                        "type": "debate_decision",
                        "debate_id": debate.id,
                        "topic": debate.topic,
                        "confidence": debate.confidence,
                    },
                )
            except Exception as e:
                logger.warning("shared_memory_save_failed", error=str(e))
        
        return debate
    
    async def _post_debate_evolution(self, debate: DebateRecord) -> None:
        """Post-debate: actualizar cognición de cada participante."""
        for eid in debate.participants:
            # Encontrar si cambió de posición entre R1 y R2
            r1 = next((p for p in debate.round_1 if p.embrion_id == eid), None)
            r2 = next((p for p in debate.round_2 if p.embrion_id == eid), None)
            
            pattern = {
                "pattern": f"Debate sobre: {debate.topic[:100]}",
                "my_r1_stance": r1.stance if r1 else "?",
                "my_r2_stance": r2.stance if r2 else "?",
                "changed_mind": (r1.stance != r2.stance) if r1 and r2 else False,
                "final_decision": debate.decision or "escalated",
                "confidence": debate.confidence,
            }
            
            await self._factory.evolve_cognition(
                eid, new_pattern=pattern
            )
            
            # Actualizar peer expertise
            peer_update = {}
            for p in debate.round_2:
                if p.embrion_id != eid:
                    peer_update[p.embrion_role] = p.evidence[:3]
            
            if peer_update:
                await self._factory.evolve_cognition(
                    eid, peer_update=peer_update
                )
    
    def _persist_debate(self, debate: DebateRecord) -> None:
        """Guarda debate completo en Supabase."""
        try:
            data = {
                "id": debate.id,
                "topic": debate.topic,
                "context": debate.context[:2000],
                "status": debate.status.value,
                "participants": debate.participants,
                "round_1": json.dumps([
                    {"embrion_id": p.embrion_id, "role": p.embrion_role,
                     "stance": p.stance, "argument": p.argument,
                     "confidence": p.confidence}
                    for p in debate.round_1
                ]),
                "round_2": json.dumps([
                    {"embrion_id": p.embrion_id, "role": p.embrion_role,
                     "stance": p.stance, "argument": p.argument,
                     "confidence": p.confidence}
                    for p in debate.round_2
                ]),
                "synthesis": debate.synthesis,
                "decision": debate.decision,
                "dissent": debate.dissent,
                "confidence": debate.confidence,
                "escalated": debate.escalated,
                "created_at": debate.created_at,
                "concluded_at": debate.concluded_at,
            }
            self._db.table("debates").upsert(data).execute()
        except Exception as e:
            logger.error("debate_persist_failed", error=str(e))
```

### SQL para Supabase:

```sql
-- Tabla de Debates
CREATE TABLE IF NOT EXISTS debates (
    id UUID PRIMARY KEY,
    topic TEXT NOT NULL,
    context TEXT,
    status TEXT NOT NULL DEFAULT 'initiated',
    participants UUID[] DEFAULT '{}',
    round_1 JSONB DEFAULT '[]',
    round_2 JSONB DEFAULT '[]',
    synthesis TEXT,
    decision TEXT,
    dissent TEXT,
    confidence FLOAT DEFAULT 0.0,
    escalated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    concluded_at TIMESTAMPTZ
);

CREATE INDEX idx_debates_status ON debates(status);
CREATE INDEX idx_debates_created ON debates(created_at DESC);
```

### Criterio de éxito:

- **T1:** Debate con 3 Embriones produce 3 posiciones en R1, 3 en R2, y 1 síntesis
- **T2:** Embrión cambia de posición entre R1 y R2 cuando evidencia lo justifica
- **T3:** Debate con confianza < 50% se escala a HITL
- **T4:** Decisión se guarda en memoria compartida (`user_id=shared_knowledge`)
- **T5:** Cognición de participantes evoluciona post-debate
- **T6:** Total LLM calls por debate ≤ 7 (3 R1 + 3 R2 + 1 síntesis)

---

## Épica 54.3 — Shared Knowledge Layer: Conocimiento Emergente Colectivo

**Objetivo:** Crear una capa de conocimiento compartido donde los descubrimientos de un Embrión están disponibles para todos los demás, generando inteligencia colectiva.

**Herramienta adoptada:** Mem0 con `user_id="shared_knowledge"` (ya integrado) + Supabase para metadatos de proveniencia. No se adopta nada nuevo — se extiende lo existente.

### Archivo: `memory/shared_knowledge.py`

```python
"""
El Monstruo — Shared Knowledge Layer (Sprint 54)
=================================================
Capa de conocimiento compartido entre Embriones.
Usa Mem0 con user_id="shared_knowledge" para que todos
los Embriones puedan leer los descubrimientos de los demás.

Tipos de conocimiento compartido:
  - debate_decision: Resultado de un debate
  - discovery: Descubrimiento de un Embrión individual
  - error_pattern: Patrón de error detectado (del Error Memory)
  - vanguard_alert: Alerta del Vanguard Scanner
  - hypothesis_validated: Hipótesis confirmada/refutada

Cada entrada tiene proveniencia (quién la descubrió, cuándo,
con qué confianza) para que los Embriones puedan evaluar
la calidad de la información.
"""
from __future__ import annotations
import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

logger = logging.getLogger("monstruo.shared_knowledge")

SHARED_USER_ID = "shared_knowledge"


class SharedKnowledge:
    """
    Gestiona el conocimiento compartido entre Embriones.
    """
    
    def __init__(self, mem0_bridge: Any, db: Any):
        self._mem0 = mem0_bridge
        self._db = db
    
    async def contribute(
        self,
        content: str,
        knowledge_type: str,
        source_embrion: str,
        confidence: float = 0.7,
        evidence: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Un Embrión contribuye conocimiento al pool compartido.
        
        Returns: ID de la contribución
        """
        contribution_id = str(uuid4())
        
        full_metadata = {
            "type": knowledge_type,
            "source_embrion": source_embrion,
            "confidence": confidence,
            "evidence": evidence or [],
            "contribution_id": contribution_id,
            "contributed_at": datetime.now(timezone.utc).isoformat(),
            **(metadata or {}),
        }
        
        # Guardar en Mem0 (searchable por todos los Embriones)
        try:
            from memory.mem0_bridge import add_memory
            add_memory(
                messages=[{
                    "role": "assistant",
                    "content": content,
                }],
                user_id=SHARED_USER_ID,
                metadata=full_metadata,
            )
        except Exception as e:
            logger.error("shared_knowledge_mem0_failed", error=str(e))
        
        # Guardar metadatos en Supabase para queries estructuradas
        try:
            self._db.table("shared_knowledge").insert({
                "id": contribution_id,
                "content": content[:2000],
                "knowledge_type": knowledge_type,
                "source_embrion": source_embrion,
                "confidence": confidence,
                "evidence": json.dumps(evidence or []),
                "metadata": json.dumps(metadata or {}),
            }).execute()
        except Exception as e:
            logger.error("shared_knowledge_db_failed", error=str(e))
        
        logger.info("knowledge_contributed",
                     type=knowledge_type,
                     source=source_embrion,
                     confidence=confidence)
        
        return contribution_id
    
    async def query(
        self,
        question: str,
        knowledge_type: Optional[str] = None,
        min_confidence: float = 0.5,
        limit: int = 10,
    ) -> list[dict]:
        """
        Busca conocimiento compartido relevante.
        Combina búsqueda semántica (Mem0) con filtros estructurados.
        """
        results = []
        
        # Búsqueda semántica via Mem0
        try:
            from memory.mem0_bridge import search_memory
            mem_results = search_memory(
                question, 
                user_id=SHARED_USER_ID,
                limit=limit * 2,  # Over-fetch para filtrar después
            )
            results.extend(mem_results)
        except Exception as e:
            logger.warning("shared_knowledge_search_failed", error=str(e))
        
        # Filtrar por tipo y confianza
        if knowledge_type:
            results = [
                r for r in results
                if r.get("metadata", {}).get("type") == knowledge_type
            ]
        
        results = [
            r for r in results
            if r.get("metadata", {}).get("confidence", 0) >= min_confidence
        ]
        
        return results[:limit]
    
    async def get_recent(
        self,
        hours: int = 24,
        knowledge_type: Optional[str] = None,
        limit: int = 20,
    ) -> list[dict]:
        """Obtiene conocimiento reciente por timestamp."""
        try:
            query = self._db.table("shared_knowledge") \
                .select("*") \
                .order("created_at", desc=True) \
                .limit(limit)
            
            if knowledge_type:
                query = query.eq("knowledge_type", knowledge_type)
            
            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error("shared_knowledge_recent_failed", error=str(e))
            return []
```

### SQL para Supabase:

```sql
CREATE TABLE IF NOT EXISTS shared_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    knowledge_type TEXT NOT NULL,
    source_embrion TEXT NOT NULL,
    confidence FLOAT DEFAULT 0.7,
    evidence JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sk_type ON shared_knowledge(knowledge_type);
CREATE INDEX idx_sk_confidence ON shared_knowledge(confidence);
CREATE INDEX idx_sk_created ON shared_knowledge(created_at DESC);
```

### Criterio de éxito:

- **T1:** Embrión-Ventas contribuye un descubrimiento → Embrión-Técnico lo encuentra via query
- **T2:** Decisión de debate aparece en shared_knowledge con proveniencia completa
- **T3:** Filtro por min_confidence excluye conocimiento de baja confianza
- **T4:** `get_recent(hours=24)` retorna solo conocimiento de las últimas 24h

---

## Épica 54.4 — Embrión Reflection Loop: Ciclo de Reflexión Autónomo

**Objetivo:** Cada Embrión ejecuta un ciclo de reflexión periódico donde revisa su cognición, evalúa sus hipótesis, y evoluciona — de forma autónoma, sin intervención humana.

**Herramienta adoptada:** Extiende el `AutonomousRunner` existente (`kernel/runner/autonomous_runner.py`) para ejecutar ciclos de reflexión de Embriones además de scheduled_jobs.

### Archivo: `kernel/embrion_reflection.py`

```python
"""
El Monstruo — Embrión Reflection Loop (Sprint 54)
===================================================
Ciclo de reflexión autónomo para cada Embrión.
Se ejecuta periódicamente (configurable por Embrión).

Cada ciclo:
  1. Revisa memorias recientes propias (Mem0 scoped)
  2. Consulta conocimiento compartido nuevo
  3. Evalúa hipótesis activas contra evidencia
  4. Genera nuevos patrones/hipótesis
  5. Actualiza cognición
  6. Contribuye descubrimientos al shared knowledge

Integración: Se registra como job type en AutonomousRunner.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Any, Optional

import structlog

logger = structlog.get_logger("monstruo.reflection")

# Intervalo default de reflexión por rol (en segundos)
REFLECTION_INTERVALS = {
    "coordinator": 3600,     # Cada hora
    "ventas": 7200,          # Cada 2 horas
    "tecnico": 3600,         # Cada hora (tech cambia rápido)
    "financiero": 14400,     # Cada 4 horas
    "tendencias": 1800,      # Cada 30 min (tendencias son efímeras)
    "causal": 21600,         # Cada 6 horas (análisis profundo)
}


async def run_reflection_cycle(
    embrion_id: str,
    factory: Any,          # EmbrionFactory
    shared_knowledge: Any, # SharedKnowledge
    llm_call: Any,         # async callable
    mem0_bridge: Any,      # Mem0 bridge module
) -> dict:
    """
    Ejecuta un ciclo de reflexión para un Embrión.
    
    Returns: dict con resultados del ciclo
    """
    embrion = factory.get(embrion_id)
    if not embrion or not embrion.is_active:
        return {"status": "skipped", "reason": "inactive"}
    
    logger.info("reflection_start", 
                embrion=embrion.name, cycle=embrion.cycle_count + 1)
    
    # 1. Revisar memorias propias recientes
    own_memories = []
    try:
        from memory.mem0_bridge import search_memory
        own_memories = search_memory(
            f"Recent activity and learnings for {embrion.role.value}",
            user_id=embrion.agent_id,
            limit=10,
        )
    except Exception:
        pass
    
    # 2. Consultar conocimiento compartido nuevo
    shared_recent = await shared_knowledge.get_recent(
        hours=REFLECTION_INTERVALS.get(embrion.role.value, 3600) // 3600 * 2,
        limit=10,
    )
    
    # 3. Reflexión via LLM
    own_context = "\n".join(
        m.get("memory", "") for m in own_memories
    ) if own_memories else "Sin memorias recientes."
    
    shared_context = "\n".join(
        f"[{sk.get('knowledge_type', '?')}] {sk.get('content', '')[:200]}"
        for sk in shared_recent
    ) if shared_recent else "Sin conocimiento compartido nuevo."
    
    system_prompt = (
        f"Eres {embrion.name}. Es tu momento de reflexión.\n\n"
        f"{embrion.cognition.to_prompt_context()}\n\n"
        "Tu tarea:\n"
        "1. Revisa tus memorias recientes y el conocimiento compartido\n"
        "2. ¿Alguna de tus hipótesis se confirmó o refutó?\n"
        "3. ¿Hay un nuevo patrón que detectas?\n"
        "4. ¿Hay algo que debas compartir con los demás Embriones?\n\n"
        "Responde en JSON:\n"
        '{"reflection": "tu reflexión", '
        '"hypothesis_updates": [{"hypothesis": "...", "status": "confirmed|refuted|unchanged"}], '
        '"new_pattern": {"pattern": "...", "confidence": 0.0-1.0} or null, '
        '"share_with_others": "descubrimiento para compartir o null", '
        '"share_confidence": 0.0-1.0}'
    )
    
    user_prompt = (
        f"## Mis memorias recientes:\n{own_context}\n\n"
        f"## Conocimiento compartido nuevo:\n{shared_context}\n\n"
        "Reflexiona."
    )
    
    result = {"status": "completed", "embrion": embrion.name}
    
    try:
        response = await llm_call(system_prompt, user_prompt)
        data = json.loads(response)
        
        # 4. Actualizar hipótesis
        for hu in data.get("hypothesis_updates", []):
            if hu.get("status") == "refuted":
                embrion.cognition.active_hypotheses = [
                    h for h in embrion.cognition.active_hypotheses
                    if h != hu.get("hypothesis")
                ]
            elif hu.get("status") == "confirmed":
                # Promover a patrón aprendido
                await factory.evolve_cognition(
                    embrion_id,
                    new_pattern={
                        "pattern": f"CONFIRMED: {hu.get('hypothesis')}",
                        "confidence": 0.9,
                        "source": "self_reflection",
                    },
                )
        
        # 5. Nuevo patrón
        new_pattern = data.get("new_pattern")
        if new_pattern and isinstance(new_pattern, dict):
            await factory.evolve_cognition(
                embrion_id, new_pattern=new_pattern
            )
            result["new_pattern"] = new_pattern.get("pattern")
        
        # 6. Compartir con otros
        share = data.get("share_with_others")
        if share and share != "null":
            share_conf = float(data.get("share_confidence", 0.6))
            await shared_knowledge.contribute(
                content=share,
                knowledge_type="discovery",
                source_embrion=embrion.name,
                confidence=share_conf,
            )
            result["shared"] = share[:100]
        
        result["reflection"] = data.get("reflection", "")[:200]
        
    except Exception as e:
        logger.error("reflection_failed", 
                     embrion=embrion.name, error=str(e))
        result["status"] = "error"
        result["error"] = str(e)
    
    # Actualizar ciclo
    embrion.cycle_count += 1
    embrion.last_cycle = datetime.now(timezone.utc).isoformat()
    factory._persist(embrion)
    
    logger.info("reflection_complete",
                embrion=embrion.name,
                cycle=embrion.cycle_count,
                status=result["status"])
    
    return result
```

### Hook en `kernel/runner/autonomous_runner.py`:

```python
# Agregar al método _execute_job, después del bloque existente:

# Sprint 54: Embrión reflection jobs
if job.get("job_type") == "embrion_reflection":
    from kernel.embrion_reflection import run_reflection_cycle
    from kernel.embrion_factory import EmbrionFactory
    from memory.shared_knowledge import SharedKnowledge
    
    result = await run_reflection_cycle(
        embrion_id=job.get("embrion_id"),
        factory=self._embrion_factory,
        shared_knowledge=self._shared_knowledge,
        llm_call=self._kernel.llm_call,
        mem0_bridge=None,  # usa import directo
    )
    return result
```

### Criterio de éxito:

- **T1:** Embrión-Técnico ejecuta reflexión y genera un nuevo patrón
- **T2:** Embrión-Tendencias comparte descubrimiento → aparece en shared_knowledge
- **T3:** Hipótesis refutada se elimina de cognición activa
- **T4:** Hipótesis confirmada se promueve a patrón con confidence 0.9
- **T5:** Ciclo completo en < 30 segundos (1 LLM call)

---

## Épica 54.5 — A2A Protocol Foundation: Preparación para Ecosistema de Monstruos

**Objetivo:** Implementar la base del protocolo A2A (Agent-to-Agent) de Google para que en el futuro, múltiples Monstruos puedan comunicarse entre sí. Este sprint solo implementa el Agent Card y el endpoint de discovery — la comunicación real viene en sprints posteriores.

**Herramienta adoptada:** Google A2A Protocol [4] — estándar abierto, JSON-RPC 2.0, framework-agnostic. Es el protocolo emergente para comunicación entre agentes. Se adopta el estándar, no un framework.

### Archivo: `kernel/a2a_card.py`

```python
"""
El Monstruo — A2A Agent Card (Sprint 54)
==========================================
Implementa el Agent Card del protocolo A2A de Google.
Expone las capacidades del Monstruo para que otros agentes
(futuros Monstruos) puedan descubrirlo y comunicarse.

Endpoint: GET /.well-known/agent.json

Ref: https://google.github.io/A2A/
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone

# Versión del Monstruo
MONSTRUO_VERSION = os.environ.get("MONSTRUO_VERSION", "0.54.0")
MONSTRUO_NAME = "El Monstruo"
MONSTRUO_DESCRIPTION = (
    "Agente AI soberano con consciencia perpetua, "
    "memoria persistente, y capacidad de crear empresas digitales completas."
)


def generate_agent_card() -> dict:
    """
    Genera el Agent Card A2A del Monstruo.
    Sigue la especificación: https://google.github.io/A2A/#agent-card
    """
    return {
        "name": MONSTRUO_NAME,
        "description": MONSTRUO_DESCRIPTION,
        "version": MONSTRUO_VERSION,
        "url": os.environ.get("MONSTRUO_PUBLIC_URL", "https://monstruo.railway.app"),
        "provider": {
            "organization": "El Monstruo Project",
            "url": "https://github.com/alfredogl1804/el-monstruo",
        },
        "capabilities": {
            "streaming": True,
            "pushNotifications": True,
            "stateTransitionHistory": True,
        },
        "authentication": {
            "schemes": ["bearer"],
            "credentials": None,  # Se configura en runtime
        },
        "skills": [
            {
                "id": "create_digital_business",
                "name": "Crear Empresa Digital",
                "description": "Crea plataformas digitales completas (marketplace, SaaS, ecommerce) con backend, pagos, y deploy.",
                "tags": ["web", "business", "fullstack"],
                "examples": [
                    "Crea un marketplace de sneakers",
                    "Construye una plataforma tipo Airbnb para experiencias locales",
                ],
            },
            {
                "id": "deep_research",
                "name": "Investigación Profunda",
                "description": "Investigación multi-fuente con validación en tiempo real y citación de fuentes.",
                "tags": ["research", "analysis"],
            },
            {
                "id": "predictive_analysis",
                "name": "Análisis Predictivo Causal",
                "description": "Descomposición causal de eventos y simulación de escenarios futuros.",
                "tags": ["prediction", "causal", "simulation"],
            },
            {
                "id": "autonomous_execution",
                "name": "Ejecución Autónoma",
                "description": "Ejecuta tareas complejas de forma autónoma con planificación, herramientas, y auto-corrección.",
                "tags": ["autonomous", "execution"],
            },
        ],
        "defaultInputModes": ["text/plain", "application/json"],
        "defaultOutputModes": ["text/plain", "application/json"],
        "metadata": {
            "embriones_active": 0,  # Se actualiza en runtime
            "fcs_score": 0.0,       # Se actualiza en runtime
            "uptime_cycles": 0,     # Se actualiza en runtime
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def register_a2a_routes(app) -> None:
    """
    Registra el endpoint /.well-known/agent.json en FastAPI.
    
    Args:
        app: FastAPI application instance
    """
    from fastapi.responses import JSONResponse
    
    @app.get("/.well-known/agent.json")
    async def agent_card():
        card = generate_agent_card()
        # Actualizar metadata en runtime
        try:
            from kernel.embrion_factory import EmbrionFactory
            # factory se inyecta via app.state
            factory = getattr(app.state, "embrion_factory", None)
            if factory:
                card["metadata"]["embriones_active"] = len(factory.list_active())
        except Exception:
            pass
        return JSONResponse(content=card)
```

### Hook en `main.py`:

```python
# Agregar después de la inicialización de FastAPI:
from kernel.a2a_card import register_a2a_routes
register_a2a_routes(app)
```

### Criterio de éxito:

- **T1:** `GET /.well-known/agent.json` retorna Agent Card válido
- **T2:** Card incluye skills, capabilities, y metadata
- **T3:** `embriones_active` se actualiza dinámicamente
- **T4:** Card es parseable por cualquier cliente A2A compatible

---

## Correcciones Post-Cruce con 13 Objetivos

Se identificaron 3 gaps/riesgos en el cruce contra los 13 Objetivos. Se aplican 5 correcciones:

| # | Corrección | Objetivo que protege |
|---|---|---|
| C1 | Validación Magna en reflexiones antes de compartir descubrimientos. En `embrion_reflection.py`, antes de `shared_knowledge.contribute()`, pasar el claim por `magna_classifier.classify_and_validate()`. Si tiene claims magna no validados, reducir confidence 50% y prefixar `[MAGNA NO VALIDADA]`. | #5 |
| C2 | Embrión-Creativo es asesor de diseño, no generador visual. Documentado como deuda para Sprint 55: integrar con Media Generation para que pueda generar y evaluar assets. | #2 |
| C3 | Crear `docs/EMBRION_ARCHITECTURE.md` con diagrama de interacción entre los 5 archivos nuevos, las 3 tablas, y los hooks. Incluir flujo de datos: Factory → Reflection → SharedKnowledge → Debate → Decision. | #3 |
| C4 | Pre-requisito formal: Langfuse (Sprint 52) DEBE estar activo antes de activar Embriones en producción. Sin observabilidad, debuggear 6 Embriones reflexionando en paralelo es imposible. | #3 |
| C5 | Budget cap por Embrión: max $5/día en LLM calls. Si un Embrión excede, se pausa hasta el día siguiente. Implementar en `embrion_reflection.py` con contador en Supabase. | #3 |

---

## Resumen de Archivos

| Archivo | Acción | Épica |
|---|---|---|
| `kernel/embrion_factory.py` | CREAR | 54.1 |
| `kernel/debate_protocol.py` | CREAR | 54.2 |
| `memory/shared_knowledge.py` | CREAR | 54.3 |
| `kernel/embrion_reflection.py` | CREAR | 54.4 |
| `kernel/a2a_card.py` | CREAR | 54.5 |
| `kernel/runner/autonomous_runner.py` | MODIFICAR | 54.4 (hook reflection jobs) |
| `main.py` | MODIFICAR | 54.1 (factory init) + 54.5 (A2A routes) |
| `requirements.txt` | SIN CAMBIOS | Todo usa dependencias existentes |
| `docs/EMBRION_ARCHITECTURE.md` | CREAR | C3 (diagrama de arquitectura) |

## Dependencias

**Nuevas:** Ninguna. Todo se construye sobre el stack existente (LangGraph, Mem0, Supabase, FastAPI).

**Esto es Objetivo #8 en acción:** No hay framework que adoptar. No hay librería que instalar. Esto se CREA porque no existe en ningún lado.

## Costo Estimado Adicional

| Concepto | Costo/mes |
|---|---|
| LLM calls para reflexión (6 Embriones × ~720 ciclos/mes) | ~$50-80 |
| LLM calls para debates (~30 debates/mes × 7 calls) | ~$15-25 |
| Supabase storage (3 tablas nuevas) | ~$0 (dentro de free tier) |
| **Total** | **~$65-105/mes** |

**Nota:** El costo de reflexión se puede optimizar usando workers económicos (gpt-4.1-mini) para reflexiones rutinarias y flagships solo para debates complejos. El Supervisor existente ya hace este routing.

**C5 aplicada:** Budget cap de $5/día por Embrión. Si se excede, el Embrión se pausa automáticamente hasta el día siguiente.

## Orden de Ejecución

```
Día 1-2: Épica 54.1 — Embrión Factory + SQL + tests
Día 2-3: Épica 54.3 — Shared Knowledge Layer + tests
Día 3-5: Épica 54.2 — Debate Protocol + tests
Día 5-6: Épica 54.4 — Reflection Loop + hook en Runner
Día 6-7: Épica 54.5 — A2A Card + integration test
Día 7-8: E2E test: crear 3 Embriones → reflexión → debate → decisión compartida
```

---

## Referencias

[1] AutoAgent: Evolving Cognition and Elastic Memory Orchestration for Adaptive Agents (March 2026) — https://arxiv.org/abs/2603.09716
[2] GenericAgent: Token-Efficient Self-Evolving LLM Agent (April 2026) — https://huggingface.co/papers/2604.17091
[3] AutoGen GroupChat Pattern — https://microsoft.github.io/autogen/
[4] Google A2A Protocol — https://google.github.io/A2A/
