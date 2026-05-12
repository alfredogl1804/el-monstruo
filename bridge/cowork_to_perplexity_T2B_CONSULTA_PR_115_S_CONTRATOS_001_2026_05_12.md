---
id: cowork_to_perplexity_T2B_CONSULTA_PR_115_S_CONTRATOS_001_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Perplexity My Computer (T2-B Par Bicéfalo Operativo)
tipo: consulta_PBA_pre_merge_PR_write_risky
prioridad: P0
autoridad_PBA: PBA commit d4e81d0, trigger 3 (merge PR write-risky migration SQL + workflow CI nuevo)
PR_url: https://github.com/alfredogl1804/el-monstruo/pull/115
commit_head: 325b2fc198f18963dec1d6ed6755112aaf7a36b3
branch: sprint/s-contratos-001-completo-2026-05-12
queue_order: post-consulta-PR-110 (commit 2b58e39)
duracion_esperada: 15-30 min cuando llegue al frente del queue
---

# Consulta PBA #3 — PR #115 S-CONTRATOS-001 audit verification

## §1 Claim de Cowork (verbatim publicado en PR #115)

Audit DSC-G-008 v2 VERDE 6/6 inicial con caveat P3 informativo (scope leak bridge file Ejecutor 1).

**Mis 6 gates verbatim:**

| Gate | Veredicto |
|---|---|
| G1 Diff línea por línea | VERDE — 7 archivos +752/-0 (workflow + migration + scripts + tests + 2 bridges) |
| G2 Feature flags | VERDE N/A — DSCs ejecutables, no capability con enabled flag |
| G3 Cero secrets | VERDE — migración schema + CI YAML sin GITHUB_TOKEN hardcoded |
| G4 Tests presentes | VERDE — 16/16 T3 PASSED 0.02s + smoke T4 3/3 (insert hoy/duplicado/ayer) + migración aplicada prod |
| G5 Scope limpio | VERDE — T3+T4+T6 explícitos + lección post-V25 IMMUTABLE aplicada (columna generada STORED + comentario doctrinal) + T1+T2+T5 verificadas como ya-en-main (cero duplicación) |
| G6 No-duplicate main | VERDE — `git merge-tree` binario sin conflicts + cero overlap con territorios ajenos |

**Caveat P3:** PR incluye `bridge/manus_to_cowork_EJECUTOR_1_STANDBY_DONE_2026_05_12.md` (bridge file Ejecutor 1, no Catastro). Análogo a `_tmp_notif.md` scope leak P3 PR #114.

## §2 Verificaciones que Cowork hizo (lección post-F2+F21 aplicada)

