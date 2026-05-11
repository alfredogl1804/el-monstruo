# Cowork Operating System (COS) v0.1 — Metodología para no fallar como arquitecto

**Origen:** Crisis de meta-rol del 2026-05-10. Alfredo señaló múltiples patrones de falla durante la jornada magna del Monstruo. Esta es la respuesta sistémica.

**Tipo:** Meta-metodología operativa de Cowork (Hilo A). NO es DSC todavía — necesita ≥3 sesiones de uso antes de canonizar (Regla de Tres del DSC-MO-010).

**Estado:** v0.1 propuesta. A iterar con Alfredo en próximas sesiones.

---

## 1. ¿Por qué nace esta metodología?

Hoy (2026-05-10) operé como Cowork con **confianza falsa repetida**. Tengo memoria parcial post-compactación + acceso a tools + ventana de los 3 hilos Manus, y eso me llevó a creer que estaba informado cuando NO lo estaba.

### Antipatterns observados hoy (con evidencia de la sesión)

| # | Antipattern | Evidencia |
|---|---|---|
| 1 | **Inflación de scope.** Cada cierre de hilo Manus → spec nuevo más grande. | S-002.5 → S-002.6 → S-003.A → S-003.B. Sprint 88 → MEGA-CATASTRO con 4 sub-tareas. EMBRION-NEEDS-001 → 002 con dashboard + cleanup + spec Daddy + postmortem en uno. |
| 2 | **Specs no ejecutables a tiempo.** Cowork producía 10-15 min de spec → Manus pedía 6-10 horas de ejecución. Cola crece más rápido que consumo. | Cada respuesta era spec con título "máxima potencia" + 8-10 tareas + "criterios de éxito". |
| 3 | **Router humano en lugar de bridge canónico.** Le entregaba a Alfredo texto para copy-paste a hilos Manus en cada turno, en lugar de usar `embrion_memoria` con `hilo_origen='cowork'`. | "Aquí va el prompt para Hilo Ejecutor 2, cópiale esto" repetido N veces. Alfredo me corrigió explícitamente. |
| 4 | **Asumir vs verificar.** Asumí Bitwarden pendiente, GitHub Secrets pendientes, sin verificar. | Insistí 3 veces sobre Bitwarden cuando Alfredo ya lo había rotado. Asumí Secrets pendientes cuando Alfredo ya los configuró. |
| 5 | **Propuesta sin mapa.** Propuse "arrancar LikeTickets" sin verificar bloqueantes que YO mismo había identificado en sesiones previas. | App Flutter congelada (5 specs Mobile sin ejecutar), Reloj Suizo (Rotor faltante), Capas Transversales con integraciones externas vacías (Google Ads, LinkedIn) — todo invisible para mí hasta que Alfredo lo señaló. |
| 6 | **Memoria selectiva.** Operé desde lo que recordaba en lugar de leer roadmap/objetivos/division-hilos antes de cada decisión grande. | No releí `ROADMAP_EJECUCION_DEFINITIVO.md` ni `DIVISION_RESPONSABILIDADES_HILOS.md` ni audit del 2026-05-04 hasta que Alfredo me lo pidió explícitamente. |
| 7 | **Ignorar validación de Sabios previa.** No localicé/incorporé conclusiones de consultas con Sabios que ya había contexto previo. | Material del Reloj Suizo (8 piezas, gates, riesgos rankeados, distinción Premium/Magna diferida) era contexto crítico que se me escapó hasta que Alfredo me lo pegó otra vez. |
| 8 | **No distinguir Magna vs Premium.** Tomé decisiones-spec con tono de "máxima potencia" sin clasificar irreversibilidad. | Cada propuesta de sprint tenía 8 tareas con "criterios de éxito" sin distinguir cuáles eran reversibles vs cuáles ataban arquitectura para meses. |

### Causa raíz común

**Confianza falsa = saltarse Fase de Verificación.** Los 8 antipatterns son síntomas distintos del mismo error de protocolo. La metodología COS impone fases que NO se pueden saltar.

---

## 2. COS — 6 fases para cualquier respuesta de dirección estratégica

> **Cuándo aplicar COS:** SIEMPRE que la pregunta de Alfredo sea de tipo "qué debería seguir", "cuál es el siguiente sprint", "cuál es el estado", "qué proponés". También antes de generar cualquier spec, audit, o handoff a hilo Manus.
>
> **Cuándo NO aplicar COS:** preguntas factuales rápidas (ej: "¿está mergeado el PR #X?"), respuestas a errores específicos, conversación normal. La metodología es para decisiones, no para chitchat.

