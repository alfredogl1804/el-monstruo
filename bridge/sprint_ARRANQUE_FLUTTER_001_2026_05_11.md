---
id: sprint_ARRANQUE_FLUTTER_001
fecha_spec: 2026-05-11
arquitecto: Cowork
estado: spec_firme
nivel_autoridad: 5 (sprint canonizado, ejecución autorizada)
objetivo_principal: |
  Alfredo usa la app Flutter desde su Mac (y eventualmente cel) conectada
  al kernel del Monstruo en producción dentro de 1-2 sesiones operativas.
cruza_con:
  - PREFLIGHT_ARRANQUE_2026_05_11
  - DSC-MO-011 (Embryo Patch Lane v1)
  - CORRECTIVO_ARQUITECTONICO_2026_05_11
  - DSC-S-006 (RLS por defecto)
  - Objetivo Maestro principal: Monstruo usable desde Mac
---

# Sprint ARRANQUE-FLUTTER-001

## Contexto Nivel 1 confirmado en sesión 2026-05-11 madrugada

Verificación en vivo contra Supabase producción + filesystem completo:

### Estado real del sistema (Nivel 1, evidencia binaria)

| Item | Estado | Evidencia |
|---|---|---|
| Embrión vivo | ✅ ACTIVO | Último latido hace 5min 9seg (2026-05-11 04:57:09 UTC) |
| Latidos 24h | ✅ 390 | `embrion_budget_state` |
| Memoria 24h | ✅ 141 entries | 134 respuestas + 5 mensajes Alfredo + 1 latido + 1 doctrina |
| Gasto LLM 24h | ✅ $5.47 USD | 18% del Mainspring $30/día — bien dentro |
| Self-Verifier 24h | ✅ 376 acciones | Activo en 96% de latidos |
| Write Policy log | ✅ 1762 totales | Activo |
| Memento validations | ✅ 25 totales, 0 últimas 24h | Activo pero sin uso reciente |
| `kernel_audit_log` | 🔴 0 entries totales | Tabla existe, Sprint S-003.B nunca activado en prod |
| `governance_log` | 🔴 0 entries | Tabla existe, sin uso |
| **Downtime confirmado** | 🔴 **4h 8min** | 2026-05-10 19:52 → 2026-05-11 00:00 UTC |
| `catastro_vision_generativa` RLS | 🔴 SIN RLS | 38 rows expuestos al `anon` role |
| `catastro_agentes` | ⚠️ 98 rows | Bajó de 111 (anomalía sin canonizar) |
| Kernel/Gateway accesible desde sandbox Cowork | 🔴 status 000 | Sandbox sin acceso a Railway — kernel SÍ funciona, pero verificación remota debe hacerse desde tu Mac |
| Repo en `main` commit | ✅ `da70b95` | hace 16h, alineado |
| Branch local `cowork/canonization-jornada-2026-05-10` | ⏳ pendiente push | tiene mis canonizaciones |
| App Flutter código | ✅ 31 archivos `.dart` | URL Gateway: `https://ag-ui-gateway-production.up.railway.app` |
| Flutter SDK en sandbox | 🔴 no instalado | `flutter build` debe correr en tu Mac |

### URLs canonizadas (de `apps/mobile/lib/core/config.dart`)

```
Gateway REST: https://ag-ui-gateway-production.up.railway.app
Gateway WS:   wss://ag-ui-gateway-production.up.railway.app/ws/chat
Kernel:       https://el-monstruo-kernel-production.up.railway.app
```

---

## Objetivo del Sprint

**Output binario:** Alfredo abre la app Flutter en macOS, ve la pantalla principal, envía un mensaje al embrión, recibe respuesta en tiempo real vía WebSocket, navega al feature Embrión Screen y ve los latidos en vivo.

**No-objetivo:** monetización, auto-mejora del kernel, T3 público, GTM. Esos vienen DESPUÉS.

---

## Tareas del Sprint (ordenadas por dependencia)

### T1 — Fix RLS `catastro_vision_generativa` [P0, 10 min]

**Por qué primero:** Supabase advisory advierte 38 rows expuestos al `anon` role. Riesgo de seguridad activo. Y es prerequisito de cualquier sprint posterior (compliance).

**SQL completo a aplicar (replica pattern `catastro_modelos`):**

