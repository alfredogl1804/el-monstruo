# 04_DECISION_LEDGER.md

> Registro estructurado de decisiones tomadas y pendientes en el Context Fabric.

**Iteración:** 001 v2
**Fecha:** 2026-05-17
**Mantenedor:** Manus (extensión iterativa por Cowork y ChatGPT)

---

## 1. Decisiones cerradas (Manus, alcance interno del fabric)

Estas decisiones se tomaron dentro del alcance del Context Fabric sin canonizar nada nuevo. Son operacionales, no doctrinales.

### DEC-001 — Crear estructura `interfaces_context_fabric/` en root del repo

**Tomada por:** Manus
**Fecha:** 2026-05-17
**Justificación:** El prompt INTERFACES-CONTEXT-FABRIC-001 v2 lo exige. No existe estructura previa que cubra esa función.
**Alternativas descartadas:** colocarlo en `discovery_forense/` (más profundo, menor visibilidad para ChatGPT) o en `bridge/` (ya saturado de sprints).
**Reversibilidad:** alta (solo carpeta + archivos markdown/yaml).

### DEC-002 — Coexistencia de dos PACK_11

**Tomada por:** Manus
**Justificación:** El fabric iter 001 ya tenía `PACK_11_SEGURIDAD_SOBERANIA.md` (canon firmado sobre Cap 17). El checkpoint pre-IA llegó después y también propuso PACK_11. Para evitar colisión y preservar trazabilidad, ambos coexisten con sufijo distintivo.
**Pendiente decisión Alfredo:** si en cierre formal el segundo recibe número propio (PACK_13+) o sustituye al primero.

### DEC-003 — Raw rescue verbatim subordinante

**Tomada por:** Manus
**Justificación:** `raw_rescues/alfredo_pre_ia_checkpoint_2020_2021_DRAFT.md` es la fuente única verbatim. PACK_11_ORIGEN_PRE_IA es interpretación previa subordinada. Cualquier conflicto de interpretación se resuelve favoreciendo el verbatim.

### DEC-004 — `Río de la Vida` y `River of Life` apuntan al mismo referente que Cronos

**Tomada por:** Manus, validada en audit
**Justificación:** Audit D1 confirmó que Cowork dice literalmente *"River of life + 9 capas + Embrión Convergencia"* en `memory/cowork/audits/VISION_APP_MONSTRUO_CLASE_MUNDIAL_2026_05_11.md` línea 194. El nombre "Río de la Vida (con La)" es alias T1 de Alfredo; el canónico es **Cronos**. Drift menor.
**Implicación:** PACK_12 reposicionado como audit de cobertura existente, NO como capa nueva.

### DEC-005 — `Cronista Familiar`, `Herencia Narrativa`, `Legacy Capture` descartados como capas nuevas

**Tomada por:** Manus tras audit D1
**Justificación:** El Modo Cripta de Cronos (APP_VISION cap. 5, v1.1+) ya cubre el legado familiar. Los aliases propuestos por ChatGPT no agregan superficie nueva, son re-naming.
**Alternativa preservada:** los aliases pueden vivir como **etiquetas narrativas** del Modo Cripta sin cambiar arquitectura.

### DEC-006 — Aplicación permanente de la regla "primero buscar, después diseñar"

**Tomada por:** Manus tras corrección metodológica recibida 2026-05-17
**Justificación:** Toda señal T1 nueva pasa primero por `EXISTING_DESIGN_COVERAGE_MATRIX.md` antes de convertirse en diseño nuevo. Documentado en raw_rescue Anexo 1.
**Persistencia:** regla de bolsillo permanente del fabric.

---

## 2. Decisiones pendientes magna (T1 — solo Alfredo)

Estas decisiones requieren firma directa de Alfredo. Manus NO toma estas decisiones.