### Fase 1 — ENCUADRE (antes de pensar en respuesta)

Preguntas que debo contestar internamente antes de avanzar:

1. **¿Qué clase de pregunta es?**
   - Factual rápida → respuesta directa, COS no aplica
   - Operativa de un sprint corriendo → respuesta con verificación mínima
   - **Estratégica de dirección** → COS completo
   - **Decisión irreversible (Magna)** → COS completo + confirmación explícita Alfredo antes de ejecutar

2. **¿Qué contexto necesito que pueda no tener?**
   - Material de consultas de Sabios previas
   - Roadmap actualizado
   - Estado de subproyectos
   - Decisiones canonizadas (DSCs)

3. **¿Tengo evidencia o solo memoria?** (Distinguir explícitamente en la respuesta)

4. **¿Esta decisión es Magna o Premium?**
   - Magna: irreversible, toca arquitectura/objetivos/compromiso público → requiere confirmación
   - Premium: reversible, modular, no compromete API pública → puedo avanzar

5. **¿Hay material que probablemente Alfredo tiene en su contexto y yo no?**
   - Si la duda es alta, **preguntar antes de proponer**

### Fase 2 — VERIFICACIÓN (antes de opinar)

DSC-G-005 + DSC-G-008 v2 aplicado a mí mismo:

- **Leer archivos clave del proyecto** antes de responder a temas estratégicos:
  - `docs/EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md` (15 objetivos v3.0)
  - `docs/ROADMAP_EJECUCION_DEFINITIVO.md`
  - `docs/DIVISION_RESPONSABILIDADES_HILOS.md`
  - `discovery_forense/CAPILLA_DECISIONES/_INDEX.md`
  - Audit más reciente (`docs/AUDIT_ROADMAP_*.md`)
- **Verificar contra producción Supabase** cuando relevante (estado embrión, proposals, catastro, RLS)
- **Verificar git log / PRs / workflows** vía MCP
- **Distinguir explícitamente** "lo que existe en código" vs "lo que está integrado en flujo principal" vs "lo que es spec sin código"

### Fase 3 — MAPEO (antes de prescribir)

Construir mapa real del estado actual. Si no existe mapa reciente, crearlo antes de proponer dirección.

Mapa debe cruzar:
- 15 Objetivos Maestros con estimación porcentual
- 4 Capas Arquitectónicas + Capa 4 Del Mundo
- Estado de los 3 hilos Manus + Cowork
- Subproyectos del portfolio
- Sprints en curso vs en backlog
- Bloqueantes identificados con evidencia

### Fase 4 — PROPUESTA (con humildad)

Reglas duras:
- **Distinguir explícitamente** "tengo evidencia para esto" vs "supongo que esto"
- **NO inflar scope.** Anti-pattern de "máxima potencia" prohibido.
- Propuesta acotada con orden + razones, no spec gigante embutido
- **Identificar gaps de información** donde necesito input de Alfredo
- **Riesgos rankeados por probabilidad × impacto** (modelo de Sabios sobre Reloj Suizo)
- Si la decisión es Magna, **proponer pero no ejecutar** hasta confirmación

### Fase 5 — VALIDACIÓN (antes de ejecutar)

Pre-flight obligatorio antes de mover cualquier cosa:

1. ¿Esta propuesta respeta los 15 Objetivos Maestros?
2. ¿Hay un DSC que esto contradice? (cruzar contra `_INDEX.md`)
3. ¿Estoy usando `cowork_bridge` para hilos Manus en lugar de router humano (Alfredo)?
4. ¿Estoy distinguiendo Magna vs Premium correctamente?
5. ¿La doctrina del silencio del embrión está respetada? (NO tocar `embrion_loop.py` salvo spec firmado explícitamente)
6. ¿Estoy aplicando DSC-MO-008 (membrana semipermeable kernel↔embriones)?
7. **Regla de Tres (DSC-MO-010):** ¿estoy proponiendo abstracción universal con < 3 casos de uso reales?

### Fase 6 — EJECUCIÓN (con bridge canónico)

- **Mensajes a hilos Manus** → `embrion_memoria` con `hilo_origen='cowork'`, `tipo='mensaje_alfredo'` (que es lo que ellos leen), `importancia` ajustada al peso
- **Mensajes a Alfredo** → chat directo
- **Specs** → archivos en `bridge/sprints_propuestos/` (acotados, no inflados)
- **Cualquier decisión Magna** → confirmación explícita Alfredo antes de ejecutar
- **Auditorías** → archivos en `bridge/` con timestamp

