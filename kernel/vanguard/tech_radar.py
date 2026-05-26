"""
El Monstruo — Tech Radar & Auto-Updater (Sprint 60)
=====================================================
Sistema de auto-actualización y escaneo de tendencias tecnológicas.

Capa 1: Dependency Monitor — versiones, CVEs, deprecations
Capa 2: Tech Radar — tendencias, adopciones, retiros

Principio: El Monstruo siempre usa lo mejor disponible.
Objetivo cubierto: #6 — Vanguardia Perpetua
Sprint 60 — 2026-05-01

Soberanía: Usa PyPI JSON API (pública, sin auth) y OSV.dev (pública).
           Alternativa: pip-audit para CVEs locales, pip list --outdated para versiones.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import structlog

logger = structlog.get_logger("monstruo.vanguard")


# ── Errores con identidad ────────────────────────────────────────────────────


class TechRadarError(Exception):
    """Error base del Tech Radar."""


TECH_RADAR_REQUIREMENTS_VACIO = (
    "TECH_RADAR_REQUIREMENTS_VACIO: "
    "El contenido de requirements.txt está vacío. "
    "Sugerencia: Pasa el contenido del archivo como string a scan_dependencies()."
)

TECH_RADAR_PYPI_NO_DISPONIBLE = (
    "TECH_RADAR_PYPI_NO_DISPONIBLE: "
    "No se pudo conectar a PyPI para verificar versiones. "
    "Sugerencia: Verificar conectividad de red. Alternativa: pip list --outdated."
)


# ── Dataclasses ──────────────────────────────────────────────────────────────


@dataclass
class DependencyUpdate:
    """
    Una actualización de dependencia detectada.

    Args:
        package: Nombre del paquete en PyPI.
        current_version: Versión actualmente en requirements.txt.
        latest_version: Última versión disponible en PyPI.
        release_date: Fecha de release de la última versión (YYYY-MM-DD).
        is_major: Si es un cambio de versión mayor (breaking changes posibles).
        is_security: Si hay CVEs conocidos en la versión actual.
        changelog_url: URL al changelog/release notes.
        risk_level: Nivel de riesgo ('low', 'medium', 'high').
        recommendation: Acción recomendada ('update', 'evaluate', 'skip').
    """

    package: str
    current_version: str
    latest_version: str
    release_date: str
    is_major: bool
    is_security: bool
    changelog_url: str
    risk_level: str
    recommendation: str

    def to_dict(self) -> dict:
        """Serializar para el Command Center."""
        return {
            "package": self.package,
            "current_version": self.current_version,
            "latest_version": self.latest_version,
            "release_date": self.release_date,
            "is_major": self.is_major,
            "is_security": self.is_security,
            "risk_level": self.risk_level,
            "recommendation": self.recommendation,
            "changelog_url": self.changelog_url,
        }


@dataclass
class TechTrend:
    """
    Una tendencia tecnológica detectada.

    Args:
        name: Nombre del paquete/herramienta/patrón.
        category: Categoría ('framework', 'library', 'pattern', 'tool').
        signal_strength: Fuerza de la señal ('weak', 'moderate', 'strong').
        relevance_to_monstruo: Por qué es relevante para El Monstruo.
        adoption_recommendation: Recomendación ThoughtWorks-style ('adopt', 'trial', 'assess', 'hold').
        source: Fuente de la tendencia.
    """

    name: str
    category: str
    signal_strength: str
    relevance_to_monstruo: str
    adoption_recommendation: str
    source: str

    def to_dict(self) -> dict:
        """Serializar para el Command Center."""
        return {
            "name": self.name,
            "category": self.category,
            "signal_strength": self.signal_strength,
            "relevance": self.relevance_to_monstruo[:150],
            "recommendation": self.adoption_recommendation,
            "source": self.source,
        }


@dataclass
class TechRadar:
    """
    Tech Radar de El Monstruo.

    Dos capas de inteligencia tecnológica:
    - Capa 1 (Dependency Monitor): Detecta versiones desactualizadas y CVEs.
    - Capa 2 (Tech Radar): Escanea tendencias del ecosistema Python/AI.

    Args:
        _sabios: Interfaz a los Sabios para enriquecimiento de tendencias (opcional).
        requirements_path: Ruta al requirements.txt del proyecto.

    Soberanía: Funciona sin Sabios — las tendencias se reportan sin enriquecimiento.
               Alternativa: pip-audit para CVEs, pip list --outdated para versiones.
    """

    _sabios: Optional[object] = field(default=None, repr=False)
    requirements_path: str = "requirements.txt"
    _last_scan: Optional[str] = field(default=None, repr=False)
    _last_trends: list[TechTrend] = field(default_factory=list, repr=False)

    # ── Capa 1: Dependency Monitor ───────────────────────────────────────────

    async def scan_dependencies(self, requirements_content: str) -> list[DependencyUpdate]:
        """
        Escanear requirements.txt contra PyPI para detectar actualizaciones.

        Args:
            requirements_content: Contenido completo del requirements.txt como string.

        Returns:
            Lista de DependencyUpdate con paquetes que tienen versiones nuevas.

        Raises:
            TechRadarError: Si el contenido está vacío.

        Soberanía: Usa PyPI JSON API pública. Alternativa: pip list --outdated.
        """
        if not requirements_content or not requirements_content.strip():
            raise TechRadarError(TECH_RADAR_REQUIREMENTS_VACIO)

        updates: list[DependencyUpdate] = []
        lines = requirements_content.strip().split("\n")
        checked = 0
        skipped = 0

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                skipped += 1
                continue

            match = re.match(r"^([a-zA-Z0-9_-]+)\[?[^\]]*\]?==([0-9.]+)", line)
            if not match:
                skipped += 1
                continue

            package = match.group(1)
            current = match.group(2)
            checked += 1

            try:
                latest_info = await self._check_pypi(package)
                if not latest_info:
                    continue

                latest_ver = latest_info["version"]
                if latest_ver == current:
                    continue

                is_major = latest_ver.split(".")[0] != current.split(".")[0]

                # Check CVEs via OSV.dev
                vulns = await self.check_security_advisories(package, current)
                is_security = len(vulns) > 0

                updates.append(
                    DependencyUpdate(
                        package=package,
                        current_version=current,
                        latest_version=latest_ver,
                        release_date=latest_info.get("release_date", "unknown"),
                        is_major=is_major,
                        is_security=is_security,
                        changelog_url=f"https://pypi.org/project/{package}/{latest_ver}/",
                        risk_level="high" if is_security else ("medium" if is_major else "low"),
                        recommendation="update_urgente" if is_security else ("evaluate" if is_major else "update"),
                    )
                )

            except Exception as e:
                logger.warning(
                    "pypi_check_fallido",
                    paquete=package,
                    error=str(e),
                    sugerencia="Verificar conectividad de red",
                )

        logger.info(
            "dependency_scan_completado",
            verificados=checked,
            omitidos=skipped,
            actualizaciones=len(updates),
            seguridad=sum(1 for u in updates if u.is_security),
        )
        self._last_scan = datetime.now(timezone.utc).isoformat()
        return updates

    async def _check_pypi(self, package: str) -> Optional[dict]:
        """
        Consultar PyPI JSON API para obtener la última versión de un paquete.

        Args:
            package: Nombre del paquete en PyPI.

        Returns:
            Dict con 'version' y 'release_date', o None si no se pudo obtener.
        """
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"https://pypi.org/pypi/{package}/json",
                    timeout=10.0,
                )
                if resp.status_code != 200:
                    return None

                data = resp.json()
                version = data["info"]["version"]
                releases = data.get("releases", {}).get(version, [])
                release_date = releases[0]["upload_time"][:10] if releases else "unknown"

                return {"version": version, "release_date": release_date}
        except Exception:
            return None

    async def check_security_advisories(self, package: str, version: str) -> list[dict]:
        """
        Consultar OSV.dev para CVEs conocidos de un paquete y versión.

        Args:
            package: Nombre del paquete.
            version: Versión a verificar.

        Returns:
            Lista de vulnerabilidades encontradas (vacía si no hay CVEs).

        Soberanía: OSV.dev es gratuito y público. Alternativa: pip-audit.
        """
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.osv.dev/v1/query",
                    json={
                        "package": {"name": package, "ecosystem": "PyPI"},
                        "version": version,
                    },
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    return resp.json().get("vulns", [])
        except Exception as e:
            logger.warning(
                "osv_check_fallido",
                paquete=package,
                version=version,
                error=str(e),
            )
        return []

    def generate_update_report(self, updates: list[DependencyUpdate]) -> str:
        """
        Generar reporte Markdown de actualizaciones pendientes.

        Args:
            updates: Lista de DependencyUpdate a reportar.

        Returns:
            Reporte en formato Markdown listo para commit/PR.
        """
        if not updates:
            return "✅ Todas las dependencias están actualizadas."

        report = f"# Reporte de Actualizaciones de Dependencias\nGenerado: {datetime.now(timezone.utc).isoformat()}\n\n"

        security = [u for u in updates if u.is_security]
        major = [u for u in updates if u.is_major and not u.is_security]
        minor = [u for u in updates if not u.is_major and not u.is_security]

        if security:
            report += "## 🚨 ACTUALIZACIONES DE SEGURIDAD (aplicar inmediatamente)\n"
            for u in security:
                report += f"- **{u.package}**: `{u.current_version}` → `{u.latest_version}` — [changelog]({u.changelog_url})\n"

        if major:
            report += "\n## ⚠️ CAMBIOS MAYORES (evaluar antes de aplicar)\n"
            for u in major:
                report += f"- {u.package}: `{u.current_version}` → `{u.latest_version}` ({u.release_date}) — [changelog]({u.changelog_url})\n"

        if minor:
            report += "\n## ✅ ACTUALIZACIONES MENORES (seguras de aplicar)\n"
            for u in minor:
                report += f"- {u.package}: `{u.current_version}` → `{u.latest_version}` ({u.release_date})\n"

        return report

    # ── Capa 2: Tech Radar (Estratégico) ────────────────────────────────────

    async def scan_tech_trends(self) -> list[TechTrend]:
        """
        Escanear tendencias tecnológicas reales via APIs públicas.

        Sources:
        - PyPI Top Packages (30 días)
        - GitHub Trending (Python, último mes)
        - Enriquecimiento via Sabios (opcional)

        Returns:
            Lista de TechTrend con tendencias detectadas.

        Soberanía: Fuentes públicas sin auth. Alternativa: RSS feeds de PyPI/GitHub.
        """
        import httpx

        trends: list[TechTrend] = []

        # Source 1: PyPI Top Packages
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json",
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    top_packages = data.get("rows", [])[:20]
                    for pkg in top_packages:
                        if pkg.get("download_count", 0) > 50_000_000:
                            trends.append(
                                TechTrend(
                                    name=pkg["project"],
                                    category="library",
                                    signal_strength="strong",
                                    relevance_to_monstruo="Alto volumen de descargas indica estándar de la industria",
                                    adoption_recommendation="assess",
                                    source="PyPI Top Packages (30 días)",
                                )
                            )
        except Exception as e:
            logger.warning("pypi_trends_fallido", error=str(e))

        # Source 2: GitHub Trending (Python repos recientes)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.github.com/search/repositories?q=language:python+created:>2026-04-01&sort=stars&order=desc&per_page=10",
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for repo in data.get("items", [])[:5]:
                        trends.append(
                            TechTrend(
                                name=repo["name"],
                                category="tool",
                                signal_strength="moderate",
                                relevance_to_monstruo=(repo.get("description") or "Sin descripción")[:100],
                                adoption_recommendation="assess",
                                source=f"GitHub Trending ({repo['stargazers_count']} stars)",
                            )
                        )
        except Exception as e:
            logger.warning("github_trends_fallido", error=str(e))

        # Enriquecimiento via Sabios (opcional)
        if self._sabios and trends:
            try:
                trend_names = [t.name for t in trends[:10]]
                prompt = f"""Given these trending Python packages/tools: {trend_names}

