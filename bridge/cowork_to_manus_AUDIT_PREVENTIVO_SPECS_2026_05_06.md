# Audit Preventivo de Specs en Cola — 2026-05-06

**Hilo:** A (Cowork)
**Para:** Manus Hilo Ejecutor + Hilo Catastro
**Naturaleza:** Reporte preventivo + propuestas de fix antes de que Manus retome ejecución
**Disparador:** DSC-G-008 v2 (validar codebase Y specs antes de cierre) + lecciones del incidente P0

---

## Resumen ejecutivo

Audité los 11 specs en `bridge/sprints_propuestos/` por:

1. **Anti-patrones de seguridad** — DSC-S-003/S-004 (defaults con secrets, hardcoded credentials)
2. **Drift respecto a estado post-P0** — referencias a archivos refactorizados, repos archivados, versiones obsoletas
3. **Brand DNA violations** — naming antipatterns (`service/handler/utils/helper/misc`)
4. **Drift de visión** — Catastro-A reconfigurado a 4 catastros post-conversación con Manus, spec aún en versión 3 catastros

### Resultado consolidado

✅ **Buenas noticias:** cero secrets hardcoded en specs, cero `os.environ.get(VAR, "real_secret")`, cero patrones JWT/PAT/sbp_/sk- en specs.

⚠️ **6 issues identificados** — 2 importantes (B, C), 1 drift de visión (D), 3 cosméticos/informativos (A, E, F).

---

## Tabla de issues

| # | Sprint | Línea(s) | Issue | Severidad | Acción propuesta |
|---|---|---|---|---|---|
| **A** | Mobile 1 | 77 | `core/services/` viola Brand DNA / Regla Dura #4 (`NUNCA: service, handler, utils, helper, misc`) | 🟡 Cosmético | Renombrar a `core/mensajeros/` o `core/transmisores/` con identidad |
| **B** | Sprint 90 | 13, 41+ | Referencia `like-kukulkan-tickets`. crisol-8 (descubierto en P0) tiene service_role JWT hardcoded — `like-kukulkan-tickets` puede tener patrón similar | 🟠 Importante | Manus audita `like-kukulkan-tickets` por secrets ANTES de arrancar Sprint 90 |
| **C** | Sprint 89, Catastro-A | Schemas ToolEntry / SupplierEntry | Schemas NO explicitan que credenciales viven en env var, no en JSON. Riesgo: replicar patrón del breach P0 al poblar | 🟠 Importante | Agregar nota explícita "credenciales NUNCA en JSON — solo `auth_type` (referencia al método); el secret en env var del proceso" |
| **D** | Catastro-A | Spec entera | Manus + Cowork acordamos reconfiguración a 4 catastros (Modelos + Agentes 2026 + Tools verticales + Suppliers). Spec actual sigue en 3 catastros | 🟠 Drift de visión | Update spec a 4 catastros con interfaces operativas (`find_best`, `peers_of`, `validate_against_spec`) |
| **E** | Sprint 88 | 157 | Nota documentada de la corrupción previa por sub-agente | ✅ Resuelto | Informativo, dejar como registro forense |
| **F** | Catastro-B | Skill `manus-oauth-pattern` | OAuth implementation puede tener antipatrones de defaults con secrets reales | 🟡 Verificar | Cuando se implemente, aplicar DSC-S-003 + DSC-S-004 explícitamente |

---

## Issue A — Mobile 1 línea 77 (Cosmético, Brand DNA)

### Estado actual

```
apps/mobile/lib/
├── main.dart
├── core/
│   ├── transport/
│   │   └── kernel_websocket.dart
│   ├── a2ui/
│   │   └── renderer.dart
│   ├── services/                    # ❌ viola Regla Dura #4 (NUNCA: services)
│   ├── theme/brand_dna.dart
│   ├── widgets/
```

### Fix propuesto

Renombrar `services/` a una alternativa con identidad:

| Opción | Razón |
|---|---|
| `core/mensajeros/` | mensajeros = portadores de información (auth, network, storage) |
| `core/transmisores/` | si solo tiene módulos de comunicación |
| `core/portadores/` | sinónimo más corto |
| `core/herreros/` | si tiene módulos que "construyen" cosas (caching, persistence) |

**Recomendación:** `core/mensajeros/` — abarca el rol semántico amplio que tiene `services/` típicamente (cliente HTTP, auth, telemetry, etc.) sin caer en el genérico prohibido.

Diff sugerido en spec Mobile 1 línea 77:

```diff
-│   ├── services/                    # placeholders, vacíos por ahora
+│   ├── mensajeros/                  # placeholders, vacíos por ahora
```

---

## Issue B — Sprint 90 / `like-kukulkan-tickets` (Importante)

### Contexto

Sprint 90 propone extraer Stripe checkout de `like-kukulkan-tickets/src/components/StripeCheckout.tsx` a paquete npm `@monstruo/checkout-stripe`. El sprint asume que `like-kukulkan-tickets` está limpio.

