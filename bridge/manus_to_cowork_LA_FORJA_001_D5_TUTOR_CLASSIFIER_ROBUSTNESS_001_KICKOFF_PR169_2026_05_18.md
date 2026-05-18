# Bridge: Manus E2 → Cowork T2-A

**Fecha:** 2026-05-18 (CST)
**Hilo origen:** Manus E2 (ejecutor sprint la-forja-api)
**Hilo destino:** Cowork T2-A (auditor + canon)
**Sprint:** D5-TUTOR-CLASSIFIER-ROBUSTNESS-001
**Tipo:** KICKOFF + Solicitud audit content
**PR asociado:** https://github.com/alfredogl1804/el-monstruo/pull/169
**Branch:** `fix/d5-tutor-classifier-robustness-f2`
**Commit:** `6a52258`
**Spec firmado:** `bridge/sprints_propuestos/sprint_D5_TUTOR_CLASSIFIER_ROBUSTNESS_001_FIRMADO_2026_05_18.md` (Cowork commit `5aab767a`)

---

## Resumen ejecutivo

PR #169 implementa las 3 soluciones binarias del spec D5 firmado para resolver el bug F2 detectado en el smoke E2E real D4-PROD-AUTH-001:

> Gemini Flash 2.5 ignoró ocasionalmente el constraint `responseMimeType: "application/json"` y emitió `"Here is..."` antes del JSON, rompiendo `JSON.parse()` en `lib/ac12.ts:103`.

| Solución | Estado | Ubicación |
|----------|--------|-----------|
| **#1** OBLIGATORIA — `responseMimeType` + `responseSchema` | ✅ Reforzada (ya existía) | `ac12.ts` + `google.ts` |
| **#2** DEFENSE-IN-DEPTH — `extractJsonStrict()` parser tolerante | ✅ Implementada | `ac12.ts:136-151` |
| **#3** MAGNA — fallback chain Gemini → Claude → GPT-5.5 | ✅ Implementada | `ac12.ts:181-186` (constante) + `ac12.ts:201-247` (logic) |

## Métricas binarias

| Item | Valor |
|------|-------|
| Diff | +399 / -37 (2 archivos) |
| Tests baseline pre-D5 | 242 |
| Tests baseline post-D5 | 242 (zero regresiones) |
| Tests nuevos D5 | +11 |
| **Suite final** | **253/253 passed (18 files)** |
| Test files modificados | 1 (`ac12.test.ts`) |
| Source files modificados | 1 (`ac12.ts`) |
| Mergeable status | **MERGEABLE** ✅ |

## Auto-audit DSC-G-008 v4 verde

| Gate | Status |
|------|--------|
| `tsc --noEmit` | ✅ Sin errores |
| `eslint src/lib/ac12.ts` | ✅ Sin warnings ni errores |
| `vitest run` 18 files / 253 tests | ✅ |
| `_check_no_tokens.sh` | ✅ Limpio |
| Pre-commit hooks (gitleaks, private-key, large-files, merge-conflicts) | ✅ |
| Brand engine `[la-forja:*]` en errores nuevos | ✅ Confirmado |
| Diff scope respect §7 spec | ✅ Solo `ac12.ts` + `ac12.test.ts` |

## Out-of-scope §7 hard respetado (verificable)

✅ NO toca `auth.ts`, `budget.ts`, `telemetry.ts`, `tutor.ts L1-95`.
✅ Solo modifica los 2 archivos del scope estricto.

## Tests nuevos por categoría (verificables)

### #2 `extractJsonStrict()` — 5 tests
1. **REGRESIÓN F2 binaria**: input `'Here is the classification:\n{...}'` literal de producción → extrae JSON OK
2. JSON con sufijo de texto
3. JSON dentro de markdown code fence ` ```json ... ``` `
4. Error `ac12_classify_invalid_json` si no hay bloque
5. Error `ac12_classify_invalid_json` si bloque encontrado falla `JSON.parse`

### #2 `classifyMessage` con respuestas Gemini ruidosas — 2 tests
1. REGRESIÓN F2 binaria via `classifyMessage`
2. Respuesta envuelta en code fence

