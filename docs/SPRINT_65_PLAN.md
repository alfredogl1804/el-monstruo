# Sprint 65 — "La Experiencia Definitiva"

**Fecha:** 1 mayo 2026
**Autor:** Manus AI
**Tipo:** Sprint de Experiencia + Demostración
**Tema:** Elevar la experiencia del usuario final y demostrar inteligencia emergente con evidencia

---

## Contexto Estratégico

El promedio de los 13 Objetivos post Sprint 64 es **91.0%**. Los 4 objetivos más rezagados son Obj #13 (Del Mundo, 87%), Obj #2 (Apple/Tesla, 88%), Obj #6 (Vanguardia, 88%), y Obj #8 (Emergencia, 88%). Sprint 65 ataca directamente estos 4 gaps con un enfoque en EXPERIENCIA medible y EVIDENCIA demostrable.

**Cambio de paradigma:** Después del sprint de validación (64), Sprint 65 vuelve a construir — pero con un enfoque en lo que el USUARIO FINAL experimenta, no en la infraestructura interna.

---

## Stack Validado

| Componente | Versión | Estado | Uso en Sprint 65 |
|---|---|---|---|
| tools/github.py | Sprint 28-33 | Existente | Commit Loop para auto-integration PRs |
| ElevenLabs API | Configurado | Existente | Whisper STT + TTS para voice interface |
| Emergent Tracker | Sprint 59 | Planificado | Base para Evidence Collector |
| Quality Gate | Sprint 13 | Existente | Base para Apple HIG Benchmark |
| Transversal Layers | Sprint 57-58 | Planificado | Base para multi-region templates |

---

## Épica 65.1 — Multi-Region & Cultural UX

**Objetivo:** #13 (Del Mundo) — De 87% a 92%
**Principio:** La internacionalización real no es traducir — es ADAPTAR culturalmente.

### Tabla de Regiones Target

| Región | Moneda | Payment Gateway | Legal Framework | Date Format | Address Format |
|---|---|---|---|---|---|
| LATAM (MX, CO, AR, BR) | MXN/COP/ARS/BRL | Mercado Pago | LFPDPPP/LGPD | dd/mm/yyyy | Calle, Colonia, CP, Ciudad |
| USA/Canada | USD/CAD | Stripe | CCPA/PIPEDA | mm/dd/yyyy | Street, City, State, ZIP |
| Europe (ES, FR, DE) | EUR | Stripe EU | GDPR | dd/mm/yyyy | Street, Postal, City |
| India | INR | Razorpay | DPDP Act 2023 | dd/mm/yyyy | Street, Area, City, PIN |
| Middle East (UAE, SA) | AED/SAR | Tap Payments | PDPL | dd/mm/yyyy (RTL) | Building, Street, City |

### Implementación

```python
# kernel/transversal/global_deployment.py

from dataclasses import dataclass
from enum import Enum
from typing import Optional

class Region(Enum):
    LATAM_MX = "latam_mx"
    LATAM_BR = "latam_br"
    LATAM_CO = "latam_co"
    USA = "usa"
    EUROPE_ES = "europe_es"
    EUROPE_FR = "europe_fr"
    EUROPE_DE = "europe_de"
    INDIA = "india"
    MIDDLE_EAST_UAE = "middle_east_uae"
    MIDDLE_EAST_SA = "middle_east_sa"

@dataclass
class RegionalConfig:
    region: Region
    currency_code: str
    currency_symbol: str
    payment_gateway: str
    legal_framework: str
    date_format: str
    number_format: str  # "1,234.56" vs "1.234,56"
    address_fields: list[str]
    rtl: bool = False
    tax_included_in_price: bool = False
    privacy_banner_required: bool = False

REGIONAL_CONFIGS: dict[Region, RegionalConfig] = {
    Region.LATAM_MX: RegionalConfig(
        region=Region.LATAM_MX,
        currency_code="MXN",
        currency_symbol="$",
        payment_gateway="mercadopago",
        legal_framework="LFPDPPP",
        date_format="dd/MM/yyyy",
        number_format="1,234.56",
        address_fields=["calle", "numero", "colonia", "cp", "ciudad", "estado"],
        tax_included_in_price=True,
        privacy_banner_required=True,
    ),
    Region.USA: RegionalConfig(
        region=Region.USA,
        currency_code="USD",
        currency_symbol="$",
        payment_gateway="stripe",
        legal_framework="CCPA",
        date_format="MM/dd/yyyy",
        number_format="1,234.56",
        address_fields=["street", "apt", "city", "state", "zip"],
        privacy_banner_required=True,  # CCPA requires opt-out
    ),
    Region.EUROPE_ES: RegionalConfig(
        region=Region.EUROPE_ES,
        currency_code="EUR",
        currency_symbol="€",
        payment_gateway="stripe_eu",
        legal_framework="GDPR",
        date_format="dd/MM/yyyy",
        number_format="1.234,56",
        address_fields=["calle", "numero", "piso", "cp", "ciudad", "provincia"],
        tax_included_in_price=True,
        privacy_banner_required=True,  # GDPR strict consent
    ),
    # ... más regiones
}


class CulturalUXAdapter:
    """Adapts UX patterns to cultural expectations."""

    COLOR_PSYCHOLOGY: dict[Region, dict[str, str]] = {
        Region.LATAM_MX: {
            "trust": "#1a5276",      # Azul oscuro
            "action": "#e74c3c",     # Rojo vibrante
            "success": "#27ae60",    # Verde
            "warning": "#f39c12",    # Amarillo/naranja
            "luxury": "#8e44ad",     # Púrpura
        },
        Region.MIDDLE_EAST_UAE: {
            "trust": "#006633",      # Verde (Islam)
            "action": "#c0392b",     # Rojo oscuro
            "success": "#27ae60",    # Verde
            "warning": "#d4ac0d",    # Dorado
            "luxury": "#1a237e",     # Azul profundo
        },
        Region.INDIA: {
            "trust": "#1565c0",      # Azul
            "action": "#ff6f00",     # Naranja/azafrán
            "success": "#2e7d32",    # Verde
            "warning": "#f57f17",    # Amarillo
            "luxury": "#6a1b9a",     # Púrpura
        },
    }

    GREETING_PATTERNS: dict[Region, dict[str, str]] = {
        Region.LATAM_MX: {
            "formal": "Estimado/a {name}",
            "informal": "¡Hola {name}!",
            "business": "Buen día, {name}",
        },
        Region.USA: {
            "formal": "Dear {name}",
            "informal": "Hi {name}!",
            "business": "Hello {name}",
        },
        Region.MIDDLE_EAST_UAE: {
            "formal": "Dear Mr./Ms. {name}",
            "informal": "Hello {name}",
            "business": "Respected {name}",
        },
    }

    async def adapt_project(self, project_config: dict, target_region: Region) -> dict:
        """Adapt a project's UX to a target region."""
        regional = REGIONAL_CONFIGS[target_region]
        
        adaptations = {
            "currency": {
                "code": regional.currency_code,
                "symbol": regional.currency_symbol,
                "format": regional.number_format,
                "tax_included": regional.tax_included_in_price,
            },
            "payment": {
                "gateway": regional.payment_gateway,
                "methods": self._get_payment_methods(target_region),
            },
            "legal": {
                "framework": regional.legal_framework,
                "privacy_banner": regional.privacy_banner_required,
                "cookie_consent": regional.privacy_banner_required,
                "terms_template": f"templates/legal/{regional.legal_framework.lower()}.md",
            },
            "ux": {
                "rtl": regional.rtl,
                "date_format": regional.date_format,
                "address_fields": regional.address_fields,
                "colors": self.COLOR_PSYCHOLOGY.get(target_region, {}),
            },
        }
        return {**project_config, "regional_adaptations": adaptations}

    def _get_payment_methods(self, region: Region) -> list[str]:
        """Get available payment methods per region."""
        methods = {
            Region.LATAM_MX: ["card", "oxxo", "spei", "mercadopago_wallet"],
            Region.LATAM_BR: ["card", "pix", "boleto", "mercadopago_wallet"],
            Region.USA: ["card", "apple_pay", "google_pay", "ach"],
            Region.EUROPE_ES: ["card", "apple_pay", "google_pay", "sepa", "bizum"],
            Region.INDIA: ["card", "upi", "netbanking", "wallet"],
            Region.MIDDLE_EAST_UAE: ["card", "apple_pay", "samsung_pay", "tabby"],
        }
        return methods.get(region, ["card"])
```

