---
name: ciclo-investigacion-descubrimiento-perpetuo
description: Sistema de descubrimiento continuo gobernado por evidencia, validación y convergencia. Toma cualquier software/plataforma existente, la investiga a profundidad en 19+ dimensiones, y ejecuta un ciclo iterativo perpetuo orquestado por GPT-5.4 para diseñar y construir una versión 10x superior. Integra los 6 Sabios con roles especializados, validación en tiempo real por Manus, memoria jerárquica externa, y broker de GPUs para entrenamiento. Usar cuando se necesite analizar un software existente, descubrir mejoras, diseñar una alternativa superior, o ejecutar un ciclo de investigación-diseño-construcción iterativo.
---

# Ciclo de Investigación y Descubrimiento Perpetuo (CIDP) v1.2

## Propósito

CIDP es un motor de convergencia medible que transforma investigación infinita en mejora finita y verificable. Toma un software, aplicación o plataforma existente, la investiga al 100% en 19+ dimensiones, descubre mejoras en tiempo real, y ejecuta un ciclo iterativo perpetuo orquestado por GPT-5.4 como Arquitecto para diseñar y construir una versión 10x superior.

> **Principio rector:** Investigación infinita debe producir mejora finita y medible. El ciclo no es "perpetuo" en sentido literal, sino continuo pero gobernado por compuertas de convergencia, presupuesto y evidencia.

## Reglas Inquebrantables

1. **PROHIBIDO** asumir capacidades no verificadas de los modelos IA. Los roles se asignan por benchmark interno, no por reputación.
2. **OBLIGATORIO** usar `run_cidp.py` como entrypoint. Orquesta los 7 stages automáticamente.
3. **OBLIGATORIO** aplicar el protocolo `anti-autoboicot` en cada iteración del ciclo.
4. **PROHIBIDO** hardcodear proveedores de infraestructura ni pricing. Todo pasa por el `gpu_broker` con consulta en tiempo real.
5. **OBLIGATORIO** definir "10x" como score compuesto medible antes de iniciar el ciclo.
6. **PROHIBIDO** continuar una iteración si el Convergence Gate la rechaza.
7. Cada iteración genera artefactos versionados en `data/`.

## Arquitectura del Bucle (7 Stages)

```
Stage 1: Intake & Scope
    ↓
Stage 2: Deep Research Mesh (19+ dimensiones)
    ↓
Stage 3: Synthesis Core (GPT-5.4 como Arquitecto)
    ↓
Stage 4: Swarm Execution (Sabios con roles especializados)
    ↓
Stage 5: Reality Validation Loop (Manus + anti-autoboicot)
    ↓
Stage 6: Build / Prototype / Eval
    ↓
Stage 7: Convergence Gate
    ↓
[Si no converge → Stage 3 con nueva evidencia]
[Si converge → Entrega final]
```

## Los Roles en el Ciclo

| Actor | Rol | Responsabilidad |
|-------|-----|-----------------|
| GPT-5.4 | Arquitecto/Orquestador | Sintetiza evidencia, prioriza backlog, delega tareas, define North Star por iteración |
| Claude 4.6/4.7 | Arquitecto Profundo | Arquitectura de software, calidad de código, detección de patrones anti-autoboicot |
| Gemini 3.1 | Verificador/Evaluador | Google Search grounding, verificación factual, evaluación de UX/visión |
| Grok 4.20 | Contrarian/Estratega | Revisión adversarial, detección de debilidades, estrategia de producto |
| DeepSeek R1 | Optimizador/Código | Optimización de rendimiento, generación de código, análisis de costos |
| Perplexity Sonar | Investigador en Tiempo Real | Grounding factual, investigación de mercado, precios actuales |
| Manus | Validador Activo | Extrae claims, triangula fuentes, verifica frescura, rechaza obsoleto |

**Nota:** Los roles son provisionales y benchmark-driven. La primera iteración incluye una fase de calibración donde se evalúan las capacidades reales de cada modelo.

## Las 19+ Dimensiones de Investigación

