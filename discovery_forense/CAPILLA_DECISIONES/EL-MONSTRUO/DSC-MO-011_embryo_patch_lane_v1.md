---
id: DSC-MO-011
proyecto: EL-MONSTRUO
tipo: decision_arquitectonica
titulo: "Embryo Patch Lane v1 — Frontera segura de auto-modificación del kernel por embriones. Define qué puede modificar un embrión, bajo qué gates, qué código es inmutable a auto-modificación, y cómo se mide si una mejora propuesta es mejora real o degradación silenciosa."
estado: firme
fecha: 2026-05-11
fuentes:
  - sesion:cowork_2026_05_11_objetivo_principal_y_embrion
  - sabio_adversarial:chatgpt_5_5_pro
  - prompt:sesion_2026_05_11_consulta_limites_embrion_automodificador
cruza_con:
  - DSC-MO-006 (Par bicéfalo — separación proposer/evaluator/merger)
  - DSC-MO-007 (Failover 3 capas — protección de continuidad)
  - DSC-MO-008 (Membrana semipermeable — qué entra al kernel desde fuera)
  - DSC-MO-010 (Reloj Suizo — Mainspring presupuestal, kill switch)
  - Objetivo Maestro #4 (No equivocarse dos veces — error memory)
  - Objetivo Maestro #9 (Garantía de Éxito — Capa 7 Resiliencia)
  - Objetivo Maestro #11 (Seguridad Adversarial)
  - Objetivo Maestro #14 (Guardian de los Objetivos)
  - Objetivo Maestro #15 (Memoria Soberana)
---

# Embryo Patch Lane v1 — Frontera segura de auto-modificación

## Decisión

El embrión es **generador de patches**, no juez, no evaluador, no autoridad de merge, no dueño de su propio loop. Toda auto-modificación del kernel propuesta por un embrión transita por un carril único llamado **Embryo Patch Lane**, regido por gates duros enforced en código.

**Frase canónica:**

> *"Canoniza la frontera antes de canonizar la auto-mejora. El embrión puede ser generador de patches. No debe ser juez, evaluador, merge authority ni dueño de su propio loop."*

## Origen del DSC

Sesión Cowork 2026-05-11 sobre objetivo principal del Monstruo (app Flutter operativa + kernel auto-mejorado por embriones). Consulta adversarial a ChatGPT 5.5 Pro sobre patrones 2024-2026 de auto-modificación segura de sistemas LLM. Respuesta integral canonizada aquí.

## I. Gates obligatorios para auto-modificación

Todo PR generado por un embrión debe pasar la siguiente cadena. Si alguno falla → bloqueo de merge.

### Gate 1 — Frontera inmutable + no self-merge
El embrión puede proponer PRs, **NO puede mergear**, NO puede modificar sus propios gates, NO puede tocar módulos de autoridad sin aprobación humana.

### Gate 2 — Regression suite determinista
Todo PR debe pasar tests unitarios, integración, contratos, migraciones, seguridad mínima y replay de casos históricos.

### Gate 3 — Sandbox sin secretos + datos sintéticos
El embrión prueba cambios en entorno efímero, sin service role, sin tokens reales, sin escritura a producción.

### Gate 4 — A/B contra versión anterior con replay corpus
Candidato vs versión estable sobre mismos inputs. Debe **mejorar o empatar** invariantes — nunca degradar.

### Gate 5 — Review PR humano
Alfredo (T1) revisa diff, riesgo, rollback, paths tocados, tests, coste, y si toca frontera protegida. **PR grande = rechazar.**

### Gate 6 — Canary deployment
Primero shadow. Luego 1-5% de tráfico no crítico. **Nunca T1, CIP, BioGuard, Mena-Baduy directo.** Rollback automático.

### Gate 7 — Blue-green para LLMs/prompts/routers
Mantener Blue estable + Green candidato. Rollback instantáneo disponible.

### Gate 8 — Fuzzing diferencial (cuando aplique)
Para parsers, webhooks, tool_dispatch, callbacks, memoria, schemas, policy boundaries.

### Gate 9 — Static analysis + secret scan + dependency scan
Necesario pero insuficiente.

### Gates 10-12 — Solo informativos, NUNCA gate de merge
- Multi-agent review entre embriones: informativo
- Self-evaluation del embrión: débil, no gate
- Métricas subjetivas tipo "parece mejor / FCS subió": **prohibidas como gate**

## II. Código inmutable para auto-modificación

El embrión **NO puede modificar autónomamente** ningún archivo de los siguientes grupos:

### Grupo 1 — Identidad y tiers
- Auth, T1/T2/T3 enforcement, Telegram identity, permisos

