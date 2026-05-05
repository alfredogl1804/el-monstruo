"""
Semilla #33 — Composite scoring con z-scores intra-dominio (Sprint 86 Bloque 4)

Lección a sembrar en la base error_memory:
  Cuando se necesita combinar múltiples métricas heterogéneas (escalas
  distintas, distribuciones distintas) en un score único comparable, el
  patrón state-of-art 2026 NO es ponderación absoluta sobre valores crudos
  — es z-scores normalizados intra-grupo (dominio/categoría) seguidos de
  suma ponderada y mapeo a rango interpretable.

Patrón ganador (Trono Score del Catastro):
  Para cada modelo m en dominio d:
    z_i  = (m.metric_i - mean_d.metric_i) / std_d.metric_i   ∀ i
    score = base + scale * Σ(w_i · z_i)
    score = clamp(score, MIN, MAX)
  Ventajas:
    1. Los pesos solo regulan IMPORTANCIA RELATIVA, no compensan escalas.
    2. El score es interpretable: base = promedio del grupo, scale = 1σ.
    3. Robusto a outliers extremos (porque std crece con ellos).
    4. Comparable entre dominios distintos (mismo significado del score).
  Validado contra: BenchLM.ai (2026), LLM-Stats Score (Apr 2026),
  Artificial Analysis composite scoring.

Salvaguardas obligatorias (anti-autoboicot):
  - Si std == 0 (todos iguales o un solo modelo) → z = 0 para todos.
  - Si grupo tiene < 2 modelos → score = base (modo neutral) + warning.
  - Métrica NULL → z = 0 (neutro), NO crash, tag warning.
  - Validar Σ pesos = 1.0 ± tolerancia; rechazar pesos extra/missing.
  - Bandas de confianza: half_width = scale * (1 - confidence_promedio).

Anti-patrón evitado:
  Multiplicar pesos directamente sobre valores crudos cuando las métricas
  tienen escalas heterogéneas (e.g. quality∈[0,100] vs brand_fit∈[0,1]).
  Eso convierte los pesos en scaling factors implícitos y rompe la
  comparabilidad inter-dominio.

Espejo Python ↔ SQL:
  Cuando una fórmula numérica vive tanto en BD (PL/pgSQL) como en código
  (Python), AMBAS implementaciones MUST mantenerse en sincronía. La de
  Python existe para tests offline reproducibles sin tocar BD; la de SQL
  para que `recompute` sea bulk via UPDATE FROM. Si una cambia, la otra
  debe actualizarse en el MISMO commit y los tests deben capturar la
  divergencia. Usar comentario "Espejo de funcion_X(...)" en ambos.

Mejoras del Audit Cowork al Bloque 3 incorporadas en Bloque 4:
  - error_category enum + failure_rate_observed propagado al batch
    permiten alerting granular sin romper API existente.
  - skip_persist como flag separado de dry_run habilita auditorías
    "compute only" — cálculo Trono sin tocar BD ni siquiera dry-run.
  - curator_alias TEXT[] + GIN index resuelven el matching frágil de
    curadores por id|proveedor|modelo_llm con un campo dedicado.

Origen del aprendizaje:
  Sprint 86 Bloque 4 del Catastro — diseño del Trono Score por dominio
  con re-ranking contextual matemático (SPEC sec 4 + Addendum 86-002).
  Validado en tiempo real contra BenchLM (2026), LLM-Stats Score
  (Apr 2026) y consenso de Cowork audit.

Uso:
  Este archivo describe el payload que el Hilo Ejecutor debe POST-ear
  a https://el-monstruo-mvp.up.railway.app/v1/error-memory/seed con el
  schema oficial. Ver scripts/seed_28_*.py como referencia del schema.

[Hilo Manus Catastro] · Sprint 86 Bloque 4 · 2026-05-04
"""
from __future__ import annotations


SEED_PAYLOAD = {
    "id": "seed-33-zscore-intradominio-sprint86",
    "sprint": "86",
    "bloque": "4",
    "fecha": "2026-05-04",
    "hilo": "manus_catastro",
    "categoria": "patron_algoritmico",
    "titulo": "Composite scoring multi-métrica = z-scores intra-grupo + suma ponderada",
    "contexto": (
        "El Catastro necesita un Trono Score único por modelo dentro de "
        "cada dominio combinando 5 métricas heterogéneas (Q, CE, S, R, BF) "
        "con escalas y distribuciones distintas. La fórmula del SPEC sec 4 "
        "(0.40·Q + 0.25·CE + 0.15·S + 0.10·R + 0.10·BF) sobre valores "
        "crudos sería incorrecta porque las métricas no comparten escala. "
        "El patrón state-of-art 2026 es z-scores normalizados intra-dominio."
    ),
    "patron_recomendado": (
        "Para cada modelo m en dominio d: "
        "z_i = (m.metric_i - mean_d.metric_i) / std_d.metric_i; "
        "score = base + scale * Σ(w_i · z_i); "
        "score = clamp(score, MIN, MAX). "
        "Salvaguardas obligatorias: std=0 → z=0; grupo<2 → score=base + "
        "warning; métrica NULL → z=0 + warning; Σ pesos validado en init. "
        "Espejo Python ↔ SQL para tests offline + recompute bulk en BD."
    ),
    "antipatron_evitado": (
        "Multiplicar pesos directamente sobre valores crudos cuando las "
        "métricas tienen escalas heterogéneas (e.g. quality∈[0,100] vs "
        "brand_fit∈[0,1]). Convierte pesos en scaling factors implícitos "
        "y rompe comparabilidad inter-dominio."
    ),
    "validacion_tiempo_real": [
        "BenchLM.ai (2026) — z-scores por categoría + weighted average",
        "LLM-Stats Score (Apr 2026) — verified weighted composite",
        "Artificial Analysis (2026) — composite scoring intra-categoría",
    ],
    "evidencia_archivos": [
        "scripts/019_sprint86_catastro_trono.sql",
        "kernel/catastro/trono.py",
        "tests/test_sprint86_bloque4.py",
        "scripts/_smoke_trono_sprint86.py",
    ],
    "mejoras_audit_cowork_incorporadas": [
        "error_category enum: db_down|rpc_validation|item_crash|network_timeout|unknown",
        "failure_rate_observed: float propagado a todos los items del batch",
        "skip_persist flag + CATASTRO_SKIP_PERSIST env var",
        "curator_alias TEXT[] + GIN index para matching robusto",
    ],
    "validado_con_tests": 47,
    "validado_smoke": True,
    "version_modulo": "0.86.4",
}


def main() -> None:
    import json
    print(json.dumps(SEED_PAYLOAD, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
