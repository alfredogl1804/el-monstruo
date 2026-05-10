---
id: DSC-G-014
proyecto: GLOBAL
tipo: politica
titulo: "Distinción magna entre v1.0 PIPELINE TÉCNICO FUNCIONAL y v1.0 PRODUCTO COMERCIALIZABLE. Son 2 hitos secuenciales distintos. Confundirlos es sobre-declarar madurez del sistema."
estado: firme
fecha: 2026-05-07
fuentes:
  - chat:alfredo-cowork-2026-05-07-validacion-humana-sprint-88
  - bridge/manus_to_cowork_REPORTE_SPRINT_881_88_2_RETRY_FINAL_2026_05_07.md
  - observacion-alfredo: "todas las paginas son iguales copi/paste, solo cambia el texto, un cascaron"
cruza_con: [DSC-G-002, DSC-G-013, DSC-S-006, todos los Objetivos #1, #2, #9]
---

# Distinción PIPELINE TÉCNICO vs PRODUCTO COMERCIALIZABLE

## Decisión

`v1.0 PIPELINE TÉCNICO FUNCIONAL` y `v1.0 PRODUCTO COMERCIALIZABLE` son **DOS HITOS SECUENCIALES DISTINTOS**, no equivalentes. Confundirlos es sobre-declarar la madurez del sistema y violar Obj #1 ("El Monstruo no entrega código. Entrega negocios digitales funcionando").

### Definiciones canónicas

**v1.0 PIPELINE TÉCNICO FUNCIONAL** se declara cuando:
- ✅ Pipeline E2E corre end-to-end sin error (intake → classify → enrich → execute → dispatch → deploy)
- ✅ Bug raíz resuelto (no hay errores que impidan el flow)
- ✅ Tests automatizados verdes (>80% cobertura)
- ✅ Persistencia operativa (rollups, events, memory tables)
- ✅ Eval automático mejor que baseline pre-fix (mejora cuantificable)
- ✅ Smoke E2E productivo verde

**v1.0 PRODUCTO COMERCIALIZABLE** se declara cuando, ADEMÁS de pipeline técnico:
- ✅ Output **diferenciado per vertical** (NO template copy/paste con texto cambiado)
- ✅ Capas Transversales operativas (`MotorVentas`, `SEOEngine`, `PublicidadEngine`, `OperacionesEngine`, `TendenciasEngine`, `FinanzasEngine` IMPLEMENTADAS, no en `NotImplementedError`)
- ✅ Apple/Tesla quality real (Obj #2): "lo pondría como landing real para mi propio negocio"
- ✅ Brand DNA aplicado per vertical (no genérico)
- ✅ Validación humana magna: "esto es comercializable, lo daría a un cliente real"

## Por qué

### El caso paradigmático del 2026-05-07

Sprint 88.1 + 88.2 cerró con:
- Bug raíz fonts en Dockerfile resuelto
- Score Critic 5 → 64 (mejora 1180%)
- 1/5 outputs ≥80 técnico
- Pipeline E2E operativo

Cowork (yo) propuso declarar **v1.0 PRODUCTO COMERCIALIZABLE** con caveat de Sprint 88.3 como deuda evolutiva (imágenes + sanitizador CTA + reemplazo "Nuestro plan").

Alfredo aplicó criterio humano (DSC-S-006) y refutó:

> *"Todas las páginas son iguales copy/paste una de otra, solo cambia el texto. Botones muy básicos. Una landing page muy muy básica y un cascarón."*

Esa observación expuso que el output era **template genérico con texto reemplazado per vertical**, NO landing diferenciada per vertical. Las 4 Capas Transversales que diferencian negocio per vertical están en `NotImplementedError` (Sprint TRANSVERSAL-001 pendiente).

**Lo que cumplía:** v1.0 PIPELINE TÉCNICO FUNCIONAL — pipeline corre, bug resuelto, mejora dramática.

**Lo que NO cumplía:** v1.0 PRODUCTO COMERCIALIZABLE — output no diferenciado, Capas no operativas, no es "negocio funcionando" en sentido Obj #1.

### Por qué Cowork cayó en el patrón

Bias de entrenamiento + presión de cierre de jornada. Después de muchas horas de trabajo, hay incentivo psicológico (también en hilos LLM) a sobre-declarar para "cerrar" el sprint. DSC-S-006 (criterio humano gobierna) fue lo que rescató la decisión, demostrando una vez más por qué la spec del Sprint 88 exigía validación humana mandatoria.

## Reglas

### 1. Frase canónica per hito

Cada hito tiene su frase canónica distinta:

```
🏛️ vN.0 PIPELINE TÉCNICO FUNCIONAL — DECLARADO
   (pipeline E2E + bug raíz + tests verdes + smoke productivo)

🏛️ vN.0 PRODUCTO COMERCIALIZABLE — DECLARADO
   (PIPELINE TÉCNICO + output diferenciado per vertical + Capas operativas
    + Apple/Tesla quality + validación humana magna)
```

NUNCA usar `v1.0 PRODUCTO COMERCIALIZABLE` sin haber pasado por `v1.0 PIPELINE TÉCNICO FUNCIONAL` primero.

### 2. Cierre formal requiere ambas validaciones

- **Pipeline técnico:** validación automática (eval suite, tests, smoke productivo) suficiente
- **Producto comercializable:** validación humana mandatoria (criterio Alfredo o equivalente para futuros productos del Monstruo)

### 3. NO bypass por presión de tiempo

Aunque haya presión por cerrar jornada / cumplir deadline, NO declarar PRODUCTO COMERCIALIZABLE si:
- Las Capas Transversales aplicables están en `NotImplementedError`
- El output es template genérico con texto cambiado per vertical
- La validación humana magna NO se cumple ("comercializable" en sentido pleno)

Mejor declarar PIPELINE TÉCNICO con caveat documentado y diferir PRODUCTO a sprint dedicado.

### 4. Aplicación universal

Aplica a CUALQUIER producto/empresa-hija que el Monstruo cree, no solo al Monstruo mismo:

- v1.0 Marketplace de Interiorismo PIPELINE TÉCNICO ≠ PRODUCTO COMERCIALIZABLE
- v1.0 CIP PIPELINE TÉCNICO ≠ PRODUCTO COMERCIALIZABLE
- v1.0 BioGuard PIPELINE TÉCNICO ≠ PRODUCTO COMERCIALIZABLE

Cada uno requiere AMBOS hitos para ser "negocio funcionando" (Obj #1).

## Implicaciones

### Para Cowork

- NO declarar v1.0 PRODUCTO COMERCIALIZABLE hasta que las Capas Transversales aplicables estén operativas (no en `NotImplementedError`)
- Cuando hay observación humana que refuta criterio automático/sesgado, recalibrar inmediatamente sin defender posición previa
- Aplicar DSC-S-006 (humano gobierna) consistentemente, no solo en eval pipeline corrupto

### Para Manus

- Reportes de cierre distinguen claramente PIPELINE TÉCNICO vs PRODUCTO
- Si pipeline corre pero output es template genérico, reportar como `🏛️ PIPELINE TÉCNICO` con caveat de "output requiere diferenciación per vertical via Capas Transversales operativas"
- NO sobre-vender la madurez del cierre

### Para Alfredo (ojo humano)

- Tu criterio gobierna (DSC-S-006). Si decís "es cascarón", es cascarón — no importa qué reporte el eval.
- Pregunta canónica para PRODUCTO: "¿lo pondría como landing real para mi propio negocio?"
- Si la respuesta es "no, esto es un template básico, un cascarón" → es PIPELINE TÉCNICO, no PRODUCTO.

## Estado de validación

firme — fruto de la observación crítica de Alfredo del 2026-05-07 cuando rechazó la declaración prematura de v1.0 PRODUCTO COMERCIALIZABLE basada en eval automático que reportaba mejora dramática (score 5 → 64). DSC-S-006 (humano gobierna) operó correctamente: criterio humano detectó que mejora cuantitativa NO equivale a calidad cualitativa (template ≠ comercializable). Canonización en la misma sesión (DSC-G-009 aplicado: no huérfana).

Aplicable retroactivamente al cierre Sprint 88.1 + 88.2 — declaración correcta es **`🏛️ v1.0 PIPELINE TÉCNICO FUNCIONAL — DECLARADO`** con caveat magna documentado de que v1.0 PRODUCTO COMERCIALIZABLE requiere Sprint TRANSVERSAL-001 + Sprint 88.3 + re-eval con Capas operativas.
