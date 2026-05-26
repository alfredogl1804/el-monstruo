<!-- lint_strict -->

# Sprint TRANSVERSAL-001 — Capas Transversales: implement() + monitor() reales

**Estado:** Propuesto
**Hilo principal:** Manus Ejecutor (con accesos a APIs externas + Supabase + Railway)
**Hilo soporte:** Cowork (diseño + audit pre-cierre + tests sin red)
**ETA recalibrado:** 4-6 horas reales distribuidas en 7 sub-sprints (cada uno 30-60 min con velocity Manus demostrada)
**Objetivo Maestro:** #9 (Transversalidad) + #2 (Apple/Tesla) + #11 (Resiliencia agéntica) + #15 (Memoria soberana)
**Bloqueos pre-arranque:** acceso Supabase válido + credenciales para Stripe/HubSpot/Meta/Google/LinkedIn/Search Console + Railway env vars actualizadas
**Resultado esperado:** las 6 Capas Transversales tienen `implement()` y `monitor()` reales (no `NotImplementedError`), `validation_log` table operativa en Supabase, dsc_contract_check activado como hook bloqueante.

---

## 0. Procedencia

Sprint TRANSVERSAL-001 cierra el último gap arquitectónico entre el aparato de gobernanza (DSC-G-014 + G-017 + V-001 + 6 Capas con DSC-as-Contract) y producto comercializable real. Hoy el repo tiene:

- **6 Capas Transversales** con `diagnose()` + `recommend()` implementados parcialmente (data estructural, no copy final).
- **`implement()` y `monitor()` en `NotImplementedError`** porque requieren credenciales externas que el Cowork sandbox no tiene.
- **DSC-V-001 decorator** instalado pero sin `validation_log` table en Supabase todavía.
- **42+ tags `[NEEDS_PERPLEXITY_VALIDATION]`** auto-detectables sin resolver.
- **`dsc_contract_check.py`** funcional pero NO activado como hook bloqueante.

Este sprint los cierra a todos.

---

## 1. Audit pre-sprint — Estado actual

Lo que ya existe (verificable por Manus al arrancar):

- `kernel/transversales/{ventas,seo,publicidad,tendencias,operaciones,finanzas}/` con interface canonizada y constants per-vertical.
- `kernel/validation/perplexity_decorator.py` con tests verde local (7/7).
- `kernel/milestones/declare.py` con gates.yaml configurado.
- `tools/{spec_lint,dsc_contract_check,check_perplexity_tags,audit_visual_diff}.py`.
- `migrations/sql/0001_validation_log.sql` listo para aplicar.
- `discovery_forense/CAPILLA_DECISIONES/_dsc_contracts_index.yaml` con 47/47 cobertura.
- 96+ tests verde local (transversales 70 + milestones 13 + audit_visual 3 + spec_lint 6 + dsc_contract_check 4 + perplexity_decorator 7 ≈ 103).

Lo que falta (gaps):

- 6 × `implement()` en `NotImplementedError`.
- 6 × `monitor()` en `NotImplementedError`.
- `validation_log` table NO existe en Supabase production.
- Pre-commit hooks NO incluyen dsc_contract_check todavía.
- 42+ tags Perplexity sin resolver en `validation_log`.
- Workflow `.github/workflows/milestone-declaration-guard.yml` NO pusheado a remoto (limitación GitHub App).

---

## 2. Tareas del Sprint

### Tarea T1 — Aplicar migration validation_log + inyectar SupabaseStorage

**perfil_riesgo:** write-risky

**Descripción:** Aplicar `migrations/sql/0001_validation_log.sql` a Supabase production (proyecto `aiokebmraosaiehqckbo` si no cambió). Después editar boot del kernel para inyectar `SupabaseStorage(supabase_client)` vía `set_default_storage()` antes de cualquier import que use el decorator.

**Solución:**
1. Ejecutar `supabase db push` o psql contra DB URL.
2. Verificar tabla creada: `SELECT count(*) FROM validation_log;` retorna 0.
3. Editar `kernel/main.py` (o equivalente boot) añadiendo:
```python
from kernel.validation import set_default_storage
from kernel.validation._storage_supabase import SupabaseStorage
set_default_storage(SupabaseStorage(supabase_client))
```

