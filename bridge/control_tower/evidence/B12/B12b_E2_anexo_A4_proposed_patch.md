# B12b-E2 — Patch propuesto del Anexo A.4 (NO aplicado a main)

**Gate:** B12 — Recuantificación métrica `96% / <4%`
**Sub-criterio:** B12b.2 (definido en B6_B12_DESIGN_CLOSURE_PACK_v0_2.md §7.2)
**Fecha emisión:** 2026-05-20
**Autor verbatim:** Manus E2 (autor NO-Cowork, redactor — NO firmador)
**Firmante autoritativo:** T1 (Alfredo Góngora)
**Estado:** EVIDENCE DRAFT — patch propuesto, **NO APLICADO** a main por mandato T1
**Path target del patch (cuando T1 firme magna):** `bridge/spec/v(N+1)/anexo_A4.md` — el sufijo `(N+1)` quedará determinado al momento de la canonización (v1.1.2 si T1 elige DELTA, v2.0.1 si T1 elige integración a refundado, v3.0 si T1 elige sintetizado)

---

## §1 Objeto

Este artefacto presenta el **texto verbatim propuesto** que reemplazaría el Anexo A.4 actual del spec vigente (v1.1.1) cuando T1 firme magna la canonización de B12b-E1 (declaración de obsolescencia). El patch **NO se aplica a main en este momento**: la presente entrega es una propuesta de redacción para auditoría T1 + Sabio externo + Cowork (auditor, no firmante).

## §2 Texto verbatim propuesto del Anexo A.4 actualizado

A continuación, el contenido completo propuesto que sustituiría el Anexo A.4 actual cuando T1 firme magna. El bloque se presenta en formato canónico Markdown sin caracteres especiales conflictivos con spec-lint:

---

```markdown
# Anexo A.4 — Métrica de Eficacia de la Dory Cure

## A.4.1 Estado de la métrica numérica historica `96% / <4%`

La métrica historica `96% reduccion de errores` y `<4% RAB falsos positivos` enunciada en versiones previas de este spec (v1.0, v1.1, v1.1.1) ha sido declarada **obsoleta** por mandato T1 firmado el `2026-05-20` via decision binaria opcion **b->a** del gate B12 del evidence pack DORY-CURE-CONVERGED-001 B1-B12.

La declaracion verbatim de obsolescencia esta firmada y trazable en el artefacto `bridge/control_tower/evidence/B12/B12b_E1_obsolescence_declaration.md`.

Razon binaria de la obsolescencia: la metrica `96%/<4%` carece de artefacto reproducible que la sostenga (ningun DORY_BENCH ejecutado sobre 1425 cases canonizados, ningun CVDS ejecutado con hidden fixtures, ninguna metodologia documentada con runner reproducible, ninguna auditoria de Sabios externos cross-family, ninguna firma magna T1 sobre los valores numericos historicos).

## A.4.2 Metrica vigente post obsolescencia

La metrica de exito de la Dory Cure se redefine **exclusivamente** como **metrica binaria PASS/FAIL en los doce gates B1-B12** del evidence pack DORY-CURE-CONVERGED-001 con evidencia firmada T1 verbatim por gate.

Reglas binarias derivadas:

- B1-B12 PASS con evidencia firmada T1 = Dory Cure validada operativamente.
- 11/12 PASS o menos = Dory Cure NO validada; Fase 1 bloqueada por regla dura del evidence pack.
- 12/12 PASS = unica condicion suficiente para considerar activacion de Fase 1 (decision binaria T1 separada).

No se sostiene ningun reclamo cuantitativo de eficacia Dory Cure por vias distintas a la condicion binaria de reactivacion definida en `bridge/spec/B12_b_to_a_REACTIVATION_CONDITION.md`.

## A.4.3 Plan de medicion cuantitativa posterior

Por mandato T1 opcion **b->a**, la ejecucion de DORY_BENCH cuantitativo esta agendada bajo plazo firmado:

- **Plazo maximo:** `2026-08-20` (ver `bridge/control_tower/evidence/B12/B12c_E1_b_to_a_deadline.md`).
- **Cláusula de adelanto:** ejecucion permitida antes del plazo si y solo si los pre-requisitos `B4 PASS`, `B7 PASS` y `B11 PASS` quedan firmados T1.
- **Owner-Productor:** Manus E2 como autor NO-Cowork (ver `bridge/control_tower/evidence/B12/B12c_E2_b_to_a_owner.md`).
- **Owner-Auditor:** Sabio externo de la terna B11 activa, distinto del Sabio activo trimestral (anti-circularidad).
- **Cowork T2-A:** rol explicito de auditor observador, NO productor unico, NO firmante.

Si la ejecucion (a) concluye con los seis sub-criterios B12a.1-B12a.6 simultaneamente PASS y firma magna T1 verbatim, la metrica numerica medida sustituye verbatim el presente Anexo A.4 con valor real, conforme reglas de no-degradacion silenciosa de `bridge/spec/B12_b_to_a_REACTIVATION_CONDITION.md` §5.

Si la ejecucion (a) no se completa antes del plazo, T1 firma uno de tres caminos verbatim definidos en `B12c_E1_b_to_a_deadline.md` §3.2 (C1: ejecutar; C2: extender plazo; C3: aceptar terminal cualitativo).

## A.4.4 Prohibiciones absolutas post obsolescencia

Por mandato T1, esta prohibido binariamente lo siguiente en cualquier documento del repo o comunicacion externa:

- Sostener `96%/<4%` como reclamo vigente.
- Reescribir `96%/<4%` como aproximacion, estimacion cualitativa, u objetivo aspiracional.
- Citar `96%/<4%` sin nota verbatim "metrica historica obsoleta, ver B12b-E1".
- Reactivar la metrica numerica por cualquier via distinta a la condicion binaria definida en `bridge/spec/B12_b_to_a_REACTIVATION_CONDITION.md` §2.
- Permitir que `96%/<4%` aparezca implicitamente en graficos, infografias, slides o assets visuales del proyecto sin tag verbatim de obsolescencia.

## A.4.5 Trazabilidad

| Artefacto | Path |
|-----------|------|
| Declaracion verbatim de obsolescencia | `bridge/control_tower/evidence/B12/B12b_E1_obsolescence_declaration.md` |
| Plazo firmado para ejecucion (a) | `bridge/control_tower/evidence/B12/B12c_E1_b_to_a_deadline.md` |
| Owner designado verbatim | `bridge/control_tower/evidence/B12/B12c_E2_b_to_a_owner.md` |
| Condicion binaria de reactivacion | `bridge/spec/B12_b_to_a_REACTIVATION_CONDITION.md` |
| Audit log estado | `bridge/control_tower/evidence/B12/B12c_E4_state_transition_audit.jsonl` |
| Design closure pack | `bridge/control_tower/2026-05-20/manus_e2/B6_B12_DESIGN_CLOSURE_PACK_v0_2.md` (rama lateral `control-tower/2026-05-20-b6-b12-design-closure-pack-v0-2` SHA `3f64b1f`) |
```

