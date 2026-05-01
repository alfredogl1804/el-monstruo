"""
El Monstruo — Sovereignty Engine (Sprint 60)
==============================================
Capa de soberanía que mapea dependencias externas,
define alternativas self-hosted, y genera migration paths.

Principio: El Monstruo PUEDE funcionar sin internet.
Realidad: Funciona MEJOR con internet, pero SOBREVIVE sin él.

Objetivo cubierto: #12 — Ecosistema de Monstruos Soberanos
Sprint 60 — 2026-05-01

Soberanía: Este módulo NO tiene dependencias externas en tiempo de importación.
           Todas las llamadas de red son lazy y con fallback.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

import structlog

logger = structlog.get_logger("monstruo.sovereignty")


# ── Errores con identidad ────────────────────────────────────────────────────

class SovereigntyEngineError(Exception):
    """Error base del Sovereignty Engine."""


SOVEREIGNTY_ENGINE_DEPENDENCIA_NO_ENCONTRADA = (
    "SOVEREIGNTY_ENGINE_DEPENDENCIA_NO_ENCONTRADA: "
    "La dependencia '{name}' no está registrada en el inventario. "
    "Sugerencia: Verifica el nombre o agrega la dependencia con register_dependency()."
)

SOVEREIGNTY_ENGINE_MODO_SOBERANO_YA_ACTIVO = (
    "SOVEREIGNTY_ENGINE_MODO_SOBERANO_YA_ACTIVO: "
    "El modo soberano ya está activado (SOVEREIGN_MODE=true). "
    "Sugerencia: Llama deactivate_sovereign_mode() primero si quieres re-activar."
)


# ── Enums ────────────────────────────────────────────────────────────────────

class DependencyTier(str, Enum):
    """Nivel de criticidad de una dependencia externa."""
    CRITICAL = "critical"   # Sistema no funciona sin ella
    HIGH = "high"           # Funcionalidad degradada sin ella
    MEDIUM = "medium"       # Feature específico no disponible
    LOW = "low"             # Conveniencia, fácil de reemplazar


class HealthStatus(str, Enum):
    """Estado de salud de una dependencia."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


# ── Dataclasses ──────────────────────────────────────────────────────────────

@dataclass
class ExternalDependency:
    """
    Representación de una dependencia externa del Monstruo.

    Args:
        name: Identificador único de la dependencia.
        service_type: Tipo de servicio ('llm', 'database', 'observability', etc.).
        tier: Nivel de criticidad (CRITICAL, HIGH, MEDIUM, LOW).
        endpoint: Variable de entorno que contiene la credencial.
        self_hosted_alternative: Alternativa self-hosted disponible.
        migration_path: Pasos para migrar a la alternativa.
        health: Estado de salud actual.
        last_checked: ISO timestamp del último health check.
        monthly_cost_usd: Costo mensual estimado en USD.
        data_exported: Si podemos exportar nuestros datos.
        api_compatible: Si la alternativa es API-compatible.

    Soberanía: No requiere conexión de red para instanciarse.
    """
    name: str
    service_type: str
    tier: DependencyTier
    endpoint: str
    self_hosted_alternative: str
    migration_path: str
    health: HealthStatus = HealthStatus.UNKNOWN
    last_checked: Optional[str] = None
    monthly_cost_usd: float = 0.0
    data_exported: bool = False
    api_compatible: bool = False

    def to_dict(self) -> dict:
        """Serializar para el Command Center."""
        return {
            "name": self.name,
            "service_type": self.service_type,
            "tier": self.tier.value,
            "health": self.health.value,
            "last_checked": self.last_checked,
            "monthly_cost_usd": self.monthly_cost_usd,
            "has_alternative": bool(self.self_hosted_alternative),
            "data_exported": self.data_exported,
            "api_compatible": self.api_compatible,
            "migration_path_preview": self.migration_path[:100] + "..." if len(self.migration_path) > 100 else self.migration_path,
        }


