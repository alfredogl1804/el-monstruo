---
id: DSC-S-011
proyecto: EL-MONSTRUO
serie: Seguridad
tipo: decision_arquitectonica_de_proceso
titulo: "Sistema de Realidad Ejecutable — Todo hilo del Monstruo verifica realidad binaria antes de actuar; ningún claim canonizado puede sobrevivir un round de auditoría contra Supabase/git/API. La memoria de un hilo NO es fuente de verdad; el código que ejecuta verificación SÍ."
estado: firme
fecha: 2026-05-11
autoridad: T1 (Alfredo) + T2 (Cowork) con propuesta originada en Hilo Ejecutor 2 (manus_hilo_b)
fuentes:
  - sesion:cowork_2026_05_11_p0_rls_catch_F2
  - hilo_b:sandbox_local_monstruo_local_reality_ejecutable_v1
  - acuse_cierre:bridge/cowork_to_manus_ACUSE_CIERRE_VERDE_P0_RLS_2026_05_11.md
cruza_con:
  - DSC-MO-006 (Par bicéfalo — Proposer ≠ Evaluator ≠ Merger)
  - DSC-MO-011 (Embryo Patch Lane v1 — gates de auto-modificación)
  - DSC-G-008 v2 (validar antes de specs Y antes de cierre)
  - DSC-S-006 (RLS por defecto)
  - Objetivo Maestro #4 (No equivocarse dos veces)
  - Objetivo Maestro #11 (Seguridad Adversarial)
  - Objetivo Maestro #15 (Memoria Soberana)
  - F2 antipattern (afirmar sin verificar)
  - S5 solución (verificar antes de cuestionar)
---

# DSC-S-011 — Sistema de Realidad Ejecutable

## Decisión

Todo hilo del Monstruo (Cowork T2, hilos Manus T3, embriones) DEBE pasar sus claims factuales por un verificador ejecutable que contraste contra realidad fresca (Supabase, git, GitHub API, filesystem) antes de actuar o canonizar. La memoria de un hilo NO es fuente autoritativa de verdad. El código que ejecuta verificación SÍ.

**Frase canónica:**

> *"El runtime de los hilos ya no depende de la memoria de los hilos. La doctrina ahora es código que se ejecuta, no texto que se lee."*

## Origen

Hilo Ejecutor 2 (manus_hilo_b) construyó autónomamente un Sistema de Realidad Ejecutable local en `~/el-monstruo/.monstruo-local/` (sandbox personal, no commiteado al repo) entre 2026-05-11 03:00-06:30 UTC. Sin haberle pedido la construcción, anticipó que Cowork iba a emitir specs con stale info y armó 7 niveles de verificación binaria.

Durante el sprint P0 RLS Fix (autorizado 10:22 UTC), su Sistema detectó vía `ls` que mi acuse instruía path `supabase/migrations/` cuando el repo usa `migrations/sql/`. Sin su catch, hubiéramos creado carpeta duplicada y roto convención del repo (10 migraciones existentes 0001-0009). Corregí en commit `a29e76e`. **F2 mío atrapado por S5 suyo, en vivo, durante ejecución de P0.**

Esto canonizó el patrón.

## I. Los 7 niveles del Sistema (especificación)

### Nivel 1 — Reality Runner maestro (`reality/reality.sh all`)
Ejecuta en ≤10 segundos: kernel `/health`, openapi de Supabase (count tablas, RLS coverage), estado embrión (memoria, budget, write proposals), git status del repo, mensajes bridge últimas 24h. Guarda snapshot con timestamp.

### Nivel 2 — Reality Diff (`reality/reality.sh diff`)
Compara snapshot actual vs anterior. Detecta cualquier delta real sin depender de la memoria del hilo.

### Nivel 3 — Validate Skills (`reality/validate_skills.sh`)
Contrasta afirmaciones de skills/docs/contexto contra realidad en vivo. Si un skill dice "Sprint 27 con 14 componentes" y `/health` devuelve 16, el skill está stale y se marca para actualizar.