### Payment Gateway Template Generator

```python
# kernel/transversal/payment_templates.py

class PaymentTemplateGenerator:
    """Generates payment integration code for target region."""

    GATEWAY_CONFIGS = {
        "mercadopago": {
            "sdk": "mercadopago",
            "env_vars": ["MERCADOPAGO_ACCESS_TOKEN", "MERCADOPAGO_PUBLIC_KEY"],
            "webhook_events": ["payment.created", "payment.updated"],
            "test_mode_flag": "sandbox",
        },
        "stripe": {
            "sdk": "stripe",
            "env_vars": ["STRIPE_SECRET_KEY", "STRIPE_PUBLISHABLE_KEY", "STRIPE_WEBHOOK_SECRET"],
            "webhook_events": ["checkout.session.completed", "payment_intent.succeeded"],
            "test_mode_flag": "test_",
        },
        "razorpay": {
            "sdk": "razorpay",
            "env_vars": ["RAZORPAY_KEY_ID", "RAZORPAY_KEY_SECRET"],
            "webhook_events": ["payment.captured", "payment.failed"],
            "test_mode_flag": "test_",
        },
    }

    async def generate_backend_template(self, gateway: str) -> str:
        """Generate FastAPI payment route template."""
        config = self.GATEWAY_CONFIGS[gateway]
        template = f'''
"""Payment integration for {gateway} — Auto-generated by El Monstruo."""
import os
from fastapi import APIRouter, Request, HTTPException
import {config["sdk"]}

router = APIRouter(prefix="/payments", tags=["payments"])

# Initialize client
{self._init_code(gateway, config)}

@router.post("/create-checkout")
async def create_checkout(request: Request):
    """Create a checkout session."""
    body = await request.json()
    {self._checkout_code(gateway)}

@router.post("/webhook")
async def payment_webhook(request: Request):
    """Handle payment webhook."""
    {self._webhook_code(gateway, config)}
'''
        return template

    def _init_code(self, gateway: str, config: dict) -> str:
        if gateway == "mercadopago":
            return 'sdk = mercadopago.SDK(os.environ["MERCADOPAGO_ACCESS_TOKEN"])'
        elif gateway == "stripe":
            return 'stripe.api_key = os.environ["STRIPE_SECRET_KEY"]'
        elif gateway == "razorpay":
            return 'client = razorpay.Client(auth=(os.environ["RAZORPAY_KEY_ID"], os.environ["RAZORPAY_KEY_SECRET"]))'
        return ""

    def _checkout_code(self, gateway: str) -> str:
        # Returns gateway-specific checkout creation code
        return f"# {gateway}-specific checkout logic"

    def _webhook_code(self, gateway: str, config: dict) -> str:
        return f"# Verify {gateway} webhook signature and process event"
```

### Archivos Creados

| Archivo | Propósito |
|---|---|
| `kernel/transversal/global_deployment.py` | Regional configs + Cultural UX Adapter |
| `kernel/transversal/payment_templates.py` | Payment gateway code generator |
| `templates/legal/gdpr.md` | GDPR privacy policy template |
| `templates/legal/ccpa.md` | CCPA privacy policy template |
| `templates/legal/lfpdppp.md` | Mexico privacy policy template |
| `templates/legal/lgpd.md` | Brazil privacy policy template |

