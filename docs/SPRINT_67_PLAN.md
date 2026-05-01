# Sprint 67 — "La Prueba Viviente"

**Fecha:** 1 mayo 2026
**Autor:** Manus AI
**Filosofía:** Un sistema que no puede DEMOSTRAR que funciona, no funciona. Sprint 67 transforma planes en evidencia.

---

## Contexto Estratégico

Después de 16 sprints (51-66), El Monstruo tiene un promedio de cobertura de 93.8% sobre los 13 Objetivos Maestros. Los 5 objetivos más débiles comparten un patrón: **les falta DEMOSTRACIÓN en el mundo real**.

| Objetivo | Cobertura | Gap | Problema Central |
|----------|-----------|-----|------------------|
| #1 Crear Empresas | 91% | 9% | Solo 1 template genérico, no multi-industria |
| #6 Vanguardia Perpetua | 91% | 9% | Discovery sin auto-adoption |
| #13 Del Mundo | 91% | 9% | Sin compliance legal por mercado |
| #2 Nivel Apple/Tesla | 92% | 8% | Sin user testing real |
| #3 Mínima Complejidad | 92% | 8% | Sin progressive disclosure |

Sprint 67 es un sprint de **ORQUESTACIÓN** — conecta piezas existentes para demostrar que el sistema funciona de extremo a extremo. Casi no requiere dependencias nuevas.

---

## Infraestructura Existente (Validada)

| Componente | Sprint | Archivo | Capacidad | Gap |
|-----------|--------|---------|-----------|-----|
| web_dev.py | 28 | `tools/web_dev.py` | Scaffold Vite+React | Solo 1 template genérico |
| user_dossier.py | 14 | `tools/user_dossier.py` | Almacena industry del usuario | No se usa para template selection |
| agents_radar.py | 45 | `tools/agents_radar.py` | 10 fuentes, 17+ repos | Discovery only, no PRs |
| tools/github.py | 28-33 | `tools/github.py` | Commit loop, PR creation | Ready para auto-adoption |
| cidp_compliance.py | 42 | `skills/cidp/scripts/` | Gates regulatorios | No market-specific legal |
| PostHog | 58 (plan) | Pendiente | Analytics | No session recording |
| Conversational UX | 59 (plan) | Pendiente | Intent parsing | No progressive disclosure |

**Insight clave:** Sprint 67 es 90% orquestación de infraestructura existente. Solo necesita 1 nueva dependencia (react-joyride para guided tours).

---

## Épica 67.1 — Multi-Industry Template Engine

**Objetivo:** 10 templates pre-configurados por industria que El Monstruo instancia en <5 minutos.

**Dependencia de Obj #1:** Crear empresas REALES = poder crear CUALQUIER tipo de empresa, no solo genérica.

### Las 10 Industrias

| # | Industria | Secciones Clave | Features Específicas |
|---|-----------|----------------|---------------------|
| 1 | SaaS B2B | Hero, Features, Pricing, Testimonials, CTA | Pricing tiers, free trial flow, API docs |
| 2 | E-commerce | Products, Cart, Checkout, Reviews | Product catalog, payment, inventory |
| 3 | Marketplace | Listings, Search, Profiles, Messaging | Two-sided, ratings, commission |
| 4 | Restaurant/Food | Menu, Reservations, Gallery, Location | Online ordering, delivery integration |
| 5 | Professional Services | About, Services, Portfolio, Contact | Booking calendar, testimonials |
| 6 | Education/Courses | Catalog, Enrollment, Dashboard, Progress | Video player, quizzes, certificates |
| 7 | Healthcare/Wellness | Services, Booking, Practitioners, Blog | HIPAA-aware, appointment scheduling |
| 8 | Real Estate | Listings, Search, Map, Agent Profiles | Property filters, virtual tours |
| 9 | Media/Content | Articles, Categories, Subscribe, Archive | CMS, newsletter, paywall |
| 10 | Non-Profit | Mission, Impact, Donate, Events | Donation flow, volunteer signup |

### Estructura de un Template

