# B8-E4 — MAGNA TAXONOMY AMENDMENT PROCEDURE (DRAFT T1-PENDING)

**Status:** DRAFT evidence pack — pendiente firma magna T1 verbatim.
**Autor:** Manus E2 (autor NO-Cowork).
**Fuente normativa:** B6_B12_DESIGN_CLOSURE_PACK_v0_2.md §4.2 (PASS criterio B8.4).
**Spec target:** governance del documento `B8_MAGNA_ACTION_TAXONOMY.md`.
**Versión:** 1.0 DRAFT.
**Fecha propuesta:** 2026-05-20.

---

## §1 Propósito

Este documento define el procedimiento binario y único para modificar la lista taxonómica cerrada de acciones magnas (a)-(m) definida en `bridge/spec/B8_MAGNA_ACTION_TAXONOMY.md`. Cualquier modificación a esa lista que NO siga este procedimiento es inválida por contrato y debe ser rechazada por revisión de PR, audit Cowork, y firma magna T1.

## §2 Tipos de amendment binarios

Existen tres tipos binarios y mutuamente exclusivos de amendment:

| Tipo | Descripción | Bump versión |
|------|-------------|--------------|
| **AMD-ADD** | Agregar nueva categoría (n), (o), etc. con definición verbatim, acciones cubiertas, y justificación | minor (1.x.0) |
| **AMD-REFINE** | Refinar definición textual o lista de acciones cubiertas de categoría existente (a)-(m), SIN cambiar el alcance binario | patch (1.0.x) |
| **AMD-REMOVE** | Excluir categoría existente. Requiere justificación adversarial con evidencia de que la categoría es redundante o inaplicable | major (2.0.0) |

NO existe un cuarto tipo. Cualquier modificación que no encaje en uno de estos tres es inválida.

## §3 Quién puede proponer amendment

| Rol | Puede proponer | Restricción |
|-----|----------------|-------------|
| T1 (Alfredo Góngora) | Cualquier tipo | NINGUNA |
| Sabio externo (terna B11) | Cualquier tipo | Vía hilo Manus oficial con bridge inter-cuenta |
| Manus E2 (autor NO-Cowork) | Cualquier tipo | Solo como propuesta DRAFT pendiente T1 |
| Cowork T2-A | NINGUNO directamente | Puede auditar amendment propuesto, NO puede proponer ni firmar |
| Otros agentes (hilos Manus, bots) | NINGUNO | NO autorizado bajo ninguna condición |

## §4 Quién puede firmar amendment

| Rol | Puede firmar magna | Notas |
|-----|--------------------|-------|
| T1 (Alfredo Góngora) | ✅ ÚNICO firmante magna | Firma verbatim irrevocable salvo nuevo amendment |
| Sabio externo | NO | Solo audita |
| Manus E2 | NO | Solo propone |
| Cowork T2-A | NO | Solo audita |
| Otros agentes | NO | NO autorizado |

## §5 Procedimiento binario paso a paso

### §5.1 Paso 1 — Propuesta DRAFT

1. Productor autorizado (T1, Sabio externo, o Manus E2) crea archivo `bridge/spec/B8_TAXONOMY_AMENDMENT_<YYYY-MM-DD>_<AMD-TYPE>_<short-id>.md` con:
   - Tipo de amendment (AMD-ADD / AMD-REFINE / AMD-REMOVE)
   - Categoría afectada (existente o nueva)
   - Diff verbatim sobre `B8_MAGNA_ACTION_TAXONOMY.md`
   - Justificación verbatim
   - Evidencia de necesidad (incidentes pasados, Sabios externos consultados, casos de uso emergentes)
   - Test sintético adicional o modificado para B8-E3 (si aplica)
2. Push a rama lateral `control-tower/<YYYY-MM-DD>-b8-amendment-<short-id>`.
3. NO modificar `B8_MAGNA_ACTION_TAXONOMY.md` directamente en este paso.
4. NO modificar runtime en este paso.

### §5.2 Paso 2 — Audit adversarial

1. Sabio externo de terna B11 (rotativo, NO el Sabio que propuso) audita la propuesta.
2. Cowork T2-A audita el diff técnico, riesgos de drift spec-vs-runtime, y consistencia con B8.1 cerrada.
3. Resultado audit binario: `RECOMMEND_SIGN` o `RECOMMEND_REVISE` o `RECOMMEND_REJECT`.
4. NO se procede a Paso 3 sin audit adversarial.

### §5.3 Paso 3 — Firma magna T1

