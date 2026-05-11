# Mapa de Fuentes con Jerarquía de Autoridad — Fase 1 del Plan v1.5

**Generado:** 2026-05-11
**Razón:** Antes de auditar el Monstruo en Fase 2-5, necesito criterio para resolver contradicciones entre fuentes. Sin jerarquía explícita, cualquier choque entre "lo que dice un DSC" vs "lo que hace el código" vs "lo que recuerda Alfredo" se resuelve por sesgo de proximidad, no por evidencia.
**Origen del refactor:** Audit adversarial de ChatGPT 5.5 Pro identificó como supuesto peligroso "documentación equivale a verdad". Este mapa rompe ese supuesto.

---

## §1. Principio fundacional

**Verdad operacional > Verdad declarativa.**

El Monstruo es un sistema vivo. Lo que está ejecutándose AHORA es la verdad. Lo que un documento dice que debería pasar es intención (alta autoridad como dirección, baja autoridad como evidencia de estado actual). Cuando chocan, la verdad operacional vence.

Esto NO desautoriza la doctrina. Significa que la doctrina es **prescriptiva** (cómo debe ser) y la realidad es **descriptiva** (cómo es). Si chocan, la auditoría debe detectar el gap, no esconderlo bajo apelación a la doctrina.

---

## §2. Jerarquía canónica de autoridad (9 niveles)

| Nivel | Tipo de fuente | Autoridad | Decay rate |
|---|---|---|---|
| 1 | **Producción real** (Railway services running, Supabase production, Telegram bot live, LikeTickets activo) | **Máxima** | 0 (siempre vigente mientras corre) |
| 2 | **Código desplegado** (branch main del repo, código que produce la producción) | Muy alta | Baja (cambia cuando se mergea PR) |
| 3 | **Logs/datos** (embrion_memoria, Langfuse traces, Railway logs, Supabase query history, GitHub commit history) | Muy alta | 0 (historia inmutable) |
| 4 | **Tests reproducibles** (99 test_*.py + 10 workflows CI + pre-commit hooks) | Alta | Media (caducan cuando código cambia sin actualizar test) |
| 5 | **DSC canonizada vigente** (62+ DSCs firmados) | Alta | Variable (alta si el código cumple, baja si no) |
| 6 | **Docs estratégicos** (ROADMAP, OBJETIVOS, AGENTS.md, ARQUITECTURA_*, CLAUDE.md, ANÁLISIS_*) | Media | Alta (caducan rápido en proyecto vivo) |
| 7 | **Chats / outputs de agentes** (bridge/, outputs Manus, outputs Cowork históricos, 12 audits del 10-may) | Media-baja | Muy alta (semanas) |
| 8 | **Opinión actual** (esta sesión Cowork-Alfredo, conversación viva) | Variable | Inmediata (cambia cada turno) |
| 9 | **Aspiración** (Objetivos Maestros como visión, sprints firmados sin arrancar, futuras macroáreas) | Baja como evidencia / Alta como dirección | Lenta (años) |

---

## §3. Fuentes específicas del Monstruo clasificadas

### Nivel 1 — Producción real (máxima autoridad)

| Activo | Dónde vive | Cómo validarlo |
|---|---|---|
| Kernel principal | Railway service `el-monstruo-kernel` | `curl /v1/health` retorna 200 |
| Embrión vivo | Proceso autónomo en kernel | Query `embrion_memoria` últimas 24h: 147 latidos verificados al 11-may |
| Gateway AG-UI | Railway service `ag-ui-gateway` | WebSocket connect |
| Command Center | Manus hosted `monstruodash-ggmndxgx.manus.space` | HTTP GET |
| Proposal processor cron worker | Railway service separado | 0 proposals en limbo verificado |
| Supabase production | Proyecto `xsumzuhwmivjgftsneov` | 119 tablas, 118 con RLS, 147 latidos/24h, 41 modelos catastro, 98 agentes |
| Telegram bot `@MounstroOC_bot` | Producción Telegram + webhook al kernel | Mensaje `6cc845f1-...` aprobado por chat_id `7712993094` |
| LikeTickets producción | Repo externo `like-kukulkan-tickets` + dominio + Stripe LIVE | $41,445 MXN/sem, 303 órdenes pagadas, $105,035 MXN acumulados |

