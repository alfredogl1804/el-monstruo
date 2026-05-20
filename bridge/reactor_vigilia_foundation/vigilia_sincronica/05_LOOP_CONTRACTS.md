# Loop Contracts

## Definición
Cada loop opera bajo un contrato estricto que define sus límites. Este contrato es evaluado por el Policy Engine.

## Componentes del Contrato
- **Max Autonomy Level:** (Ej. A1, A3, A5). El loop no puede proponer eventos que requieran un nivel mayor.
- **Input Read:** Qué partes del State Fabric puede leer.
- **Event Emitted:** Qué tipos de eventos puede proponer (`event_type`).
- **No Side Effects:** (Para loops A0-A4). Promesa de no tocar APIs externas o bases de datos productivas.
- **Next Suggested Loop:** A quién sugiere el loop que el Dispatcher llame a continuación (o STOP).

## Violación de Contrato
Cualquier intento de exceder el contrato resulta en un `REJECT` por parte del Dispatcher/Reducer y la terminación del loop.
