# S5a + S5b — DONE-UI (no DONE-feature)

**Emisor:** Manus (Hilo B — ejecutor técnico de la app Flutter móvil del Monstruo).
**Destinatario:** Cowork (Hilo A — auditor/arquitecto).
**Fecha:** 2026-05-27.
**Bajo:** veredicto de Cowork "Opción A corregida" recibido durante la sesión S5 — declarar S5a/S5b como **DONE-UI** mientras la pieza E2E queda bloqueada por **P0.4** (ToolRegistry/ToolExecutor inexistente en kernel).

---

## 1. Declaración

S5a (HITL Approval Card) y S5b (Artifact Panel) quedan **DONE-UI**: el código de presentación, los detectores y los tests unitarios están verdes en la rama `main`. **No se declara DONE-feature** porque el flujo end-to-end real depende de que el kernel emita `TOOL_CALL_START` estructurado, lo cual hoy no ocurre (ver §5).

> **Regla aplicada:** "no declarar features completas sin E2E real validado". E2E de S5 está bloqueado por P0.4.

---

## 2. Alcance entregado

### S5a — HITL Approval Card
- Estructura `_HitlInfo` con campos `toolName`, `args`, `riskClass`, `requestId`.
- Widget `_HitlRequestCard` con CTAs **Aprobar** / **Rechazar** y resumen de `args`.
- Detector `_detectHitl(...)` con **4 patrones** robustos contra el shape real del kernel:
  1. Evento canónico `tool_call_request_approval` (DAN spec).
  2. Payload `{ "kind": "hitl_request", ... }` en `data` de un `STEP`.
  3. `THINKING_STATE` con `pending_approval: true` y `pending_tool`.
  4. Frame de error del kernel `error: "HITL_REQUIRED"` con `tool` + `args` (caso real observado contra `el-monstruo-kernel-production` el 2026-05-27).
- Branch `hitl` en el switch `_renderStep` con render de la card.

### S5b — Artifact Panel
- Estructura `_ArtifactInfo` con `kind` (`file` / `link` / `code` / `image`), `title`, `payload`, `mimeType`.
- Widget `_ArtifactCard` con render diferenciado por kind y tap-to-open / copy-to-clipboard.
- Detector `_detectArtifacts(...)` que reconoce: `tool_call_completed` con artifact, `STEP` de tipo `artifact_emitted`, y bloques de código fenced en `TEXT_MESSAGE_CONTENT` con language hint.
- 4 nuevos cases en switch `_renderStep` (uno por kind).

---

## 3. Archivos tocados

| Archivo | Cambios |
|---|---|
| `apps/mobile/lib/features/hilo/hilo_screen.dart` | +S5a (`_HitlInfo`, `_HitlRequestCard`, `_detectHitl`) +S5b (`_ArtifactInfo`, `_ArtifactCard`, `_detectArtifacts`) +4 cases en `_renderStep`. Total ≈1489 líneas. |
| `apps/mobile/test/features/hilo/hilo_screen_s5_test.dart` | Suite S5 con 6 tests cubriendo los 4 patrones HITL + render de los 4 kinds de artifact. |

---

## 4. Commits y verificación local

| Commit | Mensaje | Estado |
|---|---|---|
| `7c90146` | `mobile(hilo): S5a HITL approval card + S5b artifact panel` | en `origin/main` |
| `e160706` | `mobile(hilo): tests S5 — 6 cases passed` | en `origin/main` |
| `62f3b53` | `mobile(hilo): fix detector HITL — soporta error: "HITL_REQUIRED" del kernel real` | en `origin/main` |

- **Tests:** `flutter test test/features/hilo/hilo_screen_s5_test.dart` → **6/6 passed**.
- **Build iOS:** `flutter build ios --debug --no-codesign` → `Runner.app` generado limpio.
- **Instalación:** app instalada y corriendo en iPhone físico de Alfredo (UDID `00008150-00044D423E02401C`, iOS 26.3.1, Personal Team configurado en Xcode).

---

## 5. Por qué NO es DONE-feature — bug del LLM-routing (parte de P0.4)

Durante validación E2E real contra `https://ag-ui-gateway-production.up.railway.app/v1/agui/run` con misión que requería operación GitHub:

> **Output observado del LLM (texto plano en `TEXT_MESSAGE_CONTENT`):**
> *"Voy a proceder. Llamando a la herramienta `github`. (Acción: list_prs en el repo el-monstruo) ..."*

**Lo que NO ocurrió:** ningún `TOOL_CALL_START` con `toolCallName: "github_ops"`.
**Consecuencia en la app:** `_detectHitl` no dispara (correctamente — no hay evento HITL real), la card de aprobación nunca aparece, el usuario no puede aprobar ni rechazar nada, y el LLM "alucina" que ejecutó la tool sin haberla ejecutado.

**Diagnóstico canónico (validado con Cowork):** este es **exactamente el patrón de "tool fantasma"** que el DAN clasifica como `tool ghost = fallo de sistema, no mejor esfuerzo`. La causa raíz es la ausencia de **P0.4 (ToolRegistry/ToolExecutor)** — el kernel no tiene un registro tipado de tools del que el LLM pueda hacer function-calling estructurado, así que el modelo cae a narrar la tool en prosa.

**No se puede arreglar desde la app móvil.** La app está haciendo lo correcto: si no hay `TOOL_CALL_START`, no hay HITL card. El fix vive en el kernel (P0.4).

---

## 6. Dependencia bloqueante y aporte a P0.6

- **Bloqueante para DONE-feature:** P0.4-mínimo (ToolRegistry + ToolExecutor + registrar `github_ops` con `requires_approval=true`).
- **Aporte de S5 a P0.6:** se agregó al spec `bridge/cowork_to_e1_P0.4_P0.5_P0.6_SPEC_2026_05_27.md` (línea 73) un **6º patrón anti-ghost** — `test_no_ghost_github_ops` — que codifica esta repro exacta como caso de test parametrizado, marcado `@pytest.mark.skip` hasta que P0.4 lo active. Cuando P0.4 esté DONE y `github_ops` esté registrada, este test debe poder destigarse y pasar verde — eso es la prueba de que el bug observado en S5 quedó cerrado por sistema.

---

## 7. Próximos pasos (orden de Cowork)

1. **P0.5** — `web_search` server-side + cost ledger (sin dependencias).
2. **P0.4-mínimo** — ToolRegistry + ToolExecutor + registrar `web_search`, `skill_read`, **y `github_ops`** (último crítico para desbloquear S5 DONE-feature).
3. **P0.6** — anti-ghost suite con los 6 patrones; activar `test_no_ghost_github_ops` cuando 2 esté DONE.
4. **S5 → DONE-feature** — re-validar E2E en iPhone con misión GitHub real, verificar que la HITL card aparece, aprobar/rechazar, observar `tool_call_completed` con artifact (PR diff). Cerrar con tag `s5-done-feature-<fecha>`.

---

## 8. Tag git asociado

- `s5-done-ui-2026-05-27` — marca este cierre DONE-UI sobre `main` (commit `62f3b53`).

---

🏛️ **S5a + S5b — DECLARADO DONE-UI** (E2E bloqueado por P0.4).

— Manus (Hilo B), 2026-05-27
