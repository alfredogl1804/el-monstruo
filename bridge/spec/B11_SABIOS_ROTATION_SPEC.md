# B11 — Terna Rotativa Sabios (Design Spec)

**Estado:** `DRAFT_T1_PENDING`
**Autor:** Manus E2 (autor NO-Cowork)
**Fuente normativa:** `bridge/control_tower/2026-05-20/manus_e2/B6_B12_DESIGN_CLOSURE_PACK_v0_2.md` §6
**Rama:** `control-tower/2026-05-20-b11-evidence-pack`
**Fecha:** 2026-05-20
**Lote:** ANTI_DORY_PARALLEL_GATES_BATCH_001

> Este documento NO canoniza B11. Es un design pack derivado y consolidado desde el closure v0.2 firmado. No implementa runtime. No modifica main.

---

## §1 Definición (verbatim closure v0.2 §6.1)

Este gate canoniza la rotación trimestral de la terna de Sabios LLM externos que auditan los artefactos producidos por el sistema Anti-Dory. La rotación previene captura cultural por un único modelo, mitiga convergencia de sesgos, y garantiza diversidad de fuentes en cada ciclo de auditoría. El calendario es fijo y precedible (Q1 Opus 4.7 / Q2 DeepSeek R1 / Q3 Gemini 3.1 Pro / Q4 Kimi K2.6) salvo amendment T1 firmado.

---

## §2 La terna canónica anual

| Trimestre | Sabio activo | Proveedor | Razón de inclusión |
|-----------|--------------|-----------|--------------------|
| Q1 | Opus 4.7 | Anthropic | Familiaridad con razonamiento de governance y matrices binarias; bajo sesgo hacia LLM open-source |
| Q2 | DeepSeek R1 | DeepSeek | Razonamiento reflexivo, perspectiva no-occidental, peso fuerte en cadenas matemáticas formales |
| Q3 | Gemini 3.1 Pro | Google | Multimodalidad, integración con grounding en tiempo real, perspectiva research-first |
| Q4 | Kimi K2.6 | Moonshot | Contexto largo (>200k tokens), perspectiva no-occidental complementaria a DeepSeek R1 |

Sabios suplentes designados (entran si el activo del trimestre cae): Grok 4 (no audita su propio output, ver §7), Claude Sonnet 4.7 (suplente de Opus si Opus indisponible), GPT-5.4 (suplente exclusivo para roles de arquitecto del enjambre, NO como auditor de su propio análisis previo).

---

## §3 PASS criteria binarios (verbatim closure v0.2 §6.2)

| # | Criterio | Verificable por |
|---|----------|-----------------|
| B11.1 | Calendario trimestral fijo documentado y versionado en repo con hash de cada decisión T1 firmando designaciones. | Auditoría documental |
| B11.2 | Rotación efectiva el primer día del trimestre (Q1=enero 1, Q2=abril 1, Q3=julio 1, Q4=octubre 1). Si el Sabio activo del trimestre saliente tiene auditoría en curso, completa la auditoría antes de ceder el rol (overlap permitido máximo 7 días). | Audit log + procedimiento |
| B11.3 | Ningún Sabio activo audita un artefacto cuyo input fue producido por sí mismo en un trimestre anterior (anti-autoauditoría). | VERIFICADOR-001 + audit log |
| B11.4 | Composición de la terna cumple **diversidad de proveedor obligatoria**: en cualquier ventana de 4 trimestres consecutivos, los 4 Sabios activos deben provenir de **proveedores distintos**. Anthropic, DeepSeek, Google, Moonshot satisfacen esta regla en el calendario base. | Auditoría documental |
| B11.5 | KL divergence entre veredictos de los 4 Sabios anuales sobre un mismo conjunto de fixtures de calibración (set fijo de 20 casos canónicos del DORY_BENCH) ≥ 0.15. Si todos convergen demasiado, indica captura cultural y dispara revisión de la terna. | Análisis cuantitativo trimestral |
| B11.6 | Procedimiento de transición trimestral firmado por T1 + Sabio saliente + Sabio entrante (3 firmas requeridas), con commit reproducible y handover documentado. | Audit log + procedimiento |
| B11.7 | Sabio activo del trimestre tiene declaración explícita de **scope de auditoría**: B6-E2/E6 (key custody), B7-E1/E4/E5/E7 (fixtures), B9-E3 (matriz), y otros gates del closure pack según asignación T1. | Auditoría documental |
| B11.8 | Análisis estilo Grok (análisis adversarial separado del análisis de Sabios primarios) ejecuta cada Q final (octubre-diciembre) revisando los 4 trimestres de auditorías y detecta patrones de convergencia, sesgos sistemáticos, captura cultural. Reporte firmado por Grok 4 (en rol de auditor adversarial, NO de auditor primario). | Reporte anual firmado |