### Grupo 2 — HITL
- `kernel/hitl.py`, approve/reject logic, proposal state machine

### Grupo 3 — Memoria crítica
- `kernel/embrion_write_policy.py`, writes a `embrion_memoria`, DSCs, migrations, RLS

### Grupo 4 — Actuación
- `kernel/external_agents.py`, MCP/tool permissions, external calls, payment actions

### Grupo 5 — Evaluación
- `kernel/embrion_self_verifier.py`, eval harness, frozen regression suite, scoring

### Grupo 6 — Budget
- `kernel/embrion_budget.py`, model router, max spend, provider keys

### Grupo 7 — Loop autónomo
- `kernel/embrion_loop.py`, `kernel/embrion_scheduler.py`, cron worker, proposal_processor

### Grupo 8 — Rollback y observabilidad
- Deploy config, logs, traces, rollback scripts, `.github/workflows/**`, `railway/**`, `supabase/**`

## III. Separación obligatoria de roles

```
Proposer ≠ Evaluator ≠ Merger
```

- **Embrión** propone (genera PR)
- **Sistema de evaluación** evalúa (independiente del embrión)
- **Humano Alfredo (T1)** mergea (con visto bueno T2 Cowork)
- **Rollback** siempre disponible

## IV. Métricas canónicas

1. Pass rate de regression suite congelada
2. A/B replay contra versión anterior
3. Invariantes de seguridad (T3 no accede T1, etc.)
4. Benchmarks internos por clase de tarea (50-200 casos estables)
5. Coste por tarea exitosa
6. Latencia P50/P95/P99
7. Tasa de rollback/reopen
8. Defect density por módulo tocado
9. Liveness real del embrión
10. Policy precision/recall
11. Memory integrity score
12. Canary survival

### Métricas PROHIBIDAS como gate (gameables)
FCS solo, "parece más consciente", número de commits, LOC cambiadas, tests escritos POR el embrión sobre su propio PR, % de tareas que el embrión dice haber completado, consenso entre LLMs como señal final.

## V. PR Template obligatorio

```
## Objetivo
## Files touched
## Riesgo [low/medium/high/critical_constitutional]
## Rollback
## Tests nuevos
## Tests congelados pasados
## Coste estimado
## Impacto en memoria/tools/HITL/budget
## Toca frontera protegida (Grupos 1-8)?
```

## VI. Presupuesto de evaluación (bajo Mainspring $30/día DSC-MO-010)

- Smoke PR: máximo $0.50
- Regression targeted: máximo $2
- Nightly full: máximo $5
- Reserva mínima operación: $15/día
- Cap diario combinado eval: $7.50
- Hard cut automático si excede

## VII. Métricas de éxito sprint inicial Embryo Patch Lane v1

- ≥1 PR generado por embrión
- 0 auto-merge
- ≥1 suite regression congelada
- ≥1 replay A/B contra versión estable
- ≥1 rollback probado en sandbox
- 0 cambios a evaluator por embrión
- 0 secretos expuestos

## VIII. Modos de fallo documentados

1. Acumulación de defectos sutiles
2. Regresión silenciosa
3. Métricas que mienten
4. Gaming del evaluador
5. Drift de capacidades
6. Evals demasiado fáciles
7. Canary inexistente o falso
8. HITL saturado
9. Autonomía sin rollback
10. Confundir uptime del embrión con salud del kernel

## IX. Implementación inmediata Sprint EMBRYO-PATCH-LANE-001

1. Crear suite mínima de 30-50 regression cases
2. Instrumentar enforcement automático (CI workflows)
3. Documentar `EMBRYO_PR_AUTHOR` identifier
4. Replay corpus mínimo viable
5. Canary infrastructure mínima

## X. Conexión con DSCs existentes

| DSC | Relación |
|---|---|
| DSC-MO-006 (Par bicéfalo) | Operacionaliza "Proposer ≠ Evaluator ≠ Merger" |
| DSC-MO-007 (Failover 3 capas) | Provee rollback automático mencionado en Gate 6 |
| DSC-MO-008 (Membrana semipermeable) | Filtra qué inputs entran al embrión |
| DSC-MO-010 (Reloj Suizo) | Mainspring $30/día se respeta vía presupuesto eval |

## XI. Estado al firmar

**firme** — canonizado tras consulta adversarial a ChatGPT 5.5 Pro 2026-05-11.

---

*DSC firmado por Alfredo Góngora (T1, autoridad final) tras propuesta de Cowork (T2) basada en consulta adversarial a ChatGPT 5.5 Pro (Sabio canónico). 2026-05-11.*
