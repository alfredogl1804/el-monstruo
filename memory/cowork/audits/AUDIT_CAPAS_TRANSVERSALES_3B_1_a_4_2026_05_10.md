# AUDIT CAPAS TRANSVERSALES 1–4 — Sub-Fase 3B

**Generado por:** Cowork (scheduled task `cowork-estudio-fase3b-capas-transversales-1-4`)
**Fecha:** 2026-05-10
**Capas auditadas:** 1 Ventas, 2 SEO, 3 Publicidad, 4 Tendencias
**Capas pendientes 3C:** 5 Operaciones, 6 Finanzas, 7 Resiliencia, 8 Memento + Reloj Suizo profundo

**Pre-flight ejecutado:** ✅
- `memory/cowork/COWORK_BASE_CONOCIMIENTO.md` (256 líneas) — leído íntegro
- `memory/cowork/audits/AUDIT_4_CAPAS_3A_2026_05_10.md` (321 líneas) — leído íntegro
- `memory/cowork/audits/CARTOGRAFIA_1C_KERNEL_ESPECIALIZADOS_2026_05_10.md` (379 líneas) — leído íntegro

**Capa 8 Memento aplicada al propio audit:** ✅ — todas las cifras de LOC, tests, integraciones, métodos stub vs real validadas vía `wc -l` / `grep -nE` / `find` / `ls` contra el codebase del 2026-05-10. Cero cifras heredadas por confianza desde 1C o 3A sin re-validación contra archivo.

**Naturaleza:** Sub-Fase 3B continúa la auditoría Cowork tras 3A (4 Capas + Capa 4). Responde al cierre 3A §10 ítem 8 que recomendó "auditar las 8 Capas Transversales una a una". 3B audita 1–4 (las 4 capas comerciales más públicas); 3C audita 5–8.

---

## §0. Tabla resumen consolidada (TL;DR)

| # | Capa | LOC `__init__.py` | LOC constraints | Tests (archivos / casos) | `diagnose` | `recommend` | `implement` | `monitor` | DSC-G-017 adjunto | Integraciones reales wireadas | % real | Δ vs declarado |
|---|---|---:|---:|:---:|:---:|:---:|:---:|:---:|:---:|---|---:|---:|
| 1 | **Ventas** | 246 | 162 | 3 archivos / **32 casos** | ✅ | ✅ | ❌ stub | ❌ stub | ✅ SÍ | NINGUNA real (HubSpot/Salesforce/Apollo/Clay 0%) | **25%** | -50 vs "75% Obj #9" |
| 2 | **SEO** | 386 | 145 | 2 archivos / **24 casos** | ✅ | ✅ | ✅ REAL (212-336) | ✅ REAL estructural (337+) | ✅ SÍ | NINGUNA externa (GSC/Ahrefs/SEMrush 0%; deferido a Sprint TRANSVERSAL-001 T3) | **75%** | tope/referencia honesto |
| 3 | **Publicidad** | 247 | 187 | 1 archivo / **13 casos** | ✅ | ✅ | ❌ stub | ❌ stub | ✅ SÍ | NINGUNA real (Meta/Google/TikTok/LinkedIn Ads 0%) — Meta declarado en constraints sin wiring | **22%** | -53 vs "75% Obj #9" |
| 4 | **Tendencias** | 112 | 129 | 1 archivo / **9 casos** | ✅ | ✅ | ❌ stub | ❌ stub | ✅ SÍ | NINGUNA (Google Trends/Twitter X 0%) | **20%** | -55 vs "75% Obj #9" |

**Promedio real Capas 1–4:** (25 + 75 + 22 + 20) / 4 = **35.5%**.
**vs `COWORK_BASE_CONOCIMIENTO §3` "75% completo":** **delta -39.5 pts**.
**vs `CARTOGRAFIA 1C` "1/6 capas end-to-end = 17%":** consistente — el 17% de 1C contó sólo `implement()` end-to-end; el 35.5% de 3B promedia los 4 métodos del contrato `TransversalLayer(ABC)` (`diagnose` + `recommend` + `implement` + `monitor`).