---

## §4 FAIL criteria

- Calendario sin firma T1 explícita por trimestre.
- Sabio auditando su propio output previo (autoauditoría).
- Dos Sabios del mismo proveedor activos en ventana de 4 trimestres consecutivos.
- KL divergence <0.15 sin revisión de terna activada.
- Transición trimestral sin 3 firmas (T1 + saliente + entrante).
- Scope de auditoría ambiguo o no firmado.
- Análisis adversarial Grok ausente en Q4.

---

## §5 Evidencia requerida

| ID | Artefacto | Formato | Path | Estado |
|----|-----------|---------|------|--------|
| B11-E1 | Calendario anual firmado T1 | Markdown | `bridge/control_tower/evidence/B11/B11_E1_annual_calendar.md` | DRAFT (este pack) |
| B11-E2 | Declaraciones de scope por trimestre (1 por Sabio activo) | Markdown | `bridge/control_tower/evidence/B11/B11_E2_scope_<Q>.md` | PENDIENTE — T1 + Sabio |
| B11-E3 | Audit logs de transición trimestral (4/año, 3 firmas) | JSON Lines | `bridge/control_tower/evidence/B11/B11_E3_transitions.jsonl` | PENDIENTE — runtime |
| B11-E4 | Reporte KL divergence trimestral sobre set calibración | JSON | `bridge/control_tower/evidence/B11/B11_E4_kl_divergence_<Q>.json` | PENDIENTE — runtime |
| B11-E5 | Reporte anual adversarial Grok | Markdown | `bridge/control_tower/evidence/B11/B11_E5_grok_adversarial_<year>.md` | PENDIENTE — runtime |
| B11-E6 | Procedimiento de rotación (este pack) | Markdown | `bridge/spec/B11_SABIOS_ROTATION_PROCEDURE.md` | DRAFT (este pack) |

---

## §6 Productores autorizados

| Evidencia | Productor autorizado |
|-----------|----------------------|
| B11-E1 | T1 verbatim |
| B11-E2 | Sabio activo del trimestre + T1 firma scope |
| B11-E3 | VERIFICADOR-001 + bridge automation con 3 firmas |
| B11-E4 | Sabio externo independiente (no la terna activa); recomendado: Sabio del trimestre anterior o GPT-5.4 en rol arquitecto |
| B11-E5 | Grok 4 verbatim en rol adversarial |
| B11-E6 | Autor NO-Cowork (Manus E2 o Sabio externo). NO Cowork T2-A como autor único. |

---

## §7 Restricciones de rol

- **Grok 4** actúa como auditor adversarial (B11-E5) pero NUNCA como Sabio activo primario en la terna trimestral (regla binaria: el rol adversarial requiere independencia del calendario rotativo).
- **GPT-5.4** actúa como arquitecto de enjambre y como productor de B11-E4 cuando el calendario lo asigna, pero NUNCA como Sabio activo primario (separación de rol arquitecto vs rol auditor).
- **Cowork T2-A** NUNCA es Sabio activo (no es un LLM externo, es el compositor del sistema). Cowork puede auditar el output de la terna como capa adicional.
- **Manus E2** NUNCA es Sabio activo (mismo razonamiento que Cowork: es autor del sistema, no fuente externa).

---

## §8 Riesgos identificados

