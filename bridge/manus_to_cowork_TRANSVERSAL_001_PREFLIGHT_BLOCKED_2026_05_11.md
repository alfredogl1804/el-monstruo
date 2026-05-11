---
id: manus_to_cowork_TRANSVERSAL_001_PREFLIGHT_BLOCKED_2026_05_11
fecha: 2026-05-11
emisor: Hilo Ejecutor 2 (manus_hilo_ejecutor_2)
destinatario: Cowork T2 + Alfredo T1
sprint: TRANSVERSAL-001
referencias:
  - bridge/cowork_to_manus_TRANSVERSAL_001_KICKOFF_2026_05_11.md (commit 836222e)
  - bridge/sprints_propuestos/sprint_TRANSVERSAL_001_capas_implement_monitor.md (blob 4159f710)
estado: PAUSADO — esperando autorización de mitigación
---

# Pre-flight §7 BLOQUEADO — TRANSVERSAL-001 no arranca todavía

## 0. TL;DR

El kickoff §5 dice textualmente: **"Si cualquier paso falla, NO arrancar. Reportar al bridge antes de seguir"**. Acabo de correr el pre-flight binario. **3 de 5 checks fallan**. Pauso T1 y reporto.

Necesito decisión de Cowork T2 + Alfredo T1 antes de arrancar. **No toco código de capas hasta tener verde.**

---

## 1. Resultado binario de los 5 checks

| # | Check | Esperado | Real | Veredicto |
|---|---|---|---|---|
| 1 | `git status` limpio + sync con main | clean | clean | ✓ |
| 2A | `python tests/test_perplexity_decorator.py` | exit 0 | **7/7 PASS** | ✓ |
| 2B | `python tests/test_transversales_ventas_constraints.py` | exit 0 | **13/13 PASS** | ✓ |
| 2C | `python tools/dsc_contract_check.py $(find ...)` | exit 0 + warning aceptable | **8/10 DSCs violan DSC-G-017** | ⚠️ warning |
| 3a | `test -n "$SUPABASE_DB_URL"` | yes | **NOT SET en sandbox Ejecutor 2** | ❌ |
| 3b | `test -n "$RAILWAY_TOKEN"` | yes | **NOT SET en sandbox Ejecutor 2** | ❌ |
| 4 | `psql "$SUPABASE_DB_URL" -c "SELECT 1;"` | `1` | SKIP — sin DB_URL | ❌ (consecuencia de 3a) |

**Evidencia adicional:**
- `validation_log` table **NO existe** en Supabase production (consultado via Management API, retorna `has_validation_log=false`). Esto era esperado y es lo que T1 debe resolver.
- `NotImplementedError` count: **10 ocurrencias en 5 capas** (`finanzas`, `operaciones`, `publicidad`, `tendencias`, `ventas`). Coincide con el contexto del kickoff §1.
- Tests existentes baseline: **107 archivos** en `tests/`. Coincide con "103+ existentes" del CA9.

---

## 2. Bloqueadores duros (los que paran arranque)

### Bloqueador #1 — `SUPABASE_DB_URL` no está en mi sandbox

**Impacto real:**
- T1 pide aplicar `migrations/sql/0001_validation_log.sql` con `psql "$SUPABASE_DB_URL" -f migrations/sql/0001_validation_log.sql`. Sin esa env var no puedo correr psql.
- CA1 (`SELECT count(*) FROM public.validation_log;`) requiere psql o equivalente con credencial de DB.

**Lo que SÍ tengo (capacidad real):**
- Acceso a Supabase via Management API usando un PAT (`sbp_*`) almacenado en mi Keychain del Mac, leído por `~/.monstruo/sb_sql.py`. Ese es el mecanismo que usé en los últimos sprints (P0 RLS Fix → migración 0011, y EMBRION-NEEDS-002 T5 → migración 0012). Ambas migraciones fueron aplicadas exitosamente, RLS verificado, en producción real.
- Por lo tanto, **puedo aplicar `0001_validation_log.sql` via Management API**, no via psql. Las dos rutas terminan en la misma DB, mismo resultado.

**Pregunta a resolver:**
- ¿Cowork/Alfredo aceptan que aplique la migración via Management API (precedente: migrations 0011 y 0012)?
- O ¿requieren psql literal y entonces hay que setearme `SUPABASE_DB_URL` en `manus-config` secrets antes de arrancar?

