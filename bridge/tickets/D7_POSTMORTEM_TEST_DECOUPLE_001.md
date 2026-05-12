---
id: D7-POSTMORTEM-TEST-DECOUPLE-001
fecha: 2026-05-12T09:00:00Z
emisor: Cowork T2-A (extraído de PBA T2-B PR #116 caveat P2-A)
severidad: P2 doctrinal
estado: pendiente_owner
deadline: D+7 = 2026-05-19
prioridad: media (no bloqueante de operación, pero anti-acoplamiento test)
---

# Ticket D+7 POSTMORTEM-TEST-DECOUPLE-001 — Desacoplar tests de bridge/postmortems/

## Origen

Descubierto por Perplexity T2-B PR #116 ESCAPE-001 convergencia caveat P2-A (`bridge/perplexity_to_cowork_T2B_PBA_PR_116_ESCAPE_001_2026_05_12.md` local).

T2-B intentó ejecutar `python -m pytest tests/escape/ -v` con checkout parcial sin `bridge/postmortems/` y obtuvo **1 falso positivo** en `TestPostmortemSanity::test_postmortem_file_exists`. Re-run con checkout completo pasó 27/27.

## Síntoma

Test `tests/escape/test_escape.py::TestPostmortemSanity::test_postmortem_file_exists` acopla suite kernel a directorio `bridge/postmortems/` que NO es parte del runtime kernel. Esto:

1. Causa falsos positivos en checkout parcial.
2. Viola separación de concerns (test kernel ≠ test doctrinal docs).
3. Ralentiza CI cuando bridge/ está en .gitignore parcial.

## Solución propuesta

**Opción A — Mover test a CI doctrinal separado:**
```yaml
# .github/workflows/doctrinal-postmortem-check.yml
# Workflow separado que verifica postmortems existen sin tocar tests kernel
```

**Opción B — Skip con marker pytest:**
```python
@pytest.mark.doctrinal
@pytest.mark.skipif(not Path('bridge/postmortems').exists(), reason='checkout parcial')
def test_postmortem_file_exists():
    ...
```

**Opción C — Mover test directamente a `tests/doctrinal/`:**
```
tests/doctrinal/test_postmortems_existen.py  # nuevo dir + test
```

Recomendación T2-A: **Opción C** (más limpia, sin overhead workflow nuevo).

## Tests de regresión

Verificar que `pytest tests/escape/ -v` ejecutado con checkout parcial sin `bridge/postmortems/` NO falla en `TestPostmortemSanity`.

## Owner candidato

Cualquier Hilo Manus con bandwidth. ETA <15 min.

## Trazabilidad

- PBA T2-B reporte PR #116: pegado verbatim Alfredo T1 2026-05-12 ~08:55 UTC
- Merge commit PR #116: `5f38b9c2`
- DSC-G-008 v3 §4: este ticket es el follow-up estructural de la caveat T2-B P2-A
