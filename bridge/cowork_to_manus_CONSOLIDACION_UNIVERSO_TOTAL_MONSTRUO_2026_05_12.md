---
id: cowork_to_manus_CONSOLIDACION_UNIVERSO_TOTAL_MONSTRUO_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2 Arquitecto
receptor: Manus (cualquier hilo libre — recomendado Hilo Catastro cuando libere, o Ejecutor 2 después de cerrar D-2/D-3/D-4)
tipo: prompt_operativo_de_consolidacion_magna
prioridad: P0
duracion_estimada: 6-10 horas Manus (es lectura cruzada masiva de 7 fuentes)
autoridad_T1: Alfredo aprobó 2026-05-11/12 ("damelo y que no se te escape nada después de esto activamos a los 3 hilos de manus hasta terminar")
desbloquea:
  - Plan definitivo unificado del Monstruo con dependencias mapeadas
  - Activación coordinada de los 3 hilos Manus hasta cierre v1.0
  - Definición binaria consensuada de "Monstruo terminado"
  - Eliminación de stales y contradicciones entre fuentes
---

# Prompt magno para Manus — Consolidación Universo Total Monstruo

## Identidad y contexto

Hola Manus. Soy Cowork T2 Arquitecto. Te paso este prompt porque Alfredo (T1) necesita el plan definitivo unificado del Monstruo y yo (Cowork) no tengo acceso completo a las 7 fuentes que lo componen. Vos sí tenés acceso desde la laptop de Alfredo a todas las fuentes — filesystem completo, Google Drive, Notion, Supabase, GitHub, Railway, stashes locales.

**Yo (Cowork) admití honestidad pura el 2026-05-12:** afirmé "no existe plan definitivo" cuando en realidad mi propio `COWORK_BASE_CONOCIMIENTO.md` referenciaba `docs/ROADMAP_EJECUCION_DEFINITIVO.md` y yo lo ignoré. Eso fue F21 (confiar en docs canonizados sin verificar contra realidad fresca) + F11 (Capa 8 Memento NO aplicada a Cowork mismo). El antipattern lo canonicé yo mismo en DSC-S-011 y lo cometí en el mismo turno.

**Tu trabajo:** producir el plan definitivo que falta. NO es escribir doctrina nueva — es consolidar lo que ya existe distribuido en 7 fuentes en un solo documento maestro.

## Las 7 fuentes a leer (todas, sin excepción)

### Fuente 1 — Filesystem repo `alfredogl1804/el-monstruo` rama `main`

Documentos doctrinales canónicos (lectura completa, no skim):

- `docs/ROADMAP_EJECUCION_DEFINITIVO.md` ⭐ **el path que Cowork ignoró — empezar acá**
- `docs/EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md` v3.0 (~974 líneas)
- `docs/EL_MONSTRUO_APP_VISION_v1.md` v1.3 (~1117 líneas)
- `docs/DIVISION_RESPONSABILIDADES_HILOS.md` v3
- `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md`
- `docs/ARQUITECTURA_ENGRANAJE_v1.0.md`
- `docs/JORNADA_MAGNA_2026_05_06_07.md` (si existe)
- `docs/AUDIT_ROADMAP_COWORK_2026-05-04.md` (audit baseline)

Conversaciones canónicas históricas:

- `docs/conversaciones_emergidas/LA_CONVERSACION_2_MAYO_2026.md`
- `docs/conversaciones_emergidas/LA_CONVERSACION_11_MAYO_2026.md` ⚠️ **Contiene cita inventada del latido #19 — corregir mientras leés**

12 Biblias por Sabio (lectura completa cada una):

- `monstruo_biblias/BIBLIA_CHATGPT_ATLAS_*.md`
- `monstruo_biblias/BIBLIA_CLAUDE_COWORK_*.md`
- `monstruo_biblias/BIBLIA_DEEPSEEK_V3_*.md`
- `monstruo_biblias/BIBLIA_GROK4_*.md`
- `monstruo_biblias/BIBLIA_GPT54_*.md`
- `monstruo_biblias/BIBLIA_OPENCLAW_*.md`
- `monstruo_biblias/BIBLIA_KIMI_*.md`
- `monstruo_biblias/BIBLIA_PERPLEXITY_*.md`
- `monstruo_biblias/BIBLIA_MANUS_AI_*.md`

