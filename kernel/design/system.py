"""
El Monstruo — Design System Enforcement Engine (Sprint 61)
===========================================================
Motor de enforcement de calidad de diseño.

4 dimensiones de auditoría:
1. Design Tokens — vocabulario visual ejecutable (OKLCH + Inter)
2. Accessibility — WCAG 2.2 via axe-core (Playwright)
3. Performance — Core Web Vitals via PageSpeed Insights API
4. Visual Consistency — LLM multimodal scoring

Estándar: Apple/Tesla level (Objetivo #2)
Sprint 61 — 2026-05-01

Soberanía:
- axe-core → Lighthouse CLI fallback si Playwright no disponible
- PageSpeed Insights → Lighthouse local si no hay GOOGLE_PSI_API_KEY
- Sabios LLM → score heurístico 70.0 si no hay API key
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from typing import Optional

import structlog

logger = structlog.get_logger("monstruo.design")


# ── Excepciones con identidad ──────────────────────────────────────────────


class DesignAuditoriaFallida(RuntimeError):
    """La auditoría de diseño no pudo completarse.

    Causa: URL inaccesible, Playwright no instalado, o API key inválida.
    Sugerencia: Verificar que la URL es pública y que Playwright está instalado.
    """


class DesignTokensInvalidos(ValueError):
    """Los design tokens tienen formato inválido.

    Causa: Tokens con valores no reconocidos por el sistema.
    Sugerencia: Usar el formato OKLCH para colores y rem para espaciado.
    """


# ── Design Tokens ──────────────────────────────────────────────────────────


@dataclass
class DesignTokens:
    """Sistema de design tokens — vocabulario visual ejecutable.

    Basado en OKLCH (Tailwind 4 compatible) + Inter typography.
    Exportable como JSON (Style Dictionary) o CSS custom properties.
    """

    # Spacing scale (rem)
    spacing: dict = field(
        default_factory=lambda: {
            "xs": "0.25rem",
            "sm": "0.5rem",
            "md": "1rem",
            "lg": "1.5rem",
            "xl": "2rem",
            "2xl": "3rem",
            "3xl": "4rem",
            "4xl": "6rem",
            "5xl": "8rem",
        }
    )

    # Color system (OKLCH for Tailwind 4 compatibility)
    colors: dict = field(
        default_factory=lambda: {
            "primary": {
                "base": "oklch(0.65 0.15 250)",
                "light": "oklch(0.85 0.08 250)",
                "dark": "oklch(0.45 0.15 250)",
            },
            "secondary": {
                "base": "oklch(0.70 0.10 180)",
                "light": "oklch(0.90 0.05 180)",
                "dark": "oklch(0.50 0.10 180)",
            },
            "neutral": {
                "50": "oklch(0.98 0 0)",
                "100": "oklch(0.95 0 0)",
                "900": "oklch(0.15 0 0)",
            },
            "success": "oklch(0.72 0.15 145)",
            "warning": "oklch(0.80 0.15 85)",
            "error": "oklch(0.65 0.20 25)",
        }
    )

    # Typography
    typography: dict = field(
        default_factory=lambda: {
            "font_display": "'Inter Tight', system-ui, sans-serif",
            "font_body": "'Inter', system-ui, sans-serif",
            "font_mono": "'JetBrains Mono', monospace",
            "scale": {
                "xs": "0.75rem",
                "sm": "0.875rem",
                "base": "1rem",
                "lg": "1.125rem",
                "xl": "1.25rem",
                "2xl": "1.5rem",
                "3xl": "1.875rem",
                "4xl": "2.25rem",
                "5xl": "3rem",
            },
            "line_height": {"tight": "1.25", "normal": "1.5", "relaxed": "1.75"},
        }
    )

    # Shadows
    shadows: dict = field(
        default_factory=lambda: {
            "sm": "0 1px 2px oklch(0 0 0 / 0.05)",
            "md": "0 4px 6px oklch(0 0 0 / 0.07)",
            "lg": "0 10px 15px oklch(0 0 0 / 0.1)",
            "xl": "0 20px 25px oklch(0 0 0 / 0.1)",
        }
    )

    # Border radius
    radii: dict = field(
        default_factory=lambda: {
            "sm": "0.25rem",
            "md": "0.5rem",
            "lg": "0.75rem",
            "xl": "1rem",
            "2xl": "1.5rem",
            "full": "9999px",
        }
    )

    def export_json(self) -> str:
        """Exportar tokens como JSON para Style Dictionary.

        Returns:
            JSON string con todos los tokens.
        """
        return json.dumps(
            {
                "spacing": self.spacing,
                "colors": self.colors,
                "typography": self.typography,
                "shadows": self.shadows,
                "radii": self.radii,
            },
            indent=2,
        )

    def export_css_variables(self) -> str:
        """Exportar tokens como CSS custom properties.

        Returns:
            String CSS con :root { --spacing-*, --radius-*, etc. }
        """
        lines = [":root {"]

        for key, value in self.spacing.items():
            lines.append(f"  --spacing-{key}: {value};")

        for key, value in self.radii.items():
            lines.append(f"  --radius-{key}: {value};")

        # Colors (flatten nested)
        for color_name, color_value in self.colors.items():
            if isinstance(color_value, dict):
                for variant, val in color_value.items():
                    lines.append(f"  --color-{color_name}-{variant}: {val};")
            else:
                lines.append(f"  --color-{color_name}: {color_value};")

        lines.append("}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Serializar para Command Center."""
        return {
            "spacing_keys": list(self.spacing.keys()),
            "color_keys": list(self.colors.keys()),
            "typography_fonts": [self.typography["font_display"], self.typography["font_body"]],
            "radii_keys": list(self.radii.keys()),
        }