**Regla operacional:** si un DSC, doc o claim contradice un dato Nivel 1, el dato Nivel 1 vence. La doctrina debe actualizarse para cerrar el gap, no al revés.

### Nivel 2 — Código desplegado (muy alta)

| Activo | Path | Cómo validarlo |
|---|---|---|
| `el-monstruo` branch main | Commit hash `da70b95...` al 11-may 03:04 UTC | `git log -1` |
| `like-kukulkan-tickets` | Repo externo privado (acceso solo Alfredo + Daniel) | Solo Daniel puede confirmar estado |
| Apps Flutter | `apps/mobile/lib/` | Último commit toca apps/mobile: `71f8c9a` (Agent Selector scrollable). Congelado desde Sprint 48 |
| Command Center frontend | Repo externo Manus | Manus hosted |
| Migraciones SQL aplicadas | `migrations/sql/0001` a `0010+` | Verificar `pg_dump` schema vs archivos SQL |

**Regla operacional:** lo que está en `main` mergeado es lo que opera en producción (después del deploy). Si una DSC dice X y `main` hace Y, la DSC está aspiracionalmente firmada pero NO enforced. Eso es deuda doctrinal a documentar.

### Nivel 3 — Logs/datos (muy alta, historia inmutable)

| Activo | Acceso |
|---|---|
| `embrion_memoria` table | MCP Supabase. Captura cada mensaje a Alfredo, cada latido del embrión, cada reanclaje Cowork, cada acuse Manus |
| `kernel_audit_log` (si existe post-S-003.B Tarea 1) | MCP Supabase — investigar en Fase 2 |
| Langfuse traces | Dashboard Langfuse (no probé acceso desde sandbox) |
| Railway logs | Railway dashboard (acceso vía Alfredo) |
| GitHub commit history | MCP github, `git log` |
| GitHub PR history | MCP github |
| Supabase query history | Supabase dashboard |
| Stripe LikeTickets transaction log | Stripe dashboard (acceso vía Alfredo o Daniel) |

**Regla operacional:** los logs son la única fuente irrefutable de "qué pasó cuándo". Si un postmortem dice "X pasó el 4-may" y los logs no lo confirman, el postmortem está reconstruido por memoria, no por evidencia.

### Nivel 4 — Tests reproducibles (alta, decay cuando código cambia)

| Activo | Conteo | Cómo validar vigencia |
|---|---|---|
| Tests unitarios + integración | 99 archivos `tests/test_*.py` | `pytest` debe pasar en CI |
| Workflow CI principal | `.github/workflows/ci.yml` | Último run status |
| Workflow RLS weekly audit | `rls-audit-weekly.yml` | Verificar status + GitHub Secrets configurados |
| Workflow SAST | `sast.yml` | Último run |
| Workflow SBOM | `sbom.yml` | Último run |
| Workflow CVE scan | `cve-scan.yml` (S-003.A) | Último run |
| Workflow Credentials rotation reminder | `credentials-rotation-reminder.yml` (S-003.A) | Status |
| Workflow Milestone Declaration Guard | `milestone-declaration-guard.yml` (DSC-G-014/G-017) | Status |
| Workflow License audit | `license-audit.yml` | Status |
| Workflow eval | `eval.yml` | Status |
| Workflow AI infra guard | `ai-infra-guard.yml` | Status |
| Workflow secret-scan | `secret-scan.yml` | Status |
| Pre-commit hooks | `.pre-commit-config.yaml` | Lista: gitleaks, trufflehog, detect-private-key, large-files, merge-conflicts, spec-lint, rls-default-check |

**Regla operacional:** tests en verde son evidencia fuerte. Tests sin correr o sin ejecutar tras un cambio son evidencia débil. Para Fase 2, debo verificar **última corrida exitosa** de cada workflow.

### Nivel 5 — DSCs canonizadas vigentes (alta, variable según enforcement)

**Total al 11-may: 62+ DSCs**