| # | Dimensión | Descripción |
|---|-----------|-------------|
| 1 | Funcionalidad | Features, completitud, edge cases |
| 2 | Robustez | Manejo de errores, resiliencia, recovery |
| 3 | Escalabilidad | Horizontal, vertical, límites |
| 4 | Seguridad | Vulnerabilidades, autenticación, cifrado |
| 5 | Estética/UI | Diseño visual, consistencia, modernidad |
| 6 | UX/Accesibilidad | Flujos de usuario, a11y, inclusividad |
| 7 | Arquitectura/Deuda Técnica | Patrones, acoplamiento, mantenibilidad |
| 8 | Datos/IA/Grounding/Evals | Modelos, datasets, evaluaciones |
| 9 | Observabilidad/Operaciones | Logging, monitoring, alertas |
| 10 | Cumplimiento Regulatorio | GDPR, AI Act, NIS2 por fase/obligación |
| 11 | Licencias/PI | Open source, patentes, ToS |
| 12 | Economía/FinOps | Costos de infra, ROI, TCO |
| 13 | Modelo de Negocio | Monetización, pricing, unit economics |
| 14 | Ecosistema/Integraciones | APIs, plugins, marketplace |
| 15 | DX/Extensibilidad | SDK, docs, onboarding de devs |
| 16 | Posicionamiento Competitivo | Market share, diferenciadores |
| 17 | Riesgo Estratégico | Vendor lock-in, dependencias, obsolescencia |
| 18 | Sostenibilidad/Eficiencia | Consumo energético, eficiencia operativa |
| 19 | Palancas 10x del Dominio | Oportunidades específicas del sector |

## Ejecución

```bash
cd /home/ubuntu/skills/ciclo-investigacion-descubrimiento-perpetuo/scripts

# Ciclo completo
python3.11 run_cidp.py \
    --target "Nombre del software/plataforma a investigar" \
    --objective "Descripción del objetivo 10x" \
    --output-dir /ruta/salida/ \
    --max-iterations 10 \
    --budget-usd 50.0

# Solo investigación (sin build)
python3.11 run_cidp.py \
    --target "Software X" \
    --objective "Investigar al 100%" \
    --output-dir /ruta/salida/ \
    --research-only

# Con GPU broker habilitado
python3.11 run_cidp.py \
    --target "Software X" \
    --objective "Construir versión 10x" \
    --output-dir /ruta/salida/ \
    --enable-gpu-broker \
    --gpu-budget-usd 100.0
```

Opciones adicionales:
- `--max-iterations N` — Límite de iteraciones del ciclo (default: 10)
- `--budget-usd N` — Presupuesto máximo en USD para APIs (default: 50)
- `--research-only` — Solo ejecuta investigación, sin build
- `--skip-calibration` — Salta la calibración de sabios (solo si ya existe)
- `--enable-gpu-broker` — Habilita renta de GPUs para entrenamiento
- `--gpu-budget-usd N` — Presupuesto máximo para GPUs (default: 100)
- `--convergence-threshold N` — Umbral de convergencia 0-1 (default: 0.8)
- `--dimensions "dim1,dim2,..."` — Limitar dimensiones de investigación

## Scripts (16 archivos)

### Core (7)

| Script | Función | API |
|--------|---------|-----|
| run_cidp.py | Entrypoint orquestador del ciclo completo | — |
| cidp_intake.py | Normaliza input, clasifica software, define scope y métricas 10x | GPT-5.4 |
| cidp_research.py | Deep Research Mesh: investigación paralela en 19+ dimensiones | Perplexity + Manus search |
| cidp_orchestrator.py | Synthesis Core: GPT-5.4 sintetiza, prioriza y delega | GPT-5.4 |
| cidp_swarm.py | Swarm Execution: distribuye tareas a Sabios especializados | consulta-sabios |
| cidp_validator.py | Reality Validation Loop: anti-autoboicot, grounding, contradicciones | Manus + Perplexity + Gemini |
| cidp_convergence.py | Convergence Gate: evalúa si continuar o entregar | GPT-5.4 |

### Build & Infra (4)

| Script | Función | API |
|--------|---------|-----|
| cidp_builder.py | Genera specs, prototipos, código, tests | GPT-5.4 + Claude |
| cidp_evals.py | Evalúa la solución contra función objetivo 10x | Multi-modelo |
| gpu_broker.py | Broker de infraestructura: renta/gestión de GPUs | Vast.ai API + RunPod API |
| cidp_infra.py | Deploy, monitor de costos, teardown | Local + APIs |

### Memoria & Inteligencia (5)