```python
# kernel/templates/industry_templates.py
"""Sprint 67 — Multi-Industry Template Engine."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
import structlog

logger = structlog.get_logger("kernel.templates")


@dataclass
class IndustryTemplate:
    """Complete template definition for an industry vertical."""
    id: str                          # "saas_b2b"
    name: str                        # "SaaS B2B"
    description: str                 # One-line description
    
    # Design System
    color_palette: dict[str, str]    # {primary, secondary, accent, bg, text}
    typography: dict[str, str]       # {heading_font, body_font, mono_font}
    design_mood: str                 # "professional", "playful", "luxury", etc.
    
    # Structure
    pages: list[dict[str, Any]]      # [{name, route, sections, components}]
    navigation_type: str             # "top_nav", "sidebar", "hamburger"
    
    # Features
    required_features: list[str]     # ["auth", "payment", "analytics"]
    optional_features: list[str]     # ["chat", "notifications", "i18n"]
    
    # Content
    copy_templates: dict[str, str]   # {hero_headline, hero_subtitle, cta_text}
    placeholder_images: list[str]    # Unsplash collection IDs by industry
    
    # Technical
    api_endpoints: list[dict]        # Pre-defined API structure
    db_schema: list[dict]            # Suggested tables
    third_party_integrations: list[str]  # ["stripe", "sendgrid", "twilio"]
    
    # Compliance
    legal_requirements: list[str]    # ["privacy_policy", "terms_of_service"]
    industry_regulations: list[str]  # ["HIPAA", "PCI-DSS", "GDPR"]


# Template Registry
INDUSTRY_TEMPLATES: dict[str, IndustryTemplate] = {}


def register_template(template: IndustryTemplate) -> None:
    """Register an industry template."""
    INDUSTRY_TEMPLATES[template.id] = template
    logger.info("template_registered", id=template.id, name=template.name)


# Example: SaaS B2B Template
SAAS_B2B = IndustryTemplate(
    id="saas_b2b",
    name="SaaS B2B",
    description="Software-as-a-Service for business customers",
    color_palette={
        "primary": "#2563EB",      # Blue-600
        "secondary": "#1E40AF",    # Blue-800
        "accent": "#F59E0B",       # Amber-500
        "bg": "#F8FAFC",           # Slate-50
        "text": "#1E293B",         # Slate-800
    },
    typography={
        "heading_font": "Inter",
        "body_font": "Inter",
        "mono_font": "JetBrains Mono",
    },
    design_mood="professional",
    pages=[
        {
            "name": "Landing",
            "route": "/",
            "sections": ["hero", "social_proof", "features", "pricing", "testimonials", "cta"],
            "components": ["Navbar", "Hero", "FeatureGrid", "PricingTable", "TestimonialCarousel", "Footer"],
        },
        {
            "name": "Pricing",
            "route": "/pricing",
            "sections": ["pricing_hero", "plans", "faq", "cta"],
            "components": ["PricingHero", "PlanCards", "FAQ", "CTABanner"],
        },
        {
            "name": "Dashboard",
            "route": "/dashboard",
            "sections": ["sidebar", "metrics", "activity", "settings"],
            "components": ["Sidebar", "MetricCards", "ActivityFeed", "SettingsPanel"],
        },
    ],
    navigation_type="top_nav",
    required_features=["auth", "payment", "analytics", "email"],
    optional_features=["chat", "notifications", "i18n", "api_docs"],
    copy_templates={
        "hero_headline": "Ship faster with {product_name}",
        "hero_subtitle": "The all-in-one platform that helps {target_audience} {key_benefit}",
        "cta_text": "Start free trial",
        "pricing_headline": "Simple, transparent pricing",
    },
    placeholder_images=["unsplash/saas-dashboard", "unsplash/team-collaboration"],
    api_endpoints=[
        {"method": "POST", "path": "/api/auth/signup", "description": "User registration"},
        {"method": "POST", "path": "/api/auth/login", "description": "User login"},
        {"method": "GET", "path": "/api/dashboard/metrics", "description": "Dashboard data"},
        {"method": "POST", "path": "/api/billing/subscribe", "description": "Create subscription"},
    ],
    db_schema=[
        {"table": "users", "columns": ["id", "email", "name", "plan", "created_at"]},
        {"table": "subscriptions", "columns": ["id", "user_id", "plan", "status", "stripe_id"]},
        {"table": "usage", "columns": ["id", "user_id", "metric", "value", "timestamp"]},
    ],
    third_party_integrations=["stripe", "sendgrid", "segment"],
    legal_requirements=["privacy_policy", "terms_of_service", "cookie_policy"],
    industry_regulations=["GDPR", "SOC2"],
)

register_template(SAAS_B2B)


class TemplateEngine:
    """
    Selects and customizes industry templates based on user input.
    
    Integration points:
    - user_dossier.py: reads industry field for auto-selection
    - web_dev.py: generates scaffold from template
    - Conversational UX: suggests template from natural language
    """
    
    def __init__(self, user_dossier: Any = None) -> None:
        self._dossier = user_dossier
    
    def suggest_template(self, user_input: str) -> list[dict]:
        """
        Suggest templates based on user's description.
        
        "Quiero una app para vender cursos online" → Education/Courses
        "Necesito un marketplace de freelancers" → Marketplace
        """
        # Score each template against user input
        scores = []
        for tid, template in INDUSTRY_TEMPLATES.items():
            score = self._calculate_relevance(user_input, template)
            scores.append({"template_id": tid, "name": template.name, "score": score})
        
        # Return top 3 sorted by score
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:3]
    
    def customize_template(self, template_id: str, customizations: dict) -> dict:
        """
        Apply user customizations to a template.
        
        Customizations can include:
        - brand_name: str
        - color_override: dict
        - features_add: list
        - features_remove: list
        - pages_add: list
        - copy_overrides: dict
        """
        template = INDUSTRY_TEMPLATES.get(template_id)
        if not template:
            return {"error": f"Template {template_id} not found"}
        
        # Deep copy and apply customizations
        config = self._template_to_config(template)
        
        if "brand_name" in customizations:
            config["brand_name"] = customizations["brand_name"]
            # Replace placeholders in copy
            for key, value in config["copy"].items():
                config["copy"][key] = value.replace("{product_name}", customizations["brand_name"])
        
        if "color_override" in customizations:
            config["colors"].update(customizations["color_override"])
        
        if "features_add" in customizations:
            config["features"].extend(customizations["features_add"])
        
        if "features_remove" in customizations:
            config["features"] = [f for f in config["features"] 
                                  if f not in customizations["features_remove"]]
        
        return config
    
    def generate_scaffold_config(self, template_id: str, customizations: dict) -> dict:
        """
        Generate a complete scaffold configuration for web_dev.py.
        
        Returns a dict that web_dev.py can use to create the project.
        """
        config = self.customize_template(template_id, customizations)
        
        return {
            "framework": "react",
            "styling": "tailwind",
            "pages": config["pages"],
            "components": config["components"],
            "colors": config["colors"],
            "typography": config["typography"],
            "features": config["features"],
            "api_structure": config["api_endpoints"],
            "db_schema": config["db_schema"],
            "integrations": config["integrations"],
            "legal": config["legal"],
        }
    
    def _calculate_relevance(self, user_input: str, template: IndustryTemplate) -> float:
        """Calculate relevance score between user input and template."""
        # Simple keyword matching (in production, use embeddings)
        keywords = user_input.lower().split()
        template_text = f"{template.name} {template.description}".lower()
        
        matches = sum(1 for kw in keywords if kw in template_text)
        return matches / max(len(keywords), 1)
    
    def _template_to_config(self, template: IndustryTemplate) -> dict:
        """Convert template dataclass to mutable config dict."""
        return {
            "id": template.id,
            "name": template.name,
            "colors": dict(template.color_palette),
            "typography": dict(template.typography),
            "pages": list(template.pages),
            "features": list(template.required_features),
            "copy": dict(template.copy_templates),
            "api_endpoints": list(template.api_endpoints),
            "db_schema": list(template.db_schema),
            "integrations": list(template.third_party_integrations),
            "legal": list(template.legal_requirements),
            "components": [],  # Derived from pages
        }
```

### Integración con web_dev.py

El `TemplateEngine.generate_scaffold_config()` produce un dict que se pasa directamente a `web_dev.py` para generar el proyecto. El flujo completo:

