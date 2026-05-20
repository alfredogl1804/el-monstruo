# State Fabric Single-Writer

## Concepto
El "State Fabric" es la memoria a corto plazo y el estado operativo del Monstruo. Para evitar la contaminación de memoria (memory contamination) y cerebros divididos (split-brain), debe ser "single-writer".

## Reglas
1. Los loops individuales **no pueden** escribir directamente en el `current_state`.
2. Los loops solo pueden emitir `event_proposals`.
3. Un único componente (el Dispatcher/Reducer) procesa los eventos y muta el State Fabric de forma serializada.
4. Si un loop alucina, su propuesta puede ser rechazada antes de contaminar el estado global.
