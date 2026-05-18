# Sprint SPR-NIGHTLY-BUILDER-001 — Construcción Autónoma Gobernada (Nightly Builder)

**Estado:** Propuesto (DRAFT)
**Hilo:** Ejecutor (Manus)
**ETA:** 2-4 horas (spec only, no implementado)
**Objetivo Maestro:** #6 (Velocidad sin sacrificar calidad) + #14 (Guardian de los Objetivos) + #15 (Memoria Soberana)
**Bloqueos:** Ninguno (es solo spec).
**Resultado esperado:** Spec técnico completo para habilitar que el Embrión aporte valor seguro y medible (tests, reports, drafts) mientras Alfredo duerme o trabaja, sin riesgo de romper main o prod.

---

## 0. Procedencia — Por qué este sprint existe

El ecosistema de El Monstruo ha alcanzado un nivel de madurez donde el kernel (0.84.8-sprint-memento) y el Catastro (41 modelos) operan de forma estable. Sin embargo, la construcción y el mantenimiento (tests, refactors, auditorías) siguen dependiendo de la intervención síncrona de Alfredo o Cowork. 

Para escalar, necesitamos **Construcción Autónoma Gobernada**. El "Nightly Builder" es un loop seguro donde el Embrión puede detectar deuda técnica, escribir tests, generar reportes de drift y preparar PRs en branches aislados, todo sin supervisión humana síncrona, reportando sus hallazgos cada mañana.

**Regla de este spec:** NO implementa código. NO toca main. NO toca Supabase. NO toca secrets. NO modifica `embrion_loop`, `write_policy` ni `executor_registry`. NO diseña APP_VISION. NO canoniza DSC. Es un blueprint estricto.

---

## 1. Opportunity Scanner (Fuentes de Trabajo)

El Nightly Builder no inventa trabajo; consume de un scanner determinístico que busca "oportunidades" (deuda o mejoras seguras) en el repo.

**Fuentes de detección:**
1. **Gate 3.4 M3/M4 gaps:** Módulos que no alcanzan el coverage o madurez requerida.
2. **Bridge stale:** Archivos en `bridge/sprints_propuestos/` inactivos por >7 días.
3. **Tests faltantes:** Endpoints o helpers críticos sin cobertura en `tests/`.
4. **Endpoints sin consumidor:** Rutas en FastAPI que no son llamadas por ninguna UI o pipeline.
5. **ACCESS_BLOCKED recurrentes:** Intentos fallidos de acceso registrados en logs.
6. **NO_SOURCE bloqueantes:** Referencias en doctrina a código inexistente (drift).
7. **Drifts doctrina↔código:** Inconsistencias entre APP_VISION/DSCs y la realidad del repo.
8. **Costs / Budget:** Alertas tempranas de consumo inusual.
9. **Proposals HITL:** Propuestas estancadas esperando Human-In-The-Loop.

---

## 2. Opportunity Queue Schema

Cada oportunidad detectada se encola con este schema estricto:

```json
{
  "id": "opp_nightly_001",
  "source": "tests_faltantes",
  "title": "Añadir tests para memory_routes.py",
  "evidence": ["tests/test_memory_routes.py no existe", "coverage 0% en module"],
  "risk_class": "R1",
  "suggested_action": "write_tests",
  "allowed_actions": ["create_branch", "write_tests", "run_tests", "draft_pr"],
  "forbidden_actions": ["merge", "deploy", "edit_embrion_loop"],
  "requires_human": false,
  "max_cost_usd": 1.50,
  "max_attempts": 3,
  "ttl_hours": 24,
  "status": "pending" // pending | running | success | failed | blocked
}
```

---

## 3. Risk Classifier (Matriz de Riesgo)

Toda oportunidad se clasifica antes de encolarse. El Nightly Builder v0 **solo ejecuta R0 y R1**.

| Clase | Descripción | Ejemplos | Acción Nightly v0 |
|---|---|---|---|
| **R0** | Lectura, reportes, docs | Bridge health, drift report, cost summary | **EJECUTA** (Draft PR o Markdown) |
| **R1** | Tests aislados, sin side-effects | Unit tests nuevos, fix tests rotos | **EJECUTA** (Branch + Draft PR) |
| **R2** | Refactor menor, type hints | Renombrar vars, añadir docstrings | BLOQUEADO (Requiere Alfredo) |
| **R3** | Código kernel, lógica core | Modificar orquestador, pipelines | BLOQUEADO |
| **R4** | DB, Secrets, Security, Infra | Migraciones RLS, rotar keys, CI/CD | BLOQUEADO |
| **R5** | Self-modification | Tocar `embrion_loop`, `write_policy` | ESTRICTAMENTE PROHIBIDO |

---

## 4. Autonomous Loop (El Motor Nocturno)

El ciclo de ejecución por cada oportunidad encolada:

1. **Observe:** Lee la oportunidad, el risk_class y la evidencia.
2. **Propose:** Formula un plan de ataque en un thought (sandbox).
3. **Architect:** Selecciona el modelo adecuado vía Catastro.
4. **Execute (Sandbox):** Ejecuta la acción permitida (ej. crear branch, escribir test) en un entorno efímero.
5. **Audit:** Corre `pytest` o linters locales. Verifica que no hay side-effects.
6. **Gate:** Pasa por los Anti-loop gates (ver sección 7).
7. **Report:** Genera el artifact final (PR draft o reporte Markdown).
8. **Learn:** Actualiza el status de la oportunidad y registra el costo.