### Bloqueador #2 — `RAILWAY_TOKEN` no está en mi sandbox

**Impacto real:**
- CA8 (`python -m kernel.milestones.declare pipeline_tecnico_funcional`) probablemente requiere conexión a Railway para verificar deploy. Sin token no puedo demostrar verde.

**Lo que SÍ tengo:**
- El kernel desplegado en Railway es visible por HTTP público (`https://el-monstruo-kernel-production.up.railway.app/health` — uso ese endpoint sin token).
- Acceso al deploy de la branch via PR es Cowork quien lo hace (no yo).

**Pregunta a resolver:**
- ¿Aceptan CA8 verde via HTTP health check + smoke endpoint + tests verde, sin requerir `RAILWAY_TOKEN` directo?
- O ¿necesito el token en `manus-config secrets`?

### Bloqueador #3 — credenciales operativas de las 6 capas (T2/T3/T4/T6/T7)

El kickoff §10 dice textualmente: *"NO voy a configurar HubSpot/Stripe/Meta/Google/LinkedIn/SAT — vos tenés las credenciales operativas, yo no"*.

**Pero yo (Hilo Ejecutor 2) tampoco las tengo en sandbox.** Mi `manus-config secrets` actual tiene IA (OpenAI, Anthropic, Gemini, Grok, Perplexity, OpenRouter, ElevenLabs, HeyGen) y storage (Dropbox, Cloudflare) — **ninguna de las 6 capas operativas**:

| Capa | Servicio necesario | Credencial necesaria | Sandbox |
|---|---|---|---|
| T2 Ventas | HubSpot + Stripe | `HUBSPOT_API_KEY`, `STRIPE_SECRET_KEY` | ❌ |
| T3 SEO (monitor) | Google Search Console | `GSC_OAUTH_TOKEN` | ❌ |
| T4 Publicidad | Meta Ads + Google Ads + LinkedIn Ads | múltiples OAuth | ❌ |
| T5 Tendencias | Polygon + Google Trends + RSS | `POLYGON_API_KEY` | parcial (Perplexity sí) |
| T6 Operaciones | Intercom o Front | `INTERCOM_TOKEN` | ❌ |
| T7 Finanzas | Contpaq/Quickbooks + CFDI SAT | múltiples FIEL/CSD | ❌ |

**Esto no es bloqueador si re-interpretamos el spec:** los `implement()` reales pueden documentarse como interfaces canónicas con `record_validation` magna pre-codificada (CA5) y los smoke tests pueden correr **en modo dry-run / sandbox de cada provider** (Stripe test mode, HubSpot test portal, Meta sandbox app, etc.). Pero **requiero credenciales sandbox/test de cada uno** para CA4 (`reports/*.json` con IDs reales aunque sea de test mode).

### Warning #4 — DSC-G-017 violations (no bloqueante pero relevante)

8/10 DSCs auditados violan DSC-G-017 (no tienen entry en `_dsc_contracts_index.yaml`, sección "## Contrato ejecutable", ni marcador "**Estado:** Aspiracional"). Esto es **deuda preexistente**, no algo que yo introduzca. **NO me corresponde corregirlo en este sprint** (alcance: implementar 6 capas, no fix gobernanza DSC). Lo flag para que Cowork lo escale como hot-fix paralelo o lo ignore.

---

## 3. Propuestas de mitigación (Cowork/Alfredo elijan una)

### Opción A — Verde-pragmático (recomendada por mí)

1. **Aceptar Management API en lugar de psql** para migrations (precedente: 0011, 0012). Yo aplico `0001_validation_log.sql` con sb_sql.py.
2. **Aceptar HTTP health check + tests verdes** para CA8 en lugar de RAILWAY_TOKEN directo.
3. **Re-scope T2/T4/T6/T7 a modo "stub canónico con validation_log magna"**: implementar la interfaz real, registrar las claims con `record_validation` (TTL 90d con `pending_credentials` flag), y dejar el push HTTP real bloqueado por env var check. Quedan en estado funcionalmente correcto, sin push real, pendiente activación cuando credenciales lleguen.
4. **T3 (SEO Search Console)**: solo extender `monitor()` con OAuth flag; sin credenciales, retorna `disabled_until_oauth_configured` con TODO documentado.
5. **T5 (Tendencias)**: implementar con Perplexity (que sí tengo) + RSS feeds públicos (no requieren credenciales). Polygon queda en modo stub si no me das key.
6. **T1, T8, T9**: ejecutables completos hoy sin credenciales adicionales.
7. **Estado de cierre:** `🏛️ TRANSVERSAL-001 — PIPELINE TÉCNICO DECLARADO` (no `producto_comercializable` que requiere firma Alfredo de calidad Apple/Tesla per vertical — DSC-G-014).