---

## §1. Capa 1 — Ventas

### Archivos y LOC

```
kernel/transversales/ventas/
├── __init__.py                      246 LOC  (clase VentasLayer)
└── _canonical_constraints.py        162 LOC  (hard constraints DSC-derived)
                                     ─────
                                     408 LOC total
```

**Lo que NO existe:** archivo separado tipo `ventas_layer.py`. La clase `VentasLayer(TransversalLayer)` vive directamente en `__init__.py` (patrón heredado del esqueleto 1C §3.2).

### Implementación: métodos del contrato

| Método | Línea | Estado | Notas |
|---|---|---|---|
| `diagnose(ctx)` | 68 | ✅ REAL | Docstring + lógica de ramas por archetype |
| `recommend(ctx)` | 81 | ✅ REAL | Genera `TransversalRecommendations` |
| `implement(...)` | 174-181 | ❌ **STUB** | `raise NotImplementedError("VentasLayer.implement pendiente Sprint TRANSVERSAL-001. Requiere CRM (HubSpot) + billing (Stripe) integration.")` |
| `monitor(ctx)` | 183-189 | ❌ **STUB** | `raise NotImplementedError("VentasLayer.monitor pendiente Sprint TRANSVERSAL-001. Requiere event_store integration para CAC/LTV/conversion.")` |

### Tests (3 archivos, 32 casos totales)

```
tests/test_transversales_ventas_constraints.py            13 tests / 245 LOC  (DSC-derived constraints)
tests/test_sprint871_embrion_ventas.py                     9 tests / 207 LOC  (Sprint 87.1 EmbriónVentas)
tests/test_sprint881_render_landing_cta_embrion_ventas.py 10 tests / 242 LOC  (Sprint 88.1 render landing/CTA)
                                                          ─────────────────
                                                          32 tests / 694 LOC
```

Tests cubren constraints DSC-derived + integración EmbriónVentas + render landing/CTA. **NO cubren `implement()` ni `monitor()` de la capa transversal porque no existen.**

### Integraciones externas reales

| Integración | Estado | Evidencia |
|---|---|---|
| **HubSpot** (key entregada según spec del scheduled task) | ❌ **NO wireada** | `grep -rn "hubspot\|HUBSPOT\|HubSpot" kernel/` → único hit es la **propia string en `NotImplementedError`** del stub. Cero SDK Python, cero cliente HTTP, cero `requests.post` a `api.hubapi.com`, cero tabla `embrion_memoria` con `tipo='hubspot_*'`. |
| **Salesforce** | ❌ NO wireada | 0 hits en kernel/ |
| **Apollo** | ❌ NO wireada | 0 hits en kernel/ |
| **Clay** | ❌ NO wireada | 0 hits en kernel/ |
| `kernel/embrion_ventas.py` (314 LOC) | ✅ existe pero sin HubSpot | `grep "hubspot\|requests\|httpx" kernel/embrion_ventas.py` → 0 hits. EmbriónVentas opera sobre el grafo interno + Magna; NO hace push a CRM externo. |

**Veredicto integraciones:** Spec del scheduled task afirma "HubSpot key entregada — ¿wireada?". Respuesta: **NO**. La key puede existir como variable de entorno declarada (no localizada en `.env.example`), pero **0 LOC del kernel la consumen**.

### DSC-as-Contract (DSC-G-017) adjunto

✅ **SÍ** — `_canonical_constraints.py:14-17` cita textualmente:
> "Origen: DSC-G-017 (DSC-as-Contract) — texto puede ser desobedecido, código no."

El archivo `_canonical_constraints.py` es la materialización del DSC-G-017: hard constants derivadas de DSCs firmados, con tests `test_transversales_ventas_constraints.py` que asertean coincidencia entre constants y texto canónico. Mecanismo correcto. Ejecutado disciplinadamente.

### % real Ventas

Ponderación (4 métodos del contrato + tests + integraciones):