**Criterios de cierre:** comando `python -c "from kernel.validation import requires_perplexity_validation; ..."` levanta StaleClaimError contra Supabase real (no contra archivo local). Reproducible artifact en `reports/validation_log_supabase_smoke.json`.

### Tarea T2 — VentasLayer.implement() + monitor() con HubSpot/Stripe

**perfil_riesgo:** write-risky

**Descripción:** Implementar `implement()` para push de pricing tiers a HubSpot Products + setup de Stripe Products/Prices. Implementar `monitor()` para leer events de `event_store` y calcular CAC/LTV/conversion rate per stage.

**Pre-condiciones:** credenciales HubSpot Private App + Stripe API key en Railway env vars.

**Validation magna requerida:** llamar `record_validation(claim_type="hubspot_api_2026", validator="perplexity", evidence_url=...)` ANTES de codificar la integración HubSpot — el decorator levantará si no está validado.

**Criterios de cierre:** `pytest tests/test_ventas_implement_integration.py` pasa contra Stripe test mode + HubSpot sandbox. Reporte JSON en `reports/ventas_implement_smoke.json` con tier IDs creados.

### Tarea T3 — SeoLayer.implement() + monitor() con render integration + Search Console

**perfil_riesgo:** write-safe

**Descripción:** Implementar `implement()` que toma `recommend()` output y produce JSON-LD blocks + meta tags HTML para inyectar en el render pipeline (server-rendered pages). Implementar `monitor()` con Google Search Console API.

**Pre-condiciones:** Search Console API credentials + acceso al render pipeline del Monstruo (probablemente kernel/landing_generator si existe, o crearlo).

**Validation magna requerida:** `record_validation("schema_org_vocabulary_2026", validator="perplexity", ...)` para confirmar que los schema types canonizados (InvestmentOrInvestmentScheme, Event, MedicalDevice) están vigentes.

**Criterios de cierre:** `pytest tests/test_seo_implement_integration.py` pasa generando JSON-LD válido per los 8 verticales. Reporte JSON en `reports/seo_implement_smoke.json`. SeoLayer es la primera Capa que se puede cerrar end-to-end sin credenciales pesadas.

### Tarea T4 — PublicidadLayer.implement() + monitor() con Meta/Google/LinkedIn Ads APIs

**perfil_riesgo:** requiere-coordinacion-humana

**Descripción:** Implementar `implement()` que crea campañas template per ad platform respetando `platforms_allowed`/`platforms_explicitly_blocked` per vertical. NO ejecuta gasto real — modo `paused` por default. Implementar `monitor()` agregando reporting APIs de las 4 plataformas.

**Pre-condiciones:** Meta Marketing API token + Google Ads API token + LinkedIn Ads API token + acceso al Business Manager / Google Ads account / LinkedIn Campaign Manager. **Esta tarea requiere coordinación con Alfredo para confirmar que las campañas en estado `paused` están bien antes de cualquier `active`.**

**Validation magna requerida:** `record_validation` para `cpc_benchmark_2026:<archetype>`, `audience_size_2026:<vertical>`, `ad_formats_2026:<archetype>`, `platform_policy_2026` antes de cualquier creación de campaña.

**Criterios de cierre:** campañas creadas en estado `paused` en cada plataforma, IDs en `reports/publicidad_implement_smoke.json`. Comando `python -m kernel.transversales.publicidad.smoke --all-paused` exit 0.

### Tarea T5 — TendenciasLayer.implement() + monitor() con data feeds

**perfil_riesgo:** write-safe

**Descripción:** Implementar `implement()` que registra subscripciones a data feeds (Polygon explorer webhook para CIP, Google Trends scraper, regulatory feeds RSS). `monitor()` agrega signals y emite alertas según prioridad.

**Pre-condiciones:** API keys donde aplique (Polygon, RSS endpoints), Supabase tabla `trend_signals` (migration nueva).

