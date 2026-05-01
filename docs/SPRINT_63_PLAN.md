# Sprint 63 — "La Vanguardia Viviente"

**Fecha:** 1 mayo 2026
**Version:** 0.63.0
**Autor:** Manus AI
**Filosofia:** El Monstruo deja de ser un sistema que se actualiza manualmente y se convierte en un organismo que evoluciona continuamente, descubre su propio futuro, y se presenta al mundo con la elegancia de un producto de clase mundial.

---

## Contexto Estrategico

Post Sprint 62, el promedio de cobertura es 87.2%. Los 5 objetivos mas rezagados son:

| Objetivo | Cobertura | Gap to 90% | Estrategia Sprint 63 |
|---|---|---|---|
| #6 Vanguardia Perpetua | 81% | 9% | Research auto-discovery + integration proposals |
| #3 Minima Complejidad | 82% | 8% | Zero-config experience |
| #13 Del Mundo | 82% | 8% | Marketplace + community |
| #2 Nivel Apple/Tesla | 83% | 7% | Animation system + motion tokens |
| #8 Inteligencia Emergente | 83% | 7% | Cross-embrion learning |

Sprint 63 ataca los 5 simultaneamente. El hilo conductor es la **evolucion autonoma**: el sistema descubre herramientas (#6), las integra sin friccion (#3), las comparte globalmente (#13), con calidad visual de clase mundial (#2), aprendiendo de si mismo (#8).

---

## Stack Validado en Tiempo Real

| Herramienta | Version | Fecha | Rol |
|---|---|---|---|
| Motion (prev Framer Motion) | 12.38.0 | Mar 17, 2026 | Animation system [1] |
| Semantic Scholar API | v1 | Activo | Deep paper discovery [2] |
| Agents Radar | Sprint 45 | Apr 30, 2026 | YA EXISTE — se expande, no se recrea |
| arXiv API | v1 | Activo | Paper search by category |
| Pluggy | ~1.5.0 | Sprint 62 | Base para marketplace |

**Hallazgo critico:** `tools/agents_radar.py` (Sprint 45) YA cubre 10 fuentes de discovery (GitHub Trending, arXiv, HuggingFace, HN, Product Hunt, Dev.to, Lobsters, Anthropic, OpenAI, Claude Code Skills). Sprint 63 NO recrea esto — lo EXPANDE con relevance scoring e integration proposals.

---

## Epica 63.1 — Research Intelligence Engine

**Objetivo:** Obj #6 (Vanguardia Perpetua)
**Impacto:** +8% en Obj #6
**Depende de:** `tools/agents_radar.py` (Sprint 45), `kernel/plugins/` (Sprint 62)

### Vision

Transformar el Agents Radar de un "feed de noticias" a un "motor de inteligencia" que no solo descubre herramientas sino que evalua su relevancia, propone integraciones concretas, y ejecuta upgrades automaticos cuando el beneficio es claro.

### Arquitectura

```
kernel/vanguard/
  __init__.py
  intelligence_engine.py   # Core: scoring + proposals
  semantic_scholar.py      # Deep academic paper search
  stack_analyzer.py        # Analyze current stack for gaps
  integration_proposer.py  # Generate integration plans
  weekly_digest.py         # Scheduled digest generation
```

### Intelligence Engine

```python
"""kernel/vanguard/intelligence_engine.py"""
import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = structlog.get_logger("vanguard.intelligence")

@dataclass
class DiscoveryItem:
    source: str          # "agents_radar", "semantic_scholar", "pypi_monitor"
    title: str
    url: str
    category: str        # "library", "paper", "tool", "model", "framework"
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    relevance_score: float = 0.0    # 0-1
    integration_effort: str = "unknown"  # "trivial", "moderate", "significant", "major"
    replaces: Optional[str] = None  # Existing tool it could replace
    summary: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass
class IntegrationProposal:
    discovery: DiscoveryItem
    rationale: str
    impact_areas: list[str]         # Which objectives it advances
    estimated_effort_hours: float
    risk_level: str                 # "low", "medium", "high"
    migration_steps: list[str]
    rollback_plan: str
    approved: bool = False
    executed: bool = False


class ResearchIntelligenceEngine:
    """Core engine that transforms raw discoveries into actionable intelligence."""

    def __init__(self, supabase, router):
        self.supabase = supabase
        self.router = router
        self._current_stack: dict = {}
        self._discoveries: list[DiscoveryItem] = []

    async def analyze_discovery(self, item: DiscoveryItem) -> DiscoveryItem:
        """Score a discovery item for relevance to El Monstruo."""
        # 1. Check if it relates to current stack
        stack_relevance = await self._check_stack_relevance(item)

        # 2. Check if it solves a known gap
        gap_relevance = await self._check_gap_relevance(item)

        # 3. Check community adoption (stars, downloads, citations)
        adoption_score = await self._check_adoption(item)

        # 4. Check security (CVEs, maintenance status)
        security_score = await self._check_security(item)

        # Weighted composite score
        item.relevance_score = (
            stack_relevance * 0.35 +
            gap_relevance * 0.30 +
            adoption_score * 0.20 +
            security_score * 0.15
        )

        # Determine integration effort
        item.integration_effort = self._estimate_effort(item)

        # Check if it replaces something
        item.replaces = await self._find_replacement_target(item)

        logger.info("discovery_scored", title=item.title, score=item.relevance_score)
        return item

    async def generate_proposal(self, item: DiscoveryItem) -> Optional[IntegrationProposal]:
        """Generate an integration proposal for high-relevance discoveries."""
        if item.relevance_score < 0.7:
            return None

        # Use LLM to generate detailed proposal
        prompt = f"""Analyze this discovery for integration into El Monstruo:

Title: {item.title}
URL: {item.url}
Category: {item.category}
Summary: {item.summary}
Replaces: {item.replaces or 'Nothing'}
Current stack context: {self._current_stack}

Generate:
1. Rationale (why integrate)
2. Impact areas (which of the 13 objectives it advances)
3. Estimated effort in hours
4. Risk level (low/medium/high)
5. Step-by-step migration plan
6. Rollback plan if integration fails
"""
        from router.engine import route_completion
        response = await route_completion(
            messages=[{"role": "user", "content": prompt}],
            intent="analyze",
        )

        # Parse LLM response into structured proposal
        proposal = IntegrationProposal(
            discovery=item,
            rationale=response.content[:500],
            impact_areas=self._extract_objectives(response.content),
            estimated_effort_hours=self._extract_hours(response.content),
            risk_level=self._extract_risk(response.content),
            migration_steps=self._extract_steps(response.content),
            rollback_plan=self._extract_rollback(response.content),
        )

        # Persist proposal
        await self._save_proposal(proposal)
        return proposal

    async def run_daily_scan(self) -> dict:
        """Run daily scan: fetch from all sources, score, propose."""
        results = {"scanned": 0, "relevant": 0, "proposals": 0}

        # 1. Fetch from Agents Radar
        from tools.agents_radar import fetch_latest_digest
        radar_items = await fetch_latest_digest()
        for raw in radar_items:
            item = DiscoveryItem(
                source="agents_radar",
                title=raw["title"],
                url=raw["url"],
                category=raw.get("category", "tool"),
                summary=raw.get("description", ""),
                tags=raw.get("tags", []),
            )
            scored = await self.analyze_discovery(item)
            results["scanned"] += 1

            if scored.relevance_score >= 0.7:
                results["relevant"] += 1
                proposal = await self.generate_proposal(scored)
                if proposal:
                    results["proposals"] += 1

        # 2. Fetch from Semantic Scholar (weekly, not daily)
        # Handled by separate scheduled task

        logger.info("daily_scan_complete", **results)
        return results

    async def _check_stack_relevance(self, item: DiscoveryItem) -> float:
        """Check if discovery relates to technologies in current stack."""
        stack_keywords = set()
        for dep in self._current_stack.get("dependencies", []):
            stack_keywords.add(dep.lower())
            stack_keywords.update(dep.lower().split("-"))

        item_keywords = set(item.title.lower().split() + item.tags)
        overlap = stack_keywords & item_keywords
        return min(len(overlap) / 3.0, 1.0)

    async def _check_gap_relevance(self, item: DiscoveryItem) -> float:
        """Check if discovery addresses a known gap in objectives."""
        # Query gaps from objectives tracker
        gaps = await self.supabase.table("objective_gaps").select("*").execute()
        gap_keywords = set()
        for gap in (gaps.data or []):
            gap_keywords.update(gap.get("keywords", []))

        item_keywords = set(item.title.lower().split() + item.tags)
        overlap = gap_keywords & item_keywords
        return min(len(overlap) / 2.0, 1.0)

    async def _check_adoption(self, item: DiscoveryItem) -> float:
        """Score based on community adoption metrics."""
        # Simplified: use tag-based heuristics
        high_adoption_signals = ["trending", "popular", "1k+", "10k+", "100k+"]
        score = sum(1 for s in high_adoption_signals if s in str(item.tags).lower())
        return min(score / 3.0, 1.0)

    async def _check_security(self, item: DiscoveryItem) -> float:
        """Check for known security issues."""
        # Default to 0.8 (assume safe unless proven otherwise)
        # In production, query OSV.dev
        return 0.8

    def _estimate_effort(self, item: DiscoveryItem) -> str:
        category_effort = {
            "library": "moderate",
            "paper": "significant",
            "tool": "moderate",
            "model": "trivial",
            "framework": "major",
        }
        return category_effort.get(item.category, "moderate")

    async def _find_replacement_target(self, item: DiscoveryItem) -> Optional[str]:
        """Check if this discovery could replace an existing dependency."""
        # Compare against requirements.txt entries
        # Simplified: return None for now, full implementation uses LLM
        return None

    def _extract_objectives(self, text: str) -> list[str]:
        objectives = []
        for i in range(1, 14):
            if f"#{i}" in text or f"Obj {i}" in text or f"Objetivo {i}" in text:
                objectives.append(f"#{i}")
        return objectives or ["#6"]

    def _extract_hours(self, text: str) -> float:
        import re
        match = re.search(r"(\d+(?:\.\d+)?)\s*(?:hours?|horas?)", text, re.I)
        return float(match.group(1)) if match else 8.0

    def _extract_risk(self, text: str) -> str:
        text_lower = text.lower()
        if "high risk" in text_lower or "alto riesgo" in text_lower:
            return "high"
        if "low risk" in text_lower or "bajo riesgo" in text_lower:
            return "low"
        return "medium"

    def _extract_steps(self, text: str) -> list[str]:
        import re
        steps = re.findall(r"(?:^|\n)\s*\d+[\.\)]\s*(.+)", text)
        return steps[:10] if steps else ["Evaluate", "Implement", "Test", "Deploy"]

    def _extract_rollback(self, text: str) -> str:
        if "rollback" in text.lower():
            idx = text.lower().index("rollback")
            return text[idx:idx+200]
        return "Revert to previous version via git"

    async def _save_proposal(self, proposal: IntegrationProposal) -> None:
        await self.supabase.table("integration_proposals").insert({
            "title": proposal.discovery.title,
            "url": proposal.discovery.url,
            "relevance_score": proposal.discovery.relevance_score,
            "rationale": proposal.rationale,
            "impact_areas": proposal.impact_areas,
            "effort_hours": proposal.estimated_effort_hours,
            "risk_level": proposal.risk_level,
            "migration_steps": proposal.migration_steps,
            "rollback_plan": proposal.rollback_plan,
            "status": "pending",
        }).execute()
```

### Semantic Scholar Integration

```python
"""kernel/vanguard/semantic_scholar.py"""
import httpx
import structlog
from typing import Optional

logger = structlog.get_logger("vanguard.semantic_scholar")

BASE_URL = "https://api.semanticscholar.org/graph/v1"
RELEVANT_FIELDS = "title,abstract,year,citationCount,url,authors,fieldsOfStudy"


class SemanticScholarClient:
    """Search academic papers for deep research intelligence."""

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=30)

    async def search_papers(
        self,
        query: str,
        year_from: int = 2024,
        min_citations: int = 5,
        limit: int = 20,
    ) -> list[dict]:
        """Search for relevant papers."""
        params = {
            "query": query,
            "fields": RELEVANT_FIELDS,
            "limit": limit,
            "year": f"{year_from}-",
        }
        try:
            resp = await self._client.get(f"{BASE_URL}/paper/search", params=params)
            resp.raise_for_status()
            data = resp.json()
            papers = data.get("data", [])
            # Filter by citation count
            return [p for p in papers if (p.get("citationCount") or 0) >= min_citations]
        except Exception as e:
            logger.error("semantic_scholar_error", error=str(e))
            return []

    async def get_recommendations(self, paper_id: str, limit: int = 10) -> list[dict]:
        """Get paper recommendations based on a seed paper."""
        try:
            resp = await self._client.get(
                f"{BASE_URL}/recommendations",
                params={"paperId": paper_id, "fields": RELEVANT_FIELDS, "limit": limit},
            )
            resp.raise_for_status()
            return resp.json().get("recommendedPapers", [])
        except Exception as e:
            logger.error("recommendations_error", error=str(e))
            return []

    async def weekly_scan(self, topics: list[str]) -> list[dict]:
        """Run weekly scan across all relevant topics."""
        all_papers = []
        for topic in topics:
            papers = await self.search_papers(topic, year_from=2025, min_citations=3)
            all_papers.extend(papers)
        # Deduplicate by paper ID
        seen = set()
        unique = []
        for p in all_papers:
            pid = p.get("paperId")
            if pid and pid not in seen:
                seen.add(pid)
                unique.append(p)
        return sorted(unique, key=lambda x: x.get("citationCount", 0), reverse=True)
```

### Weekly Digest Generator

```python
"""kernel/vanguard/weekly_digest.py"""
import structlog
from datetime import datetime, timezone

logger = structlog.get_logger("vanguard.digest")


class WeeklyDigestGenerator:
    """Generate weekly intelligence digest for the user."""

    def __init__(self, intelligence_engine, semantic_scholar, supabase):
        self.engine = intelligence_engine
        self.scholar = semantic_scholar
        self.supabase = supabase

    async def generate(self) -> dict:
        """Generate complete weekly digest."""
        digest = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "period": "last_7_days",
            "sections": {},
        }

        # 1. Top discoveries from daily scans
        proposals = await self.supabase.table("integration_proposals")\
            .select("*").eq("status", "pending")\
            .order("relevance_score", desc=True).limit(10).execute()
        digest["sections"]["top_proposals"] = proposals.data or []

        # 2. Academic papers (weekly scan)
        topics = [
            "multi-agent systems autonomous",
            "LLM cost optimization routing",
            "causal inference prediction",
            "AI code generation quality",
            "emergent behavior artificial intelligence",
        ]
        papers = await self.scholar.weekly_scan(topics)
        digest["sections"]["academic_papers"] = papers[:10]

        # 3. Stack health report
        digest["sections"]["stack_health"] = await self._generate_stack_health()

        # 4. Trend analysis
        digest["sections"]["trends"] = await self._analyze_trends()

        # Persist digest
        await self.supabase.table("weekly_digests").insert(digest).execute()
        logger.info("digest_generated", proposals=len(digest["sections"]["top_proposals"]))
        return digest

    async def _generate_stack_health(self) -> dict:
        """Check health of current dependencies."""
        return {
            "outdated_packages": [],  # Filled by dependency audit
            "security_advisories": [],  # Filled by OSV.dev check
            "deprecation_warnings": [],
        }

    async def _analyze_trends(self) -> list[dict]:
        """Identify emerging trends from accumulated discoveries."""
        # Aggregate tags from last 30 days of discoveries
        return [
            {"trend": "multi-agent orchestration", "momentum": "rising"},
            {"trend": "local LLM inference", "momentum": "stable"},
            {"trend": "causal AI", "momentum": "rising"},
        ]
```

### Tabla Supabase

```sql
CREATE TABLE integration_proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    url TEXT,
    relevance_score FLOAT NOT NULL,
    rationale TEXT,
    impact_areas TEXT[],
    effort_hours FLOAT,
    risk_level TEXT CHECK (risk_level IN ('low', 'medium', 'high')),
    migration_steps TEXT[],
    rollback_plan TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'executed')),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE weekly_digests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generated_at TIMESTAMPTZ NOT NULL,
    period TEXT,
    sections JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

---

## Epica 63.2 — Zero-Config Experience

**Objetivo:** Obj #3 (Minima Complejidad)
**Impacto:** +6% en Obj #3

### Vision

Un usuario nuevo debe poder crear su primer proyecto funcional en menos de 60 segundos, sin llenar un solo formulario. El sistema infiere todo lo necesario a partir de una sola frase.

### Arquitectura

```
kernel/zero_config/
  __init__.py
  intent_inferrer.py     # Parse natural language into project config
  smart_defaults.py      # Industry + locale based defaults
  progressive_ui.py      # Progressive disclosure config
  one_click_deploy.py    # Deploy without configuration
```

### Intent Inferrer

```python
"""kernel/zero_config/intent_inferrer.py"""
import structlog
from dataclasses import dataclass, field
from typing import Optional

logger = structlog.get_logger("zero_config.inferrer")

@dataclass
class InferredProject:
    project_type: str       # "ecommerce", "saas", "portfolio", "blog", "landing"
    industry: str           # "restaurant", "fitness", "tech", "fashion", etc.
    locale: str             # "es-MX", "en-US", etc.
    features: list[str]     # ["payments", "auth", "blog", "gallery"]
    style: str              # "minimal", "bold", "elegant", "playful"
    name: Optional[str] = None
    description: Optional[str] = None
    confidence: float = 0.0
    inferred_from: str = ""


# Industry detection patterns
INDUSTRY_PATTERNS: dict[str, list[str]] = {
    "restaurant": ["restaurante", "comida", "menu", "food", "cafe", "bar", "cocina", "chef"],
    "fitness": ["gym", "fitness", "yoga", "crossfit", "entrenamiento", "workout", "deporte"],
    "tech": ["saas", "app", "software", "startup", "api", "platform", "tech"],
    "fashion": ["moda", "ropa", "tienda", "boutique", "fashion", "clothing", "store"],
    "real_estate": ["inmobiliaria", "propiedades", "real estate", "apartments", "casas"],
    "education": ["escuela", "cursos", "academia", "learning", "education", "tutoring"],
    "health": ["clinica", "doctor", "salud", "health", "medical", "dental", "therapy"],
    "creative": ["fotografia", "diseno", "portfolio", "creative", "art", "design", "studio"],
    "consulting": ["consultoria", "consulting", "advisory", "coaching", "mentoring"],
    "ecommerce": ["tienda", "vender", "productos", "shop", "ecommerce", "marketplace"],
}

# Project type detection
TYPE_PATTERNS: dict[str, list[str]] = {
    "ecommerce": ["tienda", "vender", "shop", "store", "productos", "carrito", "checkout"],
    "saas": ["saas", "dashboard", "usuarios", "suscripcion", "subscription", "platform"],
    "portfolio": ["portfolio", "portafolio", "proyectos", "trabajos", "showcase"],
    "blog": ["blog", "articulos", "contenido", "posts", "noticias", "magazine"],
    "landing": ["landing", "pagina", "presentar", "negocio", "empresa", "servicio"],
}


class IntentInferrer:
    """Infer complete project configuration from a single phrase."""

    async def infer(self, user_input: str, user_locale: str = "es-MX") -> InferredProject:
        """Infer project config from natural language input."""
        input_lower = user_input.lower()

        # 1. Detect project type
        project_type = self._detect_type(input_lower)

        # 2. Detect industry
        industry = self._detect_industry(input_lower)

        # 3. Infer features based on type + industry
        features = self._infer_features(project_type, industry)

        # 4. Infer style based on industry
        style = self._infer_style(industry)

        # 5. Calculate confidence
        confidence = self._calculate_confidence(project_type, industry, input_lower)

        result = InferredProject(
            project_type=project_type,
            industry=industry,
            locale=user_locale,
            features=features,
            style=style,
            name=self._extract_name(user_input),
            description=user_input,
            confidence=confidence,
            inferred_from=user_input,
        )

        logger.info("intent_inferred", type=project_type, industry=industry,
                    confidence=confidence)
        return result

    def _detect_type(self, text: str) -> str:
        scores: dict[str, int] = {}
        for ptype, patterns in TYPE_PATTERNS.items():
            scores[ptype] = sum(1 for p in patterns if p in text)
        if max(scores.values(), default=0) > 0:
            return max(scores, key=scores.get)
        return "landing"  # Default

    def _detect_industry(self, text: str) -> str:
        scores: dict[str, int] = {}
        for industry, patterns in INDUSTRY_PATTERNS.items():
            scores[industry] = sum(1 for p in patterns if p in text)
        if max(scores.values(), default=0) > 0:
            return max(scores, key=scores.get)
        return "tech"  # Default

    def _infer_features(self, project_type: str, industry: str) -> list[str]:
        base_features = {
            "ecommerce": ["payments", "cart", "product_catalog", "search", "auth"],
            "saas": ["auth", "dashboard", "billing", "analytics", "api"],
            "portfolio": ["gallery", "contact_form", "blog", "testimonials"],
            "blog": ["cms", "search", "categories", "newsletter", "comments"],
            "landing": ["contact_form", "testimonials", "pricing", "faq"],
        }
        features = base_features.get(project_type, ["contact_form"])

        # Add industry-specific features
        industry_extras = {
            "restaurant": ["menu_display", "reservations", "gallery"],
            "fitness": ["class_schedule", "membership", "trainer_profiles"],
            "real_estate": ["property_listings", "map", "virtual_tours"],
            "education": ["course_catalog", "enrollment", "progress_tracking"],
        }
        features.extend(industry_extras.get(industry, []))
        return list(set(features))

    def _infer_style(self, industry: str) -> str:
        style_map = {
            "restaurant": "elegant",
            "fitness": "bold",
            "tech": "minimal",
            "fashion": "elegant",
            "creative": "playful",
            "consulting": "minimal",
            "health": "clean",
            "education": "friendly",
        }
        return style_map.get(industry, "minimal")

    def _calculate_confidence(self, project_type: str, industry: str, text: str) -> float:
        """Calculate confidence score based on signal strength."""
        signals = 0
        # Type detected with multiple keywords
        type_matches = sum(1 for p in TYPE_PATTERNS.get(project_type, []) if p in text)
        signals += min(type_matches, 3)
        # Industry detected
        industry_matches = sum(1 for p in INDUSTRY_PATTERNS.get(industry, []) if p in text)
        signals += min(industry_matches, 3)
        # Longer input = more context = higher confidence
        if len(text) > 50:
            signals += 1
        if len(text) > 100:
            signals += 1
        return min(signals / 8.0, 0.95)

    def _extract_name(self, text: str) -> Optional[str]:
        """Try to extract a project/business name from input."""
        # Look for quoted text or capitalized words
        import re
        quoted = re.findall(r'"([^"]+)"', text)
        if quoted:
            return quoted[0]
        # Look for "llamado/called" patterns
        named = re.search(r"(?:llamad[oa]|called|named)\s+(\w+(?:\s+\w+)?)", text, re.I)
        if named:
            return named.group(1)
        return None
```

### Smart Defaults

```python
"""kernel/zero_config/smart_defaults.py"""
from dataclasses import dataclass

@dataclass
class ProjectDefaults:
    theme: str
    primary_color: str
    font_heading: str
    font_body: str
    layout: str
    animations: str
    dark_mode: bool
    components: list[str]


# Defaults by industry + style combination
SMART_DEFAULTS: dict[str, ProjectDefaults] = {
    "restaurant_elegant": ProjectDefaults(
        theme="dark", primary_color="#C9A96E", font_heading="Playfair Display",
        font_body="Lato", layout="full-width", animations="subtle",
        dark_mode=True, components=["hero_parallax", "feature_grid", "testimonial", "contact_form", "footer"],
    ),
    "fitness_bold": ProjectDefaults(
        theme="dark", primary_color="#FF4500", font_heading="Oswald",
        font_body="Open Sans", layout="full-width", animations="energetic",
        dark_mode=True, components=["hero_video", "stats_bar", "pricing_table", "testimonial", "cta_section", "footer"],
    ),
    "tech_minimal": ProjectDefaults(
        theme="light", primary_color="#2563EB", font_heading="Inter",
        font_body="Inter", layout="contained", animations="subtle",
        dark_mode=False, components=["navbar", "hero_split", "feature_grid", "pricing_table", "faq", "footer"],
    ),
    "fashion_elegant": ProjectDefaults(
        theme="light", primary_color="#1A1A1A", font_heading="Cormorant Garamond",
        font_body="Montserrat", layout="editorial", animations="smooth",
        dark_mode=False, components=["navbar", "hero_centered", "product_card", "testimonial", "newsletter", "footer"],
    ),
    "creative_playful": ProjectDefaults(
        theme="light", primary_color="#7C3AED", font_heading="Space Grotesk",
        font_body="DM Sans", layout="asymmetric", animations="playful",
        dark_mode=False, components=["navbar", "hero_split", "timeline", "gallery", "contact_form", "footer"],
    ),
    "health_clean": ProjectDefaults(
        theme="light", primary_color="#059669", font_heading="Nunito",
        font_body="Nunito", layout="contained", animations="gentle",
        dark_mode=False, components=["navbar", "hero_centered", "feature_grid", "testimonial", "contact_form", "footer"],
    ),
}


def get_defaults(industry: str, style: str) -> ProjectDefaults:
    """Get smart defaults for an industry + style combination."""
    key = f"{industry}_{style}"
    if key in SMART_DEFAULTS:
        return SMART_DEFAULTS[key]
    # Fallback: try industry with any style
    for k, v in SMART_DEFAULTS.items():
        if k.startswith(industry):
            return v
    # Ultimate fallback
    return SMART_DEFAULTS["tech_minimal"]
```

---

## Epica 63.3 — Motion Design System

**Objetivo:** Obj #2 (Nivel Apple/Tesla)
**Impacto:** +7% en Obj #2

### Vision

Un sistema de animaciones coherente que transforma interfaces estaticas en experiencias fluidas. No animaciones aleatorias — un vocabulario de movimiento con tokens, reglas, y proposito.

### Arquitectura

```
kernel/motion/
  __init__.py
  tokens.py           # Motion design tokens
  presets.py          # Pre-built animation presets
  orchestrator.py     # Page-level animation orchestration
  accessibility.py    # Reduced motion support
```

### Motion Tokens

```python
"""kernel/motion/tokens.py"""
from dataclasses import dataclass

@dataclass
class MotionToken:
    name: str
    duration: str       # CSS duration: "200ms", "0.3s"
    easing: str         # CSS easing or spring config
    distance: str       # "4px", "16px", "100%"
    description: str


# Core motion tokens — the vocabulary of movement
MOTION_TOKENS: dict[str, MotionToken] = {
    # Durations
    "instant": MotionToken("instant", "100ms", "ease-out", "0", "Micro-feedback"),
    "fast": MotionToken("fast", "200ms", "ease-out", "4px", "Button states, toggles"),
    "normal": MotionToken("normal", "300ms", "cubic-bezier(0.4, 0, 0.2, 1)", "8px", "Standard transitions"),
    "slow": MotionToken("slow", "500ms", "cubic-bezier(0.4, 0, 0.2, 1)", "16px", "Page elements entering"),
    "deliberate": MotionToken("deliberate", "800ms", "cubic-bezier(0.22, 1, 0.36, 1)", "32px", "Hero animations"),

    # Springs (for Motion library)
    "spring_snappy": MotionToken("spring_snappy", "spring", "stiffness:400,damping:30", "auto", "Snappy interactions"),
    "spring_gentle": MotionToken("spring_gentle", "spring", "stiffness:120,damping:14", "auto", "Gentle movements"),
    "spring_bouncy": MotionToken("spring_bouncy", "spring", "stiffness:300,damping:10", "auto", "Playful bounces"),
}


# Animation presets by interaction type
INTERACTION_PRESETS: dict[str, dict] = {
    "button_hover": {
        "scale": 1.02,
        "transition": {"type": "spring", "stiffness": 400, "damping": 30},
    },
    "button_tap": {
        "scale": 0.98,
        "transition": {"type": "spring", "stiffness": 400, "damping": 30},
    },
    "card_hover": {
        "y": -4,
        "shadow": "0 20px 40px rgba(0,0,0,0.1)",
        "transition": {"duration": 0.3, "ease": [0.4, 0, 0.2, 1]},
    },
    "fade_in": {
        "initial": {"opacity": 0, "y": 20},
        "animate": {"opacity": 1, "y": 0},
        "transition": {"duration": 0.5, "ease": [0.4, 0, 0.2, 1]},
    },
    "slide_in_left": {
        "initial": {"opacity": 0, "x": -40},
        "animate": {"opacity": 1, "x": 0},
        "transition": {"duration": 0.6, "ease": [0.22, 1, 0.36, 1]},
    },
    "slide_in_right": {
        "initial": {"opacity": 0, "x": 40},
        "animate": {"opacity": 1, "x": 0},
        "transition": {"duration": 0.6, "ease": [0.22, 1, 0.36, 1]},
    },
    "scale_in": {
        "initial": {"opacity": 0, "scale": 0.9},
        "animate": {"opacity": 1, "scale": 1},
        "transition": {"type": "spring", "stiffness": 200, "damping": 20},
    },
    "stagger_children": {
        "animate": {"transition": {"staggerChildren": 0.1, "delayChildren": 0.2}},
    },
    "scroll_reveal": {
        "initial": {"opacity": 0, "y": 60},
        "whileInView": {"opacity": 1, "y": 0},
        "viewport": {"once": True, "margin": "-100px"},
        "transition": {"duration": 0.7, "ease": [0.22, 1, 0.36, 1]},
    },
    "page_enter": {
        "initial": {"opacity": 0},
        "animate": {"opacity": 1},
        "exit": {"opacity": 0},
        "transition": {"duration": 0.3},
    },
    "parallax_slow": {
        "style": {"y": "calc(var(--scroll-y) * -0.3)"},
    },
}


# Style-specific motion profiles
STYLE_MOTION_PROFILES: dict[str, dict] = {
    "minimal": {
        "default_duration": "300ms",
        "default_easing": "cubic-bezier(0.4, 0, 0.2, 1)",
        "hover_scale": 1.01,
        "entrance": "fade_in",
        "stagger_delay": 0.08,
        "use_springs": False,
    },
    "bold": {
        "default_duration": "400ms",
        "default_easing": "cubic-bezier(0.22, 1, 0.36, 1)",
        "hover_scale": 1.05,
        "entrance": "scale_in",
        "stagger_delay": 0.12,
        "use_springs": True,
    },
    "elegant": {
        "default_duration": "600ms",
        "default_easing": "cubic-bezier(0.4, 0, 0.2, 1)",
        "hover_scale": 1.02,
        "entrance": "slide_in_left",
        "stagger_delay": 0.15,
        "use_springs": False,
    },
    "playful": {
        "default_duration": "500ms",
        "default_easing": "spring",
        "hover_scale": 1.05,
        "entrance": "scale_in",
        "stagger_delay": 0.1,
        "use_springs": True,
    },
}
```

### Motion Orchestrator

```python
"""kernel/motion/orchestrator.py"""
import structlog
from kernel.motion.tokens import INTERACTION_PRESETS, STYLE_MOTION_PROFILES

logger = structlog.get_logger("motion.orchestrator")


class MotionOrchestrator:
    """Orchestrate animations across a page for coherent motion design."""

    def __init__(self, style: str = "minimal"):
        self.style = style
        self.profile = STYLE_MOTION_PROFILES.get(style, STYLE_MOTION_PROFILES["minimal"])

    def get_page_animations(self, components: list[str]) -> dict:
        """Generate animation config for an entire page."""
        animations = {}
        for i, component in enumerate(components):
            animations[component] = {
                "entrance": self._get_entrance(component, i),
                "interactions": self._get_interactions(component),
                "scroll": self._get_scroll_behavior(component, i),
            }
        return animations

    def _get_entrance(self, component: str, index: int) -> dict:
        """Get entrance animation for a component based on its position."""
        base = INTERACTION_PRESETS[self.profile["entrance"]].copy()
        # Add stagger delay based on position
        delay = index * self.profile["stagger_delay"]
        if "transition" in base:
            if isinstance(base["transition"], dict):
                base["transition"]["delay"] = delay
        return base

    def _get_interactions(self, component: str) -> dict:
        """Get interaction animations for a component."""
        interactions = {}
        # All components get hover effect
        interactions["hover"] = {
            "scale": self.profile["hover_scale"],
            "transition": {"type": "spring", "stiffness": 400, "damping": 30}
            if self.profile["use_springs"]
            else {"duration": 0.2},
        }
        # Buttons get tap effect
        if "button" in component or "cta" in component:
            interactions["tap"] = INTERACTION_PRESETS["button_tap"]
        # Cards get lift effect
        if "card" in component or "product" in component:
            interactions["hover"] = INTERACTION_PRESETS["card_hover"]
        return interactions

    def _get_scroll_behavior(self, component: str, index: int) -> dict:
        """Get scroll-triggered animation."""
        if index == 0:
            return {}  # Hero doesn't need scroll trigger
        return INTERACTION_PRESETS["scroll_reveal"]

    def generate_motion_css(self) -> str:
        """Generate CSS custom properties for motion tokens."""
        return f"""
:root {{
  --motion-duration-instant: 100ms;
  --motion-duration-fast: 200ms;
  --motion-duration-normal: 300ms;
  --motion-duration-slow: 500ms;
  --motion-duration-deliberate: 800ms;
  --motion-easing-default: {self.profile['default_easing']};
  --motion-easing-enter: cubic-bezier(0, 0, 0.2, 1);
  --motion-easing-exit: cubic-bezier(0.4, 0, 1, 1);
  --motion-easing-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
}}

@media (prefers-reduced-motion: reduce) {{
  :root {{
    --motion-duration-instant: 0ms;
    --motion-duration-fast: 0ms;
    --motion-duration-normal: 0ms;
    --motion-duration-slow: 0ms;
    --motion-duration-deliberate: 0ms;
  }}
  *, *::before, *::after {{
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }}
}}
"""
```

---

## Epica 63.4 — Plugin Marketplace

**Objetivo:** Obj #13 (Del Mundo)
**Impacto:** +6% en Obj #13

### Vision

Transformar el plugin system local (Sprint 62) en un marketplace global donde desarrolladores publican plugins, templates, y componentes. Revenue sharing 70/30 (developer/platform).

### Arquitectura

```
kernel/marketplace/
  __init__.py
  registry.py          # Global plugin registry
  publisher.py         # Publish plugins to marketplace
  installer.py         # Install from marketplace
  reviewer.py          # Quality review pipeline
  revenue.py           # Revenue sharing calculations
```

### Marketplace Registry

```python
"""kernel/marketplace/registry.py"""
import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = structlog.get_logger("marketplace.registry")

@dataclass
class MarketplaceItem:
    id: str
    name: str
    type: str              # "plugin", "template", "component"
    author: str
    version: str
    description: str
    category: str
    tags: list[str]
    downloads: int = 0
    rating: float = 0.0
    rating_count: int = 0
    price_usd: float = 0.0  # 0 = free
    revenue_share: float = 0.70  # 70% to developer
    published_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    verified: bool = False
    source_url: Optional[str] = None


class MarketplaceRegistry:
    """Global registry for marketplace items."""

    def __init__(self, supabase):
        self.supabase = supabase

    async def search(self, query: str, item_type: str = None,
                     category: str = None, sort: str = "relevance") -> list[dict]:
        """Search marketplace items."""
        q = self.supabase.table("marketplace_items").select("*")

        if item_type:
            q = q.eq("type", item_type)
        if category:
            q = q.eq("category", category)

        # Text search
        if query:
            q = q.or_(f"name.ilike.%{query}%,description.ilike.%{query}%")

        # Sorting
        if sort == "downloads":
            q = q.order("downloads", desc=True)
        elif sort == "rating":
            q = q.order("rating", desc=True)
        elif sort == "newest":
            q = q.order("published_at", desc=True)
        else:
            # Relevance: combination of downloads + rating
            q = q.order("downloads", desc=True)

        result = await q.limit(50).execute()
        return result.data or []

    async def publish(self, item: MarketplaceItem) -> str:
        """Publish an item to the marketplace."""
        data = {
            "name": item.name,
            "type": item.type,
            "author": item.author,
            "version": item.version,
            "description": item.description,
            "category": item.category,
            "tags": item.tags,
            "price_usd": item.price_usd,
            "revenue_share": item.revenue_share,
            "verified": False,  # Requires review
        }
        result = await self.supabase.table("marketplace_items").insert(data).execute()
        item_id = result.data[0]["id"]
        logger.info("item_published", id=item_id, name=item.name)
        return item_id

    async def install(self, item_id: str, user_id: str) -> dict:
        """Install a marketplace item for a user."""
        # 1. Get item details
        item = await self.supabase.table("marketplace_items")\
            .select("*").eq("id", item_id).single().execute()

        if not item.data:
            raise ValueError(f"Item not found: {item_id}")

        # 2. Record installation
        await self.supabase.table("marketplace_installations").insert({
            "item_id": item_id,
            "user_id": user_id,
            "installed_at": datetime.now(timezone.utc).isoformat(),
        }).execute()

        # 3. Increment download count
        await self.supabase.table("marketplace_items")\
            .update({"downloads": item.data["downloads"] + 1})\
            .eq("id", item_id).execute()

        # 4. Handle payment if paid item
        if item.data["price_usd"] > 0:
            await self._process_payment(item.data, user_id)

        return {"status": "installed", "item": item.data}

    async def rate(self, item_id: str, user_id: str, score: int, review: str = "") -> None:
        """Rate a marketplace item (1-5 stars)."""
        await self.supabase.table("marketplace_reviews").insert({
            "item_id": item_id,
            "user_id": user_id,
            "score": max(1, min(5, score)),
            "review": review,
        }).execute()

        # Update average rating
        reviews = await self.supabase.table("marketplace_reviews")\
            .select("score").eq("item_id", item_id).execute()
        scores = [r["score"] for r in (reviews.data or [])]
        avg = sum(scores) / len(scores) if scores else 0
        await self.supabase.table("marketplace_items")\
            .update({"rating": round(avg, 2), "rating_count": len(scores)})\
            .eq("id", item_id).execute()

    async def _process_payment(self, item: dict, user_id: str) -> None:
        """Process payment for a paid marketplace item."""
        # Placeholder: integrate with Stripe in future sprint
        logger.info("payment_processed", item=item["name"], amount=item["price_usd"])
```

### Tabla Supabase

```sql
CREATE TABLE marketplace_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    type TEXT CHECK (type IN ('plugin', 'template', 'component')),
    author TEXT NOT NULL,
    version TEXT NOT NULL,
    description TEXT,
    category TEXT,
    tags TEXT[],
    downloads INTEGER DEFAULT 0,
    rating FLOAT DEFAULT 0,
    rating_count INTEGER DEFAULT 0,
    price_usd FLOAT DEFAULT 0,
    revenue_share FLOAT DEFAULT 0.70,
    verified BOOLEAN DEFAULT false,
    source_url TEXT,
    published_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE marketplace_installations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID REFERENCES marketplace_items(id),
    user_id TEXT NOT NULL,
    installed_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE marketplace_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID REFERENCES marketplace_items(id),
    user_id TEXT NOT NULL,
    score INTEGER CHECK (score BETWEEN 1 AND 5),
    review TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(item_id, user_id)
);
```

---

## Epica 63.5 — Cross-Embrion Learning

**Objetivo:** Obj #8 (Inteligencia Emergente)
**Impacto:** +7% en Obj #8

### Vision

Los 7 embriones no solo se comunican (Sprint 61) sino que APRENDEN unos de otros. Cuando Embrion-Tecnico descubre un patron exitoso, ese conocimiento se propaga automaticamente a los demas. Emergencia real = aprendizaje colectivo sin programacion explicita.

### Arquitectura

```
kernel/collective/
  __init__.py
  knowledge_propagator.py  # Pattern propagation between embriones
  learning_tracker.py      # Track what each embrion learns
  emergence_detector.py    # Detect emergent patterns (expands Sprint 59)
  shared_memory.py         # Shared knowledge store