| Script | Función | API |
|--------|---------|-----|
| cidp_memory.py | Facts Graph, Decision Log, Contradiction Ledger, Artifact Store | SQLite local |
| cidp_calibrator.py | Calibración de sabios: benchmark interno de capacidades reales | Multi-modelo |
| cidp_score.py | Función objetivo 10x: score compuesto configurable | Local |
| cidp_compliance.py | Policy engine: gates regulatorios por obligación y fecha | Perplexity |
| cidp_telemetry.py | Métricas por iteración: tokens, costo, convergencia, tiempo | Local |

## Artefactos por Iteración

| Artefacto | Formato | Descripción |
|-----------|---------|-------------|
| scope.md | Markdown | Definición de alcance y guardrails |
| success_metrics.json | JSON | Función objetivo 10x con pesos |
| research_cards.json | JSON | Hallazgos por dimensión con score de confianza |
| evidence_pack.json | JSON | Evidencia estructurada con fuentes |
| contradictions.json | JSON | Contradicciones detectadas y resolución |
| north_star_spec.md | Markdown | Especificación de la iteración por GPT-5.4 |
| task_delegations.json | JSON | Asignaciones a cada Sabio |
| sabios_responses.json | JSON | Respuestas de los Sabios |
| validation_report.json | JSON | Informe de validación de Manus |
| build_plan.json | JSON | Plan de construcción |
| eval_results.json | JSON | Resultados de evaluación |
| decision_log.json | JSON | Log de decisiones con justificación |
| convergence_report.json | JSON | Reporte del gate de convergencia |

## Memoria Jerárquica Externa

CIDP no depende del contexto máximo del LLM. Implementa tres niveles de memoria:

1. **Memoria Permanente** (facts_store.db): Hechos verificados, decisiones tomadas, contradicciones resueltas. Persiste entre iteraciones y entre ejecuciones.
2. **Memoria de Trabajo** (working_memory/): Contexto de la iteración actual. Se comprime al finalizar cada iteración.
3. **Memoria Histórica** (history/): Resúmenes de iteraciones anteriores, accesibles bajo demanda. Permite al orquestador recordar sin saturar el contexto.

## GPU Broker

El módulo `gpu_broker.py` gestiona la renta dinámica de GPUs:

| Proveedor | Adaptador | Status |
|-----------|-----------|--------|
| Vast.ai | vastai_adapter | Primario |
| RunPod | runpod_adapter | Fallback |
| CoreWeave | coreweave_adapter | Futuro |
| Lambda | lambda_adapter | Futuro |

Selección por política configurable: precio, disponibilidad, reputación, riesgo de preemption, cumplimiento.

## Configuración

- `config/cidp_config.yaml` — Configuración general del ciclo
- `config/dimensions.yaml` — Definición de las 19+ dimensiones
- `config/score_weights.yaml` — Pesos de la función objetivo 10x
- `config/gpu_policy.yaml` — Políticas del GPU broker
- `config/compliance_rules.yaml` — Reglas regulatorias por normativa y fecha

## Dependencias

- **consulta-sabios** v2.1+ en `/home/ubuntu/skills/consulta-sabios/`
- **anti-autoboicot** en `/home/ubuntu/skills/anti-autoboicot/`
- **api-context-injector** v4.0+ en `/home/ubuntu/skills/api-context-injector/`

Variables de entorno: `OPENAI_API_KEY`, `SONAR_API_KEY`, `OPENROUTER_API_KEY`, `GEMINI_API_KEY`, `XAI_API_KEY`.

Opcional para GPU broker: `VASTAI_API_KEY`, `RUNPOD_API_KEY`.

## Ciclo de Mejora Perpetua

Cada ejecución del ciclo alimenta automáticamente:
1. `data/execution_history.jsonl` — Historial de ejecuciones
2. `data/calibration_results.json` — Calibración de sabios
3. `data/convergence_trends.jsonl` — Tendencias de convergencia
4. `data/cost_tracking.jsonl` — Tracking de costos
5. `data/pattern_library.jsonl` — Patrones reutilizables

## Diseñado por

Arquitectura co-diseñada por el Consejo de 6 Sabios (GPT-5.4, Claude Sonnet 4.6, Gemini 3.1 Pro, Grok 4.20 Reasoning, DeepSeek R1, Perplexity Sonar Reasoning Pro) el 16 de abril de 2026. Validado con Paso 7 post-síntesis (score global: 0.91, factual: 0.86, incorporación: 1.0).

