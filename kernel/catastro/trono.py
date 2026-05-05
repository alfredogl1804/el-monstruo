"""
El Catastro · Trono Score Calculator (Sprint 86 Bloque 4).

Calcula el Trono Score por dominio usando z-scores normalizados intra-dominio
y suma ponderada con los pesos canónicos del SPEC sección 4:

    trono_global = round(base + scale * Σ(w_i · z_i), 2)
    z_i          = (x_i - mean_d.x_i) / std_d.x_i
    pesos        = {Q: 0.40, CE: 0.25, S: 0.15, R: 0.10, BF: 0.10}
    base         = 50.00      (media del dominio)
    scale        = 10.00      (1σ ≈ 10 puntos)
    rango        = [0, 100]   (clampeado, consistente con NUMERIC(5,2))

Espejo Python EXACTO de la función PL/pgSQL `catastro_recompute_trono(text)`
en `scripts/019_sprint86_catastro_trono.sql`. Si una de las dos fórmulas
cambia, AMBAS deben actualizarse y los tests del Bloque 4 lo deben capturar.

Salvaguardas (anti-autoboicot):
  - Si `std == 0` (todos iguales o un solo modelo) → z = 0 para todos.
  - Si dominio tiene < 2 modelos → trono = base (50.00) + flag `mode='neutral'`.
  - Métricas faltantes (None) → z = 0 (neutro), NO crash.
  - Validación de pesos: Σ pesos == 1.0 ± 0.001 (tolerancia float).

Identidad de marca (Brand Engine, AGENTS.md regla #4):
  - Errores con prefijo `catastro_trono_*`.
  - Naming `forja`-style implícito en el módulo del Catastro.

[Hilo Manus Catastro] · Sprint 86 Bloque 4 · 2026-05-04 · v0.86.4
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Iterable, Optional

from kernel.catastro.schema import CatastroModelo


# ============================================================================
# Constantes canónicas
# ============================================================================

# Pesos por defecto del SPEC sección 4. Σ = 1.00.
DEFAULT_WEIGHTS: dict[str, float] = {
    "quality_score":     0.40,
    "cost_efficiency":   0.25,
    "speed_score":       0.15,
    "reliability_score": 0.10,
    "brand_fit":         0.10,
}

# Métricas que aporta el Trono (orden canónico para iteración).
METRIC_FIELDS: tuple[str, ...] = tuple(DEFAULT_WEIGHTS.keys())

# Base y escala de la fórmula final.
DEFAULT_BASE: float = 50.0
DEFAULT_SCALE: float = 10.0

# Rango clampeado consistente con NUMERIC(5,2) en el schema.
TRONO_MIN: float = 0.0
TRONO_MAX: float = 100.0

# Tolerancia para validar Σ pesos = 1.0.
WEIGHTS_SUM_TOLERANCE: float = 0.001

# Confidence default cuando un modelo no la trae explícita.
DEFAULT_CONFIDENCE: float = 0.50


# ============================================================================
# Errores con identidad de marca (catastro_trono_*)
# ============================================================================


class CatastroTronoError(Exception):
    """Error base del módulo Trono. Identidad de marca: catastro_trono_*."""

    code: str = "catastro_trono_error"

    def __init__(self, message: str, **context):
        super().__init__(message)
        self.context = context


class CatastroTronoInvalidWeights(CatastroTronoError):
    """Pesos pasados al TronoCalculator no suman 1.0 ± tolerancia."""

    code = "catastro_trono_invalid_weights"


class CatastroTronoEmptyInput(CatastroTronoError):
    """Lista de modelos vacía pasada a compute_for_domain o compute_all."""

    code = "catastro_trono_empty_input"


class CatastroTronoInvalidDomain(CatastroTronoError):
    """Dominio vacío o None pasado a compute_for_domain."""

    code = "catastro_trono_invalid_domain"


# ============================================================================
# Resultado del cálculo (explainable, con bandas de confianza)
# ============================================================================


@dataclass
class TronoResult:
    """
    Resultado del cálculo de Trono Score para un modelo en un dominio.

    Es explainable: incluye z-scores por métrica y la contribución
    (w_i * z_i) de cada una al total. Útil para audit y para alimentar
    la tool MCP `catastro.recommend(explicar=True)` del Sprint 87.
    """

    modelo_id: str
    dominio: str
    trono_old: Optional[float]      # valor previo en BD (puede ser None)
    trono_new: float                # valor nuevo calculado
    trono_delta: float              # trono_new - (trono_old or 50.0)
    trono_low: float                # banda inferior de confianza
    trono_high: float               # banda superior de confianza
    z_scores: dict[str, float]      # z por métrica (puede ser 0.0 si NULL)
    contributions: dict[str, float] # w_i * z_i por métrica
    confidence: float               # confidence del modelo (band width)
    mode: str = "z_score"           # "z_score" | "neutral" | "skipped"
    warnings: list[str] = field(default_factory=list)


# ============================================================================
# TronoCalculator
# ============================================================================


class TronoCalculator:
    """
    Calculadora del Trono Score por dominio.

    Espejo Python de `catastro_recompute_trono(text)` en migration 019.
    Pensado para:
      - Tests offline reproducibles (sin tocar Supabase).
      - Pre-cómputo en el pipeline antes de persistir vía RPC.
      - Recomendaciones contextuales en queries en vivo (futuro Sprint 87).

    Inmutable después de la construcción. Reutilizable entre runs.
    """

    def __init__(
        self,
        weights: Optional[dict[str, float]] = None,
        base: float = DEFAULT_BASE,
        scale: float = DEFAULT_SCALE,
    ) -> None:
        self.weights: dict[str, float] = dict(weights) if weights else dict(DEFAULT_WEIGHTS)
        self.base: float = float(base)
        self.scale: float = float(scale)
        self._validate_weights()

    # ------------------------------------------------------------------------
    # Validaciones
    # ------------------------------------------------------------------------

    def _validate_weights(self) -> None:
        """Σ pesos == 1.0 ± WEIGHTS_SUM_TOLERANCE; todos los keys deben existir."""
        missing = set(METRIC_FIELDS) - set(self.weights.keys())
        extra = set(self.weights.keys()) - set(METRIC_FIELDS)
        if missing or extra:
            raise CatastroTronoInvalidWeights(
                f"weights debe contener exactamente {METRIC_FIELDS}; "
                f"missing={missing} extra={extra}",
                missing=list(missing),
                extra=list(extra),
            )
        total = sum(self.weights.values())
        if abs(total - 1.0) > WEIGHTS_SUM_TOLERANCE:
            raise CatastroTronoInvalidWeights(
                f"Σ pesos debe ser 1.0 ± {WEIGHTS_SUM_TOLERANCE}, recibido {total:.6f}",
                weights=dict(self.weights),
                sum=total,
            )

    # ------------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------------

    def compute_for_domain(
        self,
        modelos: list[CatastroModelo],
        dominio: str,
    ) -> list[TronoResult]:
        """
        Calcula trono_global para todos los modelos del `dominio` dado.

        Filtra previamente:
          - Solo modelos cuyo `dominios` incluye `dominio`.
          - Estado != 'deprecated'.

        Caso degenerado:
          - Si quedan < 2 modelos tras filtrar → todos reciben
            trono_new = base (50) con mode='neutral'.

        Returns:
            list[TronoResult] — uno por cada modelo del dominio.
        """
        if not dominio:
            raise CatastroTronoInvalidDomain("dominio no puede ser vacío o None")
        if not modelos:
            raise CatastroTronoEmptyInput(
                "modelos no puede estar vacío",
                dominio=dominio,
            )

        # Filtrar modelos del dominio + estado válido
        in_domain = [
            m for m in modelos
            if dominio in (m.dominios or [])
            and (m.estado is None or str(m.estado.value if hasattr(m.estado, "value") else m.estado) != "deprecated")
        ]

        if len(in_domain) < 2:
            return self._neutral_results(in_domain, dominio,
                                         razon="menos_de_2_modelos")

        # Calcular medias y std por métrica
        means: dict[str, float] = {}
        stds: dict[str, float] = {}
        for metric in METRIC_FIELDS:
            valores = [getattr(m, metric) for m in in_domain
                       if getattr(m, metric) is not None]
            if not valores:
                # Toda la métrica es NULL en el dominio → z=0 para todos
                means[metric] = 0.0
                stds[metric] = 1.0
                continue
            means[metric] = statistics.fmean(valores)
            if len(valores) < 2:
                stds[metric] = 1.0  # std muestral indefinida con n<2 → z=0
                continue
            std = statistics.stdev(valores)
            stds[metric] = std if std > 0 else 1.0  # safeguard std=0

        # Construir resultados
        results: list[TronoResult] = []
        for m in in_domain:
            results.append(self._compute_single(m, dominio, means, stds))

        return results

    def compute_all(
        self,
        modelos: list[CatastroModelo],
    ) -> dict[str, list[TronoResult]]:
        """
        Calcula trono_global para TODOS los dominios distintos en `modelos`.

        Returns:
            dict[dominio -> list[TronoResult]]
        """
        if not modelos:
            raise CatastroTronoEmptyInput("modelos no puede estar vacío")

        dominios: set[str] = set()
        for m in modelos:
            for d in (m.dominios or []):
                dominios.add(d)

        out: dict[str, list[TronoResult]] = {}
        for d in sorted(dominios):
            out[d] = self.compute_for_domain(modelos, d)
        return out

    # ------------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------------

    def _compute_single(
        self,
        modelo: CatastroModelo,
        dominio: str,
        means: dict[str, float],
        stds: dict[str, float],
    ) -> TronoResult:
        """Calcula trono para UN modelo dado means/stds del dominio."""
        z_scores: dict[str, float] = {}
        contributions: dict[str, float] = {}
        warnings: list[str] = []

        for metric in METRIC_FIELDS:
            x = getattr(modelo, metric)
            if x is None:
                z = 0.0
                warnings.append(f"{metric}_null_treated_as_zero_z")
            else:
                z = (float(x) - means[metric]) / stds[metric]
            z_scores[metric] = z
            contributions[metric] = self.weights[metric] * z

        weighted_z = sum(contributions.values())
        raw_trono = self.base + self.scale * weighted_z
        trono_new = round(_clamp(raw_trono, TRONO_MIN, TRONO_MAX), 2)

        trono_old = modelo.trono_global
        trono_delta = round(trono_new - (trono_old if trono_old is not None else self.base), 2)

        confidence = modelo.confidence if modelo.confidence is not None else DEFAULT_CONFIDENCE
        band_half_width = self.scale * (1.0 - confidence)
        trono_low = round(_clamp(trono_new - band_half_width, TRONO_MIN, TRONO_MAX), 2)
        trono_high = round(_clamp(trono_new + band_half_width, TRONO_MIN, TRONO_MAX), 2)

        return TronoResult(
            modelo_id=modelo.id,
            dominio=dominio,
            trono_old=trono_old,
            trono_new=trono_new,
            trono_delta=trono_delta,
            trono_low=trono_low,
            trono_high=trono_high,
            z_scores=z_scores,
            contributions=contributions,
            confidence=confidence,
            mode="z_score",
            warnings=warnings,
        )

    def _neutral_results(
        self,
        modelos: list[CatastroModelo],
        dominio: str,
        razon: str,
    ) -> list[TronoResult]:
        """Caso degenerado: todos los modelos reciben base como trono_new."""
        out: list[TronoResult] = []
        for m in modelos:
            confidence = m.confidence if m.confidence is not None else DEFAULT_CONFIDENCE
            band = self.scale * (1.0 - confidence)
            trono_old = m.trono_global
            out.append(TronoResult(
                modelo_id=m.id,
                dominio=dominio,
                trono_old=trono_old,
                trono_new=self.base,
                trono_delta=round(self.base - (trono_old if trono_old is not None else self.base), 2),
                trono_low=round(_clamp(self.base - band, TRONO_MIN, TRONO_MAX), 2),
                trono_high=round(_clamp(self.base + band, TRONO_MIN, TRONO_MAX), 2),
                z_scores={k: 0.0 for k in METRIC_FIELDS},
                contributions={k: 0.0 for k in METRIC_FIELDS},
                confidence=confidence,
                mode="neutral",
                warnings=[razon],
            ))
        return out


# ============================================================================
# Helpers
# ============================================================================


def _clamp(x: float, lo: float, hi: float) -> float:
    """Clampea x al rango [lo, hi]."""
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def apply_results_to_models(
    modelos: Iterable[CatastroModelo],
    results: Iterable[TronoResult],
) -> int:
    """
    Aplica los TronoResult.trono_new/delta a los CatastroModelo correspondientes
    in-place. Útil para que el pipeline serialice los modelos con el trono ya
    calculado antes de la persistencia atómica.

    Returns:
        int — cantidad de modelos actualizados.
    """
    by_id: dict[str, CatastroModelo] = {m.id: m for m in modelos}
    updated = 0
    for r in results:
        m = by_id.get(r.modelo_id)
        if m is None:
            continue
        m.trono_global = r.trono_new
        m.trono_delta = r.trono_delta
        updated += 1
    return updated