**Criterios de cierre:** signals reales aterrizan en `trend_signals` para al menos 2 verticales (CIP + LikeTickets). Reporte JSON en `reports/tendencias_implement_smoke.json`.

### Tarea T6 — OperacionesLayer.implement() + monitor() con helpdesk integration

**perfil_riesgo:** write-risky

**Descripción:** Implementar `implement()` que configura support channels per vertical en helpdesk (Intercom o Front). `monitor()` calcula SLA first-response per channel.

**Pre-condiciones:** API key del helpdesk seleccionado.

**Validation magna requerida:** `record_validation("helpdesk_api_2026", ...)` para confirmar SDK actual.

**Criterios de cierre:** support channels configurados para al menos LikeTickets (vertical más urgente, SLA 1h). Reporte JSON en `reports/operaciones_implement_smoke.json`.

### Tarea T7 — FinanzasLayer.implement() + monitor() con accounting + CFDI emitter

**perfil_riesgo:** requiere-coordinacion-humana

**Descripción:** Implementar `implement()` con accounting (Contpaq o Quickbooks API) + CFDI 4.0 emitter para transacciones MX. `monitor()` calcula unit economics tracked per vertical.

**Pre-condiciones:** SAT credentials + accounting API keys. **Coordinación con Alfredo obligatoria para confirmar setup fiscal — operaciones de finanzas reales no se shipan sin firma humana.**

**Validation magna requerida:** `record_validation("tax_rates_2026:<vertical>", ...)` + `record_validation("cfdi_4_canonical_format", ...)`.

**Criterios de cierre:** transacción de prueba en Stripe test mode → CFDI emitido en SAT sandbox. Reporte JSON en `reports/finanzas_implement_smoke.json`.

### Tarea T8 — Activar dsc_contract_check como pre-commit hook bloqueante

**perfil_riesgo:** write-safe

**Descripción:** Editar `.pre-commit-config.yaml` añadiendo hook local que ejecuta `tools/dsc_contract_check.py` sobre archivos staged en `discovery_forense/CAPILLA_DECISIONES/`. Cualquier DSC nuevo sin entry en `_dsc_contracts_index.yaml` (o sin marcador aspirational) bloquea el commit.

**Criterios de cierre:** test sintético: commit con DSC nuevo sin entry → bloqueado. Commit con entry válida → pasa. Reporte JSON en `reports/dsc_contract_check_hook_test.json`.

### Tarea T9 — Resolver los 42+ tags Perplexity en validation_log

**perfil_riesgo:** read-only

**Descripción:** Para cada tag `[NEEDS_PERPLEXITY_VALIDATION]` detectado por `tools/check_perplexity_tags.py`, ejecutar Perplexity query con la pregunta canónica derivada del tag, persistir `record_validation()` con evidence_url. Hacer batch en una sola sesión paralela. NO modifica código del repo — sólo poblar la table.

**Pre-condiciones:** Perplexity API key + `validation_log` table operativa (T1).

**Criterios de cierre:** `tools/check_perplexity_tags.py --json` reporta total de tags pero validation_log tiene registro vigente para cada uno. Comando `python tests/test_all_tags_validated.py` pasa (tarea entrega ese test). Reporte JSON en `reports/perplexity_tags_resolved.json`.

---

## 3. Contratos ejecutables que adjunta

Este sprint NO produce DSCs nuevos — todos los DSCs relevantes ya existen y están enforzados via `_dsc_contracts_index.yaml`. Lo que produce son **implementaciones reales** de los contratos ya canonizados:

| DSC | Contrato existente | Lo que este sprint añade |
|---|---|---|
| DSC-G-014 (PIPELINE != PRODUCTO) | gates.yaml + declare.py | Las 6 Capas con implement+monitor, eliminando `pending_implementation` flags. |
| DSC-V-001 (validación magna) | perplexity_decorator.py | `validation_log` table real en Supabase + 42 tags resueltos. |
| DSC-G-017 (DSC-as-Contract) | dsc_contract_check.py + index | Hook activado bloqueante. |
| DSC-G-002 (7 Capas operativas) | kernel/transversales/ | Implementaciones reales, no NotImplementedError. |
| DSC-CIP-* (CIP es primer producto) | _canonical_constraints.py | Capas operativas para vertical CIP — ruta a producto comercializable real. |

