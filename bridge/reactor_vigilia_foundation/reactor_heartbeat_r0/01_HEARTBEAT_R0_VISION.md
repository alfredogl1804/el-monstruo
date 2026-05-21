# VISION: Heartbeat R0

## El Primer Latido Controlado

**Frase Doctrinal:**
> "El Monstruo deja de ser herramienta cuando tiene pulso propio; pero un pulso propio no equivale a autonomía ilimitada."

El Heartbeat R0 es el primer latido local y controlado del Monstruo. Es una ejecución única (one-shot) que permite al sistema:
1. **Despertar:** Leer su estado actual (State Fabric, Vigilia, Riesgos).
2. **Evaluar:** Determinar si hay trabajo seguro (R0) pendiente.
3. **Actuar (o no):** Ejecutar una acción segura o decidir que no hay nada que hacer.
4. **Registrar:** Escribir evidencia de su decisión de forma inmutable (append-only).
5. **Dormir:** Terminar la ejecución sin dejar procesos residuales.

## Por qué no es un Daemon ni un Scheduler

Este sprint **NO** crea un daemon, **NO** crea un cronjob, y **NO** activa un scheduler persistente. 

La autonomía continua es peligrosa si el ciclo de evaluación no es perfecto. Antes de darle al Monstruo un "reloj" que lo despierte automáticamente, debemos probar que cuando despierta (manualmente), toma decisiones perfectas basadas en su Policy Engine y State Fabric, sin exceder sus límites.

El Heartbeat R0 es la prueba de concepto del ciclo cognitivo de despertar-evaluar-dormir.

## Límites Estrictos

- **Máximo Nivel de Autonomía:** A3 (artefactos persistentes no productivos).
- **A4+:** Estrictamente prohibido.
- **Acciones Productivas:** Cero.
- **Supabase/DB:** Cero contacto.
- **Nuevas APIs:** Cero llamadas (salvo cadenas R0 ya aprobadas).