| Subdirectorio | Conteo | DSCs firmados |
|---|---|---|
| `_GLOBAL/` | 22+ | G-001 a G-009, G-012, G-014, G-017, V-001/002, X-001 a X-006, S-001 a S-008, S-010, G-007.2, G-007.5 |
| `EL-MONSTRUO/` | 10 | MO-001 a MO-010 (con DSC-EL-MONSTRUO-001/003/004 sin renombrar) |
| `CIP/` | 8 | CIP-001 a CIP-006 + 2 PEND |
| `LIKETICKETS/` | 3 | LT-001/002/003 |
| `MENA-BADUY/` | 3 | MB-001/002/003 |
| `BIOGUARD/` | 2 | BG-001 + 1 PEND |
| `TOP-CONTROL-PC/` | 2 | TC-001/002 |
| `KUKULKAN-365/` | 2 | K365-001/002 |

**Estados posibles de un DSC:**
- **FIRMADO + enforced** (código cumple, tests validan) → autoridad ALTA real
- **FIRMADO + aspiracional** (código no cumple aún) → autoridad ALTA como dirección, BAJA como descripción del estado actual
- **FIRMADO + contradicho por realidad** (código hace lo opuesto) → DSC en estado de **deuda doctrinal**, debe re-canonizarse o el código debe alinearse
- **PROPUESTO** (no firmado todavía) → autoridad BAJA, requiere validación Alfredo
- **OBSOLETO no marcado** → autoridad baja, debe marcarse como histórico

**Regla operacional:** para cada DSC en Fase 2, debo asignar uno de los 5 estados. NO basta saber que existe.

**Deudas canónicas detectadas en snapshot:**
- `_INDEX.md` declara 44 DSCs cuando hay 62+ (deuda de indexación)
- Naming inconsistente (DSC-EL-MONSTRUO-* vs DSC-MO-*, DSC-LIKETICKETS-* vs DSC-LT-*, DSC-GLOBAL-* vs DSC-V-*)
- DSC-S-005 con dos archivos distintos (normativo Cowork + forense Manus)
- DSC-CIP-002 confusión nominal entre ticket mínimo $1 USD vs CIP-PEND-002 distribución rendimientos

### Nivel 6 — Docs estratégicos (media autoridad, decay alto)

**89 archivos en `docs/`** + subdirectorios `adr/`, `biblias/`, `biblias_agentes_2026/`, `biblias_v73/`, `embrion_export/`, `proyectos/`, `templates/`.

**Categorías:**

| Categoría | Ejemplos | Autoridad relativa |
|---|---|---|
| Constitucionales | `AGENTS.md`, `CLAUDE.md` raíz, `EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md` v3.0 | Alta (cuasi-Nivel 5) |
| Arquitectura | `ARQUITECTURA_RELOJ_SUIZO_v1.0.md`, `ARQUITECTURA_ENGRANAJE_v1.0.md`, `DIVISION_RESPONSABILIDADES_HILOS.md` | Alta si cumplida, media si aspiracional |
| Roadmap | `ROADMAP_EJECUCION_DEFINITIVO.md`, sprints firmados | Media-alta como dirección, baja como descripción de estado |
| Sprint plans históricos | `SPRINT_55_PLAN.md` a `SPRINT_80_PLAN.md`, `SPRINT_79`, `SPRINT_80` | Histórico — bajo nivel actual, alto valor para entender trayectoria |
| Cruces de validación | `CRUCE_SPRINT*_vs_14OBJETIVOS.md` (15 archivos) | Histórico, validador puntual |
| Analyses | `ANALISIS_CAPA1_FISICA_ENGRANAJES`, `ANALISIS_RELOJ_SUIZO_CAPA2`, `ANALISIS_GUARDIAN_DE_LOS_OBJETIVOS`, `ANALISIS_FALLO_AGENTICO_vs_13_OBJETIVOS` | Media — analítico, no normativo |
| Brand | `BRAND_ENGINE_ESTRATEGIA.md` | Alta para Objetivo #2 |
| Históricos / desactualizados | `DIRECTIVA_HILO_A_FASE1.md` (cuando Cowork era Ejecutor — ya invertido el rol), `ESTADO_UNIFICADO_SINCRONIZACION_HILOS.md` (v2.0 con dos hilos Manus, no 3) | Baja — patrimonio histórico |
| Auditorías | `AUDIT_ROADMAP_COWORK_2026-05-04.md`, `AUDITORIA_OBJETIVOS_SPRINTS_55_70.md`, `AUDIT_ROADMAP_APENDICE_1_3_FACTOR_VELOCITY_RECALIBRADO.md` | Media — snapshot puntual |
| Estado del Monstruo | `ESTADO_DEL_MONSTRUO_*.md`, `ESTADO_UNIFICADO_SINCRONIZACION_HILOS.md` | Decay rápido |
| Visión | `EL_MONSTRUO_APP_VISION_v1.md` | Aspiracional (Nivel 9 mixto) |
| Backlog | `BACKLOG_TECNICO_MONSTRUO_VS_MANUS.md` | Media |

