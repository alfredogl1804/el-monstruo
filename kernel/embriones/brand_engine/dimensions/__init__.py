"""Dimensiones canónicas del Brand Engine.

Cada dimensión es un evaluador especializado que recibe la respuesta candidata
y emite un ``DimensionResult`` con score numérico y veredicto binario contra
un umbral configurable.

Las 4 dimensiones canónicas (DSC-MO-006):

    D1 — Brand DNA tono (¿suena a Monstruo o a chatbot genérico?)
    D2 — Honestidad pura (¿admite lo que no sabe?)
    D3 — Consistencia doctrinal (¿contradice algún DSC firme?)
    D4 — Calidad Apple/Tesla (¿pasaría test "keynote-ready"?)

Naming canónico DSC-G-004: archivo por dimensión con nombre de dominio,
NO ``dimension_a.py`` / ``dimension_b.py`` / ``helper.py``.

PR-A definió la interfaz abstracta. PR-B agrega:

- Método ``evaluate_async()`` para uso desde el embrion_loop (que ya está en loop).
- ``BaseSabioDimension``: clase concreta que delega al Sabio configurado
  y comparte 95% del código entre las 4 dimensiones.

Spec: bridge/sprint_PAR_BICEFALO_001_brand_engine_spec_2026_05_11.md.
"""

from __future__ import annotations

import abc
import asyncio
import dataclasses
import logging
from typing import Optional

log = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class DimensionResult:
    """Resultado de evaluar una dimensión individual sobre una respuesta candidata.

    Atributos
    ---------
    score : float entre 0.0 (peor) y 1.0 (mejor).
    passed : bool — True si score >= umbral configurado en YAML.
    reason : razón estructurada cuando passed=False (None cuando passed=True).
    cost_usd : costo de la llamada al Sabio para esta dimensión.
    latency_ms : latencia de esta dimensión específica.
    """

    score: float
    passed: bool
    reason: Optional[str]
    cost_usd: float
    latency_ms: int


class DimensionEvaluator(abc.ABC):
    """Interfaz canónica para todas las dimensiones del Brand Engine.

    Cada dimensión concreta implementa ``evaluate(respuesta_candidata, criterios,
    umbral_pass)`` y opcionalmente ``evaluate_async(...)`` para uso desde código
    que ya corre dentro de un event loop (caso del ``embrion_loop.py``).

    PR-A solo exponía esta interfaz abstracta. PR-B agrega ``evaluate_async()``
    y la implementación concreta ``BaseSabioDimension``.
    """

    name: str = "DimensionEvaluator"

    @abc.abstractmethod
    def evaluate(
        self,
        respuesta_candidata: str,
        criterios: list[str],
        umbral_pass: float,
    ) -> DimensionResult:
        """Evalúa la respuesta contra los criterios y emite DimensionResult."""
        raise NotImplementedError

    async def evaluate_async(
        self,
        respuesta_candidata: str,
        criterios: list[str],
        umbral_pass: float,
    ) -> DimensionResult:
        """Variante async — default delega a ``evaluate()`` en thread pool.

        Subclases pueden override para invocar ``await router.execute(...)``
        directamente sin bloquear ni anidar event loops.
        """
        return await asyncio.to_thread(self.evaluate, respuesta_candidata, criterios, umbral_pass)


class BaseSabioDimension(DimensionEvaluator):
    """Implementación concreta que delega la evaluación al Sabio configurado.

    Comparte la lógica entre las 4 dimensiones: cada subclase solo aporta
    ``name`` canónico (D1, D2, D3, D4). El resto (prompt, router, fallback,
    parsing, scoring contra umbral) es común.

    El Sabio se invoca a través de ``kernel.embriones.brand_engine.sabio_evaluator``
    que a su vez usa ``router.engine.RouterEngine`` (patrón canónico del repo).

    Fail-open: cualquier excepción retorna score neutro 0.5 con ``passed=True``
    (no bloquea el embrión). El cost y latency se registran en todos los casos.
    """

    def __init__(
        self,
        evaluator_llm: str = "claude-opus-4-7",
        evaluator_fallback: Optional[str] = "claude-opus-4-6",
    ) -> None:
        self._evaluator_llm = evaluator_llm
        self._evaluator_fallback = evaluator_fallback

    def evaluate(
        self,
        respuesta_candidata: str,
        criterios: list[str],
        umbral_pass: float,
    ) -> DimensionResult:
        """Versión sync — envuelve el async con asyncio.run o thread.

        Si ya estamos en un event loop, esto fallaría — el caller debería usar
        ``evaluate_async`` directamente. Por eso esta implementación detecta
        y degrada a fail-open neutral cuando se llama mal.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # En event loop — no podemos asyncio.run; usuario debe llamar evaluate_async.
                log.warning(
                    "brand_engine_evaluate_called_inside_loop",
                    extra={"dim": self.name},
                )
                return DimensionResult(
                    score=0.5,
                    passed=True,
                    reason="evaluate() llamado dentro de event loop — use evaluate_async()",
                    cost_usd=0.0,
                    latency_ms=0,
                )
        except RuntimeError:
            # No hay loop activo — asyncio.run es seguro.
            pass

        return asyncio.run(self.evaluate_async(respuesta_candidata, criterios, umbral_pass))

    async def evaluate_async(
        self,
        respuesta_candidata: str,
        criterios: list[str],
        umbral_pass: float,
    ) -> DimensionResult:
        # Import diferido — evita cargar router en tests CI sin secrets.
        from kernel.embriones.brand_engine.sabio_evaluator import (
            evaluar_dimension_via_sabio,
        )

        evaluation = await evaluar_dimension_via_sabio(
            dim_name=self.name,
            respuesta_candidata=respuesta_candidata,
            criterios=criterios,
            evaluator_llm=self._evaluator_llm,
            evaluator_fallback=self._evaluator_fallback,
        )

        # Fail-open: si el Sabio devolvió error, marcamos passed=True con
        # score=score real pero la razón documenta el fail-open. El engine
        # global retorna APPROVED en estos casos (no bloquea por caída del
        # Sabio). El cost y latency se registran siempre.
        if evaluation.error is not None:
            log.warning(
                "brand_engine_dim_fail_open",
                extra={
                    "dim": self.name,
                    "error": evaluation.error,
                    "latency_ms": evaluation.latency_ms,
                },
            )
            return DimensionResult(
                score=evaluation.score,
                passed=True,  # fail-open absoluto.
                reason=None,
                cost_usd=evaluation.cost_usd,
                latency_ms=evaluation.latency_ms,
            )

        passed = evaluation.score >= umbral_pass
        reason = None if passed else evaluation.reason
        return DimensionResult(
            score=evaluation.score,
            passed=passed,
            reason=reason,
            cost_usd=evaluation.cost_usd,
            latency_ms=evaluation.latency_ms,
        )
