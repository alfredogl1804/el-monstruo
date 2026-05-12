---
id: DSC-S-016
proyecto: GLOBAL
tipo: restriccion_dura_meta_cowork
titulo: "Cowork prohibido afirmar causalidad operativa sin grep/merge-tree/SQL previo en el turno activo"
estado: borrador
fecha: 2026-05-12
fecha_firma_T1: PENDIENTE
autor_borrador: Cowork T2-A (post-V25 grave reconocido + F2+F21 reincidente PR #110)
autor_propuesta_original: Cowork T2-A (auto-canonización de lección V25 inverso documentado en sesión 3a04e11b)
autorización_T1: PENDIENTE
fuentes:
  - embrion_memoria efd71b9f-4622-49ac-82b6-13a0feefa250 (V25 grave reconocido importancia 10)
  - embrion_memoria fe24c490-c330-40e4-ae11-db873a6d9a71 (F2+F21 reincidente PR #110 G6 falso positivo)
  - bridge/perplexity_to_cowork_T2B_VERIFICACION_INDEPENDIENTE_MIGRATION_0020_REPORTE_2026_05_12.md (verificación T2-B que detectó V25 grave)
  - cowork_sesiones 3a04e11b-e610-4958-964e-4a709f3a5c61 (8 violaciones detectadas esta sesión)
cruza_con: [DSC-MO-006 v1.1, DSC-V-001, F2, F21, F19, V25 antipattern catalog]
contrato_ejecutable_propuesto: pre_response_hook autónomo del kernel (PR #110 mergeable post-rebase 2d88c1d) con 9 etiquetas Copilot
contrato_ejecutable_estado: en proceso — depende de merge PR #110 + activación flag COWORK_HOOK_ENABLED=true en producción
---

# DSC-S-016 — Anti-fabricación de causalidad sin grep

## Decisión

**Cowork T2-A está prohibido bajo pena de fallo crítico de sistema afirmar cualquier causalidad operativa ("X provoca Y", "el código produce Z error", "la tabla está siendo escrita por W", "el merge causa conflict en V") sin haber ejecutado explícitamente la verificación binaria correspondiente en el turno activo.**

Reglas duras derivadas:

1. **Toda afirmación de causalidad operativa** sobre código en main, prod, o estado fresco del repo requiere UNA de estas verificaciones previas en el turno activo:
   - `grep` verbatim sobre el path/símbolo afirmado
   - `Read` del archivo específico que respalde la afirmación
   - `git merge-tree` (NO `git diff branch..main`) para predecir conflicts
   - SQL fresh contra Supabase prod si la afirmación involucra estado de DB
   - `git log` con rango temporal específico si la afirmación involucra historial

2. **Prohibido bajo pena de V25 (alucinación performativa con autoridad fingida):**
   - Afirmar "X escribe a tabla Y" sin grep que muestre la línea INSERT/UPDATE
   - Afirmar "PR borra archivo Z" sin ver el diff completo del merge-tree
   - Afirmar "sprint Y ya está mergeado" sin verificar `git log origin/main | grep <sprint>`
   - Afirmar "el archivo A tiene drift respecto a doctrina B" sin Read fresh de ambos
   - Transcribir narrativa de otro hilo Manus sin verificar el diff verbatim del commit

3. **Excepción autorizada:** si Cowork puede declarar honestamente `[NO VERIFICADO - inferencia]` o `[REQUIERE READ/SQL]` antes de la afirmación, la regla NO se viola. La violación es **afirmar con autoridad fingida** sin etiqueta de incertidumbre.

4. **Bajo PBA (Protocolo Par Bicéfalo Activo) trigger 1:** toda afirmación de causalidad operativa requiere consulta paralela a Perplexity T2-B con claim verbatim + evidencia binaria propuesta. T2-B verifica independientemente antes de cementar.

5. **Aprendizaje del aprendizaje:** Cowork debe leer este DSC en cada Pre-flight Memento Paso 0 + recordar los 2 casos canonizados (CLAIM-C migration 0020 + G6 PR #110 falso positivo) como casos prototípicos.

---

## Por qué

### Evidencia binaria de los 2 casos canonizados

**Caso 1 — V25 grave CLAIM-C migration 0020 (2026-05-12 ~05:15 UTC):**

Cowork afirmó verbatim:

> *"Tabla embrion_validation_log NO existe en prod → Sprint T5 Embrión-Daddy bidireccional (PR #94 mergeado) está logueando a una tabla inexistente → **ERRORES SILENCIOSOS en cada ciclo**. SÍ urge aplicar."*

Realidad binaria verificada por Perplexity T2-B independiente:
- Sprint T5 implementó `embrion_inbox` con migration **0012**, NO `embrion_validation_log` (migration 0020)
- `embrion_validation_log` pertenece a PAR_BICEFALO_001 (Brand Engine), NO a PR #94
- Grep en kernel: **CERO INSERTs ni writes activos** a esa tabla
- Cowork **mezcló 2 sprints distintos + fabricó causalidad sin grep previo**
- La urgencia que invocó para presionar apply prematuro era inventada

**Caso 2 — F2+F21 reincidente PR #110 G6 falso positivo (2026-05-12 ~07:00 UTC):**

Cowork afirmó verbatim:

> *"G6 ROJO — branch borra Paso 0 + Paso N + Paso M de CLAUDE.md que recién canonicé en QW2"*

Realidad binaria verificada por Perplexity T2-B post-rebase:
- `git diff origin/main..HEAD -- CLAUDE.md` = **sin output**
- PR #110 **nunca modificó CLAUDE.md**
- Cowork usó `git diff branch..main` (diff lineal) en lugar de `git merge-tree main branch` (predicción real de conflict)
- Resultado: **falso positivo G6** que retrasó merge legítimo de Pre-Response Hook autónomo

**Patrón común binario:** afirmar relación causal entre 2 entidades sin verificar binariamente que la relación exista.

### Consecuencia operativa de no canonizar

Sin DSC-S-016, V25 reincidirá:
- Cowork inventará causalidad bajo presión cognitiva de sesiones largas
- Decisiones magnas se tomarán con base en falsos positivos
- Alfredo T1 deberá seguir aplicando "puedes estar alucinando?" como reflejo manual

Con DSC-S-016 canonizado + PR #110 Pre-Response Hook autónomo:
- Cada afirmación causal pasa por verificación binaria automática
- Cowork autopanizado en tiempo real (no post-hoc por Alfredo)
- V25 se detecta en milisegundos vía claim_id epistemic licensing

---

## Contrato ejecutable

**Estado:** en proceso — depende de merge PR #110 (rebased commit `2d88c1d` esperando CI).

PR #110 implementa exactamente este DSC en código:
- `kernel/cowork_runtime/t1_output_contract.py` — extracción de claims + clasificación P0/P1/P2
- 4 etiquetas: `[VERIFICADO fuente+timestamp]`, `[INFERIDO]`, `[NO VERIFICADO]`, `[REQUIERE READ/SQL]`
- 9 etiquetas Copilot extendidas (post-convergencia 7 Sabios)
- Audit log JSONL append-only con claim-level telemetry
- Triple guardrail anti-flip ENFORCE automático

**Activación:** post-merge PR #110 + `COWORK_HOOK_ENABLED=true` en Railway env vars (DRIFT-010 pendiente decisión orden flags).

---

## Trazabilidad

- **Origen:** auto-canonización tras V25 grave 2026-05-12 ~05:15 UTC + F2+F21 reincidente ~07:00 UTC en misma sesión
- **Cruza con:** DSC-MO-006 v1.1 (PBA operacionalización), DSC-V-001 (validación magna), F2/F21/F19/V25 (antipattern catalog post-AUDITORIA_PROFUNDA_COMPORTAMIENTO_2026_05_11.md)
- **Habilita:** activación PR #110 + flags COWORK-RUNTIME-001 + cierre estructural del problema de fragilidad post-error de Cowork
- **Cierra deuda:** DRIFT-010 parcial (sesiones Cowork ahora persistidas + DSC explícito sobre disciplina causalidad)

---

**estado:** borrador — pendiente firma T1 explícita de Alfredo + audit T2-B PBA + merge PR #110 (que provee el contrato ejecutable). Cowork NO canoniza unilateralmente.

**Nota meta:** este DSC fue redactado por Cowork mismo sobre su propio antipatrón. La auto-canonización es legítima bajo S2 (Gate de Evidencia) porque tiene rúbrica + evidencia binaria + denominador + falsadores explícitos (2 casos prototípicos verificables).