---

## Épica 65.2 — Apple Design Benchmark

**Objetivo:** #2 (Nivel Apple/Tesla) — De 88% a 92%
**Principio:** "Si no puedes medirlo, no puedes mejorarlo." — Benchmark cuantitativo contra Apple HIG.

### Apple HIG Scoring Criteria (60 puntos)

```python
# kernel/quality/apple_hig_benchmark.py

from dataclasses import dataclass
from typing import Optional
import structlog

logger = structlog.get_logger()


@dataclass
class HIGScore:
    category: str
    criterion: str
    score: float  # 0.0 - 1.0
    weight: float  # Importance multiplier
    evidence: str
    recommendation: Optional[str] = None


class AppleHIGBenchmark:
    """
    Quantitative design audit against Apple Human Interface Guidelines.
    60 criteria across 6 categories. Each scored 0-1 with weight.
    Final score: weighted average normalized to 100.
    """

    CATEGORIES = {
        "typography": {
            "weight": 0.20,
            "criteria": [
                ("hierarchy_clear", "Clear visual hierarchy with 3-4 levels max"),
                ("font_consistency", "Max 2 font families used consistently"),
                ("size_scale", "Modular scale (1.2-1.5 ratio) between sizes"),
                ("line_height", "Line height 1.4-1.6 for body text"),
                ("letter_spacing", "Appropriate tracking for each size"),
                ("contrast_ratio", "WCAG AAA (7:1) for body text"),
                ("weight_variation", "Strategic use of 2-3 weights"),
                ("alignment", "Consistent text alignment per context"),
                ("truncation", "Proper ellipsis/truncation for overflow"),
                ("responsive_scaling", "Fluid typography across breakpoints"),
            ],
        },
        "spacing_layout": {
            "weight": 0.20,
            "criteria": [
                ("grid_system", "Consistent grid (4px/8px base unit)"),
                ("whitespace_ratio", "Min 40% whitespace on any screen"),
                ("element_breathing", "Adequate padding around interactive elements"),
                ("alignment_grid", "All elements snap to alignment grid"),
                ("section_rhythm", "Consistent vertical rhythm between sections"),
                ("responsive_breakpoints", "Smooth transitions at breakpoints"),
                ("touch_targets", "Min 44x44px for interactive elements"),
                ("content_density", "Appropriate density for context"),
                ("margin_consistency", "Consistent margins throughout"),
                ("visual_balance", "Balanced weight distribution"),
            ],
        },
        "color_harmony": {
            "weight": 0.15,
            "criteria": [
                ("palette_size", "5-7 colors max in primary palette"),
                ("contrast_accessibility", "All color pairs meet WCAG AA"),
                ("semantic_consistency", "Colors have consistent meaning"),
                ("saturation_harmony", "Consistent saturation levels"),
                ("dark_mode_support", "Proper dark mode with adjusted palette"),
                ("accent_restraint", "Accent color used sparingly (<10% area)"),
                ("neutral_foundation", "Strong neutral palette for structure"),
                ("gradient_subtlety", "Gradients subtle, max 2 stops"),
                ("state_colors", "Clear hover/active/disabled states"),
                ("brand_integration", "Brand colors integrated naturally"),
            ],
        },
        "motion_interaction": {
            "weight": 0.15,
            "criteria": [
                ("duration_appropriate", "Animations 200-500ms (not too fast/slow)"),
                ("easing_natural", "Natural easing curves (no linear)"),
                ("purpose_clear", "Every animation has clear purpose"),
                ("interruptible", "Animations can be interrupted"),
                ("reduced_motion", "Respects prefers-reduced-motion"),
                ("feedback_immediate", "Immediate feedback on interaction"),
                ("loading_states", "Skeleton/shimmer for async content"),
                ("transition_smooth", "Smooth page/view transitions"),
                ("micro_interactions", "Subtle micro-interactions on key actions"),
                ("scroll_behavior", "Smooth, predictable scroll behavior"),
            ],
        },
        "content_clarity": {
            "weight": 0.15,
            "criteria": [
                ("copy_concise", "UI copy is concise and actionable"),
                ("labels_clear", "All labels are unambiguous"),
                ("error_helpful", "Error messages explain AND suggest fix"),
                ("empty_states", "Meaningful empty states with CTA"),
                ("onboarding_progressive", "Progressive disclosure of complexity"),
                ("icons_recognizable", "Icons are universally recognizable"),
                ("imagery_purposeful", "Images serve clear purpose"),
                ("hierarchy_scannable", "Content scannable in 3 seconds"),
                ("cta_obvious", "Primary CTA immediately visible"),
                ("navigation_predictable", "Navigation is predictable"),
            ],
        },
        "technical_quality": {
            "weight": 0.15,
            "criteria": [
                ("lcp_fast", "LCP < 2.5s"),
                ("cls_stable", "CLS < 0.1"),
                ("fid_responsive", "FID < 100ms"),
                ("bundle_optimized", "JS bundle < 200KB gzipped"),
                ("images_optimized", "Images in WebP/AVIF, properly sized"),
                ("accessibility_score", "Lighthouse accessibility > 95"),
                ("keyboard_navigable", "Full keyboard navigation"),
                ("screen_reader", "Proper ARIA labels and roles"),
                ("focus_visible", "Visible focus indicators"),
                ("semantic_html", "Semantic HTML structure"),
            ],
        },
    }

    def __init__(self, llm_client):
        self.llm = llm_client

    async def audit(self, project_url: str, screenshots: list[str]) -> dict:
        """
        Run full Apple HIG audit on a project.
        Uses LLM multimodal for visual criteria + Lighthouse for technical.
        """
        scores: list[HIGScore] = []

        # Visual audit (LLM multimodal)
        visual_scores = await self._audit_visual(screenshots)
        scores.extend(visual_scores)

        # Technical audit (Lighthouse)
        tech_scores = await self._audit_technical(project_url)
        scores.extend(tech_scores)

        # Calculate final score
        category_scores = {}
        for cat_name, cat_config in self.CATEGORIES.items():
            cat_criteria = [s for s in scores if s.category == cat_name]
            if cat_criteria:
                avg = sum(s.score * s.weight for s in cat_criteria) / sum(s.weight for s in cat_criteria)
                category_scores[cat_name] = avg

        final_score = sum(
            category_scores.get(cat, 0) * config["weight"]
            for cat, config in self.CATEGORIES.items()
        ) / sum(config["weight"] for config in self.CATEGORIES.values())

        return {
            "final_score": round(final_score * 100, 1),
            "grade": self._score_to_grade(final_score),
            "category_scores": {k: round(v * 100, 1) for k, v in category_scores.items()},
            "details": scores,
            "top_improvements": self._get_top_improvements(scores, n=5),
        }

    def _score_to_grade(self, score: float) -> str:
        if score >= 0.95:
            return "S"  # Apple-tier
        elif score >= 0.90:
            return "A"
        elif score >= 0.80:
            return "B"
        elif score >= 0.70:
            return "C"
        else:
            return "D"

    def _get_top_improvements(self, scores: list[HIGScore], n: int = 5) -> list[dict]:
        """Get top N improvements sorted by impact (low score * high weight)."""
        impact_scores = [
            {
                "criterion": s.criterion,
                "category": s.category,
                "current_score": s.score,
                "impact": (1 - s.score) * s.weight,
                "recommendation": s.recommendation,
            }
            for s in scores
            if s.score < 0.9
        ]
        return sorted(impact_scores, key=lambda x: x["impact"], reverse=True)[:n]

    async def _audit_visual(self, screenshots: list[str]) -> list[HIGScore]:
        """Use LLM multimodal to score visual criteria."""
        visual_categories = ["typography", "spacing_layout", "color_harmony", 
                           "motion_interaction", "content_clarity"]
        scores = []
        
        for cat in visual_categories:
            criteria = self.CATEGORIES[cat]["criteria"]
            prompt = self._build_visual_audit_prompt(cat, criteria, screenshots)
            
            response = await self.llm.analyze_images(
                images=screenshots,
                prompt=prompt,
                response_format="json",
            )
            
            for criterion_id, criterion_desc in criteria:
                criterion_result = response.get(criterion_id, {})
                scores.append(HIGScore(
                    category=cat,
                    criterion=criterion_desc,
                    score=criterion_result.get("score", 0.5),
                    weight=1.0,
                    evidence=criterion_result.get("evidence", ""),
                    recommendation=criterion_result.get("recommendation"),
                ))
        
        return scores

    async def _audit_technical(self, project_url: str) -> list[HIGScore]:
        """Run Lighthouse and map to HIG technical criteria."""
        # Integration with Lighthouse CLI or API
        # Maps Core Web Vitals to HIG scores
        scores = []
        criteria = self.CATEGORIES["technical_quality"]["criteria"]
        
        for criterion_id, criterion_desc in criteria:
            # Each criterion mapped to specific Lighthouse metric
            scores.append(HIGScore(
                category="technical_quality",
                criterion=criterion_desc,
                score=0.5,  # Placeholder — filled by Lighthouse
                weight=1.0,
                evidence="Pending Lighthouse audit",
            ))
        
        return scores

    def _build_visual_audit_prompt(self, category: str, criteria: list, screenshots: list) -> str:
        criteria_text = "\n".join(f"- {cid}: {desc}" for cid, desc in criteria)
        return f"""You are an expert UI/UX designer trained in Apple Human Interface Guidelines.
Analyze the provided screenshots and score each criterion from 0.0 to 1.0.

Category: {category}
Criteria to evaluate:
{criteria_text}

For each criterion, provide:
- score: float 0.0-1.0 (0.95+ = Apple-tier, 0.8+ = professional, <0.7 = needs work)
- evidence: specific observation from the screenshot
- recommendation: actionable improvement (only if score < 0.9)

Return JSON with criterion_id as keys."""
```

