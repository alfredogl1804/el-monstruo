# PACK 12 — Río de la Vida: Auditoría de Cobertura Existente

**Estado:** AUDIT_COMPLETO — sustituye al obsoleto `PACK_12_LEGADO_FAMILIAR_EXISTING_AUDIT.md`
**Iteración:** 001 v2 (post-corrección consolidada 2026-05-17)
**Generado:** 2026-05-17
**Vinculado a:** `interfaces_context_fabric/maps/EXISTING_DESIGN_COVERAGE_MATRIX.md`, `raw_rescues/alfredo_pre_ia_checkpoint_2020_2021_DRAFT.md`, `reports/d1_rio_vida_audit.md`

---

## 0. Por qué este pack reemplaza al anterior

En la iteración 001 v1, ChatGPT 5.5 Pro propuso nombres provisionales (**"Cronista Familiar"**, **"Herencia Narrativa"**, **"Legacy Capture"**) para una capa hipotética del Monstruo. Manus produjo un PACK_12 anterior tratándolas como propuestas genuinamente nuevas. Era correcto desde la evidencia disponible en ese momento, pero **incompleto**: faltaba auditar el módulo `Cronos` con la profundidad que merecía.

La corrección del 2026-05-17 aclara:

> *"Alfredo recordó que Cowork le puso nombre a la capa de legado / historia familiar: 'Río de la Vida'."*

El audit D1 forense confirma que la frase exacta "Río de la Vida" **no existe** en el repo (cero archivos), pero **sí existen las raíces canonizadas equivalentes**:

- **APP_VISION cap. 5** define Cronos como *"el río navegable de tu vida"* — la metáfora del río está canonizada desde antes que ChatGPT propusiera los aliases.
- **Cowork audit 2026-05-11 línea 194** dice: *"Cronos | No existe | River of life + 9 capas + Embrión Convergencia | Sin implementar; Smart Notebook tampoco."*
- **3 sprints firmados por Cowork**: CRONOS_1, CRONOS_2, CRONOS_3 — chasis del río + 9 capas + niebla del futuro.
- **Modo Cripta** firmado en APP_VISION para v1.1+: Cronos legable a herederos vía Shamir Secret Sharing.

Conclusión vinculante: las propuestas de ChatGPT son **aliases provisionales** del módulo **Cronos = río de vida = River of Life**. NO son capa nueva. Existen 3 puntos de absorción canonizados.

---

## 1. Las 11 preguntas obligatorias

### 1.1. ¿Qué era exactamente "Río de la Vida" según Cowork?

El nombre exacto que usa Cowork en su audit firmado del 2026-05-11 es **"River of life"** (en inglés, dentro de una tabla de gap matrix sobre el módulo Cronos):

> *"Cronos | No existe | River of life + 9 capas + Embrión Convergencia | Sin implementar; Smart Notebook tampoco"*

La frase "Río de la Vida" (con artículo "la") **no aparece en ningún archivo del repo**. El nombre canónico equivalente que sí está canonizado en APP_VISION cap. 5 es **"el río de Cronos"**, **"el río navegable de tu vida"**, y **"río de vida"**. La afirmación de Alfredo *"Cowork lo llamó Río de la Vida"* tiene drift menor de memoria T1: el nombre canónico que firmó Cowork es "River of life" / "río de Cronos" / "río de vida" — pero el referente es idéntico.

**Definición canónica desde APP_VISION cap. 5:**

> *"Cronos es el río navegable de tu vida. La metáfora central: tu vida es el río, fluye sola, el usuario es el navegante. Vos podés moverte por el río en cualquier dirección — aguas arriba (pasado), aguas abajo (futuro proyectado). Pellizcás para zoom-out (años) o zoom-in (días, momentos). En cada punto, transparencia: ves lo que pasó, las personas, los lugares, las decisiones, los climas emocionales."*

> *"Cronos no es journaling pop. Es apuesta civilizacional: en 30 años, no documentar tu vida va a ser tan obvio como hoy es no usar cinturón de seguridad."*

### 1.2. ¿Está en sprints CRONOS_1 / CRONOS_2 / CRONOS_3?

Sí, los 3 sprints existen como propuestas firmadas por Cowork en `memory/cowork/audits/VISION_APP_MONSTRUO_CLASE_MUNDIAL_2026_05_11.md` líneas 264-268:

| Sprint | Scope verbatim Cowork | Estado |
|---|---|---|
| **CRONOS_1** | "chasis del río + captura passive WhatsApp + Photos + ambient bajo SMP" | `SPRINT_ESCRITO`, no firmado por Alfredo, sin código |
| **CRONOS_2** | "9 capas básicas + modo espejo + Smart Notebook" | `SPRINT_ESCRITO`, no firmado, sin código |
| **CRONOS_3** | "niebla del futuro + Embrión Convergencia inter-capa + ofrendas voluntarias" | `SPRINT_ESCRITO`, no firmado, sin código |

Los 3 sprints son secuenciales: 1 establece el chasis técnico (captura ambient + WhatsApp + Photos bajo SMP), 2 implementa la estructura de 9 capas semánticas + interacción de espejo, 3 cierra con la dimensión predictiva (niebla del futuro) + convergencias cross-layer + sistema de ofrendas voluntarias.

### 1.3. ¿Qué relación tiene con Memento?

Memento (`EXISTE_PLENO`, 107 archivos, sprint COWORK_MEMENTO_001 declarado verde) es el **sistema de memoria operativa** del agente — captura eventos, decisiones técnicas, audits, validaciones, error tracking. Cronos = río de vida es el **sistema de memoria personal-vivencial** del usuario humano — captura lo que viviste, las personas, los lugares, los climas emocionales.

Comparten infraestructura (SMP, Supabase, embeddings) pero son **dimensiones distintas del mismo agente**. Memento responde "¿qué decidió el Monstruo?", Cronos responde "¿qué viviste vos?". El audit Cowork no los confunde: línea 142 lista **Memento** y **Cronos** como superficies separadas del Cockpit.

Existe una conexión técnica: el **Embrión Convergencia Cronos** (canonizado en APP_VISION + audit Cowork línea 142) puede consumir datos de Memento para detectar convergencias agente↔usuario.

### 1.4. ¿Qué relación tiene con Fototeca / fotos / videos?

`Fototeca` como módulo nominado **no existe** en el repo (cero hits sustantivos según audit D1). Pero sí existe la **capability** que cubre fotos:

- **Cap 4 capabilities transversales**: línea 75 del audit Cowork lista 13 servicios incluyendo `photo_intelligence_service.dart` (estado: `0/13` implementadas).
- **CRONOS_1** captura "Photos" como fuente passive bajo SMP — es decir, Cronos consume el camera roll del usuario para generar el río.
- **APP_VISION cap. 5** menciona "los lugares, las personas" como dimensiones del río — implícitamente fotogeolocalizadas + reconocimiento facial.

Conclusión: `Fototeca` no es un módulo separado. Es **una fuente de captura passive de Cronos** + un servicio dentro de las 13 capabilities del Cap 4. El nombre "Fototeca" como interfaz visible nunca fue canonizado por Alfredo o Cowork — es un alias coloquial.

### 1.5. ¿Qué relación tiene con legado familiar?

El legado familiar está **canonizado dentro de Cronos** como **Modo Cripta** (APP_VISION cap. 5 firmado para v1.1+):

> *"Cuando alguien que usó el Monstruo durante años fallece, su Cronos puede ser legado a sus seres queridos — soberano, encriptado, cerrado a edición pero navegable. Implementación técnica vía Shamir's Secret Sharing pre-distribuido a herederos elegidos."*

El Modo Cripta tiene 2 sub-modos:

- **Preservación** (firmado v1.1): acceso estructurado a transcripciones reales, decisiones reales, reacciones reales del difunto. *"Como una colección de cartas pero infinitamente más rica."*
- **Simulación** (DIFERIDO v1.2+ con peso ético propio, NO firmado): AI extrapola en estilo del difunto.

Cita de Alfredo en APP_VISION verbatim: *"parece no ético pero es lo más cercano a seguir teniendo con vida a un ser vivo."*

El "regalo futuro para Tata cuando él no esté" mencionado en el checkpoint pre-IA es **exactamente esto**: el Modo Cripta de Cronos. Lo que Alfredo intentó manualmente con Day One en el pasado, el Monstruo lo cubre estructuralmente en Cronos + SMP + Shamir + AUTH_TIERS_001.