## Historial de Versiones y Lecciones Aprendidas

### v1.1 (Post-Test Extremo)
**Fecha:** 16 de Abril, 2026
**Target de Prueba:** Notion
**Mejoras Implementadas:**
1. **Resiliencia de F-Strings (Stage 6):** Se corrigió un bug crítico donde la inyección de JSON dentro de f-strings en Python causaba un `TypeError: unhashable type: 'dict'`. Ahora los JSON se pre-formatean en variables independientes.
2. **Maximización de Presupuesto de Validación (Stage 5):** La lógica de extracción de *claims* se actualizó. Si los Sabios no generan suficientes afirmaciones dudosas (`needs_validation`), el sistema rellena el batch de verificación (hasta 25 claims) con afirmaciones explícitas (`explicit`) para aprovechar al máximo el costo de la llamada a Perplexity y garantizar mayor rigor factual.
3. **Graceful Degradation:** Se implementaron bloques `try/except` alrededor de la invocación de cada uno de los 7 stages en `run_cidp.py`. Si un stage falla (ej. timeout de API), el ciclo no crashea; registra el error en la memoria, devuelve un *fallback* seguro, y permite que el *Convergence Gate* decida si abortar o reintentar en la siguiente iteración.

**Lección del Test:** El pipeline *Anti-Autoboicot* (Stage 5) demostró ser vital. Durante el test contra Notion, detectó y rechazó 5 afirmaciones arquitectónicas propuestas por los Sabios que estaban desactualizadas respecto a la realidad actual del software, previniendo que el Stage 6 construyera sobre premisas falsas.

### v1.2 (Hardening P0 + Handoff Desacoplado)
**Fecha:** 16 de Abril, 2026
**Motivación:** Plan estratégico de los 6 Sabios para preparar el CIDP como microservicio autónomo, evitando colisión con el Hilo A (construcción del Monstruo).

**Mejoras Implementadas:**

1. **Sistema de Checkpointing (SQLite):** Nueva tabla `checkpoints` en `cidp_memory.db` con métodos `save_checkpoint()`, `get_checkpoint()` y `get_latest_checkpoint()`. Cada stage (2-6) guarda su resultado al completarse. Si el proceso crashea, al reiniciar detecta el último checkpoint exitoso y reanuda desde ahí sin repetir trabajo. Clave única `(run_id, iteration, stage)` garantiza idempotencia.

2. **Budget Guards Mejorados:** El mensaje de corte de presupuesto ahora muestra el costo acumulado vs. el presupuesto asignado para diagnóstico inmediato. La verificación ocurre al inicio de cada iteración, antes de gastar tokens adicionales.

3. **Idempotencia y Resume por Stage:** La lógica del bucle iterativo ahora evalúa `resume_stage` para cada stage. Si un stage ya fue completado en la iteración actual (checkpoint existe), se salta y carga el resultado desde SQLite. Si el checkpoint no existe pero debería (inconsistencia), fuerza la re-ejecución de ese stage.

4. **Rollback en Stage 6 (Build):** Si el Stage 6 falla con GPUs activas, se dispara un rollback que marca la iteración como fallida y señaliza teardown de recursos antes de abortar.

5. **Contrato OpenAPI 3.1 para el Kernel:** Se generó `openapi.yaml` con endpoints REST (`/jobs`, `/jobs/{id}`, `/jobs/{id}/resume`) para que el Hilo A (El Monstruo) pueda consumir el CIDP como un worker desacoplado.

6. **Cliente Python Asíncrono:** `cidp_client.py` basado en `aiohttp`, listo para inyectar en un nodo de LangGraph con `start_job()`, `get_status()`, `cancel_job()`, `resume_job()` y `wait_for_completion()`.

7. **Documentación Operativa:** `STATE_MACHINE.md`, `RUNBOOK.md` y `HANDOFF_TO_KERNEL.md` para operación, depuración e integración.

**Tests Unitarios:** 6/6 tests del sistema de checkpointing pasaron exitosamente (save, upsert, latest, non-existent, failed status, budget guard logic).

**Validación:** 16/16 scripts Python pasan syntax check. 5/5 archivos YAML parsean correctamente.
