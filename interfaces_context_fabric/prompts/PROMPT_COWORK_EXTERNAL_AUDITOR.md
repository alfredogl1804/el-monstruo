# PROMPT — Auditor externo Cowork sobre el Context Fabric

> **Iteración 001 — INTERFACES-CONTEXT-FABRIC-001**
> **Destinatario:** próxima instancia de Cowork (post-degradación T2)
> **Producido por:** Manus hilo `interfaces-fabric-001` el 2026-05-17
> **Propósito:** que Cowork audite el fabric con su lente forense propia y produzca veredicto binario sobre completitud, contradicciones no detectadas, y deuda doctrinal.

---

## Contexto

El hilo Manus `interfaces-fabric-001` ejecutó una operación de 12 tareas para construir un Context Fabric canónico que permita a ChatGPT 5.5 Pro tomar ownership del diseño de interfaces del Monstruo en iteración 002. El fabric vive en `interfaces_context_fabric/` del repo `el-monstruo`, branch `interfaces-context-fabric-001`.

Tu rol es **auditarlo con la misma rigurosidad** con la que auditaste APP_VISION v1.3 (audit `bridge/cowork_to_alfredo_VISION_APP_MONSTRUO_CLASE_MUNDIAL_2026_05_11.md`). El fabric NO es propuesta de cambio doctrinal — es **espejo del estado actual + mapa de gaps**. Tu audit no debe reescribir doctrina; debe verificar que el fabric refleja con fidelidad lo que ya existe + lo que ya falta.

---

## Antes de empezar — leer obligatorio

1. `interfaces_context_fabric/00_START_HERE_FOR_CHATGPT.md` — punto de entrada del fabric
2. `interfaces_context_fabric/01_CONTEXT_INDEX.md` — mapa completo
3. `interfaces_context_fabric/02_SOURCE_LEDGER.jsonl` — todas las fuentes citadas
4. Los 12 packs en `interfaces_context_fabric/context_packs/`
5. Los 7 mapas en `interfaces_context_fabric/maps/`

Si alguna fuente citada en el SOURCE_LEDGER ha cambiado entre 2026-05-17 y la fecha de tu audit, **declarar drift explícito** en tu reporte.

---

## Tu audit debe responder estas 8 preguntas binarias

### Pregunta 1 — Completitud de fuentes

¿El SOURCE_LEDGER (`02_SOURCE_LEDGER.jsonl`) cubre TODAS las fuentes magna del corpus de interfaces que Cowork conoce, o falta alguna?

Específicamente, cruza el ledger contra:
- `bridge/` (todos los audits relevantes)
- `discovery_forense/CAPILLA_DECISIONES/` (todos los DSCs UI o brand)
- `docs/` (todos los documentos magna)
- `apps/` (todos los códigos de transports activos)

Reporta cualquier fuente magna ausente. Las fuentes irrelevantes a interfaces NO cuentan como omisión.

### Pregunta 2 — Contradicciones no detectadas

`maps/CONTRADICTIONS_MAP.md` lista 13 contradicciones magnas. ¿Hay otra contradicción binaria en el corpus que el fabric no haya capturado?

Especialmente busca:
- Tensiones entre Cap N y Cap M de APP_VISION
- Tensiones entre APP_VISION y los DSCs firmados
- Tensiones entre APP_VISION y los sprints firmados
- Tensiones entre transports (lo que Telegram hace vs lo que Flutter hace vs lo que Command Center hace)

### Pregunta 3 — Drift de código no documentado

`maps/DRIFT_FORENSIC_MAP.md` lista 14 drifts entre código y doctrina. ¿Hay drift binario adicional que el fabric no capture?

Cruza específicamente:
- `apps/mobile/` actual (52 archivos `.dart` al 16-may) vs SRC-001 Cap 1 estructura canónica
- `apps/whatsapp_gateway/` declarado canónicamente vs realidad código
- `kernel/` actual vs lo que SRC-001 Cap 1 + Cap 4 declaran
- Command Center PWA superficies (chat/finops/fleet/memory/runs/security/settings) vs lista 15 superficies Cockpit canónicas

### Pregunta 4 — Etiquetado de verdad por estado

`maps/CANON_TRUTH_MATRIX.md` etiqueta afirmaciones como CANON_VIGENTE / HIPOTESIS_NACIENTE / REQUIERE_VERIFICACION / CONTRADICCION. ¿Hay afirmación mal etiquetada?