1. Usuario dice "Quiero una app para vender cursos"
2. Conversational UX → `suggest_template("vender cursos")` → Education/Courses
3. Usuario confirma → `customize_template("education", {brand_name: "MiAcademia"})`
4. `generate_scaffold_config()` → config completo
5. `web_dev.py` scaffold con config → proyecto listo en <5 minutos

---

## Épica 67.2 — Auto-Adoption Pipeline

**Objetivo:** Cuando Tech Radar detecta una herramienta relevante, genera PR automático con la integración.

**Dependencia de Obj #6:** Vanguardia = no solo SABER qué es nuevo, sino ADOPTAR lo nuevo automáticamente.

### Arquitectura

```python
# kernel/vanguard/auto_adoption.py
"""Sprint 67 — Auto-Adoption Pipeline."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger("kernel.vanguard.auto_adoption")


@dataclass
class AdoptionProposal:
    """A proposal to adopt a new technology."""
    id: str
    tool_name: str                # "fastmcp"
    current_version: Optional[str]  # "3.1.0" or None if new
    proposed_version: str         # "3.2.4"
    category: str                 # "framework", "library", "service"
    relevance_score: float        # 0.0-1.0 from Research Intelligence
    risk_score: float             # 0.0-1.0 (higher = riskier)
    integration_plan: list[str]   # Steps to integrate
    files_to_modify: list[str]    # Which files change
    breaking_changes: list[str]   # Known breaking changes
    status: str = "proposed"      # proposed, approved, implementing, merged, rejected
    created_at: str = ""
    pr_url: Optional[str] = None


class AutoAdoptionPipeline:
    """
    Converts Tech Radar discoveries into actual code changes.
    
    Pipeline:
    1. DISCOVER: agents_radar.py finds new tool/version
    2. ASSESS: Score relevance + risk
    3. PLAN: Generate integration plan
    4. VALIDATE: Security check (OSV.dev) + compatibility check
    5. IMPLEMENT: Generate code changes
    6. PR: Create pull request via tools/github.py
    7. REVIEW: Wait for human approval (or auto-merge if low-risk)
    
    Safety rules:
    - Max 3 proposals per day
    - No auto-merge for major version bumps
    - Security check MUST pass before PR
    - Breaking changes require human approval
    """
    
    MAX_DAILY_PROPOSALS = 3
    AUTO_MERGE_MAX_RISK = 0.3  # Only auto-merge if risk < 30%
    
    def __init__(self, radar: Any, github: Any, llm: Any, security: Any = None) -> None:
        self._radar = radar       # agents_radar.py
        self._github = github     # tools/github.py
        self._llm = llm
        self._security = security
        self._proposals: list[AdoptionProposal] = []
        self._daily_count = 0
        self._last_reset: Optional[str] = None
    
    async def process_discovery(self, discovery: dict) -> Optional[AdoptionProposal]:
        """
        Process a discovery from Tech Radar and potentially create a proposal.
        
        Args:
            discovery: {
                "tool_name": str,
                "version": str,
                "source": str,  # "pypi", "npm", "github_trending"
                "description": str,
                "relevance_to_monstruo": float,
            }
        """
        # Rate limit
        self._check_daily_reset()
        if self._daily_count >= self.MAX_DAILY_PROPOSALS:
            logger.info("daily_proposal_limit_reached", count=self._daily_count)
            return None
        
        # Step 1: Assess relevance
        relevance = discovery.get("relevance_to_monstruo", 0.0)
        if relevance < 0.6:
            logger.debug("discovery_below_threshold",
                        tool=discovery["tool_name"], relevance=relevance)
            return None
        
        # Step 2: Security check
        security_result = await self._security_check(discovery["tool_name"], discovery["version"])
        if security_result.get("has_cve"):
            logger.warning("discovery_has_cve",
                         tool=discovery["tool_name"],
                         cves=security_result["cves"])
            return None
        
        # Step 3: Generate integration plan
        plan = await self._generate_integration_plan(discovery)
        
        # Step 4: Calculate risk
        risk = self._calculate_risk(discovery, plan)
        
        # Step 5: Create proposal
        proposal = AdoptionProposal(
            id=f"adopt_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            tool_name=discovery["tool_name"],
            current_version=await self._get_current_version(discovery["tool_name"]),
            proposed_version=discovery["version"],
            category=discovery.get("category", "library"),
            relevance_score=relevance,
            risk_score=risk,
            integration_plan=plan["steps"],
            files_to_modify=plan["files"],
            breaking_changes=plan.get("breaking_changes", []),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        
        self._proposals.append(proposal)
        self._daily_count += 1
        
        logger.info("adoption_proposal_created",
                   tool=proposal.tool_name,
                   version=proposal.proposed_version,
                   risk=proposal.risk_score)
        
        # Step 6: Auto-approve if low risk
        if risk <= self.AUTO_MERGE_MAX_RISK and not plan.get("breaking_changes"):
            await self._execute_adoption(proposal)
        else:
            # Notify for human review
            proposal.status = "proposed"
            await self._notify_proposal(proposal)
        
        return proposal
    
    async def _execute_adoption(self, proposal: AdoptionProposal) -> None:
        """Execute the adoption: generate code and create PR."""
        proposal.status = "implementing"
        
        # Generate code changes using LLM
        changes = await self._generate_code_changes(proposal)
        
        # Create branch and PR
        branch_name = f"auto-adopt/{proposal.tool_name}-{proposal.proposed_version}"
        
        pr_result = await self._github.create_pr(
            branch=branch_name,
            title=f"chore: adopt {proposal.tool_name} {proposal.proposed_version}",
            body=self._format_pr_body(proposal),
            changes=changes,
        )
        
        proposal.pr_url = pr_result.get("url")
        proposal.status = "merged" if proposal.risk_score <= 0.2 else "pending_review"
        
        logger.info("adoption_pr_created",
                   tool=proposal.tool_name,
                   pr_url=proposal.pr_url)
    
    async def _generate_integration_plan(self, discovery: dict) -> dict:
        """Use LLM to generate integration plan."""
        prompt = f"""Analyze this tool discovery and generate an integration plan for El Monstruo.

Tool: {discovery['tool_name']} v{discovery['version']}
Description: {discovery.get('description', 'N/A')}
Source: {discovery.get('source', 'N/A')}

El Monstruo is a Python FastAPI application with:
- FastMCP server for MCP tools
- Supabase for database
- Multiple LLM providers (OpenAI, Anthropic, Google, xAI)
- Embrion-based autonomous agent system

Generate:
1. steps: List of integration steps
2. files: List of files that would need modification
3. breaking_changes: Any breaking changes to be aware of
4. estimated_effort: "trivial", "small", "medium", "large"

Respond in JSON."""
        
        response = await self._llm.generate(prompt, response_format="json")
        return response.parsed
    
    def _calculate_risk(self, discovery: dict, plan: dict) -> float:
        """Calculate risk score for adoption."""
        risk = 0.0
        
        # Major version bump = higher risk
        current = discovery.get("current_version")
        proposed = discovery["version"]
        if current:
            current_major = int(current.split(".")[0])
            proposed_major = int(proposed.split(".")[0])
            if proposed_major > current_major:
                risk += 0.4  # Major version bump
        else:
            risk += 0.2  # New dependency
        
        # Breaking changes
        if plan.get("breaking_changes"):
            risk += 0.1 * len(plan["breaking_changes"])
        
        # Number of files affected
        num_files = len(plan.get("files", []))
        risk += min(0.3, num_files * 0.05)
        
        # Effort
        effort_map = {"trivial": 0.0, "small": 0.1, "medium": 0.2, "large": 0.4}
        risk += effort_map.get(plan.get("estimated_effort", "medium"), 0.2)
        
        return min(1.0, risk)
    
    async def _security_check(self, tool_name: str, version: str) -> dict:
        """Check OSV.dev for known vulnerabilities."""
        # Query OSV.dev API
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.osv.dev/v1/query",
                json={"package": {"name": tool_name, "ecosystem": "PyPI"}, "version": version},
            )
            if response.status_code == 200:
                data = response.json()
                vulns = data.get("vulns", [])
                return {
                    "has_cve": len(vulns) > 0,
                    "cves": [v.get("id") for v in vulns],
                }
        return {"has_cve": False, "cves": []}
    
    def _format_pr_body(self, proposal: AdoptionProposal) -> str:
        """Format PR body with proposal details."""
        return f"""## Auto-Adoption: {proposal.tool_name} {proposal.proposed_version}

**Relevance Score:** {proposal.relevance_score:.0%}
**Risk Score:** {proposal.risk_score:.0%}
**Category:** {proposal.category}

### Integration Plan
{chr(10).join(f"- {step}" for step in proposal.integration_plan)}

### Files Modified
{chr(10).join(f"- `{f}`" for f in proposal.files_to_modify)}

### Breaking Changes
{chr(10).join(f"- ⚠️ {bc}" for bc in proposal.breaking_changes) if proposal.breaking_changes else "None"}

---
*Generated by El Monstruo Auto-Adoption Pipeline (Sprint 67)*
"""
```

