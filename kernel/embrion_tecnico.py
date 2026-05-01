"""
embrion_tecnico.py — Embrión-Técnico: Especialista en Arquitectura y DevOps
=============================================================================
Segundo Embrión especializado del Objetivo #11 (Multiplicación de Embriones).

RESPONSABILIDAD: Evalúa y mejora la calidad técnica de todos los proyectos
que El Monstruo crea. Nunca entrega código que no pasaría un code review serio.

Tareas autónomas (5 tareas, registradas en EmbrionScheduler):
  - architecture_audit: Audita arquitectura de proyectos activos (cada 24h)
  - dependency_scan: Escanea vulnerabilidades en dependencias (cada 12h)
  - performance_check: Verifica métricas de performance (cada 6h)
  - code_quality_review: Review de calidad en últimos commits (cada 8h)
  - infra_cost_audit: Audita costos de infraestructura (cada 48h)

Soberanía:
  - Code analysis: Python AST (built-in) → sin dependencia externa
  - Vulnerability DB: PyPI Advisory DB via httpx → alternativa: safety-db local
  - Performance metrics: httpx para health checks → alternativa: aiohttp

Sprint 58 — "La Fortaleza Completa"
Obj #11 — Embrión especializado #2
"""
from __future__ import annotations

import re
import ast
import structlog
from datetime import datetime, timezone
from typing import Any, Optional

from kernel.embrion_loop import EmbrionLoop

logger = structlog.get_logger("embrion.tecnico")


# ─── Errores con identidad (Brand Check #2) ──────────────────────────────────

class EmbrionTecnicoError(Exception):
    """Error base del Embrión-Técnico."""
    pass


class EMBRION_TECNICO_PROYECTO_VACIO(EmbrionTecnicoError):
    """La estructura del proyecto está vacía. Proporciona un dict con 'files' como lista."""
    pass


class EMBRION_TECNICO_CODIGO_INVALIDO(EmbrionTecnicoError):
    """El código proporcionado no es Python válido y no puede ser analizado."""
    pass


# ─── Clase principal ─────────────────────────────────────────────────────────

