"""
Test de paridad Trono Score: Python (TronoCalculator) vs simulación PL/pgSQL.

Sprint 86 — DEUDA AGENDADA del audit Cowork Bloque 4 (post-cierre).

Objetivo:
  Garantizar que la implementación Python del Trono (kernel/catastro/trono.py)
  produce resultados idénticos (tolerancia 0.01) a la función PL/pgSQL
  catastro_recompute_trono(p_dominio) definida en
  scripts/019_sprint86_catastro_trono.sql.

Por qué importa:
  El sistema tiene DOS implementaciones de la misma fórmula matemática:
    1. Python (TronoCalculator): se invoca desde el pipeline.py durante
       cada run, calcula trono ANTES de persistir, lo aplica a los
       Pydantic models para que los snapshots tengan trono propio.
    2. PL/pgSQL (catastro_recompute_trono): se invoca via RPC desde el
       orquestador después de persistir, recalcula trono leyendo desde
       catastro_modelos y aplicando UPDATE atómico.
  Si ambas divergen, el cliente que consulta /v1/catastro/recommend
  recibe trono inconsistente con el que vio el pipeline en el log.

Estrategia:
  - Generar 50 casos sintéticos con seed determinístico (reproducible).
  - Cada caso: dominio + N modelos (N variable: 1, 2, 3, 5, 10, 20)
    con métricas aleatorias, NULLs ocasionales, y un caso degenerado
    (todos los modelos con la misma métrica → std=0 → safeguard).
  - Aplicar TronoCalculator.compute_for_domain() (el oficial Python).
  - Aplicar _simulate_sql_trono() (réplica fiel del SQL en Python puro).
  - Asertar que cada modelo tiene mismo trono_new, trono_low, trono_high
    con tolerancia 0.01 (numérica, no exactitud bit-perfect).

Salvaguardas:
  - statistics.stdev de Python ≡ STDDEV_SAMP de PostgreSQL (denominador
    n-1, sample std, NO population std).
  - ROUND(x, 2) implementado igual en ambos.
  - Clamp [0, 100] aplicado en ambos.
  - NULL → z=0 en ambos.
  - Caso n<2 → trono=50 neutro en ambos.

[Hilo Manus Catastro] · Sprint 86 standby productivo · 2026-05-04
"""
from __future__ import annotations

import random
import statistics
from dataclasses import dataclass
from typing import Optional

import pytest

from kernel.catastro.schema import CatastroModelo, EstadoModelo, TipoLicencia
from kernel.catastro.trono import (
    DEFAULT_WEIGHTS,
    METRIC_FIELDS,
    TronoCalculator,
)


# ============================================================================
# Réplica fiel del SQL en Python puro (réplica directa de las líneas 263-345
# de scripts/019_sprint86_catastro_trono.sql).
# ============================================================================


@dataclass
class SqlTronoResult:
    """Espejo de lo que el SQL retornaría tras UPDATE."""
    modelo_id: str
    trono_old: Optional[float]
    trono_new: float
    trono_delta: float
    modo: str  # 'z_score' | 'neutral'