---

## Épica 65.3 — Emergence Evidence Collector

**Objetivo:** #8 (Inteligencia Emergente) — De 88% a 93%
**Principio:** La emergencia DEBE ser demostrable con evidencia reproducible.

### Los 4 Criterios Estrictos de Emergencia

```python
# kernel/intelligence/emergence_evidence.py

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import structlog

logger = structlog.get_logger()


class EmergenceCriterion(Enum):
    UNEXPECTED = "unexpected"        # Not explicitly programmed
    BENEFICIAL = "beneficial"        # Produces positive outcome
    REPRODUCIBLE = "reproducible"    # Can be triggered again
    NOVEL = "novel"                  # Not a simple recombination


@dataclass
class EmergenceEvidence:
    id: str
    title: str
    description: str
    criteria_met: dict[EmergenceCriterion, bool]
    evidence_artifacts: list[str]  # File paths to logs, screenshots, etc.
    trigger_conditions: dict       # What caused this behavior
    observed_at: datetime
    observer: str                  # Which system detected it
    confidence: float              # 0.0-1.0
    anti_gaming_check: bool = False  # Passed anti-gaming validation
    human_verified: bool = False


class EmergenceEvidenceCollector:
    """
    Collects, validates, and publishes evidence of emergent behavior.
    
    Anti-gaming measures:
    1. Behavior must NOT be traceable to a single instruction
    2. Must occur across multiple contexts (not one-off)
    3. Must not be a direct result of scheduler assignment
    4. Human verification required for publication
    """

    MINIMUM_CONFIDENCE = 0.7
    MINIMUM_CRITERIA_MET = 3  # At least 3 of 4 criteria

    def __init__(self, supabase_client, llm_client):
        self.supabase = supabase_client
        self.llm = llm_client
        self.pending_evidence: list[EmergenceEvidence] = []

    async def detect_candidate(self, event: dict) -> Optional[EmergenceEvidence]:
        """
        Analyze an event for potential emergent behavior.
        Called by Embrion Loop when unexpected outcomes occur.
        """
        # Step 1: Check if behavior was explicitly programmed
        is_unexpected = await self._check_unexpected(event)
        if not is_unexpected:
            return None

        # Step 2: Check if outcome is beneficial
        is_beneficial = await self._check_beneficial(event)

        # Step 3: Check reproducibility (has it happened before?)
        is_reproducible = await self._check_reproducible(event)

        # Step 4: Check novelty (not simple recombination)
        is_novel = await self._check_novel(event)

        criteria = {
            EmergenceCriterion.UNEXPECTED: is_unexpected,
            EmergenceCriterion.BENEFICIAL: is_beneficial,
            EmergenceCriterion.REPRODUCIBLE: is_reproducible,
            EmergenceCriterion.NOVEL: is_novel,
        }

        criteria_count = sum(1 for v in criteria.values() if v)
        if criteria_count < self.MINIMUM_CRITERIA_MET:
            logger.debug("emergence_candidate_rejected", 
                        criteria_met=criteria_count, event=event.get("type"))
            return None

        # Step 5: Anti-gaming check
        passed_anti_gaming = await self._anti_gaming_check(event)

        evidence = EmergenceEvidence(
            id=f"EMG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            title=event.get("title", "Untitled emergence"),
            description=await self._generate_description(event, criteria),
            criteria_met=criteria,
            evidence_artifacts=event.get("artifacts", []),
            trigger_conditions=event.get("context", {}),
            observed_at=datetime.now(),
            observer=event.get("observer", "system"),
            confidence=criteria_count / 4.0,
            anti_gaming_check=passed_anti_gaming,
        )

        if passed_anti_gaming and evidence.confidence >= self.MINIMUM_CONFIDENCE:
            await self._store_evidence(evidence)
            self.pending_evidence.append(evidence)
            logger.info("emergence_candidate_stored", id=evidence.id, 
                       confidence=evidence.confidence)

        return evidence

    async def _check_unexpected(self, event: dict) -> bool:
        """Verify behavior is not traceable to a single instruction."""
        prompt = f"""Analyze this system event and determine if the behavior 
was EXPLICITLY programmed or if it emerged from the interaction of multiple 
components without direct instruction.

Event: {event}

Respond with:
- is_unexpected: true/false
- reasoning: why you believe this was/wasn't programmed
- traced_to_instruction: the specific code/instruction if found, or "none"
"""
        response = await self.llm.analyze(prompt, response_format="json")
        return response.get("is_unexpected", False)

    async def _check_beneficial(self, event: dict) -> bool:
        """Verify outcome is positive (not random/harmful)."""
        outcome = event.get("outcome", {})
        # Check quality score, user satisfaction, or efficiency gain
        if outcome.get("quality_score", 0) > 0.8:
            return True
        if outcome.get("efficiency_gain", 0) > 0.2:
            return True
        if outcome.get("user_satisfaction", 0) > 0.8:
            return True
        return False

    async def _check_reproducible(self, event: dict) -> bool:
        """Check if similar behavior has occurred before."""
        similar = await self.supabase.table("emergence_candidates")\
            .select("*")\
            .textSearch("description", event.get("type", ""))\
            .limit(5)\
            .execute()
        return len(similar.data or []) >= 2  # At least 2 prior occurrences

    async def _check_novel(self, event: dict) -> bool:
        """Verify this isn't a simple recombination of known patterns."""
        prompt = f"""Is this behavior a NOVEL capability, or simply a 
recombination of explicitly programmed features?

Novel = the system does something its individual components were not 
designed to do when combined.

Not novel = the system does exactly what component A + component B 
were designed to do together.

Event: {event}

Respond: is_novel (true/false) and reasoning."""
        response = await self.llm.analyze(prompt, response_format="json")
        return response.get("is_novel", False)

    async def _anti_gaming_check(self, event: dict) -> bool:
        """
        Prevent false positives from:
        1. Scheduler-assigned tasks (not spontaneous)
        2. Direct user commands (not autonomous)
        3. Template-following (not creative)
        """
        # Check 1: Was this triggered by scheduler?
        if event.get("trigger") == "scheduler":
            return False
        
        # Check 2: Was this a direct user command?
        if event.get("trigger") == "user_command":
            return False
        
        # Check 3: Does it follow a known template exactly?
        if event.get("template_match_score", 0) > 0.95:
            return False
        
        return True

    async def generate_emergence_report(self) -> dict:
        """Generate publish-ready emergence report."""
        verified = await self.supabase.table("emergence_evidence")\
            .select("*")\
            .eq("human_verified", True)\
            .order("observed_at", desc=True)\
            .execute()

        if not verified.data:
            return {"status": "no_verified_emergence", "evidence_count": 0}

        return {
            "status": "emergence_demonstrated",
            "evidence_count": len(verified.data),
            "strongest_cases": verified.data[:5],
            "criteria_distribution": self._criteria_distribution(verified.data),
            "timeline": self._build_timeline(verified.data),
            "publication_ready": len(verified.data) >= 3,
        }

    def _criteria_distribution(self, evidence_list: list) -> dict:
        dist = {c.value: 0 for c in EmergenceCriterion}
        for e in evidence_list:
            for criterion, met in e.get("criteria_met", {}).items():
                if met:
                    dist[criterion] = dist.get(criterion, 0) + 1
        return dist

    def _build_timeline(self, evidence_list: list) -> list:
        return [
            {"date": e["observed_at"], "title": e["title"], "confidence": e["confidence"]}
            for e in sorted(evidence_list, key=lambda x: x["observed_at"])
        ]

    async def _store_evidence(self, evidence: EmergenceEvidence) -> None:
        await self.supabase.table("emergence_evidence").insert({
            "id": evidence.id,
            "title": evidence.title,
            "description": evidence.description,
            "criteria_met": {k.value: v for k, v in evidence.criteria_met.items()},
            "evidence_artifacts": evidence.evidence_artifacts,
            "trigger_conditions": evidence.trigger_conditions,
            "observed_at": evidence.observed_at.isoformat(),
            "observer": evidence.observer,
            "confidence": evidence.confidence,
            "anti_gaming_check": evidence.anti_gaming_check,
            "human_verified": False,
        }).execute()

    async def _generate_description(self, event: dict, criteria: dict) -> str:
        met_criteria = [k.value for k, v in criteria.items() if v]
        prompt = f"""Write a concise, scientific description of this emergent behavior.
Include: what happened, why it's unexpected, and what criteria it meets.
Event: {event}
Criteria met: {met_criteria}"""
        response = await self.llm.generate(prompt)
        return response
```