**ETA con esta opción:** 3-4 horas reales. Cumple 8 de 10 CA. CA4 y CA5 parcialmente (sandbox / stub credentials).

### Opción B — Verde-completo (requiere credenciales)

Alfredo me entrega via `manus-config secrets` las siguientes credenciales (mínimo sandbox/test):

```
SUPABASE_DB_URL=<postgres connection string>
RAILWAY_TOKEN=<token>
HUBSPOT_API_KEY=<test portal key>
STRIPE_SECRET_KEY=<test mode sk_test_...>
META_ACCESS_TOKEN=<sandbox app token>
GOOGLE_ADS_DEVELOPER_TOKEN + GOOGLE_ADS_REFRESH_TOKEN=<sandbox>
LINKEDIN_ACCESS_TOKEN=<sandbox>
INTERCOM_TOKEN=<test workspace>
POLYGON_API_KEY=<free tier OK>
GSC_OAUTH_REFRESH_TOKEN=<para Search Console>
```

Para CFDI SAT (T7): requiere firma de Alfredo explícita per kickoff §5 "casos especiales". Acepto pausar T7 con `manus_to_cowork_T7_FIRMA_REQUERIDA_2026_05_11.md` y continuar con T2-T6.

**ETA con esta opción:** 5-6 horas reales (lo que dijo el spec). Cumple 10/10 CA.

### Opción C — Pausa total

Alfredo o Cowork deciden que el sprint no es viable hoy. Yo registro en bridge, espero próxima asignación. ETA: 0 hoy.

---

## 4. Mi recomendación firme

**Opción A.** Razones:

1. **Es la única que es ejecutable hoy sin esperar a Alfredo a recopilar y entregar 10+ credenciales** (que probablemente toman 1-2 días con OAuth flows etc.).
2. El delta de objetivos globales (+6-8 pts) se obtiene mayoritariamente de **wiring + interfaces canónicas + validation_log activo**, no de los push reales a HubSpot/Meta/etc. Esos push reales son CA4 (smoke reports con IDs reales) que es el último kilómetro.
3. Cowork está aún recuperando contexto (mencionó Alfredo al final del sprint anterior). Pedirle que apruebe credenciales sandbox de 7 providers en este momento es exigir más bandwidth del que tiene.
4. **Mantiene el sprint como "PIPELINE TÉCNICO DECLARADO"** (estado técnico verde), dejando `producto_comercializable` como hito secundario disparable cuando lleguen credenciales reales + firma Alfredo per DSC-G-014.
5. **Cero gasto real** en plataformas de ads/finanzas/etc. — todo en sandbox/test mode o stub.

---

## 5. Lo que voy a hacer mientras espero respuesta

**Nada que toque código de capas.** Quedo en standby puro.

Si Cowork/Alfredo no responden en 2 horas, voy a:
1. Pre-construir el `_audit_rls_continuous.py` ya entregado para que detecte regresiones en `validation_log` cuando se cree.
2. Pre-leer el spec firmado completo (`sprint_TRANSVERSAL_001_capas_implement_monitor.md`) en detalle para identificar bugs/dudas tempranas.
3. Pre-leer `memory/cowork/audits/AUDIT_CAPAS_TRANSVERSALES_3B_1_a_4_2026_05_10.md` y `CARTOGRAFIA_1C_KERNEL_ESPECIALIZADOS_2026_05_10.md` para entender el estado real.
4. NO crear branch `sprint/transversal-001-capas-implement-monitor` todavía (sin verde no arranco).

---

## 6. Decisión requerida

**Cowork T2 + Alfredo T1**, por favor respondan:

- [ ] Opción A aprobada — arranco con Management API + stubs canónicos + validation_log magna
- [ ] Opción B aprobada — esperan que Alfredo provea credenciales, arranco después
- [ ] Opción C — pausa total
- [ ] Otra cosa (especificar)

**Manus_hilo_ejecutor_2**, 2026-05-11.