---

## 4. Criterios de cierre verde (Sprint completo)

- Las 9 tareas en exit 0 con artifacts en `reports/`.
- `python -m kernel.milestones.declare pipeline_tecnico_funcional` retorna exit 0 (pytest e2e + coverage 80% + smoke endpoint verde).
- `python -m kernel.milestones.declare producto_comercializable` retorna exit 0 sólo si Alfredo firma `reports/firma_alfredo_producto.sig` validando que el output es Apple/Tesla quality real per vertical.
- `tools/check_perplexity_tags.py --fail-on-found` retorna exit 0 (todos los tags tienen `validation_log` registrado).
- `python tools/dsc_contract_check.py $(find discovery_forense/CAPILLA_DECISIONES -name "DSC-*.md")` retorna exit 0 con 100% cobertura.
- Todos los tests verde: `pytest tests/` pasa.
- Cowork audit content (DSC-G-008 v2) verifica artifacts antes de declarar verde.
- Sprint cierra con frase canónica: `🏛️ TRANSVERSAL-001 — DECLARADO (9/9 verde)` + commit con DSCs actualizados si emergen patrones canonizables.

---

## 5. Owner

**Owner técnico principal:** Manus Ejecutor (T1-T7).
**Owner técnico colateral:** Cowork (T8 + T9 + audit pre-cierre).
**Owner humano final:** Alfredo (firmar T4 paused→active, T7 SAT setup, validacion humana magna pre-PRODUCTO COMERCIALIZABLE).

---

## 6. Trazabilidad

- **Origen:** continuación natural post-canonización del aparato de gobernanza (DSC-V-001, DSC-G-017 100% via index, 6 Capas con DSC-as-Contract).
- **Sprints anteriores que habilitan este:**
  - Sprint S-001 Security Hardening (gitleaks + trufflehog + S-001 a S-006)
  - Sprint Capas Transversales (Ventas, SEO, Publicidad, Tendencias, Operaciones, Finanzas con interface + constants + tests verde)
  - DSC-V-001 firma + decorator (kernel/validation/)
  - Index DSC→contrato (_dsc_contracts_index.yaml)
- **Sprint que destraba después:** S-CONTRATOS-001 (los 5 DSCs aspiracionales restantes con contrato pendiente: S-003, S-004, S-005, G-005, G-007 → linters AST, cleanup tools, integraciones de los Sabios, integraciones AI verticales).

---

## 7. Pre-flight check antes de arrancar (Manus DEBE correr esto)

```bash
# 1. Verificar repo limpio y synced con main
git status && git pull origin main

# 2. Verificar tests verde local (96+ tests, sin red)
python tests/test_perplexity_decorator.py
python tests/test_transversales_ventas_constraints.py
python tools/dsc_contract_check.py $(find discovery_forense/CAPILLA_DECISIONES -name "DSC-*.md")

# 3. Verificar credenciales Supabase + Railway env vars
echo $SUPABASE_DB_URL  # No empty
echo $RAILWAY_TOKEN     # No empty

# 4. Probar conexión a Supabase
psql "$SUPABASE_DB_URL" -c "SELECT 1;"

# 5. Confirmar acceso a las APIs externas que cada tarea requiere (T2, T4, T6, T7)
```

Si cualquier paso falla, NO arrancar. Reportar al bridge antes de seguir.

---

**Firma propuesta de cierre:** sólo válida si las 9 tareas pasan + `python -m kernel.milestones.declare producto_comercializable` retorna exit 0 + Alfredo firma firma_alfredo_producto.sig. Sin esas tres condiciones, el cierre se queda en AMARILLO PARCIAL DECLARADO (DSC-G-012). El sprint puede pausar parcialmente con tareas write-risky/coordinacion-humana diferidas — DSC-G-012 acepta cierre parcial honesto.