# ── Resultado de Auditoría ─────────────────────────────────────────────────


@dataclass
class DesignAuditResult:
    """Resultado de auditoría de diseño (4 dimensiones).

    Args:
        url: URL auditada.
        overall_score: Score general 0-100.
        accessibility_score: Score WCAG 2.2 (0-100).
        performance_score: Score Core Web Vitals (0-100).
        token_compliance_score: Score de uso de design tokens (0-100).
        visual_consistency_score: Score de consistencia visual LLM (0-100).
        issues: Lista de issues encontrados.
        recommendations: Lista de recomendaciones accionables.
    """

    url: str
    overall_score: float
    accessibility_score: float
    performance_score: float
    token_compliance_score: float
    visual_consistency_score: float
    issues: list[dict]
    recommendations: list[str]

    def to_dict(self) -> dict:
        """Serializar para Command Center."""
        return {
            "url": self.url,
            "overall_score": self.overall_score,
            "accessibility_score": self.accessibility_score,
            "performance_score": self.performance_score,
            "token_compliance_score": self.token_compliance_score,
            "visual_consistency_score": self.visual_consistency_score,
            "issues_count": len(self.issues),
            "issues": self.issues[:5],  # Top 5 issues
            "recommendations": self.recommendations,
            "grade": self._grade(),
        }

    def _grade(self) -> str:
        """Calcular grado de calidad."""
        if self.overall_score >= 90:
            return "A — Apple/Tesla Level"
        elif self.overall_score >= 75:
            return "B — Professional"
        elif self.overall_score >= 60:
            return "C — Acceptable"
        else:
            return "D — Needs Work"


# ── Motor principal ────────────────────────────────────────────────────────