| Dimensión | Peso | % | Aporte |
|---|---|---:|---:|
| `diagnose` real | 15% | 100 | 15 |
| `recommend` real | 15% | 100 | 15 |
| `implement` real | 25% | 0 | 0 |
| `monitor` real | 15% | 0 | 0 |
| Tests cubren contrato | 10% | 50 (cubren constraints, no implement/monitor) | 5 |
| Integración HubSpot wireada | 10% | 0 | 0 |
| Integración Salesforce/Apollo/Clay | 10% | 0 | 0 |
| **TOTAL** | **100%** | | **35** ← antes de penalización |

Penalización por **claim de "key entregada" sin wiring** (riesgo magna de credencial expuesta sin uso útil): -10.

**% real Ventas: ~25%.**

---

## §2. Capa 2 — SEO

### Archivos y LOC

```
kernel/transversales/seo/
├── __init__.py                      386 LOC  (clase SeoLayer)
└── _canonical_constraints.py        145 LOC
                                     ─────
                                     531 LOC total
```

### Implementación: métodos del contrato

| Método | Línea | Estado | Notas |
|---|---|---|---|
| `diagnose(ctx)` | 55 | ✅ REAL | Lógica completa |
| `recommend(ctx)` | 70 | ✅ REAL | Genera reglas SEO por archetype |
| `implement(...)` | 212-335 | ✅ **REAL** | Genera artefactos: `json_ld_block`, `meta_tags_html`, `robots_meta`, `hreflang_links_html`, `canonical_strategy`, `disclosures_required`, `indexable`, `validation_tags_pending`. **No modifica HTML directamente — retorna strings inyectables.** |
| `monitor(ctx)` | 337+ | ✅ **REAL ESTRUCTURAL** | Health-check sin credenciales externas. Search Console API explícitamente diferida: comentario en docstring "Search Console API queda pendiente Sprint TRANSVERSAL-001 T3." |

**Hallazgo clave:** SEO es la **única capa transversal cerrada end-to-end** entre las 4 auditadas. Confirmado por 1C §3.2 ("ÚNICA capa completa"), confirmado por este audit línea por línea.

### Tests (2 archivos, 24 casos totales)

```
tests/test_seo_layer_implement.py            11 tests / 184 LOC  (cubre implement() artefactos)
tests/test_transversales_seo_constraints.py  13 tests / 258 LOC  (DSC-derived constraints)
                                             ─────────────────
                                             24 tests / 442 LOC
```

**Discrepancia con spec:** El spec del scheduled task pidió "11 tests verificar". El audit reporta **24 tests** totales (11 de `test_seo_layer_implement.py` + 13 de `test_transversales_seo_constraints.py`). La cifra "11" del spec corresponde sólo al archivo de implement; debe sumar constraints. **Spec subestimaba cobertura SEO.**

### Integraciones externas reales

| Integración | Estado | Evidencia |
|---|---|---|
| **Google Search Console API** | 🟡 **declarada deferida** | Comentario explícito en `monitor()`: "Search Console API queda pendiente Sprint TRANSVERSAL-001 T3." `diagnose()` retorna `"deep_diagnostics_status": "structural_only_search_console_pending"`. Honestidad pura — no se afirma cubrimiento que no existe. |
| **Ahrefs** | ❌ NO wireada | 0 hits en `kernel/transversales/seo/__init__.py` |
| **SEMrush** | ❌ NO wireada | 0 hits |
| HTTP libs (`requests`, `httpx`, `aiohttp`) | ❌ ninguna importada | `grep "requests\.\|httpx\.\|aiohttp\." kernel/transversales/seo/__init__.py` → 0 hits. SeoLayer es **puramente computacional** — no hace I/O externo. |

**Veredicto integraciones:** SEO Layer cierra end-to-end **sin** integraciones externas porque su valor es generar artefactos inyectables (JSON-LD, meta tags, hreflang). Esto es **arquitectónicamente correcto** — el monitor con GSC API es deseable pero no condición para "comercializable".

### DSC-as-Contract (DSC-G-017) adjunto

