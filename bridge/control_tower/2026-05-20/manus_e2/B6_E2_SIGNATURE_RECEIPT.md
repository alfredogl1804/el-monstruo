# B6-E2 — Signature Receipt — Custody Declaration PASS

**Estado resultante:** `B6-E2 = PASS_T1_SIGNED`
**Tipo:** Signature receipt pack (registro de firma magna T1 sobre evidencia documental)
**Coordinador:** Manus E2 (redactor de receipt, NO auditor, NO autor de la evidencia)
**Rama:** `control-tower/2026-05-20-b6-e2-signature-receipt`
**Fecha:** 2026-05-20
**Fuente normativa:** `bridge/control_tower/2026-05-20/manus_e2/B6_E1_SIGNATURE_RECEIPT.md` §5 (Ruta A: B6-E2 custody declaration)
**Evidencia firmada:** B6-E2 (custody declaration)

> Este documento registra la firma magna T1 sobre la evidencia documental B6-E2 producida en la rama lateral `control-tower/2026-05-20-b6-e2-custody-declaration`. NO produce runtime, NO genera clave criptográfica, NO publica clave pública, NO modifica `main`, NO abre PR, NO canoniza la implementación completa de B6.

---

## §1 Firma T1 verbatim

> "T1 firma magna B6-E2 PASS. Acepto verbatim la declaración de custodia documentada en la rama `control-tower/2026-05-20-b6-e2-custody-declaration` en el commit `a95b1cced4941e7e99c7c715d928802e46b9408f`, archivo `bridge/control_tower/evidence/B6/B6_E2_custody_declaration.md`. La auditoría externa fue ejecutada por Gemini 3.1 Pro con veredicto `PASS_TO_T1_SIGNATURE`, con DeepSeek R1 como suplente disponible. Acepto los caveats explícitos sobre control del riesgo de sincronización iCloud/Keychain, sobre la ejecución física pendiente del esquema Shamir 3-de-5, sobre la naturaleza declarativa y no técnica de B6-E2, y sobre la dependencia restante de B6-E3 y B6-E6 para cierre completo del gate B6. Esta firma cubre exclusivamente B6-E2. No genero clave en este acto. No publico clave pública en este acto. No declaro Dory muerto. No activo Fase 1. No toco R1."

**Firmante:** T1 (Alfredo Góngora)
**Fecha de firma:** 2026-05-20
**Vehículo de firma:** instrucción magna verbatim al hilo Manus E2
**Fuente firmada:** rama `control-tower/2026-05-20-b6-e2-custody-declaration` @ commit `a95b1cced4941e7e99c7c715d928802e46b9408f` verificado en `origin`
**Auditoría externa:** Gemini 3.1 Pro = `PASS_TO_T1_SIGNATURE` (principal) | DeepSeek R1 = suplente disponible

---

## §2 Alcance firmado por T1

La firma magna del §1 cubre verbatim los siguientes elementos del régimen de custodia. Cada elemento queda canonizado como política operativa de B6.

### §2.1 Custodio designado y delegados

El custodio único de la clave privada ed25519 del kill switch del sistema Anti-Dory es el **OS Keychain de la Mac principal de T1**, accesible exclusivamente por el usuario T1 (Alfredo Góngora). No existen delegados autorizados con acceso a la clave privada bajo el régimen actual; cualquier delegación futura requiere amendment T1 explícito. Esta configuración es coherente con D-B6-1 firmado en BATCH_001.

### §2.2 Esquema de respaldo Shamir 3-de-5

T1 aprueba el esquema Shamir 3-de-5 firmado en D-B6-4 (BATCH_001) como política de respaldo. La ejecución física de los 5 slices Shamir queda pendiente. Hasta que la ejecución física se complete y se documente en una evidencia futura (B6-E2.1 o equivalente), la clave privada existe en custodia única sin respaldo distribuido material. Esto deja un riesgo de pérdida total ante falla del Keychain o del hardware Mac principal que T1 acepta verbatim bajo el caveat §3.2.

### §2.3 Restricción de uso pre-runtime

La clave privada B6 no debe usarse para firmar artefactos de Fase 1 ni para ejecutar runtime crítico hasta que el respaldo físico Shamir 3-de-5 esté completamente ejecutado y documentado. Esta restricción aplica como precondición técnica al avance hacia Fase 1 del sistema Anti-Dory y queda anclada por esta firma como bloqueador explícito.

