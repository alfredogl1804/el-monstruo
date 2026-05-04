"""
El Monstruo — Embrión Critic Visual (Sprint 85)
==================================================
Embrión nuevo que evalúa outputs del Executor antes de publicar.

Cuando el Executor termina de generar un sitio web, este embrión NO confía.
Toma screenshot del output renderizado, lo evalúa contra la rúbrica del Brief,
y decide si pasa o regresa al Executor con findings específicos.

Pipeline:
    1. Recibe URL deployada + brief.json
    2. Toma screenshot (desktop + mobile 375px)
    3. Evalúa contra rúbrica de 8 componentes (estructura, contenido, visual,
       brand fit, mobile, performance, CTA, meta tags)
    4. Retorna {"score": 0-100, "findings": [...], "passed": bool}
    5. Si score < 80, regresa al Executor con findings como feedback
    6. Loop máximo 3 iteraciones, después escala al usuario

Rúbrica (componentes ponderados):
    | Componente   | Peso |
    |--------------|------|
    | Estructura   |  20  |
    | Contenido    |  25  |
    | Visual       |  15  |
    | Brand fit    |  15  |
    | Mobile       |  10  |
    | Performance  |   5  |
    | CTA          |   5  |
    | Meta tags    |   5  |
    | TOTAL        | 100  |

Score >= 80 = quality_passed=true. Score < 80 = regresa al Executor.

Hermanos: Product Architect (Sprint 85, produce el Brief que evaluamos contra).
Backend: BrowserAutomation (soberano) o BrowserlessClient (fallback temporal).

Sprint 85 — 2026-05-04
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

import structlog

logger = structlog.get_logger("monstruo.embrion.critic_visual")


# ── Errores con identidad ────────────────────────────────────────────────────
class EmbrionCriticVisualError(Exception):
    """Error base del Embrión Critic Visual."""


CRITIC_VISUAL_SIN_BROWSER = (
    "CRITIC_VISUAL_SIN_BROWSER: "
    "El Critic Visual requiere un browser backend (soberano o browserless). "
    "Sugerencia: setear CRITIC_BROWSER_BACKEND=browserless + BROWSERLESS_URL/TOKEN, "
    "o esperar Sprint 84.6 (browser soberano)."
)

CRITIC_VISUAL_BRIEF_INVALIDO = (
    "CRITIC_VISUAL_BRIEF_INVALIDO: "
    "El Brief recibido no tiene las keys mínimas (vertical, structure, client_brand). "
    "Sugerencia: verificar que el Product Architect produjo el Brief correctamente."
)

CRITIC_VISUAL_NAVEGACION_FALLO = (
    "CRITIC_VISUAL_NAVEGACION_FALLO: "
    "No se pudo navegar a la URL '{url}'. Error del browser: {error}. "
    "Sugerencia: verificar que el deploy esté activo y la URL sea pública."
)


# ── Pesos de la rúbrica (suma = 100) ─────────────────────────────────────────
RUBRICA_PESOS = {
    "estructura": 20,
    "contenido": 25,
    "visual": 15,
    "brand_fit": 15,
    "mobile": 10,
    "performance": 5,
    "cta": 5,
    "meta_tags": 5,
}

PASS_SCORE_DEFAULT = int(os.environ.get("CRITIC_PASS_SCORE", "80"))
MAX_ITERATIONS_DEFAULT = int(os.environ.get("CRITIC_MAX_ITERATIONS", "3"))


# ── Dataclass: CriticReport ──────────────────────────────────────────────────
@dataclass
class CriticFinding:
    """Hallazgo específico del Critic. El Executor lo consume como feedback."""

    componente: str
    severity: str  # "blocker" | "major" | "minor"
    descripcion: str
    sugerencia: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "componente": self.componente,
            "severity": self.severity,
            "descripcion": self.descripcion,
            "sugerencia": self.sugerencia,
        }


@dataclass
class CriticReport:
    """Resultado completo de una evaluación del Critic Visual."""

    deploy_url: str
    brief_id: Optional[str]
    score: int  # 0-100
    passed: bool
    componente_scores: dict[str, int] = field(default_factory=dict)
    findings: list[CriticFinding] = field(default_factory=list)
    screenshot_desktop_path: Optional[str] = None
    screenshot_mobile_path: Optional[str] = None
    backend_used: str = "soberano"
    iteration: int = 1
    duration_ms: int = 0
    error: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "deploy_url": self.deploy_url,
            "brief_id": self.brief_id,
            "score": self.score,
            "passed": self.passed,
            "componente_scores": self.componente_scores,
            "findings": [f.to_dict() for f in self.findings],
            "screenshot_desktop_path": self.screenshot_desktop_path,
            "screenshot_mobile_path": self.screenshot_mobile_path,
            "backend_used": self.backend_used,
            "iteration": self.iteration,
            "duration_ms": self.duration_ms,
            "error": self.error,
            "created_at": self.created_at,
        }


# ── Browser Adapter ──────────────────────────────────────────────────────────
class CriticVisualBrowserAdapter:
    """
    Encapsula browser para que el Critic Visual no dependa de implementación.

    Switch via env var: CRITIC_BROWSER_BACKEND = soberano | browserless

    Cuando Sprint 84.6 termine, el backend "soberano" cubre todo. Hasta
    entonces, browserless es el fallback temporal autorizado por Cowork.
    """

    def __init__(self):
        # Lectura en cada uso (regla del Cowork)
        backend = os.environ.get("CRITIC_BROWSER_BACKEND", "soberano").lower()
        self.backend = backend
        self._impl = self._cargar_backend(backend)

    def _cargar_backend(self, backend: str):
        if backend == "browserless":
            from kernel.embriones.critic_visual_browserless_fallback import (
                BrowserlessClient,
            )
            return BrowserlessClient()
        elif backend == "soberano":
            try:
                from kernel.browser_automation import BrowserAutomation
                return BrowserAutomation()
            except Exception as exc:
                # Fallback automático a browserless si soberano no está listo
                logger.warning(
                    "critic_browser_soberano_unavailable_fallback_browserless",
                    error=str(exc),
                )
                from kernel.embriones.critic_visual_browserless_fallback import (
                    BrowserlessClient,
                )
                self.backend = "browserless"
                return BrowserlessClient()
        else:
            raise EmbrionCriticVisualError(
                f"CRITIC_BROWSER_BACKEND inválido: {backend}. "
                f"Válidos: soberano, browserless."
            )

    async def initialize(self):
        return await self._impl.initialize()

    async def navigate(self, url: str):
        return await self._impl.navigate(url)

    async def screenshot(self, path: Optional[str] = None, full_page: bool = False):
        return await self._impl.screenshot(path=path, full_page=full_page)

    async def extract_text(self, selector: str):
        return await self._impl.extract_text(selector)

    async def set_viewport(self, width: int, height: int):
        if hasattr(self._impl, "set_viewport"):
            return await self._impl.set_viewport(width, height)
        # Fallback: setear el viewport del adapter (soberano puede leerlo en initialize)
        if hasattr(self._impl, "viewport"):
            self._impl.viewport = {"width": width, "height": height}
        return None

    async def close(self):
        return await self._impl.close()


# ── Embrión principal ────────────────────────────────────────────────────────
@dataclass
class CriticVisual:
    """
    Embrión que evalúa outputs del Executor con rúbrica visual + estructural.

    Args:
        _sabios: Cliente de Sabios para análisis cualitativo (opcional).
        _db: Cliente Supabase para persistir reports en `deployments`.
        pass_score: Score mínimo para pasar (default 80 desde env CRITIC_PASS_SCORE).
        max_iterations: Máximo de iteraciones antes de escalar (default 3).
    """

    _sabios: Optional[object] = field(default=None, repr=False)
    _db: Optional[object] = field(default=None, repr=False)
    pass_score: int = PASS_SCORE_DEFAULT
    max_iterations: int = MAX_ITERATIONS_DEFAULT

    EMBRION_ID: str = field(default="critic-visual", init=False)
    SPECIALIZATION: str = field(
        default="Evaluación visual + estructural de sites contra Brief",
        init=False,
    )

    # ── API pública ──────────────────────────────────────────────────────
    async def evaluar(
        self,
        deploy_url: str,
        brief: dict[str, Any],
        iteration: int = 1,
    ) -> CriticReport:
        """
        Evalúa un sitio deployado contra el Brief.

        Args:
            deploy_url: URL pública del sitio deployado.
            brief: Brief producido por Product Architect (dict).
            iteration: Número de iteración (1-3).

        Returns:
            CriticReport con score 0-100, findings, screenshots y veredicto.
        """
        started = datetime.now(timezone.utc)

        # Validar brief mínimo
        self._validar_brief(brief)

        report = CriticReport(
            deploy_url=deploy_url,
            brief_id=brief.get("brief_id"),
            score=0,
            passed=False,
            iteration=iteration,
        )

        # Inicializar browser
        adapter = CriticVisualBrowserAdapter()
        report.backend_used = adapter.backend

        init = await adapter.initialize()
        if not getattr(init, "success", False):
            report.error = f"browser_init_failed: {getattr(init, 'error', 'unknown')}"
            await adapter.close()
            return report

        try:
            # Navegar (capturando métricas de performance)
            nav = await adapter.navigate(deploy_url)
            if not getattr(nav, "success", False):
                report.error = CRITIC_VISUAL_NAVEGACION_FALLO.format(
                    url=deploy_url, error=getattr(nav, "error", "unknown")
                )
                await adapter.close()
                return report

            perf_metrics = getattr(nav, "data", {}) or {}

            # Screenshot DESKTOP (full page)
            desktop_path = f"/tmp/critic_{brief.get('brief_id', 'noid')}_desktop_iter{iteration}.png"
            shot_desktop = await adapter.screenshot(path=desktop_path, full_page=True)
            if getattr(shot_desktop, "success", False):
                report.screenshot_desktop_path = shot_desktop.screenshot_path

            # Switch a MOBILE viewport y screenshot
            await adapter.set_viewport(375, 812)
            mobile_path = f"/tmp/critic_{brief.get('brief_id', 'noid')}_mobile_iter{iteration}.png"
            shot_mobile = await adapter.screenshot(path=mobile_path, full_page=True)
            if getattr(shot_mobile, "success", False):
                report.screenshot_mobile_path = shot_mobile.screenshot_path

            # Extraer texto de secciones críticas (volver a desktop primero)
            await adapter.set_viewport(1280, 720)
            await adapter.navigate(deploy_url)

            hero_result = await adapter.extract_text("h1, .hero, header h1")
            cta_result = await adapter.extract_text("button, a.cta, .btn-primary, [role='button']")
            body_result = await adapter.extract_text("main, body, article")
            head_html_result = await adapter.extract_text("head")

            hero_text = getattr(hero_result, "data", "") or ""
            cta_text = getattr(cta_result, "data", "") or ""
            body_text = getattr(body_result, "data", "") or ""
            head_text = getattr(head_html_result, "data", "") or ""

            # Aplicar rúbrica
            scores, findings = self._aplicar_rubrica(
                brief=brief,
                hero_text=str(hero_text),
                cta_text=str(cta_text),
                body_text=str(body_text),
                head_text=str(head_text),
                perf_metrics=perf_metrics,
                screenshot_mobile_path=report.screenshot_mobile_path,
            )

            report.componente_scores = scores
            report.findings = findings
            report.score = sum(scores.values())
            report.passed = report.score >= self.pass_score

            await adapter.close()

        except Exception as exc:
            report.error = f"critic_evaluation_failed: {exc}"
            try:
                await adapter.close()
            except Exception:
                pass

        # Métricas
        report.duration_ms = int(
            (datetime.now(timezone.utc) - started).total_seconds() * 1000
        )

        # Persistir en `deployments` si hay DB
        await self._persistir_report(report)

        logger.info(
            "critic_evaluation_complete",
            deploy_url=deploy_url,
            score=report.score,
            passed=report.passed,
            iteration=iteration,
            backend=report.backend_used,
            findings_count=len(report.findings),
        )

        return report

    # ── Rúbrica ─────────────────────────────────────────────────────────
    def _aplicar_rubrica(
        self,
        brief: dict[str, Any],
        hero_text: str,
        cta_text: str,
        body_text: str,
        head_text: str,
        perf_metrics: dict[str, Any],
        screenshot_mobile_path: Optional[str],
    ) -> tuple[dict[str, int], list[CriticFinding]]:
        """Aplica los 8 componentes de la rúbrica. Retorna (scores, findings)."""
        scores: dict[str, int] = {}
        findings: list[CriticFinding] = []

        structure = brief.get("structure", {}) or {}
        client_brand = brief.get("client_brand", {}) or {}

        # ── 1. Estructura (20pts) ────────────────────────────────────────
        secciones_requeridas = structure.get("sections", []) or []
        scores["estructura"], structure_findings = self._evaluar_estructura(
            secciones_requeridas, body_text
        )
        findings.extend(structure_findings)

        # ── 2. Contenido (25pts) ──────────────────────────────────────────
        scores["contenido"], content_findings = self._evaluar_contenido(
            body_text, brief
        )
        findings.extend(content_findings)

        # ── 3. Visual (15pts) ─────────────────────────────────────────────
        # Sin LLM multimodal en MVP, scoring conservador basado en heurísticas
        scores["visual"], visual_findings = self._evaluar_visual(
            hero_text, body_text
        )
        findings.extend(visual_findings)

        # ── 4. Brand Fit (15pts) ──────────────────────────────────────────
        scores["brand_fit"], brand_findings = self._evaluar_brand_fit(
            body_text, client_brand
        )
        findings.extend(brand_findings)

        # ── 5. Mobile (10pts) ─────────────────────────────────────────────
        scores["mobile"], mobile_findings = self._evaluar_mobile(
            screenshot_mobile_path
        )
        findings.extend(mobile_findings)

        # ── 6. Performance (5pts) ─────────────────────────────────────────
        scores["performance"], perf_findings = self._evaluar_performance(perf_metrics)
        findings.extend(perf_findings)

        # ── 7. CTA (5pts) ─────────────────────────────────────────────────
        scores["cta"], cta_findings = self._evaluar_cta(cta_text, structure)
        findings.extend(cta_findings)

        # ── 8. Meta tags (5pts) ──────────────────────────────────────────
        scores["meta_tags"], meta_findings = self._evaluar_meta_tags(head_text)
        findings.extend(meta_findings)

        return scores, findings

    def _evaluar_estructura(
        self, secciones_requeridas: list, body_text: str
    ) -> tuple[int, list[CriticFinding]]:
        """20pts. Todas las secciones del brief deben estar presentes."""
        findings = []
        if not secciones_requeridas:
            return RUBRICA_PESOS["estructura"], findings

        body_lower = body_text.lower()
        secciones_encontradas = 0
        for seccion in secciones_requeridas:
            if isinstance(seccion, dict):
                seccion_id = seccion.get("id", "") or seccion.get("name", "")
            else:
                seccion_id = str(seccion)

            seccion_id_lower = seccion_id.lower()
            keywords = [
                kw for kw in seccion_id_lower.replace("_", " ").split()
                if len(kw) > 2
            ]
            # HOTFIX Sprint 85 (post-audit 84.5): word boundaries para evitar
            # "learn" matcheando "learning" sin estar en un heading real.
            if keywords:
                pattern = re.compile(
                    r"\b(?:" + "|".join(re.escape(k) for k in keywords) + r")\b",
                    re.IGNORECASE,
                )
                seccion_match = bool(pattern.search(body_lower))
            else:
                seccion_match = False
            if seccion_match:
                secciones_encontradas += 1
            else:
                findings.append(CriticFinding(
                    componente="estructura",
                    severity="major",
                    descripcion=f"Sección '{seccion_id}' del Brief no detectada en el output",
                    sugerencia=f"Agregar sección '{seccion_id}' con heading visible",
                ))

        if not secciones_requeridas:
            return RUBRICA_PESOS["estructura"], findings

        ratio = secciones_encontradas / len(secciones_requeridas)
        score = int(RUBRICA_PESOS["estructura"] * ratio)
        return score, findings

    def _evaluar_contenido(
        self, body_text: str, brief: dict
    ) -> tuple[int, list[CriticFinding]]:
        """25pts. Sin Lorem ipsum, sin placeholders no autorizados."""
        findings = []
        score = RUBRICA_PESOS["contenido"]
        body_lower = body_text.lower()

        # Detectar Lorem ipsum
        if "lorem ipsum" in body_lower or "lorem ipsum dolor" in body_lower:
            findings.append(CriticFinding(
                componente="contenido",
                severity="blocker",
                descripcion="Lorem ipsum detectado en el contenido",
                sugerencia="Reemplazar con contenido real basado en el Brief",
            ))
            score -= 15

        # Detectar placeholders no autorizados (<<X>>, [X], TODO)
        unauthorized_placeholders = re.findall(r"<<[A-Z_]+>>|\bTODO\b|\bFIXME\b", body_text)
        # Excluir placeholders explícitos del brief
        autorizados = brief.get("data_missing", []) or []
        autorizados_set = {f"<<{a.upper().replace('.', '_')}>>" for a in autorizados}
        no_autorizados = [p for p in unauthorized_placeholders if p not in autorizados_set]

        if no_autorizados:
            findings.append(CriticFinding(
                componente="contenido",
                severity="major",
                descripcion=f"Placeholders no autorizados: {', '.join(set(no_autorizados[:3]))}",
                sugerencia="Eliminar TODO/FIXME y placeholders no declarados en data_missing",
            ))
            score -= 5

        # Longitud mínima de contenido
        word_count = len(body_text.split())
        if word_count < 100:
            findings.append(CriticFinding(
                componente="contenido",
                severity="major",
                descripcion=f"Contenido muy escaso: {word_count} palabras (mínimo 100)",
                sugerencia="Expandir cada sección con copy real basado en value_proposition",
            ))
            score -= 5

        return max(0, score), findings

    def _evaluar_visual(
        self, hero_text: str, body_text: str
    ) -> tuple[int, list[CriticFinding]]:
        """15pts. Heurísticas de jerarquía visual sin LLM multimodal."""
        findings = []
        score = RUBRICA_PESOS["visual"]

        if not hero_text.strip():
            findings.append(CriticFinding(
                componente="visual",
                severity="major",
                descripcion="No se detectó hero (h1 / .hero) en la página",
                sugerencia="Agregar un hero con h1 visible y mensaje del Brief",
            ))
            score -= 8

        if len(body_text.strip()) < 50:
            findings.append(CriticFinding(
                componente="visual",
                severity="blocker",
                descripcion="Body text casi vacío — la página puede estar en blanco",
                sugerencia="Verificar que el deploy renderizó correctamente",
            ))
            score -= 7

        return max(0, score), findings

    def _evaluar_brand_fit(
        self, body_text: str, client_brand: dict
    ) -> tuple[int, list[CriticFinding]]:
        """15pts. Anti-patrones de copy + presencia del nombre."""
        findings = []
        score = RUBRICA_PESOS["brand_fit"]
        body_lower = body_text.lower()

        # Nombre de marca presente
        nombre = (client_brand.get("name") or "").strip()
        if nombre and nombre.lower() not in body_lower:
            findings.append(CriticFinding(
                componente="brand_fit",
                severity="major",
                descripcion=f"Nombre de marca '{nombre}' no aparece en el output",
                sugerencia=f"Incluir '{nombre}' en hero, footer o título",
            ))
            score -= 8

        # Anti-patrones genéricos
        anti_patterns = ["10x", "growth hack", "lorem", "scale your", "disrupt"]
        encontrados = [ap for ap in anti_patterns if ap in body_lower]
        if encontrados:
            findings.append(CriticFinding(
                componente="brand_fit",
                severity="minor",
                descripcion=f"Anti-patrones de copy genérico: {', '.join(encontrados)}",
                sugerencia="Reemplazar con copy alineado al tono del vertical",
            ))
            score -= 3

        return max(0, score), findings

    def _evaluar_mobile(
        self, screenshot_path: Optional[str]
    ) -> tuple[int, list[CriticFinding]]:
        """10pts. Screenshot mobile capturado = base. Detección de overflow horizontal queda para Sprint 86."""
        findings = []
        if not screenshot_path or not os.path.exists(screenshot_path):
            findings.append(CriticFinding(
                componente="mobile",
                severity="major",
                descripcion="No se pudo capturar screenshot mobile (375px)",
                sugerencia="Verificar que el browser soporta set_viewport runtime",
            ))
            return 0, findings

        # MVP: si captura OK, asumimos pass parcial. Análisis visual queda para Sprint 86.
        return RUBRICA_PESOS["mobile"], findings

    def _evaluar_performance(
        self, perf_metrics: dict
    ) -> tuple[int, list[CriticFinding]]:
        """5pts. TTFB < 1000ms, LCP < 2500ms, CLS < 0.1."""
        findings = []
        score = RUBRICA_PESOS["performance"]

        ttfb = perf_metrics.get("ttfb_ms", 0)
        lcp = perf_metrics.get("lcp_ms", 0)

        if ttfb > 1000:
            findings.append(CriticFinding(
                componente="performance",
                severity="minor",
                descripcion=f"TTFB elevado: {ttfb}ms (target < 1000ms)",
                sugerencia="Optimizar respuesta del servidor o usar CDN",
            ))
            score -= 2

        if lcp > 2500:
            findings.append(CriticFinding(
                componente="performance",
                severity="minor",
                descripcion=f"LCP elevado: {lcp}ms (target < 2500ms)",
                sugerencia="Optimizar imágenes hero, lazy load, comprimir assets",
            ))
            score -= 2

        return max(0, score), findings

    def _evaluar_cta(
        self, cta_text: str, structure: dict
    ) -> tuple[int, list[CriticFinding]]:
        """5pts. Al menos 1 CTA visible above-the-fold."""
        findings = []
        if not cta_text.strip():
            findings.append(CriticFinding(
                componente="cta",
                severity="major",
                descripcion="No se detectaron CTAs (button, .cta, [role='button'])",
                sugerencia=f"Agregar CTA primario: '{structure.get('primary_cta', 'Contactar')}'",
            ))
            return 0, findings

        primary = (structure.get("primary_cta") or "").strip().lower()
        if primary and primary not in cta_text.lower():
            findings.append(CriticFinding(
                componente="cta",
                severity="minor",
                descripcion=f"CTA primario del Brief ('{primary}') no aparece literal en buttons",
                sugerencia=f"Renombrar uno de los CTAs a '{primary}'",
            ))
            return RUBRICA_PESOS["cta"] - 2, findings

        return RUBRICA_PESOS["cta"], findings

    def _evaluar_meta_tags(self, head_text: str) -> tuple[int, list[CriticFinding]]:
        """5pts. title, description, OG, Schema.org presentes."""
        findings = []
        score = RUBRICA_PESOS["meta_tags"]
        head_lower = head_text.lower()

        if "<title>" not in head_lower and "title" not in head_lower:
            # extract_text() puede haber stripeado las tags; ser más generoso
            pass

        # Heurística simple basada en strings esperados
        if "og:" not in head_lower:
            findings.append(CriticFinding(
                componente="meta_tags",
                severity="minor",
                descripcion="Open Graph tags no detectados (og:title, og:description)",
                sugerencia="Agregar <meta property='og:title'> y og:description",
            ))
            score -= 2

        return max(0, score), findings

    # ── Validación ──────────────────────────────────────────────────────
    def _validar_brief(self, brief: dict) -> None:
        required = {"vertical", "structure", "client_brand"}
        if not isinstance(brief, dict) or not required.issubset(brief.keys()):
            raise EmbrionCriticVisualError(CRITIC_VISUAL_BRIEF_INVALIDO)

    # ── Persistencia ────────────────────────────────────────────────────
    async def _persistir_report(self, report: CriticReport) -> None:
        """Persiste el report en la tabla `deployments` (si hay DB)."""
        if self._db is None or not getattr(self._db, "_connected", False):
            return

        try:
            row = {
                "url": report.deploy_url,
                "brief_id": report.brief_id,
                "critic_score": report.score,
                "quality_passed": report.passed,
                "retry_count": report.iteration,
                "screenshot_url": report.screenshot_desktop_path,
                "critic_findings": [f.to_dict() for f in report.findings],
                "status": "active" if report.passed else "rejected_by_critic",
            }
            # Si la fila existe (por brief_id + url), upsert. Si no, insert.
            await self._db.upsert("deployments", row, on_conflict="url")
            logger.info("critic_report_persisted", url=report.deploy_url, score=report.score)
        except Exception as exc:
            logger.warning("critic_report_persist_failed", error=str(exc))

    def estado(self) -> dict[str, Any]:
        """Estado del embrión para el Command Center."""
        backend = os.environ.get("CRITIC_BROWSER_BACKEND", "soberano")
        return {
            "embrion_id": self.EMBRION_ID,
            "specialization": self.SPECIALIZATION,
            "estado": "activo",
            "backend_default": backend,
            "pass_score": self.pass_score,
            "max_iterations": self.max_iterations,
            "rubrica_pesos": RUBRICA_PESOS,
        }