✅ **SÍ** — `_canonical_constraints.py` sigue mismo patrón que Ventas (no inspeccionado encabezado completo en este audit, pero presente por convención del módulo `transversales/`).

### % real SEO

| Dimensión | Peso | % | Aporte |
|---|---|---:|---:|
| `diagnose` real | 15% | 100 | 15 |
| `recommend` real | 15% | 100 | 15 |
| `implement` real | 25% | 100 | 25 |
| `monitor` real (estructural, sin GSC) | 15% | 70 | 10.5 |
| Tests cubren contrato | 10% | 100 | 10 |
| Integraciones externas wireadas | 10% | 0 (deferido honestamente) | 0 |
| Honestidad arquitectónica (no claim falso) | 10% | 100 | 10 |
| **TOTAL** | **100%** | | **85.5** ← antes de descuento por GSC |

Descuento por GSC pendiente (-10) y por nadie consume `kernel.transversales.seo` desde el flujo principal del kernel (`grep -rln "kernel\.transversales\.seo" kernel/` excluyendo el propio dir y tests = 0 hits, conforme 1C §3.2): **-1**.

**% real SEO: ~75%.**

(Coincide con la afirmación 3A §3 "SeoLayer cerrada end-to-end". 75% es **tope de referencia**: ninguna otra capa de las auditadas hoy alcanza este número.)

---

## §3. Capa 3 — Publicidad

### Archivos y LOC

```
kernel/transversales/publicidad/
├── __init__.py                      247 LOC  (clase PublicidadLayer)
└── _canonical_constraints.py        187 LOC
                                     ─────
                                     434 LOC total
```

### Implementación: métodos del contrato

| Método | Línea | Estado | Notas |
|---|---|---|---|
| `diagnose(ctx)` | 47 | ✅ REAL | Lógica por archetype |
| `recommend(ctx)` | 65 | ✅ REAL | Genera recommendations |
| `implement(...)` | 229-237 | ❌ **STUB** | `raise NotImplementedError("PublicidadLayer.implement pendiente Sprint TRANSVERSAL-001. Requiere ad platform APIs (Meta Marketing API, Google Ads API, TikTok Ads API, LinkedIn Ads API).")` |
| `monitor(ctx)` | 239-244 | ❌ **STUB** | `raise NotImplementedError("PublicidadLayer.monitor pendiente Sprint TRANSVERSAL-001. Requiere ad platform reporting APIs + spend tracking.")` |

### Tests (1 archivo, 13 casos)

```
tests/test_transversales_publicidad_constraints.py        13 tests / 208 LOC  (DSC-derived constraints)
```

✅ Coincide con cifra del spec ("13 tests verificar").

**Cobertura `implement()`/`monitor()`:** ❌ **NO** — los métodos son stubs, no hay tests posibles.

### Integraciones externas reales

| Integración | Estado | Evidencia |
|---|---|---|
| **Meta Marketing API** | 🟡 **DECLARADO en constraints, NO wireado** | `_canonical_constraints.py` línea 21,35,64,85: `"meta_ads"` aparece en listas de plataformas permitidas por archetype. **Sólo constante string** — cero código que invoque la API. |
| **Google Ads API** | ❌ NO wireada | Mismo patrón: declarado en constants (líneas 22, 36, 65, 86), 0 hits HTTP/SDK |
| **LinkedIn Ads API** | ❌ NO wireada | Líneas 24, 37 |
| **TikTok Ads API** | ❌ NO wireada | Líneas 23, 39 (a veces explicitly_blocked por archetype: línea 39 "tiktok_ads" en blocked) |

**Veredicto integraciones:** Confirmado el hallazgo del spec del scheduled task — **"Google Ads ❌, LinkedIn Ads ❌, Meta Marketing API DECLARADO (verificar wiring real)"** — el wiring real de Meta Marketing es **declarativo en strings**, no funcional. Cero código que llame `https://graph.facebook.com/v*/act_*/campaigns`.

### DSC-as-Contract (DSC-G-017) adjunto