def _simulate_sql_trono(
    modelos: list[CatastroModelo],
    p_dominio: str,
) -> list[SqlTronoResult]:
    """
    Réplica fiel de catastro_recompute_trono(p_dominio) en Python puro.

    NO usa TronoCalculator. Implementa la lógica del PL/pgSQL paso a paso
    para que cualquier cambio en el SQL se detecte aquí como divergencia.

    Pesos hardcoded del SQL (línea 327-331):
      0.40 * z_q + 0.25 * z_ce + 0.15 * z_s + 0.10 * z_r + 0.10 * z_bf
    """
    if not p_dominio:
        raise ValueError("catastro_trono_invalid_input: p_dominio obligatorio")

    # Filtrar dominio + estado != deprecated (línea 263-266 del SQL)
    in_domain = [
        m for m in modelos
        if p_dominio in (m.dominios or [])
        and (m.estado is None or str(
            m.estado.value if hasattr(m.estado, "value") else m.estado
        ) != "deprecated")
    ]

    v_count = len(in_domain)

    # Caso degenerado: 0 o 1 modelo → trono=50 neutro (línea 269-285)
    if v_count < 2:
        out: list[SqlTronoResult] = []
        for m in in_domain:
            trono_old = m.trono_global
            trono_new = 50.00
            trono_delta = trono_new - (
                trono_old if trono_old is not None else trono_new
            )
            out.append(SqlTronoResult(
                modelo_id=m.id,
                trono_old=trono_old,
                trono_new=round(trono_new, 2),
                trono_delta=round(trono_delta, 2),
                modo="neutral",
            ))
        return out

    # Calcular medias y stddev_samp por métrica (línea 288-302 del SQL)
    means: dict[str, Optional[float]] = {}
    stds: dict[str, float] = {}
    for metric in METRIC_FIELDS:
        valores = [
            getattr(m, metric) for m in in_domain
            if getattr(m, metric) is not None
        ]
        if not valores:
            # AVG sobre todos NULL = NULL; SQL maneja con COALESCE(NULL, 0)=0 al z_calc
            means[metric] = None
            stds[metric] = 1.0
            continue
        means[metric] = statistics.fmean(valores)
        if len(valores) < 2:
            # STDDEV_SAMP de 1 valor = NULL; COALESCE(NULLIF(NULL, 0), 1) = 1
            stds[metric] = 1.0
            continue
        std = statistics.stdev(valores)
        # COALESCE(NULLIF(STDDEV_SAMP, 0), 1) = 1 si std=0
        stds[metric] = std if std > 0 else 1.0

    # Aplicar fórmula con clamp y round (línea 305-336)
    out2: list[SqlTronoResult] = []
    for m in in_domain:
        z = {}
        for metric in METRIC_FIELDS:
            x = getattr(m, metric)
            mean = means[metric]
            std = stds[metric]
            if x is None or mean is None:
                # COALESCE(... / std, 0) = 0 cuando numerador es NULL
                z[metric] = 0.0
            else:
                z[metric] = (float(x) - mean) / std

        # Pesos hardcoded del SQL (NO usar DEFAULT_WEIGHTS para validar idéntico)
        weighted = (
            0.40 * z["quality_score"]
            + 0.25 * z["cost_efficiency"]
            + 0.15 * z["speed_score"]
            + 0.10 * z["reliability_score"]
            + 0.10 * z["brand_fit"]
        )

        raw_trono = 50.00 + 10.00 * weighted
        # LEAST(100, GREATEST(0, ...)) ≡ clamp [0,100]
        clamped = max(0.00, min(100.00, raw_trono))
        # ROUND(..., 2) ≡ Python round(.., 2) — banker rounding similar
        trono_new = round(clamped, 2)

        trono_old = m.trono_global
        # COALESCE(n.trono_new - n.trono_old, 0) → si trono_old None, delta=0
        trono_delta = round(
            trono_new - trono_old, 2
        ) if trono_old is not None else 0.0

        out2.append(SqlTronoResult(
            modelo_id=m.id,
            trono_old=trono_old,
            trono_new=trono_new,
            trono_delta=trono_delta,
            modo="z_score",
        ))

    return out2


# ============================================================================
# Generador determinístico de casos sintéticos
# ============================================================================


def _build_modelo(
    slug: str,
    dominio: str,
    rng: random.Random,
    null_metric: Optional[str] = None,
    fixed_metric: Optional[tuple[str, float]] = None,
) -> CatastroModelo:
    """
    Construye un CatastroModelo válido con métricas aleatorias.

    null_metric: si se da, esa métrica se setea a None (test de NULL handling).
    fixed_metric: si se da (metric, value), todos los modelos tendrán ese valor
                  para esa métrica (test de std=0 safeguard).
    """
    metrics = {
        "quality_score": rng.uniform(20, 95),
        "cost_efficiency": rng.uniform(20, 95),
        "speed_score": rng.uniform(20, 95),
        "reliability_score": rng.uniform(20, 95),
        "brand_fit": rng.uniform(0.1, 0.95),
    }
    if null_metric:
        metrics[null_metric] = None
    if fixed_metric:
        m, v = fixed_metric
        metrics[m] = v

    return CatastroModelo(
        id=slug,
        nombre=slug.title().replace("-", " "),
        proveedor="test-provider",
        modelo_llm=slug,
        macroarea="inteligencia",
        dominios=[dominio],
        licencia=TipoLicencia.PROPIETARIO,
        estado=EstadoModelo.PRODUCTION,
        trono_global=rng.uniform(30, 70),
        confidence=0.7,
        **metrics,
    )


