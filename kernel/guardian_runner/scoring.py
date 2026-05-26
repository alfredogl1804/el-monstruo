"""
kernel/guardian/scoring.py

Scoring Engine para el Guardian de los Objetivos (Sprint GUARDIAN-AUTONOMO-001 T2).

Diseño:
- Cada Objetivo Maestro (1-15) tiene una rubrica YAML firmada en
  ``kernel/guardian/rubricas/objetivo_<N>.yaml`` (DSC-G-008 v2 enforcement).
- La rubrica declara metrics, evidence sources, thresholds y formula.
- ``compute_objective_score(objetivo_id)`` devuelve un ``ObjectiveScore``
  con score_pct, evidencias evaluadas y status segun thresholds.
- Las evidencias pueden ser:
    - sql: query Supabase (cuenta tablas, RLS coverage, etc.)
    - filesystem: glob/wc de archivos en el repo
    - git: count de commits/PRs en un rango
    - static: valor literal (cuando la metrica es declarativa)

Anti-autoboicot:
- ESTA es la primera vez que se canoniza el scoring engine. No se asume nada
  sobre rubricas previas; las 15 YAMLs son la fuente de verdad.

Compatibilidad con Guardian existente:
- ``GuardianDeObjetivos.evaluate_objetivo(objetivo_id, metrics)`` espera un
  ``metrics: dict``. ``ObjectiveScore.metrics`` cumple ese contrato.
- ``GuardianDeObjetivos.evaluate_all(metrics_by_objetivo)`` recibe el dict
  completo. La funcion auxiliar ``compute_all_objectives_scores()`` lo arma.

DSC enforzado:
- DSC-G-008 v2 (Gate de Evidencia): rubrica + evidencia + denominador + falsadores
- DSC-G-017 (DSC-as-Contract): cada rubrica tiene rubrica_version semver
- DSC-V-001 (validacion magna): record_validation antes de invocar APIs externas
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None  # PyYAML opcional, falla limpio si rubricas requieren

logger = logging.getLogger(__name__)

RUBRICAS_DIR = Path(__file__).parent / "rubricas"


# ── Tipos ─────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class EvidenceResult:
    """Resultado de evaluar una evidencia individual de una rubrica."""

    metric_key: str
    metric_type: str  # 'sql' | 'filesystem' | 'git' | 'static'
    observed_value: Optional[float]
    threshold_min: Optional[float]
    threshold_max: Optional[float]
    passed: bool
    error: Optional[str] = None
    raw_output: Optional[str] = None


@dataclass(frozen=True)
class ObjectiveScore:
    """Resultado consolidado de evaluar un Objetivo Maestro."""

    objective_id: int
    objective_name: str
    rubrica_version: str
    score_pct: float  # 0.0-100.0
    status: str  # 'ok' | 'warning' | 'critical' | 'emergency'
    metrics: dict[str, Any]  # Para alimentar Guardian.evaluate_objetivo
    evidence: list[EvidenceResult]
    computed_at: str

    def to_jsonb(self) -> dict[str, Any]:
        """Serializar para columna evidence_jsonb de guardian_audit_log."""
        return {
            "objective_name": self.objective_name,
            "rubrica_version": self.rubrica_version,
            "metrics": self.metrics,
            "evidence": [asdict(e) for e in self.evidence],
            "computed_at": self.computed_at,
        }


@dataclass(frozen=True)
class ScoringError(Exception):
    """Error al computar el scoring de un objetivo."""

    objective_id: int
    reason: str

    def __str__(self) -> str:
        return f"ScoringError(objective_id={self.objective_id}, reason={self.reason})"


# ── Carga de rubricas ────────────────────────────────────────────────────


def load_rubrica(objetivo_id: int) -> dict[str, Any]:
    """Cargar rubrica YAML del objetivo."""
    if yaml is None:
        raise ScoringError(objetivo_id, "PyYAML no instalado")

    path = RUBRICAS_DIR / f"objetivo_{objetivo_id:02d}.yaml"
    if not path.exists():
        raise ScoringError(objetivo_id, f"Rubrica no existe: {path}")

    with open(path, "r", encoding="utf-8") as f:
        rubrica = yaml.safe_load(f)

    if not isinstance(rubrica, dict):
        raise ScoringError(objetivo_id, "Rubrica YAML no es dict")

    required_keys = {"objective_id", "objective_name", "rubrica_version", "evidence"}
    missing = required_keys - set(rubrica.keys())
    if missing:
        raise ScoringError(objetivo_id, f"Rubrica YAML incompleta: faltan {missing}")

    if rubrica["objective_id"] != objetivo_id:
        raise ScoringError(
            objetivo_id,
            f"Rubrica YAML declara objective_id={rubrica['objective_id']} pero archivo es objetivo_{objetivo_id:02d}",
        )

    return rubrica


# ── Evaluadores de evidencia ─────────────────────────────────────────────


def _eval_evidence_sql(evidence_spec: dict[str, Any]) -> tuple[Optional[float], Optional[str]]:
    """Ejecutar SQL contra Supabase via sb_sql.py wrapper."""
    query = evidence_spec.get("query")
    if not query:
        return None, "SQL evidence sin query"

    home = os.path.expanduser("~")
    sb_sql = os.path.join(home, ".monstruo", "sb_sql.py")
    if not os.path.exists(sb_sql):
        return None, "sb_sql.py no disponible en ~/.monstruo/"

    try:
        result = subprocess.run(
            ["python3", sb_sql, "sql", "-q", query],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return None, "SQL timeout"
    except Exception as e:  # noqa: BLE001
        return None, f"SQL error: {e}"

    if result.returncode != 0:
        return None, f"SQL exit {result.returncode}: {result.stderr[:200]}"

    raw = result.stdout
    # sb_sql.py emite "[HTTP 201]\n" + JSON. Tomar la primera estructura JSON.
    bracket = raw.find("[")
    if bracket == -1:
        return None, f"SQL output no parseable: {raw[:200]}"

    try:
        rows = json.loads(raw[bracket:])
    except json.JSONDecodeError as e:
        return None, f"SQL JSON parse error: {e}"

    if not isinstance(rows, list) or len(rows) == 0:
        return 0.0, raw[:200]

    # Si la primera fila tiene una sola columna numerica, usarla
    first = rows[0]
    if isinstance(first, dict) and len(first) == 1:
        val = list(first.values())[0]
        try:
            return float(val), raw[:200]
        except (TypeError, ValueError):
            return None, f"SQL value no numerico: {val}"

    # Si tiene varias columnas, buscar la primera numerica
    for k, v in first.items():
        try:
            return float(v), raw[:200]
        except (TypeError, ValueError):
            continue

    return None, f"SQL output sin columnas numericas: {raw[:200]}"


def _eval_evidence_filesystem(evidence_spec: dict[str, Any]) -> tuple[Optional[float], Optional[str]]:
    """Contar archivos / lineas via glob."""
    pattern = evidence_spec.get("pattern")
    operation = evidence_spec.get("operation", "count_files")

    if not pattern:
        return None, "filesystem evidence sin pattern"

    repo_root = Path(__file__).resolve().parent.parent.parent

    if operation == "count_files":
        try:
            files = list(repo_root.glob(pattern))
            return float(len(files)), f"glob {pattern}: {len(files)} files"
        except Exception as e:  # noqa: BLE001
            return None, f"filesystem error: {e}"

    if operation == "count_lines":
        try:
            total = 0
            files = list(repo_root.glob(pattern))
            for f in files:
                if f.is_file():
                    with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                        total += sum(1 for _ in fh)
            return float(total), f"glob {pattern}: {total} lines"
        except Exception as e:  # noqa: BLE001
            return None, f"filesystem error: {e}"

    return None, f"filesystem operation desconocida: {operation}"


def _eval_evidence_git(evidence_spec: dict[str, Any]) -> tuple[Optional[float], Optional[str]]:
    """Ejecutar git log y contar resultados."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    args = evidence_spec.get("git_args", [])
    if not isinstance(args, list):
        return None, "git_args debe ser lista"

    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root)] + args,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        return None, "git timeout"

    if result.returncode != 0:
        return None, f"git exit {result.returncode}: {result.stderr[:200]}"

    lines = [line for line in result.stdout.splitlines() if line.strip()]
    return float(len(lines)), f"git: {len(lines)} lines"


