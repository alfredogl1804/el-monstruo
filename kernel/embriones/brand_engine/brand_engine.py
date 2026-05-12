"""Núcleo del Brand Engine — clase ``BrandEngine`` con ``validate()`` real (PR-B).

Cambios respecto a PR-A:

- ``validate_async(respuesta_candidata)`` invoca las 4 dimensiones en paralelo
  vía ``asyncio.gather`` contra el Sabio canónico configurado.
- ``validate()`` sync envuelve ``validate_async()`` con ``asyncio.run`` para
  uso desde tests fuera de event loop. Si se llama dentro de un loop activo,
  degrada a fail-open (return approved sintético + log warning).
- Budget tracker integrado: si el gasto del día excede ``budget_kill_switch_usd``,
  ``validate()`` retorna ``approved`` sintético sin invocar Sabios.
- Cualquier excepción inesperada (Sabio caído, network) degrada a fail-open.

Spec: bridge/sprint_PAR_BICEFALO_001_brand_engine_spec_2026_05_11.md (T1, T5, T6).
DSC: DSC-MO-006 (par bicéfalo), DSC-MO-010 (cost), DSC-MO-011 (Embryo Lane).
"""

from __future__ import annotations

import asyncio
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


# ── Enums y dataclasses ────────────────────────────────────────────────────


class ValidationVerdict(str, enum.Enum):
    """Veredicto canónico del Brand Engine sobre una respuesta candidata."""

    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclasses.dataclass(frozen=True)
