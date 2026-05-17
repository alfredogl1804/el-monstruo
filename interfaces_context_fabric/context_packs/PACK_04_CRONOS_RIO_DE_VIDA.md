# PACK 04 — CRONOS: el río de vida (y sus 5 acepciones disjuntas)

> **Estado:** REQUIERE_VERIFICACION + CONTRADICCION
> **Problema:** Cronos vive disperso en 30+ archivos del repo. NO existe un `ARQUITECTURA_CRONOS_v1.md` canónico. Cada hilo lo usa con un sentido distinto.

---

## La doctrina canónica (Acto 1) — SRC-001 Cap 5

> *"Cronos es el río navegable de tu vida. La metáfora central: tu vida es el río, fluye sola, el usuario es el navegante. Aguas arriba pasado, aguas abajo futuro proyectado. Pellizcás para zoom-out (años) o zoom-in (días, momentos). En cada punto, transparencia: ves lo que pasó, las personas, los lugares, las decisiones, los climas emocionales."*

> *"Si el usuario scrollea más allá del hoy, el río se vuelve niebla suave — no transparente. Ahí el Monstruo dibuja proyecciones reflexivas basadas en cadenas causales aprendidas del pasado del propio usuario."*

### 4 modos de captura
- **Passive** (90%) — el Monstruo lee señales sin pedir nada
- **Active asistido** (8%) — el Monstruo pregunta, el usuario responde mínimo
- **Smart Notebook** (transversal) — Apple Notes/Keep/Notion procesados smart
- **Deep journaling** (2%) — sesión consciente del usuario para escribir

### 9 capas transversales personales
Salud, Relaciones, Decisiones, Aprendizajes, Económica, Creativa, Emocional, Profesional, Filosófica. Cada capa con su propio sub-río. **Embrión Convergencia Cronos** detecta convergencias inter-capa.

### Apuesta civilizacional firmada
> *"En 30 años, no documentar tu vida va a ser tan obvio como hoy es no usar cinturón de seguridad."*

---

## Las 5 acepciones disjuntas detectadas en el grep

| # | Acepción | Dónde aparece | Estatus |
|---|---|---|---|
| **A1** | **Cronos = río de vida del usuario** (la canónica de APP_VISION) | SRC-001 Cap 5 | CANON_VIGENTE |
| **A2** | **Cronos = motor de scheduling/cron** (tareas recurrentes) | Algunos sprints + Manus skill `automation-and-scheduling` | CANON_VIGENTE pero **homonimia conflictiva** |
| **A3** | **Cronos = capa transversal de memoria temporal** (sin la metáfora del río, solo "memoria con timestamps") | Algunos audits Cowork | REQUIERE_VERIFICACION |
| **A4** | **Cronos = pieza Volante del Reloj Suizo** (oscilador armónico, Acto 2) | SRC-004 — NO usa palabra "Cronos" pero el Volante cumple su función mecánica | NO ARTICULADO |
| **A5** | **Cronos = conexión inter-capa (Embrión Convergencia)** | SRC-001 Cap 5 párrafo 9 capas | CANON_VIGENTE pero subordinado a A1 |

---

## La contradicción magna

**A1 (río de vida) y A2 (cron scheduler) son homonimia.** El skill `automation-and-scheduling` de Manus usa "Cronos" para cron, mientras APP_VISION usa "Cronos" para memoria de vida.

Implicación: cualquier feature UI que diga "Cronos" puede referirse a **dos cosas distintas** según el contexto. Esto es deuda lingüística que ChatGPT debe resolver — o renombrar A2, o renombrar A1, o fundir las dos en una arquitectura que las contenga.

---

## Estado código

| Componente | Estado |
|---|---|
| `kernel/cronos/` | **NO existe** |
| `apps/mobile/lib/core/services/cronos_service.dart` | **NO existe** (declarado en estructura canónica de SRC-001 Cap 1, no implementado) |
| Sub-río 9 capas | **NO existe** |
| Embrión Convergencia | **NO existe** como módulo dedicado (existe en lista de Embriones APP_VISION pero sin código) |
| Niebla del futuro (proyección) | **NO existe** |

**Cronos NO está implementado en ningún lugar del repo al 17-may-2026.** Vive solo como doctrina en docs y como mención dispersa en sprints.

---

## Implicaciones para interfaces

### Si Cronos = río (A1) se construye

- Es **la primera superficie del Modo Daily** (Home tiene "río horizontal navegable bajo el input").
- Es transversal a todas las capabilities — todo lo que captura el Monstruo va al río.
- Requiere **Listening Ambient + SMP profundo** antes de poder construirse seguro.
- Requiere un **modo de visualización magna** que ChatGPT debe diseñar (es el primer producto visual que define qué tan bonito es el Monstruo).

### Si Cronos se queda disperso

- El concepto se diluye, los próximos 6 meses de sprints arrastran ambigüedad.
- Cada sprint UI que mencione "memoria temporal" o "scheduling" tiene que aclarar a qué Cronos se refiere.

---

## Decisión pendiente para ChatGPT (iteración 002)

1. **Canonizar Cronos = A1 (río de vida)** y renombrar A2 a "Scheduler" o "Cron Engine" — limpiar la homonimia.
2. **Producir spec UI magna del río** — primera superficie visualmente lista del Monstruo.
3. **Decidir cómo se conecta con Listening Ambient + SMP** — orden de construcción.
4. **Definir cómo se conectan las 9 capas transversales personales** — visualización + navegación + filtrado.