### 1.6. ¿Qué relación tiene con Daily / Cockpit?

Cronos aparece en ambos modos pero con peso diferente:

- **Daily (5 superficies)**: APP_VISION línea 138 lista *"Home (input universal + río de Cronos), Threads, Pendientes, Conexiones, Perfil"*. El río de Cronos vive como **franja horizontal navegable bajo el input** del Home (línea 230). Presencia silenciosa de la vida documentada, accesible con un swipe lateral pero no obligatoria.
- **Cockpit (12-15 superficies)**: incluye Cronos como superficie densa con todas sus capas, modos, convergencias y replay (Embrión Convergencia Cronos línea 282).

El usuario en modo Daily ve Cronos como río ambient en el Home; en Cockpit lo manipula como sistema completo.

### 1.7. ¿Qué está diseñado?

| Pieza | Origen | Estado |
|---|---|---|
| Río navegable + zoom temporal | APP_VISION cap. 5 | `CANON_VIGENTE` firmado |
| 9 capas básicas (Salud, Económica, Relaciones, Profesional, Creativa, Filosófica, Aprendizajes, Decisiones, Emocional) | APP_VISION cap. 5 | `CANON_VIGENTE` firmado |
| Convergencias inter-capa (6 ejemplos verbatim) | APP_VISION cap. 5 | `CANON_VIGENTE` firmado |
| Embrión Convergencia Cronos | APP_VISION + audit Cowork línea 142 | `CANON_VIGENTE` |
| Modo Espejo (default) | APP_VISION cap. 5 | `CANON_VIGENTE` |
| Modo Testigo silente (toggle) | APP_VISION cap. 5 | `CANON_VIGENTE` |
| Modo Cripta — Preservación | APP_VISION cap. 5 | `CANON_VIGENTE` para v1.1+ |
| Modo Cripta — Simulación | APP_VISION cap. 5 | `DIFERIDO_v1.2+` con peso ético explícito |
| Captura de voz interna ("escuchame") | APP_VISION cap. 5 | `CANON_VIGENTE` |
| Anti-gaslighting / fuente de verdad inviolable | APP_VISION cap. 5 | `CANON_VIGENTE` |
| Cronos como input al Modo Confidente | APP_VISION cap. 5 línea 525 | `CANON_VIGENTE` |
| Niebla del Futuro | APP_VISION + audit Cowork | `CANON_VIGENTE` (parte de CRONOS_3) |
| Smart Notebook | APP_VISION + Cowork | `CANON_VIGENTE` (parte de CRONOS_2) |
| Spatial Cronos (Vision Pro) | APP_VISION línea 78 | `CANON_VIGENTE` para v1.2+ |

### 1.8. ¿Qué está implementado?

**Cero**, según Cowork audit línea 194: *"Cronos | No existe | ... | Sin implementar; Smart Notebook tampoco."*

Confirmado por inspección:
- `apps/mobile/lib/core/services/cronos_service.dart` — referencia en línea 75 del audit como **0/13 capabilities transversales** implementadas. El archivo existe como stub vacío o no existe.
- `smart_notebook_service.dart` — mismo estado.
- `kernel/embriones/embrion_estratega.py` existe, pero `embrion_convergencia_cronos.py` no.

Cronos hoy es **doctrina pura sin código**.

### 1.9. ¿Qué está solo propuesto?

Los 3 sprints CRONOS_1/2/3 + el Embrión Convergencia + el sistema de ofrendas voluntarias + el modo espejo + niebla del futuro + integración WhatsApp/Photos/Ambient. Todo está propuesto en el audit Cowork del 2026-05-11 pero **ninguno firmado por Alfredo**.

### 1.10. ¿Qué parte falta?

| Gap | Bloqueante de | Quién lo decide |
|---|---|---|
| Firma de Alfredo en CRONOS_1 / 2 / 3 | Implementación | Alfredo |
| SMP (Sprint Mobile 0) — pre-requisito | CRONOS_1 entero (captura passive bajo SMP) | Alfredo |
| AUTH_TIERS_001 — pre-requisito de Modo Cripta | Modo Cripta | Alfredo |
| Decisión sobre Spatial Cronos (Vision Pro v1.2+) | Roadmap largo | Alfredo |
| Shamir Secret Sharing implementado | Modo Cripta Preservación | sprint dedicado, no escrito |
| Decisión sobre Modo Cripta Simulación (v1.2+) | Roadmap largo | Alfredo + peso ético |