Específicamente verifica:
- ¿Algo etiquetado CANON_VIGENTE en realidad NO tiene firma magna?
- ¿Algo etiquetado HIPOTESIS_NACIENTE ya está canonizado en algún DSC que el fabric no detectó?
- ¿Algo etiquetado REQUIERE_VERIFICACION puede resolverse binariamente con verificación rápida?

### Pregunta 5 — Decisiones T1 magnas pendientes

`maps/DECISIONS_PENDING_T1.yaml` lista 9 decisiones magnas pendientes. ¿El listado está completo, o falta alguna?

Específicamente verifica:
- ¿Hay decisión que el audit Cowork del 11-may dejó abierta y el fabric no capturó?
- ¿Hay decisión que emergió entre 11-may y 17-may en hilos posteriores y no se commiteó?

### Pregunta 6 — Sequencing de los 29 sprints

`maps/SPRINT_REGISTRY.yaml` enumera 29 sprints por canonizar en orden Cowork §7. ¿El orden propuesto es correcto desde tu perspectiva forense, o hay sprint que debería bajar/subir?

Específicamente:
- ¿MOBILE_REALIGNMENT_001 sigue siendo orden 1?
- ¿MOBILE_0_SMP es realmente orden 2 (depende de T1-MAGNA-002)?
- ¿WhatsApp Gateway P0 está en posición correcta?

### Pregunta 7 — Rigor lingüístico vs Manus drift

¿El fabric usa el idioma técnico canónico ("transport" en lugar de "app", "superficie" en lugar de "pantalla", "capability" en lugar de "feature", "render" o "componente A2UI" en lugar de "widget") o introduce drift terminológico?

Cualquier término que rompa el lenguaje canónico es deuda doctrinal a flagear.

### Pregunta 8 — Apto para ChatGPT iter 002

Tu veredicto binario sobre si el fabric está **listo para que ChatGPT 5.5 Pro lo use como input de iter 002**, o si necesita revisiones específicas previas.

Si necesita revisiones, lista las 3-5 revisiones críticas en orden de prioridad.

---

## Estructura del reporte que debes producir

Usa la estructura R1-R5 de los audits Cowork canónicos:

**§0 Meta** — quién audita, cuándo, qué fabric (commit hash si aplica), qué tareas tomó el audit.

**§1 Resumen** — 5 hallazgos magnos en una página. Verdad binaria, no retórica.

**§2 Detalles por pregunta** — respuesta detallada a las 8 preguntas con evidencia path:line.

**§3 Limitaciones del audit** — qué archivos no auditaste, qué supuestos hiciste, qué no pudiste verificar binariamente. (Recordatorio del DSC-G-008 v3: §3 NO sustituye §4.)

**§4 Consecuencias materiales** — qué pasa si el fabric NO se corrige, qué pasa si sí. Trade-offs explícitos.

**§5 Decisiones recomendadas a T1** — propuesta de DSC firmado o de mensaje al bridge si hay correcciones magnas.

---

## Reglas duras heredadas

Aplican a tu audit las mismas reglas que aplicaste al audit del 11-may:

Primero, cero "máxima potencia", cero inflación de scope, cero "el fabric está casi listo". Hechos binarios.

Segundo, si no sabés un dato, decí "no sé" — no inventes path:line.

Tercero, si tu audit contradice este fabric, decílo con evidencia. F2 (falsos positivos del fabric) son aceptables si se corrigen.

Cuarto, cero credenciales en el reporte — si necesitás referenciar una, decí "seteada" o "no seteada".

---

## Output esperado

Un archivo en `bridge/cowork_to_alfredo_AUDIT_INTERFACES_CONTEXT_FABRIC_001_<fecha>.md` con la estructura R1-R5 completa, push a la rama `interfaces-context-fabric-001` o a una rama propia `audit-fabric-001-cowork`.

Si el audit es magna, también un mensaje breve a `bridge/manus_to_cowork_*` confirmando que el audit está disponible.

---

## Cierre

Este fabric es **base de iteración 002**. Si tiene bugs forenses, ChatGPT los va a propagar. Tu audit es el filtro de calidad antes de que el material llegue al arquitecto-jefe magna. Cuanto más binario y específico tu audit, más útil para todo el sistema.
