# DIMENSIONES: AUTHORITY, RISK, RUNTIME

Para lograr una codificación verdaderamente matemática y "no-hint", los conceptos operativos más críticos deben proyectarse como coordenadas numéricas exactas, eliminando la necesidad de explicaciones textuales.

## 1. Eje de Autoridad (Authority Axis)
Basado directamente en la Escalera de Autonomía A0-A8.
*   **Vector:** $c_{auth} \in [0, 8]$
*   **Mapeo:**
    *   $0$: Observer (Read-only)
    *   $3$: Self-Evolution R1 (Safe environment)
    *   $8$: Kernel Modification (T1 only)

## 2. Eje de Riesgo (Risk Axis)
Clasificación de la severidad del impacto si la partícula falla o actúa maliciosamente.
*   **Vector:** $c_{risk} \in [0, 3]$
*   **Mapeo:**
    *   $0$: P0 (Riesgo Crítico - Ej. Split Brain, Loop Storm)
    *   $1$: P1 (Riesgo Alto - Ej. Pérdida de contexto)
    *   $2$: P2 (Riesgo Moderado)
    *   $3$: P3 (Riesgo Bajo - Safe to fail)

## 3. Eje de Permiso de Ejecución (Runtime Permission)
Control binario sobre la capacidad de ejecutar código o alterar el estado del sistema host.
*   **Vector:** $c_{runtime} \in \{0, 1\}$
*   **Mapeo:**
    *   $0$: `NO_RUNTIME` (Bloqueado. Solo simulación o planificación).
    *   $1$: `RUNTIME_ALLOWED` (Puede ejecutar scripts/comandos).

## Intersección Dimensional
Una partícula $p_i$ que representa a un "Auditor de Código" podría tener las coordenadas:
$$ \mathbf{C}_i = [c_{auth}=2, c_{risk}=1, c_{runtime}=0] $$
La IA receptora lee `[2, 1, 0]` y sabe inmediatamente: "Tengo permiso para leer (A2), mi fallo causaría problemas altos (P1), pero no puedo ejecutar el código que estoy auditando (Runtime=0)". No se requiere texto explicativo.
