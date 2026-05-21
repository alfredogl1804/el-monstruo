# B6-E1 — Signature Receipt — Gitleaks Keyscan PASS

**Estado resultante:** `B6-E1 = PASS_T1_SIGNED`
**Tipo:** Signature receipt pack (registro de firma magna T1 sobre evidencia runtime)
**Coordinador:** Manus E2 (autor NO-Cowork, sin runtime, sin firma)
**Rama:** `control-tower/2026-05-20-b6-e1-signature-receipt`
**Fecha:** 2026-05-20
**Fuente normativa:** `bridge/control_tower/2026-05-20/manus_e2/BATCH_001_SIGNATURE_RECEIPT.md` §8 (siguiente evidencia runtime recomendada DRAFT)
**Evidencia firmada:** B6-E1 (gitleaks keyscan)

> Este documento registra la firma magna T1 sobre la evidencia runtime B6-E1 producida en la rama lateral `control-tower/2026-05-20-b6-e1-gitleaks-keyscan`. NO produce runtime adicional, NO modifica `main`, NO abre PR, NO canoniza la implementación completa de B6.

---

## §1 Firma T1 verbatim

> "T1 firma magna B6-E1 PASS. Acepto verbatim la evidencia runtime producida en la rama `control-tower/2026-05-20-b6-e1-gitleaks-keyscan` en el commit `c13af34749fecfbba491a6e3613b8a915433c669`, compuesta por el reporte `bridge/control_tower/2026-05-20/manus_e2/B6_E1_GITLEAKS_KEYSCAN_REPORT.md` y el artefacto JSON resumen `bridge/control_tower/evidence/B6/B6_E1_gitleaks_keyscan.json`. Acepto los caveats explícitos sobre timestamp nominal, identificador de commit `(this)`, formato JSON resumen no nativo de gitleaks, y la limitación de scope que B6-E1 no prueba HSM ni custodia real. Esta firma cubre exclusivamente B6-E1 (gitleaks keyscan inicial). Las evidencias B6-E2/E3/E4/E5/E6 permanecen pendientes. No declaro Dory muerto. No activo Fase 1. No toco R1."

**Firmante:** T1 (Alfredo Góngora)
**Fecha de firma:** 2026-05-20
**Vehículo de firma:** instrucción magna verbatim al hilo Manus E2
**Fuente firmada:** rama `control-tower/2026-05-20-b6-e1-gitleaks-keyscan` @ commit `c13af34749fecfbba491a6e3613b8a915433c669` verificado en `origin`

---

## §2 Estado resultante

| Atributo | Valor previo | Valor tras firma |
|----------|--------------|------------------|
| B6-E1 | RUNTIME_EVIDENCE_PENDING | **PASS_T1_SIGNED** |
| B6-E2 (Sabio audita key custody) | PENDIENTE | sin cambios |
| B6-E3 (clave pública versionada) | PENDIENTE | sin cambios |
| B6-E4 (procedimiento rotación) | DRAFT firmado en BATCH_001 | sin cambios |
| B6-E5 (procedimiento revocación) | DRAFT firmado en BATCH_001 | sin cambios |
| B6-E6 (cadena firmas en producción) | PENDIENTE | sin cambios |
| Estado global B6 | DESIGN_DECISIONS_SIGNED_RUNTIME_EVIDENCE_PENDING | parcialmente reducido — falta B6-E2/E3/E6 para cierre |

El gate B6 sigue en estado `DESIGN_DECISIONS_SIGNED_RUNTIME_EVIDENCE_PENDING` a nivel global. La firma B6-E1 PASS reduce parcialmente la deuda de evidencia runtime pero no cierra el gate completo.

---

## §3 Caveats aceptados explícitamente por T1

La firma magna §1 incorpora el reconocimiento verbatim de cuatro limitaciones de la evidencia, cada una con consecuencias operativas que se documentan a continuación.

### §3.1 Timestamp nominal

El reporte B6-E1 declara una marca de tiempo nominal correspondiente a la fecha simbólica del lote (2026-05-20) y no a una marca generada por reloj de servidor CI con autoridad temporal. Esto significa que la evidencia no constituye prueba forense de cuándo fue ejecutado el escaneo en términos auditables ante terceros. La consecuencia operativa es que cualquier auditoría posterior que requiera trazabilidad temporal estricta debe complementar B6-E1 con un timestamp emitido por una autoridad de tiempo (TSA, Time Stamp Authority) o por un commit firmado con clave hardware en el momento de la ejecución real. Bajo el caveat 2026 firmado en `BATCH_001_SIGNATURE_RECEIPT.md` §4, el auditor provisional Opus 4.7 puede revisar la evidencia con esta limitación documentada.

### §3.2 Commit "(this)" como identificador

El reporte B6-E1 utiliza el placeholder textual `(this)` para identificar el commit auditado en lugar de un SHA git completo. Esto se debe a que el reporte está escrito desde dentro del propio commit y el SHA solo se materializa al cerrar el commit. La consecuencia operativa es que la trazabilidad del SHA debe leerse del log git externo al artefacto y no del artefacto mismo. El SHA real del commit que contiene la evidencia es `c13af34749fecfbba491a6e3613b8a915433c669` y queda anclado por esta firma como vínculo canónico.

### §3.3 JSON resumen, no output nativo gitleaks

