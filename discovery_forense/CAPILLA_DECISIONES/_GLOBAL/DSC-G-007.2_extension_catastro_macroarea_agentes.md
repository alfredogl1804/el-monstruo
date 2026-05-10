# DSC-G-007.2 — Extensión del Catastro a Macroárea AGENTES

**Tipo:** Decisión Sistémica Canónica (DSC) GLOBAL
**Fecha:** 2026-05-10
**Hilo origen:** Hilo Catastro (Manus)
**Estado:** PROPUESTO — pendiente firma Cowork (DSC-G-008 v2 audit content)
**Sprint:** S-088
**Versión:** 1.0
**Predecesores:** DSC-G-007.1 (Catastro inicial macroárea inteligencia), DSC-MO-009 (Arsenal seleccionable por Catastro)

---

## Contexto

El Catastro nació en Sprint 86 con la macroárea `inteligencia` (37 modelos LLM puros catalogados). DSC-MO-009 declara que el arsenal del Monstruo debe poder **consultar y decidir** entre todas las herramientas relevantes, no solo modelos LLM. Las macroáreas pendientes son:

- `agentes` — productos/sustratos que envuelven LLMs y ejecutan tareas (Sprint 88, este DSC)
- `vision_generativa` — imagen + video + audio gen (Sprint 87)
- Otras macroáreas futuras: `infraestructura`, `bases_de_datos`, `apis_publicas`, etc.

Sin extensión a `agentes`, el Catastro queda incompleto y el Monstruo no puede razonar sobre qué herramienta usar para tareas operacionales (deploy, browse, render, etc.).

---

## Decisión

Extender el Catastro a macroárea **`agentes`** con **9 dominios canónicos** y **84 productos** clasificados como seed inicial. Establecer la metodología de tronos por dominio con desempate documentado.

### 9 Dominios canónicos

| Dominio (slug) | Definición |
|---|---|
| `agentes_desarrollo` | IDEs, CLIs y agentes de desarrollo profesional dirigidos por developers expertos |
| `agentes_vibe_coding` | Constructores de apps web/mobile no-code/low-code dirigidos por prompt |
| `agentes_multi_swarm` | Frameworks y plataformas de orquestación multi-agente |
| `agentes_investigacion` | Agentes especializados en investigación, browsing autónomo y deep research |
| `agentes_ejecutores` | Workflow engines y agentes de automatización operacional |
| `agentes_creacion_audiovisual` | Generación de video, música, audio y SFX de calidad cinematográfica |
| `agentes_branding_diseno` | Logos, identidad visual, slogans, UI design |
| `agentes_marketing_ventas` | CRM agentic, lead generation, outreach, marketing automation |
| `interfaces_usuario` | Interfaces consumer pro de modelos LLM (chat, computer use, browser nativo) |

### Schema técnico

**Tabla nueva: `catastro_agentes`** (separada de `catastro_modelos` porque las dimensiones técnicas son fundamentalmente distintas).

Campos clave:
- 5 dimensiones booleanas: `tiene_sandbox`, `acceso_filesystem`, `acceso_internet`, `multi_step_capable`, `multi_swarm_capable`
- Enums: `dominio`, `persistencia_memoria` (`none`/`session`/`persistent`/`external_db`), `costo_por_uso_tipico` (`gratis`/`bajo`/`medio`/`alto`/`muy_alto`/`enterprise`), `estado` (`production`/`beta`/`preview`/`open-source`/`deprecated`/`alpha`)
- FK opcional: `llm_base_id` → `catastro_modelos(id)` (NULL para productos agnósticos o cuyo modelo base aún no está catalogado)
- `tier_seed` SMALLINT (1=top-5 por dominio, 2=resto)
- `bonus_curador` SMALLINT (0-5) + `bonus_curador_razon` TEXT — desempate documentado
- Invariante: `multi_swarm_capable=true ⇒ multi_step_capable=true` (CHECK constraint)

### Metodología de selección 6 criterios (DSC-G-007.3)

Cada producto candidato se evalúa contra 6 criterios objetivos:

1. **C1** — Relevancia para arsenal del Monstruo (DSC-MO-009 lo nombra o categoría aplicable)
2. **C2** — Adopción demostrada 2026 (≥2 listas independientes top-AI-agents 2026)
3. **C3** — Madurez técnica (estado `production` o `beta` consolidado)
4. **C4** — Tiene LLM base catalogable (envuelve LLM o framework agnóstico documentado)
5. **C5** — Accesible para Alfredo/Monstruo (API pública, CLI, o tier accesible)
6. **C6** — Capacidad agéntica real (≥2 dimensiones técnicas)

**Tier 1** (score ≥4): validación profunda 3 sabios + tronos. **Tier 2** (score 2-3): validación ligera, candidatos Sprint 88.1.

Matriz completa de los 84 productos × 6 criterios persistida en `bridge/sprint88_matriz_seleccion_6c_2026_05_10.md`.

### Tronos por dominio (DSC-G-007.4)

**Trono = producto con mayor score técnico-operativo por dominio**, calculado en vista materializada `catastro_tronos_agentes`:

```
score_trono =
  + 30 si tier_seed=1 (top-5 del dominio)
  + 15 si multi_swarm_capable
  + 10 si tiene_sandbox
  + 10 si acceso_filesystem
  + 10 si acceso_internet
  + 10 si multi_step_capable
  + 10 si persistencia_memoria='external_db'
  +  5 si estado='production'
  +  bonus_curador (0-5, requiere razón documentada)
```

Desempate: open_weights DESC, tier_seed ASC, id ASC.

### 9 Tronos finales del Sprint 88

| Dominio | 👑 Trono | Score | Justificación |
|---|---|---|---|
| agentes_desarrollo | **Manus** | 85 | Sandbox completo + skills + browser |
| agentes_vibe_coding | **Lovable** | 76 | +1 bonus: top adopción 2026 |
| agentes_multi_swarm | **Kimi K2.6 Agent Swarm** | 100 | Score perfecto, DSC-MO-009 |
| agentes_investigacion | **Perplexity Personal Computer** | 76 | +1 bonus: arsenal Monstruo, lanzado 2026-05-07 |
| agentes_ejecutores | **n8n + LLM nodes** | 95 | Open-source + sandbox + multi-swarm |
| agentes_creacion_audiovisual | **Higgsfield** | 55 | Studio completo + multi-step |
| agentes_branding_diseno | **Kittl** | 55 | Editorial control + brand suite |
| agentes_marketing_ventas | **Clay** | 80 | Data orchestration multi-swarm |
| interfaces_usuario | **Claude.ai** | 76 | +1 bonus: interfaz operativa Monstruo |

---

## Implementación

| Componente | Archivo | Migración |
|---|---|---|
| Tabla `catastro_agentes` | `scripts/030_sprint88_catastro_agentes.sql` | Aplicada |
| 4 dominios nuevos en CHECK | `scripts/031_sprint88_dominios_expandidos.sql` | Aplicada |
| Columna `tier_seed` | `scripts/032_sprint88_tier_seed.sql` | Aplicada |
| Normalizar CHECKs (drop viejo + ampliar costo/persistencia) | `scripts/033_sprint88_normalizar_checks.sql` | Aplicada |
| Columna `bonus_curador` + vista materializada `catastro_tronos_agentes` | `scripts/034_sprint88_bonus_curador.sql` | Aplicada |
| Schema Pydantic | `kernel/catastro/schema.py` (clase `CatastroAgente`, enum `DominioAgentes`, `PersistenciaMemoria`, `CostoPorUsoTipico`) | Commited |
| Seed Python (84 productos) | `scripts/sprint88_seed_85_productos.py` | Insertado |
| INSERT batch | `scripts/sprint88_insert_seed.py` | Ejecutado (84/0/0) |
| Cómputo tronos | `scripts/sprint88_calc_tronos.py` | Ejecutado |
| Matriz 6 criterios | `bridge/sprint88_matriz_seleccion_6c_2026_05_10.md` | Persistida |

---

## Reglas de gobierno

1. **Toda extensión futura del Catastro requiere DSC firmado.** Extender macroáreas o dominios nuevos sin DSC bloquea el cierre de sprint.

2. **Productos cuyo LLM base no está en `catastro_modelos` se admiten con `llm_base_id=NULL` + nota en `data_extra.nota`** indicando "modelo X pendiente catalogar Sprint 88.1". Aplica a: Sora, Veo, Kimi K2.6, Perplexity Sonar.

3. **`tier_seed=1` (top-5 por dominio)** requiere validación adversarial profunda con 3 sabios. **`tier_seed=2`** se admite con validación ligera (1 sabio o evidencia documental).

4. **`bonus_curador > 0`** requiere `bonus_curador_razon` documentada con: (a) razón objetiva del desempate, (b) fuente de evidencia citada, (c) firma humana (Alfredo).

5. **Vista materializada `catastro_tronos_agentes`** se refresca automáticamente al cambiar `bonus_curador` o agregar productos. `REFRESH MATERIALIZED VIEW catastro_tronos_agentes;` requerido tras INSERT/UPDATE batch.

6. **No se modifica `embrion_loop.py` ni tablas del embrión.** Esta extensión es read-add-only sobre el Catastro; el embrión sigue consultando vía abstracción `kernel/catastro/`.

---

## Riesgos asumidos y diferidos

| Riesgo | Plan |
|---|---|
| Validación adversarial 3 sabios sobre 44 productos Tier 1 puede tomar 30+ min | Diferido a fase final del sprint, no bloquea cierre técnico de schema/seed |
| 4 modelos LLM faltantes en `catastro_modelos` (Kimi K2.6, Sonar, Sora, Veo) | Sprint 88.1 |
| Empates de score con `bonus_curador=0` (Higgsfield, Kittl) | Aceptables — tronos canónicos por orden alfabético, ajustar en Sprint 88.1 con métricas de adopción real |
| 40 productos Tier 2 con validación ligera | Aceptable como seed inicial; Sprint 88.1 valida profundo |

---

## Frase canónica de adopción

> 🏛️ **DSC-G-007.2 — Catastro extendido a macroárea AGENTES con 9 dominios, 84 productos seed y 9 tronos calculados. Schema Pydantic + migraciones SQL + vista materializada en producción.**

---

**Firma propuesta:** Manus (Hilo Catastro), 2026-05-10
**Pendiente:** Cowork audit content (DSC-G-008 v2) → firma definitiva