### Tabla SQL

```sql
CREATE TABLE emergence_evidence (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    criteria_met JSONB NOT NULL,
    evidence_artifacts TEXT[] DEFAULT '{}',
    trigger_conditions JSONB DEFAULT '{}',
    observed_at TIMESTAMPTZ NOT NULL,
    observer TEXT NOT NULL,
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    anti_gaming_check BOOLEAN DEFAULT FALSE,
    human_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_emergence_confidence ON emergence_evidence(confidence DESC);
CREATE INDEX idx_emergence_verified ON emergence_evidence(human_verified);
```

---

## Épica 65.4 — Auto-Integration Executor

**Objetivo:** #6 (Vanguardia Perpetua) — De 88% a 92%
**Principio:** No solo proponer — EJECUTAR integraciones automáticamente via PR.

### Implementación

```python
# kernel/vanguard/auto_integrator.py

from dataclasses import dataclass
from typing import Optional
import structlog

logger = structlog.get_logger()


@dataclass
class IntegrationProposal:
    id: str
    tool_name: str
    tool_version: str
    category: str  # "dependency", "api", "pattern"
    rationale: str
    impact_score: float  # 0-1
    risk_level: str  # "low", "medium", "high"
    files_to_modify: list[str]
    files_to_create: list[str]
    test_plan: str


class AutoIntegrationExecutor:
    """
    Converts Research Intelligence proposals into actual PRs.
    Uses existing tools/github.py commit loop.
    
    Flow:
    1. Receive proposal from Research Intelligence Engine (Sprint 63)
    2. Generate implementation code
    3. Generate tests
    4. Create branch + commit + PR via tools/github.py
    5. Run tests in CI
    6. Auto-rollback if tests fail
    """

    MAX_DAILY_PRS = 3  # Budget guard
    ALLOWED_RISK_LEVELS = ["low", "medium"]  # High risk requires human approval

    def __init__(self, github_tool, llm_client, supabase_client):
        self.github = github_tool
        self.llm = llm_client
        self.supabase = supabase_client
        self._daily_pr_count = 0

    async def execute_proposal(self, proposal: IntegrationProposal) -> dict:
        """Execute an integration proposal as a PR."""
        
        # Guard: daily limit
        if self._daily_pr_count >= self.MAX_DAILY_PRS:
            logger.warning("auto_integration_daily_limit", count=self._daily_pr_count)
            return {"status": "rate_limited", "reason": "Daily PR limit reached"}

        # Guard: risk level
        if proposal.risk_level not in self.ALLOWED_RISK_LEVELS:
            logger.info("auto_integration_high_risk", tool=proposal.tool_name)
            return {"status": "needs_human_approval", "proposal": proposal}

        # Step 1: Generate implementation
        implementation = await self._generate_implementation(proposal)
        if not implementation:
            return {"status": "generation_failed"}

        # Step 2: Generate tests
        tests = await self._generate_tests(proposal, implementation)

        # Step 3: Create branch
        branch_name = f"auto-integrate/{proposal.tool_name}-{proposal.tool_version}"
        await self.github.create_branch(branch_name)

        # Step 4: Commit files
        for file_path, content in implementation.items():
            await self.github.create_or_update_file(
                path=file_path,
                content=content,
                message=f"feat: integrate {proposal.tool_name} v{proposal.tool_version}",
                branch=branch_name,
            )

        # Step 5: Commit tests
        for test_path, test_content in tests.items():
            await self.github.create_or_update_file(
                path=test_path,
                content=test_content,
                message=f"test: add tests for {proposal.tool_name}",
                branch=branch_name,
            )

        # Step 6: Update requirements.txt
        await self._update_requirements(proposal, branch_name)

        # Step 7: Create PR
        pr_result = await self.github.create_pull_request(
            title=f"[Auto-Integration] {proposal.tool_name} v{proposal.tool_version}",
            body=self._build_pr_body(proposal),
            head=branch_name,
            base="main",
        )

        self._daily_pr_count += 1

        # Log execution
        await self._log_execution(proposal, pr_result)

        return {
            "status": "pr_created",
            "pr_url": pr_result.get("html_url"),
            "branch": branch_name,
            "files_modified": list(implementation.keys()) + list(tests.keys()),
        }

    async def _generate_implementation(self, proposal: IntegrationProposal) -> Optional[dict]:
        """Generate implementation code for the proposal."""
        prompt = f"""Generate production-ready Python code to integrate {proposal.tool_name} v{proposal.tool_version}.

Context:
- Project: El Monstruo (FastAPI + Supabase + multi-LLM)
- Category: {proposal.category}
- Rationale: {proposal.rationale}
- Files to modify: {proposal.files_to_modify}
- Files to create: {proposal.files_to_create}

Requirements:
1. Follow existing code patterns (structlog, async/await, type hints)
2. Include proper error handling with fallbacks
3. Add docstrings with sprint reference
4. Use environment variables for secrets
5. Keep backward compatibility

Return a JSON dict with file_path: file_content pairs."""

        response = await self.llm.generate(prompt, response_format="json")
        return response if isinstance(response, dict) else None

    async def _generate_tests(self, proposal: IntegrationProposal, implementation: dict) -> dict:
        """Generate test code for the implementation."""
        prompt = f"""Generate pytest tests for this integration:
Tool: {proposal.tool_name}
Test plan: {proposal.test_plan}
Implementation files: {list(implementation.keys())}

Requirements:
1. Test happy path + error cases
2. Mock external services
3. Use pytest-asyncio for async tests
4. Follow existing test patterns

Return JSON dict with test_file_path: test_content pairs."""

        response = await self.llm.generate(prompt, response_format="json")
        return response if isinstance(response, dict) else {}

    async def _update_requirements(self, proposal: IntegrationProposal, branch: str) -> None:
        """Add new dependency to requirements.txt."""
        if proposal.category == "dependency":
            # Read current requirements
            current = await self.github.get_file_contents("requirements.txt")
            new_req = f"{proposal.tool_name}>={proposal.tool_version}"
            if new_req not in current:
                updated = current + f"\n{new_req}\n"
                await self.github.create_or_update_file(
                    path="requirements.txt",
                    content=updated,
                    message=f"deps: add {proposal.tool_name}",
                    branch=branch,
                )

    def _build_pr_body(self, proposal: IntegrationProposal) -> str:
        return f"""## Auto-Integration: {proposal.tool_name} v{proposal.tool_version}

**Category:** {proposal.category}
**Risk Level:** {proposal.risk_level}
**Impact Score:** {proposal.impact_score:.2f}

### Rationale
{proposal.rationale}

### Changes
- Files modified: {', '.join(proposal.files_to_modify)}
- Files created: {', '.join(proposal.files_to_create)}

### Test Plan
{proposal.test_plan}

---
*This PR was auto-generated by El Monstruo's Auto-Integration Executor.*
*Human review by Alfredo is the HITL gate.*
"""

    async def _log_execution(self, proposal: IntegrationProposal, pr_result: dict) -> None:
        await self.supabase.table("auto_integration_log").insert({
            "proposal_id": proposal.id,
            "tool_name": proposal.tool_name,
            "tool_version": proposal.tool_version,
            "pr_url": pr_result.get("html_url", ""),
            "status": "pr_created",
            "risk_level": proposal.risk_level,
        }).execute()
```