**Regla operacional:** docs ≠ código. Si doc dice X y código hace Y, el código vence. El doc debe actualizarse o marcarse como histórico.

### Nivel 7 — Chats / outputs de agentes (media-baja, decay muy rápido)

| Activo | Conteo | Cómo tratarlos |
|---|---|---|
| Handoffs `bridge/cowork_to_manus_*.md` | ~10 | Históricos de intenciones — validar si Manus efectivamente ejecutó |
| Reportes `bridge/manus_to_cowork_*.md` | ~20 | Outputs Manus — evidencia DÉBIL hasta verificar producción |
| Postmortems `bridge/postmortem_*.md` | 6+ | Reconstrucciones — fuerza media (mejor que opinión, peor que logs) |
| Sprints propuestos `bridge/sprints_propuestos/*.md` | 10+ | Aspiracional hasta firma |
| Specs específicos (sprint_memento, sprint_88, etc.) | Variable | Idem |
| **Audits scheduled del 10-may** | 12 en `memory/cowork/audits/` | Outputs autónomos Cowork — **autoridad MEDIA porque fueron escritos sin validación humana ni cruce con producción** |
| `cowork_to_manus_DRAFT_*.txt` y `.md` | 2 (drafts Ejecutor 1) | Borradores — autoridad BAJA |
| Resúmenes mensajes Cowork↔Alfredo | Esta sesión + previas | Variable |

**Regla operacional CRÍTICA:** los **12 audits scheduled del 10-may** son outputs autónomos sin validación humana al momento de generarse. Cuando los lea en Fase 2, debo cruzarlos contra Nivel 1-3 (producción + código + logs) antes de aceptar sus claims. NO darles autoridad de Nivel 5 (DSC) automáticamente.

### Nivel 8 — Opinión actual (variable, decay inmediato)

Esta sesión Cowork-Alfredo del 11-may.

| Tipo | Autoridad |
|---|---|
| Decisiones Magnas declaradas por Alfredo | Alta (cuasi Nivel 5) — necesitan canonización en DSC para subir a 5 |
| Decisiones operativas declaradas por Alfredo | Alta |
| Hipótesis de Alfredo sin verificar | Media — requiere validación |
| Opiniones de Cowork (yo) | Baja — yo no soy fuente normativa por mí mismo, solo intérprete + auditor |
| Outputs de Manus en sesiones vivas | Media-baja — verificar antes de ejecutar |

**Regla operacional:** la opinión de Alfredo en esta sesión sobre temas estructurales (visión, dirección estratégica, restricciones reales) tiene autoridad ALTA pero NO es DSC hasta canonizarse. Las decisiones operativas pueden ejecutarse en el momento.

### Nivel 9 — Aspiración (baja como evidencia, alta como dirección)

| Activo | Naturaleza |
|---|---|
| 15 Objetivos Maestros como visión a largo plazo | Dirección — alta autoridad para decidir qué construir; baja autoridad para afirmar qué está construido |
| Objetivo #13 "Del Mundo" | Aspiracional — al 10% real |
| Ecosistema federado SOVEREIGN-RED | Aspiracional — sprint sin arrancar |
| Reloj Suizo eventual publicación SDK | Aspiracional + 10 gates pendientes |
| 8 Embriones de La Colmena | Aspiracional — solo Embrión-0 vivo (Embrión-1 a Embrión-7 son specs futuros) |
| Sprints firmados sin arrancar | Aspiracional hasta ejecutarse |
| Roadmap META Sprint 90+ | Aspiracional |

**Regla operacional:** la aspiración NO es evidencia de estado actual. Si Objetivo #13 dice "Del Mundo" pero hoy estamos al 10%, decir "el Monstruo es del Mundo" sería falso. Decir "el Monstruo aspira a ser del Mundo" es verdadero. La diferencia importa para honestidad pura.

