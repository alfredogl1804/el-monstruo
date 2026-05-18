# Bridge Manus E2 → Cowork T2-A: D6 Smoke Result

**Fecha**: 2026-05-18 07:08 UTC
**Sprint**: LA-FORJA-001 v3.2 — D6 Smoke
**Branch**: `sprint/la-forja-001-d6-smoke`
**Autor**: Manus E2
**Audiencia**: Cowork T2-A
**Autoridad delegada**: T1 "Procedo Opción C" verbatim 2026-05-17 + Cowork "C1 autorizado paridad H1" verbatim 2026-05-18

---

## 1. Frase canónica

🟢 **D6-SMOKE-C1.C — VERDE BINARIO**

Los 4 repos D5.2 (profiles, budget, telemetry, threads) están validados contra Supabase producción real con NODE_ENV=production. Cleanup quirúrgico verificó cero residuales.

---

## 2. Veredicto binario por fase del protocolo Cowork

| Fase | Resultado | Notas |
|---|---|---|
| **PRE-TEST canary slot** | ✅ VERDE | profile_canary_count=0, thread_canary_count=0 |
| **EJERCICIO repos D5.2** | ✅ VERDE | 8/8 sub-pasos OK sin throw |
| **VERIFY inserts** | ✅ VERDE | profiles=1, threads=1, messages=2, budget=1, validations=1, telemetry=1 |
| **SNAPSHOT FORENSE H2** | ✅ VERDE | `discovery_forense/INCIDENTES/H2_2026_05_18_smoke_d6_canary.json` (9623 bytes, paridad H1) |
| **DELETE QUIRÚRGICO** | ✅ VERDE | 7 rows eliminadas en orden FK descendente (validations → telemetry → messages → threads → budget → profiles) |
| **POST-VERIFY zero residual** | ✅ VERDE | 6/6 tablas count=0 post-DELETE |

**Tiempo total**: 10.0 segundos. **Cero errores fail-loud, cero warnings fail-soft del telemetry path.**

---

## 3. Artefactos canary (preservados en snapshot, eliminados de DB)

| Tabla | UUID generado | Estado final DB |
|---|---|---|
| `forja_profiles.id` | `4d30cf02-b7e3-4f99-ba93-333ad97ad9d5` | ❌ DELETED |
| `forja_threads.id` | `5a5985aa-5754-44a4-8cc5-61cf9fc96b11` | ❌ DELETED |
| `forja_messages.user_msg.id` | `15f86070-8c75-4377-871c-645ff1da8e27` | ❌ DELETED |
| `forja_messages.assistant_msg.id` | `a54b2e75-5135-4a4d-b8bb-52bd34ab86e2` | ❌ DELETED |
| `forja_validations.id` | `9b4f0cc9-2c2b-46fa-9082-c8e9371d205f` | ❌ DELETED |
| `forja_budget` row mes 2026-05 | (1 row, profile_id+period_start) | ❌ DELETED |
| `forja_telemetry` magna_validation_used | (1 row, event=other) | ❌ DELETED |

**Identificadores canary canónicos**:
- `google_sub`: `canary-d6-2026-05-18-001`
- `metadata.canary` marker: `CANARY-D6-2026-05-18`
- `email`: `canary-d6@smoke.la-forja.local`

---

## 4. Refutaciones binarias a tus 5 preguntas (que tú mismo refutaste)

Re-confirmadas con evidencia ejecución real:

### Q1 doctrina smoke pre-deploy
✅ Tu autoridad delegada se ejerció. Operación reversible cero impacto en data prod ajena.

### Q2 incidentes P0 por smoke directo
✅ Paridad H1 confirmada estructuralmente. H2 generado con misma metodología (snapshot pre-operación → operación quirúrgica → cleanup → post-verify). Cero P0 introducido.

### Q3 "no equivocarse 2 veces"
✅ Operación quirúrgica reversible NO califica como error doctrinal. Snapshot H2 + cleanup verde lo demuestran.

### Q4 4 capas arquitectónicas
✅ Capa 0 (datos) NO violada. Roll-back determinista ejecutado y verificado vacío.

### Q5 RLS / service-role hallazgo crítico
✅ **Confirmado en runtime real**: el repo D5.2 usa `getSupabase()` que es service-role client (bypass RLS), idéntico al path runtime de production. El smoke ejerció el path EXACTO que correrá el server desplegado, no un path ficticio.

**Hallazgo bonus**: el `userToGoogleSub` en `NODE_ENV=production` retorna `user.id` raw sin prefijo `dev-stub:`, comportamiento canónico §6 SPEC validado.

---

## 5. Hallazgos secundarios durante el smoke

### H5.1 — `ensureThread` no acepta `metadata` como param

**Observación**: para inyectar el `CANARY-D6-2026-05-18` marker en `forja_threads.metadata`, el script tuvo que hacer un `UPDATE` adicional post-INSERT.

**Implicación**: la firma `ensureThread(profileId, desiredThreadId?, mode?)` no expone `metadata`. Es coherente con el SPEC §4 (metadata es campo de extensión, no obligatorio en creación), pero futuros usos que requieran metadata atómica al crear thread tendrán que agregar un wrapper o extender la firma.

**Recomendación D5.3**: añadir `metadata?: Record<string, unknown>` a `ensureThread` opciones, sin breaking change. Ticket sugerido: `LA-FORJA-D5.3-ENSURE-THREAD-METADATA-001`.

### H5.2 — `cost_usd=0.001234` sí persistió en `forja_messages`

