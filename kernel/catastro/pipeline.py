"""
El Catastro · Pipeline orquestador.

Orquesta el ciclo diario:
  1. Fetch paralelo de las 3 fuentes (Artificial Analysis, OpenRouter, LMArena)
  2. Normalización a `ModeloIA` por fuente
  3. Cross-validation con QuorumValidator 2-de-3 por modelo y por campo
  4. Persistencia en `catastro_modelos` (solo campos con quorum)
  5. Audit trail en `catastro_eventos` (todos los votos, incluso los failed)
  6. Update de `catastro_curadores.trust_score` con deltas

Diseño:
  - Async first: las 3 fuentes corren en paralelo con asyncio.gather
  - Tolerante a fallos: si una fuente cae, el quorum 2-de-3 sigue posible
    con las otras 2 (siempre que pasen >=2 valores)
  - Idempotente: si un modelo ya existe en BD, hace UPSERT con merge de
    fuentes_evidencia
  - Logging estructurado: cada paso emite log con run_id

Disciplina os.environ:
  - SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY se leen al ejecutar `.run()`
  - Nunca se cachean a nivel módulo

[Hilo Manus Catastro] · Sprint 86 Bloque 2 · 2026-05-04
"""
from __future__ import annotations

import asyncio
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from kernel.catastro.persistence import (
    CatastroPersistence,
    PersistResult,
    build_modelo_from_pipeline_persistible,
)
from kernel.catastro.quorum import (
    FieldType,
    FuenteVote,
    QuorumOutcome,
    QuorumResult,
    QuorumValidator,
)
from kernel.catastro.sources import (
    ArtificialAnalysisFuente,
    BaseFuente,
    FuenteError,
    HumanEvalFuente,
    LMArenaFuente,
    MBPPFuente,
    OpenRouterFuente,
    RawSnapshot,
    SWEBenchFuente,
)
from kernel.catastro.coding_classifier import (
    CodingClassifier,
    CodingClassification,
)
from kernel.catastro.sources.field_mapping import (
    apply_field_mapping,
    load_field_mapping,
    FieldMappingError,
)
from kernel.catastro.trono import (
    TronoCalculator,
    TronoResult,
    apply_results_to_models,
)


logger = logging.getLogger(__name__)


# ============================================================================
# RESULTADO DE UN RUN COMPLETO
# ============================================================================

@dataclass
class PipelineRunResult:
    """Resultado completo de un ciclo del pipeline."""

    run_id: str
    started_at: datetime
    finished_at: Optional[datetime] = None

    # Snapshots crudos por fuente
    snapshots: dict[str, RawSnapshot] = field(default_factory=dict)
    # Errores por fuente (si hubo)
    fuente_errors: dict[str, str] = field(default_factory=dict)

    # Modelos procesados (slug → quorum_results por campo)
    modelos_procesados: dict[str, list[QuorumResult]] = field(default_factory=dict)

    # Modelos que pasaron quorum y serán persistidos
    modelos_persistibles: dict[str, dict[str, Any]] = field(default_factory=dict)

    # Trust deltas finales por fuente
    trust_deltas: dict[str, float] = field(default_factory=dict)

    # Resultados de persistencia (Bloque 3)
    persist_results: list[PersistResult] = field(default_factory=list)

    # Resultados de Trono Score por dominio (Bloque 4)
    trono_results: dict[str, list[TronoResult]] = field(default_factory=dict)

    # Flag: se omitió la persistencia por skip_persist=True (Bloque 4)
    persist_skipped: bool = False

    # Métricas resumen
    metrics: dict[str, Any] = field(default_factory=dict)

    # Sprint 86.4.5 Bloque 2 — métricas single-source extraídas via field_mapping
    # Forma: { slug: { campo: valor } } — solo para observabilidad/tests.
    # Los valores ya están duplicados en modelos_persistibles[slug]["fields"].
    metrics_extracted: dict[str, dict[str, float | None]] = field(default_factory=dict)

    @property
    def duration_seconds(self) -> Optional[float]:
        if not self.finished_at:
            return None
        return (self.finished_at - self.started_at).total_seconds()

    @property
    def is_success(self) -> bool:
        """True si al menos 2 fuentes respondieron exitosamente."""
        return len(self.snapshots) >= 2

    def summary(self) -> dict[str, Any]:
        """Resumen serializable para logs / API."""
        persist_ok = sum(1 for r in self.persist_results if r.success and not r.dry_run)
        persist_dry = sum(1 for r in self.persist_results if r.dry_run)
        persist_fail = sum(1 for r in self.persist_results if not r.success)

        # Mejora #2 audit Cowork Bloque 3: failure_rate y desglose por categoría.
        total = len(self.persist_results)
        failure_rate = (persist_fail / total) if total else 0.0
        error_categories: dict[str, int] = {}
        for r in self.persist_results:
            if not r.success and not r.dry_run:
                cat = r.error_category or "unknown"
                error_categories[cat] = error_categories.get(cat, 0) + 1

        # Trono summary (Bloque 4)
        trono_summary = {
            "dominios": len(self.trono_results),
            "modelos_calculados": sum(len(rs) for rs in self.trono_results.values()),
            "modos": {
                "z_score": sum(
                    1 for rs in self.trono_results.values() for r in rs if r.mode == "z_score"
                ),
                "neutral": sum(
                    1 for rs in self.trono_results.values() for r in rs if r.mode == "neutral"
                ),
            },
        }

        return {
            "run_id": self.run_id,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration_seconds": self.duration_seconds,
            "is_success": self.is_success,
            "fuentes_ok": list(self.snapshots.keys()),
            "fuentes_error": self.fuente_errors,
            "modelos_total": len(self.modelos_procesados),
            "modelos_persistibles": len(self.modelos_persistibles),
            "trust_deltas": self.trust_deltas,
            "trono_summary": trono_summary,
            "persist_summary": {
                "ok": persist_ok,
                "dry_run": persist_dry,
                "failed": persist_fail,
                "skipped": self.persist_skipped,
                "failure_rate_observed": failure_rate,
                "error_categories": error_categories,
            },
            "metrics": self.metrics,
        }


