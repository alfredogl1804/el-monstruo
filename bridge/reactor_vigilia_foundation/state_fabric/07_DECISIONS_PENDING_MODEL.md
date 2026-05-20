# 07 DECISIONS PENDING MODEL

## Estado
- SPRINT_CANDIDATE_R0
- DOCTRINE_CANDIDATE

## Definición
El `decisions_pending.v0.json` es el buzón de entrada de Alfredo (T1). Contiene todas las decisiones estratégicas que requieren firma humana antes de que el sistema pueda avanzar en esos frentes.

## Reglas
1. **Inmutabilidad de la Firma:** Ningún loop puede cambiar el estado de una decisión de `PENDING` a `SIGNED` sin evidencia explícita en el Event Log (ej. un evento `T1_DECISION_RECORDED` originado por el Unified Face tras interacción con Alfredo).
2. **Estados Válidos:**
   - `PENDING`: Esperando a Alfredo.
   - `SIGNED`: Aprobado, ejecución autorizada.
   - `REJECTED`: Rechazado, no ejecutar.
   - `SUPERSEDED`: Obsoleto por una decisión posterior.

## Contenido v0 (Sprint Actual)
1. SPR-REACTOR-SOBERANO-001 aprobación detallada.
2. Cockpit v0.3 destino.
3. Sprint Factory v2 aprobación formal.
4. Embrión Perito model aprobación.
5. SPR-ORACLE-AI-001 ejecución inicial.
6. Modos operativos: triggers y transiciones.
7. Primer batch Self-Evolution R1.
8. Tecnología futura State Fabric: file-backed vs Supabase vs Redis vs PostgresSaver.

**Nota para el Sprint:** La tecnología actual (v0) se declara como `file-backed local-first`. La migración a tecnología productiva es una decisión pendiente.
