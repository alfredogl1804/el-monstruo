# CHATGPT PERICIA CHECKPOINT v1.2 — POST REACTOR/EMBRYOS — GLOBAL 95 COVERAGE PATCH

> **Propósito:** persistir el estado de pericia post-patch GLOBAL_95_REQUIRED_COVERAGE para evitar pérdida por compactación, drift o re-interpretación futura.
>
> **Generado por:** Manus B, por instrucción de Alfredo Góngora (T1), 2026-05-18.
>
> **Extiende:** `CHATGPT_PERICIA_CHECKPOINT_v1_1.md` (no lo reemplaza — es capa adicional).
>
> **Estado:** blindaje. NO diseñar, NO canonizar, NO corregir Atlas todavía salvo notas de drift.
>
> **Si abrís este archivo en hilo nuevo:** leelo completo + v1.1 + ejecutá ambos tests (v1.1 = 20 preguntas, v1.2 = 18 preguntas). Si fallás cualquiera, NO diseñes.

---

## 1. Qué cambió entre v1.1 y v1.2

| Aspecto | v1.1 | v1.2 |
|---|---|---|
| Frentes evaluados | 9 dominios genéricos | 9 frentes GLOBAL_95 obligatorios |
| Test | 20 preguntas | 20 + 18 = 38 preguntas |
| Score cap | no existía | score_caps por frente no absorbido |
| Fail conditions | implícitas | explícitas y automáticas |
| Confirmed truths | CT-001 a CT-019 | CT-020 a CT-025 (adiciones) |
| Do-not-repeat | DNR-001 a DNR-009 | DNR-010 a DNR-013 (adiciones) |

---

## 2. Los 9 frentes GLOBAL_95 (resumen ejecutivo)

| # | Frente | Qué exige | Fail condition más grave |
|---|---|---|---|
| 1 | Gate 3.4 | Distinguir 5 niveles de madurez, M4 != M5 | Afirmar production-ready sin M5 |
| 2 | Interfaces/Fabric | Leer EXISTING_DESIGN_COVERAGE_MATRIX antes de proponer | Proponer concepto sin consultar |
| 3 | APP_VISION | Doctrina no runtime, solo T1 firma | Llamar runtime a APP_VISION |
| 4 | Mobile/Flutter | Placeholders != implementación, Brand DNA drift | Afirmar implementado sin código |
| 5 | anonymous/security | BLOCKER preventivo, 3 identity layers | Afirmar bug/feature sin T1 |
| 6 | SMP/Cronos/Cripta | Sovereign Memory Plane, aliases descartados | Redibujar Cronista Familiar |
| 7 | PRE-IA | Solo T1 cierra, hypotheses = DRAFT | Cerrar PRE-IA |
| 8 | Command Center | 7 superficies reales, no control plane | Llamar control plane |
| 9 | Portfolio UI | No existe, proyectos-hijos independientes | Afirmar implementado |

---

## 3. Confirmed Truths nuevas (CT-020 a CT-025)

### CT-020 — M4 != production-ready
M4_Tested significa que existen tests de lógica pasando. NO significa route-hardening completo, madurez de UI, 100% error-path coverage, ni preparación para producción (M5). Actualmente 0/14 módulos auditados tienen M5.

### CT-021 — anonymous = BLOCKER preventivo
`user_id=anonymous` es INSUFFICIENT_EVIDENCE, no un usuario válido. Bloquea R1, tests memory_routes E2E, memoria multiusuario. Requiere clasificación T1 antes de cualquier acción.

### CT-022 — SMP = Sovereign Memory Plane
NO "Secure Memory Protocol". Es el cimiento criptográfico que garantiza Privacidad por Imposibilidad. Sin SMP, Cronos y capabilities sensibles no pueden implementarse.

### CT-023 — Portfolio UI no existe
No hay vista consolidada de portfolio dentro del Monstruo. Los proyectos-hijos (CIP, ticketlike, SoftRestaurant) tienen UIs independientes.

