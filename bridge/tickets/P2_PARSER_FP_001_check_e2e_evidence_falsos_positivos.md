---
id: P2-PARSER-FP-001
fecha: 2026-05-12T08:05:00Z
emisor: Cowork T2-A (extraído de PBA T2-B convergencia PR #115)
severidad: P2 doctrinal
estado: pendiente_owner
prioridad: media (no bloqueante de merges actuales, pero enforcement DSC-G-010 trivialmente bypaseable)
---

# Ticket P2-PARSER-FP-001 — `_check_e2e_evidence.py` permite falsos positivos

## Origen

Descubierto por Perplexity T2-B durante verificación independiente PR #115 S-CONTRATOS-001 (`bridge/perplexity_to_cowork_T2B_VERIFICACION_PR_115_S_CONTRATOS_001_2026_05_12.md` §5#3). Cowork T2-A audit inicial NO detectó este hallazgo. PBA convergencia lo extrajo.

## Síntoma

Parser `_check_e2e_evidence.py` (workflow CI E2E enforcement DSC-G-010) acepta como evidencia válida strings que NO son evidencia real:

| String input | Parser decisión | Realidad |
|---|---|---|
| `abc1234` | pasa como `sha:abc1234` | NO es SHA git válido (necesita 7+ hex) |
| `Todo OK` | pasa como `test:OK` | NO es output de test runner |
| `0 passed` | pasa como `test:0 passed` | 0 tests passed = sin evidencia ejecutiva |

## Consecuencia material

Enforcement DSC-G-010 ("E2E evidence binaria obligatoria en body del PR") es **trivialmente bypaseable sin label** `e2e-evidence-bypass`. Cualquier PR puede escribir `Tests: Todo OK` en body y pasar el check, sin ejecutar tests reales.

Esto vacía el propósito de DSC-G-010. Si bien el bypass label existe para casos legítimos (refactor docs, etc.), el parser actual ni siquiera obliga a usarlo.

## Solución propuesta

Reforzar parser `_check_e2e_evidence.py` con regex estrictos:

```python
# SHA git real: 7-40 chars hex lowercase
SHA_REGEX = r'\bsha:([0-9a-f]{7,40})\b'

# Tests passed: requiere número entero ≥ 1
TESTS_PASSED_REGEX = r'\btest:([1-9]\d*)\s+passed\b'

# Status válido: PASSED|VERDE|GREEN explícito
STATUS_REGEX = r'\bstatus:(PASSED|VERDE|GREEN)\b'
```

## Tests de regresión

Agregar `tests/test_check_e2e_evidence_strict.py` con los 3 casos de falso positivo + 5+ casos válidos.

## Owner candidato

Cualquier hilo Manus con bandwidth. NO bloqueante. ETA estimado <30 min con velocity reciente.

## Trazabilidad

- PBA T2-B reporte: `bridge/perplexity_to_cowork_T2B_VERIFICACION_PR_115_S_CONTRATOS_001_2026_05_12.md` §5#3
- Cowork audit comment PR #115: https://github.com/alfredogl1804/el-monstruo/pull/115#issuecomment-4428505769
- Merge commit: `b59bc2a6`