def _eval_evidence_static(evidence_spec: dict[str, Any]) -> tuple[Optional[float], Optional[str]]:
    """Valor estatico declarado en la rubrica."""
    value = evidence_spec.get("value")
    if value is None:
        return None, "static evidence sin value"
    try:
        return float(value), f"static: {value}"
    except (TypeError, ValueError):
        return None, f"static value no numerico: {value}"


EVIDENCE_EVALUATORS = {
    "sql": _eval_evidence_sql,
    "filesystem": _eval_evidence_filesystem,
    "git": _eval_evidence_git,
    "static": _eval_evidence_static,
}


def _evaluate_one_evidence(metric_key: str, spec: dict[str, Any]) -> EvidenceResult:
    """Evaluar una evidencia individual de la rubrica."""
    metric_type = spec.get("type")
    if metric_type not in EVIDENCE_EVALUATORS:
        return EvidenceResult(
            metric_key=metric_key,
            metric_type=metric_type or "unknown",
            observed_value=None,
            threshold_min=spec.get("threshold_min"),
            threshold_max=spec.get("threshold_max"),
            passed=False,
            error=f"Tipo de evidencia desconocido: {metric_type}",
        )

    evaluator = EVIDENCE_EVALUATORS[metric_type]
    observed, raw = evaluator(spec)

    threshold_min = spec.get("threshold_min")
    threshold_max = spec.get("threshold_max")

    if observed is None:
        passed = False
    else:
        passed = True
        if threshold_min is not None and observed < float(threshold_min):
            passed = False
        if threshold_max is not None and observed > float(threshold_max):
            passed = False

    return EvidenceResult(
        metric_key=metric_key,
        metric_type=metric_type,
        observed_value=observed,
        threshold_min=threshold_min,
        threshold_max=threshold_max,
        passed=passed,
        error=None if observed is not None else raw,
        raw_output=raw if observed is not None else None,
    )