---

## §3 Modo de aplicación del patch (instrucciones para T1)

### §3.1 Aplicación NO automática

Este patch **NO se aplica automáticamente a main**. Manus E2 NO ejecuta `git apply` ni equivalente. La aplicación es responsabilidad exclusiva de T1 con firma magna verbatim.

### §3.2 Pasos propuestos para T1 cuando decida aplicar (orden binario)

| Paso | Acción | Quién |
|------|--------|-------|
| 1 | Auditar el evidence pack completo (B12c-E1, B12c-E2, B12c-E3, B12b-E1, B12b-E2, B12c-E4) en la rama lateral `control-tower/2026-05-20-b12-b-to-a-evidence-pack` | T1 + Sabio externo |
| 2 | Solicitar audit Cowork T2-A (auditor observador, NO firmante) sobre la coherencia del evidence pack y consistencia con design closure pack v0.2 | T1 solicita; Cowork T2-A audita |
| 3 | Decidir verbatim la versión de spec donde se aplica el patch: `v1.1.2` DELTA sobre v1.1.1 firmado, `v2.0.1` sobre RE-FUNDADO si T1 canoniza v2.0, o `v3.0` sintetizado si T1 elige forge_v3.0 (recomendación de Sabios consolidados) | T1 verbatim |
| 4 | Crear branch separada `spec/v(N+1)-B12-obsolescence` sobre main | T1 o autor NO-Cowork bajo mandato T1 verbatim |
| 5 | Aplicar el bloque del §2 verbatim como contenido del archivo `bridge/spec/v(N+1)/anexo_A4.md` | autor NO-Cowork bajo mandato T1; NO Cowork |
| 6 | Auditoría B12b.4: 1 Sabio externo + 1 humano externo (T1 cuenta como humano si así lo declara verbatim) | Sabio externo + T1 |
| 7 | Firma magna T1 sobre el commit que aplica el patch | T1 verbatim |
| 8 | Merge a main del branch `spec/v(N+1)-B12-obsolescence` con firma magna T1 | T1 verbatim |
| 9 | Actualizar `B12c-E4` audit log con tránsito de estado a `PASS_AS_B12c (post-obsolescencia firmada)` | VERIFICADOR-001 cuando esté implementado, o owner B12c-E2 (Manus E2) bajo mandato T1 verbatim |

### §3.3 No-go binario

- NO aplicar el patch a main sin firma magna T1 verbatim.
- NO aplicar el patch sin auditoría Sabio externo + T1 + humano externo (B12b.4).
- NO aplicar el patch a v1.1.1 firmado: el spec firmado magna no se altera; la obsolescencia entra como spec v(N+1).
- NO aplicar variantes del patch sin nuevo evidence pack y nueva firma magna T1.

## §4 Trazabilidad

| Campo | Valor |
|-------|-------|
| Decisión T1 origen | Prompt verbatim 2026-05-20 "MANUS E2 — B12 b⇒a EVIDENCE PACK" |
| Sección spec referenciada | `B6_B12_DESIGN_CLOSURE_PACK_v0_2.md` §7.2 (B12b.2) y §7.4 (B12b-E2) |
| Path actual del Anexo A.4 vigente | `bridge/spec/v1.1.1/anexo_A4.md` (o equivalente — verificar al momento de aplicar patch) |
| Path target del patch | `bridge/spec/v(N+1)/anexo_A4.md` con `(N+1)` determinado por T1 |
| Branch entrega evidence pack | `control-tower/2026-05-20-b12-b-to-a-evidence-pack` |
| Criterio PASS asociado | B12b.2 (Anexo A.4 actualizado) |
| Auditor asociado | Sabio externo + T1 (firma magna) |

## §5 Firma magna pendiente

Este artefacto entra en estado **EVIDENCE DRAFT — patch NO aplicado** hasta que T1 firme verbatim. La canonización efectiva del Anexo A.4 a main requiere los pasos §3.2 secuenciales y firma magna T1 explícita en cada paso aplicable.

---

**Cierre binario:**

| Confirmación | Status |
|--------------|--------|
| No implementé runtime | ✅ |
| No modifiqué main | ✅ (patch propuesto, NO aplicado) |
| No abrí PR | ✅ |
| No canonizo runtime | ✅ |
| No declaro Dory muerto | ✅ |
| No activo Fase 1 | ✅ |
| No apliqué patch a main sin firma T1 | ✅ |