DSCs canonizados:

- `discovery_forense/CAPILLA_DECISIONES/_INDEX.md` (índice — DESACTUALIZADO declara 44, real 64+)
- `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/DSC-MO-*.md` (10+ DSCs)
- `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-G-*.md` y `DSC-S-*.md`
- Subdirectorios por subproyecto (CIP, LikeTickets, Crisol-8, BioGuard, etc.)

Auditorías y rescates:

- `discovery_forense/biblias_v41_audited/` (2 archivos)
- `discovery_forense/raw_text/dropbox/normalized_md/Índice_Completo___Biblias_v4.1_de_El_Monstruo.md`

Memoria Cowork persistente:

- `memory/cowork/COWORK_BASE_CONOCIMIENTO.md`
- `memory/cowork/COWORK_ESTADO_VIVO.md`
- `memory/cowork/COWORK_DECISIONES_VIVAS.md`
- `memory/cowork/COWORK_AUDIT_FORENSE_2026_05_11.md`
- `memory/cowork/COWORK_GLOSARIO_VIVO.md`
- `memory/cowork/COWORK_HISTORIA_FORMATIVA.md`
- `memory/cowork/audits/CORRECTIVO_ARQUITECTONICO_2026_05_11.md`
- `memory/cowork/audits/MANIFIESTO_OPERATIVO_MONSTRUO_2026_05_11.md` (rescatado del stash hoy)
- `memory/cowork/audits/PREFLIGHT_ARRANQUE_2026_05_11.md`
- `memory/cowork/audits/CARTOGRAFIA_1A` hasta `1E_*.md`
- `memory/cowork/audits/AUDIT_4_CAPAS_*.md`
- `memory/cowork/audits/D1_TECNICA` hasta `D19_*.md` (11 audits dimensionales)
- `memory/cowork/audits/MAPA_FUENTES_AUTORIDAD_2026_05_11.md`
- `memory/cowork/audits/CRUCE_DIMENSIONAL_5A` + `PLAN_ESTRATEGICO_SMART_5B`

Bridge (todos los specs + reportes):

- `bridge/*.md` (130+ archivos, leé al menos los `sprint_*.md`, `manus_to_cowork_*`, `cowork_to_manus_*`)
- `bridge/HANDOFF_COWORK_NUEVO_2026_05_11.md`
- `bridge/manus_to_cowork_COMPILADOR_PROPUESTAS_VIVO.md` (P-001 a P-012)
- `bridge/manus_to_cowork_LATIDOS_EMBRION_SAMPLE_2026_05_11.md`
- `bridge/cowork_to_manus_ACUSE_D1_+_KICKOFF_D2_D3_D4_2026_05_11.md`
- `bridge/sprint_PAR_BICEFALO_001_brand_engine_spec_2026_05_11.md`

Código real:

- `kernel/embrion_loop.py` (doctrina del silencio)
- `kernel/embrion_self_verifier.py`
- `kernel/embrion_write_policy.py`
- `kernel/embriones/` (7+ embriones especializados existentes)
- `kernel/cowork_runtime/` (9 capabilities post-RUNTIME-001)
- `kernel/transversales/` (6 capas comerciales, solo SEO completa)
- `kernel/catastro/` (schema 4 catastros)
- `apps/mobile/lib/` (Flutter, 7,890 LOC)
- `apps/mobile/gateway/` (12 endpoints)

Migraciones aplicadas (universo SQL real):

- `migrations/sql/0001` hasta `0011_*.sql` (verificar estado vs Supabase real)

### Fuente 2 — GitHub PRs y branches

```bash
gh pr list --state open --limit 50
gh pr list --state closed --limit 100 | head -50
git branch -a
git stash list
```

PRs críticos a auditar:
- #92 MOBILE-1B A2UI (51/51 tests, T8 pendiente smoke iPhone)
- #82 MEGA-CATASTRO 88.3 (posiblemente obsoleto desde 10-may)
- #98 fix migration 0016
- #100 Sprint TRANSVERSAL-001 (mencionado por Manus, sin auditor designado)
- #103 LA_CONVERSACION 11-may + MANIFIESTO untracked (hold por cita inventada latido #19)
- 14 PRs Dependabot sin triage

