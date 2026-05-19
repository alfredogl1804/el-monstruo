# Cockpit Local — Fase 2 MVP Supervisado

> ⚠️ **SUPERVISED LOCAL DEMO — no production control plane — no R1 authorization**
>
> T1 = Alfredo. ChatGPT-0 = integrador, NO T1. Approve/reject visual NO equivale a firma T1 productiva. Cero side-effects productivos. v2.2 DRAFT (commit `148a502`), NO canon, NO runtime.

---

## 1. Cómo abrir local

Este cockpit es un **archivo HTML estático local** que se renderiza en cualquier browser moderno sin servidor, sin build step y sin dependencias remotas.

```bash
# Opción A — Abrir directo en browser
open apps/cockpit/index.html   # macOS
xdg-open apps/cockpit/index.html  # Linux
start apps/cockpit/index.html  # Windows

# Opción B — Servidor estático local (recomendado si tu browser bloquea fetch file://)
cd apps/cockpit
python3 -m http.server 8000
# Luego abrir http://127.0.0.1:8000/index.html
```

Las fixtures viven en `apps/cockpit/fixtures/`:

- `diagnostic.mock.json` — heartbeat, budget, cycles, errors, blockers, silence state
- `proposals.mock.json` — proposals visuales con approve/reject DISABLED

**Cero fetch a producción.** El cockpit carga exclusivamente fixtures locales. Si detectas cualquier request HTTP saliente a `*.railway.app`, `*.supabase.co`, `*.anthropic.com`, `*.openai.com` o cualquier dominio productivo, **eso es un bug y debe reportarse a Cowork T2-A**.

---

## 2. Qué es el cockpit

- **MVP visible supervisado local** para inspeccionar visualmente el estado mock del ecosistema El Monstruo.
- **Lectura pasiva** de fixtures estáticos versionados en repo.
- **Demo de UI** para iterar lenguaje, layout y disclaimers antes de cualquier conexión productiva.
- **Espacio de diseño** para flujos approve/reject sin riesgo (todos los flujos están **DISABLED** en fixtures).
- **Artefacto de Fase 2** del Sprint HITL Cockpit (branch `supervised/SPR-HITL-COCKPIT-001-hitl-cockpit-mvp`).

---

## 3. Qué NO es

- **NO es control plane productivo.** Cero side-effects sobre Supabase, Anthropic, OpenAI, Railway, kernel-monstruo, embriones, Memento, Anti-Dory, learning memory.
- **NO es runtime.** v2.2 sigue DRAFT (commit `148a502`).
- **NO es canon.** Ninguna interacción con el cockpit canoniza patrones, decisiones ni doctrina.
- **NO sustituye firma T1.** Approve/reject visual NO equivale a firma productiva de Alfredo. Cualquier acción productiva real requiere bridge file separado con sign-off verbatim T1.
- **NO autoriza R1.** Nightly Builder R1 autónomo sigue **BLOQUEADO** doctrinalmente. El cockpit no puede activar R1 bajo ninguna circunstancia.
- **NO actualiza APP_VISION** ni cierra PRE-IA.
- **NO escribe a Memento, Anti-Dory, learning_memory ni cualquier tabla Supabase.**
- **NO toca secrets** ni credenciales productivas.
- **NO usa auth real, user_id real ni RLS productiva.**
- **NO persiste estado** vía localStorage / sessionStorage (cualquier estado visual vive en memoria de la pestaña).
- **NO expone raw chain-of-thought** de embriones ni Sabios. Solo `redacted_cycle_summary`.

---

## 4. Estado actual

| Dimensión | Estado |
|---|---|
| Tipo | **Read-only local demo** |
| Production control plane | **NO** |
| POST approve/reject productivo | **NO** (todos los botones `DISABLED`) |
| `user_id=anonymous` blocker | **ACTIVO** (audit OPP-NB-023 → INSUFFICIENT_EVIDENCE) |
| Nightly Builder R1 | **BLOQUEADO** |
| OPP-NB-001 memory_routes E2E tests | **R1_CANDIDATE_NOT_APPROVED** |
| v2.2 | **DRAFT** (commit `148a502`, NO canon, NO runtime) |
| T1 | **Alfredo** (único firmante productivo) |
| ChatGPT-0 | **Integrador**, NO T1 |
| Auditor doctrinal | **Cowork T2-A** |
| Auditor de este sprint | **Perplexity** |

---

## 5. Fixtures

### 5.1 Cómo están marcadas

Todos los archivos en `apps/cockpit/fixtures/` llevan:

- Campo `_meta.fixture_type = "MOCK_DATA"`
- Campo `_meta.do_not_use_as_evidence = true`
- Por cada item: `label = "MOCK_DATA"`, `freshness = "stale"`, `action_allowed = "DISPLAY_ONLY"`
- Para proposals: `approve_reject_mode = "DISABLED"` adicional + `t1_signoff_required = false` + `r1_authorization_implied = false`

### 5.2 Por qué no son evidencia productiva

