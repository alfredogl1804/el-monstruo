---
id: D7-DASHBOARD-XSS-AUDIT-001
fecha: 2026-05-12T09:00:00Z
emisor: Cowork T2-A (extraído de PBA T2-B PR #116 caveat P3-B)
severidad: P3 menor doctrinal
estado: pendiente_owner
deadline: D+7 = 2026-05-19 (post-7-días-prod con datos reales)
prioridad: baja (escape escape XSS declarado pero no verificado runtime)
---

# Ticket D+7 DASHBOARD-XSS-AUDIT-001 — Verificar runtime XSS escape en dashboards

## Origen

Descubierto por Perplexity T2-B PR #116 ESCAPE-001 caveat P3-B. Aplicable también a otros dashboards del kernel (rotor, escape, guardian, cost).

Los dashboards declaran "XSS protected" via HTML escape pero T2-B no verificó runtime con datos reales en prod. **No urgente, pero D+7 con datos reales en prod permite verificación robusta.**

## Síntoma posible

Si escape() solo cubre `<>&"'` pero no cubre otros vectores (URLs javascript:, event handlers como onerror, data: URIs, nullbytes, unicode), un consumer name malicioso o metadata JSONB con XSS payload podría romper el dashboard.

## Dashboards afectados

- `kernel/dashboards/escape_history.py` (este sprint)
- `kernel/dashboards/rotor_history.py`
- `kernel/dashboards/guardian_dashboard.py`
- `kernel/dashboards/cost_history.py`

## Solución propuesta

**Auditoría D+7 (2026-05-19) con datos reales:**

1. Inyectar registro test con consumer name + metadata con XSS payload conocido:
   ```sql
   INSERT INTO escape_pulse_log (consumer, metadata) VALUES (
     '<script>alert(1)</script>',
     '{"key": "<img src=x onerror=alert(2)>", "nested": {"javascript:void(0)": true}}'::jsonb
   );
   ```
2. Generar dashboard HTML.
3. Verificar binariamente que el HTML output NO contiene `<script>` ejecutable ni `onerror=` ni `javascript:` no escapados.
4. Si falla → reforzar escape() con whitelist más amplia.
5. Limpiar test row post-audit.

## Tests de regresión

Agregar tests con vectores XSS conocidos a `tests/test_*_dashboard.py` para los 4 dashboards.

## Owner candidato

Cualquier Hilo Manus con bandwidth post-D+7. ETA <60 min para auditar los 4 dashboards.

## Trazabilidad

- PBA T2-B reporte PR #116: pegado verbatim Alfredo T1 2026-05-12 ~08:55 UTC
- Merge commit PR #116: `5f38b9c2`
- DSC-G-008 v3 §4: este ticket es el follow-up estructural de la caveat T2-B P3-B