### §2.4 Frecuencia de rotación

La clave privada se rota cada 90 días naturales o ante incidente de exposición, lo primero que ocurra. Esta política coincide verbatim con D-B6-2 firmado en BATCH_001. La rotación se ejecuta según el procedimiento documentado en `bridge/control_tower/keys/DORY_CURE_KEY_ROTATION_PROCEDURE.md` (B6-E4 DRAFT firmado en bloque por BATCH_001).

### §2.5 SLA de revocación

La revocación de emergencia de la clave privada debe completarse en menos de 60 minutos desde la detección del incidente. Esta política coincide verbatim con D-B6-2 (parte del flujo post-incidente) y con el procedimiento documentado en `bridge/control_tower/keys/DORY_CURE_KEY_REVOCATION_PROCEDURE.md` (B6-E5 DRAFT firmado en bloque por BATCH_001). El cumplimiento del SLA es responsabilidad del custodio T1 y se documenta como evidencia post-incidente cuando corresponde.

### §2.6 Herramienta de firma

La herramienta canónica de firma para artefactos B6 es **minisign**. Esta selección coincide verbatim con D-B6-5 firmado en BATCH_001. Cualquier cambio de herramienta requiere amendment T1 que actualice simultáneamente D-B6-5 y la presente declaración.

---

## §3 Caveats aceptados explícitamente por T1

La firma magna §1 incorpora el reconocimiento verbatim de cuatro limitaciones de la evidencia, cada una con consecuencias operativas que se documentan a continuación.

### §3.1 Riesgo de sincronización iCloud/Keychain

El OS Keychain de macOS sincroniza por defecto con iCloud Keychain bajo cuenta Apple ID del usuario. Esta sincronización transmite el material clave a infraestructura Apple cifrada extremo a extremo, pero introduce un riesgo de exposición ante compromiso de la cuenta Apple ID o ante backup automático en otros dispositivos no auditados. T1 acepta este riesgo y se compromete a controlarlo verificando explícitamente que la entrada de Keychain que contiene la clave privada B6 esté marcada como **no sincronizable con iCloud** o que la cuenta Apple ID asociada cumpla con los requisitos mínimos de seguridad (2FA hardware, sesiones auditadas, sin dispositivos secundarios con acceso al Keychain). La verificación de esta configuración queda pendiente como evidencia complementaria recomendada y no es bloqueador para B6-E2 PASS.

### §3.2 Shamir 3-de-5 no ejecutado físicamente

Como se anticipó en §2.2, los 5 slices Shamir aún no existen como artefactos físicos distribuidos. La política está aprobada y firmada, pero la ejecución material requiere una sesión criptográfica con hardware token donde T1 genere la clave, divida el material privado en 5 slices según esquema Shamir, y los entregue a las 5 ubicaciones de custodia firmadas en el régimen. Esta sesión es pre-requisito tanto de B6-E3 (publicación de la clave pública correspondiente al par criptográfico generado bajo el esquema Shamir) como del levantamiento de la restricción §2.3.

### §3.3 B6-E2 es declaración política, no attestation técnica

La evidencia B6-E2 documenta la **política de custodia** (qué entidad almacena qué, bajo qué régimen, con qué SLAs). NO constituye una attestation técnica que pruebe que el material clave está efectivamente almacenado en un secure enclave de hardware certificado, ni que el Keychain de macOS esté operando en modo enclave-backed para esta entrada específica. Una attestation técnica completa requeriría artefactos adicionales como output de `security find-generic-password` con flags de auditoría, captura del SEP (Secure Enclave Processor) attestation, o equivalente. T1 acepta verbatim que B6-E2 cubre el plano declarativo y que el plano técnico-criptográfico se cubre por las evidencias B6-E3 (par criptográfico real publicable) y B6-E6 (cadena de firmas observable en producción) todavía pendientes.

### §3.4 B6 completo sigue pendiente

La firma B6-E2 PASS reduce parcialmente la deuda de evidencia del gate B6 pero no lo cierra. Las evidencias B6-E3 (clave pública versionada) y B6-E6 (cadena de firmas en producción) permanecen `RUNTIME_EVIDENCE_PENDING`. El estado global del gate B6 sigue siendo `DESIGN_DECISIONS_SIGNED_RUNTIME_EVIDENCE_PENDING` hasta que las tres evidencias restantes se firmen.