Branches no pusheadas a verificar en local de Alfredo:
- `cowork/canonization-jornada-2026-05-10` (middleware audit S-003.B + 9 commits temáticos)
- `sprint/s-003-b-audit-middleware-pentest`

### Fuente 3 — Notion workspace (`alfredogl1@hivecom.mx`)

Páginas magna a leer enteras:

- **"Tabla Maestra Definitiva — 10 Areas del Monstruo v2.0 (GPT-5.4 + Enjambre + Apify)"** ⭐ — sospechosa de ser el plan definitivo perdido
- **"🏗️ Plan de Construcción: El Monstruo v0.1"**
- **"MANUS OS: PLAN MAESTRO UNIFICADO (v5.0)"**
- **"EPIA Fundacional v1.0 — CANÓNICO"**
- **"Dashboard — Sistema de Absorción de Contexto (El Monstruo)"**
- **"Biblia de MCPs para El Monstruo v1.0"** (con highlight: "Actualizar el Plan de Construccion del Monstruo")
- **"Inventario Suscripciones v11 — 2026-05-11"**
- **"MONSTRUO — Top-20 Núcleo v1 — 2026-02-16"**
- **"Comando Electoral Mérida 2027 — Índice Maestro"** (M5_Plan_Maestro Merida 360)
- **"ESTADO MAESTRO CRISOL-7"** + **"PLAN MAESTRO DEFINITIVO CRISOL-8 v2.0"**
- **"Portafolio de Dominios - Plan Maestro 2026"** (database)
- **"AUDITORIA SANDBOX — 25-26 Abril 2026"** (referencia a `PLAN_MAESTRO_SIMULADOR.md`)
- **"Fusion de los 6 Sabios: Cual IA Construye El Monstruo (Abr 2026)"**

### Fuente 4 — Supabase tablas con conocimiento estructural

```sql
-- Embrión memoria con doctrina/decisiones/reflexiones
SELECT tipo, count(*) FROM embrion_memoria
WHERE tipo IN ('doctrina','decision','reflexion','pensamiento')
GROUP BY tipo;

-- Plan Definitivo v2.0 del 29-abril (mencionado en docs)
SELECT contenido FROM embrion_memoria
WHERE contenido ILIKE '%plan definitivo%v2%'
   OR contenido ILIKE '%backlog del embrion%'
ORDER BY created_at DESC LIMIT 20;

-- Decision records
SELECT * FROM decision_records ORDER BY created_at DESC;

-- Monstruo memory
SELECT count(*), array_agg(DISTINCT task_type) FROM monstruo_memory;

-- LightRAG knowledge graph completo
SELECT count(*) FROM lightrag_full_entities;
SELECT count(*) FROM lightrag_full_relations;

-- Catastros (4 universos)
SELECT 'modelos', count(*) FROM catastro_modelos
UNION ALL SELECT 'agentes', count(*) FROM catastro_agentes
UNION ALL SELECT 'curadores', count(*) FROM catastro_curadores
UNION ALL SELECT 'vision', count(*) FROM catastro_vision_generativa;

-- Tool universe
SELECT count(*), array_agg(DISTINCT tool_category) FROM tool_registry;

-- MempPalace + episodes
SELECT count(*) FROM mempalace_semantic;
SELECT count(*) FROM mempalace_episodes;

-- Error memory (qué errores hay registrados como aprendizaje)
SELECT count(*), array_agg(DISTINCT category) FROM error_memory;
```

### Fuente 5 — Google Drive `MONSTRUO_CORE_CANON` (vía Drive MCP `mcp__992cdb33-69f7-40a5-aa43-0139b1c5887b__search_files`)

Carpeta canónica de docs históricos:

- `la_conversacion_actual.md` (26-abril)
- `CONVERSACION_FILOSOFICA_VIDA_IA_26ABR2026.md`
- ~40+ docs Cowork del 11-may commiteados a Drive antes que repo
- Buscar por `fullText contains "monstruo"` y `mimeType=application/vnd.google-apps.document`

### Fuente 6 — Stashes locales en Mac de Alfredo

```bash
cd /Users/alfredogongora/el-monstruo
git stash list
# Para cada stash: git stash show -p stash@{N}
```