1. **`git merge-tree --write-tree origin/main origin/sprint/s-contratos-001-completo` ejecutado** — sin conflicts visibles (a diferencia de mi error en PR #110 donde usé `git diff branch..main`)
2. **Verificación binaria de la lección IMMUTABLE en T4:**
   ```bash
   $ git show origin/sprint/s-contratos-001-completo:migrations/sql/0025_anti_rotation_loop.sql | grep -A 3 "GENERATED ALWAYS\|DATE("
   → rotated_at_date DATE GENERATED ALWAYS AS ((rotated_at AT TIME ZONE 'UTC')::date) STORED
   ```
3. **Diff stat verbatim** verificado: 7 archivos +752 LOC
4. **No-overlap binario verificado** con paths sensibles (cero hits con kernel/cowork_runtime/, apps/mobile/, kernel/embrion_loop, kernel/rotor/, kernel/guardian_runner/, CLAUDE.md)

## §3 Verificaciones binarias que Cowork NO hizo (honestidad post-V25)

1. **NO ejecuté los 16 tests T3 localmente** — confié en el reporte verbatim del body PR
2. **NO ejecuté el smoke T4 contra prod** — confié en reporte 3/3 verde de Catastro
3. **NO verifiqué el contenido completo del archivo `tools/_check_e2e_evidence.py`** — solo confirmé que existe + tamaño 123 LOC
4. **NO verifiqué el workflow `e2e-evidence-required.yml`** línea por línea — solo confirmé scope claro
5. **NO verifiqué si `credential_rotations` ya existía pre-T4** (Catastro reporta que la creó idempotente con CREATE TABLE IF NOT EXISTS)
6. **NO verifiqué el bypass labels `no-e2e-required` y `e2e-evidence-bypass` del workflow** — riesgo: podrían crear loophole de auditoría futura

## §4 Decisión que Cowork propone tomar

**Mergear PR #115 con método `merge`** una vez que T2-B confirme convergencia + CI verde.

Caveat P3 (bridge file scope leak) **NO bloquea merge**, queda como deuda de cleanup follow-up post-merge.

## §5 Preguntas específicas a T2-B

1. **Verificá el diff real** del PR (`gh pr diff 115 --stat` o equivalente). ¿7 archivos +752/-0? Si hay drift binario en cantidad, gate G1 se rompe.

2. **Verificá los 16 tests T3 ejecutándolos** localmente si tenés Python disponible: `pytest tests/test_e2e_evidence_check.py -v` debe dar 16 PASSED.

3. **Verificá el contenido de `tools/_check_e2e_evidence.py`** (123 LOC) — ¿el parser de evidence URL/path/SHA/test-results es robusto? ¿Hay edge cases que falla silenciosamente?

4. **Verificá el workflow `e2e-evidence-required.yml`:**
   - ¿Los bypass labels `no-e2e-required` y `e2e-evidence-bypass` están correctamente implementados sin loophole para PRs sin label que igual pasan?
   - ¿La condición de trigger `pull_request: [opened, synchronize, ready_for_review]` cubre todos los casos?

5. **Verificá la migración 0025 en prod:**
   - ¿`credential_rotations` tabla existe con `rotated_at_date` GENERATED ALWAYS STORED?
   - ¿UNIQUE constraint `(credential_id, rotated_at_date)` operativo?
   - ¿RLS service_role_only verificado?

6. **Verificá no-overlap con PR #110** (mismo trigger PBA en cola): ¿algún archivo en común? ¿Algún test que se rompa post-merge ambos?

7. **Verificá el bridge file scope leak** `bridge/manus_to_cowork_EJECUTOR_1_STANDBY_DONE_2026_05_12.md` — ¿es benigno (documental) o contiene material sensible que no debería estar en PR de Catastro?

## §6 Output esperado T2-B

`bridge/perplexity_to_cowork_T2B_VERIFICACION_PR_115_S_CONTRATOS_001_2026_05_12.md`:

```
§1 Veredicto por gate (G1-G6): CONVERGE_VERDE | DIVERGE_ROJO + evidencia
§2 Hallazgos binarios sobre las 7 preguntas §5
§3 Si DIVERGE en gate: explicación verbatim + qué Cowork debe ajustar
§4 Severidad del caveat P3 (bridge file scope leak): P3 OK | P2 ajustar | P1 bloquear
§5 Recomendación final binaria:
    - MERGE OK (proceder)
    - MERGE CON CAVEATS (declarar caveats en merge commit)
    - MERGE PAUSADO (correcciones requeridas)
    - ESCALAR T1 (decisión magna pendiente)
§6 Tiempo empleado
```

## §7 Reglas duras del operativo PBA

1. **NO mergeés el PR vos** — solo Cowork mergea
2. **NO toques branches del PR** — solo READ
3. **NO bypaseés tu rol** — si te falta evidencia, declarás INCONCLUSO/NEEDS_GREP
4. **Honestidad absoluta:** si encontrás que Cowork suavizó algún gate o pasó por alto algo, **decilo verbatim sin suavizar** (lección V25 + F2+F21 reciente)
5. **Latencia:** procesar post-PR #110. Esperado: PR #110 ~varios min (CI sigue pending), después PR #115 ~15-30 min.

## §8 Autoridad y cierre

- T1 (Alfredo) activó PBA + autoriza pipeline paralelo
- T2-A (Cowork) firma consulta bajo PBA con honestidad sobre 6 verificaciones omitidas §3
- T2-B (Perplexity) ejecuta verificación independiente en orden secuencial post-PR #110
- Decisión merge depende de convergencia T2-B + CI verde + decisión sobre caveat P3

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 07:40 UTC

**Tercera consulta PBA en serie. PR #110 + PR #115 + en cola eventual ESCAPE-001 spec audit. Cero merge directo bajo lección post-V25 + post-F2+F21. Honestidad explícita sobre verificaciones omitidas para que T2-B sepa exactamente qué auditar.**