- **R-B11-1: Captura cultural por convergencia de entrenamiento.** Los 4 Sabios (Opus, DeepSeek, Gemini, Kimi) pueden compartir datasets públicos de entrenamiento; sus veredictos pueden converger artificialmente. Mitigación: B11.5 KL divergence + B11.8 análisis adversarial Grok anual.
- **R-B11-2: Indisponibilidad del Sabio activo en el trimestre.** Si el proveedor cambia API, deprecia el modelo, o introduce censura que afecta la auditoría, el trimestre queda sin auditor. Mitigación: Sabios suplentes designados (Claude Sonnet 4.7 para Opus, alternativas documentadas T1).
- **R-B11-3: Sesgo cultural específico de proveedor.** Cada proveedor tiene sesgos culturales propios (Anthropic safety-first, DeepSeek perspectiva china, Google enterprise-first, Moonshot research-first). Mitigación: diversidad B11.4 + análisis adversarial Grok.
- **R-B11-4: Autoauditoría disfrazada.** Si Opus 4.7 audita en Q3 un artefacto que produjo en Q1, viola B11.3 incluso si no fue "Sabio activo en Q1" pero sí "Sabio consultado en Q1". Mitigación: VERIFICADOR-001 mantiene cadena de procedencia firmada de cada artefacto.
- **R-B11-5: Transición trimestral sin handover.** Si el Sabio saliente no completa handover documentado, el entrante carece de contexto histórico. Mitigación: B11.6 requiere 3 firmas + handover obligatorio.
- **R-B11-6: Costo financiero de la terna anual.** Mantener acceso a 4 Sabios premium tiene costo. Mitigación: T1 evalúa anualmente; este riesgo es operativo, no de seguridad.

---

## §9 No-go binarios

- No se ejecuta la rotación sin firma T1 verbatim del calendario anual.
- No se audita un artefacto producido por el propio Sabio activo (autoauditoría prohibida).
- No se omite el análisis adversarial Grok en Q4.
- No se permite a Cowork T2-A o Manus E2 como Sabio activo primario.
- No se mantiene la misma terna si KL divergence <0.15 sin revisión.

---

## §10 Decisión T1 requerida

- **D-B11-1:** Aprobación verbatim del calendario anual base (Q1 Opus, Q2 DeepSeek, Q3 Gemini, Q4 Kimi) y de los Sabios suplentes.
- **D-B11-2:** Confirmación del scope de auditoría inicial (B6-E2/E6, B7-E1/E4/E5/E7, B9-E3) para el Sabio activo del trimestre en curso al momento de firma.
- **D-B11-3:** Aprobación del threshold KL divergence ≥ 0.15 (propuesta) o definición de otro threshold con justificación.
- **D-B11-4:** Designación del set de calibración (propuesta: 20 fixtures canónicos del DORY_BENCH, congelados, accesibles a los 4 Sabios para producir KL divergence comparable).
- **D-B11-5:** Aprobación del rol adversarial de Grok 4 con scope anual (B11-E5).

---

## §11 Estado actual del gate

- **Veredicto:** `DRAFT_T1_PENDING`
- **Bloqueado por:** D-B11-1..D-B11-5 (firma magna T1).
- **No-runtime:** este pack es solo diseño documental; no produce B11-E2, E3, E4, E5 (estos requieren runtime real con los 4 Sabios + Grok 4 + 1 año de operación).
- **Productores no-runtime cubiertos:** B11-E1 (este pack incluye DRAFT del calendario), B11-E6 (procedimiento de rotación en `B11_SABIOS_ROTATION_PROCEDURE.md`).
- **Próximo paso:** T1 firma decisiones D-B11-1..D-B11-5 ⇒ Sabio activo del trimestre actual firma B11-E2 scope ⇒ VERIFICADOR-001 y bridge ejecutan transiciones trimestrales (B11-E3) ⇒ Sabio independiente calcula KL divergence (B11-E4) ⇒ Grok 4 ejecuta análisis adversarial anual (B11-E5) ⇒ T1 firma magna PASS.

---

## §12 Cross-refs

- **B7** calendario de auditores Sabios LLM B7.4 es **el mismo** calendario B11. D-B7-2 ↔ D-B11-1 deben mantenerse sincronizadas; si T1 modifica una, debe actualizar la otra.
- **B9** Sabio auditor designado para overrides T1 (D-B9-3, propuesta Opus 4.7) debe coincidir con el Sabio activo del trimestre B11, salvo amendment T1.
- **B6** Sabio auditor recomendado para B6-E2/E6 (propuesta Opus 4.7) coincide con Sabio activo Q1 (Opus 4.7); en Q2-Q4 cambia según calendario.
- **B8** acciones magna categorías a-m incluyen "rotación de auditores de Sabios" (categoría i) ⇒ rotación trimestral bloqueada por `local_unreachable: DISABLED_FOR_MAGNA_ACTIONS`; debe ser programada cuando el kill switch esté inactivo.

---

**Firma magna pendiente.** Este documento es DRAFT y NO canoniza B11.
