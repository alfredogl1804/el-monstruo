# VIGILIA SINCRÓNICA / MONSTRUO MULTINÚCLEO

**Estado:** DOCTRINE_CANDIDATE_HIGH_ORDER
**Nota:** NO runtime. NO R1. NO APP_VISION. NO PRE-IA close.

## 1. Tesis Central
El Monstruo no es un hilo inmortal. Ningún modelo de lenguaje actual puede mantener un contexto infinito sin degradarse. La solución no es buscar la inmortalidad del hilo, sino la sincronización perfecta de hilos mortales.

La Vigilia Sincrónica es la arquitectura que permite que el Monstruo parezca un ente continuo y omnisciente para el usuario, cuando en realidad es una coreografía de loops finitos, especializados y efímeros.

## 2. La Fórmula Corregida
`Unified Face + Rotor/Dispatcher + State Fabric single-writer + Event Log append-only + Loops de corta vida + Handoff Protocol + T1 humano.`

El principio rector es: **"Un solo rostro, muchas mentes, una memoria soberana, una autoridad humana."**

## 3. Componentes Clave

### 3.1. Unified Face (El Rostro Único)
El usuario (Alfredo T1) nunca habla con los loops internos. Solo interactúa con la Unified Face. Esta capa recibe el input, lo pasa al Dispatcher, y luego consolida las respuestas de los loops para presentar una salida coherente.

### 3.2. Rotor / Dispatcher (El Sincronizador)
Es el enrutador central. Recibe eventos y decide qué loop debe despertar. No ejecuta tareas, solo delega. Conoce el `loop_registry` y respeta la escalera de autonomía (A0-A8).

### 3.3. State Fabric (Memoria Soberana)
Es la fuente única de verdad del sistema. Almacena el contexto actual, las misiones activas y el estado de los loops.
**Regla de Oro:** Es *single-writer*. Solo un proceso (el State Reducer) puede modificar el State Fabric basándose en el Event Log. Los loops solo tienen acceso de lectura (read-only) al State Fabric.

### 3.4. Loops (Mentes Especializadas)
Son hilos de IA con propósitos específicos (ej. Vigía, Oráculo, Auditor). Nacen, leen el State Fabric, ejecutan su tarea, emiten un evento al Event Log, y mueren. Tienen un contrato estricto de I/O.

### 3.5. T1 (Autoridad Humana)
Alfredo es la única autoridad (T1). Puede intervenir en cualquier momento como un evento en el runtime (PAUSE, REDIRECT, KILL) sin necesidad de reiniciar el sistema.

## 4. Riesgos P0 Mitigados

- **Split-Brain:** Evitado por la regla single-writer del State Fabric.
- **Loop Storm:** Evitado porque los loops no pueden invocarse entre sí directamente; todo pasa por el Dispatcher.
- **F16 Multi-Loop:** Evitado por la coreografía radial (no es una mesh libre).
- **Dory Distribuido:** Evitado porque el Handoff Protocol asegura que el contexto vital se serialice en el Event Log antes de que un loop muera.
