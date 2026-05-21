# Visión: Reclasificación de Riesgo Post-M2

**SPRINT:** SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001
**Estado:** DOCTRINE_CANDIDATE

## El Principio Operativo
La arquitectura de Vigilia Sincrónica y el Oráculo de IAs opera bajo un principio estricto de tres fases:

1. **Verificar Realidad:** Obtener evidencia empírica (M2) de que una capacidad existe y es accesible, sin asumir nada basado en documentación o entrenamiento.
2. **Reclasificar Riesgo:** (Este sprint) Evaluar la superficie de ataque real de las capacidades verificadas y asignarles un nivel de riesgo operativo (R1-R4) y un nivel de autonomía requerido (A0-A8).
3. **Automatizar:** (Futuro) Conceder permisos de ejecución recurrente o productiva solo a aquellas capacidades que hayan superado las dos fases anteriores y cuenten con la aprobación explícita de T1.

## El Problema de la Inercia
En el catálogo inicial (M1), todas las capacidades fueron marcadas como `R0` (Sin Riesgo / Inerte) porque su evidencia era `STATIC_CATALOG`. Una IA que solo existe en un documento JSON no puede causar daño.

Tras el sprint M2, 4 de los 6 proveedores demostraron estar vivos, accesibles y responder a las credenciales inyectadas. Sus capacidades (visión, tool use, ejecución de código, etc.) ya no son inertes. Mantenerlas en `R0` sería una negligencia arquitectónica.

## El Propósito de este Sprint
Este sprint toma los artefactos inmutables generados por M2 y aplica reglas lógicas para elevar el riesgo de las capacidades verificadas. 

**Lo que SÍ hace:**
- Eleva el `risk_class` de capacidades verificadas (ej. de R0 a R2).
- Asigna `required_autonomy_level` (ej. A3).
- Deriva el riesgo compuesto para Power Stacks y Sprint Candidates.
- Propone una matriz de proveedores Core vs Opcionales.
- Prepara un paquete de decisión formal para T1.

**Lo que NO hace:**
- No ejecuta nuevas llamadas a APIs externas.
- No activa schedulers, daemons o cron jobs.
- No mueve datos a bases de datos productivas (Supabase).
- No toma decisiones finales sobre automatización (eso requiere firma T1).
- No altera destructivamente los artefactos de sprints anteriores.
