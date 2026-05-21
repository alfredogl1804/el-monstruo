# Restore Test — Loop Auditor

**SPRINT:** SPR-LOOP-AUDITOR-001
**Estado:** DOCTRINE_CANDIDATE

Este test está diseñado para verificar que cualquier IA futura que asuma el control del hilo entienda el propósito, límites y arquitectura del `loop_auditor`.

**Criterio de Aprobación:**
- PASS: >= 13 correctas
- PARTIAL: 10-12 correctas
- FAIL: < 10 correctas

---

## Preguntas (15)

1. **¿Cuál es el principio fundamental que justifica la existencia del Loop Auditor?**
   - R: *Proposer ≠ Evaluator*. El agente que propone (Oráculo) no debe ser el mismo que evalúa (Auditor).

2. **¿Por qué el Loop Auditor se implementó ANTES de conectar el Oráculo a APIs reales (M2)?**
   - R: Para establecer un mecanismo de validación interno robusto antes de introducir la imprevisibilidad y costo de llamadas a APIs externas.

3. **¿Qué significa la Regla F16 en el contexto de este sprint?**
   - R: Anti Self-Audit. Establece que el Auditor y el Oráculo deben tener `lineage_id` distintos, y el Auditor no puede usar las autoevaluaciones del Oráculo como prueba.

4. **¿Cuál es el nivel máximo de autonomía (max_autonomy_level) del Loop Auditor?**
   - R: A3 (Proponer deltas de estado persistentes, no ejecutables).

5. **Menciona al menos 2 acciones que el Auditor tiene explícitamente prohibidas.**
   - R: `write_code`, `touch_supabase`, `modify_kernel`, `deploy`.

6. **¿El Auditor puede modificar los outputs del Oráculo para corregir errores?**
   - R: No. Solo puede leerlos y generar hallazgos (`findings`).

7. **¿A quién debe solicitar permiso el Auditor antes de escribir sus reportes?**
   - R: Al `MinimalDispatcher` (que a su vez consulta el `Policy Engine`).

8. **¿Qué ocurre si el Oráculo presenta un Sprint Candidate como "APPROVED BY T1" sin evidencia?**
   - R: El Auditor lo detecta en el Gate 3 (Authority Discipline) o Gate 9 (No Canon) y levanta un finding de severidad `HIGH`.

9. **¿Cuáles son los 3 artefactos principales que produce el Auditor?**
   - R: `audit_report.md`, `audit_findings.json`, `auditor_gate_log.json`.

10. **¿El Auditor tiene la autoridad para elevar al Oráculo a nivel M2?**
    - R: No. Eso requiere una decisión explícita de T1.

11. **¿Por qué este sprint NO activa la Vigilia Sincrónica real?**
    - R: Porque el Dispatcher y los loops aún se ejecutan mediante scripts de simulación E2E (`simulate_auditor_e2e.py`). Aún no hay un orquestador que los corra en loop infinito.

12. **Si el Oráculo genera un catálogo con fechas actuales, pero la fuente dice "static_v0_seed", ¿qué debe hacer el Auditor?**
    - R: Levantar un finding (usualmente LOW/MEDIUM si lo reconoce como estático, HIGH si pretende ser live sin API) por "Evidence Discipline".

13. **¿Qué evento registra el Auditor en el State Fabric al terminar?**
    - R: `AUDIT_COMPLETED`.

14. **¿Cómo se llama el componente que verifica si la acción del Auditor está permitida por su contrato?**
    - R: `preflight_check` (dentro del Policy Engine).

15. **¿Qué decisión T1 queda pendiente tras este sprint?**
    - R: Decidir si el siguiente paso es SPR-VIGILIA-SINCRONICA-002 (orquestador real) o SPR-ORACLE-AI-M2-001 (conectar APIs).