---

## §4. Reglas de resolución de conflictos entre niveles

Cuando dos fuentes contradicen, esta tabla resuelve:

| Si A es Nivel X y B es Nivel Y | Vence |
|---|---|
| X > Y | A |
| X = Y, A más reciente | A (con justificación documentada) |
| X = Y, ambas vigentes contradictorias | **Anomalía: documentar como deuda — requiere decisión Alfredo** |
| Nivel 1 (producción) vs cualquier otro | Producción siempre |
| Nivel 5 (DSC firmada) vs Nivel 2 (código que la viola) | **Deuda doctrinal**: o se actualiza DSC o se ajusta código. Mientras tanto, REALIDAD = código |
| Nivel 7 (output Manus) sin Nivel 1-3 confirmando | DESCONFIAR — verificar antes de actuar |
| Nivel 9 (aspiración) vs Nivel 1 (realidad actual) | Realidad para describir estado; aspiración para definir dirección |

### Casos típicos esperables en Fase 2-3

1. **"DSC dice X pero código hace Y"** → documentar como deuda doctrinal explícita. NO ocultar.
2. **"Audit del 10-may declara N% completado, pero producción muestra menor"** → audits scheduled son Nivel 7, producción es Nivel 1 — producción vence.
3. **"Manus reportó haber pusheado X, pero git log no lo muestra"** → log vence. Investigar dónde quedó el trabajo de Manus.
4. **"Alfredo recuerda haber decidido Y, pero DSC dice otra cosa"** → si DSC tiene fecha posterior, DSC vence; si memoria de Alfredo es posterior y consistente, requiere canonización (subir Nivel 8 a Nivel 5).
5. **"Doc estratégico (Nivel 6) contradice DSC (Nivel 5)"** → DSC vence; doc debe actualizarse.
6. **"Snapshot 11-may muestra 98 agentes Catastro, pero audit 10-may declaraba 111"** → snapshot vence. Anomalía a investigar.

---

## §5. Aplicación a las 27 dimensiones del Plan v1.5

Cada dimensión debe auditarse usando esta jerarquía. Plantilla para cada dimensión:

```
Dimensión X — [Nombre]

Fuente Nivel 1 disponible: [path / acceso]
Fuente Nivel 2 disponible: [path]
Fuente Nivel 3 disponible: [tabla / log]
Fuente Nivel 4 disponible: [test path]
Fuente Nivel 5 disponible: [DSC IDs]
Fuente Nivel 6 disponible: [doc paths]
Fuente Nivel 7 disponible: [outputs históricos]
Fuente Nivel 8 disponible: [opiniones actuales]
Fuente Nivel 9 disponible: [aspiración / visión]

Estado evidence-based: [síntesis usando Nivel 1-4]
Estado declarado: [síntesis usando Nivel 5-7]
GAP entre los dos: [diferencia]
Acción para cerrar GAP: [pregunta para Alfredo / verificación adicional / DSC update / código update]
```

---

## §6. Excepciones especiales y casos límite

### Excepción 1 — Filosofía del Monstruo

La filosofía (honestidad pura, par bicéfalo, membrana semipermeable, etc.) es Nivel 5 cuando está canonizada como DSC, pero su **fuente generadora** es Alfredo + emergencias de hilos Manus en conversaciones específicas (`LA_CONVERSACION_2_MAYO_2026.md`).

Esto crea una tensión:
- Las conversaciones emergidas son Nivel 7 (outputs de agentes en sesión)
- Pero la filosofía que emergió en ellas es Nivel 5 cuando se canoniza
- Sin embargo, la **autoridad última de la filosofía es Alfredo** (Nivel 8 elevado a Nivel 5 mediante canonización)

**Regla especial:** la filosofía canonizada en DSC vence interpretaciones posteriores. Pero NUEVAS canonizaciones filosóficas (DSCs nuevos) requieren autoridad de Alfredo, no de Cowork solo.

### Excepción 2 — Memoria persistente del propio Cowork

Los 5 documentos en `memory/cowork/` (Base de Conocimiento, Decisiones Vivas, Historia Formativa, Estado Vivo, Glosario) escritos por Cowork son Nivel 7 cuando se escriben, pero **pueden subir a Nivel 6 (docs estratégicos)** si Alfredo los valida.