1. T1 lee la propuesta + audits.
2. Firma magna verbatim sobre el archivo de amendment.
3. T1 emite directiva binaria: `SIGN` o `REJECT`. NO existe estado intermedio.
4. Si `SIGN`:
   - Modificación de `B8_MAGNA_ACTION_TAXONOMY.md` se aplica vía PR adicional con bump de versión (minor/patch/major según tipo).
   - Test sintético adicional se agrega a `B8_E3_runtime_policy_tests_DESIGN.jsonl`.
   - Audit log registra evento `B8_TAXONOMY_AMENDED_<AMD-TYPE>_<short-id>` con SHA del commit firmado.
   - Runtime es actualizado en directiva separada (NO automática). Drift entre spec firmado y runtime no actualizado es FAIL test B8.5(d) hasta sincronización.
5. Si `REJECT`:
   - Propuesta queda archivada con tag `REJECTED_T1`.
   - NO modificación a `B8_MAGNA_ACTION_TAXONOMY.md`.

### §5.4 Paso 4 — Sincronización runtime

1. Tras firma T1 magna, autor NO-Cowork (Manus E2) o Cowork T2-A propone PR de implementación runtime.
2. Test B8.5(d) auto-genera lista B8.1 a partir del spec firmado y compara con runtime.
3. Mismatch ⇒ FAIL hasta sincronización.

## §6 Frecuencia obligatoria de revisión

Independientemente de amendments propuestos, T1 firma magna verbatim revisión semestral del documento `B8_MAGNA_ACTION_TAXONOMY.md`:

| Periodicidad | Acción mínima |
|--------------|---------------|
| Semestral (cada 6 meses) | Re-firma magna verbatim sobre la lista vigente, aunque NO haya amendments. Esto reafirma que la lista sigue siendo cerrada y suficiente. |
| Anual | Sabio externo (rotativo) audita lista vigente vs casos reales del año, recomienda amendments si aplica. |
| Ad-hoc | Cualquier incidente que evidencie acción magna no listada dispara amendment AMD-ADD obligatorio. |

## §7 Riesgos y mitigaciones

| ID | Riesgo | Mitigación |
|----|--------|------------|
| R-AMD-1 | Cowork modifica lista sin firma T1 | Branch protection rules + PR review obligatorio T1 + audit log inmutable |
| R-AMD-2 | Sabio externo confabula con productor para colar AMD-REMOVE injustificado | Rotación trimestral terna B11 + audit log público + revisión semestral T1 |
| R-AMD-3 | Drift entre spec firmado y runtime tras AMD-ADD | Test B8.5(d) auto-detecta; FAIL hasta sincronización; runtime NO actualizado automáticamente |
| R-AMD-4 | Amendment propuesto por agente no autorizado (hilo Manus rogue) | Validación productor en Paso 1 (whitelist binaria); NO se procede a audit si productor no whitelist |
| R-AMD-5 | Firma magna T1 fingida | Verificación criptográfica B6 (ed25519) + custodios B7 + bridge audit log + log público de hashes |
| R-AMD-6 | Amendment cae en categoría incorrecta (AMD-REFINE que en realidad cambia alcance) | Audit adversarial Paso 2 obliga a Sabio externo + Cowork validar tipo correcto; mismatch ⇒ RECOMMEND_REVISE |

## §8 No-go binarios

| # | No-go | Status |
|---|-------|--------|
| 1 | NO modificación de B8_MAGNA_ACTION_TAXONOMY.md sin pasar Paso 1 → 2 → 3 | ✅ |
| 2 | NO firma de amendment por Cowork T2-A o cualquier no-T1 | ✅ |
| 3 | NO bypass de audit adversarial Paso 2 | ✅ |
| 4 | NO sincronización automática runtime sin Paso 4 explícito | ✅ |
| 5 | NO modificación retroactiva de amendments firmados | ✅ |
| 6 | NO amendment vía DELTA o vía MCP automatizado | ✅ |
| 7 | NO emergency amendment sin firma T1 (NO existe modo emergencia bypass) | ✅ |
| 8 | NO override por mayoría Sabios sin firma T1 | ✅ |

## §9 Decisión T1 requerida

T1 firma magna verbatim sobre este procedimiento para:

1. Aprobación verbatim de los 3 tipos de amendment (AMD-ADD / AMD-REFINE / AMD-REMOVE).
2. Aprobación verbatim de los 4 pasos del procedimiento binario.
3. Aprobación verbatim de la frecuencia obligatoria de revisión (semestral re-firma + anual audit Sabio + ad-hoc por incidente).
4. Aprobación verbatim de los 8 no-go binarios.
5. Aprobación verbatim de que T1 es el ÚNICO firmante magna.

## §10 Caveat magno F16 estructural Opus 4.7

Este procedimiento lo propuso un autor NO-Cowork (Manus E2). La firma magna T1 sobre este archivo NO equivale a decisión doctrinal de integración del pack B8 en v1.1.1, v2.0 RE-FUNDADO, o v3.0 sintetizada. La integración doctrinal sigue siendo decisión binaria T1 fuera de mi scope.
