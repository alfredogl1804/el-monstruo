"""
El Catastro · Quorum Validator 2-de-3.

Valida que un dato (ej. quality_score, pricing, context_length) sea
confirmado por al menos 2 de 3 fuentes independientes antes de
persistirlo en `catastro_modelos`. Si solo 1 fuente lo respalda, el
dato se marca como `unverified` y NO se persiste.

Lógica del quorum:
  - Para campos numéricos (quality_score, pricing): 2-de-3 cuando los
    valores caen dentro de una tolerancia configurable (default ±10%).
  - Para campos categóricos (status, license, organization): 2-de-3
    por igualdad exacta tras normalización (lowercase + strip).
  - Para campos de existencia (modelo aparece en la fuente): 2-de-3
    por presencia.

Trust score por fuente:
  Cada fuente tiene un peso base 1.0. Cuando una fuente discrepa del
  consenso 2-de-3, su trust se decrementa 0.05. Cuando confirma, no
  cambia. Esto se persiste en `catastro_curadores.trust_score` para
  uso futuro (Sprint 88+).

[Hilo Manus Catastro] · Sprint 86 Bloque 2 · 2026-05-04
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


# ============================================================================
# TIPOS Y ENUMS
# ============================================================================

class QuorumOutcome(str, Enum):
    """Resultado de una validación quorum."""

    QUORUM_REACHED = "quorum_reached"      # 2+ fuentes coinciden → persistir
    QUORUM_UNANIMOUS = "quorum_unanimous"  # 3-de-3 coinciden → confianza máxima
    QUORUM_FAILED = "quorum_failed"        # ≤1 fuente o discrepancia total
    INSUFFICIENT_DATA = "insufficient_data"  # <2 fuentes reportaron el dato


class FieldType(str, Enum):
    """Tipo de campo a validar — determina la estrategia de comparación."""

    NUMERIC = "numeric"        # tolerancia ±X%
    CATEGORICAL = "categorical"  # igualdad tras normalizar
    PRESENCE = "presence"      # existe / no existe en la fuente


@dataclass(frozen=True)
class FuenteVote:
    """
    Voto de una fuente sobre un campo específico.

    `value=None` significa "la fuente NO reportó el dato"
    (insufficient_data desde el punto de vista de esta fuente).
    """
    fuente: str
    value: Optional[Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def has_data(self) -> bool:
        """True si la fuente reportó el dato (no None)."""
        return self.value is not None


@dataclass
class QuorumResult:
    """Resultado completo de una validación quorum."""

    field_name: str
    field_type: FieldType
    outcome: QuorumOutcome
    consensus_value: Optional[Any]
    """Valor consensuado (mediana para numéricos, modo para categóricos).
    None si no hubo quorum."""

    votes: list[FuenteVote]
    """Todos los votos recibidos."""

    confirming_sources: list[str]
    """Fuentes que respaldan `consensus_value` dentro de tolerancia."""

    dissenting_sources: list[str]
    """Fuentes que reportaron pero discrepan del consenso."""

    silent_sources: list[str]
    """Fuentes que no reportaron el dato (value=None)."""

    confidence_score: float
    """Score 0.0-1.0: 1.0 = unanimous, 0.66 = 2-de-3, 0.0 = failed."""

    timestamp: datetime
    """UTC timestamp del cálculo."""

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_persistable(self) -> bool:
        """True si el resultado merece ser persistido en catastro_modelos."""
        return self.outcome in (QuorumOutcome.QUORUM_REACHED, QuorumOutcome.QUORUM_UNANIMOUS)

    def to_audit_entry(self) -> dict[str, Any]:
        """Serializa el resultado para inserción en `catastro_eventos`."""
        return {
            "field_name": self.field_name,
            "field_type": self.field_type.value,
            "outcome": self.outcome.value,
            "consensus_value": self.consensus_value,
            "confirming_sources": self.confirming_sources,
            "dissenting_sources": self.dissenting_sources,
            "silent_sources": self.silent_sources,
            "confidence_score": round(self.confidence_score, 3),
            "timestamp": self.timestamp.isoformat(),
            "votes": [
                {"fuente": v.fuente, "value": v.value, "metadata": v.metadata}
                for v in self.votes
            ],
        }


# ============================================================================
# QUORUM VALIDATOR
# ============================================================================

class QuorumValidator:
    """
    Valida campos siguiendo política 2-de-3 con cross-validation.

    Uso típico:
        validator = QuorumValidator(numeric_tolerance=0.10)

        result = validator.validate(
            field_name="quality_score",
            field_type=FieldType.NUMERIC,
            votes=[
                FuenteVote("artificial_analysis", 87.4),
                FuenteVote("openrouter", None),
                FuenteVote("lmarena", 1489.9),  # arena score, no quality
            ],
        )

        if result.is_persistable:
            modelo.quality_score = result.consensus_value
    """

    # Default de fuentes oficiales en orden canónico
    OFFICIAL_SOURCES = ("artificial_analysis", "openrouter", "lmarena")

    def __init__(
        self,
        *,
        numeric_tolerance: float = 0.10,
        categorical_normalize: bool = True,
        min_sources_required: int = 2,
    ) -> None:
        """
        Args:
            numeric_tolerance: tolerancia relativa para igualdad numérica.
                              0.10 = ±10% del valor mediano.
            categorical_normalize: si True, lowercase + strip antes de comparar.
            min_sources_required: mínimo de fuentes con dato (default 2).
        """
        if not 0 <= numeric_tolerance <= 1:
            raise ValueError(f"numeric_tolerance debe estar en [0, 1], recibido: {numeric_tolerance}")
        if min_sources_required < 1:
            raise ValueError(f"min_sources_required debe ser >= 1, recibido: {min_sources_required}")

        self.numeric_tolerance = numeric_tolerance
        self.categorical_normalize = categorical_normalize
        self.min_sources_required = min_sources_required

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def validate(
        self,
        *,
        field_name: str,
        field_type: FieldType,
        votes: list[FuenteVote],
    ) -> QuorumResult:
        """
        Valida un campo según la estrategia de su tipo.

        Returns:
            QuorumResult con outcome, consensus_value, y desglose de votos.
        """
        if not votes:
            raise ValueError("votes no puede ser una lista vacía")

        valid_votes = [v for v in votes if v.has_data]
        silent_sources = [v.fuente for v in votes if not v.has_data]

        # Caso 1: insuficientes fuentes con dato
        if len(valid_votes) < self.min_sources_required:
            return QuorumResult(
                field_name=field_name,
                field_type=field_type,
                outcome=QuorumOutcome.INSUFFICIENT_DATA,
                consensus_value=None,
                votes=votes,
                confirming_sources=[v.fuente for v in valid_votes],
                dissenting_sources=[],
                silent_sources=silent_sources,
                confidence_score=0.0,
                timestamp=datetime.now(timezone.utc),
                metadata={"reason": f"Solo {len(valid_votes)} fuente(s) reportó el dato"},
            )

        # Dispatch por tipo
        if field_type == FieldType.NUMERIC:
            return self._validate_numeric(field_name, valid_votes, silent_sources, votes)
        if field_type == FieldType.CATEGORICAL:
            return self._validate_categorical(field_name, valid_votes, silent_sources, votes)
        if field_type == FieldType.PRESENCE:
            return self._validate_presence(field_name, valid_votes, silent_sources, votes)

        raise ValueError(f"FieldType desconocido: {field_type}")

    # ------------------------------------------------------------------
    # Estrategias de validación
    # ------------------------------------------------------------------

    def _validate_numeric(
        self,
        field_name: str,
        valid_votes: list[FuenteVote],
        silent_sources: list[str],
        all_votes: list[FuenteVote],
    ) -> QuorumResult:
        """Estrategia para campos numéricos: tolerancia ±X% del mediano."""
        try:
            numeric_values = [(v.fuente, float(v.value)) for v in valid_votes]
        except (TypeError, ValueError) as e:
            return QuorumResult(
                field_name=field_name,
                field_type=FieldType.NUMERIC,
                outcome=QuorumOutcome.QUORUM_FAILED,
                consensus_value=None,
                votes=all_votes,
                confirming_sources=[],
                dissenting_sources=[v.fuente for v in valid_votes],
                silent_sources=silent_sources,
                confidence_score=0.0,
                timestamp=datetime.now(timezone.utc),
                metadata={"error": f"Valores no convertibles a float: {e}"},
            )

        # Mediana como pivote
        sorted_values = sorted(v[1] for v in numeric_values)
        n = len(sorted_values)
        if n % 2 == 1:
            median = sorted_values[n // 2]
        else:
            median = (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2.0

        # Tolerancia: si median == 0, usar tolerancia absoluta de 1e-6
        if median == 0:
            tolerance_abs = 1e-6
        else:
            tolerance_abs = abs(median) * self.numeric_tolerance

        # Quién confirma vs disiente
        confirming = []
        dissenting = []
        for fuente, value in numeric_values:
            if abs(value - median) <= tolerance_abs:
                confirming.append(fuente)
            else:
                dissenting.append(fuente)

        # Outcome
        if len(confirming) >= self.min_sources_required:
            if len(confirming) == len(numeric_values):
                outcome = QuorumOutcome.QUORUM_UNANIMOUS
                confidence = 1.0
            else:
                outcome = QuorumOutcome.QUORUM_REACHED
                confidence = len(confirming) / 3.0
            consensus_value = median
        else:
            outcome = QuorumOutcome.QUORUM_FAILED
            confidence = 0.0
            consensus_value = None

        return QuorumResult(
            field_name=field_name,
            field_type=FieldType.NUMERIC,
            outcome=outcome,
            consensus_value=consensus_value,
            votes=all_votes,
            confirming_sources=confirming,
            dissenting_sources=dissenting,
            silent_sources=silent_sources,
            confidence_score=confidence,
            timestamp=datetime.now(timezone.utc),
            metadata={
                "median": median,
                "tolerance_abs": tolerance_abs,
                "tolerance_relative": self.numeric_tolerance,
                "all_values": [v[1] for v in numeric_values],
            },
        )

    def _validate_categorical(
        self,
        field_name: str,
        valid_votes: list[FuenteVote],
        silent_sources: list[str],
        all_votes: list[FuenteVote],
    ) -> QuorumResult:
        """Estrategia para campos categóricos: igualdad tras normalización."""

        def normalize(v: Any) -> str:
            s = str(v)
            return s.strip().lower() if self.categorical_normalize else s.strip()

        normalized_votes = [(v.fuente, normalize(v.value), v.value) for v in valid_votes]

        # Frecuencia
        from collections import Counter
        freq = Counter(nv[1] for nv in normalized_votes)
        most_common_value, most_common_count = freq.most_common(1)[0]

        confirming = []
        dissenting = []
        canonical_raw_value: Optional[Any] = None
        for fuente, norm_value, raw_value in normalized_votes:
            if norm_value == most_common_value:
                confirming.append(fuente)
                if canonical_raw_value is None:
                    canonical_raw_value = raw_value
            else:
                dissenting.append(fuente)

        if most_common_count >= self.min_sources_required:
            if most_common_count == len(normalized_votes):
                outcome = QuorumOutcome.QUORUM_UNANIMOUS
                confidence = 1.0
            else:
                outcome = QuorumOutcome.QUORUM_REACHED
                confidence = most_common_count / 3.0
            consensus_value = canonical_raw_value
        else:
            outcome = QuorumOutcome.QUORUM_FAILED
            confidence = 0.0
            consensus_value = None

        return QuorumResult(
            field_name=field_name,
            field_type=FieldType.CATEGORICAL,
            outcome=outcome,
            consensus_value=consensus_value,
            votes=all_votes,
            confirming_sources=confirming,
            dissenting_sources=dissenting,
            silent_sources=silent_sources,
            confidence_score=confidence,
            timestamp=datetime.now(timezone.utc),
            metadata={
                "normalized_value": most_common_value,
                "frequency_distribution": dict(freq),
            },
        )

    def _validate_presence(
        self,
        field_name: str,
        valid_votes: list[FuenteVote],
        silent_sources: list[str],
        all_votes: list[FuenteVote],
    ) -> QuorumResult:
        """
        Estrategia para presencia: si N>=min fuentes reportan el modelo, quorum.

        El `value` se ignora — solo importa que la fuente lo reportó.
        """
        confirming = [v.fuente for v in valid_votes]
        n_total = len(all_votes)
        n_confirming = len(confirming)

        if n_confirming >= self.min_sources_required:
            if n_confirming == n_total:
                outcome = QuorumOutcome.QUORUM_UNANIMOUS
                confidence = 1.0
            else:
                outcome = QuorumOutcome.QUORUM_REACHED
                confidence = n_confirming / 3.0
            consensus_value = True
        else:
            outcome = QuorumOutcome.QUORUM_FAILED
            confidence = 0.0
            consensus_value = False

        return QuorumResult(
            field_name=field_name,
            field_type=FieldType.PRESENCE,
            outcome=outcome,
            consensus_value=consensus_value,
            votes=all_votes,
            confirming_sources=confirming,
            dissenting_sources=[],
            silent_sources=silent_sources,
            confidence_score=confidence,
            timestamp=datetime.now(timezone.utc),
            metadata={
                "confirming_count": n_confirming,
                "total_sources": n_total,
            },
        )

    # ------------------------------------------------------------------
    # Trust score updates (para catastro_curadores)
    # ------------------------------------------------------------------

    def compute_trust_deltas(
        self,
        results: list[QuorumResult],
        *,
        confirming_delta: float = 0.0,
        dissenting_delta: float = -0.05,
        silent_delta: float = 0.0,
        per_source_floor: float = -0.30,
        per_source_ceiling: float = 0.30,
    ) -> dict[str, float]:
        """
        Calcula deltas de trust_score por fuente basado en una lista de
        validaciones quorum.

        Aplica un cap (floor/ceiling) por fuente por run para evitar penalizaciones
        explosivas cuando una fuente disiente en muchas validaciones del mismo
        batch (ej: lmarena disintió en 6 validaciones del primer run productivo
        del Catastro y llegó a -0.30 sin cap; con 50 validaciones llegaría a
        -2.50, lo cual es destructivo). Patrón de escalado validado por Cowork
        (audit Sprint 86 B7):
          * 0      si la fuente aportó dato único (no entró a quorum)
          * -0.05  si discrepa minoría legítima en una validación
          * -0.30  techo descendente del run (extremo)

        Args:
            results: lista de QuorumResult del run.
            confirming_delta: delta para fuentes que confirmaron consenso.
            dissenting_delta: delta para fuentes que discreparon.
            silent_delta: delta para fuentes que no reportaron.
            per_source_floor: piso del trust_delta acumulado por fuente por run.
                Defecto -0.30 (alineado con la guía Cowork audit B7). Si es
                None, no se aplica piso (legacy behavior).
            per_source_ceiling: techo del trust_delta acumulado por fuente por
                run. Defecto +0.30. Si es None, no se aplica techo.

        Returns:
            dict con `{fuente: delta_acumulado_capado}`.
        """
        deltas: dict[str, float] = {}

        for result in results:
            if result.outcome == QuorumOutcome.INSUFFICIENT_DATA:
                continue  # No penalizar a nadie en este caso

            for fuente in result.confirming_sources:
                deltas[fuente] = deltas.get(fuente, 0.0) + confirming_delta
            for fuente in result.dissenting_sources:
                deltas[fuente] = deltas.get(fuente, 0.0) + dissenting_delta
            for fuente in result.silent_sources:
                deltas[fuente] = deltas.get(fuente, 0.0) + silent_delta

        # Cap escalado por fuente para evitar penalizaciones/recompensas
        # explosivas en runs grandes (Cowork audit B7).
        if per_source_floor is not None or per_source_ceiling is not None:
            floor = per_source_floor if per_source_floor is not None else float("-inf")
            ceil = per_source_ceiling if per_source_ceiling is not None else float("inf")
            for fuente, value in list(deltas.items()):
                deltas[fuente] = max(floor, min(ceil, value))

        return deltas
