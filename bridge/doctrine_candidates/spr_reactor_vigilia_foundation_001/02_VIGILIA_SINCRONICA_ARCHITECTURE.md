# 02 VIGILIA SINCRONICA ARCHITECTURE

## Estado
- SPRINT_CANDIDATE_R0
- DOCTRINE_CANDIDATE

## Principio Arquitectónico
"Un solo rostro, muchas mentes, una memoria soberana, una autoridad humana."
Topología: Coreografía radial (no mesh libre).

## Componentes del Sistema

### 1. Unified Face (El Rostro)
- Interfaz única para T1 (Alfredo).
- Enmascara la creación y destrucción de loops.
- Maneja el protocolo de intervención viva (PAUSE, RESUME, REDIRECT).

### 2. Dispatcher / Rotor
- Orquestador central.
- Lee la Dual Task Queue.
- Crea loops, asigna contratos (Loop Contract), define TTL (Time-To-Live).
- Monitorea heartbeats. Mata loops zombis.

### 3. Loop Registry
- Catálogo en memoria de loops activos.
- Registra: `loop_id`, `type`, `status`, `autonomy_level`, `ttl`, `assigned_task`.

### 4. Loops Finitos (Las Mentes)
- Instancias efímeras de ejecución (ej. un agente Manus, un script Python).
- Stateless por diseño. Nacen, leen el State Fabric, ejecutan, escriben resultado, mueren.

## Flujo de Vida de un Loop
1. Dispatcher lee tarea de la queue.
2. Dispatcher instancia Loop X con Contrato Y.
3. Loop X lee State Fabric (contexto necesario).
4. Loop X ejecuta. Emite heartbeats al Dispatcher.
5. Loop X termina. Escribe output en State Fabric / Event Log.
6. Dispatcher destruye Loop X.

## Mitigación de Riesgos
- **Split-Brain:** Resuelto porque el State Fabric es la única fuente de verdad.
- **Loop Storm:** Resuelto por límites de concurrencia en el Dispatcher.
- **Dory Distribuido:** Resuelto por el Handoff Protocol obligatorio al morir un loop.