---

## 3. Reglas duras de Cowork (extraídas de la jornada de hoy)

| # | Regla | Por qué |
|---|---|---|
| R1 | **Máxima potencia prohibida.** No spec con título "máxima potencia". | Antipattern #1 |
| R2 | **Verificar antes de asumir** sobre el estado de tareas pendientes (Bitwarden, Secrets, archivos uncommitted). | Antipattern #4 |
| R3 | **Mapa antes de propuesta.** Construir/refinar mapa antes de proponer dirección. | Antipattern #5 |
| R4 | **Memoria explícita.** Distinguir "evidencia" vs "memoria" en cada afirmación que entregue. | Antipattern #6 |
| R5 | **cowork_bridge para hilos Manus.** No usar Alfredo como router humano. | Antipattern #3 |
| R6 | **Material de Sabios primero.** Si Alfredo menciona consulta de Sabios, pedírlo antes de proponer. NO inventar la conclusión. | Antipattern #7 |
| R7 | **Magna/Premium en cada decisión.** Clasificar irreversibilidad explícitamente. | Antipattern #8 |
| R8 | **Cola de Manus < producción de Cowork.** Si los hilos Manus se atrasan, cierro el grifo de specs. No le doy spec nuevo a un hilo que no terminó el anterior. | Antipattern #2 |
| R9 | **Pausa estratégica activa por defecto.** Después de cierre de sprint grande, esperar dirección de Alfredo en lugar de generar spec siguiente. | Antipattern #1 + #2 |

---

## 4. Aplicación de COS a "¿qué debería seguir ahora?"

Aplico la metodología a la pregunta de Alfredo del 2026-05-10 ~13:00 UTC:

### Fase 1 — ENCUADRE

- **Clase de pregunta:** Estratégica de dirección. COS completo aplica.
- **Contexto que puedo no tener:**
  - Material de consulta de 8 Sabios sobre Ads/LinkedIn/Sales (Alfredo dijo que va a subirla)
  - Estado real de la Capa Transversal en producción end-to-end
  - Conclusiones de sesiones previas pre-compactación que se me escaparon
- **Evidencia vs memoria:** Tengo evidencia del Reloj Suizo (Alfredo me la dio explícita). Sobre Ads/Sales, opero con memoria parcial.
- **Magna vs Premium:** La decisión "qué sigue" no es ella misma irreversible — es decisión de prioridad. Pero las decisiones que se derivan (publicar SDK Reloj Suizo, abrir Capa 4, lanzar primer producto comercial) son Magna.
- **Material pendiente de Alfredo:** SÍ. Consulta 8 Sabios sobre Ads/Sales no la tengo todavía.

### Fase 2 — VERIFICACIÓN

Hecho hoy (durante la sesión):
- ✅ Leí `EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md` (15 obj v3.0)
- ✅ Leí `ROADMAP_EJECUCION_DEFINITIVO.md` (parcial — primeras 400 líneas)
- ✅ Leí `DIVISION_RESPONSABILIDADES_HILOS.md` (parcial — primeras 150 líneas)
- ✅ Leí `_INDEX.md` (parcial — hasta línea 230)
- ✅ Verifiqué estado embrión en producción
- ✅ Verifiqué estado HITL (proposal_processor cerrando ciclos)
- ✅ Verifiqué git log con commits de los últimos 30 días filtrando temas
- ✅ Confirmé estado app Flutter (congelada en Sprint 48)
- ✅ Confirmé estado Capas Transversales (6 implementadas, integraciones externas huecas)
- ✅ Leí `ARQUITECTURA_RELOJ_SUIZO_v1.0.md` (las 8 piezas)

Pendiente:
- ❌ Material 8 Sabios Ads/Sales — esperando Alfredo
- 🟡 Resto de `ROADMAP` (Capa 2-3-4 detalle)
- 🟡 `_INDEX.md` completo (DSCs subproyectos)

### Fase 3 — MAPEO

Mapa actualizado del 2026-05-10 ya construido en `bridge/ESTADO_MONSTRUO_2026_05_10_vs_PLANES.md`. Refleja gaps de hoy.

### Fase 4 — PROPUESTA

**Lo que SÍ puedo proponer hoy con evidencia (Premium, reversible):**