---

## Épica 65.5 — Voice & Natural Language Interface

**Objetivo:** #3 (Mínima Complejidad) — De 89% a 93%
**Principio:** La interfaz más simple posible: HABLAR. Una frase = un negocio.

### Implementación

```python
# kernel/interface/voice_interface.py

from dataclasses import dataclass
from typing import Optional
import os
import structlog
from elevenlabs import ElevenLabs

logger = structlog.get_logger()


@dataclass
class VoiceCommand:
    text: str
    intent: str
    confidence: float
    language: str
    requires_confirmation: bool
    parameters: dict


class VoiceInterface:
    """
    Voice-first interface for El Monstruo.
    Uses ElevenLabs for STT + TTS.
    
    Flow:
    1. User speaks → ElevenLabs Whisper transcribes
    2. Text → Intent Parser (from Sprint 59 Conversational UX)
    3. If critical action → TTS confirmation request
    4. Execute action
    5. TTS response with result summary
    """

    CRITICAL_ACTIONS = ["deploy", "delete", "payment", "publish"]
    SUPPORTED_LANGUAGES = ["es", "en", "pt", "fr", "de"]

    def __init__(self, llm_client, intent_parser):
        self.llm = llm_client
        self.intent_parser = intent_parser
        self.eleven = ElevenLabs(api_key=os.environ.get("ELEVENLABS_API_KEY"))
        self.conversation_memory: list[dict] = []

    async def process_audio(self, audio_bytes: bytes, format: str = "wav") -> dict:
        """Process audio input and return action result."""
        
        # Step 1: Transcribe
        transcription = await self._transcribe(audio_bytes, format)
        if not transcription:
            return {"status": "transcription_failed", "response_audio": await self._speak("No pude entender. ¿Puedes repetir?")}

        logger.info("voice_transcribed", text=transcription["text"], lang=transcription["language"])

        # Step 2: Add to conversation memory
        self.conversation_memory.append({
            "role": "user",
            "content": transcription["text"],
            "timestamp": "now",
        })

        # Step 3: Parse intent (with conversation context)
        command = await self._parse_intent(transcription["text"], transcription["language"])

        # Step 4: Check if confirmation needed
        if command.requires_confirmation:
            confirmation_text = await self._generate_confirmation(command)
            return {
                "status": "awaiting_confirmation",
                "command": command,
                "response_audio": await self._speak(confirmation_text, transcription["language"]),
                "response_text": confirmation_text,
            }

        # Step 5: Execute
        result = await self._execute_command(command)

        # Step 6: Generate response
        response_text = await self._generate_response(command, result)
        self.conversation_memory.append({
            "role": "assistant",
            "content": response_text,
        })

        return {
            "status": "executed",
            "command": command,
            "result": result,
            "response_audio": await self._speak(response_text, transcription["language"]),
            "response_text": response_text,
        }

    async def _transcribe(self, audio_bytes: bytes, format: str) -> Optional[dict]:
        """Transcribe audio using ElevenLabs."""
        try:
            # Save temp file for API
            temp_path = f"/tmp/voice_input.{format}"
            with open(temp_path, "wb") as f:
                f.write(audio_bytes)

            result = self.eleven.speech_to_text.convert(
                file=open(temp_path, "rb"),
                model_id="scribe_v1",
                language_code="auto",  # Auto-detect
            )

            return {
                "text": result.text,
                "language": result.language_code or "es",
                "confidence": result.confidence or 0.9,
            }
        except Exception as e:
            logger.error("voice_transcription_failed", error=str(e))
            return None

    async def _parse_intent(self, text: str, language: str) -> VoiceCommand:
        """Parse intent from transcribed text with conversation context."""
        context = self.conversation_memory[-5:]  # Last 5 turns
        
        parsed = await self.intent_parser.parse(
            text=text,
            language=language,
            context=context,
        )

        requires_confirmation = parsed.get("action") in self.CRITICAL_ACTIONS

        return VoiceCommand(
            text=text,
            intent=parsed.get("intent", "unknown"),
            confidence=parsed.get("confidence", 0.5),
            language=language,
            requires_confirmation=requires_confirmation,
            parameters=parsed.get("parameters", {}),
        )

    async def _speak(self, text: str, language: str = "es") -> bytes:
        """Convert text to speech using ElevenLabs."""
        try:
            voice_map = {
                "es": "pFZP5JQG7iQjIQuC4Bku",  # Spanish voice
                "en": "21m00Tcm4TlvDq8ikWAM",  # English voice
                "pt": "ErXwobaYiN019PkySvjV",  # Portuguese voice
            }
            voice_id = voice_map.get(language, voice_map["es"])

            audio = self.eleven.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )

            # Collect audio bytes
            audio_bytes = b""
            for chunk in audio:
                audio_bytes += chunk
            return audio_bytes
        except Exception as e:
            logger.error("voice_tts_failed", error=str(e))
            return b""

    async def _generate_confirmation(self, command: VoiceCommand) -> str:
        """Generate confirmation message for critical actions."""
        confirmations = {
            "deploy": f"Voy a desplegar el proyecto. ¿Confirmas?",
            "delete": f"Voy a eliminar {command.parameters.get('target', 'esto')}. ¿Estás seguro?",
            "payment": f"Voy a procesar un pago de {command.parameters.get('amount', '?')}. ¿Confirmas?",
            "publish": f"Voy a publicar {command.parameters.get('target', 'el proyecto')}. ¿Confirmas?",
        }
        return confirmations.get(command.intent, "¿Confirmas esta acción?")

    async def _execute_command(self, command: VoiceCommand) -> dict:
        """Execute the parsed command."""
        # Delegates to the appropriate kernel handler
        # This integrates with the existing command infrastructure
        return {"status": "executed", "intent": command.intent}

    async def _generate_response(self, command: VoiceCommand, result: dict) -> str:
        """Generate natural language response."""
        prompt = f"""Generate a concise, natural spoken response (max 2 sentences) in {command.language}.
Command: {command.intent}
Parameters: {command.parameters}
Result: {result}
Tone: Professional but friendly. Like a competent assistant."""
        
        response = await self.llm.generate(prompt)
        return response
```