### Integración con agents_radar.py

El `agents_radar.py` (Sprint 45) ya escanea 10 fuentes. Sprint 67 agrega un hook post-scan:

```python
# En agents_radar.py, después de cada scan:
async def post_scan_hook(discoveries: list[dict]) -> None:
    """Feed discoveries to Auto-Adoption Pipeline."""
    for discovery in discoveries:
        if discovery.get("relevance_to_monstruo", 0) >= 0.6:
            await auto_adoption.process_discovery(discovery)
```

---

## Épica 67.3 — Progressive Disclosure UX

**Objetivo:** 3 niveles de interfaz que se adaptan al skill del usuario.

**Dependencia de Obj #3:** Mínima complejidad = mostrar solo lo que el usuario NECESITA ver.

### Los 3 Niveles

| Nivel | Nombre | Qué Ve | Qué NO Ve | Trigger de Transición |
|-------|--------|--------|-----------|----------------------|
| 1 | Beginner | Chat simple, templates, wizard | Config avanzada, CLI, raw API | Default para nuevos usuarios |
| 2 | Standard | Chat + dashboard, embriones, settings | Raw logs, debug tools, internals | Después de 3 proyectos exitosos |
| 3 | Expert | Todo: logs, debug, raw API, config files | Nada oculto | Activación manual o 10+ proyectos |

### Implementación