class EmbrionTecnico(EmbrionLoop):
    """
    Embrión especializado en arquitectura de software, DevOps y code quality.

    Hereda de EmbrionLoop para participar en el ciclo autónomo del sistema.
    Evalúa la calidad técnica de proyectos generados por El Monstruo.

    Attributes:
        EMBRION_ID: Identificador único del Embrión en el sistema A2A.
        SPECIALIZATION: Especialización para el A2A Registry.
        SYSTEM_PROMPT: Prompt de sistema que define el expertise del Embrión.
        DEFAULT_TASKS: 5 tareas autónomas registradas en el EmbrionScheduler.
    """

    EMBRION_ID = "embrion-tecnico"
    SPECIALIZATION = "tecnico"

    SYSTEM_PROMPT = """Eres Embrión-Técnico, el especialista en arquitectura de software
    y DevOps de El Monstruo. Tu expertise:

    1. ARQUITECTURA: Microservicios, monolitos modulares, event-driven, CQRS
    2. CODE QUALITY: SOLID, DRY, KISS, clean code, design patterns
    3. DEVOPS: CI/CD, Docker, Kubernetes, infrastructure as code
    4. PERFORMANCE: Profiling, optimization, caching, database tuning
    5. SECURITY: OWASP Top 10, dependency scanning, secret management
    6. SCALABILITY: Horizontal scaling, load balancing, auto-scaling

    Principios irrenunciables:
    - Simplicidad sobre complejidad. El mejor código es el que no existe.
    - Pragmatismo sobre purismo. Ship fast, refactor later.
    - Observabilidad. Si no puedes medirlo, no puedes mejorarlo.
    - Seguridad por defecto. Nunca opt-in, siempre opt-out.
    - Tests primero. Código sin tests es deuda técnica, no código.
    """

    DEFAULT_TASKS = {
        "architecture_audit": {
            "description": "Auditar arquitectura de proyectos activos",
            "interval_hours": 24,
            "max_cost_usd": 0.25,
            "priority": 2,
        },
        "dependency_scan": {
            "description": "Escanear vulnerabilidades en dependencias",
            "interval_hours": 12,
            "max_cost_usd": 0.10,
            "priority": 1,
        },
        "performance_check": {
            "description": "Verificar métricas de performance",
            "interval_hours": 6,
            "max_cost_usd": 0.10,
            "priority": 1,
        },
        "code_quality_review": {
            "description": "Review de calidad de código en últimos commits",
            "interval_hours": 8,
            "max_cost_usd": 0.20,
            "priority": 2,
        },
        "infra_cost_audit": {
            "description": "Auditar costos de infraestructura",
            "interval_hours": 48,
            "max_cost_usd": 0.15,
            "priority": 3,
        },
    }

    def __init__(
        self,
        db: Any = None,
        kernel: Any = None,
        notifier: Optional[Any] = None,
        search_fn=None,
    ):
        """
        Inicializar Embrión-Técnico.

        Args:
            db: Conexión a base de datos (Supabase client).
            kernel: Referencia al kernel principal del sistema.
            notifier: Notificador para alertas (Telegram, etc.).
            search_fn: Función de búsqueda inyectada para research de CVEs.
        """
        super().__init__(db=db, kernel=kernel, notifier=notifier)
        self._search = search_fn
        logger.info(
            "embrion_tecnico_inicializado",
            embrion_id=self.EMBRION_ID,
            tasks_count=len(self.DEFAULT_TASKS),
        )

    async def audit_architecture(self, project_structure: dict) -> dict:
        """
        Auditar arquitectura de un proyecto.

        Args:
            project_structure: Dict con 'files' (lista de rutas) y 'metadata' opcional.

        Returns:
            Dict con score (0-100), grade, issues y recommendations.

        Raises:
            EMBRION_TECNICO_PROYECTO_VACIO: Si project_structure no tiene 'files'.
        """
        files = project_structure.get("files", [])
        if not files:
            raise EMBRION_TECNICO_PROYECTO_VACIO(
                "La estructura del proyecto no tiene archivos. "
                "Proporciona un dict con 'files' como lista de rutas."
            )

        issues = []
        recommendations = []
        score = 100

        # Verificar cantidad de archivos
        if len(files) > 200:
            issues.append("Más de 200 archivos — considerar consolidación de módulos")
            score -= 5

        # Verificar tests
        test_files = [f for f in files if "test" in f.lower() or "spec" in f.lower()]
        test_ratio = len(test_files) / max(len(files), 1)
        if len(test_files) == 0:
            issues.append("CRÍTICO: Sin archivos de test — testing es obligatorio")
            score -= 20
        elif test_ratio < 0.1:
            issues.append(f"Cobertura de tests baja ({test_ratio:.1%}) — objetivo: >10%")
            score -= 10

        # Verificar .env en repo
        if ".env" in files:
            issues.append("CRÍTICO: .env en el repositorio — secretos expuestos")
            score -= 30

        # Verificar Dockerfile
        if "Dockerfile" not in files and "docker-compose.yml" not in files:
            recommendations.append("Agregar Dockerfile para deployments consistentes")

        # Verificar CI/CD
        ci_files = [
            f for f in files
            if ".github/workflows" in f or "Jenkinsfile" in f or ".gitlab-ci" in f
        ]
        if not ci_files:
            recommendations.append("Agregar pipeline CI/CD para testing automatizado")
            score -= 5

        # Verificar README
        readme_files = [f for f in files if "README" in f.upper()]
        if not readme_files:
            recommendations.append("Agregar README.md con instrucciones de setup")
            score -= 3

        # Grade
        if score >= 90:
            grade = "excelente"
        elif score >= 70:
            grade = "bueno"
        elif score >= 50:
            grade = "necesita_mejora"
        else:
            grade = "critico"

        result = {
            "score": max(0, score),
            "grade": grade,
            "issues": issues,
            "recommendations": recommendations,
            "files_analyzed": len(files),
            "test_coverage_ratio": round(test_ratio, 3),
            "embrion_id": self.EMBRION_ID,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(
            "architecture_audit_completado",
            score=result["score"],
            grade=grade,
            issues_count=len(issues),
        )
        return result

    async def review_code_quality(self, code: str, language: str = "python") -> dict:
        """
        Review de calidad de código.

        Args:
            code: Código fuente a analizar.
            language: Lenguaje del código ("python", "javascript", etc.).

        Returns:
            Dict con quality_score, issues y lines_analyzed.

        Raises:
            EMBRION_TECNICO_CODIGO_INVALIDO: Si el código Python no puede ser parseado.

        Soberanía: Python AST (built-in) para análisis estático — sin dependencia externa.
        """
        if not code.strip():
            return {"quality_score": 0, "issues": ["Código vacío"], "lines_analyzed": 0}

        issues = []
        lines = code.split("\n")

        # Verificar longitud de líneas
        long_lines = [i + 1 for i, line in enumerate(lines) if len(line) > 120]
        if long_lines:
            issues.append(f"Líneas >120 chars en: {long_lines[:5]}")

        # Verificar TODOs sin resolver
        todos = [
            i + 1 for i, line in enumerate(lines)
            if any(t in line.upper() for t in ["TODO", "FIXME", "HACK", "XXX"])
        ]
        if todos:
            issues.append(f"TODOs/FIXMEs sin resolver en líneas: {todos[:5]}")

        # Verificar secretos hardcodeados
        secret_patterns = [
            r'(api_key|apikey|secret|password|token)\s*=\s*["\'][^"\']{8,}["\']',
            r'sk_live_[a-zA-Z0-9]+',
            r'AKIA[A-Z0-9]{16}',
        ]
        for pattern in secret_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append("CRÍTICO: Posible secreto hardcodeado detectado")
                break

        # Análisis AST para Python
        if language == "python":
            try:
                tree = ast.parse(code)
                # Verificar funciones muy largas (>50 líneas)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        func_lines = getattr(node, "end_lineno", 0) - node.lineno
                        if func_lines > 50:
                            issues.append(
                                f"Función '{node.name}' muy larga ({func_lines} líneas) — "
                                f"considera dividirla"
                            )
            except SyntaxError as e:
                raise EMBRION_TECNICO_CODIGO_INVALIDO(
                    f"El código Python no puede ser analizado: {e}. "
                    f"Verifica la sintaxis antes de hacer review."
                )

        quality_score = max(0, 100 - len(issues) * 10)

        return {
            "quality_score": quality_score,
            "issues": issues,
            "lines_analyzed": len(lines),
            "language": language,
            "embrion_id": self.EMBRION_ID,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def recommend_stack(self, requirements: dict) -> dict:
        """
        Recomendar stack técnico basado en requerimientos del proyecto.

        Args:
            requirements: Dict con 'type' (web_app/api), 'expected_users' y
                          'monthly_budget_usd'.

        Returns:
            Dict con stack recomendado y justificación.
        """
        project_type = requirements.get("type", "web_app")
        scale = requirements.get("expected_users", 1000)
        budget = requirements.get("monthly_budget_usd", 100)

        if project_type == "web_app" and scale < 10_000:
            stack = {
                "frontend": "React + Vite + Tailwind CSS",
                "backend": "FastAPI (Python 3.11+)",
                "database": "PostgreSQL (Supabase)",
                "hosting": "Vercel (frontend) + Railway (backend)",
                "cache": "Upstash Redis" if scale > 1000 else "In-memory",
                "ci_cd": "GitHub Actions",
                "monitoring": "Sentry + Langfuse",
                "costo_estimado": f"${min(budget, 50)}/mes",
                "justificacion": "Optimizado para velocidad de desarrollo y costo en esta escala",
            }
        elif project_type == "api" or scale >= 10_000:
            stack = {
                "frontend": "N/A (solo API)" if project_type == "api" else "Next.js",
                "backend": "FastAPI (Python 3.11+) con async workers",
                "database": "PostgreSQL con read replicas",
                "hosting": "AWS ECS o GCP Cloud Run",
                "cache": "Upstash Redis + CDN edge caching",
                "ci_cd": "GitHub Actions + ArgoCD",
                "monitoring": "Sentry + Datadog + Langfuse",
                "costo_estimado": f"${min(budget, 200)}/mes",
                "justificacion": "Diseñado para escalamiento horizontal y alta disponibilidad",
            }
        else:
            stack = {
                "error": "Tipo de proyecto no soportado",
                "tipos_soportados": ["web_app", "api"],
            }

        stack["embrion_id"] = self.EMBRION_ID
        stack["timestamp"] = datetime.now(timezone.utc).isoformat()
        return stack

    def to_dict(self) -> dict:
        """
        Serializar estado del Embrión-Técnico para el Command Center.

        Returns:
            Dict con estado actual consumible por el Command Center.
        """
        return {
            "embrion_id": self.EMBRION_ID,
            "specialization": self.SPECIALIZATION,
            "version": "58.4",
            "tasks_autonomas": list(self.DEFAULT_TASKS.keys()),
            "estado": "activo" if self._running else "inactivo",
            "ciclos_completados": self._cycle_count,
            "costo_hoy_usd": self._cost_today_usd,
        }
