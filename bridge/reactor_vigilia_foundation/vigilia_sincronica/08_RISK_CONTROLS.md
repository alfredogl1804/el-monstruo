# Controles de Riesgo (Vigilia Sincrónica)

| Riesgo | Descripción | Control en Vigilia Sincrónica |
|---|---|---|
| **Split-brain** | Dos loops creen tener la verdad y escriben estado divergente. | State Fabric single-writer. Dispatcher es el único que consolida estado. |
| **Loop storm** | Un loop activa a otro infinitamente. | Coreografía radial. Los loops no se llaman entre sí. Dispatcher decide. |
| **Dory distribuido** | El contexto se pierde entre saltos. | Handoff Packet estricto. Si falta contexto, el loop aborta. |
| **F16 multi-loop** | Todos los loops intentan ser el líder. | Unified Face es el único output al usuario. Contratos estrictos por loop. |
| **Memory contamination** | Un loop alucina y ensucia el estado global. | Event log append-only. Reducer audita eventos antes de mutar `current_state`. |
| **False life** | El sistema corre vacío consumiendo recursos. | Heartbeat policies (Ej. `every_5_min`, `on_demand`). |
| **Autonomy creep** | Un loop A2 empieza a ejecutar acciones A5. | Policy Engine (Preflight Check) rechaza propuestas fuera de contrato. |
| **Cost runaway** | Ejecución descontrolada de LLMs. | Dispatcher limita el número de loops por ciclo de Vigilia. |
| **Audit difficulty** | Imposible saber por qué el sistema hizo algo. | Event Log inmutable con `source_loop` y `source_lineage`. |
| **Rubber-stamping** | Auditor aprueba todo ciegamente. | Regla de linaje: Un loop no puede auditar eventos de su propio linaje. |
