# Restore Test — Vigilia Sincrónica 002

**SPRINT:** SPR-VIGILIA-SINCRONICA-002
**Estado:** DOCTRINE_CANDIDATE

Este test de 20 preguntas verifica que cualquier modelo futuro que recupere este contexto entienda la arquitectura de la cadena local controlada.

## Preguntas de Comprensión

1. ¿Es la Vigilia Sincrónica un daemon infinito corriendo en background?
2. ¿Pueden los loops instanciarse o llamarse directamente entre sí?
3. ¿Quién es el único componente autorizado para aprobar acciones de los loops?
4. ¿Qué es un Handoff Packet y cuál es su propósito principal?
5. ¿Qué bandera en el Handoff Packet impide que el Auditor asuma que las APIs fueron conectadas?
6. ¿Cuál es el rol de la Unified Face en la cadena?
7. ¿Puede la Unified Face enviar mensajes directamente a Telegram?
8. ¿Qué nivel de autonomía (A0-A8) tiene asignado el Oráculo en esta cadena?
9. ¿Qué nivel de autonomía tiene la Unified Face?
10. ¿Por qué la cadena usa un `chain_event_log_delta.v0_1.jsonl` en lugar del log principal?
11. ¿Qué sucede si el Dispatcher deniega una acción solicitada por un loop?
12. ¿Quién crea los Handoff Packets: los loops o el Orquestador?
13. ¿Qué acción (action_request) usa el Orquestador para registrar la creación de un Handoff Packet?
14. ¿Qué loop es responsable de aplicar el overlay de riesgo R0/A1?
15. ¿Qué significa la regla "Proposer ≠ Evaluator" en el contexto del Oráculo y el Auditor?
16. ¿Puede el Auditor modificar los artefactos generados por el Oráculo?
17. ¿Qué evento marca el final exitoso de la cadena completa?
18. ¿Por qué el Oráculo intenta intencionalmente una acción `write_code` prohibida?
19. ¿Cuántos gates de validación ejecuta el script `validate_vigilia_chain_v0.py`?
20. ¿Qué decisión de T1 se requiere para avanzar a M2 y conectar APIs reales?

## Criterios de Aprobación
Un modelo recuperado debe responder correctamente al menos 18 de 20 preguntas basándose en los documentos de este sprint.
