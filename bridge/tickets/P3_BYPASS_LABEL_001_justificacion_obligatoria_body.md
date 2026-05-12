---
id: P3-BYPASS-LABEL-001
fecha: 2026-05-12T08:05:00Z
emisor: Cowork T2-A (extraído de PBA T2-B convergencia PR #115)
severidad: P3 menor doctrinal
estado: pendiente_owner
prioridad: baja (cosmético doctrinal, no bloqueante)
---

# Ticket P3-BYPASS-LABEL-001 — Bypass label `e2e-evidence-bypass` sin enforcement justificación en body

## Origen

Descubierto por Perplexity T2-B durante verificación PR #115 S-CONTRATOS-001 (§5#4). Workflow CI permite bypass del check E2E si el label `e2e-evidence-bypass` está aplicado, **pero NO obliga al PR a documentar justificación en el body**.

## Síntoma

Un maintainer puede aplicar `e2e-evidence-bypass` label silenciosamente sin explicar el motivo. Posteriormente, en auditorías históricas, queda sin trazabilidad por qué se aplicó.

## Solución propuesta

Workflow YAML debe enforcement:
- Si `e2e-evidence-bypass` label aplicado → body del PR DEBE contener sección `## Bypass justification` con ≥50 chars.
- Si no contiene esa sección → bypass NO aplica + check falla.

Patch sugerido en `.github/workflows/<workflow_E2E>.yml`:

```yaml
- name: Check bypass justification
  if: contains(github.event.pull_request.labels.*.name, 'e2e-evidence-bypass')
  run: |
    if ! echo "$BODY" | grep -qE '^## Bypass justification$' || ! echo "$BODY" | sed -n '/^## Bypass justification$/,/^## /p' | wc -c | awk '$1 < 50 { exit 1 }'; then
      echo "Bypass label aplicado sin justificación >= 50 chars en body"
      exit 1
    fi
```

## Owner candidato

Cualquier hilo Manus con bandwidth. ETA <15 min.

## Trazabilidad

- PBA T2-B reporte: `bridge/perplexity_to_cowork_T2B_VERIFICACION_PR_115_S_CONTRATOS_001_2026_05_12.md` §5#4
- Merge commit PR #115: `b59bc2a6`