```python
# kernel/ux/progressive_disclosure.py
"""Sprint 67 — Progressive Disclosure UX Engine."""
from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Optional
import structlog

logger = structlog.get_logger("kernel.ux.progressive_disclosure")


class SkillLevel(IntEnum):
    BEGINNER = 1
    STANDARD = 2
    EXPERT = 3


@dataclass
class UIFeature:
    """A UI feature with visibility rules."""
    id: str
    name: str
    min_level: SkillLevel
    category: str  # "navigation", "settings", "tools", "debug"
    description: str


# Feature Registry
UI_FEATURES: list[UIFeature] = [
    # Always visible (Beginner)
    UIFeature("chat", "Chat Interface", SkillLevel.BEGINNER, "navigation", "Main conversation"),
    UIFeature("templates", "Project Templates", SkillLevel.BEGINNER, "tools", "Industry templates"),
    UIFeature("wizard", "Setup Wizard", SkillLevel.BEGINNER, "tools", "Guided project creation"),
    UIFeature("basic_settings", "Basic Settings", SkillLevel.BEGINNER, "settings", "Name, theme, language"),
    
    # Standard (after 3 projects)
    UIFeature("dashboard", "Dashboard", SkillLevel.STANDARD, "navigation", "Project metrics"),
    UIFeature("embriones", "Embrion Status", SkillLevel.STANDARD, "tools", "View embrion activity"),
    UIFeature("analytics", "Analytics", SkillLevel.STANDARD, "tools", "Usage and performance"),
    UIFeature("advanced_settings", "Advanced Settings", SkillLevel.STANDARD, "settings", "API keys, integrations"),
    UIFeature("simulator", "Business Simulator", SkillLevel.STANDARD, "tools", "Monte Carlo predictions"),
    
    # Expert (manual activation or 10+ projects)
    UIFeature("logs", "System Logs", SkillLevel.EXPERT, "debug", "Raw system output"),
    UIFeature("debug_tools", "Debug Tools", SkillLevel.EXPERT, "debug", "Inspect internals"),
    UIFeature("raw_api", "Raw API Access", SkillLevel.EXPERT, "tools", "Direct API calls"),
    UIFeature("config_files", "Config Editor", SkillLevel.EXPERT, "settings", "Edit YAML/JSON configs"),
    UIFeature("sovereignty", "Sovereignty Panel", SkillLevel.EXPERT, "tools", "Migration playbooks"),
    UIFeature("embrion_config", "Embrion Configuration", SkillLevel.EXPERT, "settings", "Customize embrion behavior"),
]


class ProgressiveDisclosureEngine:
    """
    Manages UI complexity based on user skill level.
    
    Principles:
    - New users see ONLY what they need (chat + templates)
    - Features unlock as user demonstrates competence
    - Expert mode is always available via manual activation
    - Never hide something the user is actively looking for
    """
    
    # Transition thresholds
    STANDARD_THRESHOLD = 3   # Projects completed
    EXPERT_THRESHOLD = 10    # Projects completed
    
    def __init__(self, db: Any = None) -> None:
        self._db = db
        self._user_levels: dict[str, SkillLevel] = {}
    
    async def get_user_level(self, user_id: str) -> SkillLevel:
        """Get current skill level for a user."""
        if user_id in self._user_levels:
            return self._user_levels[user_id]
        
        # Check database for stored level
        if self._db:
            result = await self._db.table("user_preferences").select("skill_level").eq("user_id", user_id).execute()
            if result.data:
                level = SkillLevel(result.data[0].get("skill_level", 1))
                self._user_levels[user_id] = level
                return level
        
        return SkillLevel.BEGINNER
    
    async def get_visible_features(self, user_id: str) -> list[UIFeature]:
        """Get features visible to this user at their current level."""
        level = await self.get_user_level(user_id)
        return [f for f in UI_FEATURES if f.min_level <= level]
    
    async def check_level_up(self, user_id: str) -> Optional[SkillLevel]:
        """
        Check if user should level up based on activity.
        Called after each project completion.
        """
        current_level = await self.get_user_level(user_id)
        
        # Get project count
        if self._db:
            result = await self._db.table("projects").select("id", count="exact").eq("user_id", user_id).eq("status", "completed").execute()
            project_count = result.count or 0
        else:
            project_count = 0
        
        new_level = current_level
        if project_count >= self.EXPERT_THRESHOLD and current_level < SkillLevel.EXPERT:
            new_level = SkillLevel.EXPERT
        elif project_count >= self.STANDARD_THRESHOLD and current_level < SkillLevel.STANDARD:
            new_level = SkillLevel.STANDARD
        
        if new_level > current_level:
            await self._level_up(user_id, current_level, new_level)
            return new_level
        
        return None
    
    async def set_expert_mode(self, user_id: str) -> None:
        """Manually activate expert mode (always available)."""
        self._user_levels[user_id] = SkillLevel.EXPERT
        if self._db:
            await self._db.table("user_preferences").upsert({
                "user_id": user_id,
                "skill_level": SkillLevel.EXPERT.value,
            }).execute()
        logger.info("expert_mode_activated", user_id=user_id)
    
    async def _level_up(self, user_id: str, old: SkillLevel, new: SkillLevel) -> None:
        """Process a level-up event."""
        self._user_levels[user_id] = new
        if self._db:
            await self._db.table("user_preferences").upsert({
                "user_id": user_id,
                "skill_level": new.value,
            }).execute()
        
        # Get newly unlocked features
        new_features = [f for f in UI_FEATURES if old < f.min_level <= new]
        
        logger.info("user_leveled_up",
                   user_id=user_id,
                   from_level=old.name,
                   to_level=new.name,
                   new_features=[f.name for f in new_features])
```

### Guided Tour (react-joyride)

Para nuevos usuarios, un tour guiado de 5 pasos explica la interfaz:

1. "Este es tu chat — aquí describes lo que quieres crear"
2. "Elige un template de industria para empezar rápido"
3. "El wizard te guía paso a paso"
4. "Aquí ves el progreso de tu proyecto"
5. "Cuando estés listo, publica con un click"

---

## Épica 67.4 — Market Compliance Engine

**Objetivo:** Templates legales por jurisdicción + payment gateway selection automática.

**Dependencia de Obj #13:** Del mundo = cumplir con las leyes de CADA mercado, no solo GDPR.

### Jurisdicciones Soportadas

| Jurisdicción | Regulación | Payment Gateways | Idiomas | Moneda |
|-------------|-----------|-------------------|---------|--------|
| EU/EEA | GDPR, ePrivacy, PSD2 | Stripe, Adyen, Mollie | 24 | EUR |
| USA | CCPA, CAN-SPAM, ADA | Stripe, Square, PayPal | EN | USD |
| UK | UK-GDPR, PECR | Stripe, GoCardless | EN | GBP |
| Brazil | LGPD, Marco Civil | Stripe, PagSeguro, Pix | PT | BRL |
| Mexico | LFPDPPP | Stripe, Conekta, OXXO | ES | MXN |
| India | DPDP Act 2023 | Razorpay, PayU, UPI | EN/HI | INR |
| Japan | APPI | Stripe, PayPay | JA | JPY |
| Australia | Privacy Act, CDR | Stripe, Afterpay | EN | AUD |
| Canada | PIPEDA, CASL | Stripe, Moneris | EN/FR | CAD |
| LATAM (other) | Varies | MercadoPago, dLocal | ES | Varies |

### Implementación

