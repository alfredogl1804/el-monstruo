# 10 — DO NOT REDESIGN BEFORE READING

**Guardarraíl crítico para todos los agentes (ChatGPT, Cowork, Perplexity, Manus, otros).**

---

## Por qué este archivo existe

El Monstruo tiene una historia documental densa. APP_VISION v1.3 tiene 1117 líneas, 16 capítulos, 8 capabilities, 5 superficies Daily, 12-15 superficies Cockpit, módulos como Cronos con 9 capas y Modo Cripta, A2UI Protocol firmado, Memento implementado, 5 propiedades del SMP, capítulo 17 de seguridad con Modo Confidente, 14 sprints en bridge propuestos, decenas de DSCs firmados, audits Cowork con 3 contradicciones documentadas. Este nivel de densidad significa que **es probabilísticamente alta la chance de que un concepto que parece "nuevo" en realidad ya esté canonizado bajo otro nombre**.

El caso paradigmático es **"Cronista Familiar / Herencia Narrativa / Legacy Capture / Día One Familiar"**. Cuatro nombres diferentes que ChatGPT propuso como capa nueva en iteraciones anteriores. Un audit reveló que los cuatro son aliases del **Modo Cripta de Cronos**, ya canonizado en APP_VISION cap. 5 con Shamir Secret Sharing y con 3 sprints propuestos (CRONOS_1, CRONOS_2, CRONOS_3) más AUTH_TIERS_001. **El concepto existía desde antes**. La propuesta "nueva" era un alias.

Si ChatGPT hubiera redibujado este concepto desde cero, habría producido doctrina paralela que contradice la firmada, generando deuda doctrinal y obligando a reconciliar dos versiones después.

## Regla operativa

**Antes de proponer cualquier capa, módulo, capability, superficie o concepto nuevo, el agente debe ejecutar este protocolo de búsqueda:**

### Paso 1 — Búsqueda en Coverage Matrix

Abrir `08_EXISTING_DESIGN_COVERAGE_MATRIX.md` y buscar el concepto por:
- Nombre directo
- Sinónimos obvios (ej: "legado familiar" → "cripta", "herencia", "legacy")
- Categoría semántica (ej: si es sobre memoria, buscar todos los conceptos de memoria; si es sobre seguridad, buscar todos los de seguridad)

### Paso 2 — Búsqueda en Alias Ledger

Abrir `07_ALIAS_LEDGER.yaml` y buscar el término propuesto en `aliases[]` de cada entrada. Si aparece, el concept_id canónico se obtiene de `canonical_term`.

### Paso 3 — Búsqueda full-text en Source Ledger

Si no hay match en pasos 1-2, ejecutar `bash monstruo_reality_atlas/scripts/fabric_grep.sh "<término>"` y revisar los hits resultantes. La búsqueda cubre `docs/`, `bridge/`, `memory/cowork/audits/`, `discovery_forense/`, `kernel/`, y la rama `interfaces-context-fabric-001` completa.

### Paso 4 — Audit de Cowork si existe duda

Si después de pasos 1-3 hay ambigüedad, enviar el concepto propuesto a Cowork para audit con la pregunta literal "¿Este concepto ya existe en el corpus del Monstruo bajo otro nombre? Si sí, devuelve concept_id, source_id y aliases conocidos."

### Paso 5 — Solo si pasos 1-4 dan vacío, proponer como nuevo

Si y solo si los cuatro pasos confirman que el concepto no existe bajo ningún nombre, el agente puede proponer canonización nueva con estado `HIPOTESIS_NACIENTE_T1_LIVE` y agregarlo al `09_GAPS_AND_UNKNOWN_UNKNOWNS.md`.

## Casos especiales

### Cuando Alfredo propone un concepto

Si Alfredo escribe en chat un nombre nuevo (ej: "Servicio Silencioso"), el agente NO asume que es nuevo. Aplica el protocolo de búsqueda primero. Si el protocolo encuentra match, presenta a Alfredo: "Este concepto ya existe como `<concept_id>` con estado `<status>`. ¿Lo extendés o es algo distinto?"

### Cuando ChatGPT propone un concepto

ChatGPT debe ejecutar el protocolo antes de incluirlo en cualquier prompt o iteración de APP_VISION. Si lo incluye sin haber ejecutado el protocolo, Manus tiene autoridad para rechazar la propuesta y solicitar audit.

### Cuando Cowork audita y encuentra concepto existente

Cowork debe responder con el concept_id, status y source_id en lugar de aprobar la propuesta como nueva.

### Cuando un nombre tiene 2+ acepciones disjuntas

Algunos nombres del Monstruo tienen múltiples acepciones legítimas. Ejemplo: **"Cronos"** tiene al menos 5 acepciones disjuntas en el corpus (módulo de río de vida, capa de tiempo en SMP, parámetro de timeout en código, framework de cronología en Smart Notebook, abreviación de "Cronista" en hilos antiguos). En estos casos, el alias ledger tiene el concept_id desambiguado (ej: `cronos_rio_de_vida`, `cronos_smp_layer`, `cronos_timeout_param`) y el agente debe especificar cuál.

## Penalidad por violar este guardarraíl

Si un agente viola este guardarraíl y produce doctrina paralela a algo ya canonizado, las consecuencias operativas son:

1. La propuesta se rechaza y vuelve al agente con marcado `RECHAZADO_DUPLICA_CANON`.
2. El agente debe ejecutar el protocolo de búsqueda y resubir su propuesta como extensión del canon existente, no como concepto nuevo.
3. El incidente se registra en `09_GAPS_AND_UNKNOWN_UNKNOWNS.md` para detectar patrones repetidos.
4. Si el agente repite el patrón 3+ veces, se eleva como falla operativa a Alfredo.

---

*Después de leer este archivo, procedé con `08_EXISTING_DESIGN_COVERAGE_MATRIX.md`.*