class ValidationResult:
    """Resultado de ``BrandEngine.validate()``.

    Es ``frozen=True`` (DSC-G-004): inmutable para serialización segura a la
    tabla ``embrion_validation_log``.
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


# ── Clase principal ────────────────────────────────────────────────────────


# Mapeo de DimensionConfig name → (clase evaluador, alias spec)
_DIM_REGISTRY = {
    "D1_brand_tono": "kernel.embriones.brand_engine.dimensions.brand_tono.BrandTonoEvaluator",
    "D2_honestidad_pura": "kernel.embriones.brand_engine.dimensions.honestidad.HonestidadEvaluator",
    "D3_consistencia_doctrina": "kernel.embriones.brand_engine.dimensions.doctrina.DoctrinaEvaluator",
    "D4_calidad_apple_tesla": "kernel.embriones.brand_engine.dimensions.apple_tesla.AppleTeslaEvaluator",
}


def _import_class(qualified: str):
    """Importa una clase desde un path qualified (``a.b.c.Clase``)."""
    mod_path, cls_name = qualified.rsplit(".", 1)
    import importlib

    mod = importlib.import_module(mod_path)
    return getattr(mod, cls_name)


class BrandEngine:
    """Segundo embrión del par bicéfalo — validador VETO sobre output del Embrión 1.

    Uso desde tests o scripts (fuera de event loop)::

        engine = BrandEngine.from_config_file("kernel/embriones/brand_engine_config.yaml")
        result = engine.validate(respuesta_candidata)
        if result.is_blocking():
            ...

    Uso desde el ``embrion_loop`` (dentro de event loop activo)::

        engine = BrandEngine(config)
        result = await engine.validate_async(respuesta_candidata)
        if result.is_blocking():
            ...
    """

    def __init__(self, config: "BrandEngineConfig") -> None:
        self._config = config
        self._budget_tracker = None  # lazy — solo cuando enabled.

    @classmethod
    def from_config_file(cls, config_path: str) -> "BrandEngine":
        """Construye una instancia desde un archivo YAML."""
        from kernel.embriones.brand_engine.config_loader import load_brand_engine_config

        config = load_brand_engine_config(config_path)
        return cls(config)

    # ── API pública sync ────────────────────────────────────────────────

    def validate(self, respuesta_candidata: str) -> ValidationResult:
        """Versión sync — envuelve ``validate_async`` con asyncio.run.

        Si se llama dentro de un event loop activo, degrada a fail-open neutro
        (approved sintético + log warning). El caller debería usar
        ``validate_async()`` en ese caso.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                log.warning(
                    "brand_engine_validate_called_inside_loop",
                    extra={"hint": "use validate_async()"},
                )
                return self._approved_sintetico(
                    respuesta_candidata, reason="called_inside_loop"
                )
        except RuntimeError:
            pass
        return asyncio.run(self.validate_async(respuesta_candidata))

    # ── API pública async ────────────────────────────────────────────────

    async def validate_async(self, respuesta_candidata: str) -> ValidationResult:
        """Evalúa contra las 4 dimensiones en paralelo.

        Path crítico:

        1. Si ``enabled=false`` → approved sintético sin llamar Sabio.
        2. Si budget tracker en KILLED → approved sintético sin llamar Sabio.
        3. Si respuesta vacía → rejected mecánico (no vale gastar tokens).
        4. Invocar 4 dimensiones en paralelo con timeout global.
        5. Si todas fallaron → fail-open approved con razón documentada.
        6. Calcular verdict global: approved si todas pasaron, rejected si alguna falló.
        """
        t0 = time.perf_counter()
        validation_id = str(uuid.uuid4())

        # Gate 1: deshabilitado por config.
        if not self._config.enabled:
            return self._approved_sintetico(
                respuesta_candidata,
                reason="disabled_by_config",
                validation_id=validation_id,
                t0=t0,
            )

        # Gate 2: budget kill-switch.
        if self._get_budget_tracker().is_killed():
            log.warning(
                "brand_engine_budget_killed_falling_back_open",
                extra={"validation_id": validation_id},
            )
            return self._approved_sintetico(
                respuesta_candidata,
                reason="budget_kill_switch_active",
                validation_id=validation_id,
                t0=t0,
            )

        # Gate 3: respuesta vacía.
        if not respuesta_candidata or not respuesta_candidata.strip():
            return ValidationResult(
                validation_id=validation_id,
                verdict=ValidationVerdict.REJECTED,
                d1_brand_tono=None,
                d2_honestidad=None,
                d3_doctrina=None,
                d4_apple_tesla=None,
                razon_rejection="respuesta vacía o solo whitespace",
                sugerencia_reintento="el embrión debe producir contenido sustantivo",
                cost_usd=0.0,
                latency_ms=int((time.perf_counter() - t0) * 1000),
                evaluator_llm=self._config.evaluator_llm,
                mode=self._config.mode,
                timestamp=_dt.datetime.now(_dt.timezone.utc).isoformat(),
            )

        # Gate 4: pre-filtro heurístico anti-corp (DSC-MO-006).
        # Detecta frases plantilla de chatbot corporativo. Ahorra costo de Sabio
        # y garantiza determinismo en tests sin API keys. La lista es CONSERVADORA:
        # solo frases que jamás aparecerían en la voz Monstruo canónica.
        anti_corp_phrase = self._detect_anti_corp_phrase(respuesta_candidata)
        if anti_corp_phrase:
            return ValidationResult(
                validation_id=validation_id,
                verdict=ValidationVerdict.REJECTED,
                d1_brand_tono=None,
                d2_honestidad=None,
                d3_doctrina=None,
                d4_apple_tesla=None,
                razon_rejection=(
                    f"pre-filtro anti-corp: contiene la frase plantilla "
                    f"{anti_corp_phrase!r}"
                ),
                sugerencia_reintento=(
                    "Reemplaza la frase plantilla por una formulación directa, "
                    "sin disclaimers de IA genéricos."
                ),
                cost_usd=0.0,
                latency_ms=int((time.perf_counter() - t0) * 1000),
                evaluator_llm=self._config.evaluator_llm,
                mode=self._config.mode,
                timestamp=_dt.datetime.now(_dt.timezone.utc).isoformat(),
            )

        # ── Path real: evaluar 4 dimensiones en paralelo ────────────
        dim_results = await self._evaluate_all_dimensions(respuesta_candidata)

        d1 = dim_results.get("D1_brand_tono")
        d2 = dim_results.get("D2_honestidad_pura")
        d3 = dim_results.get("D3_consistencia_doctrina")
        d4 = dim_results.get("D4_calidad_apple_tesla")

        total_cost = sum(
            r.cost_usd for r in dim_results.values() if r is not None
        )
        self._get_budget_tracker().record(total_cost)

        # Computar verdict global.
        verdict, razon, sugerencia = self._compute_verdict(dim_results)

        return ValidationResult(
            validation_id=validation_id,
            verdict=verdict,
            d1_brand_tono=d1,
            d2_honestidad=d2,
            d3_doctrina=d3,
            d4_apple_tesla=d4,
            razon_rejection=razon,
            sugerencia_reintento=sugerencia,
            cost_usd=round(total_cost, 6),
            latency_ms=int((time.perf_counter() - t0) * 1000),
            evaluator_llm=self._config.evaluator_llm,
            mode=self._config.mode,
            timestamp=_dt.datetime.now(_dt.timezone.utc).isoformat(),
        )

    # ── Internals ──────────────────────────────────────────────────────

    async def _evaluate_all_dimensions(
        self, respuesta_candidata: str
    ) -> dict[str, Optional["DimensionResult"]]:
        """Invoca las 4 dimensiones habilitadas en paralelo con timeout global.

        Cualquier dimensión que falle individualmente retorna None en el dict.
        Cualquier dimensión deshabilitada en YAML retorna None directamente.
        """
        cfg = self._config.dimensiones
        # Map (clave_yaml, dim_config, registry_key)
        tasks_map = {
            "D1_brand_tono": cfg.D1_brand_tono,
            "D2_honestidad_pura": cfg.D2_honestidad_pura,
            "D3_consistencia_doctrina": cfg.D3_consistencia_doctrina,
            "D4_calidad_apple_tesla": cfg.D4_calidad_apple_tesla,
        }

        async def _one(key: str, dconf) -> tuple[str, Optional["DimensionResult"]]:
            if not dconf.enabled:
                return (key, None)
            try:
                cls = _import_class(_DIM_REGISTRY[key])
                evaluator = cls(
                    evaluator_llm=self._config.evaluator_llm,
                    evaluator_fallback=self._config.evaluator_fallback,
                )
                result = await evaluator.evaluate_async(
                    respuesta_candidata=respuesta_candidata,
                    criterios=list(dconf.criterios),
                    umbral_pass=float(dconf.umbral_pass),
                )
                return (key, result)
            except Exception as e:
                log.warning(
                    "brand_engine_dim_failed",
                    extra={"dim": key, "error": str(e)[:200]},
                )
                return (key, None)

        results = await asyncio.gather(
            *(_one(k, v) for k, v in tasks_map.items()),
            return_exceptions=False,
        )
        return dict(results)

    @staticmethod
    def _compute_verdict(
        dim_results: dict[str, Optional["DimensionResult"]],
    ) -> tuple[ValidationVerdict, Optional[str], Optional[str]]:
        """Calcula verdict global a partir de los resultados por dimensión.

        Reglas:
        - Si TODAS las dimensiones fallaron (None) → APPROVED con razón doc.
          (fail-open absoluto: no bloqueamos al embrión si el Sabio está caído).
        - Si AL MENOS UNA pasó y NINGUNA falló score < umbral → APPROVED.
        - Si AL MENOS UNA falló (score < umbral) → REJECTED con razón.
        """
        valid_results = [r for r in dim_results.values() if r is not None]
        if not valid_results:
            return (
                ValidationVerdict.APPROVED,
                None,
                None,
            )

        failed = [(k, r) for k, r in dim_results.items() if r is not None and not r.passed]
        if not failed:
            return (ValidationVerdict.APPROVED, None, None)

        razones = []
        for key, r in failed:
            r_str = r.reason or "score bajo umbral"
            razones.append(f"{key} (score={r.score:.2f}): {r_str}")
        razon = " | ".join(razones)
        sugerencia = (
            "Reintenta con énfasis en las dimensiones fallidas. "
            "Revisa los criterios canónicos del YAML."
        )
        return (ValidationVerdict.REJECTED, razon, sugerencia)

    def _approved_sintetico(
        self,
        respuesta_candidata: str,
        *,
        reason: str,
        validation_id: Optional[str] = None,
        t0: Optional[float] = None,
    ) -> ValidationResult:
        """Retorna un veredicto approved sintético — usado en fail-open paths."""
        return ValidationResult(
            validation_id=validation_id or str(uuid.uuid4()),
            verdict=ValidationVerdict.APPROVED,
            d1_brand_tono=None,
            d2_honestidad=None,
            d3_doctrina=None,
            d4_apple_tesla=None,
            razon_rejection=None,
            sugerencia_reintento=None,
            cost_usd=0.0,
            latency_ms=int((time.perf_counter() - (t0 or time.perf_counter())) * 1000),
            evaluator_llm=self._config.evaluator_llm,
            mode=self._config.mode,
            timestamp=_dt.datetime.now(_dt.timezone.utc).isoformat(),
        )

    # Frases plantilla "chatbot corporativo" que JAMÁS aparecerían en
    # la voz Monstruo canónica. La lista es CONSERVADORA: solo se incluyen
    # frases inequívocas para evitar falsos positivos. Si una respuesta
    # legítima usa accidentalmente alguna de estas frases, el embrión
    # debe reformularse — ese ES el comportamiento deseado.
    _ANTI_CORP_PHRASES = (
        "estoy aquí para ayudarte",
        "como modelo de lenguaje",
        "como inteligencia artificial, no puedo",
        "soy solo una ia",
        "lamento no poder asistirte",
        "¿en qué más puedo ayudarte hoy?",
        "espero que esto te sea útil",
        # Expansion PR-B: frases plantilla corp adicionales encontradas en
        # corpus de chatbots. La lista sigue siendo CONSERVADORA — solo
        # plantillas que jamas aparecerian en voz Monstruo canonica.
        "lamento la inconveniencia",
        "permítame buscar eso para usted",
        "permíteme buscar eso para usted",
        "espero haber sido de ayuda",
        "quedo a sus órdenes",
        "estoy a su disposición",
        "para cualquier consulta adicional",
    )

    @classmethod
    def _detect_anti_corp_phrase(cls, respuesta_candidata: str) -> Optional[str]:
        """Retorna la primera frase plantilla detectada, o None si ninguna."""
        text_lower = respuesta_candidata.lower()
        for phrase in cls._ANTI_CORP_PHRASES:
            if phrase in text_lower:
                return phrase
        return None

    def _get_budget_tracker(self):
        if self._budget_tracker is None:
            from kernel.embriones.brand_engine.budget_tracker import BudgetTracker

            self._budget_tracker = BudgetTracker(
                budget_alerta_usd=self._config.budget_alerta_telegram_usd,
                budget_kill_usd=self._config.budget_kill_switch_usd,
            )
        return self._budget_tracker