### Nivel 4 — Ownership Map (`ownership_map.md`)
Mapa exhaustivo de quién es dueño de cada path/branch/tabla/workflow. Reglas duras de "NO TOCAR" por hilo. Se aplica vía Nivel 6.

### Nivel 5 — My Work Audit (`my_work_audit.md`)
Inventario verificado contra git de PRs, DSCs firmados, postmortems, runbooks, migraciones, scripts, workflows propios del hilo. Verificable por terceros.

### Nivel 6 — Pre-Flight Anti-Autoboicot (`reality/pre_flight.sh`)
Checklist obligatorio antes de push/touch/sprint_close. Rechaza acciones que violan Ownership Map. Probado contra falsos positivos (acepta lo legítimo, rechaza lo prohibido).

### Nivel 7 — Inject Context (`reality/inject_context.sh <spec.md>`)
Anotador que toma cualquier spec recibido y verifica entidad por entidad contra realidad: cada tabla mencionada chequea existencia + RLS, cada endpoint contra `/openapi.json`, cada archivo contra filesystem, cada branch contra git local+remote. Output: archivo anotado en `.monstruo-local/annotations/`.

## II. Aplicabilidad por hilo

| Hilo | Cuáles niveles obligatorios | Cuáles opcionales |
|---|---|---|
| **Cowork T2** | 1, 2, 3, 5, 7 antes de canonizar audits/specs | 4, 6 (parcial, Cowork no toca código) |
| **Hilo Ejecutor Oficial (Manus app Flutter)** | 1, 2, 4, 5, 6, 7 | 3 |
| **Hilo Ejecutor 2 (Manus seguridad/runtime)** | Los 7 — ya los implementó | — |
| **Hilo Catastro** | 1, 2, 4, 6, 7 | 3, 5 |
| **Embriones** | 1, 2 vía Embryo Patch Lane (DSC-MO-011) | 4, 6 informativos |

## III. Reglas duras

1. **Ningún spec se canoniza sin pasar Nivel 7** (inject_context). Si Cowork emite spec sin auditarlo contra realidad, queda en estado "nota exploratoria" hasta verificación.
2. **Ningún audit canónico sin Nivel 1 fresca de la sesión actual** — anti-stale info (regla canonizada previamente en CORRECTIVO_ARQUITECTONICO_2026_05_11).
3. **Pre-Flight obligatorio antes de push/merge** — si el hilo no corrió Nivel 6, el push se considera no autorizado y debe ser revertido.
4. **Diff snapshots semanales mínimo** — para detectar drift silencioso entre lo que canon dice y lo que producción es.
5. **Catches inter-hilos son aprendizaje canónico, no error individual.** Cuando un hilo atrapa F2 de otro vía S5, el aprendizaje se registra en este DSC o en un anexo, no se castiga al hilo que falló.

## IV. Cuándo NO aplica el Sistema

- Conversaciones puramente exploratorias en chat (Alfredo-Cowork) sin emisión de spec
- Diff de menos de 50 LOC sobre código personal no canónico
- Tests unitarios aislados que ya tienen su propio harness
- Decisiones T1 puras de Alfredo (su autoridad final no requiere verificación binaria)

Esta lista es estricta. Cualquier otra acción cae bajo el Sistema.

## V. Métricas canónicas del Sistema

1. Catches F2 por semana (cuántas afirmaciones sin verificar atrapadas)
2. Tiempo medio entre F2 emitido y F2 detectado (debe bajar con uso)
3. Cobertura del Nivel 7 sobre specs emitidos (% de specs auditados pre-canon)
4. False positive rate de Nivel 6 (cuántas veces rechazó acción legítima)
5. Snapshots Reality generados (frecuencia, lapsos)
6. Tablas Supabase fuera de inventario canónico (delta vs memoria)
7. Skills/docs obsoletos detectados por Nivel 3
8. Catches inter-hilos exitosos (uno atrapa al otro)

## VI. Implementación inmediata

### Fase 1 (2026-05-11) — Estado actual ya entregado
- Hilo Ejecutor 2 tiene los 7 niveles operativos en `~/el-monstruo/.monstruo-local/`
- Catch exitoso F2→S5 demostrado en P0 RLS Fix