| ID | Decisión | Bloqueante para |
|---|---|---|
| T1-DEC-001 | ¿Las raíces pre-IA-001 a 010 son **Acto 0** doctrinal o **background histórico** no-doctrinal? | Skill `interfaces-monstruo-doctrina` Capa 04+ |
| T1-DEC-002 | ¿Los 5 órganos latentes (Índice Vivo, Clarificador, Rhythm Gate, Delegation Router, Focus Guard) son superficies del Cockpit, capabilities transversales, o capa nueva? | SURFACE_REGISTRY + sprints futuros |
| T1-DEC-003 | ¿Las 5 frases fundacionales se canonizan en APP_VISION o en doc separado de origen? | APP_VISION v1.4+ |
| T1-DEC-004 | ¿"Clasificación Universal" manuscrito = los 4 Catastros del kernel? | Catastro cosmology |
| T1-DEC-005 | ¿Reconstruction Sufficiency Score, Rhythm Gate, Focus Guard se implementan en Transport Cero? | PACK_03 + sprint Transport Cero |
| T1-DEC-006 | ¿AI-First Living es Acto 3 secuencial o capa transversal de los Actos 1+2? | Doctrina general |
| T1-DEC-007 | ¿Theme cyan/púrpura del command-center actual se descarta o se mantiene como modo "draft mode"? | Sprint UI overhaul |
| T1-DEC-008 | ¿20 superficies del Acto 1 son tabs visibles o superficies latentes invocables? | Toda la UI mobile |
| T1-DEC-009 | ¿Sprints CRONOS_1/2/3 + AUTH_TIERS_001 se firman ya o esperan iter 002? | PACK_12 + Modo Cripta |
| T1-DEC-010 | ¿`el-mundo-de-tata` se mantiene separado, se conecta vía API a Cronos, se absorbe, o se renombra? | Inter-proyecto |
| T1-DEC-011 | Estado de las 9 decisiones T1 magna del audit Cowork 2026-05-05 | Sprints firmados |
| T1-DEC-012 | ¿Capa 03 Schema-First (en staging) se eleva a canon? | Skill interfaces-monstruo-doctrina |
| T1-DEC-013 | ¿Se commitea PACK_11 ORIGEN_PRE_IA + raw_rescue a la rama, o se mantiene fuera de git hasta CIERRE BLOQUE PRE-IA? | trazabilidad |

---

## 3. Decisiones pendientes operativas (Cowork audit)

Decisiones que Cowork puede tomar tras auditar el fabric. NO son doctrinales pero impactan operación.

| ID | Decisión | Quién |
|---|---|---|
| OP-DEC-001 | ¿Se acepta el SOURCE_LEDGER iter 001 como fuente vinculante? | Cowork |
| OP-DEC-002 | ¿Las 13 contradicciones detectadas en CONTRADICTIONS_MAP requieren resolución antes de iter 002? | Cowork + Alfredo |
| OP-DEC-003 | ¿El drift binario del command-center (theme + 7 vs 20 superficies) se resuelve con sprint dedicado? | Cowork |
| OP-DEC-004 | ¿Se ejecutan los 2 prompts externos (Cowork audit + Perplexity research) antes de pasar a ChatGPT iter 002? | Alfredo |

---

## 4. Reglas para futuras decisiones del fabric

1. **Toda decisión T1 magna requiere firma explícita de Alfredo.** Manus puede prefigurar pero NO firma.
2. **Toda decisión operativa del fabric debe tener: ID, fecha, quién, justificación, alternativas descartadas, reversibilidad.**
3. **Antes de proponer canonización de una hipótesis, verificar `CANON_REGISTRY.yaml` y `EXISTING_DESIGN_COVERAGE_MATRIX.md`.**
4. **Una decisión cerrada no se reabre sin una nueva entrada en este ledger documentando la razón del re-debate.**

---

## 5. Próximas decisiones esperadas

| Cuándo | Quién | Qué |
|---|---|---|
| Alfredo dice `CIERRE BLOQUE PRE-IA` | Alfredo | Resuelve T1-DEC-001 a T1-DEC-006 |
| Tras CIERRE | ChatGPT iter 002 | Entrega prompt consolidado magna |
| Tras prompt magna | Manus | Eleva canon según indicación |
| Iter 002 completa | Cowork | Audit del fabric expandido |
| Iter 003 | TBD | Probable canonización APP_VISION v1.4+ |