- Son **archivos estáticos versionados** en repo, no provienen de producción ni de runtime real.
- No reflejan estado actual de embriones, Memento, Anti-Dory, Supabase ni ninguna fuente operativa.
- Diseñados exclusivamente para **renderizar el layout visual del cockpit** y validar disclaimers/banners.
- Cualquier valor numérico (budget, cycles, ocurrencias) es **placeholder** sin correlato productivo.
- Las proposals listadas (`MOCK-PROP-001/002/003`) NO existen como proposals reales en ningún sistema productivo.
- Las referencias a paths `bridge/nightly_builder/MOCK-OPP-NB-XXX_*.md` están explícitamente marcadas como `(MOCK reference)` en `audit_trail_path_label` — son cadenas de ejemplo, no paths reales.

---

## 6. Límites doctrinales

El cockpit **NO puede**:

- Llamar a Supabase (lectura ni escritura)
- Acceder a secrets, credenciales ni env vars productivos
- Usar auth, `user_id` real, `profile_id` real ni evaluar RLS productiva
- Escribir a Memento, Anti-Dory, learning_memory, `cowork_sesiones`, `embrion_memoria`
- Modificar `docs/EL_MONSTRUO_APP_VISION_v1.md`
- Modificar `discovery_forense/CAPILLA_DECISIONES/` ni emitir frase canónica 🏛️
- Cerrar PRE-IA ni ejecutar `update_issue state=closed`
- Hacer fetch a `*.railway.app`, `*.supabase.co`, `*.anthropic.com`, `*.openai.com`, `*.google.com` ni cualquier dominio productivo
- Activar Nightly Builder R1 ni ninguna variante de R1
- Ejecutar tests reales (vitest, pytest, cualquier test runner)
- Persistir estado vía `localStorage` o `sessionStorage`
- Renderizar `chain_of_thought`, `internal_reasoning`, `raw_thoughts` ni cualquier campo raw del LLM
- Inferir permiso operacional desde el campo `allowed_actions` o `action_allowed` (siempre `DISPLAY_ONLY`)

---

## 7. Siguiente decisión

La siguiente decisión sobre este cockpit corresponde a **T1 = Alfredo**, no a ChatGPT-0 ni a Cowork.

**Decisiones candidatas que pueden plantearse:**

1. **Aceptar Fase 2 como cerrada** — cockpit local supervisado queda archivado como artefacto MVP visible.
2. **Iterar Fase 2** — agregar más fixtures, refinar disclaimers, iterar lenguaje §4 Cowork audit.
3. **Promover a Fase 3** (conectar a producción read-only) — requiere firma T1 separada + audit Cowork T2-A previa + cada endpoint productivo firmado individualmente.
4. **Pausar indefinidamente** — cockpit queda en branch supervisada sin merge ni iteración.
5. **Descartar Fase 2** — cerrar branch sin merge, archivar como evidence-only.

**Bloqueado hasta firma T1 explícita:**

- PR a `main` desde branch supervisada
- Deploy a cualquier dominio público (Vercel, Netlify, GitHub Pages, etc.)
- Habilitación de approve/reject con side-effects productivos
- Conexión a Supabase, Anthropic, OpenAI, Railway, kernel-monstruo
- Resolución del blocker `user_id=anonymous` (depende de OPP-NB-024/025/026 R0 bundles + clasificación T1 binaria)
- Promoción de Nightly Builder R1 desde el cockpit

---

## 8. Audit trail

- **Sprint:** COCKPIT-SPRINT-003 — Fixtures + README
- **Branch:** `supervised/SPR-HITL-COCKPIT-001-hitl-cockpit-mvp` (NO main, NO PR todavía)
- **Ejecutor:** Claude Cowork-Code
- **Auditor:** Perplexity (revisión pendiente)
- **Auditor doctrinal:** Cowork T2-A (audit previo §4 Frases 1-5 + matriz doctrinal)
- **Origen contextual:** ChatGPT-0 batch 002 "Cockpit Productive Consolidation"
- **Doctrina vigente:** DSC-MO-006/007/008/009/010/011 + DSC-S-001 a S-016 + DSC-G-008 v4 + F#1-F#23 + S1-S11 (CLAUDE.md)

---

## 9. Reportar bugs / desviaciones

Cualquier comportamiento del cockpit que viole los límites doctrinales arriba debe reportarse de inmediato a **Cowork T2-A** vía bridge file en `bridge/cockpit_violations_YYYY_MM_DD.md`. En particular:

- Fetch HTTP a cualquier dominio productivo
- Botón que ejecute side-effect productivo
- Render de raw chain-of-thought o internal reasoning
- Persistencia de estado vía localStorage/sessionStorage
- Modificación de archivos fuera de `apps/cockpit/`
- Cualquier intento de canonizar patrón o cerrar PRE-IA desde la UI

---

**🏛️ El Monstruo · Cockpit local Fase 2 · NO control plane · v2.2 DRAFT (commit `148a502`), NO canon, NO runtime · Nightly Builder R1 BLOQUEADO · OPP-NB-001 memory_routes `R1_CANDIDATE_NOT_APPROVED` · `anonymous` BLOCKER preventivo · T1 = Alfredo firma cualquier acción productiva mediante bridge separado.**
