# 01 STATE FABRIC VISION

## Estado
- SPRINT_CANDIDATE_R0
- DOCTRINE_CANDIDATE

## ¿Qué es el State Fabric?
El State Fabric es la capa de persistencia de la "Vigilia Sincrónica". Es la memoria consolidada y el registro de eventos que permite que múltiples loops de ejecución finita (como los hilos de Manus o Cowork) compartan un contexto único y actúen como "un solo Monstruo".

## Objetivo del v0 (Local-First)
Este v0 es **file-backed y local-first**. No usa Supabase, Redis ni bases de datos en la nube. Todo el estado se representa en archivos JSON y YAML dentro del repositorio. 

El propósito de esta versión no es la escala, sino establecer los **contratos de datos** y las **reglas de mutación** antes de conectar tecnología productiva. Si el diseño file-backed es robusto y evita el split-brain, migrarlo a una base de datos real (SPR-STATE-FABRIC-002) será trivial.

## Principios Rectores
1. **Verdad en el Event Log:** El estado actual es solo una proyección (reducer) del log de eventos append-only.
2. **Mutación controlada:** Los loops proponen eventos, no escriben directamente el estado.
3. **Lectura segura:** Los loops deben usar cursores para saber qué han leído y evitar procesamiento duplicado.
4. **Binding con Autonomía:** Cada evento propuesto debe pasar por el Policy Engine (Escalera A0-A8) antes de ser aceptado.