### API Endpoint

```python
# En main.py (FastAPI)

@app.post("/api/voice")
async def voice_input(request: Request):
    """Process voice input."""
    audio_data = await request.body()
    content_type = request.headers.get("content-type", "audio/wav")
    format = "wav" if "wav" in content_type else "mp3"
    
    result = await voice_interface.process_audio(audio_data, format)
    return result

@app.post("/api/voice/confirm")
async def voice_confirm(request: Request):
    """Confirm a pending voice command."""
    body = await request.json()
    confirmed = body.get("confirmed", False)
    command_id = body.get("command_id")
    
    if confirmed:
        result = await voice_interface._execute_command(pending_commands[command_id])
        return {"status": "executed", "result": result}
    return {"status": "cancelled"}
```

---

## Archivos Totales del Sprint

| Archivo | Épica | Propósito |
|---|---|---|
| `kernel/transversal/global_deployment.py` | 65.1 | Regional configs + Cultural UX |
| `kernel/transversal/payment_templates.py` | 65.1 | Payment gateway code generator |
| `templates/legal/gdpr.md` | 65.1 | GDPR template |
| `templates/legal/ccpa.md` | 65.1 | CCPA template |
| `templates/legal/lfpdppp.md` | 65.1 | Mexico template |
| `templates/legal/lgpd.md` | 65.1 | Brazil template |
| `kernel/quality/apple_hig_benchmark.py` | 65.2 | 60-criteria design audit |
| `kernel/intelligence/emergence_evidence.py` | 65.3 | Evidence collector + anti-gaming |
| `kernel/vanguard/auto_integrator.py` | 65.4 | Proposal → PR executor |
| `kernel/interface/voice_interface.py` | 65.5 | Voice-first interface |

