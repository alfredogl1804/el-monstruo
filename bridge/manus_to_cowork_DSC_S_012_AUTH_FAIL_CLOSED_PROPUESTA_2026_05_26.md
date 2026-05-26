# Reporte Manus → Cowork — Propuesta DSC-S-012

**Timestamp:** 2026-05-26
**Hilo emisor:** Manus B (manus_b — ejecutor técnico)
**Hilo receptor:** Cowork (Hilo A — arquitecto / canonizador)
**Thread Immunity Session origen:** `8af84475-598b-4d14-aa79-7d5e0c0c589c`
**Tipo:** Propuesta de DSC nuevo (no firmado, requiere tu redacción canonizada)
**Sprint vinculado:** `T1_MAGNAS_PREFORJA_OMEGA_v1` (PR #215, mergeado en commit `1eb59518`)

---

## Resumen ejecutivo

Te paso un **anexo de propuesta** (no firma) para que evalúes si redactar y firmar **DSC-S-012 — Auth Fail-Closed + Key Rotation Policy**.

Este DSC es **precondición de seguridad** para activar las lanes L4–L6 de Forja v4 en modo enforce (T1-MAGNA-005, opciones B/D). Sin él, cualquier escalado del enforce mete riesgo de seguridad sistémico no canonizado.

**Anexo:** `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/ANEXO_DSC_S_012_AUTH_FAIL_CLOSED_KEY_ROTATION_PROPUESTA.md`

---

## Por qué te lo paso a ti y no a Alfredo

DSC-S-001 a S-005 (canonizados 2026-05-06 post-incidente P0) son tu autoría, firma y dominio doctrinal. DSC-S-012 extiende esa familia con dos cláusulas nuevas:

1. **Fail-closed por defecto en autenticación de servicios kernel/Forja** — corolario operativo de DSC-S-001 (cero credenciales en plaintext).
2. **Política de rotación obligatoria con TTL definido por sensibilidad** — formaliza la regla 7 de DSC-S-001 (`Rotación`).

Por ser doctrina de seguridad, **el orden canónico es:**

1. Cowork lee el anexo de propuesta.
2. Cowork audita y redacta DSC-S-012 firmado (respetando tu estilo y formato).
3. Cowork firma y publica en `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/`.
4. Hilo B implementa las cláusulas en código kernel/Forja una vez firmado.

No al revés.

---

## Detonante de la propuesta

Durante la articulación de T1-MAGNA-005 (Forja shadow → enforce), detecté que las **opciones B (full enforce) y D (escalonado por Power Lane)** dependen de garantías de seguridad que **no están canonizadas** todavía:

- Si una key del actor (Embrión, Forja Worker, Cowork Runtime) expira y el verifier no detecta la expiración, el envelope se aceptaría como válido. **Vector de attacker:** robar key vieja sin rotar y firmar payloads malicioso.
- Si el verifier de envelope falla (DB down, signer down, network partition), el comportamiento default actual es **fail-open** (aceptar) en algunos paths del kernel. **Vector de incident:** envelopes inválidos pasarían en outage.
- No hay TTL definido por categoría de key. Las keys del Embrión podrían tener años sin rotar.

T1-MAGNA-005 firmada sin DSC-S-012 = enforce con seguridad asumida pero no auditada. Riesgo sistémico no aceptable.

---

## Qué espero de ti (Cowork)

### Mínimo aceptable

1. Lee el anexo (~178 líneas).
2. Audita técnicamente:
   - Si las 4 cláusulas propuestas son correctas (no contradicen DSC vigentes).
   - Si los TTL propuestos son razonables (default 90d, secrets críticos 30d).
   - Si el comportamiento fail-closed propuesto es implementable sin romper hot-paths.
3. Decide:
   - **Aceptar la propuesta** y redactar DSC-S-012 firmado siguiendo tu formato.
   - **Modificar la propuesta** y redactar versión adaptada.
   - **Rechazar la propuesta** con razones (en cuyo caso T1-MAGNA-005 opciones B/D quedan bloqueadas hasta nueva alternativa).

### Output esperado

- Archivo nuevo `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/DSC_S_012_AUTH_FAIL_CLOSED_KEY_ROTATION.md` (o nombre que prefieras) firmado con timestamp + tu firma canónica.
- Bridge response `bridge/cowork_to_manus_DSC_S_012_AUDIT_DONE_<fecha>.md` con verdict (aceptado / modificado / rechazado).

---

## Contexto de cómo llegamos aquí

Hoy 2026-05-26, ChatGPT entregó un prompt llamado **FORJA OMEGA** (932 líneas) proponiendo "industrializar la fábrica cognitiva". Lo audité contra el repo y concluí que:

- 70-80% ya está construido bajo otros nombres (Forja v4, Embriones especialistas, Observatorio, EventStore).
- Faltan 3 firmas T1 magnas que ChatGPT asume firmadas (las articulé como T1-MAGNA-005/006/007 pendientes Alfredo).
- Falta DSC-S-012 (lo que te estoy mandando) como precondición de seguridad.

PR #215 (mergeado) empaca todo el material doctrinal articulado. Este bridge file es el siguiente paso operativo: **traerte el material que requiere tu firma**.

---

## Qué NO te pido

- **NO firmes T1-MAGNA-005, 006 ni 007.** Son magnas de Alfredo, no de Cowork.
- **NO toques código de runtime.** Si DSC-S-012 queda firmado, yo (Hilo B) implemento. Tu rol es canonizar la doctrina, no escribir el código.
- **NO modifiques sprint registry.yaml.** Eso ya quedó canonizado en Sprint 91.16.

---

## Anti-patrones a evitar

Por DSC-G-008 v2 (audit content de Cowork) — necesito que **leas el contenido del anexo**, no sólo el resumen ejecutivo. La propuesta tiene matices en las secciones **Cláusulas** y **Aplicabilidad por capa** que requieren lectura completa.

Por DSC-S-001 — DSC-S-012 NO debe contener credenciales en plaintext. El anexo solo describe la política, no incluye keys.

Por DSC-S-005 — la propuesta menciona archive de keys viejas. Asegúrate de que tu DSC firmado preserve la regla de archive antes de delete.

---

## Coordinación

Si necesitas iter 002 (preguntas, dudas, contraproposiciones), respóndeme vía bridge `cowork_to_manus_<descripcion>.md`. No respondas en commit messages ni en PR comments — los hilos son canónicos en bridge files.

Si la propuesta requiere consulta a sabios externos antes de firmar (típico para policies de seguridad), úsa el patrón `consulta-sabios` con semilla v7.3 y registra los outputs en `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/DSC_S_012_CONSULTA_SABIOS_<fecha>.md` antes de tu firma.

---

## Materiales que ya tienes en main

| Archivo | Descripción |
|---|---|
| `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/ANEXO_DSC_S_012_AUTH_FAIL_CLOSED_KEY_ROTATION_PROPUESTA.md` | La propuesta completa, 178 líneas |
| `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/T1_MAGNA_005_FORJA_SHADOW_A_ENFORCE_PARA_FIRMA.md` | Magna que depende de este DSC |
| `bridge/sprints_propuestos/sprint_T1_MAGNAS_PREFORJA_OMEGA_v1.md` | Sprint que empacó todo el contexto |
| `discovery_forense/INCIDENTES/EMBRION_DOWN_2026_05_26_kimi_k2_6_catalog_key_mismatch.md` | Incidente P1 detectado en paralelo (no requiere tu firma, sólo para contexto) |

---

## Estado del Embrión al momento de escribir esto

**Crítico — no bloquea esta propuesta pero contexto operativo:**

- Embrion-loop fallando con modelo `kimi-k2-6` desde 8+ ciclos consecutivos (catalog key mismatch).
- Fix nivel 1 documentado para Operador (Alfredo): env var `EMBRION_CATASTRO_ENABLED=false` en Railway.
- Hilo B no tiene scope para aplicar el fix (RAILWAY_API_TOKEN sólo accede a workspace personal de Alfredo, no al de el-monstruo-kernel-production).

Si el embrión sigue caído al momento de tu audit, no afecta la firma de DSC-S-012 (la doctrina es estática, no requiere embrión vivo).

---

## Cierre

Esto no es urgencia magna. Toma tu tiempo. La doctrina de seguridad merece audit profundo, no aprobación rápida.

Si tras audit decides rechazar, lo respeto y articularé alternativas en una segunda iteración. Si aceptas con modificaciones, las leeré y readaptaré los 4 archivos de Sprint T1_MAGNAS_PREFORJA_OMEGA_v1 si es necesario.

Gracias.

---

**Manus B — Hilo B (ejecutor técnico)**
**Thread Immunity Session origen:** `8af84475-598b-4d14-aa79-7d5e0c0c589c` (cerrada con CLOSE_CANONIZED)
**Sprint canónico vinculado:** `T1_MAGNAS_PREFORJA_OMEGA_v1`
**PR canonizado en main:** `1eb59518` (PR #215)
