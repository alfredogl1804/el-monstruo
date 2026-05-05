#!/bin/bash
# Commit Sprint 86.4.5 Bloque 2 — anti-Dory disciplined push
set -e
cd /Users/alfredogongora/el-monstruo

echo "=== Stash uncommitted changes ==="
git stash --include-untracked || true

echo "=== Pull rebase ==="
git pull --rebase origin main

echo "=== Pop stash ==="
git stash pop || true

echo "=== Status ==="
git status --short

echo "=== Add files ==="
git add kernel/catastro/sources/field_mapping.yaml \
        kernel/catastro/sources/field_mapping.py \
        kernel/catastro/pipeline.py \
        kernel/catastro/persistence.py \
        tests/test_sprint_86_4_5_bloque2.py \
        requirements.txt

echo "=== Commit ==="
git commit -m "feat(catastro): Sprint 86.4.5 Bloque 2 - enriquecimiento campos metricos

Pobla los 6 campos metricos del Catastro (quality_score,
reliability_score, cost_efficiency, speed_score,
precio_input/output_per_million) usando un mapping declarativo en
field_mapping.yaml.

Arquitectura:
- field_mapping.yaml declara como cada campo se extrae de cada fuente
  con normalizacion opcional (passthrough, minmax, inverse_log,
  derived_from_quorum)
- field_mapping.py implementa el extractor con disciplina Memento
  preflight (warning cuando una fuente esperada no aporta el campo)
- Nuevo Paso 5.5 en pipeline (_enrich_with_metrics) entre
  _extract_persistible y trust_deltas. Tolerante a fallos:
  registra metrics_extraction_failed=True en metrics y continua.
- build_modelo_from_pipeline_persistible extendido para leer los
  6 campos del fields y construir CatastroModelo enriquecido.

Cero cambios SQL: la RPC catastro_apply_quorum_outcome ya acepta
los 6 campos en el INSERT/UPSERT (verificado en migration 019).

Cero cambios en zonas cerradas:
- _extract_persistible / _cross_validate intactos
- coding_classifier / sources del 86.5 intactos
- schema.py manual intacto (Cowork lo deprecara en 86.5/86.6)

Tests: 19 nuevos en test_sprint_86_4_5_bloque2.py
Suite Catastro+Memento+Drift: 443 PASS + 6 skipped (cero regresiones)

Memento preflight (Capa Memento aplicada):
- on_missing=warn por defecto (logs estructurados)
- on_missing=raise opcional para tests/ambientes estrictos
- registro estructurado en logger 'catastro.field_mapping'

PyYAML declarado explicitamente en requirements.txt
(antes transitiva via fastmcp/langchain-core).

[Hilo Manus Memento] - Sprint 86.4.5 Bloque 2 - 2026-05-05"

echo "=== Push ==="
git push origin main

echo "=== Done ==="
git log --oneline -3