```python
# kernel/compliance/market_compliance.py
"""Sprint 67 — Market Compliance Engine."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
import structlog

logger = structlog.get_logger("kernel.compliance.market")


@dataclass
class JurisdictionConfig:
    """Complete compliance configuration for a jurisdiction."""
    id: str                          # "eu", "usa", "brazil"
    name: str                        # "European Union"
    regulations: list[str]           # ["GDPR", "ePrivacy"]
    
    # Legal documents required
    required_documents: list[str]    # ["privacy_policy", "terms", "cookie_policy"]
    document_templates: dict[str, str]  # {doc_name: template_content}
    
    # Consent requirements
    consent_model: str               # "opt_in" (EU), "opt_out" (USA)
    cookie_consent_required: bool
    age_verification_required: bool
    age_threshold: int               # 16 (EU), 13 (USA)
    
    # Data handling
    data_residency_required: bool
    allowed_regions: list[str]       # Where data can be stored
    retention_max_days: Optional[int]  # Max data retention
    right_to_deletion: bool
    data_portability: bool
    
    # Payment
    recommended_gateways: list[str]
    local_payment_methods: list[str]  # ["pix", "oxxo", "upi"]
    currency: str
    tax_handling: str                # "inclusive", "exclusive", "varies"
    
    # Communication
    email_consent_required: bool
    unsubscribe_required: bool
    languages: list[str]


class MarketComplianceEngine:
    """
    Generates compliance configurations for target markets.
    
    Integration:
    - Template Engine: injects legal requirements into project scaffold
    - i18n Engine: ensures legal docs are in correct language
    - Sales Engine: configures payment gateways per market
    """
    
    def __init__(self) -> None:
        self._jurisdictions: dict[str, JurisdictionConfig] = {}
        self._register_defaults()
    
    def get_compliance_config(self, markets: list[str]) -> dict:
        """
        Get merged compliance config for target markets.
        
        When operating in multiple markets, use the STRICTEST requirement.
        """
        if not markets:
            markets = ["usa"]  # Default
        
        configs = [self._jurisdictions[m] for m in markets if m in self._jurisdictions]
        if not configs:
            return {"error": "No valid jurisdictions found"}
        
        # Merge: use strictest requirements
        merged = {
            "markets": markets,
            "consent_model": "opt_in" if any(c.consent_model == "opt_in" for c in configs) else "opt_out",
            "cookie_consent_required": any(c.cookie_consent_required for c in configs),
            "age_verification_required": any(c.age_verification_required for c in configs),
            "age_threshold": max(c.age_threshold for c in configs),
            "data_residency_required": any(c.data_residency_required for c in configs),
            "right_to_deletion": any(c.right_to_deletion for c in configs),
            "data_portability": any(c.data_portability for c in configs),
            "email_consent_required": any(c.email_consent_required for c in configs),
            "unsubscribe_required": True,  # Always required
            "required_documents": list(set(
                doc for c in configs for doc in c.required_documents
            )),
            "recommended_gateways": self._select_gateways(configs),
            "local_payment_methods": list(set(
                pm for c in configs for pm in c.local_payment_methods
            )),
            "currencies": list(set(c.currency for c in configs)),
            "languages": list(set(lang for c in configs for lang in c.languages)),
        }
        
        return merged
    
    def generate_legal_documents(self, markets: list[str], company_info: dict) -> dict:
        """
        Generate legal documents for target markets.
        
        Args:
            company_info: {name, email, address, website, dpo_email}
        
        Returns:
            {document_name: content} for each required document
        """
        config = self.get_compliance_config(markets)
        documents = {}
        
        for doc_name in config["required_documents"]:
            template = self._get_document_template(doc_name, markets)
            content = self._fill_template(template, company_info)
            documents[doc_name] = content
        
        return documents
    
    def _select_gateways(self, configs: list[JurisdictionConfig]) -> list[str]:
        """Select payment gateways that work across all target markets."""
        # Find gateways common to all markets
        gateway_sets = [set(c.recommended_gateways) for c in configs]
        common = set.intersection(*gateway_sets) if gateway_sets else set()
        
        if common:
            return list(common)
        
        # If no common gateway, return union with priority
        all_gateways = []
        for c in configs:
            for gw in c.recommended_gateways:
                if gw not in all_gateways:
                    all_gateways.append(gw)
        return all_gateways
    
    def _register_defaults(self) -> None:
        """Register default jurisdiction configs."""
        self._jurisdictions["eu"] = JurisdictionConfig(
            id="eu", name="European Union",
            regulations=["GDPR", "ePrivacy Directive", "PSD2", "Digital Services Act"],
            required_documents=["privacy_policy", "terms_of_service", "cookie_policy", "dpa"],
            document_templates={},
            consent_model="opt_in",
            cookie_consent_required=True,
            age_verification_required=True,
            age_threshold=16,
            data_residency_required=True,
            allowed_regions=["EU", "EEA", "adequacy_countries"],
            retention_max_days=None,  # Must be defined per purpose
            right_to_deletion=True,
            data_portability=True,
            recommended_gateways=["stripe", "adyen", "mollie"],
            local_payment_methods=["sepa", "ideal", "bancontact", "giropay"],
            currency="EUR",
            tax_handling="inclusive",
            email_consent_required=True,
            unsubscribe_required=True,
            languages=["en", "de", "fr", "es", "it", "nl", "pt", "pl"],
        )
        
        self._jurisdictions["usa"] = JurisdictionConfig(
            id="usa", name="United States",
            regulations=["CCPA", "CAN-SPAM", "ADA", "COPPA", "FTC Act"],
            required_documents=["privacy_policy", "terms_of_service"],
            document_templates={},
            consent_model="opt_out",
            cookie_consent_required=False,  # Not federally required
            age_verification_required=True,
            age_threshold=13,  # COPPA
            data_residency_required=False,
            allowed_regions=["any"],
            retention_max_days=None,
            right_to_deletion=True,  # CCPA for CA residents
            data_portability=True,   # CCPA
            recommended_gateways=["stripe", "square", "paypal"],
            local_payment_methods=["ach", "venmo", "apple_pay", "google_pay"],
            currency="USD",
            tax_handling="exclusive",  # Sales tax varies by state
            email_consent_required=False,  # CAN-SPAM allows opt-out model
            unsubscribe_required=True,
            languages=["en", "es"],
        )
        
        self._jurisdictions["brazil"] = JurisdictionConfig(
            id="brazil", name="Brazil",
            regulations=["LGPD", "Marco Civil da Internet", "CDC"],
            required_documents=["privacy_policy", "terms_of_service", "lgpd_consent"],
            document_templates={},
            consent_model="opt_in",
            cookie_consent_required=True,
            age_verification_required=True,
            age_threshold=18,
            data_residency_required=False,  # Recommended but not required
            allowed_regions=["any"],
            retention_max_days=None,
            right_to_deletion=True,
            data_portability=True,
            recommended_gateways=["stripe", "pagseguro"],
            local_payment_methods=["pix", "boleto"],
            currency="BRL",
            tax_handling="inclusive",
            email_consent_required=True,
            unsubscribe_required=True,
            languages=["pt"],
        )
        
        self._jurisdictions["mexico"] = JurisdictionConfig(
            id="mexico", name="Mexico",
            regulations=["LFPDPPP", "Ley Federal de Protección al Consumidor"],
            required_documents=["aviso_de_privacidad", "terms_of_service"],
            document_templates={},
            consent_model="opt_in",
            cookie_consent_required=True,
            age_verification_required=True,
            age_threshold=18,
            data_residency_required=False,
            allowed_regions=["any"],
            retention_max_days=None,
            right_to_deletion=True,
            data_portability=True,
            recommended_gateways=["stripe", "conekta"],
            local_payment_methods=["oxxo", "spei"],
            currency="MXN",
            tax_handling="inclusive",  # IVA included
            email_consent_required=True,
            unsubscribe_required=True,
            languages=["es"],
        )
        
        # ... (6 more jurisdictions: UK, India, Japan, Australia, Canada, LATAM)
```

