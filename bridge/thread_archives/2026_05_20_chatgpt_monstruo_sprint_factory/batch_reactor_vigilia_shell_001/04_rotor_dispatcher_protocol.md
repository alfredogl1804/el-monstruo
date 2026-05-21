# Rotor / Dispatcher Protocol

## Concepto
El Dispatcher (o Rotor) es el orquestador central de la Vigilia Sincrónica. Es el único componente que sabe qué loop debe ejecutarse a continuación.

## Responsabilidades
1. Despertar a los loops en el orden correcto (Coreografía radial, no mesh libre).
2. Empacar el contexto en el Handoff Packet.
3. Recibir el Loop Output.
4. Aplicar el Reducer a las propuestas de eventos para mutar el State Fabric.
5. Terminar el ciclo (STOP) o pasar al siguiente loop.
6. Aplicar el Policy Engine (Autonomy Ladder) para evitar autonomy creep.