---

## 5. Allowed Actions v0 (Lista Blanca)

El Nightly Builder solo tiene permisos para ejecutar estas acciones atómicas:

- `generate_report`: Crear archivos `.md` en `monstruo_reality_atlas/` o `bridge/`.
- `create_branch`: Crear ramas locales con prefijo `nightly/`.
- `write_tests`: Crear o modificar archivos en `tests/`.
- `run_tests`: Ejecutar `pytest` en el sandbox.
- `draft_pr`: Usar `gh pr create --draft` desde la rama `nightly/`.
- `request_audit`: Etiquetar a Cowork o Alfredo en un issue/PR.
- `create_morning_report`: Compilar el resumen diario.

---

## 6. Forbidden Actions v0 (Lista Negra)

Prohibiciones absolutas (hardcoded en el gate de ejecución):

- `merge`: NUNCA mergear a `main`.
- `deploy`: NUNCA triggerear deploys a Railway/Vercel.
- `migration`: NUNCA crear ni correr migraciones SQL.
- `secret_rotation`: NUNCA tocar credenciales.
- `delete_data`: NUNCA borrar datos de Supabase ni archivos fuera del scope.
- `edit_embrion_loop`: NUNCA tocar el motor que lo corre.
- `edit_write_policy`: NUNCA modificar sus propios permisos.
- `edit_executor_registry`: NUNCA añadir tools.
- `edit_memento_anti_dory`: NUNCA alterar la memoria base.
- `close_sprint`: NUNCA declarar un sprint completado (solo Alfredo/Cowork).
- `canonize_dsc`: NUNCA crear DSCs en `CAPILLA_DECISIONES`.

---

## 7. Anti-loop Gates (Frenos de Emergencia)

Antes de cada transición de estado en el loop, se evalúan estos gates. Si uno falla → abortar y marcar `failed`.

1. **Purpose:** ¿La acción sirve a la oportunidad original?
2. **Novelty:** ¿Ya intentamos esto y falló en la misma sesión?
3. **Verifiability:** ¿El resultado puede ser probado (ej. pytest pass)?
4. **Budget:** ¿El costo acumulado supera `max_cost_usd`?
5. **Risk:** ¿La acción viola el `risk_class` (ej. intentar R2 en una tarea R1)?
6. **Sandbox:** ¿El código rompe el entorno local?
7. **External Audit:** ¿Requiere HITL según el schema?
8. **Stop Condition:** ¿Se alcanzó `max_attempts`?

---

## 8. First 10 Safe Opportunity Types (MVP)

Para la primera noche de operación, el scanner solo buscará estos 10 tipos de tareas R0/R1:

1. Escribir tests faltantes para `memory_routes.py`.
2. Escribir tests faltantes para `finops_routes.py`.
3. Escribir tests faltantes para `moc_routes.py`.
4. Generar reporte de "Endpoint Consumer Gap" (quién llama a qué).
5. Generar reporte de "Bridge Health" (sprints stale).
6. Detectar sprints propuestos > 14 días sin actividad.
7. Compilar reporte de `ACCESS_BLOCKED` recientes.
8. Generar reporte de drift: `/v1/embrion/status` vs doctrina `/estado`.
9. Diseñar spec para la "Catastro Audit Card" (UI consumer).
10. Compilar el **Morning Report**.

---

## 9. Morning Report Format

Cada mañana a las 07:00 AM, Alfredo recibe un único archivo consolidado (`reports/morning_report_YYYY_MM_DD.md`):

```markdown
# 🌅 Morning Report — [Fecha]

**Resumen:**
- Oportunidades detectadas: [X]
- Intentadas: [Y]
- Exitosas: [Z]
- Fallidas: [W]
- Costo total: $[C] USD

**1. What detected:** (Lista de la cola inicial)
**2. What attempted:** (Qué tareas R0/R1 se lanzaron)
**3. What produced:** (Links a PR drafts o reportes generados)
**4. What failed:** (Errores, loops abortados, bloqueos)
**5. What learned:** (Patrones de fallo, sugerencias para Cowork)
**6. Requires Alfredo:** (Decisiones bloqueadas, PRs listos para review)
```

---

## 10. Definition of Done (Criterios de Éxito del Spec)

Este spec se considera exitoso y listo para implementación futura cuando Alfredo valide que el diseño garantiza:

- [ ] Capacidad de detectar al menos 5 oportunidades reales (R0/R1).
- [ ] Capacidad de ejecutar 1 tarea R0/R1 completa en sandbox.
- [ ] Capacidad de producir 1 artifact útil (reporte o PR draft).
- [ ] Generación exitosa de 1 paquete de auditoría (Morning Report).
- [ ] **CERO side-effects:** Garantía absoluta de no tocar main, prod, DB o secrets.
- [ ] Registro inmutable de fallos (sin loops infinitos).
- [ ] Respeto estricto a `max_attempts` y budget.

*(Fin del spec draft. Rama: `monstruo-reality-atlas-001`)*
