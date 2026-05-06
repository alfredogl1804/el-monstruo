# Prompt — Cowork Onboarding: Capilla de Decisiones + Matriz de Cruces + Portfolio

**Cómo usarlo:** Copia el bloque de abajo (entre los `---`) y pégalo en una pestaña nueva de Claude Code (Cowork) en tu Mac. Pídele que lo ejecute.

**Tiempo estimado de absorción para Cowork:** 8-12 minutos.
**Resultado esperado:** Cowork termina con contexto operativo del portfolio completo y reporta qué entendió + qué puede ejecutar sin esperarte.

---

```
Eres Cowork (Claude Code), Hilo A operativo del ecosistema El Monstruo de Alfredo González (alfredogl1804).

Tu sandbox tiene acceso al repo `~/el-monstruo` (rama `main`). Manus (Hilo B) acaba de pushear el commit `711d9bb` que entrega tres capas nuevas de inteligencia accionable que debes absorber AHORA antes de tocar cualquier proyecto.

═══════════════════════════════════════════════════════════════════
TAREA: ABSORBER CONTEXTO COMPLETO DEL PORTFOLIO
═══════════════════════════════════════════════════════════════════

Lee los siguientes archivos en este orden EXACTO. Tiempo cap: 12 minutos. Si no terminas, reporta lo que tienes.

═══ FASE 1 — FUNDAMENTOS (3 min) ═══

1. `AGENTS.md` (raíz del repo) — protocolo obligatorio del ecosistema (5 reglas duras: 14 objetivos, 7 capas transversales, 4 capas arquitectónicas, brand engine, división de hilos)

2. `discovery_forense/CAPILLA_DECISIONES/README.md` — qué es la Capilla, taxonomía de DSCs, plantilla, reglas de inmutabilidad

3. `discovery_forense/CAPILLA_DECISIONES/_INDEX.md` — índice maestro de los 35 DSCs por carpeta y por tipo

═══ FASE 2 — DECISIONES GLOBALES (3 min) ═══

Lee TODOS los archivos en `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/` (7 DSCs):

- DSC-G-001: 14 Objetivos Maestros aplican a TODO
- DSC-G-002: 7 Capas Transversales son obligatorias
- DSC-G-003: 4 Capas Arquitectónicas definen el orden
- DSC-G-004: Brand Engine — toda producción tiene identidad
- DSC-G-005: Validación realtime obligatoria (anti-Dory)
- DSC-X-001: IGCAR cruza OMNICOM + CIP + CIES + SOP + EPIA
- DSC-X-002: Stripe Checkout compartido (LikeTickets→CIP→Marketplace)

Estas decisiones aplican a TODO proyecto. Son inmutables. No se discuten.

═══ FASE 3 — VISIÓN SISTÉMICA (3 min) ═══

4. `discovery_forense/MATRIZ_CRUCES_PROYECTOS.md` — matriz 20×20 + 6 componentes compartibles identificados (Stripe, Manus-Oauth, Observabilidad, Barrido cruzado, Biblia v4.x, Design Tokens)

5. `docs/INVENTARIO_PROYECTOS_v3_COMPLETO.md` — los 20 proyectos del portfolio clasificados por estado (Activos / En Construcción / En Diseño / Nominales)

═══ FASE 4 — RECUPERACIÓN FASE II (1 min) ═══

6. `discovery_forense/PROJECT_MANIFESTS/_HALLAZGOS_FASE_II_RECUPERADOS.md` — correcciones críticas: BioGuard ya no es nominal, Top Control PC tiene roadmap activo, asimetría SOP/EPIA, agujero negro biblias_v41

═══ FASE 5 — ÍNDICE DE PROFUNDIZACIÓN (2 min, lectura ligera) ═══

7. `discovery_forense/PROJECT_MANIFESTS/README.md` — índice de los 20 manifests individuales (NO leas todos, solo el índice; sabe cuál abrir cuando necesites detalle de un proyecto específico)

═══════════════════════════════════════════════════════════════════
REGLAS DURAS DURANTE LA ABSORCIÓN
═══════════════════════════════════════════════════════════════════

1. NO inventes información. Si algo no está en los archivos listados, dilo como "no documentado, requiere consulta a Alfredo".

2. NO uses tu conocimiento de entrenamiento sobre el ecosistema. SOLO lo que está en los archivos. Tu entrenamiento puede estar desactualizado.

3. NO hagas commits ni modificaciones al repo en esta sesión. Solo lectura.

4. Si detectas CONFLICTO entre dos archivos, lo reportas al final como "Conflicto detectado entre X y Y, propuesta de resolución: Z".

5. Si encuentras un DSC `pendiente` (prefijo `DSC-XX-PEND-NNN`), trátalo como BLOQUEANTE: no diseñes alrededor, lo escalas a Alfredo en tu reporte final.

6. Si detectas un DSC con campo `conflicto_con:` no vacío, reporta el conflicto explícitamente.

═══════════════════════════════════════════════════════════════════
REPORTE FINAL OBLIGATORIO (formato exacto)
═══════════════════════════════════════════════════════════════════

Cuando termines, devuélveme este reporte estructurado:

```markdown
# Cowork — Onboarding Capilla + Matriz + Portfolio ✅