---

## Dependencias Nuevas

```txt
# requirements.txt additions
elevenlabs>=1.50.0        # Already configured, ensure version
mercadopago>=2.2.0        # LATAM payments template reference
```

---

## Costo Estimado

| Componente | Costo Mensual |
|---|---|
| ElevenLabs (STT + TTS) | $5-22/mes (depende de uso) |
| LLM calls (visual audit) | $2-5/mes |
| Supabase (emergence table) | $0 (within free tier) |
| **Total adicional** | **$7-27/mes** |

---

## Criterios de Éxito

| Métrica | Target |
|---|---|
| Regiones soportadas | 10+ con configs completas |
| Apple HIG score en proyecto demo | >80/100 |
| Emergence evidence collected | ≥1 verified case |
| Auto-integration PRs/week | 2-3 (low risk) |
| Voice command success rate | >85% |
| Voice response latency | <3 seconds |

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| ElevenLabs latency >3s | Media | Alto | Streaming response + cache frequent phrases |
| Auto-PR breaks CI | Media | Medio | Mandatory test generation + auto-rollback |
| False positive emergence | Alta | Bajo | 4 strict criteria + anti-gaming + human verification |
| Payment template security gaps | Baja | Alto | Never store real credentials in templates |
| LLM visual audit inconsistency | Media | Medio | Run 3x and average scores |
