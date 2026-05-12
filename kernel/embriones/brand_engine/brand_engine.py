"""BrandEngine — núcleo del segundo embrión del par bicéfalo.

Recibe una respuesta candidata del Embrión 1 y emite un veredicto VETO
(`approved` | `rejected` | `timeout` | `error`) basado en evaluación
multidimensional contra el Brand DNA canónico del Monstruo.

NO genera contenido. NO decide qué decir. NO cura memoria.
SOLO filtra calidad de output ya producido por otro Embrión.

Modos operativos (via config YAML):
    shadow   — loguea veredicto pero NO bloquea output (default seguro).
    enforce  — veredicto vincula: rejected fuerza reintento o silencio_brand_veto.

Doctrina de fail-open:
    Si BrandEngine lanza excepción interna NO bloquea el flujo del Embrión 1.
    El hook en embrion_loop.py captura cualquier raise y deja pasar el output
    con tag `brand_engine_error` para auditoría posterior.

Spec: bridge/sprint_PAR_BICEFALO_001_brand_engine_spec_2026_05_11.md
"""

from __future__ import annotations

import dataclasses
import datetime as _dt
import enum
import logging
import time
import uuid
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from kernel.embriones.brand_engine.config_loader import BrandEngineConfig
    from kernel.embriones.brand_engine.dimensions import DimensionResult

log = logging.getLogger(__name__)


class ValidationVerdict(str, enum.Enum):
    """Veredicto final del Brand Engine sobre una respuesta candidata."""

    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclasses.dataclass(frozen=True)
class ValidationResult:
    """Resultado completo de la validación 4D sobre una respuesta candidata.

    Atributos
    ---------
    validation_id : UUID emitido por Brand Engine para trazabilidad.
    verdict : ``approved`` | ``rejected`` | ``timeout`` | ``error``.
    d1_brand_tono : DimensionResult de la dimensión 1 (puede ser None si dim deshabilitada).
    d2_honestidad : DimensionResult de la dimensión 2.
    d3_doctrina : DimensionResult de la dimensión 3.
    d4_apple_tesla : DimensionResult de la dimensión 4.
    razon_rejection : razón estructurada (None si verdict=approved).
    sugerencia_reintento : prompt-fragment para que Embrión 1 reintente (None si approved).
    cost_usd : costo agregado de las 4 llamadas al Sabio evaluador.
    latency_ms : latencia total de la validación end-to-end.
    evaluator_llm : identificador del modelo usado (ej. ``claude-opus-4-7``).
    mode : ``shadow`` o ``enforce`` (heredado de config en momento de evaluación).
    timestamp : UTC ISO 8601 del momento de evaluación.
    """

    validation_id: str
    verdict: ValidationVerdict
    d1_brand_tono: Optional["DimensionResult"]
    d2_honestidad: Optional["DimensionResult"]
    d3_doctrina: Optional["DimensionResult"]
    d4_apple_tesla: Optional["DimensionResult"]
    razon_rejection: Optional[str]
    sugerencia_reintento: Optional[str]
    cost_usd: float
    latency_ms: int
    evaluator_llm: str
    mode: str
    timestamp: str

    def is_blocking(self) -> bool:
        """True si este veredicto debe bloquear el output (sólo en mode=enforce)."""
        return self.mode == "enforce" and self.verdict == ValidationVerdict.REJECTED


class BrandEngine:
    """Segundo embrión del par bicéfalo. Validador VETO sobre output del Embrión 1.

    Uso típico (post-merge T4 hook, no en T1-T3)::

        engine = BrandEngine.from_config_file("kernel/embriones/brand_engine_config.yaml")
        result = engine.validate(respuesta_candidata)
        if result.is_blocking():
            # Reintento o silencio_brand_veto
            ...

    En T1-T3 (PR-A) el método ``validate()`` retorna un stub estructurado que
    permite tests de scaffolding sin tocar LLM real. T4-T6 (PR-B) implementan
    el wiring real con Anthropic SDK + dimensiones reales.
    """

    def __init__(self, config: "BrandEngineConfig") -> None:
        self._config = config
        self._scaffold_mode = True  # PR-A: aún no hay wiring LLM real.

    @classmethod
    def from_config_file(cls, config_path: str) -> "BrandEngine":
        """Construye una instancia desde un archivo YAML."""
        from kernel.embriones.brand_engine.config_loader import load_brand_engine_config

        config = load_brand_engine_config(config_path)
        return cls(config)

    def validate(self, respuesta_candidata: str) -> ValidationResult:
        """Evalúa la respuesta candidata contra las 4 dimensiones.

        En PR-A (scaffolding) este método retorna un veredicto sintético basado
        únicamente en señales mecánicas (longitud, naming prohibido, etc.) para
        permitir tests de estructura sin LLM. PR-B reemplazará con evaluación
        real vía Sabio.
        """
        t0 = time.perf_counter()
        validation_id = str(uuid.uuid4())

        if not self._config.enabled:
            log.debug("BrandEngine deshabilitado por config — retorna approved sintético")
            return ValidationResult(
                validation_id=validation_id,
                verdict=ValidationVerdict.APPROVED,
                d1_brand_tono=None,
                d2_honestidad=None,
                d3_doctrina=None,
                d4_apple_tesla=None,
                razon_rejection=None,
                sugerencia_reintento=None,
                cost_usd=0.0,
                latency_ms=int((time.perf_counter() - t0) * 1000),
                evaluator_llm=self._config.evaluator_llm,
                mode=self._config.mode,
                timestamp=_dt.datetime.now(_dt.timezone.utc).isoformat(),
            )

        if self._scaffold_mode:
            # PR-A: heurística mecánica mínima para tests de estructura.
            # PR-B reemplaza esto con llamadas reales a las 4 dimensiones.
            verdict = self._scaffold_heuristic(respuesta_candidata)
            return ValidationResult(
                validation_id=validation_id,
                verdict=verdict,
                d1_brand_tono=None,
                d2_honestidad=None,
                d3_doctrina=None,
                d4_apple_tesla=None,
                razon_rejection=(
                    "scaffold_mode: heurística mecánica detectó issue"
                    if verdict == ValidationVerdict.REJECTED
                    else None
                ),
                sugerencia_reintento=None,
                cost_usd=0.0,
                latency_ms=int((time.perf_counter() - t0) * 1000),
                evaluator_llm=self._config.evaluator_llm,
                mode=self._config.mode,
                timestamp=_dt.datetime.now(_dt.timezone.utc).isoformat(),
            )

        # Branch real (PR-B) — placeholder NotImplementedError para forzar
        # implementación explícita y no fallar silenciosamente.
        raise NotImplementedError(
            "Real LLM-backed validation arrives in PR-B (T4-T6). "
            "Current PR-A only exposes scaffolding."
        )

    @staticmethod
    def _scaffold_heuristic(respuesta_candidata: str) -> ValidationVerdict:
        """Heurística mecánica de PR-A — NO refleja calidad real, solo estructura.

        Reglas mínimas para que tests determinísticos puedan ejercer la ruta
        approved/rejected sin LLM:
          - Vacío o solo whitespace → rejected.
          - Contiene literalmente "estoy aquí para ayudarte" → rejected (anti-corp).
          - En cualquier otro caso → approved.
        """
        if not respuesta_candidata or not respuesta_candidata.strip():
            return ValidationVerdict.REJECTED
        if "estoy aquí para ayudarte" in respuesta_candidata.lower():
            return ValidationVerdict.REJECTED
        return ValidationVerdict.APPROVED
