# 02 POLICY ENGINE PRINCIPLES

## Estado
- SPRINT_CANDIDATE_R0
- DOCTRINE_CANDIDATE

## Reglas de Evaluación de Permisos

El Policy Engine no es solo una tabla estática; es un conjunto de principios que se evalúan dinámicamente antes de cada acción (Preflight Check).

### 1. El permiso real es una intersección
Tener `R1_UNLOCKED` no otorga autonomía ilimitada. El permiso real para ejecutar una acción es la intersección de:
- Aprobación T1 (si aplica).
- Nivel máximo de autonomía del loop (`max_autonomy_level`).
- Allowlist de paths (si la acción involucra I/O).
- Clase de riesgo de la acción.
- Estado actual en el State Fabric.
- Gates de validación (ej. auditor independiente).

### 2. Declaración obligatoria
Todo loop debe declarar su `max_autonomy_level` al ser instanciado por el Dispatcher (mediante el Loop Contract). Un loop no puede elevar su propio nivel de autonomía bajo ninguna circunstancia.

### 3. Mapeo estricto de acciones
Toda acción que el Monstruo pueda ejecutar debe estar registrada en el `action_registry_v0.yaml` y mapeada a un nivel mínimo requerido (A0-A8). Si una acción no está en el registro, se asume nivel A8 por defecto (bloqueada).

### 4. Trazabilidad obligatoria (A3+)
Toda acción que requiera nivel A3 o superior debe dejar un registro indeleble en el Event Log (Append-Only). No hay modificaciones silenciosas de estado persistente.

### 5. Segregación de funciones (A4+)
Para acciones de nivel A4 o superior (ej. preparar un PR), el loop auditor que revisa el trabajo no puede pertenecer al mismo linaje de ejecución que el loop creador.

### 6. Decisión T1 visible (A6+)
Toda acción de nivel A6 o A7 requiere una decisión explícita y visible de T1. La firma de T1 debe quedar registrada en el State Fabric o en un archivo de aprobación antes de que el Dispatcher autorice la ejecución.

### 7. Metadata vs. Permiso
El campo `allowed_actions` en un prompt o contexto es solo metadata. No otorga permisos reales hasta que el Policy Engine lo evalúa y lo convierte en una autorización explícita durante el Preflight Check.