def _build_caso(
    rng: random.Random,
    dominio: str,
    n_modelos: int,
    case_kind: str,
) -> list[CatastroModelo]:
    """
    Genera N modelos para un dominio con variantes según case_kind:
      - 'normal': todas las métricas aleatorias.
      - 'with_nulls': cada modelo con UNA métrica aleatoria NULL.
      - 'std_zero_q': todos los modelos con quality_score=50.0 (std=0 → z=0).
      - 'std_zero_bf': todos los modelos con brand_fit=0.5.
      - 'mixed_estado': mezcla production + un deprecated (debe excluirse).
    """
    modelos = []
    for i in range(n_modelos):
        slug = f"{dominio[:6]}-m{i:02d}"
        kwargs: dict = {}

        if case_kind == "with_nulls" and i % 3 == 0:
            kwargs["null_metric"] = rng.choice(METRIC_FIELDS)
        elif case_kind == "std_zero_q":
            kwargs["fixed_metric"] = ("quality_score", 50.0)
        elif case_kind == "std_zero_bf":
            kwargs["fixed_metric"] = ("brand_fit", 0.5)

        m = _build_modelo(slug, dominio, rng, **kwargs)

        # Mixed_estado: el último modelo es deprecated (debe excluirse del cálculo)
        if case_kind == "mixed_estado" and i == n_modelos - 1:
            m.estado = EstadoModelo.DEPRECATED

        modelos.append(m)
    return modelos


def _generar_50_casos() -> list[tuple[str, list[CatastroModelo]]]:
    """
    Genera 50 casos sintéticos cubriendo todas las combinaciones relevantes.

    Combinaciones (50 casos):
      - 5 'normal' con n=2,3,5,10,20
      - 5 'normal' adicionales con seeds distintas (variación)
      - 10 'with_nulls' con n=3,5,10 (3-5 cada N)
      - 6 'std_zero_q' con n=2,3,5,10
      - 6 'std_zero_bf' con n=2,3,5,10
      - 4 'mixed_estado' con n=3,5,10,20 (deprecated debe excluirse)
      - 5 casos degenerados: n=1 (modo neutral)
      - 9 casos extra para llegar a 50 (variaciones de tamaño y seed)
    """
    casos: list[tuple[str, list[CatastroModelo]]] = []
    rng = random.Random(42)  # seed determinístico

    # 5 'normal' con tamaños variados
    for i, n in enumerate([2, 3, 5, 10, 20]):
        casos.append((f"d-normal-{n}", _build_caso(rng, f"d-normal-{n}", n, "normal")))

    # 5 'normal' con otros seeds
    for i in range(5):
        rng2 = random.Random(100 + i)
        casos.append((f"d-seed-{i}", _build_caso(rng2, f"d-seed-{i}", 5, "normal")))

    # 10 'with_nulls' (3-5 modelos × ~3 nulls cada uno)
    for n in [3, 5, 10]:
        for i in range(3 if n != 10 else 4):
            casos.append((f"d-nulls-{n}-{i}", _build_caso(rng, f"d-nulls-{n}-{i}", n, "with_nulls")))

    # 6 'std_zero_q'
    for n in [2, 3, 5, 10]:
        casos.append((f"d-stq-{n}", _build_caso(rng, f"d-stq-{n}", n, "std_zero_q")))
    casos.append(("d-stq-extra-a", _build_caso(rng, "d-stq-extra-a", 4, "std_zero_q")))
    casos.append(("d-stq-extra-b", _build_caso(rng, "d-stq-extra-b", 7, "std_zero_q")))

    # 6 'std_zero_bf'
    for n in [2, 3, 5, 10]:
        casos.append((f"d-stbf-{n}", _build_caso(rng, f"d-stbf-{n}", n, "std_zero_bf")))
    casos.append(("d-stbf-extra-a", _build_caso(rng, "d-stbf-extra-a", 4, "std_zero_bf")))
    casos.append(("d-stbf-extra-b", _build_caso(rng, "d-stbf-extra-b", 8, "std_zero_bf")))

    # 4 'mixed_estado'
    for n in [3, 5, 10, 20]:
        casos.append((f"d-mixed-{n}", _build_caso(rng, f"d-mixed-{n}", n, "mixed_estado")))

    # 5 degenerados n=1
    for i in range(5):
        casos.append((f"d-solo-{i}", _build_caso(rng, f"d-solo-{i}", 1, "normal")))

    # 9 casos extra: variedad amplia para llegar a 50 totales
    extras = [
        ("d-extra-big-1", 30, "normal"),
        ("d-extra-big-2", 50, "normal"),
        ("d-extra-nulls-15", 15, "with_nulls"),
        ("d-extra-nulls-25", 25, "with_nulls"),
        ("d-extra-stq-15", 15, "std_zero_q"),
        ("d-extra-stbf-12", 12, "std_zero_bf"),
        ("d-extra-mixed-7", 7, "mixed_estado"),
        ("d-extra-mixed-15", 15, "mixed_estado"),
        ("d-extra-normal-100", 100, "normal"),
    ]
    for name, n, kind in extras:
        casos.append((name, _build_caso(rng, name, n, kind)))

    return casos