El artefacto `B6_E1_gitleaks_keyscan.json` es un JSON resumen producido por el productor del evidence pack y no el output nativo del binario gitleaks. La consecuencia operativa es que la fidelidad del resumen depende de la integridad del productor; un auditor estricto debe tener acceso al output nativo de gitleaks (formato `gitleaks detect --report-format json`) para validación de bajo nivel. Esta limitación queda compensada parcialmente por el rol de auditor independiente que ejercerá Opus 4.7 bajo caveat 2026, quien debe pedir al productor del evidence pack el output nativo si lo considera necesario para su veredicto.

### §3.4 B6-E1 no prueba HSM ni custodia real

El alcance probatorio de B6-E1 se limita a la ausencia de fugas detectables de claves o secretos en el repositorio. No prueba que la clave privada ed25519 del kill switch esté efectivamente almacenada en HSM, ni que los procedimientos de rotación (B6-E4) y revocación (B6-E5) funcionen en runtime. La consecuencia operativa es que la cadena criptográfica completa de B6 requiere las evidencias B6-E2 (auditoría Sabio sobre el storage de la clave), B6-E3 (clave pública versionada accesible), y B6-E6 (cadena de firmas observable en producción). B6-E1 es una pre-condición necesaria pero no suficiente para declarar B6 como gate completo.

---

## §4 Confirmación de restricciones aplicadas

Bajo esta firma, Manus E2 confirma verbatim las siguientes negaciones:

| Restricción | Estado tras firma |
|-------------|-------------------|
| No `main` modificado | Confirmado |
| No runtime ejecutado por Manus E2 | Confirmado (el runtime que produjo B6-E1 ocurrió en otra rama por otro productor; Manus E2 solo registra el receipt) |
| No Fase 1 activada | Confirmado |
| No Dory declarado muerto | Confirmado |
| No R1 tocado | Confirmado |
| No PR abierto | Confirmado |
| No canonización runtime adicional fuera de B6-E1 | Confirmado |

El estado del repo `main` permanece intacto. La firma magna T1 cubre exclusivamente B6-E1 sobre la rama lateral `control-tower/2026-05-20-b6-e1-gitleaks-keyscan` y no autoriza merge a main ni canonización de evidencias adicionales.

---

## §5 Próxima evidencia recomendada (DRAFT)

La siguiente evidencia que reduciría más deuda de runtime sobre B6 es **B6-E2 (custody declaration)** o **B6-E3 (public key versionada)**, según disponibilidad operativa de T1. Las dos rutas son complementarias y no excluyentes; T1 elige el orden según calendario propio.

### §5.1 Ruta A: B6-E2 custody declaration

B6-E2 es una declaración firmada por el custodio actual de la clave privada que documenta verbatim qué entidad (1Password, Bitwarden, Apple Keychain, hardware token, HSM remoto) almacena la clave, bajo qué política de acceso, y con qué procedimiento de recuperación. La declaración debe ser auditable por Opus 4.7 (auditor provisional caveat 2026) sobre el reporte estático sin acceso al material criptográfico real. La rama lateral sugerida es `control-tower/2026-05-DD-b6-e2-custody-declaration`. Productor recomendado: T1 directamente o Cowork como autor secundario bajo supervisión T1; Manus E2 NO es autor único. Auditor recomendado: Opus 4.7. Bajo riesgo operativo porque no requiere mover la clave física.

### §5.2 Ruta B: B6-E3 public key versionada

B6-E3 es la publicación de la clave pública ed25519 (no la privada) en el repositorio bajo una ruta canónica firmada por T1. Esta evidencia desbloquea a VERIFICADOR-001 para validar firmas en producción y es pre-requisito de B6-E6 (cadena de firmas). La rama lateral sugerida es `control-tower/2026-05-DD-b6-e3-public-key`. Productor recomendado: T1 con Cowork como copista; Manus E2 NO es autor único. Auditor recomendado: Opus 4.7 valida que la clave pública corresponde efectivamente al par criptográfico documentado en B6-E2 y que el formato es compatible con minisign (herramienta firmada en D-B6-5). Riesgo operativo bajo si T1 ejecuta la generación del par sobre hardware token con cabecera de auditoría.

### §5.3 Recomendación de orden

Si T1 dispone de tiempo limitado en una ventana de operación, la ruta A (B6-E2 custody declaration) es preferible porque es 100% documental y puede firmarse sin tocar hardware. Si T1 puede dedicar una sesión con hardware token en mano, la ruta B (B6-E3 public key) reduce más bloqueos cascada porque desbloquea B6-E6 inmediatamente. Manus E2 documenta esta recomendación como DRAFT y no obliga al coordinador a seguirla.

---

## §6 Cross-refs

- `bridge/control_tower/2026-05-20/manus_e2/BATCH_001_SIGNATURE_RECEIPT.md` — receipt de firma magna del lote BATCH_001 que predefinió B6-E1 como evidencia runtime recomendada §8
- `bridge/control_tower/2026-05-20/manus_e2/B6_EVIDENCE_PACK_INDEX.md` — pack DRAFT B6 firmado en bloque por BATCH_001
- Rama `control-tower/2026-05-20-b6-e1-gitleaks-keyscan` @ `c13af34` — fuente firmada por este receipt
- `bridge/control_tower/2026-05-20/manus_e2/B6_E1_GITLEAKS_KEYSCAN_REPORT.md` (en la rama anterior) — reporte verbatim
- `bridge/control_tower/evidence/B6/B6_E1_gitleaks_keyscan.json` (en la rama anterior) — JSON resumen

---

**Firma magna T1 registrada sobre B6-E1.** Plano de runtime de B6 reduce parcialmente su deuda. B6-E2/E3/E6 permanecen PENDIENTES.