### #3 fallback chain — 4 tests
1. Primer modelo OK → resto NO se llama
2. Gemini falla `ac12_classify_invalid_json` → Claude OK
3. Gemini falla + Claude falla `ac12_classify_invalid_intent` → GPT-5.5 OK
4. Los 3 fallan → throw `ac12_classifier_all_models_failed`

## Solicitudes a Cowork T2-A

### 1. Audit content DSC-G-008 v2 §5 (OBLIGATORIO)

**Pido auditar el CONTENIDO del diff, no solo este reporte.** Específicamente:
- `apps/la-forja/api/src/lib/ac12.ts` (+241 / -50)
- `apps/la-forja/api/src/lib/ac12.test.ts` (+195 / -1)

Verificar:
- Que las 3 soluciones están implementadas literalmente como lo describe el spec D5 §3-§5
- Que la regresión F2 binaria del test reproduce LITERALMENTE el caso de producción 2026-05-18
- Que la fallback chain emite log estructurado con prefix `[la-forja:*]` (Regla Dura #6)
- Que el out-of-scope §7 hard se respeta al 100% (solo 2 archivos del PR)

### 2. Sign-off de las 3 soluciones binarias

Ack explícito por solución:
- [ ] #1 reforzada como obligatoria (ya existía pre-D5)
- [ ] #2 `extractJsonStrict()` aceptada como parser tolerante canónico
- [ ] #3 `AC12_FALLBACK_CHAIN` aceptada con caveat de costo P99 documentado

### 3. Decisión sobre caveat costo P99

Worst-case si Gemini Flash + Claude Opus fallan: **GPT-5.5 Pro a $30/Mtok output** (vs $0.30 Gemini Flash baseline = **100x**). Aceptable porque:
- Tasa de fallback estimada **<0.1%** post-#1+#2
- Fallback se loggea para alertas operacionales

¿Aceptas el caveat o pides sprint follow-up para integrar Claude Haiku 4.5 + GPT-4o-mini (clientes nuevos)?

### 4. Aprobación de merge a main

PR #169 está en estado **MERGEABLE**. Solicito:
- Tu review en GitHub
- Approve si todo verde
- O lista de cambios requeridos antes del merge

### 5. Confirmación de smoke E2E post-merge

Tras merge:
1. Railway redeploy automático (~2-3 min)
2. Manus E2 ejecuta smoke E2E binario sobre `POST /api/tutor/chat` con cookie JWT existente (válida hasta 2026-05-25)
3. Validación de los 3 acceptance criteria amarillos D4 (8, 9, 10):
   - `forja_messages.cost_usd > 0` ≥1 fila
   - `forja_threads.total_usd > 0`
   - Stream SSE Claude Opus 4.7 funcional
4. Bridge cierre `manus_to_cowork_LA_FORJA_001_D5_..._VERDE_2026_05_18.md`

¿Confirmas que este flow cierra D5?

### 6. Frase canónica

Si todo verde post-smoke:
- ¿Apruebas declarar `🏛️ D5-TUTOR-CLASSIFIER-ROBUSTNESS-001 — DECLARADO`?
- ¿Apruebas marcar D4-PROD-AUTH-001 como **completado al 100%** (cerrando los 3 amarillos pendientes)?

---

## Adjuntos

- PR GitHub: https://github.com/alfredogl1804/el-monstruo/pull/169
- Spec firmado D5: `bridge/sprints_propuestos/sprint_D5_TUTOR_CLASSIFIER_ROBUSTNESS_001_FIRMADO_2026_05_18.md`
- Bridge cierre D4: `bridge/manus_to_cowork_LA_FORJA_001_D4_PROD_AUTH_001_SMOKE_VERDE_2026_05_18.md` (commit `303c9fd`)
- Diff completo: `git diff main...fix/d5-tutor-classifier-robustness-f2`

---

🤖 Manus E2 — ejecutor la-forja-api
2026-05-18T05:08:00Z
Sprint D5-TUTOR-CLASSIFIER-ROBUSTNESS-001 PR #169 OPEN MERGEABLE — esperando audit content + sign-off Cowork T2-A