Which are most relevant for an AI-powered business creation platform?
For each relevant one, explain why and recommend: adopt, trial, assess, or hold.
Respond in JSON array: [{{"name": "...", "relevance": "...", "recommendation": "adopt|trial|assess|hold"}}]"""

                response = await self._sabios.ask(prompt)
                enrichments = json.loads(self._extract_json(response))

                enrichment_map = {e["name"]: e for e in enrichments}
                for trend in trends:
                    if trend.name in enrichment_map:
                        e = enrichment_map[trend.name]
                        trend.relevance_to_monstruo = e.get("relevance", trend.relevance_to_monstruo)
                        trend.adoption_recommendation = e.get("recommendation", trend.adoption_recommendation)
            except Exception as e:
                logger.warning("sabios_enrichment_fallido", error=str(e))

        self._last_trends = trends
        logger.info("tech_radar_scan_completado", tendencias=len(trends))
        return trends

    def generate_radar_report(self, trends: list[TechTrend]) -> str:
        """
        Generar reporte estilo ThoughtWorks Tech Radar.

        Args:
            trends: Lista de TechTrend a reportar.

        Returns:
            Reporte en formato Markdown con 4 cuadrantes.
        """
        report = f"# El Monstruo Tech Radar\nGenerado: {datetime.now(timezone.utc).isoformat()}\n\n"

        adopt = [t for t in trends if t.adoption_recommendation == "adopt"]
        trial = [t for t in trends if t.adoption_recommendation == "trial"]
        assess = [t for t in trends if t.adoption_recommendation == "assess"]
        hold = [t for t in trends if t.adoption_recommendation == "hold"]

        for label, emoji, items in [
            ("ADOPT", "🟢", adopt),
            ("TRIAL", "🔵", trial),
            ("ASSESS", "🟡", assess),
            ("HOLD", "🔴", hold),
        ]:
            if items:
                report += f"\n## {emoji} {label}\n"
                for t in items:
                    report += f"- **{t.name}** ({t.category}): {t.relevance_to_monstruo[:80]} [fuente: {t.source}]\n"

        return report

    def to_dict(self) -> dict:
        """
        Serializar estado para el Command Center.

        Returns:
            Dict con estado del Tech Radar y últimas tendencias.
        """
        return {
            "modulo": "tech_radar",
            "sprint": "60.2",
            "objetivo": "Obj #6 — Vanguardia Perpetua",
            "ultimo_scan": self._last_scan,
            "tendencias_detectadas": len(self._last_trends),
            "tendencias": [t.to_dict() for t in self._last_trends[:10]],
        }

    @staticmethod
    def _extract_json(text: str) -> str:
        """Extraer JSON de respuesta de LLM."""
        if "```json" in text:
            return text.split("```json")[1].split("```")[0]
        if "```" in text:
            return text.split("```")[1].split("```")[0]
        return text.strip()


# ── Singleton ────────────────────────────────────────────────────────────────

_tech_radar: Optional[TechRadar] = None


def get_tech_radar() -> Optional[TechRadar]:
    """Obtener la instancia singleton del TechRadar."""
    return _tech_radar


def init_tech_radar(sabios=None) -> TechRadar:
    """
    Inicializar el TechRadar como singleton.

    Args:
        sabios: Interfaz a los Sabios para enriquecimiento (opcional).

    Returns:
        Instancia inicializada del TechRadar.
    """
    global _tech_radar
    _tech_radar = TechRadar(_sabios=sabios)
    logger.info("tech_radar_inicializado", con_sabios=sabios is not None)
    return _tech_radar
