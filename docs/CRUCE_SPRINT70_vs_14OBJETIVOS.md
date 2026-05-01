# Cruce Sprint 70 vs. 14 Objetivos Maestros — Modo Detractor

> **Sprint:** 70 — "El Cierre Viviente" (SPRINT FINAL DE SERIE 61-70)
> **Fecha de análisis:** 1 de mayo de 2026
> **Metodología:** Análisis en modo detractor (devil's advocate). El objetivo NO es validar el sprint, sino encontrar debilidades, gaps y riesgos que el plan no aborda.
> **Score de confianza PRE-correcciones:** 7.5/10
> **Score de confianza POST-correcciones:** 9.0/10

---

## Tabla de Cobertura

| Obj # | Nombre | Pre-Sprint 70 | Impacto Sprint 70 | Post-Sprint 70 | Tendencia |
|---|---|---|---|---|---|
| 1 | Crear Empresas Completas | 92% | +0% | 92% | Estable |
| 2 | Estándar Apple/Tesla | 94% | +1% | 95% | Sube (demo valida calidad) |
| 3 | Mínima Complejidad | 90% | +2% | 92% | REVIERTE DESCENSO |
| 4 | No Equivocarse 2 Veces | 96% | +1% | 97% | Sube (deferred verification) |
| 5 | Gasolina | 91% | +1% | 92% | Sube (consolidación reduce costo) |
| 6 | Vanguardia | 95% | +0% | 95% | Estable |
| 7 | No Inventar la Rueda | 94% | +1% | 95% | Sube (skill deprecation) |
| 8 | Emergencia | 95% | +1% | 96% | Sube (demo captura emergencia) |
| 9 | Transversalidad | 100% | +0% | 100% | Cerrado |
| 10 | Simulador | 92% | +1% | 93% | Sube (demo como simulación) |
| 11 | Embriones | 100% | +0% | 100% | Cerrado |
| 12 | Soberanía | 92% | +1% | 93% | Sube (semantic taint con Ollama) |
| 13 | Del Mundo | 91% | +0% | 91% | Estable |
| 14 | El Guardián | 65% | +17% | 82% | Sube fuerte |

**Promedio post-Sprint 70 (14 objetivos):** 93.1% (vs. 91.1% post-Sprint 69)

**Promedio excluyendo Obj #14 (comparable):** 93.9% (recuperando del 93.2% post-Sprint 69, acercándose al 94.8% pre-Guardián)

---

## Análisis Detractor por Objetivo

### Obj #1 — Crear Empresas Completas (92% → 92%)

Sprint 70 no avanza este objetivo. Llevamos **5 sprints consecutivos** (66-70) sin avance directo en la capacidad de crear empresas. El detractor señala que esto es la debilidad más seria de la serie 61-70. El Guardián, las métricas, la resiliencia — todo es infraestructura interna. Ninguno de estos sprints ha creado una empresa real ni mejorado la capacidad de hacerlo.

La buena noticia: el propio ComplianceMonitor debería detectar esta stagnation y generar una alerta. Si no lo hace, es una falla del Guardián. Si lo hace, es la primera prueba real del sistema.

**Recomendación para serie 71-80:** Los primeros 3 sprints (71-73) deben dedicarse exclusivamente a avanzar Obj #1 con una demo de creación de empresa real.

### Obj #2 — Estándar Apple/Tesla (94% → 95%)

La demo del Guardián (Épica 70.2) incluye un escenario `quality_standard_check` que valida output contra estándares. El detractor reconoce la mejora pero reitera que **no hay evaluador visual**. El LLM evaluador (Ollama) analiza HTML como texto, no como renderizado visual. Un HTML técnicamente correcto puede verse terrible en el browser. Sprint 70 no cierra este gap — queda para serie 71-80.

### Obj #3 — Mínima Complejidad (90% → 92%) — TENDENCIA REVERTIDA

Este es el logro más importante de Sprint 70. La consolidación de 18 archivos a 9, la reducción neta de ~200 líneas, y la merge de 3 tablas SQL a 1 revierten la tendencia descendente de 2 sprints. El detractor aprueba la dirección pero nota que **la consolidación es cosmética si los conceptos internos siguen siendo igual de complejos**. Tener menos archivos no significa tener menos complejidad — solo significa menos archivos. La complejidad real se mide en conceptos que un desarrollador nuevo necesita entender para contribuir.

El detractor sugiere un test: ¿puede un desarrollador que nunca ha visto el código del Guardián entender `resilience.py` en <30 minutos? Si no, la consolidación no fue suficiente.

### Obj #4 — No Equivocarse 2 Veces (96% → 97%)

La verificación diferida (Épica 70.5) cierra el último gap significativo: ahora las correcciones se verifican no solo inmediatamente sino también 24 horas después. El detractor aprueba. Este objetivo está cerca de su techo práctico.

### Obj #5 — Gasolina (91% → 92%)

La consolidación reduce el footprint de código y por tanto el costo de mantenimiento. La merge de tablas SQL reduce queries a Supabase. El detractor aprueba marginalmente pero nota que **el costo acumulado de los ciclos del Guardián (cada 6 horas) no se ha medido en producción**. La estimación de $2-5/mes es teórica. Se necesita una medición real después de 1 semana de operación.

### Obj #6 — Vanguardia (95% → 95%)

Sprint 70 no introduce patrones nuevos — consolida los existentes. Esto es aceptable para un sprint de cierre. El detractor no tiene objeciones.

### Obj #7 — No Inventar la Rueda (94% → 95%)

La deprecación de skills obsoletas (Épica 70.5) asegura que el sistema no sugiera skills con herramientas que ya no existen. Esto es "no inventar la rueda" aplicado al mantenimiento. El detractor aprueba.

### Obj #8 — Emergencia (95% → 96%)

La demo del Guardián captura comportamiento emergente al ejecutar escenarios controlados y documentar resultados inesperados. El detractor aprueba pero nota que **los escenarios de demo son predefinidos** — la emergencia real ocurre en situaciones no predefinidas. La demo valida que el sistema funciona, no que emerge.

### Obj #9 — Transversalidad (100% → 100%)

Cerrado. Sprint 70 no afecta.

### Obj #10 — Simulador (92% → 93%)

La demo del Guardián funciona como una mini-simulación del sistema. El detractor aprueba marginalmente.

### Obj #11 — Embriones (100% → 100%)

Cerrado. Sprint 70 no afecta.

### Obj #12 — Soberanía (92% → 93%)

El SemanticTaintDetector usando Ollama local (llama3.2:1b) fortalece la soberanía. La detección de injection se hace localmente, sin enviar datos a APIs externas. El detractor aprueba pero nota que **llama3.2:1b es un modelo de 1B parámetros** — su capacidad de detección semántica es limitada. Puede detectar injections obvias pero fallará con injections sutiles (jailbreaks sofisticados). Para producción real, se necesita al menos llama3.2:3b o un modelo fine-tuned.

### Obj #13 — Del Mundo (91% → 91%)

Tercer sprint consecutivo sin avance en i18n. El detractor señala que este objetivo ha estado estancado durante toda la segunda mitad de la serie (Sprints 66-70). El ComplianceMonitor debería detectar esto como stagnation.

**Recomendación para serie 71-80:** Incluir una épica de i18n en Sprint 72 o 73.

### Obj #14 — El Guardián (65% → 82%)

Sprint 70 lleva al Guardián a un nivel operativo. Con métricas automatizadas, baseline, detección de regresiones, corrección automática, verificación diferida, aprendizaje de skills, y auto-vigilancia, el Guardián tiene todas las piezas necesarias para operar. El 82% refleja que el sistema está funcional pero no maduro.

Los gaps restantes (82% → 100%):

1. **Métricas aún tienen placeholders** (~5% del gap). Algunas fuentes retornan valores estimados, no medidos.
2. **No probado en producción** (~8% del gap). La demo es en escenario controlado. El Guardián necesita operar en producción real durante al menos 1 mes para validarse.
3. **No hay feedback del usuario** (~5% del gap). El Guardián opera internamente pero no tiene mecanismo para que Alfredo valide si las correcciones fueron apropiadas.

---

## Correcciones Mandatorias

### C1 — La demo necesita escenarios NO predefinidos

**Problema:** Los 5 escenarios de demo son predefinidos. Esto valida que el código funciona, no que el sistema es robusto ante lo inesperado.

**Corrección:** Agregar un sexto escenario "chaos" que inyecta perturbaciones aleatorias (métricas con valores extremos, herramientas que fallan, latencia artificial) y verifica que el Guardián responde correctamente.

```python
DemoScenario(
    name="chaos_resilience",
    description="Inyecta perturbaciones aleatorias en métricas y herramientas. "
               "El Guardián debe detectar anomalías y no crashear.",
    setup_fn="setup_chaos",
    expected_outcome="Guardian detects anomalies, does not crash, alerts dispatched",
    objective_ids=[14, 4, 8]
)
```

### C2 — El reporte de cierre debe incluir "deuda técnica" acumulada

**Problema:** El SeriesClosureGenerator reporta logros y gaps pero no documenta la deuda técnica acumulada (TODOs, placeholders, hacks temporales).

**Corrección:** Agregar una sección de "deuda técnica" que lista todos los TODOs y placeholders en el código del Guardián.

```python
def _compute_tech_debt(self) -> list[str]:
    """Identifica deuda técnica en el código del Guardián."""
    return [
        "MetricsCollector: _get_e2e_rate() retorna valor hardcodeado",
        "MetricsCollector: _count_novel() retorna 0",
        "MetricsCollector: _determine_trend() retorna 'stable' siempre",
        "LangfuseSource: _count_regressions() retorna 0",
        "KnowledgeExtractor: _find_similar_skill() usa overlap de herramientas, no embeddings",
        "SemanticTaintDetector: usa llama3.2:1b (1B params), insuficiente para injections sutiles",
    ]
```

### C3 — Consolidación debe incluir tests de integración

**Problema:** La consolidación de 18 archivos a 9 puede romper imports y referencias. No hay tests que verifiquen que la consolidación no introdujo regresiones.

**Corrección:** Agregar tests de integración que verifican que cada componente consolidado funciona correctamente.

```python
# tests/test_guardian_integration.py
import pytest

async def test_tool_gateway_evaluates():
    """Verifica que ToolGateway evalúa invocaciones correctamente."""
    from kernel.guardian.resilience import ToolGateway, ToolInvocation, TaintLevel
    gateway = ToolGateway(policy_engine=MockPolicy())
    
    invocation = ToolInvocation(
        tool_name="web_search",
        arguments={"query": "test"},
        taint_level=TaintLevel.TRUSTED,
        origin_goal="test",
        depth_level=0
    )
    decision = await gateway.evaluate(invocation)
    assert decision.permission.value == "allow"

async def test_compliance_monitor_detects_stagnation():
    """Verifica que ComplianceMonitor detecta stagnation."""
    from kernel.guardian.compliance import ComplianceMonitor
    # ... test implementation

async def test_knowledge_extractor_creates_skill():
    """Verifica que KnowledgeExtractor crea skills."""
    from kernel.guardian.knowledge import KnowledgeExtractor
    # ... test implementation

async def test_baseline_detects_regression():
    """Verifica que BaselineManager detecta regresiones."""
    from kernel.guardian.metrics import BaselineManager
    # ... test implementation
```

### C4 — Mecanismo de feedback de Alfredo para correcciones del Guardián

**Problema:** El Guardián opera internamente sin feedback del usuario. Las correcciones HIGH risk se escalan a HITL pero no hay mecanismo para que Alfredo diga "esta corrección fue buena" o "esta corrección fue mala".

**Corrección:** Agregar un endpoint `/guardian/feedback` que permite a Alfredo aprobar/rechazar correcciones pasadas, y usar ese feedback para ajustar la confianza del SelfCorrectionEngine.

```python
@router.post("/guardian/feedback")
async def submit_feedback(correction_id: str, approved: bool, notes: str = ""):
    """Alfredo da feedback sobre una corrección del Guardián."""
    correction = await correction_store.get(correction_id)
    if not correction:
        return {"error": "Correction not found"}
    
    # Ajustar confianza basado en feedback
    if approved:
        correction.confidence = min(0.95, correction.confidence + 0.1)
    else:
        correction.confidence = max(0.1, correction.confidence - 0.2)
    
    await correction_store.update(correction)
    
    # Crear experiencia para KnowledgeExtractor
    experience = TaskExperience(
        task_id=f"feedback_{correction_id}",
        task_type="correction_feedback",
        outcome="success" if approved else "failure",
        ...
    )
    await knowledge_extractor.evaluate(experience)
    
    return {"status": "feedback_recorded", "new_confidence": correction.confidence}
```

---

## Veredicto Final

Sprint 70 cumple su triple responsabilidad como sprint de cierre de serie:

1. **Cierra gaps:** La consolidación revierte Obj #3, la verificación diferida cierra C2-Sprint 69, la deprecación de skills cierra C4-Sprint 69, y el semantic taint cierra C6-Sprint 68.

2. **Demuestra el sistema:** La demo E2E del Guardián ejecuta 5 escenarios controlados que validan el ciclo completo de mejora continua.

3. **Prepara el terreno:** El reporte de cierre documenta el estado de los 14 objetivos y genera recomendaciones concretas para la serie 71-80.

Sin embargo, el sprint tiene 3 debilidades:

1. **Demo predefinida** (no prueba resiliencia ante lo inesperado)
2. **Sin feedback humano** (el Guardián opera en vacío sin validación de Alfredo)
3. **Consolidación sin tests** (puede romper cosas silenciosamente)

Las 4 correcciones mandatorias (C1-C4) abordan estos problemas. Con las correcciones aplicadas, el score sube de 7.5/10 a 9.0/10 — el más alto de los 3 sprints del Guardián.

---

## Balance de la Serie 61-70

| Métrica | Inicio Serie (Sprint 60) | Fin Serie (Sprint 70) | Delta |
|---|---|---|---|
| Promedio 13 Objetivos (sin #14) | 87.8% | 93.9% | +6.1% |
| Promedio 14 Objetivos (con #14) | N/A | 93.1% | N/A |
| Objetivos en 100% | 2 (#9, #11) | 2 (#9, #11) | = |
| Objetivos ≥95% | 0 | 5 (#2, #4, #6, #7, #8) | +5 |
| Objetivos ≥90% | 5 | 12 | +7 |
| Objetivos <90% | 8 | 2 (#14 en 82%, #13 en 91%) | -6 |
| Obj #14 (Guardián) | No existía | 82% | NUEVO |
| Correcciones mandatorias totales | — | 18 (8+6+4) | — |
| Líneas de código netas (Guardián) | 0 | ~1,800 | — |

La serie 61-70 logró su objetivo principal: **llevar al sistema de "funcional" a "maduro"**. El Guardián (Obj #14) es la adición más significativa — un meta-sistema que garantiza que los otros 13 objetivos se cumplan perpetuamente.

---

## Recomendaciones para Serie 71-80: "Autonomía Completa"

1. **Sprints 71-73:** Avanzar Obj #1 (Crear Empresas) con demo de empresa real. 5 sprints sin avance es inaceptable.
2. **Sprint 72:** Avanzar Obj #13 (Del Mundo) con i18n real. 5 sprints estancado.
3. **Sprint 74:** Madurar Obj #14 (Guardián) eliminando placeholders y midiendo en producción real.
4. **Sprint 75:** Implementar evaluador visual (screenshot comparison) para Obj #2.
5. **Sprint 76-80:** Autonomía completa — el sistema debe operar sin intervención humana para tareas rutinarias.
