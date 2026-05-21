# Visión del Loop Auditor

**SPRINT:** SPR-LOOP-AUDITOR-001
**Estado:** DOCTRINE_CANDIDATE

El Loop Auditor es el segundo loop real del Monstruo, diseñado específicamente para validar los outputs del Oráculo de IAs. Su existencia materializa uno de los principios fundamentales de la arquitectura del Monstruo.

## Principio Core: Proposer ≠ Evaluator

En sistemas multi-agente robustos, el agente que propone una solución o genera un artefacto no debe ser el mismo que lo evalúa. La separación de responsabilidades garantiza objetividad y previene la auto-complacencia o el "autoboicot" silencioso.

1. **Oráculo Propone:** El Oráculo de IAs escanea el entorno, detecta capacidades emergentes y propone Power Stacks y Sprint Candidates.
2. **Auditor Evalúa:** El Loop Auditor lee las propuestas del Oráculo, las contrasta contra reglas estrictas de schema, consistencia y política, y emite un veredicto.
3. **Dispatcher Autoriza:** Ninguno de los dos loops escribe en el State Fabric sin pedir permiso al Dispatcher.
4. **T1 Decide:** La aprobación final para avanzar a producción o canonizar siempre requiere la firma humana (T1).

## Límites Estrictos del Auditor

Para garantizar que el Auditor no sufra de "autonomy creep" (expansión no autorizada de su autoridad), se establecen los siguientes límites:

- **No modifica:** El Auditor lee los outputs del Oráculo, pero jamás los altera. Si encuentra errores, genera un reporte de hallazgos (`audit_findings.json`).
- **No conecta APIs:** En esta etapa (M1), el Auditor no hace llamadas a APIs externas para verificar la veracidad de las capacidades IA. Valida la estructura y consistencia interna de los documentos.
- **No canoniza:** El Auditor puede marcar un documento como `PASS`, pero esto no lo convierte en canon. Solo T1 puede canonizar.
- **No aprueba Sprints:** El Auditor verifica que los Sprint Candidates tengan la información requerida, pero no los aprueba para ejecución.