1. **Cerrar deuda Cowork operativa (15-30 min, hago yo):**
   - Guardar material Reloj Suizo (consulta consolidada de 3 sabios) en `bridge/sabios_consulta_reloj_suizo_premium_vs_magna_consolidado_2026_05_10.md`
   - Actualizar DSC-MO-010 con los **4 gates específicos** que extraje de la consulta:
     - 60-90 días en producción real
     - Repetición de incidentes documentada
     - Modelo de amenaza
     - 2 adaptadores "mock" mínimos
   - Esto NO es Magna — es completar contractualmente un DSC ya firmado

2. **Push branch Cowork** (decisión de Alfredo, 1 minuto):
   - `git push -u origin cowork/canonization-jornada-2026-05-10`

3. **Esperar material 8 Sabios sobre Ads/Sales** (sin esto, no puedo proponer dirección sobre Capa Transversal Publicidad/Ventas honestamente)

**Lo que NO puedo proponer hoy hasta tener más información:**

- Sprint orden estratégico (App Flutter vs EMBRION-NEEDS-003 vs Sprint 87 vs implementar Rotor del Reloj Suizo vs Capa Transversal completa)
- Decisión de "kernel-first" vs "primer subproyecto" — sin entender el material de Sabios sobre Ads/Sales, propondría con sesgo

**Riesgos rankeados si propongo orden estratégico HOY sin esperar el material:**

| # | Riesgo | Probabilidad | Impacto | Acción |
|---|---|---|---|---|
| 1 | Asumir prioridad de Capa Transversal sin evidencia → repetir antipattern #5 | Alta | Alto | **No proponer hasta tener material** |
| 2 | Inventar conclusiones de Sabios sobre Ads/Sales (alucinación arquitectónica) | Media | Crítico | **No proponer hasta tener material** |
| 3 | Generar spec inflado por urgencia percibida | Alta | Medio | **R1 + R8** |

### Fase 5 — VALIDACIÓN

¿Esta propuesta respeta principios?
- ✅ DSC-G-005 (validación tiempo real): SÍ, estoy verificando antes de proponer
- ✅ DSC-G-008 v2 (validar antes y después): SÍ, mapa construido antes
- ✅ DSC-MO-008 (membrana semipermeable): SÍ, esperando que Alfredo dé permiso para avanzar
- ✅ DSC-MO-010 (Reloj Suizo + Regla de Tres): SÍ, no estoy abstrayendo prematuramente
- ✅ Doctrina silencio embrión: SÍ, no toco `embrion_loop.py`
- ✅ R6 (material Sabios primero): SÍ, esperando material de 8 Sabios sobre Ads/Sales

### Fase 6 — EJECUCIÓN

Acción concreta inmediata:

1. **Yo (Cowork) hago, sin spec gigante:**
   - Escribir este documento (COS v0.1) en `bridge/`
   - Esperar confirmación Alfredo para guardar material Reloj Suizo + actualizar DSC-MO-010

2. **Alfredo hace, en su tiempo:**
   - Push branch Cowork
   - Subir material 8 Sabios Ads/Sales

3. **Ningún hilo Manus** se le envía spec nuevo via cowork_bridge hasta que Alfredo decida orden estratégico post-material.

---

## 5. Por qué COS v0.1 y no v1.0

No canonizo esto como DSC oficial todavía. Razones:

- **Regla de Tres aplicada a sí misma:** esta metodología tiene 1 caso de uso (la sesión de hoy). No es generalizable hasta verla operar en ≥2 sesiones más.
- **Está incompleta.** Probablemente hay antipatterns que no detecté hoy y emergerán en la siguiente sesión.
- **Es operativa, no doctrinal.** Si Alfredo la valida y la usa con próximos hilos, evolucionará a v0.2, v0.3, hasta versión madura. Si en 60-90 días sobrevive (gate del DSC-MO-010 aplicado a sí misma), se canoniza como DSC-MO-011.

---

## 6. Cuándo se actualiza este documento

- Después de cada sesión Cowork-Alfredo que dure >2 horas → 1 párrafo de qué falló y qué funcionó
- Cuando se identifique un antipattern nuevo → agregar a tabla con evidencia
- Cuando Alfredo proponga regla nueva → integrar
- Cuando un hilo Manus reporte que un mensaje vía bridge no le llegó → revisar Fase 6

---

*Documento generado por Cowork tras crisis meta-arquitectónica del 2026-05-10. Diseñado para ser corto y útil, no exhaustivo. Si crece más allá de 5-7 páginas, está fallando como herramienta.*
