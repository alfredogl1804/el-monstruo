# Reglas de Riesgo para Sprint Candidates

**SPRINT:** SPR-RISK-CLASSIFICATION-001
**Estado:** DOCTRINE_CANDIDATE

Un Sprint Candidate es una propuesta de trabajo futuro generada por el Oráculo. Para que el Dispatcher pueda evaluar si permite la ejecución de un sprint, este debe tener un `required_autonomy_level` explícito.

## Derivación de Autonomía Requerida

El `required_autonomy_level` de un Sprint Candidate se deriva directamente del `risk_class` del Power Stack que pretende implementar y de las acciones específicas que propone realizar durante el sprint.

1. **Analizar Capacidades Usadas:** Identificar el riesgo máximo de las capacidades involucradas.
2. **Analizar Acciones Propuestas:** Mapear las acciones propuestas contra el `action_registry_v0.yaml`.
3. **Analizar Paths Tocados:** Verificar si el sprint requiere escribir en rutas protegidas (ej. `src/`, `kernel/`).
4. **Analizar Necesidad de APIs/Secrets:** Si requiere secrets reales, el nivel mínimo es A7.

## Mapeo Base (Risk Class -> Autonomy Level)

- **R0 (Estático):** Requiere **A0** o **A1**. El sprint solo puede generar discusiones teóricas o especificaciones sin ejecución.
- **R1 (Lectura Pública):** Requiere **A2**. El sprint puede generar reportes basados en lectura de APIs públicas.
- **R2 (Lectura Sensible):** Requiere **A3**. El sprint puede generar reportes basados en datos privados, pero no modificar nada fuera de `doctrine_candidates/`.
- **R3 (Escritura Limitada):** Requiere **A3**. El sprint puede escribir artefactos persistentes no productivos.
- **R4 (Escritura de Código):** Requiere **A4** (para drafts/PRs) o **A5** (para escritura directa en sandbox).
- **R5 (Modificación de Sistema):** Requiere **A7** o **A8**. El sprint toca componentes críticos y requiere aprobación T1 explícita (`t1_required: true`).

## Prevención de Autonomy Creep

El Oráculo no puede usar la aprobación de su propio sprint de descubrimiento (SPR-ORACLE-AI-001) como permiso implícito para ejecutar los Sprint Candidates que propone. Cada candidato debe ser evaluado de forma independiente por el Dispatcher y, si supera el nivel A3, requiere aprobación T1 para ser promovido a un sprint activo.