@dataclass
class SovereigntyEngine:
    """
    Motor de soberanía de El Monstruo.

    Mapea todas las dependencias externas, verifica su salud,
    calcula el score de soberanía, y puede activar modo soberano
    (redirigir todo a alternativas locales).

    Args:
        _supabase: Cliente Supabase para persistir health checks (opcional).

    Soberanía: Funciona sin Supabase — persiste en memoria si no hay DB.
               Alternativa: PostgreSQL directo via psycopg2.
    """

    _supabase: Optional[object] = field(default=None, repr=False)
    _dependencies: dict[str, ExternalDependency] = field(default_factory=dict)

    def __post_init__(self):
        """Registrar todas las dependencias conocidas al inicializar."""
        self._register_known_dependencies()
        logger.info(
            "sovereignty_engine_inicializado",
            total_dependencias=len(self._dependencies),
            criticas=len([d for d in self._dependencies.values() if d.tier == DependencyTier.CRITICAL]),
        )

    def _register_known_dependencies(self) -> None:
        """
        Inventario completo de dependencias externas del Monstruo.

        Registra las 8 dependencias conocidas con sus alternativas
        y migration paths documentados.
        """
        deps = [
            ExternalDependency(
                name="supabase",
                service_type="database",
                tier=DependencyTier.CRITICAL,
                endpoint="SUPABASE_URL",
                self_hosted_alternative="PostgreSQL 16 + pgvector + GoTrue",
                migration_path="pg_dump → pg_restore on self-hosted PG. GoTrue for auth. pgvector extension for embeddings.",
                monthly_cost_usd=25.0,
                data_exported=True,
                api_compatible=True,
            ),
            ExternalDependency(
                name="openai",
                service_type="llm",
                tier=DependencyTier.CRITICAL,
                endpoint="OPENAI_API_KEY",
                self_hosted_alternative="Ollama + gpt-oss:120b (Sprint 56 SovereignLLM)",
                migration_path="SovereignLLM ya soporta routing a Ollama. Activar SOVEREIGN_MODE=true.",
                monthly_cost_usd=50.0,
                data_exported=False,
                api_compatible=True,
            ),
            ExternalDependency(
                name="anthropic",
                service_type="llm",
                tier=DependencyTier.HIGH,
                endpoint="ANTHROPIC_API_KEY",
                self_hosted_alternative="Ollama + deepseek-v3.1:671b",
                migration_path="Router tier swap. DeepSeek como reemplazo de Claude para razonamiento complejo.",
                monthly_cost_usd=30.0,
                data_exported=False,
                api_compatible=False,
            ),
            ExternalDependency(
                name="google_gemini",
                service_type="llm",
                tier=DependencyTier.HIGH,
                endpoint="GEMINI_API_KEY",
                self_hosted_alternative="Ollama + qwen2.5:72b",
                migration_path="Router tier swap. Qwen como reemplazo de Gemini para multimodal.",
                monthly_cost_usd=20.0,
                data_exported=False,
                api_compatible=False,
            ),
            ExternalDependency(
                name="langfuse",
                service_type="observability",
                tier=DependencyTier.MEDIUM,
                endpoint="LANGFUSE_PUBLIC_KEY",
                self_hosted_alternative="Langfuse self-hosted (Docker) o OpenTelemetry + Jaeger",
                migration_path="Langfuse soporta self-hosting via Docker. Exportar traces via API. O migrar a OTLP con Jaeger.",
                monthly_cost_usd=0.0,
                data_exported=True,
                api_compatible=True,
            ),
            ExternalDependency(
                name="langsmith",
                service_type="tracing",
                tier=DependencyTier.MEDIUM,
                endpoint="LANGSMITH_API_KEY",
                self_hosted_alternative="OpenTelemetry + Jaeger",
                migration_path="Reemplazar callbacks de LangSmith con OTLP exporters. Jaeger para visualización.",
                monthly_cost_usd=0.0,
                data_exported=True,
                api_compatible=False,
            ),
            ExternalDependency(
                name="github",
                service_type="code_hosting",
                tier=DependencyTier.LOW,
                endpoint="GITHUB_TOKEN",
                self_hosted_alternative="Gitea o Forgejo",
                migration_path="git remote set-url origin <new-url>. Todo el historial se preserva.",
                monthly_cost_usd=0.0,
                data_exported=True,
                api_compatible=False,
            ),
            ExternalDependency(
                name="deepl",
                service_type="translation",
                tier=DependencyTier.LOW,
                endpoint="DEEPL_API_KEY",
                self_hosted_alternative="LLM translation via Sabios (Sprint 59 i18n Engine)",
                migration_path="i18n Engine ya tiene fallback a LLM. Activar DEEPL_ENABLED=false.",
                monthly_cost_usd=0.0,
                data_exported=True,
                api_compatible=False,
            ),
        ]

        for dep in deps:
            self._dependencies[dep.name] = dep

    def register_dependency(self, dep: ExternalDependency) -> None:
        """
        Registrar una nueva dependencia externa.

        Args:
            dep: Dependencia a registrar.
        """
        self._dependencies[dep.name] = dep
        logger.info("dependencia_registrada", name=dep.name, tier=dep.tier.value)

    async def health_check_all(self) -> dict[str, HealthStatus]:
        """
        Verificar salud de todas las dependencias externas.

        Returns:
            Dict con nombre de dependencia → HealthStatus.

        Soberanía: Si una dependencia no responde, marca como DOWN sin crashear.
                   Alternativa: health checks via curl en bash.
        """
        import httpx

        results: dict[str, HealthStatus] = {}

        for name, dep in self._dependencies.items():
            try:
                status = await self._check_single(dep)
                dep.health = status
                dep.last_checked = datetime.now(timezone.utc).isoformat()
                results[name] = status

                # Persistir en Supabase si disponible
                if self._supabase:
                    try:
                        self._supabase.table("dependency_health").insert({
                            "dependency_name": name,
                            "status": status.value,
                            "checked_at": dep.last_checked,
                        }).execute()
                    except Exception:
                        pass  # Persistencia es opcional

            except Exception as e:
                dep.health = HealthStatus.DOWN
                results[name] = HealthStatus.DOWN
                logger.warning(
                    "health_check_fallido",
                    dependencia=name,
                    error=str(e),
                    sugerencia="Verificar conectividad de red y credenciales",
                )

        logger.info(
            "health_check_completado",
            total=len(results),
            healthy=sum(1 for s in results.values() if s == HealthStatus.HEALTHY),
            down=sum(1 for s in results.values() if s == HealthStatus.DOWN),
        )
        return results

    async def _check_single(self, dep: ExternalDependency) -> HealthStatus:
        """
        Verificar salud de una dependencia individual.

        Args:
            dep: Dependencia a verificar.

        Returns:
            HealthStatus de la dependencia.
        """
        env_key = dep.endpoint
        if not os.getenv(env_key) and not os.getenv(env_key.replace("_KEY", "_URL")):
            return HealthStatus.UNKNOWN

        checks = {
            "supabase": self._check_supabase,
            "openai": self._check_openai,
            "langfuse": self._check_langfuse,
        }

        checker = checks.get(dep.name)
        if checker:
            return await checker()

        return HealthStatus.HEALTHY

    async def _check_supabase(self) -> HealthStatus:
        """Health check específico para Supabase."""
        try:
            if self._supabase:
                self._supabase.table("health_check").select("*").limit(1).execute()
                return HealthStatus.HEALTHY
        except Exception:
            return HealthStatus.DEGRADED
        return HealthStatus.UNKNOWN

    async def _check_openai(self) -> HealthStatus:
        """Health check específico para OpenAI."""
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY', '')}"},
                    timeout=5.0,
                )
                return HealthStatus.HEALTHY if resp.status_code == 200 else HealthStatus.DEGRADED
        except Exception:
            return HealthStatus.DOWN

    async def _check_langfuse(self) -> HealthStatus:
        """Health check específico para Langfuse."""
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')}/api/public/health",
                    timeout=5.0,
                )
                return HealthStatus.HEALTHY if resp.status_code == 200 else HealthStatus.DEGRADED
        except Exception:
            return HealthStatus.DOWN

    def get_sovereignty_score(self) -> dict:
        """
        Calcular score de soberanía del sistema (0.0 a 1.0).

        Returns:
            Dict con overall_score, dimensions, total_monthly_cost,
            critical_dependencies, no_alternative.
        """
        total = len(self._dependencies)
        if total == 0:
            return {"overall_score": 0.0, "details": {}}

        scores = {
            "tiene_alternativa": sum(1 for d in self._dependencies.values() if d.self_hosted_alternative) / total,
            "datos_exportables": sum(1 for d in self._dependencies.values() if d.data_exported) / total,
            "api_compatible": sum(1 for d in self._dependencies.values() if d.api_compatible) / total,
            "tiene_migration_path": sum(1 for d in self._dependencies.values() if d.migration_path) / total,
        }

        overall = sum(scores.values()) / len(scores)

        return {
            "overall_score": round(overall, 2),
            "dimensiones": scores,
            "costo_mensual_total_usd": sum(d.monthly_cost_usd for d in self._dependencies.values()),
            "dependencias_criticas": [d.name for d in self._dependencies.values() if d.tier == DependencyTier.CRITICAL],
            "sin_alternativa": [d.name for d in self._dependencies.values() if not d.self_hosted_alternative],
        }

    def generate_sovereignty_report(self) -> str:
        """
        Generar reporte de soberanía legible.

        Returns:
            Reporte en formato Markdown.
        """
        score = self.get_sovereignty_score()

        report = f"""# El Monstruo — Sovereignty Report
Generado: {datetime.now(timezone.utc).isoformat()}

## Score de Soberanía General: {score['overall_score']*100:.0f}%

## Costo Mensual Externo: ${score['costo_mensual_total_usd']:.2f}

## Dependencias Críticas (el sistema falla sin estas):
"""
        for name in score["dependencias_criticas"]:
            dep = self._dependencies[name]
            report += f"- **{name}**: {dep.self_hosted_alternative}\n"
            report += f"  Migration: {dep.migration_path[:100]}...\n"

        report += "\n## Dimensiones de Soberanía:\n"
        for dim, val in score["dimensiones"].items():
            bar = "█" * int(val * 10) + "░" * (10 - int(val * 10))
            report += f"- {dim}: [{bar}] {val*100:.0f}%\n"

        return report

    async def activate_sovereign_mode(self) -> dict:
        """
        Activar modo soberano — redirigir todo a alternativas locales.

        Returns:
            Dict con acciones tomadas y features degradadas.

        Raises:
            SovereigntyEngineError: Si el modo soberano ya está activo.
        """
        if os.getenv("SOVEREIGN_MODE") == "true":
            raise SovereigntyEngineError(SOVEREIGNTY_ENGINE_MODO_SOBERANO_YA_ACTIVO)

        actions_taken = []

        os.environ["SOVEREIGN_MODE"] = "true"
        os.environ["LLM_FALLBACK_ONLY_LOCAL"] = "true"
        actions_taken.append("LLM routing redirigido a Ollama (local)")

        os.environ["DEEPL_ENABLED"] = "false"
        actions_taken.append("DeepL desactivado, usando traducción via LLM")

        logger.warning(
            "modo_soberano_activado",
            acciones=actions_taken,
            advertencia="Calidad de LLM puede ser menor con modelos locales",
        )

        return {
            "modo": "soberano",
            "acciones": actions_taken,
            "features_degradadas": [
                "Calidad de LLM puede ser menor (modelos locales)",
                "Calidad de traducción puede ser menor",
                "Tracing/observability limitado a logs locales",
            ],
        }

    def deactivate_sovereign_mode(self) -> dict:
        """
        Desactivar modo soberano — volver a servicios externos.

        Returns:
            Dict confirmando la desactivación.
        """
        os.environ.pop("SOVEREIGN_MODE", None)
        os.environ.pop("LLM_FALLBACK_ONLY_LOCAL", None)
        os.environ.pop("DEEPL_ENABLED", None)

        logger.info("modo_soberano_desactivado", mensaje="Volviendo a servicios externos")
        return {"modo": "normal", "mensaje": "Servicios externos restaurados"}

    def to_dict(self) -> dict:
        """
        Serializar estado para el Command Center.

        Returns:
            Dict con score, dependencias y modo actual.
        """
        score = self.get_sovereignty_score()
        return {
            "modulo": "sovereignty_engine",
            "sprint": "60.1",
            "objetivo": "Obj #12 — Ecosistema Soberano",
            "score_soberania": score["overall_score"],
            "costo_mensual_usd": score["costo_mensual_total_usd"],
            "total_dependencias": len(self._dependencies),
            "dependencias_criticas": score["dependencias_criticas"],
            "modo_soberano_activo": os.getenv("SOVEREIGN_MODE") == "true",
            "dependencias": {
                name: dep.to_dict()
                for name, dep in self._dependencies.items()
            },
        }


# ── Singleton ────────────────────────────────────────────────────────────────

_sovereignty_engine: Optional[SovereigntyEngine] = None


def get_sovereignty_engine() -> Optional[SovereigntyEngine]:
    """Obtener la instancia singleton del SovereigntyEngine."""
    return _sovereignty_engine


def init_sovereignty_engine(supabase=None) -> SovereigntyEngine:
    """
    Inicializar el SovereigntyEngine como singleton.

    Args:
        supabase: Cliente Supabase opcional para persistencia.

    Returns:
        Instancia inicializada del SovereigntyEngine.
    """
    global _sovereignty_engine
    _sovereignty_engine = SovereigntyEngine(_supabase=supabase)
    logger.info(
        "sovereignty_engine_listo",
        score=_sovereignty_engine.get_sovereignty_score()["overall_score"],
    )
    return _sovereignty_engine