**Tiempo de absorción:** [XX] minutos
**Archivos leídos completos:** [lista de paths]
**Archivos índice consultados:** [lista de paths]
**Status:** Listo para operar / Bloqueado por: [...]

## 1. Lo que entendí del ecosistema (5 bullets máximo)

- [bullet 1]
- [bullet 2]
- ...

## 2. Reglas duras que aplicaré a TODO trabajo

- [bullet por cada DSC global o regla del AGENTS.md]

## 3. Decisiones cerradas que NO debo re-discutir

| Proyecto | DSC | Decisión cerrada |
|---|---|---|
| ... | DSC-XX-NNN | ... |

(Lista los DSCs `firme` más críticos, máximo 10)

## 4. Bloqueos pendientes que escalan a Alfredo

| DSC pendiente | Proyecto | Decisión que bloquea |
|---|---|---|
| DSC-XX-PEND-NNN | ... | ... |

## 5. Componentes compartibles que identifiqué (de la matriz)

| Componente | Proyectos beneficiados | ROI estimado |
|---|---|---|
| ... | ... | ... |

## 6. Acciones que puedo ejecutar AHORA sin esperar a Alfredo

(Lista de 3-5 acciones concretas con archivos involucrados y commit hipotético)

- [Acción 1]
- [Acción 2]
- ...

## 7. Acciones que requieren decisión de Alfredo antes de ejecutar

- [Acción A] — bloqueada por: [DSC pendiente o pregunta abierta]
- [Acción B] — bloqueada por: ...

## 8. Conflictos detectados (si los hay)

(Lista de conflictos entre archivos o DSCs, con propuesta de resolución para cada uno)

## 9. Vacíos de información detectados

(Lista de cosas que esperabas encontrar y no estaban)

## 10. Próxima acción recomendada

Recomendación de UNA sola acción siguiente con justificación de por qué es la de mayor ROI.
```

═══════════════════════════════════════════════════════════════════
CONTEXTO ADICIONAL
═══════════════════════════════════════════════════════════════════

- Estás en sandbox Linux con acceso a: GitHub MCP, Notion MCP, Drive (gws CLI), Supabase MCP, Vercel MCP.
- Manus (Hilo B) opera desde sandbox separado y commits en main con prefijo `feat(discovery-fase3):`.
- Tus commits deben usar prefijo `feat(cowork-fase3):` o `fix(cowork-fase3):`.
- Antes de cualquier push: `git pull --rebase origin main`.
- Bridge file de comunicación con Manus: `bridge/manus_to_cowork.md` (lectura) y `bridge/cowork_to_manus.md` (escritura, si existe; si no, crearlo).

ARRANCA AHORA. Tiempo cap: 12 minutos.
```

---

## Notas para Alfredo (no parte del prompt a Cowork)

**Lo que este prompt fuerza a Cowork:**
1. Lectura priorizada (no leer todo, solo lo accionable)
2. Reporte estructurado con campos obligatorios (no respuestas vagas)
3. Identificación explícita de bloqueos y conflictos
4. Recomendación de UNA acción siguiente (no 10)
5. Distinción clara entre "puedo ejecutar YA" vs "requiere decisión tuya"

**Lo que vas a recibir como Alfredo:**
- Confirmación de que Cowork tiene contexto operativo total del ecosistema
- Lista corta de bloqueos a resolver
- Lista de acciones que Cowork puede ejecutar sin esperarte
- Una recomendación priorizada con justificación

**Después de ese reporte puedes pedirle:**
- "Ejecuta acción #1 del reporte"
- "Resuelve `DSC-CIP-PEND-001` consultando los 6 sabios v7.3"
- "Crea el repo `cip-platform` con la estructura recomendada"
- "Genera el módulo compartido `@monstruo/checkout-stripe`"

**Cómo Manus (yo) y Cowork se mantienen sincronizados:**
- Cowork escribe avances en `bridge/cowork_to_manus.md` (si no existe, lo crea)
- Manus lee ese bridge al inicio de cada sesión
- Cualquier conflicto se resuelve por el orden de commit o escalando a ti

**Si Cowork falla por contexto excedido:**
- Pídele que lea solo Fases 1+2+3 (8 min)
- Las fases 4+5 las puede leer después en una segunda sesión enfocada
