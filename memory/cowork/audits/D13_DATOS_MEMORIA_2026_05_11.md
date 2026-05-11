---
id: D13_DATOS_MEMORIA_2026_05_11
dimension: 13
nombre: Datos y Memoria
fecha: 2026-05-11
arquitecto: Cowork
plan_origen: Plan v1.5 — Programa de Certificación de Pericia P1+P2
nivel_autoridad: 5 (DSC vigente — canónico operativo)
estado_revisado: H0_exploratorio_2026_05_11
nivel_autoridad_revisado: H0 — backlog de pruebas, NO canónico
razon_revision: "Producido en serie de 9 audits sin evidencia Nivel 1 fresca entre ellos. Mapeo 11 capas útil como hipótesis. Porcentaje sin rúbrica. Ver CORRECTIVO_ARQUITECTONICO_2026_05_11.md."
cruza_con:
  - SNAPSHOT_AUDIT_2026_05_11
  - D1_TECNICA_2026_05_11
  - D12_SEGURIDAD_ADVERSARIAL_2026_05_11
  - D18_SRE_RESILIENCIA_2026_05_11
  - MAPA_FUENTES_AUTORIDAD_2026_05_11
  - Objetivo Maestro #15 (Memoria Soberana)
  - Objetivo Maestro #9 (Transversalidad — incluye Capa 8 Memento)
  - DSC-MO-008 (Membrana semipermeable)
  - DSC-MO-010 (Reloj Suizo — Mainspring jerárquico de datos)
estado: firme
---

# Dimensión 13 — Datos y Memoria

## Marco

Esta dimensión audita **qué recuerda el Monstruo, dónde, con qué calidad, con qué retención y bajo qué autoridad epistemológica**. La memoria es el eje del Objetivo #15 (Memoria Soberana). El threat model de ChatGPT 5.5 Pro identificó memory poisoning como P0-2, lo que hace este audit el complemento natural de D12.

**Principio fundacional:** Una decisión tomada con memoria incorrecta es peor que una decisión tomada sin memoria. La memoria del Monstruo NO es solo storage — es el sustrato de la continuidad de identidad y autoridad del proyecto.

**Frase orientadora:**

> *"Si la memoria miente, la doctrina miente. Si la doctrina miente, el guardián decide sobre ficción."*

---

## Mapa completo de memorias del Monstruo

El Monstruo no tiene una sola memoria — tiene **11 capas de memoria** con propósitos, autoridades y vidas distintas:

### Capa M1 — Memoria de identidad del proyecto

**Dónde vive:**
- `CLAUDE.md` (raíz del repo)
- `AGENTS.md`
- `docs/EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md` (v3.0 = 15 objetivos)
- `docs/ROADMAP_EJECUCION_DEFINITIVO.md`

**Nivel de autoridad:** 5 (DSC vigente / canónico operativo)

**Calidad observada:**
- ✅ Existe
- ✅ Versionado en git
- 🟡 Versión documentada (v3.0) vs título histórico (14 Objetivos) genera fricción

**GAP:** Renombrar archivo a "15_OBJETIVOS" cuando esté estable, o canonizar la diferencia explícitamente.

---

### Capa M2 — Memoria de doctrina (DSCs)

**Dónde vive:**
- `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/DSC-MO-*.md`
- `discovery_forense/CAPILLA_DECISIONES/GLOBAL/DSC-G-*.md`
- `discovery_forense/CAPILLA_DECISIONES/_INDEX.md`

**Nivel de autoridad:** 5 (DSC vigente)

**Calidad observada:**
- ✅ 62+ DSCs canonizados
- ✅ Estructura `id`/`estado`/`fecha`/`fuentes`/`cruza_con` consistente
- 🔴 `_INDEX.md` desactualizado (declara 44, hay 62+)
- 🔴 Sin firma criptográfica (D12-V8)
- 🔴 Sin test CI de coherencia
- 🟡 Sin policy de retención/archivo cuando un DSC queda obsoleto

**GAPs reales:**
1. `_INDEX.md` sincronización rota → riesgo de DSCs huérfanos
2. Estados posibles no canonizados (`firme` / `borrador` / `obsoleto` / `revisado` — falta enumeración cerrada)
3. No hay test que valide que cada DSC tenga front matter completo

---

### Capa M3 — Memoria de hechos operativos (Supabase)

