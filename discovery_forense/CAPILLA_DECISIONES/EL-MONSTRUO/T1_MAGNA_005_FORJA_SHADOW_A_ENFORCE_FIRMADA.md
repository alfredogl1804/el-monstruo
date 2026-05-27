<!-- aspiracional -->

**Estado:** Aspiracional

> Este archivo es el contrato canónico de firma del T1-MAGNA-005. Su contrato ejecutable derivado vive en `tablero-campana` (PR `design/forja-os-sovereign-agentic-fabric` → `main` con gateway condicional por Power Lane) y será marcado `enforced` en `_dsc_contracts_index.yaml` una vez que ese PR se merge a main y los tests por nivel pasen verdes.

---

# T1-MAGNA-005 — Forja Shadow a Enforce — FIRMADA

**Decisión arquitectónica magna T1 — firmada por Alfredo Góngora — 2026-05-27**

---

## Bloque canónico de firma

```yaml
decision_t1_magna_005:
  forja_modo_ganador: D
  variante: ENFORCE_ESCALONADO_L0_L3
  fecha_firma: 2026-05-27
  firmante: Alfredo Góngora
  modo_firma: respuesta_inline_hilo_manus_b
  justificacion_corta: >
    Aprovechar Power Lanes L0-L6 graduales ya canonizadas en el código,
    mitigar riesgo P0 sin bloqueo total, reversibilidad alta en producción,
    compatible con embrión-down actual, reduce scope DSC-S-018 a solo L4-L6.

  power_lanes_enforce_inicial: [0, 1, 2, 3]
  power_lanes_shadow_hasta_dsc_s_018: [4, 5, 6]
  dependencia_dsc_s_018: solo_para_L4_L6_gated
  dependencia_cowork_co_firma: no
  fecha_revision_30_dias: 2026-06-26
  rollback_si_falla: >
    Si CI detecta envelope L>3 sin DSC-S-018 vigente,
    reverter automático a shadow para esa lane específica.

  validacion_tiempo_real_pre_firma: completada_2026_05_27
  thread_immunity_session_firma: pendiente_registro_post_firma
  articulacion_canonica: T1_MAGNA_005_FORJA_SHADOW_A_ENFORCE_PARA_FIRMA.md
  instrumento_firma: T1_MAGNA_005_RESUMEN_BINARIO_PARA_FIRMAR.md
```

---

## Qué se acaba de firmar (en lenguaje claro)

Forja v4 sale de modo SHADOW para los Power Lanes **L0 (dev), L1 (staging aislado), L2 (staging compartido) y L3 (prod-like reversible)**. En esas cuatro lanes, cuando el Tablero / Embrión / cualquier agente firmado emita un envelope Ed25519 válido, **el gateway de Forja ejecuta sobre el kernel real** y devuelve un receipt Merkle real.

Los Power Lanes **L4 (producción material), L5 (irreversible administrativo) y L6 (administrativo destructivo)** **siguen en modo SHADOW**. En esas tres lanes, el gateway registra el intent firmado y deja constancia, pero **no ejecuta** hasta que DSC-S-018 (key rotation + auth fail-closed) pase de `gated` a `enforced`.

El sistema muestra **transparentemente** qué lanes están enforce y cuáles shadow en cada momento. No hay zona gris. El Trust Indicator del mobile y el panel FORJA-OMEGA-VISUAL reflejan esto en vivo.

---

## Qué desbloquea esta firma HOY

- **T1-MAGNA-006** (PR Drafts autónomos del Embrión) deja de estar bloqueada por T1-MAGNA-005.
- **FORJA-OMEGA-VISUAL Bloque A paso 1** puede arrancar (no más Potemkin parcial).
- **Receipts Merkle reales** empiezan a poblarse en `evidenceReceipts` para L0-L3.
- **Mission Center mobile** (P0.3 del DAN v1.1) se conecta a esos receipts reales.
- **Trust Indicator** del Hilo de Manus puede mostrar 🟢 verdadero para steps L0-L3 que pasaron por Forja.

## Qué queda gated (no se rompe pero no avanza sin DSC-S-018)

- Cualquier ejecución autónoma sobre producción material (L4+).
- Acciones irreversibles del Embrión sin doble factor humano.
- Key rotation automatizado (sigue manual).

---

## Plan de implementación post-firma (Manus B compromiso)

| Paso | Acción | Responsable | Plazo objetivo |
|---|---|---|---|
| 1 | Escribir este archivo de firma canónico + commit a `el-monstruo` main | Manus B | **HOY** |
| 2 | Notificar a Cowork la firma + ajuste de scope DSC-S-018 a solo L4-L6 | Manus B (bridge MD) | HOY |
| 3 | Abrir PR `design/forja-os-sovereign-agentic-fabric` → `main` en `tablero-campana` con gateway condicional por Power Lane (~100 líneas TS adicionales) | Manus B | 48-72h |
| 4 | Tests por nivel (L0 hasta L6) en CI + check "no L4 sin DSC-S-018 vigente" | Manus B | con PR |
| 5 | Cowork audita PR y firma matriz de Power Lanes como tabla oficial | Cowork | 3-5 días |
| 6 | Merge PR → cambiar entry en `_dsc_contracts_index.yaml` a `enforced` con paths reales | Manus B + Cowork | 3-5 días |
| 7 | Primer receipt Merkle real en `evidenceReceipts` para una acción L1 controlada | Manus B (demo) | 5 días máx |
| 8 | Revisión 30 días: ajustar lanes enforce/shadow según evidencia operativa | Alfredo + Manus B + Cowork | 2026-06-26 |

---

## Criterio de rollback explícito

**Disparador automático CI:** si cualquier envelope con `lane ≥ 4` se observa intentando ejecutar sin firma DSC-S-018 vigente en `_dsc_contracts_index.yaml` con status `enforced`, el gateway **revierte esa lane específica a shadow** y emite alerta a Alfredo + Cowork.

**Disparador manual:** Alfredo puede revertir cualquier lane a shadow desde el Tablero con un solo click. La acción queda registrada como envelope firmado por su propia llave T1.

**Disparador de auditoría Cowork:** si Cowork detecta drift entre intents y receipts (>1% mismatch en una ventana de 24h) puede pedir revert de la lane afectada por bridge formal.

---

## Notas finales

Esta firma cierra una decisión arquitectónica magna T1 que estuvo abierta desde 2026-05-26. La articulación canónica original (`T1_MAGNA_005_FORJA_SHADOW_A_ENFORCE_PARA_FIRMA.md`) y el instrumento de firma (`T1_MAGNA_005_RESUMEN_BINARIO_PARA_FIRMAR.md`) siguen en el repo como evidencia trazable del proceso.

La doctrina del Monstruo declarada en SOP/EPIA — *"El Monstruo ejecutando solo"* — queda parcialmente activa desde hoy en L0-L3 y se completará en L4-L6 cuando DSC-S-018 pase a enforce.

**Esta firma es irrevocable como evento histórico** (el commit queda en el git log permanente), pero **operativamente reversible** vía el criterio de rollback arriba. No firma "para siempre"; firma "hasta que la evidencia obligue revisar".

---

**Firmado:** Alfredo Góngora
**Fecha:** 2026-05-27
**Ratificado por:** Hilo Manus B (sesión Cabina dual + DAN v1.1 + Sprint 1 arranque)
**Próximo paso inmediato:** PR a `tablero-campana` branch `design/forja-os-sovereign-agentic-fabric` → `main` con gateway condicional por lane.