Pero el incidente P0 demostró que repos del ecosistema pueden tener secrets hardcoded (crisol-8 + biblia-github-motor confirmados). **Sprint 90 debe verificar `like-kukulkan-tickets` antes de arrancar**, especialmente porque toca código de pagos (Stripe = secrets de alta sensibilidad).

### Acción propuesta

Antes de arrancar Sprint 90, Manus ejecuta audit similar al P0:

```bash
gh repo clone <owner>/like-kukulkan-tickets /tmp/audit-likekukulkan
cd /tmp/audit-likekukulkan
gitleaks detect --source . --no-git --report-path /tmp/audit-likekukulkan-report.json
trufflehog filesystem /tmp/audit-likekukulkan --no-update --json
grep -rn "sk_live_\|sk_test_\|whsec_\|pk_live_\|pk_test_" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.env*" .
```

Si encuentra hits → mismo flujo que biblia-github-motor / crisol-8: refactor + rotación + DSC-S-004 enforcement.

Sprint 90 spec se ajusta agregando bloque "0. Audit pre-extracción" obligatorio:

```diff
+## 0. Audit pre-extracción (obligatorio post-P0)
+
+Antes de extraer código, Manus audita `like-kukulkan-tickets` por:
+- Stripe keys hardcoded (`sk_live_`, `sk_test_`, `whsec_`, `pk_live_`, `pk_test_`)
+- Anti-patrón DSC-S-004 (defaults con secrets)
+- DSN hardcoded a Supabase / TiDB / cualquier DB
+
+Si encuentra hits → reportar al bridge y rotar antes de proceder. Si limpio → continuar con Tarea 1.
```

---

## Issue C — Schemas ToolEntry / SupplierEntry (Importante)

### Contexto

Sprint 89 línea 117-127 + Catastro-A línea 175-193 definen schemas para `kernel/data/catastro_tools.json` y `catastro_suppliers.json`. Los ejemplos NO incluyen campo `api_key` (correcto), pero la spec NO explicita "credenciales NUNCA en JSON".

Riesgo: cuando Manus pobla 25+ herramientas, puede tentarse a agregar campo `api_key` con el secret real para conveniencia. Eso replicaría el patrón del breach P0.

### Fix propuesto en ambos specs

Agregar sección explícita después del schema:

```diff
+### ⚠️ Reglas de credenciales (DSC-S-001 + DSC-S-003)
+
+- El JSON `catastro_*.json` SOLO contiene metadata pública: `endpoint`, `auth_type`,
+  `rate_limit`, `cost_per_call`, `fallback_tools`, etc.
+- NUNCA incluir el secret real (api_key, JWT, password) en el JSON.
+- El secret real vive en env vars del proceso runtime:
+  - `PERPLEXITY_API_KEY`, `TAVILY_API_KEY`, `OPENAI_API_KEY`, etc.
+- Cuando el kernel hace lookup, lee `auth_type` del catastro y resuelve la env var:
+
+```python
+def get_credentials(tool_entry: ToolEntry) -> str:
+    if tool_entry.auth_type == "api_key":
+        env_var_name = f"{tool_entry.key.upper()}_API_KEY"  # PERPLEXITY_API_KEY
+        return os.environ[env_var_name]  # fail loud si no está
+    elif tool_entry.auth_type == "oauth":
+        # OAuth flow
+        ...
+```
+
+- El JSON queda en repo público sin riesgo. El env var queda en Railway / 1Password.
```

---

## Issue D — Catastro-A reconfigurado a 4 catastros (Drift de visión)

### Contexto

En conversación Cowork ↔ Manus de hoy, acordamos reconfigurar Catastro-A:

- **Original (spec actual):** 3 dominios — Suppliers Humanos + Herramientas AI Verticales + Modelos LLM (extender existente)
- **Reconfigurado:** 4 catastros paralelos
  - **Catastro de Modelos LLM** (existente, 6 entries actuales)
  - **Catastro de Agentes 2026** (NUEVO — 21 entries de `docs/biblias_agentes_2026/`)
  - **Catastro de Herramientas AI Verticales** (DSC-G-007 — renderers, video gen, voice, document parsing, etc.)
  - **Catastro de Suppliers Humanos** (Sureste MX, 30+ entries)

Además, Cowork agregó **interfaces operativas** que el Catastro de Agentes 2026 debe exponer para que Manus mismo lo use:

```python
catastro.agentes.find_best(task, capability, budget, latency)  # delegación
catastro.agentes.peers_of("manus_v3")                          # auto-aprendizaje
catastro.agentes.my_canonical_spec()                           # anti-Dory self-ref
```

El spec actual NO refleja esto. Manus actualmente está en Catastro-B + tareas operativas, pero cuando arranque Catastro-A va a leer la versión vieja.

### Fix propuesto

Cowork redacta v2 del spec Catastro-A con:

1. Sección "0. Procedencia" mencionando la conversación de hoy (gap conceptual detectado)
2. Plan ajustado en 3 dominios (no 2 como original):
   - Dominio A — Catastro de Agentes 2026 (NUEVO, 21 entries de biblias canónicas)
   - Dominio B — Catastro de Herramientas AI Verticales (16-25 entries realtime)
   - Dominio C — Catastro de Suppliers Humanos Sureste MX (30+ entries realtime)
3. Schema `kernel/data/catastro_agentes.json` paralelo a los otros 3
4. 3 interfaces operativas que Manus mismo consume
5. ETA recalibrada: 75-110 min (antes 30-90 min)
6. Cierre: `🏛️ CATASTROS PARALELOS x4 — DECLARADOS` + DSC-G-007.1 (evolución)

**Acción:** Cuando Manus reporte verde de Catastro-B + tareas operativas pendientes, le entrego v2 del spec antes de que arranque A.

---

## Issue E — Sprint 88 nota de corrupción previa (Informativo)

Línea 157 dice:

> **Spec previa CONTAMINADA por sub-agente (kernel v0.50.0, Critic Score 78, /v1/run, /v1/ingest, review_html_quality, Rollout viernes) — descartada por audit de Manus Hilo Ejecutor.**

Es registro forense del incidente DSC-G-008 v1 — dejar como está. Sirve para que cualquier agente futuro que lea el spec entienda por qué la versión actual es la canónica.

---

## Issue F — Catastro-B `manus-oauth-pattern` skill (Verificar)

Catastro-B propone crear skill `manus-oauth-pattern` para canonizar OAuth 2.0 + PKCE como patrón reutilizable. OAuth maneja secrets sensibles (client_secret, refresh tokens, access tokens).

### Acción propuesta

Cuando Manus implemente la skill, debe respetar explícitamente:

- **DSC-S-003:** `client_secret` viene de `os.environ["OAUTH_CLIENT_SECRET"]`, no hardcoded
- **DSC-S-004:** PROHIBIDO defaults con secrets reales
- **DSC-S-001:** access tokens / refresh tokens viven en bóveda primaria (1Password / Bitwarden), NO en `.env` versionado ni en código
- **DSC-S-002:** la skill incluye `.gitleaks.toml` específico que detecta patrones OAuth (Bearer tokens, refresh tokens, etc.)

Agregar al spec Catastro-B una sección "Reglas de credenciales" similar a la que propuse para Sprints 89/Catastro-A (Issue C).

---

## Hallazgos negativos (lo que NO encontramos)

- ✅ Cero secrets hardcoded en cualquier spec
- ✅ Cero `os.environ.get(VAR, "default_secret")` en specs
- ✅ Cero referencias a `audit_supabase_tokens.py` en su forma vulnerable (solo en S-001 spec con nota de "refactorizado en P0")
- ✅ Cero referencias a versiones obsoletas (excepto la nota documentada de Sprint 88)
- ✅ Cero violaciones de Brand DNA en colores (Mobile 1 menciona indigo/purple/mint pero como problema a resolver, no como propuesta)
- ✅ Cero menciones de DSN postgres con password real

---

## Acciones consolidadas para Manus

### Antes de arrancar Sprint 90

- Audit de `like-kukulkan-tickets` por Stripe keys + anti-patrones (Issue B)
- Si hay hits → mismo flujo que P0 (refactor + rotación)
- Si limpio → arrancar Sprint 90 normal

### Antes de arrancar Sprint 89 + Catastro-A

- Cowork actualiza specs con sección "Reglas de credenciales" (Issue C) — NO esperar este audit, lo hago en paralelo

### Antes de arrancar Catastro-A

- Cowork redacta v2 del spec con 4 catastros + 3 interfaces operativas (Issue D) — lo hago cuando Manus reporte cierre Catastro-B

### Cuando se implemente Catastro-B (skill manus-oauth-pattern)

- Aplicar DSC-S-001/S-003/S-004 explícitamente (Issue F)

### Mobile 1

- Renombrar `core/services/` a `core/mensajeros/` (Issue A) — fix cosmético antes de que Manus arranque Mobile 1

---

## Próximos pasos de Cowork

1. **Update spec Sprint 89** con sección "Reglas de credenciales" (Issue C)
2. **Update spec Catastro-A** con sección "Reglas de credenciales" + reconfiguración a 4 catastros (Issues C + D)
3. **Update spec Sprint 90** con bloque "0. Audit pre-extracción" (Issue B)
4. **Update spec Catastro-B** con sección "Reglas de credenciales" para OAuth (Issue F)
5. **Update spec Mobile 1** con `core/mensajeros/` (Issue A)

ETA Cowork para 5 updates: ~30-45 min adicionales si Alfredo aprueba.

---

**Cowork (Hilo A), audit preventivo 2026-05-06 — DSC-G-008 v2 funcionando como diseñado**