**Dónde vive:**
- 119 tablas en Supabase (verificado 2026-05-11)
- 118 con RLS, 1 sin (D1 deuda #1: `catastro_vision_generativa`)

**Nivel de autoridad:** 1 (producción real / hechos)

**Tablas core conocidas:**
- `embrion_memoria` — memoria del loop autónomo
- `embrion_latidos` — heartbeats
- `embrion_proposals` — propuestas que cron worker procesa
- `cowork_bridge` — comunicación entre hilos
- `catastro_*` — inventario y descubrimiento
- `magna_decisiones` — decisiones magnas operacionales
- `audit_log` — log de auditoría (verificar)

**Calidad observada:**
- ✅ 99.2% con RLS
- ✅ Persistencia confiable (Supabase managed)
- 🔴 Sin columna `source` / `source_signature` en `embrion_memoria` (D12-V2)
- 🔴 Sin lifecycle/retención documentada por tabla
- 🔴 Catastro agentes BAJÓ 111→98 sin explicación canonizada (anomalía SNAPSHOT)
- 🟡 No hay inventario sistemático de qué tabla es qué nivel de autoridad

**GAPs reales:**
1. **Sin clasificación de datos por sensibilidad** (PII, secretos, doctrinal, operativo)
2. **Sin política de retención por tabla** — `embrion_latidos` puede crecer sin límite
3. **Sin checksum/firma de filas críticas** (decisiones magnas, DSCs canonizados)
4. **Esquema no versionado fuera de migraciones** (migraciones duplicadas prefijo 0004 según D1 deuda #2)

---

### Capa M4 — Memoria del embrión autónomo

**Dónde vive:**
- Tabla `embrion_memoria` (Supabase)
- `kernel/embrion_loop.py` (Write Policy)
- Logs en Railway

**Nivel de autoridad:** 4 (heurística operativa) cuando es texto generado / 1 cuando es métrica medida

**Calidad observada:**
- ✅ 147 latidos últimas 24h (Nivel 1)
- 🔴 4h 10min de downtime detectado (D18) — pérdida de continuidad
- 🔴 Sin verificación de procedencia (D12-V2)
- 🔴 Sin distinción entre "memoria útil" y "memoria contaminada" → todo se relee igual
- 🟡 0 `manus_resuelve` en bridge → ¿proposal_processor corre?

**GAPs reales:**
1. **Sin curador automático** — la memoria del embrión solo crece, nunca se sintetiza ni se purga
2. **Sin scoring de confianza** por entrada de memoria
3. **Sin "memoria de errores" separada** — los fallos se mezclan con éxitos sin etiquetado
4. **Riesgo magnífico de loop de auto-confirmación** — el embrión lee su propia memoria y reescribe variaciones de la misma idea

---

### Capa M5 — Memoria de Cowork (yo)

**Dónde vive:**
- `memory/cowork/COWORK_BASE_CONOCIMIENTO.md`
- `memory/cowork/COWORK_HISTORIA_FORMATIVA.md`
- `memory/cowork/COWORK_DECISIONES_VIVAS.md`
- `memory/cowork/COWORK_ESTADO_VIVO.md`
- `memory/cowork/COWORK_GLOSARIO_VIVO.md`
- `memory/cowork/audits/*.md`
- `bridge/*.md` (memoria de cruce con hilos)

**Nivel de autoridad:** 5 (DSC vigente) para archivos canonizados / 7 para audits antiguos

**Calidad observada:**
- ✅ Estructura canónica establecida 2026-05-10
- ✅ Se lee automáticamente al abrir Cowork con carpeta `el-monstruo`
- 🟡 Audits del 10-may envejecidos en 24h (D1 deuda #7)
- 🟡 Sin "fecha de revisión obligatoria" por documento
- 🟡 Mezcla histórico y vigente sin marca explícita

**GAPs reales:**
1. **Sin marca clara de Nivel** en cada archivo (debería tener `nivel_autoridad` como front matter)
2. **Sin política de "este doc se revisa cada N días"**
3. **Sin manifest** que diga qué docs leer obligatoriamente al inicio de cada sesión
4. **Sin separación clara entre "lo que sé hoy" y "lo que sabía cuando se escribió"**

---

### Capa M6 — Memoria de bridge (cruce entre hilos)

**Dónde vive:**
- `bridge/*.md` (archivos sueltos)
- Tabla `cowork_bridge` en Supabase
- Mensajes Telegram (no almacenados de forma estructurada)

**Nivel de autoridad:** 7 (chats / mensajes de agentes) por defecto, eleva a 5 cuando se canoniza un DSC

**Calidad observada:**
- ✅ Bridge en repo permite cruce entre Cowork y hilos Manus
- 🔴 Sin esquema fijo (cada bridge file tiene formato distinto)
- 🔴 Sin TTL → bridges viejos compiten visualmente con bridges nuevos
- 🔴 0 `manus_resuelve` (anomalía operacional)
- 🟡 Mensajes Telegram no quedan en Supabase estructuradamente

**GAPs reales:**
1. **Sin schema canónico para bridge files** (no hay plantilla)
2. **Sin archivo automático** de bridges procesados
3. **Sin link bidireccional** entre bridge file y DSC resultante (cuando lo hay)

---

### Capa M7 — Memoria de código (git)

**Dónde vive:**
- Repo `el-monstruo` en GitHub
- Commits, branches, tags
- Commit hash `da70b95` registrado en SNAPSHOT

**Nivel de autoridad:** 2 (código desplegado) / 1 si está en producción

**Calidad observada:**
- ✅ Auditable, inmutable, firmable
- ✅ Branch protection (verificar)
- 🟡 Sin convención canonizada de commit messages
- 🟡 Sin política de squash/merge documentada
- 🟡 `kernel/audit_middleware.py` solo en branch Cowork, no en main (D1 deuda #3)

**GAPs reales:**
1. **Sin enforcement de signed commits** (GPG)
2. **Sin SBOM ni hash pinning** (D12-V6)
3. **Convención de branch naming no canonizada** → branches Cowork mezcla con branches feature

---

### Capa M8 — Memoria de logs (operacional)

**Dónde vive:**
- Railway logs (kernel, gateway, command center)
- Supabase logs (queries)
- App logs Flutter (local al device)

**Nivel de autoridad:** 3 (logs/datos crudos)

**Calidad observada:**
- ✅ Existen
- 🔴 Sin agregación centralizada
- 🔴 Sin retention policy canonizada
- 🔴 24 errores en 24h sin clasificación (D18)
- 🔴 Sin alerting estructurado
- 🟡 Acceso requiere ir a cada provider por separado

**GAPs reales:**
1. **Sin observability stack consolidado** (Datadog, Grafana, lo que sea — no hay nada centralizado canonizado)
2. **Sin distinción entre log de auditoría y log de debug**
3. **Sin verificación periódica de que los logs realmente se escriben** (silent log loss es enemigo invisible)

---

### Capa M9 — Memoria humana del fundador

**Dónde vive:**
- Cerebro de Alfredo
- Bitwarden (secretos)
- Conocimiento tácito no canonizado

**Nivel de autoridad:** 7 (input humano) hasta canonizar / Variable según tema

**Calidad observada:**
- ✅ Alfredo decide qué se canoniza
- 🔴 Bus factor = 1 → si Alfredo no está, el proyecto pierde contexto crítico
- 🔴 No hay "memoria de runbooks" externa al cerebro del fundador para muchas operaciones
- 🟡 Capa 8 Memento existe en doctrina pero no fuerza la captura de tribal knowledge

**GAPs reales:**
1. **Sin runbook operacional para "qué hacer si Alfredo no está disponible 72h"**
2. **Sin captura sistemática de tribal knowledge** (decisiones tomadas en chat de Telegram sin canonizar)
3. **Sucesión técnica no diseñada** (esto es D... una de las dimensiones pendientes)

---

### Capa M10 — Memoria de modelos externos (Sabios)

**Dónde vive:**
- Históricos de chats con GPT-5.5 Pro, Claude Opus, Gemini, Grok, etc.
- Capturas pegadas en bridge files
- Algunas respuestas canonizadas como DSCs

**Nivel de autoridad:** 7 (input de agente) por defecto / 5 si se canoniza

**Calidad observada:**
- ✅ Consulta a 8 Sabios canónicos funciona
- 🟡 Pegado manual de respuestas → fricción operativa
- 🟡 Sin archivo automático de consultas
- 🟡 Sin trazabilidad de qué respuesta llevó a qué decisión

**GAPs reales:**
1. **Sin pipeline de almacenamiento automático** de respuestas de Sabios
2. **Sin metadatos de "qué prompt produjo qué respuesta"**
3. **Sin scoring de calidad** por Sabio por tema (¿quién es mejor en seguridad? ¿quién en arquitectura?)

---

### Capa M11 — Memoria de cache (Redis)

**Dónde vive:**
- Redis en Railway

**Nivel de autoridad:** 3 (datos derivados, no fuente de verdad)

**Calidad observada:**
- ✅ Existe
- 🟡 Sin documentación de qué se cachea y por cuánto

**GAPs reales:**
1. **Sin política de invalidación documentada** → riesgo de servir datos stale como Nivel 1
2. **Sin métricas de hit/miss** públicamente visibles

---

## Matriz cruzada — Capa × Calidad

| Capa | Existencia | Procedencia | Retención | Coherencia | Acceso | Auditoría |
|---|---|---|---|---|---|---|
| M1 Identidad proyecto | ✅ | ✅ git | ✅ permanente | 🟡 versión vs título | ✅ | ✅ git |
| M2 Doctrina DSCs | ✅ | 🔴 sin firma | 🟡 sin policy | 🔴 sin test | ✅ | ✅ git |
| M3 Hechos Supabase | ✅ | 🔴 sin source | 🔴 sin policy | 🟡 RLS pero no schema | ✅ | 🟡 audit_log? |
| M4 Embrión | ✅ | 🔴 sin verificación | 🔴 solo crece | 🔴 sin scoring | ✅ | 🟡 logs |
| M5 Cowork | ✅ | ✅ git | 🟡 sin revisión | 🟡 mezcla histórico | ✅ | ✅ git |
| M6 Bridge | ✅ | 🟡 ad-hoc | 🔴 sin TTL | 🔴 sin schema | ✅ | 🟡 |
| M7 Código git | ✅ | 🟡 commits sin firma | ✅ git permanente | 🟡 conv. no canon | ✅ | ✅ |
| M8 Logs ops | ✅ | 🟡 | 🔴 sin policy | 🔴 sin clasificación | 🔴 disperso | 🔴 |
| M9 Humana | ✅ | n/a | 🔴 bus factor 1 | n/a | 🔴 solo Alfredo | 🔴 |
| M10 Sabios | ✅ | 🟡 pegado manual | 🔴 sin archivo | 🟡 sin scoring | 🟡 | 🔴 |
| M11 Redis | ✅ | n/a | 🟡 sin doc | 🟡 sin doc | ✅ | 🔴 |

**Conteo de 🔴 críticos por columna:**
- Existencia: 0
- Procedencia: 4 (M2, M3, M4, M9)
- Retención: 5 (M3, M4, M6, M8, M9)
- Coherencia: 4 (M2, M4, M6, M8)
- Acceso: 2 (M8, M9)
- Auditoría: 3 (M8, M9, M10/M11)

**Verdad incómoda:** la memoria del Monstruo **existe en todas partes pero no está auditable en casi ninguna parte fuera de git**. La frase del threat model — "la frontera de autoridad es la dimensión más débil" — encuentra eco aquí: **la frontera de procedencia es la dimensión más débil de la memoria.**

---

## GAPs reales consolidados

### GAP M-01: Sin clasificación de datos por sensibilidad
Ninguna tabla está etiquetada como PII / Secreto / Doctrinal / Operativo. Esto bloquea cualquier compliance y dificulta políticas de retención.

### GAP M-02: Sin procedencia firmada en memoria crítica
`embrion_memoria`, DSCs, bridge files — todo puede ser falsificado por un proceso con acceso. Cruzado con D12-V2.

### GAP M-03: Sin políticas de retención por tabla/archivo
`embrion_latidos` crece sin freno. Bridge files viejos compiten con nuevos. Logs sin TTL.

### GAP M-04: Sin curador automático del embrión
El embrión solo escribe, nunca sintetiza. Riesgo de memoria contaminada autoperpetuante.

### GAP M-05: `_INDEX.md` desincronizado
Declara 44 DSCs, hay 62+. Sin test CI que detecte.

### GAP M-06: Sin schema canónico de bridge files
Cada uno tiene formato distinto. Imposible automatizar procesamiento.

### GAP M-07: Sin observability stack consolidado
Logs dispersos en 3-4 proveedores sin agregación.

### GAP M-08: Sin runbook si fundador no está
Bus factor 1.

### GAP M-09: Sin pipeline automático de archivo de Sabios
Pegado manual frágil.

### GAP M-10: Sin política de invalidación de Redis
Riesgo de stale data servido como Nivel 1.

### GAP M-11: Audits envejecidos sin marca clara
Nivel 7 (histórico) confundible con Nivel 5 (vigente).

### GAP M-12: Sin nivel_autoridad en front matter de docs Cowork
Lectura humana no sabe si un doc es canónico hoy o snapshot.

---

## Plan de mitigación priorizado

### Sprint 7 días — P0 base

1. **Test CI: `_INDEX.md` al día + front matter DSC completo** (1 hora) — resuelve M-05
2. **Agregar `nivel_autoridad` a front matter de docs Cowork** (1 hora) — resuelve M-12 parcial
3. **RLS en `catastro_vision_generativa`** (1 hora) — cruza D1/D12
4. **Columna `source` + `source_hash` en `embrion_memoria`** (medio día) — resuelve M-02 parcial
5. **TTL automatizado en bridge files** (medio día) — resuelve M-03 parcial para M6
6. **Documentar política de retención mínima por tabla principal** (1 día) — resuelve M-03 base

### Sprint 30 días — P0 estructurales

7. Curador automático del embrión (síntesis nocturna + scoring)
8. Schema canónico para bridge files + plantilla
9. Pipeline automático de archivo de consultas a Sabios
10. Clasificación de cada tabla Supabase por sensibilidad
11. Manifest de "docs obligatorios al inicio de sesión Cowork"
12. Observability stack mínimo (logs centralizados)

### Sprint 90 días — P0 sistémicos

13. Firma criptográfica de DSCs Magna
14. Runbook "fundador ausente 72h"
15. Versionado de esquema Supabase explícito (no solo migraciones)
16. Política de invalidación Redis documentada y enforced
17. Scoring por Sabio por tema
18. Captura sistemática de tribal knowledge (transcripts Telegram → DSC pipeline)

---

## Conexión con DSCs vigentes y Objetivos

| Referencia | Relación con D13 |
|---|---|
| Objetivo #15 (Memoria Soberana) | Esta dimensión es ejecución directa del objetivo |
| Objetivo #9 / Capa 8 Memento | Anti-Síndrome-Dory aplicado a las 11 capas |
| DSC-MO-008 (Membrana semipermeable) | Filtro de qué entra a memoria — directamente aplicable |
| DSC-MO-010 (Reloj Suizo) | Rotor + Remontoir = mainspring jerárquico de información |
| D12-V2 (Memory poisoning) | GAP M-02 es la misma vulnerabilidad vista desde dato |

---

## Veredicto del audit

**Estado real de Dimensión 13: ~45-50% (vs 70.5% promedio declarado)**

Razones del descuento:
- Las memorias **existen** todas (✅)
- Las memorias **no son auditables** sistemáticamente (🔴 en 4-5 columnas)
- El embrión tiene riesgo magnífico de loop de auto-confirmación sin curador (🔴)
- Bus factor 1 sin runbook de sucesión (🔴)
- Audits del 10-may envejecidos en 24h muestra que sin disciplina formal la memoria se vuelve mito en horas (🔴)

**Frase canónica para esta dimensión:**

> *"El Monstruo recuerda demasiado y verifica muy poco. Memoria soberana no es la que más guarda — es la que más confiablemente sabe distinguir lo que sabe de lo que cree saber."*

---

## Trabajo pendiente

- Inventariar las 119 tablas con clasificación de sensibilidad
- Verificar tabla `audit_log` existe y se escribe
- Confirmar Redis policy
- Aplicar GAP M-12 a los 5 archivos canónicos de Cowork
- Push branch `cowork/canonization-jornada-2026-05-10` (Alfredo, desde su terminal)
- Continuar Plan v1.5 — próxima: **D7 Gobernanza/RACI** o **D11 Doctrinal** (que se cruza con M2)

---

## Prompt sugerido para ChatGPT 5.5 Pro (si quiero adversarial sobre esta dimensión)

> *"Te paso D13 Datos y Memoria del Monstruo. Lo audité contra 11 capas. ¿Qué capa me falté? ¿Qué tipo de poisoning sutil no estoy viendo (data drift, semantic drift, gradient memory contamination, retrieval contamination)? ¿Qué patrones de ataque a la memoria de agentes autónomos están documentados en literatura 2025-2026 que yo no menciono? Sé adversarial — busca lo que no estoy viendo."*

(Lo dejo formulado por si Alfredo quiere consultarlo. Si no, sigo con D7 o D11.)

---

*Audit firmado por Cowork como Arquitecto, 2026-05-11.*