### CT-024 — Command Center != control plane
CC actual es consola de visualización parcial (7 superficies), no un control plane con write authority. El Cockpit canónico (12-15 superficies) es la meta, no el estado actual.

### CT-025 — PRE-IA hypotheses son DRAFT
Solo T1 con frase literal explícita puede cerrar la fase PRE-IA. Hypotheses pre-IA-001..010 no pueden canonizarse sin cierre.

---

## 4. Do-Not-Repeat nuevos (DNR-010 a DNR-013)

### DNR-010 — No proponer Cronista Familiar
Es alias descartado de `cronos_modo_cripta`. Consultar `07_ALIAS_LEDGER.yaml` antes de proponer conceptos.

### DNR-011 — No llamar runtime a APP_VISION
APP_VISION es doctrina magna, no código. Que algo esté en APP_VISION no significa que esté implementado.

### DNR-012 — No cerrar PRE-IA
Solo T1 con frase literal explícita puede cerrar la fase PRE-IA.

### DNR-013 — No llamar control plane a CC
Command Center actual es consola parcial read-only, no control plane con write authority.

---

## 5. Score caps activos

| Condición | max_global_score | Desbloqueo |
|---|---|---|
| Gate 3.4 no absorbido | 85 | Leer GATE_3_4_MODULE_MATURITY_EVIDENCE_PACK + distinguir 5 niveles |
| Interfaces/Fabric/APP_VISION/Mobile no absorbidos | 88 | Leer EXISTING_DESIGN_COVERAGE_MATRIX + APP_VISION como doctrina |
| anonymous/security no absorbido | 90 | Internalizar BLOCKER + 3 identity layers |
| SMP/Cronos/Cripta/PRE-IA no absorbidos | 90 | Sovereign Memory Plane + aliases + DRAFT |
| Command Center/Portfolio no absorbidos | 92 | 7 vs 12-15 superficies + portfolio no existe |
| GLOBAL_95 incompleto (cualquier frente < 9/10) | 90 | Todos los frentes >= 9/10 |

---

## 6. Instrucciones para hilo nuevo

1. Leer `CHATGPT_PERICIA_CHECKPOINT_v1_1.md` completo.
2. Leer este archivo (`v1_2_POST_REACTOR_EMBRYOS.md`) completo.
3. Leer `GLOBAL_95_REQUIRED_COVERAGE_v1_2.md` completo.
4. Ejecutar `PERICIA_TEST_v1_1.md` (20 preguntas, threshold 18/20).
5. Ejecutar `PERICIA_TEST_v1_2_POST_REACTOR_EMBRYOS.md` (18 preguntas, threshold 16/18).
6. Si ambos tests pasan: proceder con diseño.
7. Si cualquiera falla: releer frentes fallados, reintentar una vez. Si falla de nuevo: NO diseñar.

---

## 7. Relación con otros archivos

| Archivo | Función |
|---|---|
| `CHATGPT_PERICIA_STATE_v1_2_POST_REACTOR_EMBRYOS.json` | Estado parseable (scores, caps, CTs, DNRs) |
| `PERICIA_SCORE_RUBRIC_v1_2.yaml` | Reglas de score como YAML parseable |
| `PERICIA_TEST_v1_2_POST_REACTOR_EMBRYOS.md` | 18 preguntas test |
| `GLOBAL_95_REQUIRED_COVERAGE_v1_2.md` | Definición de los 9 frentes |
| `PERICIA_GAPS_TO_95_v1_2.md` | Mapa de gaps por frente |

---

## 8. Metadata

- **NO canoniza.** Este archivo es evidencia de pericia, no doctrina.
- **NO actualiza APP_VISION.** Cero especulación sobre lo que los módulos "deberían" hacer.
- **NO cierra PRE-IA.** La fase PRE-IA se mantiene abierta.
- **NO propone sprint nuevo.** Sin firma T1 explícita, no hay sprint derivado.
- **NO declara 95%.** Este patch define el camino a 95%, no lo alcanza.
