# B8 v3 — Pre-Activation Hotfix Report

**Fecha:** 2026-05-21
**Rama:** `control-tower/2026-05-21-b8-v3-preactivation-hotfix`
**Base:** `main` @ `b8a2216` (post-merge PR #177 — Anti-Dory B8 v3 integration dark launch)
**Autor:** Cowork T2 (autónomo, sin push a main, sin deploy, sin Supabase writes)
**Estado:** `HOTFIX_READY_FOR_REVIEW` — **activación del flag sigue BLOQUEADA** hasta revisión y merge de este hotfix.

---

## 1. Contexto

El post-merge audit de PR #177 marcó `HOTFIX_RECOMMENDED` antes de activar el flag
`ANTI_DORY_B8_V3_ENABLED` por tres caveats:

1. **Sin tests pytest para flag ON/OFF ni para Layers 4-5.** El flag se lee en
   tiempo de import (`os.environ.get(...)` a nivel módulo) y no había cobertura
   que ejerciera ese comportamiento con `monkeypatch + importlib.reload`.
2. **`MAGNA_ACTION_TYPES_INHERENT` incluía `git_push` demasiado amplio.** Un
   push a feature-branch benigno sería escalado a MAGNA bajo el flag ON, lo
   cual produce ruido y desensibiliza la matriz de autoridad B9.
3. **El wording del canary/reporte sobre 231/231 sonaba como CI completo.** En
   realidad ese número corresponde al subset de regresión Anti-Dory / B8 + la
   evidencia del Canary v3, no al pipeline CI legacy completo (que tiene caveats
   conocidos documentados en commits previos).

Este hotfix corrige los tres puntos sin activar Fase 1, R1, Guardian, Dory dead
ni habilitar el flag por defecto.

## 2. Cambios

### 2.1 `kernel/anti_dory/b8_magna_classifier.py`

- **Removido** `"git_push"` (acción genérica) del set `MAGNA_ACTION_TYPES_INHERENT`.
- **Agregados** los siguientes action_types narrower con semántica de seguridad
  explícita: `"push_to_main"`, `"force_push_main"`, `"push_production"`,
  `"push_to_production"`. (Se conserva `"force_push"` y `"git_merge"`.)
- **Nueva LAYER 5.5 — Branch-aware git_push (solo activa con el flag ON).**
  Si la acción es `"git_push"` o `"push"` y `metadata.target_branch` está en
  `{main, master, production, prod, release}`, se escala a MAGNA con razón
  `"git_push targets protected branch '<branch>' (branch-aware MAGNA escalation)"`.
  En cualquier otra rama (feature/*, dev, staging-*, etc.) permanece STANDARD.
  Esto preserva la seguridad de pushes a main/production sin penalizar el
  flujo cotidiano de feature branches.
- **Docstring de LAYER 4 actualizado** para documentar la decisión.

Las Layers 1-3 (v1.0 triggers + danger keywords + v2.0 semantic patterns)
permanecen idénticas. La actividad de Layers 4-5 sigue gateada por el flag
`ANTI_DORY_B8_V3_ENABLED` (default: `false`).

### 2.2 `tests/anti_dory/test_b8_v3_flag.py` (nuevo)

40 tests nuevos organizados en 6 clases. Todos usan `monkeypatch.setenv` +
`importlib.reload(b8_mod)` con fixtures `b8_off` / `b8_on` que restauran el
estado original del módulo en teardown.

| Clase | Tests | Cubre |
|---|---|---|
| `TestDefaultOff` | 4 | (a) Flag default false; Layers 4-5 inactivas; push a feature-branch no escala por v3 |
| `TestFlagOnLayer4Inherent` | 15 (parametrize) | (b) Cada action_type inherently-dangerous escala a MAGNA con flag ON |
| `TestFlagOnLayer5ContextAware` | 8 (parametrize) | (c) Patrones context-aware (stale_state, false_memory, context_loss, secret_write, unauthorized_side_effect) escalan a MAGNA con flag ON |
| `TestBranchAwareGitPush` | 9 (parametrize) | Branch-aware: protected → MAGNA, feature → STANDARD, sin target → STANDARD |
| `TestReloadIsolation` | 1 | (d) OFF→ON→OFF reload limpio, sin side effects globales |
| `TestGitPushRegressionGuard` | 2 | Guarda: `git_push` removido, narrower variants presentes |

### 2.3 `bridge/control_tower/2026-05-21/manus/evidence/B8_V3_PREACTIVATION_HOTFIX_junit.xml`

JUnit XML generado de la corrida combinada (original + v2 semantic + v3 hotfix).

## 3. Resultados de tests

```
$ python3 -m pytest tests/anti_dory/test_b8_magna_classifier.py \
    tests/anti_dory/test_b8_v2_semantic.py \
    tests/anti_dory/test_b8_v3_flag.py
======================== 153 passed, 1 warning in 0.27s ========================
```

Breakdown:

| Suite | Tests | Resultado |
|---|---|---|
| `test_b8_magna_classifier.py` (v1 original) | 38 | 38/38 ✅ |
| `test_b8_v2_semantic.py` (v2 semantic) | 75 | 75/75 ✅ |
| `test_b8_v3_flag.py` (hotfix v3) | 40 | 40/40 ✅ |
| **Total** | **153** | **153/153 ✅** |

Sin regresiones en v1/v2. Todos los caveats del audit cubiertos.

## 4. Aclaración del wording de Canary (caveat #3)

> Las cifras del tipo **"231/231"** que aparecen en reportes previos de Canary
> v3 corresponden al **subset de regresión Anti-Dory / B8 y a la evidencia del
> Canary v3 específicamente**, NO al pipeline CI legacy completo. El CI legacy
> tiene caveats conocidos (bypass histórico documentado en commit `b11254f`
> "B8 v2 con legacy CI bypass") que NO han sido resueltos por este hotfix ni
> por PR #177. Cualquier referencia a "all green / 231/231" debe leerse como
> *"todos los tests Anti-Dory/B8 verdes en el subset de Canary v3, con bypass
> CI legacy aún vigente"*.

Este hotfix NO arregla el CI legacy. NO declara verde global. NO autoriza
activación del flag.

## 5. Guardrails confirmados

- [x] **NO push a main.** Trabajo en rama lateral `control-tower/2026-05-21-b8-v3-preactivation-hotfix`.
- [x] **NO deploy.** Sin tocar Railway, sin reiniciar servicios.
- [x] **NO writes Supabase.** Solo cambios en código + tests + reporte.
- [x] **NO activación de Fase 1.** Sin cambios en `phase_1_action`.
- [x] **NO activación de R1.** Sin cambios en `approve_r1`.
- [x] **NO activación de Guardian.** `b10_guardian_cron.py` no tocado.
- [x] **NO declaración Dory muerto.** Sin cambios en `declare_dory_dead`.
- [x] **`ANTI_DORY_B8_V3_ENABLED` sigue default `false`.** No tocado el default ni en código ni en env.
- [x] **Sin secrets.** No se exponen credenciales en código, tests o reporte. Los strings de test (ej. "real ANTHROPIC_API_KEY value") son texto descriptivo para los patrones regex, no claves reales.

## 6. Estado del activador

| Condición pre-activación PR #177 | Estado |
|---|---|
| Tests para flag ON/OFF | ✅ Cubierto (40 nuevos, 4 + 15 + 8 + 1 = 28 cubren directamente flag) |
| Tests para Layer 4 inherent | ✅ Cubierto (15 parametrize) |
| Tests para Layer 5 context-aware | ✅ Cubierto (8 parametrize) |
| `monkeypatch + importlib.reload` para flag import-time | ✅ Cubierto (fixtures `b8_off` / `b8_on`) |
| Sin escalación de feature-branch push | ✅ Cubierto (Layer 5.5 branch-aware + remoción de `git_push` inherent) |
| Wording Canary clarificado | ✅ §4 de este reporte |
| Revisión humana del hotfix | ⏳ **PENDIENTE** |
| Merge del hotfix a main | ⏳ **PENDIENTE** |

**Activación del flag `ANTI_DORY_B8_V3_ENABLED=true` permanece BLOQUEADA** hasta
que un revisor humano (T1 o T2 par) firme este hotfix y se mergee.

## 7. Próximos pasos sugeridos (NO ejecutados por este hotfix)

1. Revisión binaria diff del hotfix (Cowork audit DSC-G-008 v2 si aplica).
2. Merge a main bajo regla evolucionada del merge (instrucción T1 explícita o
   audit DSC-G-008 v2 con 6 gates verdes).
3. Una vez mergeado, decidir orden de activación de flags (sigue siendo decisión
   pendiente del Sprint COWORK-RUNTIME-001).
4. Documentar en `memory/cowork/COWORK_ESTADO_VIVO.md` cuando se active el flag.

---

**Firma técnica T2 (Cowork autónomo):** Hotfix listo para revisión. Branch
lista para PR side-only. Sin merge ejecutado.