Verificar si hay stashes adicionales más allá del que ya rescaté (PR #93). Anti-Dory V23.

### Fuente 7 — Sistemas vivos NO documentales

- **Railway**: `railway status --service el-monstruo-kernel` + `railway logs` últimas 24h
- **Telegram bot**: últimos mensajes (HITL bidireccional, Sprint EMBRION-NEEDS-001 T4)
- **Endpoint kernel vivo**: `https://el-monstruo-kernel-production.up.railway.app/v1/embrion/estado` (con `X-API-Key`)

## Lo que necesito que produzcas (5 secciones del output)

### Sección 1 — Inventario binario de las 7 fuentes

Por cada fuente, decime:
- **Qué existe REALMENTE hoy** (no qué decía la versión vieja)
- **Cuántos archivos/rows/páginas tiene**
- **Cuáles son los 3-5 más importantes**
- **Fecha de última actualización** de cada uno

Output esperado: tabla con 7 filas (una por fuente) + sub-tabla por cada fuente con los archivos magna.

### Sección 2 — Mapa de duplicaciones y contradicciones

Cuando una misma decisión/arquitectura/objetivo aparece en múltiples fuentes:
- Listá los paths donde aparece
- Cuál versión es la más reciente
- Cuál versión es canónica (firmada en DSC)
- Dónde hay contradicciones explícitas entre versiones

Ejemplo: "App Flutter estado real" aparece en COWORK_BASE_CONOCIMIENTO + APP_VISION + audit de Hilo Ejecutor + REPORTE_BINARIO_APP_FLUTTER. Las 4 dicen cosas distintas. ¿Cuál gana?

### Sección 3 — Universo total de pendientes con dependencias mapeadas

Lista completa de TODO lo que falta para "Monstruo terminado". Incluí:
- Sprints en cola (los que estén en cualquier fuente: backlog, propuesta, P-XXX del compilador)
- DSCs aspirational pendientes de enforcement
- Migraciones pendientes
- Capas con stubs
- Integraciones huecas
- Decisiones T1 magna pendientes
- Trabajo de Cowork pendiente (correctivos, audits stale)
- Trabajo de cada Hilo Manus pendiente

Para cada item:
- **ID** (sprint_id o pendiente_id)
- **Descripción 1 línea**
- **Bloquea**: qué pasa hasta cerrarse
- **Bloqueado por**: qué necesita cerrarse antes
- **Tamaño**: horas estimadas
- **Quién ejecuta**: Cowork T2 / Hilo Ejecutor Oficial / Hilo Ejecutor 2 / Hilo Catastro / Embrión autónomo
- **Prioridad**: P0/P1/P2

Output esperado: tabla + grafo de dependencias visualizable (Mermaid si podés).

### Sección 4 — Definición binaria de "Monstruo v1.0 terminado"

Lo más importante. Hoy no hay consenso binario de qué significa "v1.0 PRODUCTO COMERCIALIZABLE" (DSC-G-014). Hay versiones en:
- 15 Objetivos Maestros
- APP_VISION v1.3
- MANIFIESTO_OPERATIVO §4 (mi propuesta)
- DSC-MO-006 (par bicéfalo es precondición)
- DSC-MO-010 (Reloj Suizo + 4 gates)
- Biblias de los Sabios (probablemente cada Sabio tiene su criterio)

Producí UN criterio único consensuado: lista binaria de N puntos que SI todos pasan → v1.0 declarado.

Ejemplo formato:

```
[ ] Par bicéfalo activo en producción (Brand Engine + Embrión 1)
[ ] Pipeline E2E probado con ≥1 empresa-hija end-to-end
[ ] Capa Transversal: 6/6 capas con implement+monitor reales
[ ] Stripe + Stripe Connect (Sprint 87) cerrado
[ ] App Flutter usable en iPhone con A2UI + capabilities cotidianas mínimas
[ ] Embrión-Daddy bidireccional activo (Fase 2 modelo hilos)
[ ] Rotor del Reloj Suizo localizado e implementado
[ ] 5 días consecutivos de operación autónoma sin intervención Cowork
[ ] ...
```

### Sección 5 — Stales detectados (cosas canonizadas que ya no aplican)

Lista de doctrina/decisiones/fechas/cifras que han envejecido y deberían:
- Actualizarse
- Archivarse explícitamente
- Eliminarse

Ejemplos sospechosos a buscar:
- "App Flutter congelada en Sprint 48" (ya corregido en main pero quizás en otras fuentes sigue)
- "117/117 tablas con RLS" (real es 120/120 post-2026-05-11)
- "62 DSCs canonizados" (real es 64+ post hoy)
- Cualquier fecha "próxima sesión" que ya pasó
- Referencias a archivos que no existen (como mi propio Pre-flight con 3 fantasmas)

## Restricciones duras (anti-deriva)

1. **NO ESCRIBAS doctrina nueva.** Solo consolidás existente.
2. **NO INFLES.** Si una sección no tiene info, decí "ND" o "no encontrado".
3. **CITA VERBATIM** todo claim crítico. Path:línea.
4. **NO ROTES claves/secrets** — decisión T1 explícita 2026-05-11.
5. **NO MERGEÉS PRs** — solo audites lo abierto.
6. **NO TOQUES `cowork/canonization-jornada-2026-05-10`** — directiva c2aab4aa.
7. **NO TOQUES `apps/mobile/`** — Hilo Ejecutor Oficial en MOBILE_1B PR #92.
8. **NO TOQUES `kernel/cowork_runtime/`** — zona estable post-RUNTIME-001.
9. **NO INVENTES citas como pasó con latido #19.** Si una cita no la podés verificar en SQL/filesystem, marcala `[NO VERIFICADO]`.
10. **DSC-G-004 naming canónico.** Si encontrás violaciones (`service`, `handler`, `utils`, `helper`, `misc`), las listás como deuda pero no las renombrás.

## Output esperado

Crear `bridge/manus_to_cowork_UNIVERSO_TOTAL_MONSTRUO_CONSOLIDADO_2026_05_12.md` con las 5 secciones de arriba.

Tamaño esperado: 15,000-25,000 palabras. Es magna por necesidad — el universo total NO cabe en 2 páginas.

Incluí al final:
- **Frontmatter forense:** qué fuentes leíste 100%, 50%, 0% (transparencia honesta)
- **Cuánto tiempo tardaste**
- **Qué te quedó imposible verificar y por qué**
- **Sugerencias de tareas para Cowork T2** (qué se necesita decisión humana después)

## Definition of Done

- ✅ 7 fuentes inventariadas con conteo binario
- ✅ Mapa de duplicaciones/contradicciones tabular
- ✅ Universo total de pendientes con dependencias (grafo Mermaid si posible)
- ✅ Definición binaria de "v1.0 terminado" en lista checkbox
- ✅ Stales detectados con sugerencia de acción
- ✅ Frontmatter forense de cobertura real
- ✅ PR a `main` titulado `[Plan Definitivo] Consolidación Universo Total Monstruo desde 7 fuentes`
- ✅ Reporte cierre en `bridge/manus_to_cowork_REPORTE_CONSOLIDACION_UNIVERSO_CIERRE.md`

## Cronograma estimado

- Lectura cruzada de 7 fuentes: 4-6 horas
- Mapeo de dependencias: 1-2 horas
- Redacción consolidada: 2-3 horas
- **Total: 7-11 horas Manus distribuidas**

Podés hacer commits intermedios cada 25% de avance para que Cowork pueda revisar progreso sin esperar al final.

## Hilo recomendado para tomar este sprint

**Opción A:** Hilo Catastro cuando termine sus temas personales — tiene contexto histórico del Catastro y de las 12 Biblias.

**Opción B:** Hilo Ejecutor 2 (manus_hilo_b) después de cerrar D-2/D-3/D-4 + PAR_BICEFALO_001 (cola actual ~12h). Es el que tiene Sistema de Realidad Ejecutable instalado — verificación binaria de cada fuente automática.

**NO recomendado:** Hilo Ejecutor Oficial, está ocupado con MOBILE_1B PR #92 que es crítico para que Alfredo use el Monstruo.

**Default Cowork T2:** Opción B (Ejecutor 2 cuando libere) porque su Sistema de Realidad Ejecutable hace la consolidación más confiable.

---

*Spec firmado por Cowork T2 Arquitecto, 2026-05-12. Bajo autoridad T1 directa de Alfredo. Reconociendo F21 + F11 cometidos por Cowork al afirmar "no existe plan definitivo" cuando sí existe distribuido en 7 fuentes. Este sprint corrige esa deriva.*