---

## §4 Confirmación de restricciones aplicadas

Bajo esta firma, Manus E2 confirma verbatim las siguientes negaciones, cada una correspondiente a una restricción declarada por T1 en el prompt de receipt.

| Restricción | Estado tras firma |
|-------------|-------------------|
| No clave criptográfica generada en este acto | Confirmado |
| No clave pública (`.pub`) publicada en este acto | Confirmado |
| No `main` modificado | Confirmado |
| No runtime ejecutado por Manus E2 | Confirmado |
| No Fase 1 activada | Confirmado |
| No Dory declarado muerto | Confirmado |
| No R1 tocado | Confirmado |
| No PR abierto | Confirmado |
| No canonización runtime adicional fuera de B6-E2 | Confirmado |

El estado del repo `main` permanece intacto. La firma magna T1 cubre exclusivamente B6-E2 sobre la rama lateral `control-tower/2026-05-20-b6-e2-custody-declaration` y no autoriza generación de material clave, publicación de clave pública, merge a main, ni canonización de evidencias adicionales.

---

## §5 Próximo paso recomendado (DRAFT)

La siguiente evidencia que reduciría más deuda de runtime sobre B6 es **B6-E3 (clave pública versionada)**, condicional a autorización explícita de T1 para abrir una sesión criptográfica con hardware token. La sesión criptográfica produce simultáneamente el par ed25519 cuyo material privado se almacena bajo el régimen B6-E2 firmado en este receipt y cuya parte pública se publica versionada como artefacto de B6-E3.

La rama lateral sugerida para B6-E3 es `control-tower/2026-05-DD-b6-e3-public-key`, donde DD es la fecha real de la sesión criptográfica autorizada por T1. El productor recomendado es T1 directamente operando hardware token, con Cowork como copista del manifiesto y Manus E2 como redactor del receipt posterior. El auditor recomendado bajo caveat 2026 es Opus 4.7 (Anthropic) sobre el reporte estático que documente formato de la clave pública, compatibilidad con minisign (D-B6-5) y correspondencia con el régimen de custodia firmado en B6-E2.

Manus E2 documenta esta recomendación como DRAFT y no obliga al coordinador a seguirla. T1 puede preferir ejecutar primero la fase física de Shamir 3-de-5 (§2.2 y §3.2) antes de generar el par criptográfico, lo cual también es válido y deja B6-E3 pendiente hasta que el respaldo físico esté completo.

---

## §6 Cross-refs

- `bridge/control_tower/2026-05-20/manus_e2/BATCH_001_SIGNATURE_RECEIPT.md` — receipt de firma magna del lote BATCH_001 que firmó las 5 decisiones D-B6-1..D-B6-5 referenciadas en §2 de este receipt
- `bridge/control_tower/2026-05-20/manus_e2/B6_E1_SIGNATURE_RECEIPT.md` — receipt anterior de B6-E1 PASS que recomendó B6-E2 como Ruta A en §5
- `bridge/control_tower/2026-05-20/manus_e2/B6_EVIDENCE_PACK_INDEX.md` — pack DRAFT B6 firmado en bloque por BATCH_001
- Rama `control-tower/2026-05-20-b6-e2-custody-declaration` @ `a95b1cc` — fuente firmada por este receipt
- `bridge/control_tower/evidence/B6/B6_E2_custody_declaration.md` (en la rama anterior) — declaración de custodia verbatim
- `bridge/control_tower/keys/DORY_CURE_KEY_ROTATION_PROCEDURE.md` (B6-E4 DRAFT) — procedimiento de rotación referenciado en §2.4
- `bridge/control_tower/keys/DORY_CURE_KEY_REVOCATION_PROCEDURE.md` (B6-E5 DRAFT) — procedimiento de revocación referenciado en §2.5

---

**Firma magna T1 registrada sobre B6-E2.** Plano de custodia política firmado. B6-E3 y B6-E6 permanecen PENDIENTES. Generación física del par criptográfico y ejecución material de Shamir 3-de-5 quedan condicionadas a autorización explícita de T1 para sesión criptográfica futura.