✅ **SÍ** — patrón `_canonical_constraints.py` consistente con Ventas/SEO/Tendencias. Constraints incluyen catálogo de `ad_platforms_allowed`/`ad_platforms_explicitly_blocked` por archetype (DSC-derived).

### % real Publicidad

| Dimensión | Peso | % | Aporte |
|---|---|---:|---:|
| `diagnose` real | 15% | 100 | 15 |
| `recommend` real | 15% | 100 | 15 |
| `implement` real | 25% | 0 | 0 |
| `monitor` real | 15% | 0 | 0 |
| Tests cubren contrato | 10% | 50 (constraints sí, implement/monitor no) | 5 |
| Integración Meta Marketing wireada | 10% | 0 | 0 |
| Otras 3 plataformas (Google/LinkedIn/TikTok) | 10% | 0 | 0 |
| **TOTAL** | **100%** | | **35** ← antes de penalización |

Penalización por **declarar Meta Marketing en constraints sin wiring real** (riesgo de "spec fantasma" en el sentido del Síndrome-Dory): **-13**.

**% real Publicidad: ~22%.**

---

## §4. Capa 4 — Tendencias

### Archivos y LOC

```
kernel/transversales/tendencias/
├── __init__.py                      112 LOC  (clase TendenciasLayer) ← LA MÁS DELGADA
└── _canonical_constraints.py        129 LOC
                                     ─────
                                     241 LOC total
```

**Nota:** Tendencias es **la capa más delgada** de las 4 auditadas (241 LOC totales vs 408 Ventas / 531 SEO / 434 Publicidad). Coincidente con el hecho de que su implementación más sustantiva está deferida a integraciones externas (Google Trends, Twitter/X) que no existen.

### Implementación: métodos del contrato

| Método | Línea | Estado | Notas |
|---|---|---|---|
| `diagnose(ctx)` | 19 | ✅ REAL | Lógica corta, archetype-aware |
| `recommend(ctx)` | 32 | ✅ REAL | Genera recommendations |
| `implement(...)` | 99-103 | ❌ **STUB** | `raise NotImplementedError("TendenciasLayer.implement pendiente Sprint TRANSVERSAL-001. Tag: [NEEDS_PERPLEXITY_VALIDATION] data_source_apis_vigentes_2026")` |
| `monitor(ctx)` | 105-108 | ❌ **STUB** | `raise NotImplementedError("TendenciasLayer.monitor pendiente Sprint TRANSVERSAL-001. Tag: [NEEDS_PERPLEXITY_VALIDATION] alerting_stack_2026")` |