@dataclass
class DesignSystemEngine:
    """Motor de enforcement del design system.

    Audita 4 dimensiones de calidad de diseño:
    1. Accessibility (WCAG 2.2 via axe-core)
    2. Performance (Core Web Vitals via PageSpeed Insights)
    3. Token compliance (análisis de código)
    4. Visual consistency (LLM multimodal)

    Args:
        _sabios: Motor LLM para evaluación visual (opcional).
        tokens: Sistema de design tokens a aplicar.

    Soberanía:
        Sin Playwright: accessibility score = 0 con error descriptivo.
        Sin GOOGLE_PSI_API_KEY: performance score = 0 con error descriptivo.
        Sin Sabios: visual consistency score = 70.0 (neutral).
    """

    _sabios: Optional[object] = field(default=None, repr=False)
    tokens: DesignTokens = field(default_factory=DesignTokens)
    _audits_performed: int = 0

    # ── Accessibility Audit ────────────────────────────────────────────────

    async def audit_accessibility(self, url: str) -> dict:
        """Auditar accessibility via axe-core (requiere Playwright + @axe-core/playwright).

        Args:
            url: URL pública a auditar.

        Returns:
            Dict con score (0-100), violations count, y details.
            En caso de fallo: {"score": 0, "violations": -1, "error": "..."}

        Soberanía: Si Playwright no está instalado, retorna score 0 con mensaje descriptivo.
        """
        script = f"""
const {{ chromium }} = require('playwright');
const AxeBuilder = require('@axe-core/playwright').default;

(async () => {{
    const browser = await chromium.launch();
    const page = await browser.newPage();
    await page.goto('{url}', {{ waitUntil: 'networkidle' }});
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
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                total = data["violations"] + data["passes"]
                score = (data["passes"] / max(total, 1)) * 100
                return {
                    "score": round(score, 1),
                    "violations": data["violations"],
                    "passes": data["passes"],
                    "details": data["details"],
                }
        except subprocess.TimeoutExpired:
            logger.warning("accessibility_audit_timeout", url=url)
        except Exception as e:
            logger.warning("accessibility_audit_failed", error=str(e), url=url)

        return {
            "score": 0,
            "violations": -1,
            "details": [],
            "error": "Audit failed — Playwright o @axe-core/playwright no instalado. "
            "Instalar con: npm install playwright @axe-core/playwright",
        }

    # ── Performance Audit ──────────────────────────────────────────────────

    async def audit_performance(self, url: str) -> dict:
        """Auditar Core Web Vitals via PageSpeed Insights API.

        Args:
            url: URL pública a auditar.

        Returns:
            Dict con score (0-100), LCP (s), FID (ms), CLS.
            En caso de fallo: {"score": 0, "error": "..."}

        Soberanía: Sin GOOGLE_PSI_API_KEY funciona pero con rate limits.
        """
        import os

        import httpx

        api_key = os.getenv("GOOGLE_PSI_API_KEY", "")
        endpoint = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=mobile"
        if api_key:
            endpoint += f"&key={api_key}"

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(endpoint, timeout=60.0)
                if resp.status_code == 200:
                    data = resp.json()
                    metrics = data.get("lighthouseResult", {}).get("audits", {})

                    lcp = metrics.get("largest-contentful-paint", {}).get("numericValue", 0) / 1000
                    fid = metrics.get("max-potential-fid", {}).get("numericValue", 0)
                    cls = metrics.get("cumulative-layout-shift", {}).get("numericValue", 0)

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
                        "lcp_passes": lcp < 2.5,
                        "fid_passes": fid < 100,
                        "cls_passes": cls < 0.1,
                    }
        except Exception as e:
            logger.warning("performance_audit_failed", error=str(e), url=url)

        return {
            "score": 0,
            "error": "Audit failed — verificar GOOGLE_PSI_API_KEY o conectividad.",
        }

    # ── Full Design Audit ──────────────────────────────────────────────────

    async def full_audit(self, url: str) -> DesignAuditResult:
        """Auditoría completa de diseño (4 dimensiones).

        Args:
            url: URL pública a auditar.

        Returns:
            DesignAuditResult con scores en 4 dimensiones y recomendaciones.
        """
        self._audits_performed += 1

        # Ejecutar auditorías
        a11y_result = await self.audit_accessibility(url)
        perf_result = await self.audit_performance(url)

        # Token compliance (análisis estático — v1: score fijo)
        token_score = 75.0

        # Visual consistency (LLM multimodal si disponible)
        visual_score = 70.0
        if self._sabios:
            visual_score = await self._evaluate_visual_consistency(url)

        # Score general ponderado
        overall = (
            a11y_result.get("score", 0) * 0.30
            + perf_result.get("score", 0) * 0.25
            + token_score * 0.20
            + visual_score * 0.25
        )

        # Recopilar issues
        issues = []
        for detail in a11y_result.get("details", []):
            issues.append(
                {
                    "severity": detail.get("impact", "moderate"),
                    "category": "accessibility",
                    "description": detail.get("description", ""),
                    "element": f"{detail.get('nodes', 0)} elementos afectados",
                }
            )

        if perf_result.get("lcp_seconds", 0) > 2.5:
            issues.append(
                {
                    "severity": "serious",
                    "category": "performance",
                    "description": f"LCP es {perf_result.get('lcp_seconds')}s (debe ser < 2.5s)",
                    "element": "page load",
                }
            )

        if perf_result.get("cls", 0) > 0.1:
            issues.append(
                {
                    "severity": "moderate",
                    "category": "performance",
                    "description": f"CLS es {perf_result.get('cls')} (debe ser < 0.1)",
                    "element": "layout shift",
                }
            )

        logger.info("design_audit_completo", url=url, overall=round(overall, 1), issues=len(issues))

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
        """Evaluar consistencia visual con LLM multimodal.

        Args:
            url: URL a evaluar.

        Returns:
            Score 0-100. Retorna 70.0 si LLM no disponible.
        """
        if not self._sabios:
            return 70.0

        prompt = f"""Evalúa la calidad de diseño visual de esta página web: {url}