**Regla especial:** Cowork no canoniza Cowork por sí solo. Los docs de `memory/cowork/` requieren validación de Alfredo en sesión Cowork-Alfredo para subir su autoridad.

### Excepción 3 — Outputs autónomos de scheduled tasks (los 12 audits del 10-may)

Son outputs autónomos sin validación humana. Por defecto Nivel 7 medio-bajo.

**Regla especial:** un claim de un audit scheduled (Nivel 7) puede contradecir el snapshot 11-may (Nivel 1). Cuando eso pasa, el snapshot vence. Pero el audit puede contener información útil sobre el estado del momento (10-may) que el snapshot 11-may no captura. Reconciliar como "ESTADO al 10-may vs ESTADO al 11-may" — ambos son verdaderos en su momento.

### Excepción 4 — DSC propuesto pero no firmado

Un DSC en estado PROPUESTO tiene autoridad de Nivel 6 (doc estratégico) hasta que sea firmado y canonizado, momento en el cual sube a Nivel 5.

### Excepción 5 — Subproyectos del portfolio sin código en monorepo

LikeTickets vive en repo externo (`like-kukulkan-tickets`). Para auditar su realidad:
- Nivel 1 (producción): accesible via Stripe + dominio + Daniel
- Nivel 2 (código): inaccesible desde este sandbox sin clonar
- Nivel 5 (DSC): DSCs LT-001/002/003 firmados en monorepo

**Regla especial:** para subproyectos del portfolio sin código en monorepo, la auditoría depende de Alfredo (Nivel 8) o de Daniel para confirmar Nivel 1-2. Sin eso, la pericia es necesariamente parcial.

---

## §7. Aplicación inmediata a anomalías del snapshot 11-may

Aplicando la jerarquía a los hallazgos del snapshot:

### Anomalía 1 — Catastro agentes bajó de 111 a 98

- Fuente Nivel 1 (snapshot 11-may): 98 agentes
- Fuente Nivel 7 (audit scheduled 10-may): 111 agentes declarados
- **Verdad operacional:** 98. La diferencia (-13) ocurrió entre 10-may noche y 11-may madrugada.
- **Posibles causas a investigar Fase 2:**
  - Deduplicación ejecutada (Hilo Catastro o Alfredo manual)
  - Limpieza programada (cron desconocido)
  - Rollback de inserts erróneos
  - Modificación de `kernel/catastro/schema.py` uncommitted causó constraint que eliminó duplicados
- **Acción:** consultar Alfredo + revisar `kernel/catastro/schema.py` modificado + revisar logs Supabase del periodo 10-may 23:00 UTC a 11-may 03:00 UTC.

### Anomalía 2 — 1 tabla sin RLS

- Fuente Nivel 1 (snapshot 11-may): 118 de 119 con RLS
- Fuente Nivel 5 (DSC-S-006 v1.1): "RLS por defecto en tablas nuevas"
- **Verdad operacional:** hay 1 tabla violando la doctrina DSC-S-006.
- **Probable causa:** nueva tabla (`kernel_audit_log` Sprint S-003.B Tarea 1) agregada en producción sin migrar el patrón RLS, posiblemente porque el commit del Ejecutor 2 quedó en mi branch Cowork sin push.
- **Acción Fase 2:** identificar cuál es la tabla específica + verificar si corresponde a un PR mergeado o a un cambio directo en producción.

### Anomalía 3 — `kernel/catastro/schema.py` modificado uncommitted

- Fuente Nivel 2 (código local): modificado
- Fuente Nivel 5 (DSC): podría requerir nueva canonización si el schema cambió estructuralmente
- **Acción Fase 2:** `git diff kernel/catastro/schema.py` para ver qué cambió, decidir si commitear, descartar, o canonizar.

### Anomalía 4 — Branch Cowork sin push

- Branch local `cowork/canonization-jornada-2026-05-10` con 9 commits.
- Nivel 2 (código) está local pero NO en producción ni en GitHub remoto.
- **Acción:** push pendiente de Alfredo desde su terminal (sandbox Cowork bloqueado por proxy HTTP 403).

---

## §8. Reglas operativas Cowork para Fase 2 en adelante

Cuando audite cada dimensión:

1. **NUNCA aceptar un claim sin identificar su Nivel.** Si leo "el Monstruo tiene X% completado en Objetivo Y", debo saber si esa cifra viene de Nivel 1 (medida real) o Nivel 7 (audit declarativo) o Nivel 9 (aspiración mal interpretada).

2. **Citar el Nivel de cada afirmación.** En cada audit que escriba en Fase 2-5, debo anotar `[Nivel N: <fuente>]` después de cada claim significativo.

3. **Cuando dos niveles chocan, declarar la deuda explícitamente.** NO esconder. NO racionalizar. NO apelar a la doctrina como si fuera realidad.

4. **Cuando Nivel 1 no es accesible, declarar el límite.** Para subproyectos externos (LikeTickets), no fingir cobertura. Decir "Nivel 1 no auditable desde este sandbox, depende de Alfredo o Daniel".

5. **Outputs de scheduled tasks son Nivel 7, no Nivel 5.** Aunque estén bien escritos, no son canónicos hasta validación humana.

6. **La opinión actual de Alfredo es Nivel 8, pero su autoridad sobre dirección estratégica es Nivel 9-Alta.** Cuando Alfredo declara intención (no hecho), eso guía la siguiente canonización. NO equivale a estado actual.

7. **Yo (Cowork) no soy fuente normativa por mí mismo.** Mis outputs requieren validación de Alfredo para canonizarse. Soy intérprete + auditor + propositor — no canonizador autónomo.

8. **Tests verdes son evidencia más fuerte que DSCs.** Si DSC dice X y test correspondiente está verde, alta confianza. Si DSC dice X pero no hay test, confianza media. Si DSC dice X y test correspondiente está rojo o no existe, deuda.

---

## §9. Próxima fase

**Fase 2 — Lectura con extracción obligatoria de las 27 dimensiones.**

Estimación: 8-12 turnos.

Output esperado: documentos en `memory/cowork/audits/` con la plantilla del §5 aplicada a cada dimensión. Cada claim citado con Nivel + fuente. Cada contradicción detectada documentada como deuda.

**Orden tentativo de las 27 dimensiones (priorizado por bloqueo de otras dimensiones):**

1. Dimensión 1 (Técnica) — fundamento para todas las demás
2. Dimensión 18 (Escalabilidad SRE) — relacionada con técnica
3. Dimensión 12 (Seguridad/Adversarial) — relacionada con técnica
4. Dimensión 16 (Datos, memoria, privacidad) — relacionada con técnica
5. Dimensión 2 (Doctrinal) — base normativa
6. Dimensión 14 (Gobernanza, RACI) — relacionada con doctrinal
7. Dimensión 17 (Evaluación, metrología) — relacionada con doctrinal
8. Dimensión 11 (De futuro) — roadmap explícito
9. Dimensión 15 (Producto, UX) — qué se construye
10. Dimensión 24 (GTM, ventas) — relacionada con producto
11. Dimensión 13 (Alineación, ética, daño) — relacionada con producto
12. Dimensión 3 (Económica) — sostenibilidad
13. Dimensión 19 (IP, licencias) — economía + defensa
14. Dimensión 26 (Responsabilidad civil, seguros) — relacionada con IP
15. Dimensión 4 (Operacional) — cómo se opera hoy
16. Dimensión 22 (Salud operacional fundador) — operacional + relacional
17. Dimensión 23 (Talento, organización) — operacional + relacional
18. Dimensión 21 (Sucesión, continuidad) — riesgo existencial
19. Dimensión 6 (Relacional) — humanos
20. Dimensión 25 (Supply chain) — proveedores
21. Dimensión 9 (Regulatorio) — externas
22. Dimensión 20 (Crisis, comunicación pública) — escudo
23. Dimensión 10 (Competitivo) — externo
24. Dimensión 5 (Temporal) — histórico
25. Dimensión 7 (Visionario) — aspiracional
26. Dimensión 8 (Filosófica) — fundacional pero requiere haber leído todo
27. Dimensión 27 (Sostenibilidad ambiental) — última prioridad

---

*Mapa de fuentes con jerarquía de autoridad canonizado. Versión 1.0 al 2026-05-11. Modificar solo si nueva fuente emerge o si una regla resulta inoperante en aplicación. Documento de referencia obligatorio para todas las fases subsiguientes del estudio v1.5.*