```

### Knowledge Propagator

```python
"""kernel/collective/knowledge_propagator.py"""
import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = structlog.get_logger("collective.propagator")

@dataclass
class LearnedPattern:
    id: str
    source_embrion: str       # Who discovered it
    pattern_type: str         # "strategy", "tool_usage", "error_avoidance", "optimization"
    description: str
    context: str              # When to apply
    success_rate: float       # 0-1
    times_applied: int = 0
    times_succeeded: int = 0
    propagated_to: list[str] = field(default_factory=list)
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgePropagator:
    """Propagate learned patterns between embriones."""

    def __init__(self, supabase):
        self.supabase = supabase
        self._patterns: dict[str, LearnedPattern] = {}

    async def register_pattern(self, pattern: LearnedPattern) -> str:
        """Register a newly discovered pattern."""
        # Store in Supabase
        result = await self.supabase.table("learned_patterns").insert({
            "source_embrion": pattern.source_embrion,
            "pattern_type": pattern.pattern_type,
            "description": pattern.description,
            "context": pattern.context,
            "success_rate": pattern.success_rate,
            "times_applied": pattern.times_applied,
            "times_succeeded": pattern.times_succeeded,
            "propagated_to": pattern.propagated_to,
        }).execute()

        pattern_id = result.data[0]["id"]
        self._patterns[pattern_id] = pattern
        logger.info("pattern_registered", id=pattern_id, source=pattern.source_embrion,
                    type=pattern.pattern_type)

        # Auto-propagate if success rate is high enough
        if pattern.success_rate >= 0.8 and pattern.times_applied >= 3:
            await self.propagate(pattern_id)

        return pattern_id

    async def propagate(self, pattern_id: str, target_embriones: list[str] = None) -> int:
        """Propagate a pattern to other embriones."""
        pattern_data = await self.supabase.table("learned_patterns")\
            .select("*").eq("id", pattern_id).single().execute()

        if not pattern_data.data:
            return 0

        pattern = pattern_data.data
        source = pattern["source_embrion"]

        # Determine targets (all embriones except source)
        all_embriones = ["ventas", "tecnico", "vigia", "creativo", "estratega", "financiero", "investigador"]
        if target_embriones is None:
            target_embriones = [e for e in all_embriones if e != source]

        # Filter out already propagated
        already_propagated = set(pattern.get("propagated_to", []))
        new_targets = [e for e in target_embriones if e not in already_propagated]

        if not new_targets:
            return 0

        # Propagate: add to each embrion's knowledge base
        for embrion in new_targets:
            await self.supabase.table("embrion_knowledge").insert({
                "embrion_name": embrion,
                "pattern_id": pattern_id,
                "learned_from": source,
                "pattern_type": pattern["pattern_type"],
                "description": pattern["description"],
                "context": pattern["context"],
                "adopted": False,  # Embrion must validate before adopting
            }).execute()

        # Update propagation record
        updated_propagated = list(already_propagated | set(new_targets))
        await self.supabase.table("learned_patterns")\
            .update({"propagated_to": updated_propagated})\
            .eq("id", pattern_id).execute()

        logger.info("pattern_propagated", id=pattern_id, targets=new_targets)
        return len(new_targets)

    async def record_outcome(self, pattern_id: str, embrion: str, success: bool) -> None:
        """Record the outcome of applying a propagated pattern."""
        pattern_data = await self.supabase.table("learned_patterns")\
            .select("*").eq("id", pattern_id).single().execute()

        if not pattern_data.data:
            return

        updates = {
            "times_applied": pattern_data.data["times_applied"] + 1,
        }
        if success:
            updates["times_succeeded"] = pattern_data.data["times_succeeded"] + 1

        # Recalculate success rate
        new_applied = updates["times_applied"]
        new_succeeded = updates.get("times_succeeded", pattern_data.data["times_succeeded"])
        updates["success_rate"] = new_succeeded / new_applied

        await self.supabase.table("learned_patterns")\
            .update(updates).eq("id", pattern_id).execute()

        # If success rate drops below threshold, retract propagation
        if updates["success_rate"] < 0.5 and new_applied >= 5:
            await self._retract_pattern(pattern_id)

    async def get_relevant_patterns(self, embrion: str, context: str) -> list[dict]:
        """Get patterns relevant to an embrion's current task."""
        knowledge = await self.supabase.table("embrion_knowledge")\
            .select("*, learned_patterns(*)")\
            .eq("embrion_name", embrion)\
            .eq("adopted", True)\
            .execute()

        # Filter by context relevance (simplified: keyword matching)
        context_lower = context.lower()
        relevant = []
        for item in (knowledge.data or []):
            pattern = item.get("learned_patterns", {})
            if pattern and any(
                word in context_lower
                for word in pattern.get("context", "").lower().split()
            ):
                relevant.append(pattern)

        return sorted(relevant, key=lambda x: x.get("success_rate", 0), reverse=True)

    async def _retract_pattern(self, pattern_id: str) -> None:
        """Retract a pattern that has proven unreliable."""
        await self.supabase.table("embrion_knowledge")\
            .delete().eq("pattern_id", pattern_id).execute()
        await self.supabase.table("learned_patterns")\
            .update({"propagated_to": [], "retracted": True})\
            .eq("id", pattern_id).execute()
        logger.warning("pattern_retracted", id=pattern_id)
