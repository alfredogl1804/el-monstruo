# PERICIA RECALIBRATION BASELINE v1.2

**Sprint:** SPR-PERICIA-RECALIBRATION-v1_2-POST-REACTOR-EMBRYOS
**Fecha:** 2026-05-21
**Ejecutado por:** Manus B (hilo técnico)
**Instruido por:** Alfredo Góngora (T1)

---

## Confirmaciones de Baseline

| Aspecto | Estado | Evidencia |
|---|---|---|
| v1.1 previo | 73% | `CHATGPT_PERICIA_STATE_v1_2_POST_REACTOR_EMBRYOS.json` → `estimated_total_pericia_pct: 73` |
| v1.2 scores | NULL (9 frentes sin evaluar) | `global_95_frentes` → todos `score: null`, `status: NOT_EVALUATED_YET` |
| Global 95 requiere | 9 frentes con score >= 9/10 cada uno | `GLOBAL_95_REQUIRED_COVERAGE_v1_2.md` §10 |
| 95 declarado | NO | `status.not_yet: ARQUITECTO_PRINCIPAL` |
| Canonización | NO hay | `metadata.no_canonization: true` |

---

## Los 9 Frentes GLOBAL_95 (estado pre-recalibración)

| # | Frente | Score actual | Status |
|---|---|---|---|
| 1 | GATE_3_4_COMPLETO | null | NOT_EVALUATED_YET |
| 2 | INTERFACES_CONTEXT_FABRIC | null | NOT_EVALUATED_YET |
| 3 | APP_VISION | null | NOT_EVALUATED_YET |
| 4 | MOBILE_FLUTTER_REALITY | null | NOT_EVALUATED_YET |
| 5 | ANONYMOUS_SECURITY_IDENTITY | null | NOT_EVALUATED_YET |
| 6 | SMP_CRONOS_CRIPTA | null | NOT_EVALUATED_YET |
| 7 | PRE_IA | null | NOT_EVALUATED_YET |
| 8 | COMMAND_CENTER | null | NOT_EVALUATED_YET |
| 9 | PORTFOLIO_UI_EMPRESAS_HIJAS | null | NOT_EVALUATED_YET |

---

## Score Caps Activos (pre-recalibración)

| Condición | max_global_score |
|---|---|
| global_95_coverage_incomplete | 90 |

Nota: al no haber ningún frente evaluado, el cap más restrictivo es 90 (por cobertura incompleta). Los caps individuales (85, 88, 90, 92) se aplicarán en cascada según resultados.

---

## Archivos Leídos para Baseline

1. `CHATGPT_PERICIA_STATE_v1_2_POST_REACTOR_EMBRYOS.json` — scores null, CTs 020-025, DNRs 010-013
2. `CHATGPT_PERICIA_CHECKPOINT_v1_2_POST_REACTOR_EMBRYOS.md` — narrativa del patch, instrucciones
3. `GLOBAL_95_REQUIRED_COVERAGE_v1_2.md` — definición de 9 frentes + fail conditions
4. `PERICIA_SCORE_RUBRIC_v1_2.yaml` — reglas de score como YAML parseable
5. `PERICIA_GAPS_TO_95_v1_2.md` — gaps estimados por frente (pre-recalibración)

---

## Constraints Confirmados

- NO inflar score
- NO declarar GLOBAL_95 si no pasa
- NO mezclar pericia global con pericia Reactor/Embriones/R0+
- NO llamar embrión a carril
- NO llamar runtime a shadow
- NO llamar control plane a cockpit read-only
- NO llamar compresión a encoding más pesado
- NO canonizar
- NO APP_VISION close
- NO PRE-IA close