```sql
-- Migración: enable_rls_catastro_vision_generativa
ALTER TABLE public.catastro_vision_generativa ENABLE ROW LEVEL SECURITY;

CREATE POLICY catastro_vision_generativa_read_public 
  ON public.catastro_vision_generativa 
  FOR SELECT 
  TO public 
  USING (true);

CREATE POLICY catastro_vision_generativa_service_only 
  ON public.catastro_vision_generativa 
  FOR ALL 
  TO public 
  USING (current_setting('request.jwt.claims', true)::jsonb->>'role' = 'service_role');
```

**Quién ejecuta:** Cowork con `mcp__supabase-monstruo__apply_migration` — pero requiere visto bueno explícito de Alfredo (acción producción).

**Aceptación:** `mcp__supabase-monstruo__list_tables` reporta `rls_enabled: true` para esta tabla.

---

### T2 — Verificar kernel + gateway responden públicamente [P0, 5 min]

**Quién ejecuta:** Alfredo desde su Mac (sandbox Cowork no tiene acceso de red a Railway).

**Comandos:**
```bash
curl -i https://el-monstruo-kernel-production.up.railway.app/health
curl -i https://ag-ui-gateway-production.up.railway.app/health
```

**Aceptación:** ambos retornan HTTP 200 con respuesta JSON válida.

**Si falla:** debugging Railway antes de continuar.

---

### T3 — Investigar causa del downtime 4h 8min [P1, 30 min]

**Ventana exacta:** 2026-05-10 19:52:41 UTC → 2026-05-11 00:00:31 UTC.

**Quién ejecuta:** Alfredo accede Railway logs en esa ventana. Cowork analiza logs si Alfredo los pega.

**Aceptación:** causa raíz canonizada en bridge file. Mitigación documentada.

**Hipótesis a verificar:**
- Restart de Railway (deploy automático)
- OOM
- Crash del worker
- Network glitch
- Crash del embrion_loop por bug

---

### T4 — `flutter build macos` desde tu Mac [P0, 15-30 min]

**Quién ejecuta:** Alfredo desde su Mac.

**Comandos:**
```bash
cd ~/el-monstruo/apps/mobile
flutter --version  # confirmar Flutter ^3.29.0 instalado
flutter pub get
flutter analyze
flutter build macos --debug
```

**Aceptación:** build exitoso sin errores. `flutter analyze` muestra 0 errors (warnings OK).

**Si falla:** debugging específico — falta dependencia, version mismatch, etc.

---

### T5 — Smoke test app Flutter → kernel [P0, 15 min]

**Quién ejecuta:** Alfredo desde su Mac.

**Pasos:**
1. Lanzar app Flutter macOS desde build de T4
2. Verificar onboarding screen carga
3. Navegar a chat
4. Enviar mensaje simple ("hola")
5. Verificar conexión WebSocket activa
6. Verificar respuesta del embrión llega vía streaming AG-UI
7. Navegar a feature Embrión Screen
8. Verificar muestra estado del embrión en vivo

**Aceptación:** ciclo completo round-trip funciona. Screenshot del chat respondiendo.

**Si falla:** debugging WS connection. Verificar gateway logs en Railway.

---

### T6 — Push branch Cowork con canonizaciones [P1, 5 min]

**Quién ejecuta:** Alfredo desde su terminal local (sandbox Cowork no puede push GitHub directo).

**Comando:**
```bash
cd ~/el-monstruo
git add memory/cowork/ \
  discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/DSC-MO-011_embryo_patch_lane_v1.md \
  bridge/sprint_ARRANQUE_FLUTTER_001_2026_05_11.md \
  bridge/COWORK_OPERATING_SYSTEM_v0_1_2026_05_10.md \
  bridge/ESTADO_MONSTRUO_2026_05_10_vs_PLANES.md
git commit -m "canonization(cowork): DSC-MO-011 Embryo Patch Lane v1 + Pre-flight + audits H0 + Correctivo"
git push origin main
```

**Aceptación:** commit visible en GitHub main.

---

### T7 — Branch protection en `main` [P1, 5 min]

**Quién ejecuta:** Alfredo en GitHub settings.

**Configuración mínima:**
- Require pull request before merging
- Require status checks to pass (CI workflows existentes)
- Restrict who can push to matching branches
- Do not allow bypassing the above settings

**Aceptación:** `main` no permite push directo, solo via PR.

---

### T8 — Regenerar `_INDEX.md` de la Capilla [P2, 15 min]