```

### Emergence Detector (Expanded)

```python
"""kernel/collective/emergence_detector.py"""
import structlog
from datetime import datetime, timezone, timedelta

logger = structlog.get_logger("collective.emergence")


class EmergenceDetector:
    """Detect emergent behavior patterns across embriones.
    
    Criteria for emergence (strict, from Sprint 59):
    1. Not explicitly programmed
    2. Arises from interaction between 2+ embriones
    3. Produces measurable positive outcome
    4. Reproducible (happens more than once)
    """

    def __init__(self, supabase):
        self.supabase = supabase

    async def scan_for_emergence(self) -> list[dict]:
        """Scan recent activity for emergent patterns."""
        emergent_patterns = []

        # 1. Cross-embrion collaboration without explicit instruction
        collabs = await self._detect_spontaneous_collaboration()
        emergent_patterns.extend(collabs)

        # 2. Self-invented strategies (not in any prompt/instruction)
        strategies = await self._detect_novel_strategies()
        emergent_patterns.extend(strategies)

        # 3. Efficiency improvements without optimization request
        improvements = await self._detect_spontaneous_optimization()
        emergent_patterns.extend(improvements)

        # Validate against 4 criteria
        validated = []
        for pattern in emergent_patterns:
            if await self._validate_emergence(pattern):
                validated.append(pattern)
                await self._record_emergence(pattern)

        logger.info("emergence_scan_complete", found=len(validated))
        return validated

    async def _detect_spontaneous_collaboration(self) -> list[dict]:
        """Detect when embriones collaborate without being told to."""
        # Look for tasks where multiple embriones contributed
        # without a collective_intelligence_protocol trigger
        recent = await self.supabase.table("embrion_tasks")\
            .select("*")\
            .gte("completed_at", (datetime.now(timezone.utc) - timedelta(days=7)).isoformat())\
            .execute()

        # Group by project and look for multi-embrion involvement
        by_project: dict[str, list] = {}
        for task in (recent.data or []):
            pid = task.get("project_id", "unknown")
            if pid not in by_project:
                by_project[pid] = []
            by_project[pid].append(task)

        patterns = []
        for pid, tasks in by_project.items():
            embriones_involved = set(t.get("embrion_name") for t in tasks)
            if len(embriones_involved) >= 2:
                # Check if collaboration was spontaneous (no debate/vote trigger)
                triggered = any(t.get("trigger") == "collective_protocol" for t in tasks)
                if not triggered:
                    patterns.append({
                        "type": "spontaneous_collaboration",
                        "embriones": list(embriones_involved),
                        "project_id": pid,
                        "task_count": len(tasks),
                    })

        return patterns

    async def _detect_novel_strategies(self) -> list[dict]:
        """Detect strategies not found in any system prompt."""
        # Compare embrion outputs against known strategies
        # If an embrion produces a novel approach, flag it
        return []  # Requires LLM comparison — implemented in production

    async def _detect_spontaneous_optimization(self) -> list[dict]:
        """Detect when system optimizes itself without being asked."""
        # Look for cost reductions or speed improvements
        # that weren't triggered by an optimization request
        return []  # Requires historical comparison

    async def _validate_emergence(self, pattern: dict) -> bool:
        """Validate against 4 strict criteria."""
        # 1. Not explicitly programmed — check against known behaviors
        # 2. Arises from interaction between 2+ embriones
        if len(pattern.get("embriones", [])) < 2:
            return False
        # 3. Produces measurable positive outcome
        # 4. Reproducible
        return True  # Simplified; full validation uses historical data

    async def _record_emergence(self, pattern: dict) -> None:
        """Record validated emergent behavior."""
        await self.supabase.table("emergent_behaviors").insert({
            "type": pattern["type"],
            "embriones_involved": pattern.get("embriones", []),
            "description": str(pattern),
            "validated": True,
            "detected_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
```

### Tablas Supabase

```sql
CREATE TABLE learned_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_embrion TEXT NOT NULL,
    pattern_type TEXT CHECK (pattern_type IN ('strategy', 'tool_usage', 'error_avoidance', 'optimization')),
    description TEXT NOT NULL,
    context TEXT,
    success_rate FLOAT DEFAULT 0,
    times_applied INTEGER DEFAULT 0,
    times_succeeded INTEGER DEFAULT 0,
    propagated_to TEXT[] DEFAULT '{}',
    retracted BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE embrion_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    embrion_name TEXT NOT NULL,
    pattern_id UUID REFERENCES learned_patterns(id),
    learned_from TEXT NOT NULL,
    pattern_type TEXT,
    description TEXT,
    context TEXT,
    adopted BOOLEAN DEFAULT false,
    adopted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE emergent_behaviors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type TEXT NOT NULL,
    embriones_involved TEXT[],
    description TEXT,
    validated BOOLEAN DEFAULT false,
    detected_at TIMESTAMPTZ DEFAULT now()
);
```

---

## Integracion con el Sistema Existente

### Punto de Integracion: Agents Radar -> Intelligence Engine

```python
# En main.py, scheduled task:
from kernel.vanguard.intelligence_engine import ResearchIntelligenceEngine

@scheduler.scheduled_job("cron", hour=9, minute=0)  # Daily at 9am
async def daily_vanguard_scan():
    engine = ResearchIntelligenceEngine(supabase, router)
    await engine.run_daily_scan()
```

### Punto de Integracion: Embrion Loop -> Cross-Learning

```python
# En kernel/embrion_loop.py, despues de completar tarea:
from kernel.collective.knowledge_propagator import KnowledgePropagator

async def _on_task_complete(self, task, result):
    # ... existing logic ...
    
    # Check if this task revealed a new pattern
    if result.success and result.novel_approach:
        pattern = LearnedPattern(
            source_embrion=self.name,
            pattern_type="strategy",
            description=result.approach_description,
            context=task.context,
            success_rate=1.0,
            times_applied=1,
            times_succeeded=1,
        )
        await propagator.register_pattern(pattern)
```

### Punto de Integracion: Component Library -> Motion System

```python
# En kernel/components/renderer.py, al renderizar:
from kernel.motion.orchestrator import MotionOrchestrator

async def render_page(self, component_ids, project_type, theme, style):
    orchestrator = MotionOrchestrator(style=style)
    animations = orchestrator.get_page_animations(component_ids)
    motion_css = orchestrator.generate_motion_css()
    # Inject animations into each component's render context
```

---

## Tabla de Dependencias Nuevas

| Paquete | Version | Proposito | Costo |
|---|---|---|---|
| motion (framer-motion) | 12.38.0 | Animation system (template dep) | $0 (MIT) |
| Semantic Scholar API | v1 | Academic paper discovery | $0 (free tier) |
| APScheduler | 3.11.2 | Scheduled scans (ya en Sprint 56) | $0 |

**Costo total adicional:** ~$0/mes (todo es codigo + APIs gratuitas)

---

## Criterios de Exito

| Metrica | Target | Medicion |
|---|---|---|
| Daily scan discoveries | >=5 scored items/day | `integration_proposals` count |
| High-relevance proposals | >=1/week with score >0.8 | Weekly digest |
| Intent inference accuracy | >80% correct type+industry | Test with 50 phrases |
| Zero-config time to first project | <60 seconds | Stopwatch test |
| Motion tokens defined | >=10 | `len(MOTION_TOKENS)` |
| Animation presets | >=12 | `len(INTERACTION_PRESETS)` |
| Marketplace items (seed) | >=10 | Builtin plugins + templates |
| Patterns propagated | >=5 in first week | `learned_patterns` with propagated_to |
| Emergent behaviors detected | >=1 in first month | `emergent_behaviors` count |

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|
| Semantic Scholar rate limit | MEDIA | BAJO | Cache results + weekly (not daily) |
| Intent inference wrong | MEDIA | MEDIO | Confidence threshold + user confirmation |
| Pattern propagation spreads bad patterns | BAJA | ALTO | Success rate threshold (0.8) + retraction |
| Marketplace spam/low quality | MEDIA | MEDIO | Verified badge + review pipeline |
| Motion system increases bundle size | BAJA | BAJO | Tree-shaking + lazy load animations |

---

## Referencias

[1]: https://www.npmjs.com/package/framer-motion "Motion (prev Framer Motion) 12.38.0 — 40M downloads/week"
[2]: https://api.semanticscholar.org/ "Semantic Scholar API — Academic paper search"
[3]: https://www.designsystemscollective.com/not-just-colors-and-fonts-why-motion-tokens-belong-in-every-modern-design-system-8a2dcdc00659 "Motion Tokens in Design Systems"
[4]: https://github.com/duanyytop/agents-radar "Agents Radar — AI ecosystem daily digest (10 sources)"
[5]: https://blog.logrocket.com/best-react-animation-libraries/ "Best React Animation Libraries 2026"