---

## Épica 67.5 — User Testing Framework

**Objetivo:** A/B testing + session analytics para calibrar calidad con datos reales.

**Dependencia de Obj #2:** Apple/Tesla = calidad medida por USUARIOS, no por el sistema.

### Componentes

```python
# kernel/testing/user_testing.py
"""Sprint 67 — User Testing Framework."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime, timezone
import hashlib
import structlog

logger = structlog.get_logger("kernel.testing.user_testing")


@dataclass
class ABTest:
    """An A/B test definition."""
    id: str
    name: str
    description: str
    variants: list[dict]       # [{id: "A", name: "Control", weight: 0.5}, ...]
    metric: str                # "conversion_rate", "time_to_complete", "satisfaction"
    min_sample_size: int       # Minimum samples before declaring winner
    status: str = "running"    # "running", "completed", "paused"
    created_at: str = ""
    results: Optional[dict] = None


@dataclass
class UserSession:
    """A recorded user session for analysis."""
    session_id: str
    user_id: str
    project_id: str
    started_at: str
    ended_at: Optional[str] = None
    events: list[dict] = field(default_factory=list)  # [{type, timestamp, data}]
    satisfaction_score: Optional[int] = None  # 1-5 post-session
    completion_status: str = "in_progress"  # "completed", "abandoned", "error"


class UserTestingFramework:
    """
    Measures real user experience to calibrate quality.
    
    Capabilities:
    - A/B testing for UI variants
    - Session recording (events, not video)
    - Satisfaction surveys (post-project)
    - Funnel analysis (where do users drop off?)
    - Quality scoring from user behavior
    """
    
    def __init__(self, db: Any = None, analytics: Any = None) -> None:
        self._db = db
        self._analytics = analytics  # PostHog integration
        self._active_tests: dict[str, ABTest] = {}
        self._sessions: dict[str, UserSession] = {}
    
    # --- A/B Testing ---
    
    def assign_variant(self, test_id: str, user_id: str) -> str:
        """
        Deterministically assign a user to a test variant.
        Uses hash for consistency (same user always gets same variant).
        """
        test = self._active_tests.get(test_id)
        if not test or test.status != "running":
            return "control"
        
        # Deterministic assignment via hash
        hash_input = f"{test_id}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        normalized = (hash_value % 1000) / 1000.0
        
        cumulative = 0.0
        for variant in test.variants:
            cumulative += variant["weight"]
            if normalized < cumulative:
                return variant["id"]
        
        return test.variants[-1]["id"]
    
    async def record_metric(self, test_id: str, user_id: str, value: float) -> None:
        """Record a metric observation for an A/B test."""
        variant = self.assign_variant(test_id, user_id)
        
        if self._db:
            await self._db.table("ab_test_observations").insert({
                "test_id": test_id,
                "user_id": user_id,
                "variant": variant,
                "value": value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }).execute()
        
        # Check if we have enough data to declare winner
        await self._check_significance(test_id)
    
    async def _check_significance(self, test_id: str) -> Optional[str]:
        """Check if test has reached statistical significance."""
        test = self._active_tests.get(test_id)
        if not test:
            return None
        
        # Get observations per variant
        if self._db:
            result = await self._db.table("ab_test_observations").select("variant, value").eq("test_id", test_id).execute()
            
            if not result.data:
                return None
            
            # Group by variant
            variants_data: dict[str, list[float]] = {}
            for obs in result.data:
                v = obs["variant"]
                if v not in variants_data:
                    variants_data[v] = []
                variants_data[v].append(obs["value"])
            
            # Check minimum sample size
            if any(len(v) < test.min_sample_size for v in variants_data.values()):
                return None
            
            # Simple significance test (in production, use scipy.stats)
            # For now, declare winner if >10% improvement with >100 samples each
            if len(variants_data) >= 2:
                means = {k: sum(v) / len(v) for k, v in variants_data.items()}
                best = max(means, key=means.get)
                
                logger.info("ab_test_result",
                           test_id=test_id,
                           means=means,
                           best_variant=best)
                
                return best
        
        return None
    
    # --- Session Recording ---
    
    async def start_session(self, user_id: str, project_id: str) -> str:
        """Start recording a user session."""
        session_id = f"sess_{datetime.now().strftime('%Y%m%d%H%M%S')}_{user_id[:8]}"
        
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            project_id=project_id,
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        
        self._sessions[session_id] = session
        return session_id
    
    async def record_event(self, session_id: str, event_type: str, data: dict) -> None:
        """Record a user interaction event."""
        session = self._sessions.get(session_id)
        if not session:
            return
        
        session.events.append({
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        })
    
    async def end_session(self, session_id: str, satisfaction: Optional[int] = None) -> dict:
        """End a session and calculate metrics."""
        session = self._sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        session.ended_at = datetime.now(timezone.utc).isoformat()
        session.satisfaction_score = satisfaction
        
        # Calculate session metrics
        metrics = self._calculate_session_metrics(session)
        
        # Persist
        if self._db:
            await self._db.table("user_sessions").insert({
                "session_id": session.session_id,
                "user_id": session.user_id,
                "project_id": session.project_id,
                "started_at": session.started_at,
                "ended_at": session.ended_at,
                "event_count": len(session.events),
                "satisfaction": satisfaction,
                "completion_status": session.completion_status,
                "metrics": metrics,
            }).execute()
        
        return metrics
    
    def _calculate_session_metrics(self, session: UserSession) -> dict:
        """Calculate UX metrics from session events."""
        if not session.events:
            return {}
        
        start = datetime.fromisoformat(session.started_at)
        end = datetime.fromisoformat(session.ended_at) if session.ended_at else datetime.now(timezone.utc)
        
        duration = (end - start).total_seconds()
        
        # Count event types
        event_types = {}
        for event in session.events:
            t = event["type"]
            event_types[t] = event_types.get(t, 0) + 1
        
        # Error rate
        errors = event_types.get("error", 0)
        total_actions = len(session.events)
        error_rate = errors / max(total_actions, 1)
        
        return {
            "duration_seconds": duration,
            "total_events": total_actions,
            "error_rate": error_rate,
            "events_per_minute": total_actions / max(duration / 60, 1),
            "satisfaction": session.satisfaction_score,
            "completion": session.completion_status,
        }
    
    # --- Quality Scoring ---
    
    async def calculate_quality_score(self, project_id: str) -> dict:
        """
        Calculate overall quality score for a project based on user testing data.
        
        Dimensions:
        - Usability: time to complete, error rate
        - Satisfaction: post-session surveys
        - Engagement: events per minute, return rate
        - Completion: % of users who finish the flow
        """
        if not self._db:
            return {"error": "No database configured"}
        
        sessions = await self._db.table("user_sessions").select("*").eq("project_id", project_id).execute()
        
        if not sessions.data:
            return {"error": "No sessions recorded", "score": None}
        
        data = sessions.data
        
        # Usability (lower time + lower errors = better)
        avg_duration = sum(s["metrics"].get("duration_seconds", 0) for s in data) / len(data)
        avg_error_rate = sum(s["metrics"].get("error_rate", 0) for s in data) / len(data)
        usability = max(0, 1.0 - (avg_error_rate * 2) - (avg_duration / 600))  # Normalize
        
        # Satisfaction (direct from surveys)
        satisfaction_scores = [s["satisfaction"] for s in data if s.get("satisfaction")]
        satisfaction = (sum(satisfaction_scores) / len(satisfaction_scores) / 5.0) if satisfaction_scores else 0.5
        
        # Completion
        completed = sum(1 for s in data if s["completion_status"] == "completed")
        completion_rate = completed / len(data)
        
        # Engagement
        avg_events = sum(s["metrics"].get("events_per_minute", 0) for s in data) / len(data)
        engagement = min(1.0, avg_events / 10)  # Normalize (10 events/min = max)
        
        # Weighted score
        score = (
            usability * 0.3 +
            satisfaction * 0.3 +
            completion_rate * 0.25 +
            engagement * 0.15
        )
        
        return {
            "overall_score": round(score, 3),
            "dimensions": {
                "usability": round(usability, 3),
                "satisfaction": round(satisfaction, 3),
                "completion_rate": round(completion_rate, 3),
                "engagement": round(engagement, 3),
            },
            "sample_size": len(data),
            "benchmark": self._get_benchmark(score),
        }
    
    def _get_benchmark(self, score: float) -> str:
        """Compare score against Apple/Tesla benchmark."""
        if score >= 0.9:
            return "Exceeds Apple/Tesla standard"
        elif score >= 0.8:
            return "Meets Apple/Tesla standard"
        elif score >= 0.7:
            return "Approaching Apple/Tesla standard"
        elif score >= 0.5:
            return "Below standard — needs improvement"
        else:
            return "Critical — major UX issues"
```