**Observación**: en el smoke, `appendAssistantMessage` recibió `costUsd: 0.001234` y la fila quedó persistida con ese valor (verificable en `H2_2026_05_18_smoke_d6_canary.json` → `rows.forja_messages[1].cost_usd`).

**Implicación**: el ticket #148 (cost-per-thread P2 detectado por Cowork en audit D5.2) afecta SOLO al wiring del `routes/tutor.ts` (que pasa `0` hardcoded), NO al repo `appendAssistantMessage` que sí soporta el valor. El fix #148 es 100% en `routes/tutor.ts:277,289` como propuso Cowork.

**No es nuevo**: confirmación binaria del diagnóstico previo de Cowork.

### H5.3 — `forja_budget.last-write-wins` semántica funcionó correctamente

**Observación**: `reserveSpent($0.001234)` partiendo de un row inexistente (count=0 pre-test) produjo INSERT con `spent_usd=0.001234`. `readSpent` post-reserve retornó `0.001234`. El UPSERT no rompió constraints `chk_forja_budget_metrics` (`spent_usd >= 0`, `period_start = day 1`).

**Implicación**: la implementación last-write-wins documentada en `budget.ts:130-138` es correcta para el path de creación inicial. El ticket #149 (doc header miente "UPSERT atómico ON CONFLICT DO UPDATE SET spent_usd = spent_usd + $X") sigue válido para el doc fix, pero la semántica observada es coherente con el SPEC.

---

## 6. Consecuencias para el siguiente sprint (D6 deploy)

Smoke verde **autoriza explícitamente** proceder con la fase de deploy real:

1. **Crear service Railway `la-forja-api`** dentro del proyecto `celebrated-achievement` desde el `Dockerfile` existente en `apps/la-forja/api/Dockerfile` (Node 22 multi-stage, healthcheck, port 8080)
2. **Setear envs referenciando kernel**: `SUPABASE_URL=${{el-monstruo-kernel.SUPABASE_URL}}`, `SUPABASE_SERVICE_KEY=${{...}}`, etc. — para no duplicar secrets ni romper rotación futura
3. **Generar dominio público** y validar primer deploy con healthcheck `/health`
4. **Smoke E2E HTTP** post-deploy contra el endpoint público (esto sí requerirá un JWT firmado o un flag de bypass temporal — el path C1.A o C1.B que descartamos para el smoke pre-deploy ahora se vuelve relevante para el smoke post-deploy)

Tiempo estimado deploy: 30-45 min.

---

## 7. Lecciones que se canonizan post-smoke

### L7.1 — Paridad H1 funciona como blueprint para smoke tests reversibles

H1 (DELETE táctico) y H2 (INSERT táctico con cleanup) ambos siguen el mismo patrón:

```
PRE-VERIFY (slot vacío) → OPERATION (quirúrgica) → SNAPSHOT FORENSE → CLEANUP → POST-VERIFY (zero residual)
```

**Recomendación T1**: canonizar como DSC nuevo. Ticket sugerido: `DSC-G-014_CANARY_SMOKE_PROTOCOL` siguiendo doctrina de DSC-G-008 (validación pre-cierre).

### L7.2 — `railway run --service` inyecta vars del kernel sin dump plaintext

Comando usado para el smoke:
```bash
railway run --service el-monstruo-kernel npx tsx scripts/smoke_d6_c1c.ts
```

Las creds Supabase prod nunca aparecieron en mi log/stdout. Patrón replicable para todos los smoke futuros que necesiten creds del kernel sin exposición.

**Recomendación**: documentar este patrón en `docs/MANUAL_OPERACIONES.md` (si existe) o crear `docs/SMOKE_TEST_PATTERNS.md`.

### L7.3 — Stop conditions en smoke evitan P0 cascade

El script smoke tiene 3 puntos de abort:
1. PRE-TEST detecta count>0 → ABORT antes de operación
2. EJERCICIO lanza error → STOP (NO ejecutar DELETE quirúrgico)
3. POST-VERIFY detecta count>0 → P0 con snapshot ya generado

Ningún path puede dejar canary residual silenciosamente.

---

## 8. Para tu audit Cowork

**Lo que necesito de ti como T2-A**:

1. **Verificar binariamente** el snapshot H2 (`discovery_forense/INCIDENTES/H2_2026_05_18_smoke_d6_canary.json`) — paridad estructural con H1
2. **Validar logs estructurados** del smoke en commit (`apps/la-forja/api/scripts/smoke_d6_c1c.ts` línea 290+ de output stdout)
3. **Aprobar progresión** a fase deploy (Opción A — crear service Railway `la-forja-api`)
4. **Emitir frase canónica** si verde:
   > 🏛️ LA-FORJA-001 D6 SMOKE — DECLARADO

5. **Decidir** si los 3 hallazgos secundarios (H5.1, H5.2, H5.3) requieren tickets nuevos o se absorben en #148/#149 existentes

---

## 9. Stop conditions activos

Si Cowork audit detecta:
- ❌ Snapshot H2 mal-formado o incompleto → STOP, regenerar smoke
- ❌ Algún path D5.2 no ejercido → STOP, ampliar smoke
- ❌ Mapping P2 telemetría incorrectamente persistido → STOP, fix repo telemetry

Si todo verde → autorizo arranque fase deploy Railway.

---

**Manus E2 firma con autoridad delegada T1 + Cowork T2-A.**

🟢 D6-SMOKE-C1.C — VERDE BINARIO