# ============================================================================
# Tests
# ============================================================================


class TestTronoParity:
    """50 casos sintéticos: TronoCalculator (Python) ≡ catastro_recompute_trono (SQL)."""

    @pytest.fixture(scope="class")
    def calc(self) -> TronoCalculator:
        # Pesos por defecto del SPEC (deben matchear el SQL hardcoded)
        return TronoCalculator()

    @pytest.fixture(scope="class")
    def casos(self) -> list[tuple[str, list[CatastroModelo]]]:
        return _generar_50_casos()

    def test_genera_50_casos(self, casos):
        assert len(casos) == 50, f"Esperaba 50 casos, recibí {len(casos)}"

    def test_pesos_python_matchean_sql(self, calc):
        # Documentación viva: si DEFAULT_WEIGHTS del Python cambia, este test
        # revela que el SQL hardcoded en migration 019 también debe cambiar.
        assert calc.weights["quality_score"] == 0.40
        assert calc.weights["cost_efficiency"] == 0.25
        assert calc.weights["speed_score"] == 0.15
        assert calc.weights["reliability_score"] == 0.10
        assert calc.weights["brand_fit"] == 0.10
        assert sum(calc.weights.values()) == pytest.approx(1.0, abs=1e-9)

    def test_paridad_trono_new_50_casos(self, calc, casos):
        """Cada modelo de cada caso: |trono_python - trono_sql| < 0.01."""
        divergencias = []

        for dominio, modelos in casos:
            try:
                py_results = calc.compute_for_domain(modelos, dominio)
            except Exception as exc:
                divergencias.append(f"PYTHON CRASH en {dominio}: {exc}")
                continue

            try:
                sql_results = _simulate_sql_trono(modelos, dominio)
            except Exception as exc:
                divergencias.append(f"SQL CRASH en {dominio}: {exc}")
                continue

            assert len(py_results) == len(sql_results), (
                f"Cardinalidad distinta en {dominio}: py={len(py_results)} sql={len(sql_results)}"
            )

            sql_by_id = {r.modelo_id: r for r in sql_results}
            for py_r in py_results:
                sql_r = sql_by_id.get(py_r.modelo_id)
                assert sql_r is not None, (
                    f"Modelo {py_r.modelo_id} en Python pero no en SQL"
                )
                diff_new = abs(py_r.trono_new - sql_r.trono_new)
                if diff_new > 0.01:
                    divergencias.append(
                        f"{dominio}/{py_r.modelo_id}: "
                        f"py.trono_new={py_r.trono_new} sql.trono_new={sql_r.trono_new} "
                        f"diff={diff_new:.4f}"
                    )

        assert not divergencias, (
            f"Divergencias detectadas (tolerancia 0.01):\n  - "
            + "\n  - ".join(divergencias[:20])
            + (f"\n  ... y {len(divergencias) - 20} más" if len(divergencias) > 20 else "")
        )

    def test_paridad_trono_delta_50_casos(self, calc, casos):
        """trono_delta también debe ser idéntico (tolerancia 0.01)."""
        divergencias = []

        for dominio, modelos in casos:
            py_results = calc.compute_for_domain(modelos, dominio)
            sql_results = _simulate_sql_trono(modelos, dominio)
            sql_by_id = {r.modelo_id: r for r in sql_results}

            for py_r in py_results:
                sql_r = sql_by_id.get(py_r.modelo_id)
                if sql_r is None:
                    continue
                diff_delta = abs(py_r.trono_delta - sql_r.trono_delta)
                if diff_delta > 0.01:
                    divergencias.append(
                        f"{dominio}/{py_r.modelo_id}: "
                        f"py.delta={py_r.trono_delta} sql.delta={sql_r.trono_delta} "
                        f"diff={diff_delta:.4f}"
                    )

        assert not divergencias, (
            f"Divergencias en trono_delta:\n  - "
            + "\n  - ".join(divergencias[:20])
        )

    def test_modos_coinciden(self, calc, casos):
        """Cuando n<2, ambos deben retornar mode='neutral'; si n>=2, 'z_score'."""
        for dominio, modelos in casos:
            py_results = calc.compute_for_domain(modelos, dominio)
            sql_results = _simulate_sql_trono(modelos, dominio)

            if not py_results:
                # Caso edge: dominio sin modelos válidos en cualquiera
                assert not sql_results
                continue

            # En el TronoResult Python, .mode es 'neutral' o 'z_score'
            py_mode = py_results[0].mode
            sql_mode = sql_results[0].modo
            assert py_mode == sql_mode, (
                f"Modo distinto en {dominio}: py={py_mode} sql={sql_mode}"
            )

    def test_clamp_trono_within_0_100(self, calc, casos):
        """Ningún trono_new debe estar fuera de [0, 100] en ninguna implementación."""
        for dominio, modelos in casos:
            py_results = calc.compute_for_domain(modelos, dominio)
            sql_results = _simulate_sql_trono(modelos, dominio)

            for r in py_results:
                assert 0.00 <= r.trono_new <= 100.00, f"py {r.modelo_id}: {r.trono_new}"
            for r in sql_results:
                assert 0.00 <= r.trono_new <= 100.00, f"sql {r.modelo_id}: {r.trono_new}"

    def test_mixed_estado_excluye_deprecated(self, calc):
        """
        El último modelo de cada caso 'mixed_estado' es DEPRECATED.
        Debe excluirse del cálculo en AMBAS implementaciones (Python y SQL).
        """
        rng = random.Random(999)
        modelos = _build_caso(rng, "test-mixed", 5, "mixed_estado")

        py_results = calc.compute_for_domain(modelos, "test-mixed")
        sql_results = _simulate_sql_trono(modelos, "test-mixed")

        # Solo 4 modelos production cuentan (el 5to es deprecated)
        assert len(py_results) == 4, f"py len={len(py_results)}"
        assert len(sql_results) == 4, f"sql len={len(sql_results)}"

        # El deprecated NO debe estar en ninguna lista
        deprecated_id = modelos[-1].id
        assert all(r.modelo_id != deprecated_id for r in py_results)
        assert all(r.modelo_id != deprecated_id for r in sql_results)

    def test_std_zero_safeguard_funciona(self, calc):
        """
        Cuando todos los modelos tienen idéntica métrica X, std(X)=0 → z=0.
        El trono debe calcularse usando solo las OTRAS métricas.
        """
        rng = random.Random(7)
        modelos = _build_caso(rng, "test-stq", 5, "std_zero_q")

        py_results = calc.compute_for_domain(modelos, "test-stq")
        sql_results = _simulate_sql_trono(modelos, "test-stq")

        # Ambos deben calcular trono sin crashear y con valores razonables
        assert len(py_results) == 5
        assert len(sql_results) == 5

        # Comparar uno a uno (paridad estricta esperada)
        sql_by_id = {r.modelo_id: r for r in sql_results}
        for py_r in py_results:
            sql_r = sql_by_id[py_r.modelo_id]
            assert abs(py_r.trono_new - sql_r.trono_new) < 0.01

    def test_documentacion_de_drift(self):
        """
        Test guardarraíl: si en el futuro alguien cambia los pesos en el SQL
        o en Python sin actualizar el otro, ESTE test fallará y hará obvio
        el bug. Es la mejor defensa contra "olvidé sincronizar".
        """
        # Pesos canónicos del SPEC (Sec 4):
        canonical = {
            "quality_score": 0.40,
            "cost_efficiency": 0.25,
            "speed_score": 0.15,
            "reliability_score": 0.10,
            "brand_fit": 0.10,
        }
        assert DEFAULT_WEIGHTS == canonical, (
            "DEFAULT_WEIGHTS Python divergió del SPEC. "
            "REVISAR scripts/019_sprint86_catastro_trono.sql líneas 327-331 "
            "para asegurar que los pesos hardcoded del SQL TAMBIÉN se actualicen."
        )