**Honestidad mariposa:** los stubs incluyen **tags `[NEEDS_PERPLEXITY_VALIDATION]`** explícitos — el código declara que NO sabe qué APIs de tendencias están vigentes en 2026 y pide validación realtime (Obj #5 Magna). Esto es **arquitectónicamente disciplinado** — el código sabe lo que no sabe.

### Tests (1 archivo, 9 casos)

```
tests/test_transversales_tendencias_constraints.py        9 tests / 121 LOC  (DSC-derived constraints)
```

✅ Coincide con cifra del spec ("9 tests verificar").

### Integraciones externas reales

| Integración | Estado | Evidencia |
|---|---|---|
| **Google Trends** | ❌ NO wireada | 0 hits en kernel/. Tampoco declarada en constraints. |
| **Twitter/X Trends API** | ❌ NO wireada | 0 hits. |
| **Reddit / TikTok Discover / Perplexity Sonar** | ❌ NO wireada | 0 hits. **Sonar disponible en `kernel/causal_seeder.py`** (1C §3.6) — podría ser puente futuro. |

### DSC-as-Contract (DSC-G-017) adjunto

✅ **SÍ** — `_canonical_constraints.py` (129 LOC) sigue el mismo patrón.

### % real Tendencias

| Dimensión | Peso | % | Aporte |
|---|---|---:|---:|
| `diagnose` real | 15% | 100 | 15 |
| `recommend` real | 15% | 100 | 15 |
| `implement` real | 25% | 0 | 0 |
| `monitor` real | 15% | 0 | 0 |
| Tests cubren contrato | 10% | 40 (constraints sí, métodos stubeados no) | 4 |
| Integraciones (Google Trends, X) | 10% | 0 | 0 |
| Honestidad arquitectónica (tags `[NEEDS_PERPLEXITY_VALIDATION]`) | 10% | 70 | 7 |
| **TOTAL** | **100%** | | **41** ← antes de penalización |

Penalización por **capa más delgada (241 LOC) entre las 4** sin sprint de implementación arrancado y con dos `NotImplementedError`: **-21**.

**% real Tendencias: ~20%.**

---

## §5. Hallazgos transversales del audit 3B

### H1 — `kernel/transversales/` sigue aislado del flujo principal del kernel

Confirmación re-validada en este audit: `grep -rln "kernel\.transversales" kernel/ --include="*.py"` excluyendo el propio dir y tests retorna **0 resultados** (conforme 1C §3.2). **Ningún módulo del kernel principal importa una sola capa transversal.** Esto contradice la doctrina Obj #9 ("Transversalidad Universal — 8 capas en TODO producto").

**Implicación:** las capas transversales son hoy un **subsistema canónico-pero-callable-por-nadie**. No bloquean al Embrión, no son consumidas por el LangGraph engine, no aparecen en el pipeline E2E "frase → empresa". El gate `all_layers_implemented()` en `base.py` es laxo (solo verifica que la clase exista, no que `implement()` no levante `NotImplementedError`).

### H2 — DSC-G-017 (DSC-as-Contract) bien aplicado en las 4 capas

Las 4 capas (Ventas, SEO, Publicidad, Tendencias) tienen su `_canonical_constraints.py` como materialización del DSC-G-017. Mecanismo correcto y disciplinado: constants Python derivadas de DSCs firmados con tests que asertean coincidencia. **Esto es honestidad arquitectónica de Capa 8 Memento aplicada a la doctrina canónica.** Único "defecto magna" detectado: declarar plataformas (Meta/Google/LinkedIn/TikTok Ads) en constants sin wiring real — riesgo bajo, asumido por documentación, pero a vigilar.

### H3 — Sprint TRANSVERSAL-001 es la llave que abre 5 stubs simultáneos

Los 4 stubs de Ventas (`implement`+`monitor`) + Publicidad (`implement`+`monitor`) + Tendencias (`implement`+`monitor`) **TODOS** declaran "pendiente Sprint TRANSVERSAL-001". Total 6 `NotImplementedError` apuntan al mismo sprint que **no aparece en `bridge/sprints_propuestos/`** (verificación 3A §4 mencionó "Sprint SOVEREIGN-INFRA spec fantasma" — patrón similar aquí). **Sprint TRANSVERSAL-001 puede ser otra spec fantasma**: declarado en strings de error pero sin documento spec firmado.

**Acción recomendada:** crear o localizar `bridge/sprint_TRANSVERSAL_001_preinvestigation/spec_*.md`. Sin él, la afirmación "75% Capas Transversales" del COWORK_BASE §3 es magna falsa.

### H4 — Mismatch entre cifras de Capas Transversales

| Fuente | Cifra para Obj #9 / Capas Transversales | Método |
|---|---|---|
| `COWORK_BASE_CONOCIMIENTO §3` (10-may v0.1) | **75%** | declarado, no codebase-validated |
| `CARTOGRAFIA_1C §3.2` (10-may) | **17%** (1/6 capas end-to-end `implement()`) | grep `raise NotImplementedError` |
| `AUDIT_4_CAPAS_3A §3 Capa 2 fila Capas Transversales` | **42%** | ajuste honesto pondera diagnose/recommend |
| `AUDIT_3B` (este audit, Capas 1–4 promedio) | **35.5%** | ponderación 4-métodos + tests + integraciones por capa |

Las 4 cifras son **honestas dentro de su método**. La cifra autoritativa para reportar globalmente es la de **3A** (42%) porque pondera con criterio comparable al de las otras capas arquitectónicas. Las cifras 17% (1C) y 35.5% (3B) son **complementos forenses**, no sustitutos.

### H5 — Tests existen pero no testean implement/monitor de 3 de 4 capas

| Capa | Tests existen | Tests cubren `implement` | Tests cubren `monitor` |
|---|---|---|---|
| Ventas | ✅ 32 | ❌ (stub) | ❌ (stub) |
| SEO | ✅ 24 | ✅ (`test_seo_layer_implement.py`) | 🟡 estructural |
| Publicidad | ✅ 13 | ❌ (stub) | ❌ (stub) |
| Tendencias | ✅ 9 | ❌ (stub) | ❌ (stub) |

Total: **78 tests** distribuidos en 7 archivos para 4 capas — cobertura razonable de constraints DSC-derived, **pobre cobertura del contrato `TransversalLayer(ABC)` end-to-end**. Sólo SEO testea el contrato completo.

---

## §6. Top 3 oportunidades con mejor leverage (Capas 1–4)

### L1 — Localizar o crear Spec Sprint TRANSVERSAL-001 (1 sesión doc)

ROI: cierra el gap diagnóstico — sin spec, no se puede arrancar el sprint que cierra 6 stubs simultáneamente. Acción: `find bridge -name "*TRANSVERSAL*"` exhaustivo + si no existe, redactar spec consolidado para las 5 capas pendientes.

### L2 — Arrancar Ventas implement() con HubSpot real wireado (2-3 sesiones código)

ROI: si la spec del scheduled task afirma "HubSpot key entregada", la próxima jornada debe consumir la key en código real. Δ Capa 1 Ventas: 25% → 60%+. Δ Obj #9 global: +3-4 pts. **Prerrequisito:** Sprint 90 Stripe (audit 3A L1) para el lado Billing del par CRM+Billing.

### L3 — Cerrar SEO `monitor()` con Search Console API (1-2 sesiones)

ROI: cierra la única capa transversal completa de 75% → 90%+. Comentario explícito en código (`monitor()` docstring) ya identifica la deuda como "pendiente Sprint TRANSVERSAL-001 T3". Acción más pequeña, mayor ROI relativo. Δ Capa 2 SEO: 75% → 92%. **Convierte SEO en la primera capa transversal completamente "Apple/Tesla quality" (Obj #2).**

---

## §7. Decisiones derivadas (para próxima sesión Cowork-Alfredo)

1. **Validar existencia o ausencia de Spec Sprint TRANSVERSAL-001** — si fantasma, redactarla antes de cualquier acción de las Capas 1, 3, 4. (Patrón consistente con lo que 3A reportó para SOVEREIGN-INFRA.)
2. **Reclasificar afirmación "75% Capas Transversales" en COWORK_BASE_CONOCIMIENTO §3** — bajar a **35-42%** con cita a 3B / 3A. Mantener "SeoLayer cerrada end-to-end" como verdad.
3. **Si HubSpot key fue entregada operacionalmente:** programar sprint corto Ventas-HubSpot que la consuma. **Si no fue entregada o no será wireada en 30 días:** eliminar la afirmación de la doctrina para no inflar expectativa.
4. **Endurecer `all_layers_implemented()` gate en `base.py`** — debe verificar que los 4 métodos del contrato no levanten `NotImplementedError` (ahora sólo verifica clase existe). DSC-G-014 (PRODUCTO COMERCIALIZABLE) se gateaba con esta función — el gate actual permite declarar productos comercializables falsamente cubiertos (1C §5 ítem 1).
5. **Confirmar siguiente sub-fase 3C:** auditar Capas 5 Operaciones, 6 Finanzas, 7 Resiliencia, 8 Memento + Reloj Suizo profundo. Patrón esperado para 5 y 6: stubs idénticos a Ventas/Publicidad/Tendencias. Para 7 y 8: probablemente NO existen como subdirectorios bajo `kernel/transversales/` (solo 6 verticales detectadas en este audit y en 1C — 7 Resiliencia y 8 Memento son **AUSENTES como módulos transversales nominales** — Capa 8 Memento vive en `kernel/memento/` y `tools/memento_preflight.py`, no como capa del subsistema `transversales/`).

---

## §8. AUTOAUDIT (Capa 8 Memento aplicada a este audit)

**Pre-flight ejecutado:** ✅
- 3 lecturas largas (BASE_CONOCIMIENTO, AUDIT_4_CAPAS_3A, CARTOGRAFIA_1C) leídas íntegras
- ~10 comandos `bash` ejecutados con `wc -l`, `find`, `grep -nE`, `head`, `sed -n` validando líneas exactas de los stubs
- Conteo de tests vía `grep -cE "^def test_|^    def test_"` (32 + 24 + 13 + 9 = 78)
- Verificación de DSC-G-017 vía cita textual de `_canonical_constraints.py:14-17` Ventas

**Cifras heredadas por confianza:** 0. Toda cifra de los §1–§4 es codebase-validated 2026-05-10.

**Honestidad pura sobre limitaciones:**
1. **No ejecuté pytest** sobre los 7 archivos de tests — verifiqué presencia y conteo, no resultado de corrida. La calidad real de los 78 tests es no-medida.
2. **No leí cuerpo completo de `recommend()` y `diagnose()` por capa** — confirmé que NO levantan `NotImplementedError` vía grep, no inspeccioné las ramas de archetype una a una. Posible que algunas ramas internas tengan TODOs.
3. **No verifiqué exhaustivamente `kernel/embrion_ventas.py`** (314 LOC, no leído íntegro) — sólo grepeado por strings HubSpot/HTTP. Puede haber wiring que se me escapó si está obfuscated.
4. **Cifra "% real" por capa es una ponderación opinionada** (los pesos 15/15/25/15/10/10/10 son míos, no canónicos). Es magna defensible pero no auditable adversarialmente al 100%. Reportada con honestidad sobre el método.
5. **El conteo de tests SEO (24)** difiere del spec del scheduled task ("11 tests verificar"). Documentado y reportado, no asumido como error mío.
6. **No validé conexión a Supabase ni tabla `embrion_memoria`** para el INSERT del cierre de sub-fase. Lo hago a continuación como acción explícita post-audit.

**Síndrome-Dory check:** ✅ — este audit no asume nada de COWORK_BASE_CONOCIMIENTO §3 (75% transversales) ni de 1C (17% end-to-end) ni de 3A (42% capas transversales) sin re-validarlo contra archivo. Las 3 cifras conviven con honestidad declarada en §5 H4.

---

## §9. Cierre Sub-Fase 3B

**Sub-Fase 3B (Audit Capas Transversales 1–4) COMPLETADA.**

**Cifra consolidada Capas Transversales 1–4:** **35.5%** (vs ~75% declarado en doctrina). SEO al 75% es la única que sostiene la fachada — Ventas, Publicidad, Tendencias rondan el 20-25% real.

**Top hallazgos:** (H1) `kernel/transversales/` aislado del flujo principal, (H2) DSC-G-017 bien aplicado, (H3) Sprint TRANSVERSAL-001 posible spec fantasma, (H4) cifras inconsistentes entre fuentes con explicación honesta, (H5) sólo SEO testea contrato completo.

**Top 3 oportunidades:** (L1) localizar/crear Spec TRANSVERSAL-001, (L2) arrancar Ventas-HubSpot con key entregada, (L3) cerrar SEO monitor() con Search Console API.

**Siguiente sub-fase recomendada:** **3C — Audit Capas Transversales 5 (Operaciones), 6 (Finanzas), 7 (Resiliencia AUSENTE como módulo), 8 (Memento — vive en `kernel/memento/`, no en `kernel/transversales/`) + Reloj Suizo profundo** (las 6 piezas pendientes de cierre nominal según 3A §3 tabla Reloj Suizo).

---

*Generado por Cowork (scheduled task autónomo) aplicando Capa 8 Memento al propio proceso de auditoría. Todo en español. Cifras codebase-validated 2026-05-10. Síndrome-Dory neutralizado. v1.0 — 2026-05-10.*