### 1.11. ¿Qué NO debe rediseñar ChatGPT hasta leer este pack?

ChatGPT NO debe:

1. **Inventar nombres nuevos** para algo que ya tiene nombre canonizado (Cronos = río de vida = River of Life). Las propuestas Cronista Familiar / Herencia Narrativa / Legacy Capture son aliases provisionales que deben **descartarse** como nombres definitivos.
2. **Diseñar capa paralela** a Cronos para legado familiar — el Modo Cripta ya lo cubre.
3. **Proponer Fototeca como módulo separado** — es fuente passive de Cronos + servicio Cap 4.
4. **Proponer Day One como módulo nuevo** — el "regalo futuro para hijos" es Modo Cripta Preservación.
5. **Confundir Memento con Cronos** — son dimensiones distintas del Monstruo (operativa del agente vs vivencial del usuario).
6. **Saltarse la firma de Alfredo** sobre los CRONOS_1/2/3 — los sprints existen, falta solo la decisión humana.
7. **Diseñar Modo Cripta Simulación** sin tratar el peso ético explícitamente — APP_VISION lo difiere a v1.2+ con precondiciones específicas.

---

## 2. Estado canonizado actualizado

| Concepto | Nombre canónico | Estado | Aliases provisionales descartados |
|---|---|---|---|
| Río de vida | **Cronos** (módulo) / **río de Cronos** (objeto) / **River of Life** (eng) | `CANON_VIGENTE` | "Río de la Vida" (Alfredo memoria T1), "Cronista Familiar" (ChatGPT), "Herencia Narrativa" (ChatGPT), "Legacy Capture" (ChatGPT), "Day One replacement" (Manus) |
| Legado a herederos | **Modo Cripta** (sub-modo de Cronos) | `CANON_VIGENTE v1.1+` | "Legado familiar capa", "Memento familiar" |
| Captura passive | **CRONOS_1** + Cap 4 capabilities | `SPRINT_ESCRITO` | "Fototeca", "Photo capability separada" |
| Niebla del futuro | **CRONOS_3** | `SPRINT_ESCRITO` | — (canónico) |
| 9 capas | **Cronos 9 capas** | `CANON_VIGENTE` (CRONOS_2 implementa) | — |
| Convergencias | **Embrión Convergencia Cronos** | `CANON_VIGENTE` | — |

---

## 3. Decisión recomendada para iter 002

**No canonizar capa nueva. Cronos cubre el espacio entero.** La acción operativa es:

1. Pedir a Alfredo firma de los 3 sprints CRONOS_1 / CRONOS_2 / CRONOS_3.
2. Pedir firma del pre-requisito SMP (Sprint Mobile 0).
3. Pedir firma de AUTH_TIERS_001 (pre-requisito de Modo Cripta).
4. Diferir Modo Cripta Simulación a debate ético separado (v1.2+).
5. ChatGPT 5.5 Pro debe consumir este pack + EXISTING_DESIGN_COVERAGE_MATRIX.md antes de iter 002 y NO proponer capas nuevas en este dominio.

---

## 4. Trazabilidad

- **Audit:** `interfaces_context_fabric/scripts/d1_rio_vida_audit.sh` (44 keywords, 19 scopes, 15.3s)
- **Output bruto:** `interfaces_context_fabric/reports/d1_rio_vida_audit.md` (800+ líneas)
- **Canon de Cronos:** `docs/EL_MONSTRUO_APP_VISION_v1.md` capítulo 5 (líneas 403-540)
- **Audit Cowork:** `memory/cowork/audits/VISION_APP_MONSTRUO_CLASE_MUNDIAL_2026_05_11.md` líneas 75, 138, 142, 154, 194, 264-268, 282, 326, 375
- **Sprints CRONOS_1/2/3:** Eje 6 del audit Cowork
- **Modo Cripta:** APP_VISION cap. 5 sub-sección "Modo Cripta — preservación firme + simulación diferida"
- **Cita verbatim de Alfredo:** *"parece no ético pero es lo más cercano a seguir teniendo con vida a un ser vivo."* (APP_VISION cap. 5)
