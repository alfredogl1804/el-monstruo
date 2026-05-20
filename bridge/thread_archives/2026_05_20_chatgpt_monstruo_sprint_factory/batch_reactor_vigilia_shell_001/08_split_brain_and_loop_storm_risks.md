# Riesgos en Vigilia Sincrónica

## Split-Brain
**Definición:** Dos loops creen tener la verdad y escriben estados divergentes.
**Mitigación:** State Fabric single-writer. Solo el Dispatcher/Reducer consolida el estado.

## Loop Storm
**Definición:** Un loop activa a otro infinitamente en un ciclo sin fin.
**Mitigación:** Coreografía radial. Los loops no se llaman entre sí directamente. El Dispatcher controla el flujo y puede forzar un STOP.

## Autonomy Creep
**Definición:** Un loop A2 empieza a tomar decisiones nivel A5.
**Mitigación:** Loop Contracts estrictos validados por el Policy Engine en el Dispatcher.

## Cost Runaway
**Definición:** Consumo descontrolado de tokens/LLMs.
**Mitigación:** Límites de ciclos por sesión de Vigilia.