# ============================================================================
# PIPELINE
# ============================================================================

class CatastroPipeline:
    """
    Orquestador del ciclo diario del Catastro.

    Uso típico (Railway cron):
        pipeline = CatastroPipeline()
        result = await pipeline.run()
        if result.is_success:
            log.info(result.summary())
    """

    DEFAULT_SOURCES: tuple[type[BaseFuente], ...] = (
        ArtificialAnalysisFuente,
        OpenRouterFuente,
        LMArenaFuente,
    )

    # Sprint 86.5 — Macroarea 3 LLM Coding
    # Fuentes coding son OPCIONALES (no rompen pipeline existente si fallan).
    # Se incluyen solo si se pasan explicitamente en `sources` o si
    # CATASTRO_ENABLE_CODING=true.
    CODING_SOURCES: tuple[type[BaseFuente], ...] = (
        SWEBenchFuente,
        HumanEvalFuente,
        MBPPFuente,
    )

    def __init__(
        self,
        *,
        sources: Optional[list[BaseFuente]] = None,
        validator: Optional[QuorumValidator] = None,
        dry_run: bool = False,
        persistence: Optional[CatastroPersistence] = None,
        trono_calculator: Optional[TronoCalculator] = None,
        skip_persist: Optional[bool] = None,
    ) -> None:
        """
        Args:
            sources: lista de instancias de BaseFuente. Si None, se usan
                     las 3 oficiales con dry_run=False.
            validator: instancia de QuorumValidator. Si None, default 10%.
            dry_run: si True, todas las fuentes corren con dry_run=True
                     (sin red, devuelven snapshots fake) Y persistence
                     hereda dry_run=True (no toca Supabase).
            persistence: instancia de CatastroPersistence. Si None, se
                         construye una con dry_run igual al del pipeline.
                         Se respeta el dry_run propio si se pasa explícita.
            trono_calculator: instancia de TronoCalculator (Bloque 4). Si
                         None, se construye una con pesos default del SPEC.
            skip_persist: si True, omite el Paso 8 (persistencia atomica).
                         Si None, se lee CATASTRO_SKIP_PERSIST env var
                         (acepta 'true', '1', 'yes' en cualquier case).
                         Útil para auditorías dry-run que no deben tocar BD
                         ni siquiera en modo dry_run de persistence.
        """
        self.dry_run = dry_run
        if sources is not None:
            self.sources = sources
        else:
            self.sources = [cls(dry_run=dry_run) for cls in self.DEFAULT_SOURCES]
            # Sprint 86.5: agregar coding sources si flag activo
            enable_coding = os.environ.get("CATASTRO_ENABLE_CODING", "").strip().lower()
            if enable_coding in ("true", "1", "yes", "on"):
                self.sources.extend(
                    cls(dry_run=dry_run) for cls in self.CODING_SOURCES
                )

        self.validator = validator or QuorumValidator(numeric_tolerance=0.10)
        # Sprint 86.5 — coding classifier (heuristic fallback si no hay OPENAI_API_KEY)
        self.coding_classifier = CodingClassifier(use_llm=True)
        self.persistence = persistence or CatastroPersistence(dry_run=dry_run)
        self.trono_calculator = trono_calculator or TronoCalculator()

        # Resolución de skip_persist: argumento explícito > env var > False
        if skip_persist is not None:
            self.skip_persist: bool = bool(skip_persist)
        else:
            env_val = os.environ.get("CATASTRO_SKIP_PERSIST", "").strip().lower()
            self.skip_persist = env_val in ("true", "1", "yes", "on")

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    async def run(self) -> PipelineRunResult:
        """
        Ejecuta un ciclo completo del pipeline.

        Returns:
            PipelineRunResult con snapshots, modelos, quorum results, deltas.
        """
        run_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc)

        result = PipelineRunResult(run_id=run_id, started_at=started_at)

        logger.info(f"[catastro_pipeline] Run {run_id} starting (dry_run={self.dry_run})")

        # Paso 1: fetch paralelo
        await self._fetch_all(result)

        # Paso 2: si <2 fuentes respondieron, marcar como degradado
        if not result.is_success:
            logger.error(
                f"[catastro_pipeline] Run {run_id} DEGRADED: solo "
                f"{len(result.snapshots)} fuente(s) respondieron"
            )
            result.finished_at = datetime.now(timezone.utc)
            return result

        # Paso 3: normalizar y agrupar por modelo
        modelos_por_fuente = self._normalize_snapshots(result)

        # Paso 4: cross-validate con quorum
        all_quorum_results = self._cross_validate(modelos_por_fuente, result)

        # Paso 5: identificar persistibles
        self._extract_persistible(all_quorum_results, result)

        # Paso 5.5 (Sprint 86.4.5 Bloque 2): enriquecer persistibles con
        # campos métricos single-source desde el field_mapping.yaml.
        # Esto puebla quality_score / reliability_score / cost_efficiency /
        # speed_score / precio_input_per_million / precio_output_per_million.
        self._enrich_with_metrics(modelos_por_fuente, result)

        # Paso 6: trust deltas
        flat_results = [qr for qrs in result.modelos_procesados.values() for qr in qrs]
        result.trust_deltas = self.validator.compute_trust_deltas(flat_results)

        # Paso 7: cálculo Trono Score por dominio (Bloque 4)
        await self._compute_trono(result)

        # Paso 8: persistencia atómica via RPC (Bloque 3 + skip_persist Bloque 4)
        if self.skip_persist:
            result.persist_skipped = True
            logger.info(
                f"[catastro_pipeline] Paso 8 SKIP: skip_persist=True (run={run_id})"
            )
        else:
            await self._persist_all(result)

        # Métricas finales
        result.metrics = {
            "total_modelos_vistos": len(result.modelos_procesados),
            "total_modelos_persistibles": len(result.modelos_persistibles),
            "total_quorum_validations": len(flat_results),
            "quorum_unanimous_count": sum(
                1 for qr in flat_results if qr.outcome == QuorumOutcome.QUORUM_UNANIMOUS
            ),
            "quorum_reached_count": sum(
                1 for qr in flat_results if qr.outcome == QuorumOutcome.QUORUM_REACHED
            ),
            "quorum_failed_count": sum(
                1 for qr in flat_results if qr.outcome == QuorumOutcome.QUORUM_FAILED
            ),
            "insufficient_data_count": sum(
                1 for qr in flat_results if qr.outcome == QuorumOutcome.INSUFFICIENT_DATA
            ),
        }

        result.finished_at = datetime.now(timezone.utc)
        persist_ok = sum(1 for r in result.persist_results if r.success and not r.dry_run)
        persist_dry = sum(1 for r in result.persist_results if r.dry_run)
        persist_fail = sum(1 for r in result.persist_results if not r.success)
        logger.info(
            f"[catastro_pipeline] Run {run_id} OK \u00b7 "
            f"persistibles={result.metrics['total_modelos_persistibles']}/{result.metrics['total_modelos_vistos']} \u00b7 "
            f"persist_ok={persist_ok} dry={persist_dry} fail={persist_fail} \u00b7 "
            f"duration={result.duration_seconds:.2f}s"
        )
        return result

    # ------------------------------------------------------------------
    # Paso 7: cálculo Trono Score (Bloque 4)
    # ------------------------------------------------------------------

    async def _compute_trono(self, result: PipelineRunResult) -> None:
        """
        Calcula trono_global por dominio para los modelos persistibles
        usando el TronoCalculator (z-scores normalizados intra-dominio).

        Resultado:
          - `result.trono_results[dominio] = list[TronoResult]`
          - Se aplica `trono_global` y `trono_delta` IN-PLACE a los
            CatastroModelo construidos en `_persist_all` (no aquí; el
            apply real ocurre en _persist_all sobre el modelo construido).

        Memento:
          - Esta función NO escribe en BD. La RPC del Bloque 3 hace el
            UPSERT que persiste el trono ya calculado.
          - Si NO hay persistibles → skip silencioso.
          - El cálculo en Python es espejo de catastro_recompute_trono(text)
            de migration 019. Mantener AMBOS sincronizados.
        """
        if not result.modelos_persistibles:
            logger.info("[catastro_pipeline] Paso 7 skip: sin modelos persistibles")
            return

        # Construir CatastroModelos previamente para el cálculo
        # (los volveremos a construir en _persist_all; aquí solo necesitamos
        # tenerlos disponibles para alimentar el TronoCalculator).
        modelos: list = []
        for slug, persistible in result.modelos_persistibles.items():
            quorum_results = result.modelos_procesados.get(slug, [])
            try:
                modelos.append(build_modelo_from_pipeline_persistible(
                    slug=slug,
                    persistible=persistible,
                    quorum_results=quorum_results,
                ))
            except Exception as e:  # noqa: BLE001
                logger.warning(
                    f"[catastro_pipeline] trono build_modelo skip slug={slug}: {e}"
                )

        if not modelos:
            return

        try:
            result.trono_results = self.trono_calculator.compute_all(modelos)
        except Exception as e:  # noqa: BLE001
            logger.exception(
                f"[catastro_pipeline] trono CRASH (run={result.run_id}): {e}"
            )
            result.trono_results = {}
            return

        # Aplicar resultados in-place a los modelos para que cuando
        # _persist_all los reconstruya y serialice, ya lleven trono.
        # Como _persist_all reconstruye desde cero, almacenamos los
        # resultados en metrics para que _persist_all los pueda hidratar.
        flat_trono = [r for rs in result.trono_results.values() for r in rs]
        applied = apply_results_to_models(modelos, flat_trono)
        logger.info(
            f"[catastro_pipeline] Trono calculado: "
            f"dominios={len(result.trono_results)} "
            f"modelos={len(modelos)} aplicados={applied}"
        )

    # ------------------------------------------------------------------
    # Paso 8: persistencia atómica (Bloque 3)
    # ------------------------------------------------------------------

    async def _persist_all(self, result: PipelineRunResult) -> None:
        """
        Persiste todos los modelos persistibles via RPC atómica.

        Cada modelo es una transacci\u00f3n independiente del lado servidor.
        Si uno falla, los dem\u00e1s contin\u00faan (degraded gracefully).

        Memento:
          - Esta llamada NO es paralela: la RPC actualiza
            catastro_curadores compartido y queremos serializaci\u00f3n
            para que los deltas no se sobreescriban en concurrent UPDATEs
            (PostgreSQL los acumular\u00eda igual gracias a `+ delta`, pero
            preferimos serializaci\u00f3n estricta por simplicidad de debug).
        """
        if not result.modelos_persistibles:
            logger.info("[catastro_pipeline] Paso 7 skip: sin modelos persistibles")
            return

        # Índice por slug → TronoResult del dominio principal del modelo,
        # para hidratar los modelos antes de persistir (Bloque 4 hand-off).
        trono_by_id: dict[str, TronoResult] = {}
        for results_list in result.trono_results.values():
            for r in results_list:
                # Si un modelo aparece en múltiples dominios, gana el último;
                # para Sprint 86 los modelos solo tienen 1 dominio, es seguro.
                trono_by_id[r.modelo_id] = r

        for slug, persistible in result.modelos_persistibles.items():
            quorum_results = result.modelos_procesados.get(slug, [])
            try:
                modelo = build_modelo_from_pipeline_persistible(
                    slug=slug,
                    persistible=persistible,
                    quorum_results=quorum_results,
                )
                # Hidratar trono_global / trono_delta calculados en el Paso 7
                trono = trono_by_id.get(slug)
                if trono is not None:
                    modelo.trono_global = trono.trono_new
                    modelo.trono_delta = trono.trono_delta
            except Exception as e:  # noqa: BLE001
                logger.exception(
                    f"[catastro_pipeline] persist build_modelo CRASH slug={slug}: {e}"
                )
                result.persist_results.append(
                    PersistResult(
                        modelo_id=slug,
                        success=False,
                        error_code="catastro_persist_build_modelo_crash",
                        error_message=f"{type(e).__name__}: {e}",
                        error_category="item_crash",
                    )
                )
                continue

            try:
                # Solo enviamos los deltas que aplican a este modelo
                # (los acumulados globales — la RPC los aplicar\u00e1 una vez
                # por modelo, lo cual es contable y deseado: cada modelo
                # contribuye su propio delta al curador correspondiente)
                pr = self.persistence.persist(
                    modelo=modelo,
                    trust_deltas=result.trust_deltas,
                )
            except Exception as e:  # noqa: BLE001
                logger.exception(
                    f"[catastro_pipeline] persist CRASH slug={slug}: {e}"
                )
                pr = PersistResult(
                    modelo_id=slug,
                    success=False,
                    error_code="catastro_persist_call_crash",
                    error_message=f"{type(e).__name__}: {e}",
                    error_category="item_crash",
                )
            result.persist_results.append(pr)

        # Calcular failure_rate del batch y propagarlo a todos los items.
        # Mejora #2 audit Cowork Bloque 3 — monitor lo usa para alertar.
        if result.persist_results:
            failed = sum(
                1 for r in result.persist_results
                if not r.success and not r.dry_run
            )
            rate = failed / len(result.persist_results)
            for r in result.persist_results:
                # Solo seteamos si no viene ya seteado por persist_many
                if r.failure_rate_observed is None:
                    r.failure_rate_observed = rate

    # ------------------------------------------------------------------
    # Paso 1: fetch paralelo
    # ------------------------------------------------------------------

    async def _fetch_all(self, result: PipelineRunResult) -> None:
        """Fetch concurrente de todas las fuentes con tolerancia a fallos."""
        tasks = [self._fetch_one(source, result) for source in self.sources]
        await asyncio.gather(*tasks, return_exceptions=False)

    async def _fetch_one(self, source: BaseFuente, result: PipelineRunResult) -> None:
        """Fetch de una fuente, atrapando errores."""
        try:
            snapshot = await source.fetch()
            result.snapshots[source.nombre] = snapshot
            logger.info(
                f"[catastro_pipeline] {source.nombre} OK · "
                f"hash={snapshot.payload_hash} · meta={snapshot.metadata}"
            )
        except FuenteError as e:
            result.fuente_errors[source.nombre] = str(e)
            logger.warning(f"[catastro_pipeline] {source.nombre} FAILED: {e}")
        except Exception as e:  # noqa: BLE001
            result.fuente_errors[source.nombre] = f"{type(e).__name__}: {e}"
            logger.exception(f"[catastro_pipeline] {source.nombre} CRASH: {e}")

    # ------------------------------------------------------------------
    # Paso 3: normalización
    # ------------------------------------------------------------------

    def _normalize_snapshots(
        self, result: PipelineRunResult
    ) -> dict[str, dict[str, dict[str, Any]]]:
        """
        Normaliza cada snapshot a dict por modelo:
          { modelo_slug: { fuente: campos_normalizados } }

        El slug es la KEY canónica de cross-source. Estrategia simple:
          - Artificial Analysis: usa `slug` directamente
          - OpenRouter: usa `id` lowercased y normalizado
          - LMArena: usa `model_name`

        Para matching cross-source, se aplica `normalize_slug()` que
        maneja variaciones (claude-opus-4-7 vs claude-opus-4.7).
        """
        modelos_por_fuente: dict[str, dict[str, dict[str, Any]]] = {}

        for fuente_name, snapshot in result.snapshots.items():
            if fuente_name == "artificial_analysis":
                self._extract_aa(snapshot, modelos_por_fuente)
            elif fuente_name == "openrouter":
                self._extract_openrouter(snapshot, modelos_por_fuente)
            elif fuente_name == "lmarena":
                self._extract_lmarena(snapshot, modelos_por_fuente)
            elif fuente_name == "swe_bench":
                self._extract_swe_bench(snapshot, modelos_por_fuente)
            elif fuente_name == "human_eval":
                self._extract_human_eval(snapshot, modelos_por_fuente)
            elif fuente_name == "mbpp":
                self._extract_mbpp(snapshot, modelos_por_fuente)
            else:
                logger.warning(f"[catastro_pipeline] fuente desconocida: {fuente_name}")

        # Sprint 86.6: cachear para overfit cross-area en _enrich_with_coding
        self._modelos_por_fuente_cache = modelos_por_fuente

        return modelos_por_fuente

    def _extract_swe_bench(self, snapshot: RawSnapshot, agg: dict) -> None:
        """Sprint 86.5: extrae scores SWE-bench Verified + detecta gaming UC Berkeley."""
        if not hasattr(self, "_coding_cache"):
            self._coding_cache: dict[str, dict[str, Any]] = {}
        for item in snapshot.payload.get("data", []):
            slug = self.normalize_slug(item.get("model_id") or item.get("model_name") or "")
            if not slug:
                continue
            scores = SWEBenchFuente.extract_scores(item)
            gaming = SWEBenchFuente.detect_gaming(scores)
            agg.setdefault(slug, {})["swe_bench"] = {
                "raw_model_id": item.get("model_id"),
                "name": item.get("model_name"),
                "verified_score": scores.get("verified"),
                "lite_score": scores.get("lite"),
                "multilingual_python_score": scores.get("multilingual_python"),
                "gaming_detected": gaming,
            }
            cache_entry = self._coding_cache.setdefault(slug, {})
            cache_entry["swe_bench_verified"] = scores.get("verified")
            cache_entry["swe_bench_lite"] = scores.get("lite")
            cache_entry["swe_bench_multilingual_python"] = scores.get("multilingual_python")
            cache_entry["gaming_detected"] = gaming

    def _extract_human_eval(self, snapshot: RawSnapshot, agg: dict) -> None:
        if not hasattr(self, "_coding_cache"):
            self._coding_cache: dict[str, dict[str, Any]] = {}
        for item in snapshot.payload.get("data", []):
            slug = self.normalize_slug(item.get("model_id") or item.get("model_name") or "")
            if not slug:
                continue
            score = HumanEvalFuente.extract_score(item)
            agg.setdefault(slug, {})["human_eval"] = {
                "raw_model_id": item.get("model_id"),
                "name": item.get("model_name"),
                "pass_at_1": score,
            }
            self._coding_cache.setdefault(slug, {})["human_eval_plus"] = score

    def _extract_mbpp(self, snapshot: RawSnapshot, agg: dict) -> None:
        if not hasattr(self, "_coding_cache"):
            self._coding_cache: dict[str, dict[str, Any]] = {}
        for item in snapshot.payload.get("data", []):
            slug = self.normalize_slug(item.get("model_id") or item.get("model_name") or "")
            if not slug:
                continue
            score = MBPPFuente.extract_score(item)
            agg.setdefault(slug, {})["mbpp"] = {
                "raw_model_id": item.get("model_id"),
                "name": item.get("model_name"),
                "pass_at_1": score,
            }
            self._coding_cache.setdefault(slug, {})["mbpp_plus"] = score

    @staticmethod
    def normalize_slug(raw: str) -> str:
        """Normaliza slug: lowercase, replace . con -, replace _ con -."""
        return raw.strip().lower().replace(".", "-").replace("_", "-").replace("/", "-")

    def _extract_aa(self, snapshot: RawSnapshot, agg: dict) -> None:
        for item in snapshot.payload.get("data", []):
            slug = self.normalize_slug(item.get("slug") or item.get("id") or "")
            if not slug:
                continue
            agg.setdefault(slug, {})["artificial_analysis"] = {
                "raw_slug": item.get("slug"),
                "name": item.get("name"),
                "organization": (item.get("model_creator") or {}).get("name"),
                "quality_score": ArtificialAnalysisFuente.extract_quality_score(item),
                "pricing": ArtificialAnalysisFuente.extract_pricing(item),
                "tokens_per_second": item.get("median_output_tokens_per_second"),
                "ttft_seconds": item.get("median_time_to_first_token_seconds"),
            }

    def _extract_openrouter(self, snapshot: RawSnapshot, agg: dict) -> None:
        for item in snapshot.payload.get("data", []):
            slug = self.normalize_slug(item.get("canonical_slug") or item.get("id") or "")
            if not slug:
                continue
            agg.setdefault(slug, {})["openrouter"] = {
                "raw_id": item.get("id"),
                "name": item.get("name"),
                "context_length": OpenRouterFuente.extract_context_length(item),
                "pricing": OpenRouterFuente.extract_pricing(item),
                "is_open_source": OpenRouterFuente.is_open_source(item),
                "supported_parameters": item.get("supported_parameters", []),
                "input_modalities": (item.get("architecture") or {}).get("input_modalities", []),
                "output_modalities": (item.get("architecture") or {}).get("output_modalities", []),
            }

    def _extract_lmarena(self, snapshot: RawSnapshot, agg: dict) -> None:
        for row in snapshot.payload.get("rows", []):
            slug = self.normalize_slug(row.get("model_name") or "")
            if not slug:
                continue
            agg.setdefault(slug, {})["lmarena"] = {
                "raw_model_name": row.get("model_name"),
                "organization": row.get("organization"),
                "license": row.get("license"),
                "arena_score": LMArenaFuente.extract_arena_score(row),
                "rank": LMArenaFuente.extract_rank(row),
                "vote_count": row.get("vote_count"),
                "category": row.get("category"),
                "leaderboard_publish_date": row.get("leaderboard_publish_date"),
            }

    # ------------------------------------------------------------------
    # Paso 4: cross-validate
    # ------------------------------------------------------------------

    def _cross_validate(
        self,
        modelos_por_fuente: dict[str, dict[str, dict[str, Any]]],
        result: PipelineRunResult,
    ) -> dict[str, list[QuorumResult]]:
        """
        Para cada modelo, valida campos cross-source con QuorumValidator.

        Campos cross-source:
          - presence: ¿el modelo aparece en N fuentes?
          - organization (categorical)
          - license (categorical) — solo lmarena lo provee, así que su
            quorum será insufficient_data, pero registramos el voto
          - pricing.input_per_million (numeric, AA + OR)
          - pricing.output_per_million (numeric, AA + OR)

        Nota: quality_score y arena_score son métricas DIFERENTES con
        escalas distintas (0-100 vs Elo). NO se cross-validan entre sí.
        Se persisten ambas como columnas separadas.
        """
        all_results: dict[str, list[QuorumResult]] = {}

        for slug, fuentes_data in modelos_por_fuente.items():
            quorum_results: list[QuorumResult] = []

            # Validation 1: presence (¿en cuántas fuentes aparece?)
            presence_votes = [
                FuenteVote(f, True if f in fuentes_data else None)
                for f in QuorumValidator.OFFICIAL_SOURCES
            ]
            quorum_results.append(
                self.validator.validate(
                    field_name="presence",
                    field_type=FieldType.PRESENCE,
                    votes=presence_votes,
                )
            )

            # Validation 2: organization
            org_votes = [
                FuenteVote(f, fuentes_data.get(f, {}).get("organization") if f in fuentes_data else None)
                for f in QuorumValidator.OFFICIAL_SOURCES
            ]
            if any(v.has_data for v in org_votes):
                quorum_results.append(
                    self.validator.validate(
                        field_name="organization",
                        field_type=FieldType.CATEGORICAL,
                        votes=org_votes,
                    )
                )

            # Validation 3: pricing.input_per_million
            input_votes = [
                FuenteVote(
                    f,
                    (fuentes_data.get(f, {}).get("pricing") or {}).get("input_per_million")
                    if f in fuentes_data else None,
                )
                for f in QuorumValidator.OFFICIAL_SOURCES
            ]
            if sum(1 for v in input_votes if v.has_data) >= 2:
                quorum_results.append(
                    self.validator.validate(
                        field_name="pricing.input_per_million",
                        field_type=FieldType.NUMERIC,
                        votes=input_votes,
                    )
                )

            # Validation 4: pricing.output_per_million
            output_votes = [
                FuenteVote(
                    f,
                    (fuentes_data.get(f, {}).get("pricing") or {}).get("output_per_million")
                    if f in fuentes_data else None,
                )
                for f in QuorumValidator.OFFICIAL_SOURCES
            ]
            if sum(1 for v in output_votes if v.has_data) >= 2:
                quorum_results.append(
                    self.validator.validate(
                        field_name="pricing.output_per_million",
                        field_type=FieldType.NUMERIC,
                        votes=output_votes,
                    )
                )

            # Sprint 86.5 — Macroarea 3 LLM Coding
            # Quorum 2-de-3 ortogonal usando 3 fuentes coding independientes:
            # SWE-bench Verified, HumanEval+, MBPP+. Anti-gaming UC Berkeley
            # se aplica al normalizar (gaming_detected) y luego al consensuar.
            self._cross_validate_coding(slug, fuentes_data, quorum_results)

            all_results[slug] = quorum_results
            result.modelos_procesados[slug] = quorum_results

        return all_results

    # Sprint 86.5: 3 fuentes coding ortogonales
    CODING_OFFICIAL_SOURCES = ("swe_bench", "human_eval", "mbpp")

    def _cross_validate_coding(
        self,
        slug: str,
        fuentes_data: dict[str, dict[str, Any]],
        quorum_results: list[QuorumResult],
    ) -> None:
        """
        Quorum 2-de-3 sobre fuentes coding (SWE-bench/HumanEval+/MBPP+).

        Diseno:
          - Cada fuente reporta 1 metrica numerica principal:
              swe_bench       -> verified_score
              human_eval      -> pass_at_1
              mbpp            -> pass_at_1
          - NO se cross-validan entre si (escalas distintas) sino que
            se persisten como campos separados via `data_extra.coding`.
          - Sin embargo, el QUORUM DE PRESENCIA en >=2 de 3 fuentes
            coding es lo que activa el dominio coding_llms del modelo.
          - El flag `gaming_detected` viene precomputado del extract.
            Si TRUE en SWE-bench, se NO suma confianza coding.
        """
        # Quorum de presencia coding (¿aparece en >=2 fuentes coding?)
        coding_presence_votes = [
            FuenteVote(f, True if f in fuentes_data else None)
            for f in self.CODING_OFFICIAL_SOURCES
        ]
        if sum(1 for v in coding_presence_votes if v.has_data) >= 1:
            coding_presence_qr = self.validator.validate(
                field_name="coding.presence",
                field_type=FieldType.PRESENCE,
                votes=coding_presence_votes,
            )
            quorum_results.append(coding_presence_qr)

    # ------------------------------------------------------------------
    # Paso 5: extracción de persistibles
    # ------------------------------------------------------------------

    def _extract_persistible(
        self,
        all_quorum_results: dict[str, list[QuorumResult]],
        result: PipelineRunResult,
    ) -> None:
        """
        Identifica modelos que pasaron quorum de presence + tienen al
        menos 1 campo más con quorum.
        """
        for slug, qrs in all_quorum_results.items():
            presence_qr = next((qr for qr in qrs if qr.field_name == "presence"), None)
            if not presence_qr or not presence_qr.is_persistable:
                continue

            persistible_fields: dict[str, Any] = {}
            for qr in qrs:
                if qr.field_name == "presence":
                    continue
                if qr.is_persistable:
                    persistible_fields[qr.field_name] = qr.consensus_value

            if persistible_fields:  # debe tener ≥1 campo además de presence
                result.modelos_persistibles[slug] = {
                    "slug": slug,
                    "fields": persistible_fields,
                    "presence_confidence": presence_qr.confidence_score,
                    "confirming_sources": presence_qr.confirming_sources,
                }

        # Sprint 86.5: enriquecer persistibles con data_extra.coding
        # cuando el modelo aparezca en >=1 fuente coding, agregamos su
        # bloque coding al persistible para que se sirva via data_extra.
        for slug, persistible in result.modelos_persistibles.items():
            self._enrich_with_coding(slug, persistible, all_quorum_results.get(slug, []))

    # ------------------------------------------------------------------
    # Paso 5.5: enriquecer métricas single-source (Sprint 86.4.5 Bloque 2)
    # ------------------------------------------------------------------

    def _enrich_with_metrics(
        self,
        modelos_por_fuente: dict[str, dict[str, dict[str, Any]]],
        result: PipelineRunResult,
    ) -> None:
        """
        Sprint 86.4.5 Bloque 2 — puebla los 6 campos métricos del Catastro
        usando el `field_mapping.yaml` declarativo.

        Tolerante a fallos: si el yaml no se puede cargar o aplicar, NO
        aborta el pipeline. Loggea warning y registra en `result.metrics`
        el flag `metrics_extraction_failed=True` para que Memento lo capture.

        Mutaciones:
          - `result.modelos_persistibles[slug]["fields"]` agrega los 6 campos
          - `result.metrics_extracted[slug]` recibe el dict de métricas
        """
        if not result.modelos_persistibles:
            logger.info("[catastro_pipeline] Paso 5.5 skip: sin persistibles")
            return

        try:
            mapping = load_field_mapping()
        except FieldMappingError as e:
            logger.warning(
                f"[catastro_pipeline] Paso 5.5 SKIP: "
                f"field_mapping_load_failed err={e}"
            )
            result.metrics["metrics_extraction_failed"] = True
            result.metrics["metrics_extraction_error"] = str(e)
            return

        try:
            extracted = apply_field_mapping(
                modelos_persistibles=result.modelos_persistibles,
                modelos_por_fuente=modelos_por_fuente,
                mapping=mapping,
            )
            result.metrics_extracted = extracted
        except FieldMappingError as e:
            logger.warning(
                f"[catastro_pipeline] Paso 5.5 PARTIAL FAILURE: "
                f"field_mapping_apply_failed err={e}"
            )
            result.metrics["metrics_extraction_failed"] = True
            result.metrics["metrics_extraction_error"] = str(e)
            return

        # Métricas resumen para observabilidad
        n_modelos = len(extracted)
        n_with_4_plus = sum(
            1 for slug, m in extracted.items()
            if sum(1 for v in m.values() if v is not None) >= 4
        )
        coverage_pct = (
            round(100.0 * n_with_4_plus / n_modelos, 2) if n_modelos else 0.0
        )
        result.metrics["metrics_extraction_failed"] = False
        result.metrics["metrics_modelos_enriched"] = n_modelos
        result.metrics["metrics_modelos_with_4plus_fields"] = n_with_4_plus
        result.metrics["metrics_coverage_pct"] = coverage_pct
        logger.info(
            f"[catastro_pipeline] Paso 5.5 OK · "
            f"enriched={n_modelos} · "
            f"with_4plus_fields={n_with_4_plus} ({coverage_pct}%)"
        )

    def _enrich_with_coding(
        self,
        slug: str,
        persistible: dict[str, Any],
        qrs: list[QuorumResult],
    ) -> None:
        """
        Sprint 86.5: enriquece el persistible con `data_extra.coding`.

        Estructura del bloque coding (Opción A schema delta firmada):
          data_extra:
            coding:
              swe_bench_verified: float | None
              swe_bench_lite: float | None
              human_eval_plus: float | None
              mbpp_plus: float | None
              gaming_detected: bool
              classification:
                tags: list[str]
                primary_strength: str
                confidence: float
                reasoning: str
        """
        # Recoger scores raw del run actual desde modelos_por_fuente cache
        # (los persistibles ya tienen el slug; los datos crudos vinieron del
        # extract_*. Para mantener bajo acoplamiento, leemos del cache que
        # construye _normalize_snapshots, propagado al runtime via attr).
        coding_data = getattr(self, "_coding_cache", {}).get(slug)
        if not coding_data:
            return

        scores_for_classifier = {
            "swe_bench": coding_data.get("swe_bench_verified"),
            "human_eval": coding_data.get("human_eval_plus"),
            "mbpp": coding_data.get("mbpp_plus"),
        }
        # Solo classify si tiene >=1 score
        if not any(v is not None for v in scores_for_classifier.values()):
            return

        try:
            classification = self.coding_classifier.classify(
                modelo_id=slug,
                scores=scores_for_classifier,
                gaming_detected=coding_data.get("gaming_detected", False),
            )
            coding_data["classification"] = {
                "tags": classification.tags,
                "primary_strength": classification.primary_strength,
                "confidence": classification.confidence,
                "reasoning": classification.reasoning,
            }
        except Exception as e:  # noqa: BLE001
            logger.warning(
                f"[catastro_pipeline] coding_classifier crash slug={slug}: {e}"
            )
            coding_data["classification"] = None

        # Sprint 86.6: Anti-gaming v2 cross-area (Visión Quorum 2-de-3)
        # Detecta overfit INTER-fuente: SWE-strong vs Razonamiento general débil
        # u Arena rank bajo. Cita evidencia desde AA (intelligence_index) y
        # LMArena (rank). Lectura desde _modelos_por_fuente_cache (poblado en
        # _normalize_snapshots). Si la cache no existe, evidence quedan en None
        # y la regla NO se dispara (defensa Memento: no rompe pipeline).
        try:
            mpf_cache = getattr(self, "_modelos_por_fuente_cache", {})
            fuentes = mpf_cache.get(slug, {})
            aa_data = fuentes.get("artificial_analysis", {})
            lm_data = fuentes.get("lmarena", {})
            razonamiento = aa_data.get("quality_score")  # AA intelligence_index proxy
            arena_rank = lm_data.get("rank")
            swe_score = coding_data.get("swe_bench_verified")

            is_overfit, evidence = self.coding_classifier.detect_overfit_cross_area(
                swe_score=swe_score,
                razonamiento_score=razonamiento,
                arena_rank=arena_rank,
            )
            coding_data["overfit_suspected"] = is_overfit
            coding_data["overfit_evidence"] = evidence

            # Si overfit detectado, agregar tag al classification
            if is_overfit and coding_data.get("classification"):
                tags = coding_data["classification"].get("tags", [])
                if "coding-overfit-suspected" not in tags:
                    tags.append("coding-overfit-suspected")
                coding_data["classification"]["tags"] = tags
        except Exception as e:  # noqa: BLE001
            logger.warning(
                f"[catastro_pipeline] catastro_overfit_cross_area_detection_failed slug={slug}: {e}"
            )
            coding_data["overfit_suspected"] = False
            coding_data["overfit_evidence"] = {"error": str(e)}

        # Inyectar al persistible
        persistible.setdefault("data_extra", {})["coding"] = coding_data