**Quién ejecuta:** Cowork con script.

**Acción:** scan automático de `discovery_forense/CAPILLA_DECISIONES/**/*.md`, parse front matter, generar índice actualizado con los 60 DSCs reales (vs 44 declarados).

**Aceptación:** `_INDEX.md` lista todos los DSCs con id + título + estado + fecha.

---

## Definición de "Done" del Sprint

```
T1 ✅ catastro_vision_generativa con RLS
T2 ✅ kernel + gateway respondiendo HTTP 200
T3 ✅ Causa del downtime 4h8m canonizada
T4 ✅ flutter build macos exitoso
T5 ✅ App Flutter → kernel smoke test PASS
T6 ✅ Canonizaciones pusheadas a main
T7 ✅ Branch protection en main activo
T8 ✅ _INDEX.md regenerado
```

8 de 8 cerradas = Sprint cerrado. Vos usás el Monstruo desde tu Mac.

---

## Riesgos y mitigaciones

### Riesgo R1: Kernel/Gateway están caídos
**Probabilidad:** baja (embrión latiendo significa kernel funcional — pero quizás solo el worker, no el endpoint HTTP)
**Mitigación:** T2 lo detecta. Si caído, restart Railway antes de T4.

### Riesgo R2: flutter build falla
**Probabilidad:** media (32 archivos, deps Flutter changing, last commit hace 16h)
**Mitigación:** errores específicos en T4 se resuelven en T4. No bloquea T1-T3.

### Riesgo R3: WebSocket no conecta
**Probabilidad:** media (gateway puede tener config)
**Mitigación:** T5 detecta. Debug logs Gateway en Railway.

### Riesgo R4: Otro downtime de embrión durante sprint
**Probabilidad:** baja en ventana corta
**Mitigación:** T3 canoniza causa raíz para prevenir. No bloquea otras tareas.

---

## Lo que NO incluye este Sprint

Explícitamente diferido a sprints posteriores:

- ❌ Cerrar wiring de las 5 capas transversales restantes a APIs externas (Sprint TRANSVERSAL-001)
- ❌ Implementar Embryo Patch Lane v1 en CI (Sprint EMBRYO-PATCH-LANE-001)
- ❌ Resolver Sprint Memento producción
- ❌ Resolver `governance_log` poblado
- ❌ Resolver `kernel_audit_log` poblado
- ❌ Auto-mejora del kernel por embrión
- ❌ Mobile 6 (voice + ambient + i18n)
- ❌ GTM / monetización
- ❌ Sucesión / bus factor

Esos vienen después de que vos uses la app desde tu Mac. Una vez que VEAS el Monstruo, decidimos siguiente prioridad con tu juicio sobre la app en uso real.

---

## Cadencia del sprint

- **T1**: hoy, 5 min con tu confirmación (1 línea: "aplica RLS")
- **T2, T3**: hoy o mañana, requiere tu acceso Railway desde Mac
- **T4, T5**: 1 sesión tuya en Mac (1-2 horas)
- **T6, T7**: hoy, 10 min con tu push + GitHub settings
- **T8**: Cowork lo hace en próxima sesión Cowork

**Sprint completo: 1-2 sesiones tuyas + 2 sesiones Cowork = 1-2 días de calendario.**

---

## Estado de Cowork durante el sprint

Cowork opera bajo:
- ✅ Modo "actuar sin preguntar" para acciones reversibles
- ✅ Gate de Evidencia para audits (canonizado en CORRECTIVO)
- ✅ DSC-MO-011 Embryo Patch Lane v1 vigente (aún sin embrión auto-modificándose, pero canonizado para cuando llegue)
- ✅ Sin nuevos audits H0 hasta evidencia Nivel 1 fresca recopilada
- ✅ Cadencia máxima 1 audit canónico/día

---

## Cierre operativo

Este es el **único spec activo del Monstruo en este momento**. Todo otro trabajo se pospone hasta que vos uses la app desde tu Mac. Eso es el objetivo principal canonizado y ahora operacionalizado.

Una vez cerrado el Sprint, próxima decisión Magna tuya: **¿qué hace el Monstruo primero cuando vos lo uses en producción real?**. Esa pregunta solo es responsable AFTER seeing the app working.

---

*Spec firmado por Cowork como Arquitecto T2. 2026-05-11. Bajo modo "actuar sin preguntar". Evidencia Nivel 1 fresca recolectada en sesión.*