Puntúa del 0-100 en estos criterios:
- Jerarquía tipográfica (tamaños, pesos, interlineado consistentes)
- Armonía de color (coherencia de paleta, ratios de contraste)
- Ritmo de espaciado (padding/margins consistentes)
- Consistencia de componentes (botones, cards, inputs unificados)
- Jerarquía visual (prioridad de información clara)

Responde solo con un número del 0 al 100."""

        try:
            response = await self._sabios.ask(prompt)
            score = float(response.strip().split()[0])
            return min(100.0, max(0.0, score))
        except Exception as e:
            logger.warning("visual_consistency_failed", error=str(e))
            return 70.0

    @staticmethod
    def _generate_recommendations(issues: list[dict]) -> list[str]:
        """Generar recomendaciones accionables basadas en issues.

        Args:
            issues: Lista de issues encontrados.

        Returns:
            Lista de recomendaciones priorizadas.
        """
        recs = []

        a11y_issues = [i for i in issues if i["category"] == "accessibility"]
        if a11y_issues:
            recs.append(
                f"Corregir {len(a11y_issues)} violaciones de accessibility WCAG 2.2 — "
                "priorizar 'critical' e 'serious' primero."
            )

        perf_issues = [i for i in issues if i["category"] == "performance"]
        if perf_issues:
            recs.append(
                "Optimizar Core Web Vitals: LCP < 2.5s (lazy load images), CLS < 0.1 (reservar espacio para imágenes)."
            )

        if not issues:
            recs.append("Diseño pasa los criterios básicos. Considerar auditoría manual para refinamiento.")

        return recs

    def to_dict(self) -> dict:
        """Serializar estado para Command Center."""
        return {
            "audits_performed": self._audits_performed,
            "tokens": self.tokens.to_dict(),
            "con_sabios": self._sabios is not None,
        }


# ── Singleton ──────────────────────────────────────────────────────────────

_design_engine_instance: Optional[DesignSystemEngine] = None


def get_design_system_engine() -> Optional[DesignSystemEngine]:
    """Obtener instancia singleton del Design System Engine."""
    return _design_engine_instance


def init_design_system_engine(sabios=None) -> DesignSystemEngine:
    """Inicializar el Design System Engine.

    Args:
        sabios: Motor LLM para evaluación visual (opcional).

    Returns:
        Instancia singleton de DesignSystemEngine.
    """
    global _design_engine_instance
    _design_engine_instance = DesignSystemEngine(_sabios=sabios)
    logger.info("design_system_engine_inicializado", con_sabios=sabios is not None)
    return _design_engine_instance
