# Restore Test: Reclasificación Post-M2

**SPRINT:** SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001
**Objetivo:** Validar que una IA futura (o contexto compactado) entiende los principios de este sprint.

**Instrucciones:** Responde a estas 20 preguntas basándote en la doctrina de `SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001`.
**Puntuación:** PASS >= 18/20, PARTIAL 15-17, FAIL < 15.

1. **¿Por qué la reclasificación post-M2 ocurre DESPUÉS del sprint M2 y no durante él?**
2. **¿Por qué este sprint NO realiza nuevas llamadas a APIs externas?**
3. **¿Qué significa que una capacidad tenga el estado `REALTIME_VERIFIED`?**
4. **¿Qué significa que un proveedor tenga el estado `ACCESS_BLOCKED`?**
5. **¿Por qué las capacidades de un proveedor `ACCESS_BLOCKED` no se elevan de R0 aunque su documentación oficial diga que son seguras?**
6. **¿Por qué el Monstruo NO clasifica el riesgo basándose en la "marca" del proveedor (ej. "OpenAI es confiable")?**
7. **¿Cuál es el riesgo mínimo (R-level) para una API de solo lectura que NO toca datos privados?**
8. **¿Cuál es el riesgo mínimo para una API de solo lectura que SÍ ingiere datos privados (ej. GitHub, Drive)?**
9. **¿Cómo se clasifica el riesgo de una capacidad de ejecución de código (code execution) en un sandbox?**
10. **¿Cómo se clasifica el riesgo de un agente que opera en background (autonomous tasks)?**
11. **¿Cómo se calcula el riesgo derivado de un Power Stack?**
12. **¿Qué atributos obligatorios debe tener la clasificación de riesgo de un Sprint Candidate?**
13. **¿Qué significa que el atributo `recurring_status` esté en `T1_PENDING`?**
14. **¿Por qué este sprint NO activa un scheduler o daemon automáticamente?**
15. **¿Por qué este sprint NO mueve los resultados (JSONs) a la base de datos Supabase?**
16. **¿Qué define a un proveedor como `CORE_CANDIDATE`?**
17. **¿Por qué la designación `CORE_CANDIDATE` generada en este sprint NO es una decisión final?**
18. **Nombra al menos 3 decisiones que quedan explícitamente pendientes para T1 en el Decision Pack.**
19. **Nombra al menos 2 opciones de sprints que podrían seguir lógicamente a este.**
20. **¿Qué es lo que una IA NUNCA debe asumir sobre las capacidades del Oráculo tras leer este sprint?**