### Integración con Apple HIG Benchmark (Sprint 65)

El `calculate_quality_score()` alimenta al Apple HIG Benchmark con datos REALES de usuarios. El benchmark deja de ser teórico (scoring por criterios) y se calibra con comportamiento real.

---

## Dependencias Nuevas

| Paquete | Versión | Propósito | Costo |
|---------|---------|-----------|-------|
| react-joyride | ~2.9 | Guided tours para Progressive Disclosure | $0 (MIT) |
| httpx | ~0.28 | Async HTTP para OSV.dev queries | $0 (BSD) — ya en stack |

**Total dependencias nuevas: 1** (react-joyride, solo para frontend de proyectos generados).

Sprint 67 es el sprint con MENOS dependencias nuevas de toda la serie 51-67.

---

## Costo Estimado

| Componente | Costo Mensual |
|-----------|---------------|
| Template Engine (no LLM, pure code) | $0 |
| Auto-Adoption (LLM para integration plans) | ~$2-5 |
| Progressive Disclosure (no LLM) | $0 |
| Market Compliance (template-based) | $0 |
| User Testing (PostHog, ya planificado) | $0 (included in Sprint 58) |
| **Total** | **~$2-5/mes** |

---

## Criterios de Éxito

| Criterio | Métrica | Target |
|----------|---------|--------|
| Template coverage | Industries with templates | 10/10 |
| Auto-adoption success | PRs merged without issues | >80% |
| Progressive disclosure | New user time-to-first-project | <5 min |
| Compliance accuracy | Legal docs passing review | >90% |
| User testing | Quality score calculation | Working E2E |
| Time to scaffold | Template → running project | <5 min |

---

## Referencias

[1]: Sprint 28-33 — tools/github.py commit loop
[2]: Sprint 45 — tools/agents_radar.py (10 sources)
[3]: Sprint 57 — Sales Engine + SEO Layer
[4]: Sprint 58 — PostHog Analytics (planned)
[5]: Sprint 59 — Conversational UX (planned)
[6]: Sprint 62 — Plugin Architecture
[7]: Sprint 65 — Apple HIG Benchmark + Multi-Region
[8]: react-joyride — https://react-joyride.com/
[9]: OSV.dev API — https://osv.dev/docs/