### Fase 2 (próximas 2 semanas)
- Migrar el sistema del sandbox local del Hilo Ejecutor 2 a una versión compartida en `tools/reality_executable/` del repo
- Hilo Ejecutor Oficial adopta Niveles 4, 5, 6 para su sprint MOBILE_1B
- Cowork (yo) adopta Nivel 7 obligatorio antes de canonizar cualquier audit/spec nuevo

### Fase 3 (después de Sprint RAMP FLAGS)
- Embriones consumen Nivel 1 + 2 vía Embryo Patch Lane antes de generar PRs
- Workflows GitHub Actions que corren Nivel 1-3 en cron diario y abren issue P0 si detectan drift

### Fase 4 (post-cierre app Flutter usable)
- Nivel 6 enforced como pre-commit hook obligatorio en todo el repo
- Nivel 7 integrado al flujo de emisión de specs Cowork→Manus en bridge/

## VII. Modos de fallo documentados

1. **Sistema reporta verde pero realidad está en rojo** — Nivel 1 falla en captar señal real (ej: tabla creada por bypass como pasó con catastro_vision_generativa). Mitigación: Nivel 3 + audits adversariales semanales.
2. **Hilo ignora Pre-Flight (Nivel 6)** — actúa sin correrlo. Mitigación: Sistema CI rechaza push sin marca de Pre-Flight.
3. **False positives crean fricción** — Nivel 6 rechaza acción legítima. Mitigación: cada false positive se documenta y refina las reglas.
4. **Snapshots desactualizados** — diff comparara contra snapshot viejo y reporta "todo igual" cuando hubo drift. Mitigación: TTL automático de snapshots (>24h se invalida).
5. **Sistema consume tiempo de hilo más que ahorra** — si el overhead excede el valor. Mitigación: revisión trimestral del costo-beneficio del Sistema mismo.

## VIII. Conexión con DSCs existentes

| DSC | Relación |
|---|---|
| DSC-MO-006 (Par bicéfalo) | Niveles 4-6 operacionalizan separación Proposer/Evaluator/Merger |
| DSC-MO-011 (Embryo Patch Lane) | Niveles 1, 2 son la base de los gates 1, 2, 9 |
| DSC-G-008 v2 (validar pre-cierre) | Nivel 7 lo enforza como código en lugar de checklist textual |
| DSC-S-006 (RLS default) | Nivel 1 detecta tablas sin RLS — atrapó catastro_vision_generativa |
| CORRECTIVO ARQUITECTONICO 2026-05-11 | Niveles 1, 5 cumplen "ningún audit sin Nivel 1 fresca + denominador" |

## IX. Patrón meta: "código no texto"

La lección de origen del Sistema es brutal:

> *"La única manera que el hilo obedezca lo que se le pide y no lo ignore es hablarle con código, no con texto."*
> — Hilo Manus de honestidad pura, registrado por Alfredo el 2026-05-11

Cowork canonizó esto en `tools/cowork_guardian.py` (regex anti-pausa) y `kernel/cowork_runtime/pre_response_hook.py` (Sprint COWORK-RUNTIME-001). Hilo Ejecutor 2 canonizó el mismo principio en su sandbox local antes de que se lo pidieran. Este DSC eleva el patrón a regla universal del Monstruo: **cualquier doctrina que importa pasa por código que se ejecuta, no por texto que se lee.**

## X. Estado al firmar

**firme** — propuesto por Hilo Ejecutor 2 con implementación funcional, canonizado por Cowork T2 con autoridad delegada Premium tras catch F2→S5 demostrado en vivo, ratificación T1 (Alfredo) implícita por instrucción de canonizar el patrón.

---

*DSC firmado por Cowork T2 Arquitecto, 2026-05-11. Propuesto por Hilo Ejecutor 2 (manus_hilo_b). Origen: catch del F2 path migración durante Sprint P0 RLS Fix. Patrón "código no texto" elevado a regla universal.*