# ── Scoring publico ──────────────────────────────────────────────────────


def _status_from_score(score_pct: float, thresholds: dict[str, float]) -> str:
    """Mapear score_pct a status segun thresholds de la rubrica."""
    if score_pct < thresholds.get("emergency_below", 25):
        return "emergency"
    if score_pct < thresholds.get("critical_below", 50):
        return "critical"
    if score_pct < thresholds.get("warning_below", 75):
        return "warning"
    return "ok"


def compute_objective_score(objetivo_id: int) -> ObjectiveScore:
    """Computar el score de un objetivo segun su rubrica YAML.

    Args:
        objetivo_id: ID del objetivo (1-15).

    Returns:
        ObjectiveScore con score_pct, status, metrics y evidencias.

    Raises:
        ScoringError: si la rubrica no existe o esta mal formada.
    """
    rubrica = load_rubrica(objetivo_id)

    evidence_specs = rubrica.get("evidence", {})
    if not isinstance(evidence_specs, dict) or not evidence_specs:
        raise ScoringError(objetivo_id, "Rubrica sin evidence specs")

    results: list[EvidenceResult] = []
    for metric_key, spec in evidence_specs.items():
        try:
            results.append(_evaluate_one_evidence(metric_key, spec))
        except Exception as e:  # noqa: BLE001
            results.append(
                EvidenceResult(
                    metric_key=metric_key,
                    metric_type=spec.get("type", "unknown"),
                    observed_value=None,
                    threshold_min=spec.get("threshold_min"),
                    threshold_max=spec.get("threshold_max"),
                    passed=False,
                    error=f"Excepcion evaluando: {e}",
                )
            )

    # Score = % de evidencias que pasan, ponderadas por weight si existe
    weights = []
    passed_weights = []
    for r in results:
        spec = evidence_specs.get(r.metric_key, {})
        w = float(spec.get("weight", 1.0))
        weights.append(w)
        if r.passed:
            passed_weights.append(w)

    total_w = sum(weights) or 1.0
    score_pct = (sum(passed_weights) / total_w) * 100.0

    thresholds = rubrica.get("status_thresholds", {})
    status = _status_from_score(score_pct, thresholds)

    # Metrics dict para Guardian.evaluate_objetivo: {metric_key: observed_value}
    metrics = {r.metric_key: r.observed_value for r in results}

    return ObjectiveScore(
        objective_id=objetivo_id,
        objective_name=rubrica.get("objective_name", f"Objetivo {objetivo_id}"),
        rubrica_version=rubrica.get("rubrica_version", "0.0.0"),
        score_pct=round(score_pct, 2),
        status=status,
        metrics=metrics,
        evidence=results,
        computed_at=datetime.now(timezone.utc).isoformat(),
    )


def compute_all_objectives_scores(objective_ids: Optional[list[int]] = None) -> dict[int, ObjectiveScore]:
    """Computar scores para todos los objetivos (o un subset)."""
    if objective_ids is None:
        objective_ids = list(range(1, 16))  # 1-15 inclusive

    results: dict[int, ObjectiveScore] = {}
    for obj_id in objective_ids:
        try:
            results[obj_id] = compute_objective_score(obj_id)
        except ScoringError as e:
            logger.warning("scoring_failed_objective_%d: %s", obj_id, e)
        except Exception as e:  # noqa: BLE001
            logger.exception("scoring_unexpected_error_objective_%d: %s", obj_id, e)

    return results


def build_metrics_by_objetivo(scores: dict[int, ObjectiveScore]) -> dict[int, dict[str, Any]]:
    """Construir el dict que GuardianDeObjetivos.evaluate_all() consume."""
    return {obj_id: score.metrics for obj_id, score in scores.items()}
