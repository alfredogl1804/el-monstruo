# B12c-E1 — Plazo firmado para ejecución posterior de DORY_BENCH (opción b⇒a)

**Gate:** B12 — Recuantificación métrica `96% / <4%`
**Sub-criterio:** B12c.2 (definido en B6_B12_DESIGN_CLOSURE_PACK_v0_2.md §7.2)
**Fecha emisión:** 2026-05-20
**Autor verbatim:** Manus E2 (autor NO-Cowork, redactor — NO firmador)
**Firmante autoritativo:** T1 (Alfredo Góngora) — firma magna pendiente vía commit signature
**Estado:** EVIDENCE DRAFT — pendiente firma T1 verbatim antes de canon

---

## §1 Decisión T1 verbatim

T1 firmó el 2026-05-20 la opción **b⇒a** del gate B12 (declarar obsolescencia ahora + agendar ejecución DORY_BENCH posterior con plazo firmado). El presente artefacto canoniza el componente **plazo** de esa decisión, conforme a B12c.2 PASS criterion.

## §2 Plazo verbatim

**Fecha límite máxima:** `2026-08-20` (formato ISO `YYYY-MM-DD`).

**Cláusula binaria de adelanto:** la ejecución de DORY_BENCH puede realizarse **antes** del `2026-08-20` si y solo si los tres pre-requisitos siguientes quedan PASS (firmados T1) en cualquier momento previo:

| Pre-requisito | Gate | Definición operativa para PASS |
|---------------|------|---------------------------------|
| **B4 PASS** | DORY_BENCH cases canonizados | Los 1425 cases canonizados están publicados en `bridge/spec/B4_DORY_BENCH_CASES.md` con runner reproducible y firma T1 sobre el set verbatim. |
| **B7 PASS** | Hidden fixture custody no-compositor | Los 50 hidden fixtures están bajo custodia separada (T1 escrow / cuentas cloud privadas controladas por T1 / HSM-KMS / humanos delegados / repos privados cifrados por custodio), Sabios LLM auditan vía hashes/métricas sanitizadas únicamente, y la verificación criptográfica B7.8 está firmada T1. |
| **B11 PASS** | Sustitución Grok re-pass por terna rotativa | Calendario rotativo Q1-Q4 firmado T1, Sabio activo trimestral designado, KL divergence inter-Sabios medida con artefacto B11-E6, política de deprecación de modelos firmada. |

Si los tres pre-requisitos quedan PASS antes del `2026-08-20`, el owner B12c-E2 está habilitado para ejecutar DORY_BENCH en cualquier momento dentro de la ventana `[firma B11 PASS, 2026-08-20]`.

Si alguno de los tres pre-requisitos NO queda PASS antes del `2026-08-20`, el plazo entra en zona de **renegociación obligatoria** (ver §3).

## §3 Política de extensión y renegociación de plazo

El plazo `2026-08-20` no es absoluto. Está sujeto a las siguientes reglas binarias firmadas T1:

### §3.1 Notificación de aproximación de plazo

VERIFICADOR-001 (cuando esté implementado, ver gate B9) o el owner B12c-E2 (en su ausencia) emite evento `B12C_DEADLINE_APPROACHING` cuando faltan **≤14 días** para el plazo. Destinatarios: T1 (firmante autoritativo), Cowork T2-A (auditor observador, no validador), Sabio externo de la terna B11 activa (auditor independiente).

### §3.2 Caminos binarios al cumplir ≤14 días para plazo

Si quedan ≤14 días para el `2026-08-20` y la ejecución (a) NO se ha completado, T1 firma uno de tres caminos verbatim:

| Camino | Acción | Resultado |
|--------|--------|-----------|
| **C1: Ejecutar (a) ahora** | Owner B12c-E2 ejecuta DORY_BENCH dentro del plazo restante; si concluye PASS antes del 2026-08-20, B12 transita a `PASS_AS_B12c_COMPLETO`. | B12 cierre cuantitativo |
| **C2: Extender plazo** | T1 firma extensión explícita con nueva fecha verbatim en formato `YYYY-MM-DD` y razón verbatim (p.ej. "B7 sigue en FAIL pendiente custodios HSM"). El nuevo plazo reemplaza el `2026-08-20` y el ciclo §3.1 se reinicia con la nueva fecha. | Plazo renovado |
| **C3: Aceptar `PASS_AS_B12c (b inmediata)` como estado terminal** | T1 firma verbatim que la métrica binaria PASS/FAIL en los 12 gates es la única vigente sin reactivación cuantitativa programada. La métrica `96%/<4%` queda obsoleta sin sucesor numérico. | B12 cierre cualitativo terminal |

### §3.3 No-go binario

Está prohibido binariamente lo siguiente, conforme regla dura del gate B12 v0.2:

- Dejar pasar el plazo `2026-08-20` sin firmar uno de los tres caminos C1/C2/C3.
- Firmar extensión sin razón verbatim trazable.
- Sostener implícitamente la métrica `96%/<4%` después del 2026-08-20 sin medición ni declaración terminal.
- Producir evidencia (a) parcial sin auditoría B12a-E3 (Sabios externos cross-family) y firma T1.

## §4 Trazabilidad

| Campo | Valor |
|-------|-------|
| Decisión T1 origen | Prompt verbatim 2026-05-20 "MANUS E2 — B12 b⇒a EVIDENCE PACK" |
| Sección spec referenciada | `B6_B12_DESIGN_CLOSURE_PACK_v0_2.md` §7.2 (B12c.2) |
| Branch entrega | `control-tower/2026-05-20-b12-b-to-a-evidence-pack` (rama lateral, NO main) |
| Criterio PASS asociado | B12c.2 (plazo verbatim firmado T1) |
| Auditor asociado | Sabio externo + Cowork T2-A (auditor, no firmante) |

## §5 Firma magna pendiente

Este artefacto entra en estado **EVIDENCE DRAFT** hasta que T1 firme verbatim el commit que lo introduce a la rama `control-tower/2026-05-20-b12-b-to-a-evidence-pack`. Manus E2 **no firma**. Cowork **no firma**. Solo T1 firma plazo binario por mandato del audit Cowork 2026-05-20 §3 (Sabios LLM auditan, no custodian, no firman plazos).

---

**Cierre binario:**

| Confirmación | Status |
|--------------|--------|
| No implementé runtime | ✅ |
| No modifiqué main | ✅ (rama lateral) |
| No abrí PR | ✅ |
| No canonizo runtime | ✅ (DRAFT pendiente firma T1) |
| No declaro Dory muerto | ✅ |
| No activo Fase 1 | ✅ |
