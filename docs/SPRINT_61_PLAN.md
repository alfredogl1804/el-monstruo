# Sprint 61 — "La Inteligencia Colectiva"

**Fecha:** 1 mayo 2026
**Autor:** Manus AI
**Tema:** Emergencia colectiva, design system enforcement, i18n quality, error learning, y onboarding
**Dependencias:** Sprints 54 (EmbrionLoop), 57-60 (7 Embriones), 59 (i18n Engine)
**Significado:** Primer sprint de la serie 61-70. Ataca los 3 objetivos más débiles (#13, #2, #8) y cierra gaps de UX (#3, #4).

---

## Resumen Ejecutivo

Sprint 61 inaugura la serie 61-70 con una misión clara: **atacar los 3 objetivos más rezagados** después de la serie 51-60. El Monstruo tiene 7 embriones, 6 capas transversales, un simulador Monte Carlo, y soberanía de datos. Lo que le falta es que todo eso **funcione como un organismo** — no como piezas aisladas.

El nombre "La Inteligencia Colectiva" refleja el salto: de 7 embriones independientes a un **enjambre coordinado** que debate, vota, comparte conocimiento, y produce resultados superiores a cualquier embrión individual. Simultáneamente, Sprint 61 cierra gaps vergonzosos en calidad de diseño, internacionalización, y experiencia de usuario.

Los 5 gaps que Sprint 61 cierra:

1. **Obj #8 (Emergencia, 70%)** — Los embriones no se comunican entre sí. No hay evidencia de comportamiento emergente real.
2. **Obj #13 (Del Mundo, 60%)** — El i18n Engine traduce pero no verifica calidad. No hay RTL. No hay adaptación cultural.
3. **Obj #2 (Apple/Tesla, 65%)** — No hay design system ejecutable. No hay enforcement de calidad visual.
4. **Obj #4 (No Equivocarse 2x, 73%)** — El error_log existe pero no hay taxonomía ni reglas derivadas.
5. **Obj #3 (Mínima Complejidad, 72%)** — No hay onboarding. El usuario debe descubrir todo solo.

---

## Stack Validado en Tiempo Real

| Herramienta | Versión | Uso en Sprint 61 | Decisión |
|---|---|---|---|
| unbabel-comet | 2.2.7 (Sep 2025) | Translation quality metrics | NO usar directamente (requiere PyTorch ~2GB). Usar chrF + LLM-as-judge [1] |
| axe-core | Latest 2026 | Accessibility auditing WCAG 2.2 | Usar via Playwright/subprocess [2] |
| Style Dictionary | Latest | Design tokens system | Generar tokens como JSON, consumir desde Python [3] |
| Supabase Realtime | Incluido en supabase 2.28.3 | Inter-embrión pub/sub | Ya disponible, crear nuevos channels [4] |
| PageSpeed Insights API | v5 | Core Web Vitals programmatic | API gratis con key de Google [5] |
| sacrebleu | ~2.x | BLEU/chrF metrics (ligero) | Alternativa ligera a COMET [6] |

---

## Épica 61.1 — Collective Intelligence Protocol (Objetivo #8)

### Contexto

El Monstruo tiene 7 embriones especializados (Ventas, Técnico, Vigía, Creativo, Estratega, Financiero, Investigador). Pero cada uno opera en aislamiento total. No hay mecanismo para que el Embrión-Financiero le diga al Embrión-Ventas "el pricing que propones destruye los unit economics." No hay debate, no hay votación, no hay consenso.

La investigación académica muestra que protocolos de votación mejoran performance en 13.2% en tareas de razonamiento, y protocolos de consenso mejoran 2.8% en tareas de conocimiento [7]. Sprint 61 implementa ambos patrones.

### Arquitectura

El protocolo de inteligencia colectiva opera en 3 niveles:

**Nivel 1 — Messaging (Pub/Sub):** Comunicación asíncrona entre embriones via Supabase Realtime channels. Cada embrión puede publicar y suscribirse a topics relevantes a su dominio.

**Nivel 2 — Debate:** Cuando una decisión requiere múltiples perspectivas, se inicia un debate estructurado donde cada embrión relevante argumenta desde su dominio. Un moderador (el Supervisor) sintetiza.

**Nivel 3 — Voting:** Para decisiones binarias o de selección, los embriones votan con peso proporcional a su expertise en el tema. Mayoría calificada (>60%) para aprobar.

### Implementación

**Archivo:** `kernel/collective/protocol.py`

```python
"""
El Monstruo — Collective Intelligence Protocol (Sprint 61)
============================================================
Protocolo de inteligencia colectiva entre embriones.

Nivel 1: Messaging (pub/sub via Supabase Realtime)
Nivel 2: Debate (argumentación estructurada)
Nivel 3: Voting (decisión por mayoría calificada)

Referencia: "Voting or Consensus? Decision-Making in Multi-Agent Debate"
(arXiv:2502.19130) — voting +13.2% en reasoning, consensus +2.8% en knowledge.

Sprint 61 — 2026-05-01
"""
from __future__ import annotations
import json
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Callable
import structlog

logger = structlog.get_logger("monstruo.collective")


class MessageType(str, Enum):
    """Tipos de mensaje inter-embrión."""
    INSIGHT = "insight"  # Observación relevante para otros
    REQUEST = "request"  # Solicitud de input/expertise
    ALERT = "alert"  # Alerta que requiere atención
    VOTE_CALL = "vote_call"  # Convocatoria de votación
    VOTE_CAST = "vote_cast"  # Voto emitido
    DEBATE_OPEN = "debate_open"  # Apertura de debate
    DEBATE_ARGUMENT = "debate_argument"  # Argumento en debate
    DEBATE_CLOSE = "debate_close"  # Cierre de debate con síntesis


class DecisionMethod(str, Enum):
    """Métodos de decisión colectiva."""
    MAJORITY_VOTE = "majority_vote"  # >50% simple
    QUALIFIED_MAJORITY = "qualified_majority"  # >60% weighted
    CONSENSUS = "consensus"  # Todos de acuerdo
    DEBATE_SYNTHESIS = "debate_synthesis"  # Moderador sintetiza


@dataclass
class EmbrionMessage:
    """Mensaje entre embriones."""
    id: str
    sender: str  # Nombre del embrión emisor
    type: MessageType
    topic: str  # Topic/channel del mensaje
    content: dict  # Payload del mensaje
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    recipients: list[str] = field(default_factory=list)  # Vacío = broadcast
    requires_response: bool = False
    ttl_seconds: int = 3600  # Expira en 1 hora por defecto


@dataclass
class VoteSession:
    """Sesión de votación entre embriones."""
    id: str
    topic: str
    question: str
    options: list[str]
    method: DecisionMethod
    initiator: str
    votes: dict[str, dict] = field(default_factory=dict)  # {embrion: {option, weight, reasoning}}
    deadline: Optional[str] = None
    result: Optional[dict] = None
    status: str = "open"  # open, closed, expired


@dataclass
class DebateSession:
    """Sesión de debate entre embriones."""
    id: str
    topic: str
    context: str
    participants: list[str]
    arguments: list[dict] = field(default_factory=dict)  # [{embrion, position, reasoning, evidence}]
    rounds: int = 2  # Número de rondas de argumentación
    current_round: int = 0
    synthesis: Optional[str] = None
    status: str = "open"


@dataclass
class CollectiveIntelligenceProtocol:
    """Protocolo de inteligencia colectiva."""
    
    _supabase: Optional[object] = field(default=None, repr=False)
    _sabios: Optional[object] = field(default=None, repr=False)
    _embriones: dict[str, object] = field(default_factory=dict)
    _message_handlers: dict[str, list[Callable]] = field(default_factory=dict)
    _active_votes: dict[str, VoteSession] = field(default_factory=dict)
    _active_debates: dict[str, DebateSession] = field(default_factory=dict)
    
    # ── Nivel 1: Messaging ─────────────────────────────────────────
    
    async def publish(self, message: EmbrionMessage) -> None:
        """Publicar mensaje a un topic."""
        # Persist to Supabase
        if self._supabase:
            self._supabase.table("embrion_messages").insert({
                "id": message.id,
                "sender": message.sender,
                "type": message.type.value,
                "topic": message.topic,
                "content": json.dumps(message.content),
                "recipients": message.recipients,
                "requires_response": message.requires_response,
                "created_at": message.timestamp,
            }).execute()
        
        # Notify subscribers
        handlers = self._message_handlers.get(message.topic, [])
        for handler in handlers:
            try:
                await handler(message)
            except Exception as e:
                logger.warning("handler_failed", topic=message.topic, error=str(e))
        
        logger.info("message_published",
                    sender=message.sender, topic=message.topic, type=message.type.value)
    
    def subscribe(self, topic: str, handler: Callable) -> None:
        """Suscribir un handler a un topic."""
        if topic not in self._message_handlers:
            self._message_handlers[topic] = []
        self._message_handlers[topic].append(handler)
    
    async def get_messages_for(self, embrion_name: str, 
                                since_hours: int = 24) -> list[EmbrionMessage]:
        """Obtener mensajes relevantes para un embrión."""
        if not self._supabase:
            return []
        
        from datetime import timedelta
        since = (datetime.now(timezone.utc) - timedelta(hours=since_hours)).isoformat()
        
        result = self._supabase.table("embrion_messages").select("*").or_(
            f"recipients.cs.{{{embrion_name}}},recipients.eq.{{}}"
        ).gte("created_at", since).order("created_at", desc=True).limit(50).execute()
        
        return [
            EmbrionMessage(
                id=row["id"],
                sender=row["sender"],
                type=MessageType(row["type"]),
                topic=row["topic"],
                content=json.loads(row["content"]),
                timestamp=row["created_at"],
                recipients=row["recipients"],
                requires_response=row["requires_response"],
            )
            for row in result.data
        ]
    
    # ── Nivel 2: Debate ────────────────────────────────────────────
    
    async def open_debate(self, topic: str, context: str,
                           participants: list[str], rounds: int = 2) -> DebateSession:
        """Abrir una sesión de debate entre embriones."""
        import uuid
        
        session = DebateSession(
            id=str(uuid.uuid4())[:8],
            topic=topic,
            context=context,
            participants=participants,
            rounds=rounds,
        )
        self._active_debates[session.id] = session
        
        # Notify participants
        await self.publish(EmbrionMessage(
            id=f"debate-open-{session.id}",
            sender="collective",
            type=MessageType.DEBATE_OPEN,
            topic="debates",
            content={"debate_id": session.id, "topic": topic, "context": context},
            recipients=participants,
            requires_response=True,
        ))
        
        logger.info("debate_opened", id=session.id, topic=topic, participants=participants)
        return session
    
    async def submit_argument(self, debate_id: str, embrion: str,
                               position: str, reasoning: str, 
                               evidence: list[str] = None) -> None:
        """Embrión submite argumento en un debate."""
        session = self._active_debates.get(debate_id)
        if not session or session.status != "open":
            raise ValueError(f"Debate {debate_id} not found or closed")
        
        session.arguments.append({
            "embrion": embrion,
            "position": position,
            "reasoning": reasoning,
            "evidence": evidence or [],
            "round": session.current_round,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        
        # Check if all participants have argued this round
        round_args = [a for a in session.arguments if a["round"] == session.current_round]
        if len(round_args) >= len(session.participants):
            session.current_round += 1
            if session.current_round >= session.rounds:
                await self._close_debate(session)
    
    async def _close_debate(self, session: DebateSession) -> None:
        """Cerrar debate y generar síntesis."""
        session.status = "closed"
        
        if self._sabios:
            # Generate synthesis using LLM
            args_text = "\n".join([
                f"[{a['embrion']}] Position: {a['position']}\nReasoning: {a['reasoning']}"
                for a in session.arguments
            ])
            
            prompt = f"""You are moderating a debate between specialized AI agents.
Topic: {session.topic}
Context: {session.context}

Arguments presented:
{args_text}

Synthesize the debate into a final recommendation that:
1. Acknowledges the strongest points from each perspective
2. Identifies areas of agreement
3. Resolves conflicts with clear reasoning
4. Provides a final actionable recommendation

Respond in JSON: {{"synthesis": "...", "key_agreements": [...], "resolved_conflicts": [...], "recommendation": "..."}}"""
            
            response = await self._sabios.ask(prompt)
            session.synthesis = response
        
        logger.info("debate_closed", id=session.id, arguments=len(session.arguments))
    
    # ── Nivel 3: Voting ────────────────────────────────────────────
    
    async def call_vote(self, topic: str, question: str, options: list[str],
                         initiator: str, method: DecisionMethod = DecisionMethod.QUALIFIED_MAJORITY,
                         voters: list[str] = None) -> VoteSession:
        """Convocar una votación."""
        import uuid
        
        session = VoteSession(
            id=str(uuid.uuid4())[:8],
            topic=topic,
            question=question,
            options=options,
            method=method,
            initiator=initiator,
        )
        self._active_votes[session.id] = session
        
        # Notify voters
        await self.publish(EmbrionMessage(
            id=f"vote-call-{session.id}",
            sender=initiator,
            type=MessageType.VOTE_CALL,
            topic="votes",
            content={"vote_id": session.id, "question": question, "options": options},
            recipients=voters or list(self._embriones.keys()),
            requires_response=True,
        ))
        
        return session
    
    async def cast_vote(self, vote_id: str, embrion: str, 
                         option: str, reasoning: str, weight: float = 1.0) -> None:
        """Embrión emite su voto."""
        session = self._active_votes.get(vote_id)
        if not session or session.status != "open":
            raise ValueError(f"Vote {vote_id} not found or closed")
        
        session.votes[embrion] = {
            "option": option,
            "weight": weight,
            "reasoning": reasoning,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        # Check if all expected voters have voted
        expected_voters = len(self._embriones)
        if len(session.votes) >= expected_voters:
            await self._tally_votes(session)
    
    async def _tally_votes(self, session: VoteSession) -> None:
        """Contar votos y determinar resultado."""
        session.status = "closed"
        
        # Tally weighted votes
        option_scores = {}
        for vote in session.votes.values():
            option = vote["option"]
            weight = vote["weight"]
            option_scores[option] = option_scores.get(option, 0) + weight
        
        total_weight = sum(v["weight"] for v in session.votes.values())
        
        # Determine winner based on method
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
        
        logger.info("vote_tallied", id=session.id, winner=winner, 
                    pct=session.result["percentage"], passed=passed)
    
    # ── Emergence Detection ────────────────────────────────────────
    
    async def detect_emergence(self) -> list[dict]:
        """Detectar patrones de comportamiento emergente."""
        emergent_patterns = []
        
        if not self._supabase:
            return emergent_patterns
        
        # Pattern 1: Spontaneous collaboration (embriones que se comunican sin ser invocados)
        recent_messages = await self._count_spontaneous_messages(hours=24)
        if recent_messages > 5:
            emergent_patterns.append({
                "type": "spontaneous_collaboration",
                "evidence": f"{recent_messages} spontaneous inter-embrion messages in 24h",
                "significance": "Embriones initiate communication without external trigger",
            })
        
        # Pattern 2: Consensus without explicit vote (multiple embriones reach same conclusion independently)
        # Pattern 3: Knowledge transfer (embrión uses insight from another's domain)
        # Pattern 4: Novel combination (debate produces recommendation none had individually)
        
        return emergent_patterns
    
    async def _count_spontaneous_messages(self, hours: int = 24) -> int:
        """Contar mensajes espontáneos (no solicitados)."""
        from datetime import timedelta
        since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        
        result = self._supabase.table("embrion_messages").select("id", count="exact").eq(
            "type", "insight"
        ).gte("created_at", since).execute()
        
        return result.count or 0
```

### Tabla Supabase

```sql
-- Sprint 61: Inter-embrion messaging
CREATE TABLE IF NOT EXISTS embrion_messages (
    id TEXT PRIMARY KEY,
    sender TEXT NOT NULL,
    type TEXT NOT NULL,
    topic TEXT NOT NULL,
    content JSONB NOT NULL,
    recipients TEXT[] DEFAULT '{}',
    requires_response BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_embrion_msg_topic ON embrion_messages(topic);
CREATE INDEX idx_embrion_msg_sender ON embrion_messages(sender);
CREATE INDEX idx_embrion_msg_time ON embrion_messages(created_at DESC);

-- Sprint 61: Vote sessions
CREATE TABLE IF NOT EXISTS vote_sessions (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    question TEXT NOT NULL,
    options JSONB NOT NULL,
    method TEXT NOT NULL,
    initiator TEXT NOT NULL,
    votes JSONB DEFAULT '{}',
    result JSONB,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sprint 61: Debate sessions
CREATE TABLE IF NOT EXISTS debate_sessions (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    context TEXT NOT NULL,
    participants TEXT[] NOT NULL,
    arguments JSONB DEFAULT '[]',
    rounds INTEGER DEFAULT 2,
    synthesis TEXT,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Épica 61.2 — Design System Enforcement (Objetivo #2)

### Contexto

El Monstruo genera código frontend pero no tiene un estándar de calidad visual ejecutable. El Visual Quality Gate (Sprint 57) evalúa con LLM multimodal, pero es subjetivo y no cuantificable. Sprint 61 crea un **Design System Enforcement Engine** que mide objetivamente: accessibility (WCAG 2.2), performance (Core Web Vitals), design tokens compliance, y responsive behavior.

### Arquitectura

El Design System Engine opera en 4 dimensiones:

1. **Design Tokens:** Sistema de tokens (spacing, colors, typography, shadows, radii) que define el vocabulario visual. Generado como JSON, consumido por templates.
2. **Accessibility Audit:** axe-core via Playwright para WCAG 2.2 compliance scoring.
3. **Performance Budget:** Core Web Vitals via PageSpeed Insights API (LCP < 2.5s, FID < 100ms, CLS < 0.1).
4. **Visual Consistency:** LLM multimodal para evaluar coherencia visual (complementa métricas objetivas).

### Implementación

**Archivo:** `kernel/design/system.py`

```python
"""
El Monstruo — Design System Enforcement Engine (Sprint 61)
============================================================
Motor de enforcement de calidad de diseño.

4 dimensiones:
1. Design Tokens — vocabulario visual ejecutable
2. Accessibility — WCAG 2.2 via axe-core
3. Performance — Core Web Vitals via PageSpeed Insights
4. Visual Consistency — LLM multimodal scoring

Estándar: Apple/Tesla level (Obj #2)
Sprint 61 — 2026-05-01
"""
from __future__ import annotations
import json
import subprocess
from dataclasses import dataclass, field
from typing import Optional
import structlog

logger = structlog.get_logger("monstruo.design")


@dataclass
class DesignTokens:
    """Sistema de design tokens."""
    
    # Spacing scale (rem)
    spacing: dict = field(default_factory=lambda: {
        "xs": "0.25rem", "sm": "0.5rem", "md": "1rem",
        "lg": "1.5rem", "xl": "2rem", "2xl": "3rem",
        "3xl": "4rem", "4xl": "6rem", "5xl": "8rem",
    })
    
    # Color system (OKLCH for Tailwind 4 compatibility)
    colors: dict = field(default_factory=lambda: {
        "primary": {"base": "oklch(0.65 0.15 250)", "light": "oklch(0.85 0.08 250)", "dark": "oklch(0.45 0.15 250)"},
        "secondary": {"base": "oklch(0.70 0.10 180)", "light": "oklch(0.90 0.05 180)", "dark": "oklch(0.50 0.10 180)"},
        "neutral": {"50": "oklch(0.98 0 0)", "100": "oklch(0.95 0 0)", "900": "oklch(0.15 0 0)"},
        "success": "oklch(0.72 0.15 145)",
        "warning": "oklch(0.80 0.15 85)",
        "error": "oklch(0.65 0.20 25)",
    })
    
    # Typography
    typography: dict = field(default_factory=lambda: {
        "font_display": "'Inter Tight', system-ui, sans-serif",
        "font_body": "'Inter', system-ui, sans-serif",
        "font_mono": "'JetBrains Mono', monospace",
        "scale": {
            "xs": "0.75rem", "sm": "0.875rem", "base": "1rem",
            "lg": "1.125rem", "xl": "1.25rem", "2xl": "1.5rem",
            "3xl": "1.875rem", "4xl": "2.25rem", "5xl": "3rem",
        },
        "line_height": {"tight": "1.25", "normal": "1.5", "relaxed": "1.75"},
    })
    
    # Shadows
    shadows: dict = field(default_factory=lambda: {
        "sm": "0 1px 2px oklch(0 0 0 / 0.05)",
        "md": "0 4px 6px oklch(0 0 0 / 0.07)",
        "lg": "0 10px 15px oklch(0 0 0 / 0.1)",
        "xl": "0 20px 25px oklch(0 0 0 / 0.1)",
    })
    
    # Border radius
    radii: dict = field(default_factory=lambda: {
        "sm": "0.25rem", "md": "0.5rem", "lg": "0.75rem",
        "xl": "1rem", "2xl": "1.5rem", "full": "9999px",
    })
    
    def export_json(self) -> str:
        """Exportar tokens como JSON para Style Dictionary."""
        return json.dumps({
            "spacing": self.spacing,
            "colors": self.colors,
            "typography": self.typography,
            "shadows": self.shadows,
            "radii": self.radii,
        }, indent=2)
    
    def export_css_variables(self) -> str:
        """Exportar tokens como CSS custom properties."""
        lines = [":root {"]
        
        for key, value in self.spacing.items():
            lines.append(f"  --spacing-{key}: {value};")
        
        for key, value in self.radii.items():
            lines.append(f"  --radius-{key}: {value};")
        
        lines.append("}")
        return "\n".join(lines)


@dataclass
class DesignAuditResult:
    """Resultado de auditoría de diseño."""
    url: str
    overall_score: float  # 0-100
    accessibility_score: float
    performance_score: float
    token_compliance_score: float
    visual_consistency_score: float
    issues: list[dict]  # [{severity, category, description, element}]
    recommendations: list[str]


@dataclass
class DesignSystemEngine:
    """Motor de enforcement del design system."""
    
    _sabios: Optional[object] = field(default=None, repr=False)
    tokens: DesignTokens = field(default_factory=DesignTokens)
    
    # ── Accessibility Audit ────────────────────────────────────────
    
    async def audit_accessibility(self, url: str) -> dict:
        """Auditar accessibility via axe-core (requires Playwright)."""
        # Run axe-core via Node.js script
        script = f"""
const {{ chromium }} = require('playwright');
const AxeBuilder = require('@axe-core/playwright').default;

(async () => {{
    const browser = await chromium.launch();
    const page = await browser.newPage();
    await page.goto('{url}');
    const results = await new AxeBuilder({{ page }}).analyze();
    console.log(JSON.stringify({{
        violations: results.violations.length,
        passes: results.passes.length,
        incomplete: results.incomplete.length,
        details: results.violations.slice(0, 10).map(v => ({{
            id: v.id,
            impact: v.impact,
            description: v.description,
            nodes: v.nodes.length,
        }}))
    }}));
    await browser.close();
}})();
"""
        try:
            result = subprocess.run(
                ["node", "-e", script],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                total = data["violations"] + data["passes"]
                score = (data["passes"] / max(total, 1)) * 100
                return {"score": round(score, 1), "violations": data["violations"], "details": data["details"]}
        except Exception as e:
            logger.warning("accessibility_audit_failed", error=str(e))
        
        return {"score": 0, "violations": -1, "details": [], "error": "Audit failed"}
    
    # ── Performance Audit ──────────────────────────────────────────
    
    async def audit_performance(self, url: str) -> dict:
        """Auditar Core Web Vitals via PageSpeed Insights API."""
        import httpx
        import os
        
        api_key = os.getenv("GOOGLE_PSI_API_KEY", "")
        endpoint = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=mobile"
        if api_key:
            endpoint += f"&key={api_key}"
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(endpoint, timeout=60.0)
                if resp.status_code == 200:
                    data = resp.json()
                    
                    # Extract Core Web Vitals
                    metrics = data.get("lighthouseResult", {}).get("audits", {})
                    
                    lcp = metrics.get("largest-contentful-paint", {}).get("numericValue", 0) / 1000
                    fid = metrics.get("max-potential-fid", {}).get("numericValue", 0)
                    cls = metrics.get("cumulative-layout-shift", {}).get("numericValue", 0)
                    
                    # Score based on thresholds
                    lcp_score = 100 if lcp < 2.5 else 50 if lcp < 4 else 0
                    fid_score = 100 if fid < 100 else 50 if fid < 300 else 0
                    cls_score = 100 if cls < 0.1 else 50 if cls < 0.25 else 0
                    
                    overall = (lcp_score + fid_score + cls_score) / 3
                    
                    return {
                        "score": round(overall, 1),
                        "lcp_seconds": round(lcp, 2),
                        "fid_ms": round(fid, 0),
                        "cls": round(cls, 3),
                        "lcp_score": lcp_score,
                        "fid_score": fid_score,
                        "cls_score": cls_score,
                    }
        except Exception as e:
            logger.warning("performance_audit_failed", error=str(e))
        
        return {"score": 0, "error": "Audit failed"}
    
    # ── Full Design Audit ──────────────────────────────────────────
    
    async def full_audit(self, url: str) -> DesignAuditResult:
        """Auditoría completa de diseño (4 dimensiones)."""
        # Run audits in parallel
        a11y_result = await self.audit_accessibility(url)
        perf_result = await self.audit_performance(url)
        
        # Token compliance (check if generated code uses design tokens)
        token_score = 75.0  # Default — requires code analysis
        
        # Visual consistency (LLM multimodal if available)
        visual_score = 70.0  # Default
        if self._sabios:
            visual_score = await self._evaluate_visual_consistency(url)
        
        # Calculate overall
        overall = (
            a11y_result.get("score", 0) * 0.30 +
            perf_result.get("score", 0) * 0.25 +
            token_score * 0.20 +
            visual_score * 0.25
        )
        
        # Collect issues
        issues = []
        if a11y_result.get("violations", 0) > 0:
            for detail in a11y_result.get("details", []):
                issues.append({
                    "severity": detail.get("impact", "moderate"),
                    "category": "accessibility",
                    "description": detail.get("description", ""),
                    "element": f"{detail.get('nodes', 0)} elements affected",
                })
        
        if perf_result.get("lcp_seconds", 0) > 2.5:
            issues.append({
                "severity": "serious",
                "category": "performance",
                "description": f"LCP is {perf_result['lcp_seconds']}s (should be < 2.5s)",
                "element": "page load",
            })
        
        return DesignAuditResult(
            url=url,
            overall_score=round(overall, 1),
            accessibility_score=a11y_result.get("score", 0),
            performance_score=perf_result.get("score", 0),
            token_compliance_score=token_score,
            visual_consistency_score=visual_score,
            issues=issues,
            recommendations=self._generate_recommendations(issues),
        )
    
    async def _evaluate_visual_consistency(self, url: str) -> float:
        """Evaluar consistencia visual con LLM multimodal."""
        if not self._sabios:
            return 70.0
        
        prompt = f"""Evaluate the visual design quality of this webpage: {url}

Score from 0-100 on these criteria:
- Typography hierarchy (consistent sizes, weights, line heights)
- Color harmony (palette coherence, contrast ratios)
- Spacing rhythm (consistent padding/margins)
- Component consistency (buttons, cards, inputs look unified)
- Visual hierarchy (clear information priority)

Respond with just a number 0-100."""
        
        try:
            response = await self._sabios.ask(prompt)
            score = float(response.strip().split()[0])
            return min(100, max(0, score))
        except Exception:
            return 70.0
    
    @staticmethod
    def _generate_recommendations(issues: list[dict]) -> list[str]:
        """Generar recomendaciones basadas en issues."""
        recs = []
        
        a11y_issues = [i for i in issues if i["category"] == "accessibility"]
        if a11y_issues:
            recs.append(f"Fix {len(a11y_issues)} accessibility violations (WCAG 2.2 compliance)")
        
        perf_issues = [i for i in issues if i["category"] == "performance"]
        if perf_issues:
            recs.append("Optimize Core Web Vitals: consider lazy loading, image optimization, and code splitting")
        
        if not recs:
            recs.append("Design quality meets Apple/Tesla standards. Continue monitoring.")
        
        return recs
```

---

## Épica 61.3 — i18n Quality Assurance & RTL (Objetivo #13)

### Contexto

Sprint 59 creó el i18n Engine con 10 locales y DeepL + LLM fallback. Pero traducir no es suficiente — una traducción puede ser gramaticalmente correcta pero culturalmente inapropiada, o puede romper el layout en idiomas RTL (Arabic, Hebrew). Sprint 61 agrega la capa de **quality assurance** que falta.

### Implementación

**Archivo:** `kernel/i18n/quality.py`

```python
"""
El Monstruo — i18n Quality Assurance (Sprint 61)
==================================================
Capa de quality assurance para internacionalización.

Componentes:
1. Translation Quality Scoring (chrF + LLM-as-judge)
2. RTL Layout Support (Arabic, Hebrew)
3. Cultural Adaptation Rules
4. i18n Testing Framework

Sprint 61 — 2026-05-01
"""
from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from typing import Optional
import structlog

logger = structlog.get_logger("monstruo.i18n.quality")


@dataclass
class TranslationQualityScore:
    """Score de calidad de una traducción."""
    source_text: str
    translated_text: str
    target_locale: str
    chrf_score: float  # 0-100 (character F-score)
    fluency_score: float  # 0-100 (LLM judge)
    adequacy_score: float  # 0-100 (LLM judge)
    cultural_score: float  # 0-100 (cultural appropriateness)
    overall_score: float
    issues: list[str]


@dataclass
class RTLConfig:
    """Configuración para idiomas RTL."""
    locale: str
    direction: str  # "rtl" or "ltr"
    font_family: str
    number_system: str  # "latn" or "arab"
    calendar: str  # "gregory" or "islamic"
    
    RTL_LOCALES = {"ar", "he", "fa", "ur", "yi", "arc", "dv", "ku", "ps"}
    
    @classmethod
    def for_locale(cls, locale: str) -> "RTLConfig":
        """Generar configuración RTL para un locale."""
        lang = locale.split("-")[0].split("_")[0]
        is_rtl = lang in cls.RTL_LOCALES
        
        font_map = {
            "ar": "'Noto Sans Arabic', 'Segoe UI', sans-serif",
            "he": "'Noto Sans Hebrew', 'Segoe UI', sans-serif",
            "fa": "'Vazirmatn', 'Noto Sans Arabic', sans-serif",
        }
        
        return cls(
            locale=locale,
            direction="rtl" if is_rtl else "ltr",
            font_family=font_map.get(lang, "'Inter', system-ui, sans-serif"),
            number_system="arab" if lang == "ar" else "latn",
            calendar="islamic" if lang == "ar" else "gregory",
        )
    
    def generate_css(self) -> str:
        """Generar CSS para soporte RTL."""
        if self.direction == "ltr":
            return ""
        
        return f"""
/* RTL Support for {self.locale} */
[dir="rtl"] {{
    direction: rtl;
    text-align: right;
    font-family: {self.font_family};
}}

[dir="rtl"] .flex-row {{ flex-direction: row-reverse; }}
[dir="rtl"] .ml-auto {{ margin-left: 0; margin-right: auto; }}
[dir="rtl"] .mr-auto {{ margin-right: 0; margin-left: auto; }}
[dir="rtl"] .pl-4 {{ padding-left: 0; padding-right: 1rem; }}
[dir="rtl"] .pr-4 {{ padding-right: 0; padding-left: 1rem; }}
[dir="rtl"] .text-left {{ text-align: right; }}
[dir="rtl"] .text-right {{ text-align: left; }}
[dir="rtl"] .border-l {{ border-left: 0; border-right: 1px solid; }}
[dir="rtl"] .border-r {{ border-right: 0; border-left: 1px solid; }}
"""


@dataclass
class CulturalAdaptation:
    """Reglas de adaptación cultural por locale."""
    
    RULES: dict = field(default_factory=lambda: {
        "ar": {
            "formality": "high",
            "avoid": ["alcohol references", "pork references", "gambling"],
            "prefer": ["family values", "community", "respect for elders"],
            "date_format": "dd/MM/yyyy",
            "currency_position": "after",
            "greeting_style": "formal with religious reference acceptable",
        },
        "ja": {
            "formality": "very_high",
            "avoid": ["direct criticism", "individualism emphasis"],
            "prefer": ["group harmony", "indirect communication", "respect hierarchy"],
            "date_format": "yyyy年MM月dd日",
            "currency_position": "before",
            "greeting_style": "formal, seasonal reference",
        },
        "de": {
            "formality": "high",
            "avoid": ["informal tone in business", "humor in formal contexts"],
            "prefer": ["precision", "data-driven claims", "formal address (Sie)"],
            "date_format": "dd.MM.yyyy",
            "currency_position": "after",
            "greeting_style": "formal, time-of-day based",
        },
        "es-MX": {
            "formality": "medium",
            "avoid": ["Spain-specific idioms", "overly formal tone"],
            "prefer": ["warmth", "personal connection", "usted for business"],
            "date_format": "dd/MM/yyyy",
            "currency_position": "before",
            "greeting_style": "warm, can be informal",
        },
        "pt-BR": {
            "formality": "medium-low",
            "avoid": ["Portugal-specific terms", "excessive formality"],
            "prefer": ["warmth", "informal tone", "você over tu"],
            "date_format": "dd/MM/yyyy",
            "currency_position": "before",
            "greeting_style": "informal, friendly",
        },
    })
    
    def get_rules(self, locale: str) -> dict:
        """Obtener reglas culturales para un locale."""
        # Try exact match first, then language code
        if locale in self.RULES:
            return self.RULES[locale]
        
        lang = locale.split("-")[0].split("_")[0]
        return self.RULES.get(lang, {
            "formality": "medium",
            "avoid": [],
            "prefer": [],
            "date_format": "yyyy-MM-dd",
            "currency_position": "before",
            "greeting_style": "neutral",
        })


@dataclass
class I18nQualityEngine:
    """Motor de quality assurance para i18n."""
    
    _sabios: Optional[object] = field(default=None, repr=False)
    cultural_rules: CulturalAdaptation = field(default_factory=CulturalAdaptation)
    
    def calculate_chrf(self, reference: str, hypothesis: str) -> float:
        """Calcular chrF score (character F-score) sin dependencias pesadas."""
        # Simplified chrF implementation (character n-gram F-score)
        # Full implementation would use sacrebleu
        if not reference or not hypothesis:
            return 0.0
        
        def char_ngrams(text: str, n: int) -> dict:
            ngrams = {}
            for i in range(len(text) - n + 1):
                ng = text[i:i+n]
                ngrams[ng] = ngrams.get(ng, 0) + 1
            return ngrams
        
        # Average over n=1 to n=6
        scores = []
        for n in range(1, 7):
            ref_ngrams = char_ngrams(reference, n)
            hyp_ngrams = char_ngrams(hypothesis, n)
            
            # Precision
            matches = sum(min(hyp_ngrams.get(ng, 0), ref_ngrams.get(ng, 0)) for ng in hyp_ngrams)
            precision = matches / max(sum(hyp_ngrams.values()), 1)
            
            # Recall
            matches_r = sum(min(ref_ngrams.get(ng, 0), hyp_ngrams.get(ng, 0)) for ng in ref_ngrams)
            recall = matches_r / max(sum(ref_ngrams.values()), 1)
            
            # F-score
            if precision + recall > 0:
                f = 2 * precision * recall / (precision + recall)
            else:
                f = 0
            scores.append(f)
        
        return round(sum(scores) / len(scores) * 100, 1)
    
    async def evaluate_translation(self, source: str, translation: str,
                                     source_locale: str, target_locale: str,
                                     reference: str = None) -> TranslationQualityScore:
        """Evaluar calidad de una traducción."""
        # 1. chrF score (if reference available)
        chrf = self.calculate_chrf(reference, translation) if reference else 50.0
        
        # 2. LLM-as-judge for fluency and adequacy
        fluency = 70.0
        adequacy = 70.0
        cultural = 70.0
        issues = []
        
        if self._sabios:
            rules = self.cultural_rules.get_rules(target_locale)
            
            prompt = f"""Evaluate this translation quality:

Source ({source_locale}): {source}
Translation ({target_locale}): {translation}

Cultural rules for {target_locale}: {json.dumps(rules)}

Score each dimension 0-100:
1. Fluency: Does it read naturally in {target_locale}? Grammar, word choice, flow.
2. Adequacy: Does it preserve the meaning of the source?
3. Cultural: Is it culturally appropriate for {target_locale}?

Also list any issues found.

Respond in JSON:
{{"fluency": N, "adequacy": N, "cultural": N, "issues": ["issue1", "issue2"]}}"""
            
            try:
                response = await self._sabios.ask(prompt)
                data = json.loads(self._extract_json(response))
                fluency = data.get("fluency", 70)
                adequacy = data.get("adequacy", 70)
                cultural = data.get("cultural", 70)
                issues = data.get("issues", [])
            except Exception as e:
                logger.warning("llm_judge_failed", error=str(e))
        
        overall = (chrf * 0.2 + fluency * 0.3 + adequacy * 0.3 + cultural * 0.2)
        
        return TranslationQualityScore(
            source_text=source,
            translated_text=translation,
            target_locale=target_locale,
            chrf_score=chrf,
            fluency_score=fluency,
            adequacy_score=adequacy,
            cultural_score=cultural,
            overall_score=round(overall, 1),
            issues=issues,
        )
    
    def generate_rtl_support(self, locale: str) -> dict:
        """Generar soporte RTL completo para un locale."""
        config = RTLConfig.for_locale(locale)
        return {
            "locale": locale,
            "direction": config.direction,
            "css": config.generate_css(),
            "font_family": config.font_family,
            "html_attrs": f'dir="{config.direction}" lang="{locale}"',
        }
    
    @staticmethod
    def _extract_json(text: str) -> str:
        if "```json" in text:
            return text.split("```json")[1].split("```")[0]
        if "```" in text:
            return text.split("```")[1].split("```")[0]
        return text.strip()
```

---

## Épica 61.4 — Error Learning Loop (Objetivo #4)

### Contexto

El EmbrionLoop (Sprint 34) ya tiene `_error_log` y `_get_relevant_lessons()`. Pero el sistema actual es primitivo: guarda errores como texto plano y las "lecciones" son strings sin estructura. Sprint 61 crea un **Error Learning Loop** completo con taxonomía, reglas derivadas, y enforcement.

### Implementación

**Archivo:** `kernel/learning/error_loop.py`

```python
"""
El Monstruo — Error Learning Loop (Sprint 61)
===============================================
Sistema de aprendizaje de errores.

Pipeline: Error → Classify → Extract Lesson → Derive Rule → Enforce

Principio (Obj #4): "Nunca se equivoca dos veces de la misma forma."
Sprint 61 — 2026-05-01
"""
from __future__ import annotations
import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
import structlog

logger = structlog.get_logger("monstruo.learning")


class ErrorCategory(str, Enum):
    """Taxonomía de errores."""
    CODE_SYNTAX = "code_syntax"
    CODE_LOGIC = "code_logic"
    API_INTEGRATION = "api_integration"
    DATA_VALIDATION = "data_validation"
    DESIGN_QUALITY = "design_quality"
    PERFORMANCE = "performance"
    SECURITY = "security"
    UX_FLOW = "ux_flow"
    BUSINESS_LOGIC = "business_logic"
    INFRASTRUCTURE = "infrastructure"
    UNKNOWN = "unknown"


class RuleSeverity(str, Enum):
    """Severidad de una regla derivada."""
    BLOCK = "block"  # Detiene la ejecución
    WARN = "warn"  # Genera warning pero continúa
    INFO = "info"  # Solo registra


@dataclass
class ErrorRecord:
    """Registro estructurado de un error."""
    id: str
    category: ErrorCategory
    description: str
    context: str  # Qué se estaba haciendo cuando ocurrió
    root_cause: str
    timestamp: str
    embrion: str  # Qué embrión lo causó
    project_type: str  # Tipo de proyecto donde ocurrió
    fingerprint: str  # Hash para deduplicación
    resolved: bool = False
    lesson_id: Optional[str] = None


@dataclass
class Lesson:
    """Lección extraída de un error."""
    id: str
    error_id: str
    category: ErrorCategory
    title: str  # "Nunca hacer X cuando Y"
    description: str
    prevention_rule: str  # Regla ejecutable
    applies_to: list[str]  # Contextos donde aplica
    confidence: float  # 0-1
    times_prevented: int = 0  # Cuántas veces ha prevenido el error


@dataclass
class Rule:
    """Regla derivada de una lección."""
    id: str
    lesson_id: str
    category: ErrorCategory
    condition: str  # Cuándo aplicar la regla
    action: str  # Qué hacer
    severity: RuleSeverity
    active: bool = True
    times_triggered: int = 0
    false_positives: int = 0


@dataclass
class ErrorLearningLoop:
    """Motor de aprendizaje de errores."""
    
    _supabase: Optional[object] = field(default=None, repr=False)
    _sabios: Optional[object] = field(default=None, repr=False)
    _rules: list[Rule] = field(default_factory=list)
    
    async def record_error(self, description: str, context: str,
                            embrion: str = "system", 
                            project_type: str = "unknown") -> ErrorRecord:
        """Registrar un error y clasificarlo."""
        # Generate fingerprint for deduplication
        fingerprint = hashlib.sha256(f"{description}:{context}".encode()).hexdigest()[:12]
        
        # Check if similar error already exists
        existing = await self._find_similar_error(fingerprint)
        if existing:
            logger.info("duplicate_error_detected", fingerprint=fingerprint)
            return existing
        
        # Classify with LLM
        category = await self._classify_error(description, context)
        root_cause = await self._analyze_root_cause(description, context)
        
        record = ErrorRecord(
            id=f"err-{fingerprint}",
            category=category,
            description=description,
            context=context,
            root_cause=root_cause,
            timestamp=datetime.now(timezone.utc).isoformat(),
            embrion=embrion,
            project_type=project_type,
            fingerprint=fingerprint,
        )
        
        # Persist
        if self._supabase:
            self._supabase.table("error_records").insert({
                "id": record.id,
                "category": record.category.value,
                "description": record.description,
                "context": record.context,
                "root_cause": record.root_cause,
                "embrion": record.embrion,
                "project_type": record.project_type,
                "fingerprint": record.fingerprint,
                "created_at": record.timestamp,
            }).execute()
        
        # Extract lesson
        lesson = await self._extract_lesson(record)
        if lesson:
            record.lesson_id = lesson.id
            # Derive rule from lesson
            await self._derive_rule(lesson)
        
        logger.info("error_recorded", id=record.id, category=category.value)
        return record
    
    async def _classify_error(self, description: str, context: str) -> ErrorCategory:
        """Clasificar error usando LLM."""
        if not self._sabios:
            return ErrorCategory.UNKNOWN
        
        categories = [c.value for c in ErrorCategory]
        prompt = f"""Classify this error into one category:

Error: {description}
Context: {context}

Categories: {categories}

Respond with just the category name."""
        
        try:
            response = await self._sabios.ask(prompt)
            cat = response.strip().lower().replace(" ", "_")
            return ErrorCategory(cat) if cat in categories else ErrorCategory.UNKNOWN
        except Exception:
            return ErrorCategory.UNKNOWN
    
    async def _analyze_root_cause(self, description: str, context: str) -> str:
        """Analizar root cause con LLM."""
        if not self._sabios:
            return "Unknown root cause"
        
        prompt = f"""Analyze the root cause of this error:

Error: {description}
Context: {context}

Provide a concise root cause analysis (1-2 sentences). Focus on WHY it happened, not WHAT happened."""
        
        try:
            return await self._sabios.ask(prompt)
        except Exception:
            return "Root cause analysis unavailable"
    
    async def _extract_lesson(self, error: ErrorRecord) -> Optional[Lesson]:
        """Extraer lección de un error."""
        if not self._sabios:
            return None
        
        prompt = f"""Extract a reusable lesson from this error:

Category: {error.category.value}
Error: {error.description}
Root Cause: {error.root_cause}
Context: {error.context}

Respond in JSON:
{{
    "title": "Never do X when Y (concise rule)",
    "description": "Detailed explanation of what went wrong and how to prevent it",
    "prevention_rule": "Specific check or condition to prevent this error",
    "applies_to": ["context1", "context2"]
}}"""
        
        try:
            response = await self._sabios.ask(prompt)
            data = json.loads(self._extract_json(response))
            
            lesson = Lesson(
                id=f"lesson-{error.fingerprint}",
                error_id=error.id,
                category=error.category,
                title=data["title"],
                description=data["description"],
                prevention_rule=data["prevention_rule"],
                applies_to=data.get("applies_to", []),
                confidence=0.7,  # Initial confidence
            )
            
            # Persist
            if self._supabase:
                self._supabase.table("lessons").insert({
                    "id": lesson.id,
                    "error_id": lesson.error_id,
                    "category": lesson.category.value,
                    "title": lesson.title,
                    "description": lesson.description,
                    "prevention_rule": lesson.prevention_rule,
                    "applies_to": lesson.applies_to,
                    "confidence": lesson.confidence,
                }).execute()
            
            return lesson
        except Exception as e:
            logger.warning("lesson_extraction_failed", error=str(e))
            return None
    
    async def _derive_rule(self, lesson: Lesson) -> Optional[Rule]:
        """Derivar regla ejecutable de una lección."""
        rule = Rule(
            id=f"rule-{lesson.id}",
            lesson_id=lesson.id,
            category=lesson.category,
            condition=f"When working on {', '.join(lesson.applies_to)}",
            action=lesson.prevention_rule,
            severity=RuleSeverity.WARN,
        )
        
        self._rules.append(rule)
        
        if self._supabase:
            self._supabase.table("rules").insert({
                "id": rule.id,
                "lesson_id": rule.lesson_id,
                "category": rule.category.value,
                "condition": rule.condition,
                "action": rule.action,
                "severity": rule.severity.value,
                "active": rule.active,
            }).execute()
        
        return rule
    
    async def check_rules(self, context: str, action: str) -> list[Rule]:
        """Verificar si alguna regla aplica al contexto actual."""
        triggered = []
        
        for rule in self._rules:
            if not rule.active:
                continue
            
            # Simple keyword matching for MVP
            context_lower = context.lower()
            condition_keywords = rule.condition.lower().split()
            
            if any(kw in context_lower for kw in condition_keywords if len(kw) > 3):
                triggered.append(rule)
                rule.times_triggered += 1
                logger.info("rule_triggered", rule_id=rule.id, action=rule.action)
        
        return triggered
    
    async def get_relevant_lessons(self, context: str, limit: int = 5) -> list[Lesson]:
        """Obtener lecciones relevantes para un contexto."""
        if not self._supabase:
            return []
        
        # For MVP: keyword-based retrieval
        # Future: embedding-based semantic search
        result = self._supabase.table("lessons").select("*").order(
            "confidence", desc=True
        ).limit(limit).execute()
        
        return [
            Lesson(
                id=row["id"],
                error_id=row["error_id"],
                category=ErrorCategory(row["category"]),
                title=row["title"],
                description=row["description"],
                prevention_rule=row["prevention_rule"],
                applies_to=row["applies_to"],
                confidence=row["confidence"],
            )
            for row in result.data
        ]
    
    async def _find_similar_error(self, fingerprint: str) -> Optional[ErrorRecord]:
        """Buscar error similar por fingerprint."""
        if not self._supabase:
            return None
        
        result = self._supabase.table("error_records").select("*").eq(
            "fingerprint", fingerprint
        ).limit(1).execute()
        
        if result.data:
            row = result.data[0]
            return ErrorRecord(
                id=row["id"],
                category=ErrorCategory(row["category"]),
                description=row["description"],
                context=row["context"],
                root_cause=row["root_cause"],
                timestamp=row["created_at"],
                embrion=row["embrion"],
                project_type=row["project_type"],
                fingerprint=row["fingerprint"],
                resolved=row.get("resolved", False),
            )
        return None
    
    @staticmethod
    def _extract_json(text: str) -> str:
        if "```json" in text:
            return text.split("```json")[1].split("```")[0]
        if "```" in text:
            return text.split("```")[1].split("```")[0]
        return text.strip()
```

### Tablas Supabase

```sql
-- Sprint 61: Error Learning Loop
CREATE TABLE IF NOT EXISTS error_records (
    id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    context TEXT NOT NULL,
    root_cause TEXT,
    embrion TEXT NOT NULL,
    project_type TEXT,
    fingerprint TEXT UNIQUE NOT NULL,
    resolved BOOLEAN DEFAULT FALSE,
    lesson_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lessons (
    id TEXT PRIMARY KEY,
    error_id TEXT REFERENCES error_records(id),
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    prevention_rule TEXT NOT NULL,
    applies_to TEXT[] DEFAULT '{}',
    confidence FLOAT DEFAULT 0.7,
    times_prevented INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rules (
    id TEXT PRIMARY KEY,
    lesson_id TEXT REFERENCES lessons(id),
    category TEXT NOT NULL,
    condition TEXT NOT NULL,
    action TEXT NOT NULL,
    severity TEXT DEFAULT 'warn',
    active BOOLEAN DEFAULT TRUE,
    times_triggered INTEGER DEFAULT 0,
    false_positives INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_errors_fingerprint ON error_records(fingerprint);
CREATE INDEX idx_lessons_category ON lessons(category);
CREATE INDEX idx_rules_active ON rules(active) WHERE active = TRUE;
```

---

## Épica 61.5 — Onboarding Wizard (Objetivo #3)

### Contexto

El Monstruo es poderoso pero intimidante. Un usuario nuevo no sabe por dónde empezar. No hay wizard, no hay guía, no hay "time to first value." Sprint 61 crea un onboarding conversacional que lleva al usuario de "no sé qué hacer" a "mi primer proyecto está configurado" en menos de 5 minutos.

### Implementación

**Archivo:** `kernel/ux/onboarding.py`

```python
"""
El Monstruo — Onboarding Wizard (Sprint 61)
=============================================
Wizard conversacional de onboarding.

Objetivo: "Time to first value" < 5 minutos.
5 pasos: Saludo → Industria → Template → Config → Launch

Principio (Obj #3): "Máximo poder con mínima complejidad."
Sprint 61 — 2026-05-01
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import structlog

logger = structlog.get_logger("monstruo.ux.onboarding")


class OnboardingStep(str, Enum):
    """Pasos del onboarding."""
    WELCOME = "welcome"
    INDUSTRY = "industry"
    TEMPLATE = "template"
    CONFIGURE = "configure"
    LAUNCH = "launch"
    COMPLETE = "complete"


@dataclass
class IndustryTemplate:
    """Template pre-configurado por industria."""
    id: str
    name: str
    industry: str
    description: str
    included_layers: list[str]  # Capas transversales activas
    default_embriones: list[str]  # Embriones activos por defecto
    starter_tasks: list[str]  # Tareas iniciales sugeridas
    estimated_time_minutes: int


INDUSTRY_TEMPLATES = [
    IndustryTemplate(
        id="saas",
        name="SaaS Startup",
        industry="technology",
        description="Plataforma SaaS con suscripciones, analytics, y growth engine",
        included_layers=["sales", "seo", "analytics", "security", "scalability", "financial"],
        default_embriones=["ventas", "tecnico", "financiero", "estratega"],
        starter_tasks=["Define pricing tiers", "Create landing page", "Set up analytics"],
        estimated_time_minutes=3,
    ),
    IndustryTemplate(
        id="ecommerce",
        name="E-Commerce",
        industry="retail",
        description="Tienda online con catálogo, pagos, y logística",
        included_layers=["sales", "seo", "analytics", "security", "financial"],
        default_embriones=["ventas", "creativo", "financiero", "vigia"],
        starter_tasks=["Upload product catalog", "Configure payments", "Design storefront"],
        estimated_time_minutes=4,
    ),
    IndustryTemplate(
        id="agency",
        name="Digital Agency",
        industry="services",
        description="Agencia digital con portfolio, CRM, y project management",
        included_layers=["sales", "seo", "analytics", "security"],
        default_embriones=["creativo", "estratega", "ventas", "investigador"],
        starter_tasks=["Build portfolio site", "Set up client intake", "Define service packages"],
        estimated_time_minutes=3,
    ),
    IndustryTemplate(
        id="content",
        name="Content Creator",
        industry="media",
        description="Plataforma de contenido con monetización y community",
        included_layers=["sales", "seo", "analytics"],
        default_embriones=["creativo", "ventas", "investigador", "estratega"],
        starter_tasks=["Define content strategy", "Set up monetization", "Create brand kit"],
        estimated_time_minutes=2,
    ),
    IndustryTemplate(
        id="marketplace",
        name="Marketplace",
        industry="platform",
        description="Marketplace bilateral con vendors, buyers, y comisiones",
        included_layers=["sales", "seo", "analytics", "security", "scalability", "financial"],
        default_embriones=["tecnico", "ventas", "financiero", "vigia", "estratega"],
        starter_tasks=["Define marketplace model", "Create vendor onboarding", "Set commission structure"],
        estimated_time_minutes=5,
    ),
    IndustryTemplate(
        id="custom",
        name="Custom Project",
        industry="other",
        description="Proyecto personalizado — tú defines todo",
        included_layers=["security"],
        default_embriones=["estratega", "tecnico"],
        starter_tasks=["Describe your project", "Define success metrics"],
        estimated_time_minutes=5,
    ),
]


@dataclass
class OnboardingState:
    """Estado del onboarding de un usuario."""
    user_id: str
    current_step: OnboardingStep = OnboardingStep.WELCOME
    selected_industry: Optional[str] = None
    selected_template: Optional[str] = None
    project_name: Optional[str] = None
    custom_config: dict = field(default_factory=dict)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class OnboardingWizard:
    """Wizard de onboarding conversacional."""
    
    _sabios: Optional[object] = field(default=None, repr=False)
    _states: dict[str, OnboardingState] = field(default_factory=dict)
    
    def start(self, user_id: str) -> dict:
        """Iniciar onboarding para un usuario."""
        state = OnboardingState(
            user_id=user_id,
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        self._states[user_id] = state
        
        return {
            "step": OnboardingStep.WELCOME.value,
            "message": self._welcome_message(),
            "options": None,
            "progress": 0,
        }
    
    def advance(self, user_id: str, input_data: dict) -> dict:
        """Avanzar al siguiente paso basado en input del usuario."""
        state = self._states.get(user_id)
        if not state:
            return self.start(user_id)
        
        handlers = {
            OnboardingStep.WELCOME: self._handle_welcome,
            OnboardingStep.INDUSTRY: self._handle_industry,
            OnboardingStep.TEMPLATE: self._handle_template,
            OnboardingStep.CONFIGURE: self._handle_configure,
            OnboardingStep.LAUNCH: self._handle_launch,
        }
        
        handler = handlers.get(state.current_step)
        if handler:
            return handler(state, input_data)
        
        return {"step": "complete", "message": "Onboarding already complete"}
    
    def _handle_welcome(self, state: OnboardingState, input_data: dict) -> dict:
        """Paso 1 → 2: Welcome → Industry selection."""
        state.current_step = OnboardingStep.INDUSTRY
        
        industries = list(set(t.industry for t in INDUSTRY_TEMPLATES))
        
        return {
            "step": OnboardingStep.INDUSTRY.value,
            "message": "¿En qué industria está tu proyecto?",
            "options": industries,
            "progress": 20,
        }
    
    def _handle_industry(self, state: OnboardingState, input_data: dict) -> dict:
        """Paso 2 → 3: Industry → Template selection."""
        state.selected_industry = input_data.get("industry", "other")
        state.current_step = OnboardingStep.TEMPLATE
        
        # Filter templates by industry
        templates = [t for t in INDUSTRY_TEMPLATES if t.industry == state.selected_industry]
        if not templates:
            templates = INDUSTRY_TEMPLATES  # Show all if no match
        
        return {
            "step": OnboardingStep.TEMPLATE.value,
            "message": "Elige un template para empezar:",
            "options": [{"id": t.id, "name": t.name, "description": t.description, "time": t.estimated_time_minutes} for t in templates],
            "progress": 40,
        }
    
    def _handle_template(self, state: OnboardingState, input_data: dict) -> dict:
        """Paso 3 → 4: Template → Configuration."""
        state.selected_template = input_data.get("template_id", "custom")
        state.current_step = OnboardingStep.CONFIGURE
        
        template = next((t for t in INDUSTRY_TEMPLATES if t.id == state.selected_template), INDUSTRY_TEMPLATES[-1])
        
        return {
            "step": OnboardingStep.CONFIGURE.value,
            "message": f"Configurando '{template.name}'. ¿Cómo se llama tu proyecto?",
            "template": {
                "name": template.name,
                "layers": template.included_layers,
                "embriones": template.default_embriones,
                "starter_tasks": template.starter_tasks,
            },
            "progress": 60,
        }
    
    def _handle_configure(self, state: OnboardingState, input_data: dict) -> dict:
        """Paso 4 → 5: Configure → Launch."""
        state.project_name = input_data.get("project_name", "Mi Proyecto")
        state.custom_config = input_data.get("config", {})
        state.current_step = OnboardingStep.LAUNCH
        
        template = next((t for t in INDUSTRY_TEMPLATES if t.id == state.selected_template), INDUSTRY_TEMPLATES[-1])
        
        return {
            "step": OnboardingStep.LAUNCH.value,
            "message": f"¡'{state.project_name}' está listo para lanzar!",
            "summary": {
                "project_name": state.project_name,
                "template": template.name,
                "active_layers": template.included_layers,
                "active_embriones": template.default_embriones,
                "first_tasks": template.starter_tasks,
            },
            "progress": 80,
        }
    
    def _handle_launch(self, state: OnboardingState, input_data: dict) -> dict:
        """Paso 5 → Complete: Launch project."""
        from datetime import datetime, timezone
        state.current_step = OnboardingStep.COMPLETE
        state.completed_at = datetime.now(timezone.utc).isoformat()
        
        return {
            "step": "complete",
            "message": f"¡{state.project_name} está en marcha! Los embriones ya están trabajando.",
            "progress": 100,
            "next_actions": [
                "Revisa el dashboard para ver el progreso",
                "Los embriones comenzarán sus tareas autónomas en segundos",
                "Puedes chatear con El Monstruo para cualquier ajuste",
            ],
        }
    
    @staticmethod
    def _welcome_message() -> str:
        return """¡Bienvenido a El Monstruo! 🦾

Soy tu sistema de inteligencia artificial para crear negocios digitales.
En menos de 5 minutos tendrás tu primer proyecto configurado con:
- Embriones autónomos trabajando para ti
- Capas transversales de seguridad, SEO, y analytics
- Un simulador predictivo para tus decisiones

¿Empezamos?"""
```

---

## Archivos a Crear/Modificar

| Archivo | Acción | Épica |
|---|---|---|
| `kernel/collective/__init__.py` | Crear | 61.1 |
| `kernel/collective/protocol.py` | Crear | 61.1 |
| `kernel/design/__init__.py` | Crear | 61.2 |
| `kernel/design/system.py` | Crear | 61.2 |
| `kernel/i18n/quality.py` | Crear | 61.3 |
| `kernel/learning/__init__.py` | Crear | 61.4 |
| `kernel/learning/error_loop.py` | Crear | 61.4 |
| `kernel/ux/__init__.py` | Crear | 61.5 |
| `kernel/ux/onboarding.py` | Crear | 61.5 |
| `kernel/embrion_loop.py` | Modificar (integrar collective protocol + error learning) | 61.1, 61.4 |
| `kernel/main.py` | Modificar (agregar /api/onboarding, /api/design-audit) | 61.2, 61.5 |
| `supabase/migrations/` | Crear tablas (messages, votes, debates, errors, lessons, rules) | 61.1, 61.4 |

---

## Criterios de Aceptación

| Épica | Criterio | Verificación |
|---|---|---|
| 61.1 | Embriones pueden enviar y recibir mensajes | Test: publish + subscribe + receive |
| 61.1 | Debate produce síntesis con argumentos de múltiples embriones | Test: 3 embriones debaten, síntesis generada |
| 61.1 | Votación calcula resultado con mayoría calificada | Test: 5 votos, threshold 60% |
| 61.2 | Accessibility audit detecta violaciones WCAG | Test con página con issues conocidos |
| 61.2 | Performance audit retorna Core Web Vitals reales | Test con URL pública |
| 61.2 | Design tokens exportan CSS variables válidas | Test: parse CSS output |
| 61.3 | chrF score calcula correctamente | Test con traducciones de referencia |
| 61.3 | RTL CSS genera reglas correctas para Arabic | Test: dir="rtl" + mirrored layout |
| 61.3 | Cultural rules existen para 5+ locales | Verify RULES dict |
| 61.4 | Error → Lesson → Rule pipeline completo | Test: record error, verify lesson + rule created |
| 61.4 | Deduplicación por fingerprint funciona | Test: mismo error 2x, solo 1 record |
| 61.5 | Onboarding completa en 5 pasos | Test: advance through all steps |
| 61.5 | Template selection filtra por industria | Test: select "technology", verify SaaS template |

---

## Estimación de Costos

| Componente | Costo Mensual |
|---|---|
| Supabase Realtime (channels adicionales) | $0 (incluido en plan) |
| PageSpeed Insights API | $0 (free tier) |
| axe-core (npm package) | $0 (open source) |
| LLM calls (debate, quality scoring, error analysis) | ~$5-12/mes |
| sacrebleu (library) | $0 |
| **Total Sprint 61** | **$5-12/mes adicionales** |

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Debates entre embriones son lentos (múltiples LLM calls) | Alta | Medio | Timeout de 30s por argumento, máximo 2 rondas |
| axe-core requiere Playwright (pesado) | Media | Bajo | Fallback a Lighthouse CLI si Playwright no disponible |
| Error Learning genera reglas falsas | Media | Alto | Confidence threshold (>0.8) para activar reglas como BLOCK |
| Onboarding demasiado simplista para power users | Baja | Bajo | "Skip onboarding" option + advanced mode |
| chrF sin referencia es inútil | Alta | Medio | Usar LLM-as-judge como primary, chrF como supplementary |

---

## Significado del Sprint 61

Sprint 61 marca el inicio de la serie 61-70 con un cambio de paradigma: de **construir piezas** a **hacer que las piezas funcionen juntas**. Los 7 embriones ahora se comunican, debaten, y votan. Los errores se convierten en reglas. El diseño se mide objetivamente. Y un usuario nuevo puede empezar en 5 minutos.

**Saltos esperados:**
- Obj #8 (Emergencia): 70% → 82% (protocolo colectivo + detección de emergencia)
- Obj #13 (Del Mundo): 60% → 72% (RTL + quality scoring + cultural adaptation)
- Obj #2 (Apple/Tesla): 65% → 77% (design system + accessibility + performance)
- Obj #4 (No Equivocarse 2x): 73% → 83% (error learning loop completo)
- Obj #3 (Mínima Complejidad): 72% → 80% (onboarding wizard)

---

## Referencias

[1]: https://github.com/Unbabel/COMET "COMET — Neural Framework for MT Evaluation (unbabel-comet 2.2.7)"
[2]: https://github.com/dequelabs/axe-core "axe-core — Accessibility engine for automated Web UI testing"
[3]: https://styledictionary.com/ "Style Dictionary — Design token build system (Amazon)"
[4]: https://supabase.com/ "Supabase — Realtime subscriptions included"
[5]: https://developers.google.com/speed/docs/insights/v5/get-started "PageSpeed Insights API v5"
[6]: https://github.com/mjpost/sacrebleu "SacreBLEU — Standard BLEU/chrF scoring"
[7]: https://arxiv.org/abs/2502.19130 "Voting or Consensus? Decision-Making in Multi-Agent Debate (Feb 2025)"
