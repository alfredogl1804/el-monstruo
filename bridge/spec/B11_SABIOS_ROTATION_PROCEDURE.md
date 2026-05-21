# B11-E6 — Sabios Rotation Procedure

**Estado:** `DRAFT_T1_PENDING`
**Autor:** Manus E2 (autor NO-Cowork)
**Gate:** B11 — Terna rotativa Sabios
**Fuente normativa:** closure pack v0.2 §6.6
**Aplica a:** transición trimestral del Sabio activo + análisis adversarial anual

> Este procedimiento NO se ejecuta hasta que T1 firme D-B11-1..D-B11-5.

---

## §1 Cronograma de transición trimestral

Cada transición ocurre el primer día del trimestre con overlap permitido de hasta 7 días:

| Trimestre | Fecha de transición | Sabio saliente | Sabio entrante |
|-----------|---------------------|----------------|----------------|
| Q1 | 1 de enero | Kimi K2.6 (del año anterior) | Opus 4.7 |
| Q2 | 1 de abril | Opus 4.7 | DeepSeek R1 |
| Q3 | 1 de julio | DeepSeek R1 | Gemini 3.1 Pro |
| Q4 | 1 de octubre | Gemini 3.1 Pro | Kimi K2.6 |

---

## §2 Pre-condiciones (T-30 días)

Treinta días naturales antes de la transición:

1. T1 confirma que la disponibilidad y costo del Sabio entrante están vigentes (API key, cuota, SLA del proveedor).
2. El Sabio saliente recibe notificación de cierre de su trimestre y completa cualquier auditoría en curso.
3. Bridge automation prepara el set de calibración (20 fixtures DORY_BENCH) para enviar al Sabio entrante en T+1.
4. Si el calendario base requiere amendment (proveedor deprecó modelo, sabio indisponible, decisión T1), T1 firma decisión adicional con razón verbatim antes de T-7 días.

---

## §3 Pasos de la transición (día T)

### §3.1 Handover documentado

El Sabio saliente produce un handover en formato Markdown que incluye:

- Lista de artefactos auditados en su trimestre.
- Lista de findings críticos abiertos al cierre del trimestre.
- Decisiones tomadas y razones verbatim.
- Recomendaciones específicas para el Sabio entrante.

Este documento se firma con la identidad del Sabio saliente (vía API call firmada con la clave del Sabio, registrada por VERIFICADOR-001).

### §3.2 Aceptación del Sabio entrante

El Sabio entrante recibe:

- El handover §3.1.
- La declaración de scope B11-E2 firmada por T1 para el nuevo trimestre.
- El set de calibración (20 fixtures DORY_BENCH).
- Los hashes (no contenido) de los slices de fixtures B7 que auditará durante su trimestre.

El Sabio entrante firma aceptación con su identidad API.

### §3.3 Firma T1 + 3 firmas

El audit log B11-E3 requiere las tres firmas:

| Firma | Origen | Forma |
|-------|--------|-------|
| T1 | Alfredo Góngora | Commit firmado en el repo o firma Bridge UI |
| Sabio saliente | API del proveedor | Llamada API firmada al endpoint del Sabio que devuelve token de cierre |
| Sabio entrante | API del proveedor | Llamada API firmada al endpoint del Sabio que devuelve token de aceptación |

VERIFICADOR-001 valida las 3 firmas antes de promover la transición.

### §3.4 Cálculo de KL divergence trimestral (B11-E4)

Inmediatamente tras la transición, un Sabio independiente (no parte de la terna activa del trimestre saliente ni entrante) calcula la KL divergence sobre el set de calibración:

1. Se ejecutan los 20 fixtures sobre los 4 Sabios actuales (incluyendo al entrante y los 3 que ya operaron en trimestres anteriores del año).
2. Se computa la distribución de veredictos (PASS/FAIL/AMBIGUO) por fixture.
3. Se calcula la KL divergence pairwise entre los 4 Sabios.
4. Se reporta el promedio.

Si la KL divergence promedio cae por debajo de 0.15, se dispara `KL_DIVERGENCE_LOW` y T1 + Cowork + Grok 4 (adversarial) revisan la terna en sesión extraordinaria.

---

## §4 Análisis adversarial anual Grok (B11-E5)

Cada cuarto trimestre (octubre-diciembre), Grok 4 ejecuta análisis adversarial sobre las auditorías de los 4 trimestres del año:

1. Recibe los logs de las auditorías (B6-E2/E6, B7-E1/E4/E5/E7, B9-E3, B11-E3, B11-E4) sanitizados.
2. Detecta patrones de convergencia inusuales entre Sabios.
3. Detecta sesgos sistemáticos que pudieron pasar desapercibidos.
4. Detecta captura cultural (si los 4 Sabios coincidieron en validar artefactos que objetivamente no debieron pasar).
5. Produce reporte firmado con findings, severidad, y recomendaciones para el calendario del año siguiente.

El reporte se publica en `bridge/control_tower/evidence/B11/B11_E5_grok_adversarial_<year>.md` y T1 lo audita verbatim antes de firmar el calendario del año siguiente.

---

## §5 Triggers de rotación extraordinaria

Además del calendario fijo, una rotación extraordinaria del Sabio activo puede dispararse por:

| Trigger | Detector | Acción |
|---------|----------|--------|
| Sabio activo deprecated o offline >72h | Heartbeat API | Promover Sabio suplente designado |
| Sabio activo introduce censura que afecta auditoría | Reporte Sabio o T1 | Promover suplente + reporte forensics |
| Análisis adversarial Grok identifica captura cultural | B11-E5 | Revisión de calendario completo |
| Conflict of interest detectado (Sabio entrenado con datos comprometidos) | Reporte externo | Revisión calendario + retirar Sabio si aplica |

Toda rotación extraordinaria requiere firma T1 verbatim.

---

## §6 Audit log B11-E3 schema

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `transition_id` | uuid | Identificador único |
| `quarter_from` | string | `Q4-2026` |
| `quarter_to` | string | `Q1-2027` |
| `sabio_outgoing_id` | string | `opus-4.7-anthropic` |
| `sabio_incoming_id` | string | `deepseek-r1-deepseek` |
| `handover_doc_path` | string | path al markdown firmado |
| `t1_signature` | string | hash de la firma magna |
| `sabio_outgoing_signature` | string | token de cierre firmado |
| `sabio_incoming_signature` | string | token de aceptación firmado |
| `kl_divergence_pre_transition` | float | KL del trimestre saliente |
| `notes` | string | observaciones |

---

## §7 No-go

- No transición sin 3 firmas (T1 + saliente + entrante).
- No autoauditoría (B11.3).
- No Sabios del mismo proveedor en ventana 4Q consecutiva (B11.4).
- No omisión del cálculo KL divergence trimestral.
- No omisión del análisis adversarial Grok en Q4.
- No promoción de Cowork ni de Manus E2 como Sabio activo.
- No rotación durante `local_unreachable: DISABLED_FOR_MAGNA_ACTIONS` activo.

---

**Firma magna pendiente.** Este procedimiento entra en operación cuando T1 firme D-B11-1..D-B11-5.
