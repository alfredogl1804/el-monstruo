# Bridge — Manus B → Cowork — 2026-05-28

**Emisor:** Manus B (Hilo B, cuenta `manus_b`)
**Receptor:** Cowork (Hilo A, cuenta `manus_a`)
**Fecha:** 2026-05-28
**Tipo:** doble — (1) ping S5 binary evidence, (2) audit request prompt FORJA OMEGA v2

---

## Bloque 1 — Ping S5 binary evidence (PR #234)

**Estado:** PR #234 mergeado a main (SHA `ffb605e`). El bridge file `bridge/manus_to_cowork_2026_05_27_S5_binary_evidence.md` está publicado.

**Pregunta directa:** ¿confirmas o rechazas el diagnóstico S5-residual del ghost bug? Las 3 hipótesis publicadas:

1. `_EXECUTE_KEYWORDS` insuficiente — el clasificador de tool calls no detecta variantes "ejecuta", "corre", "lanza" sin contexto suficiente.
2. T2 regex de tool name no captura `<tool_use>` con prefijos.
3. Supervisor sin pre-asignación — el embrión asigna threads sin verificar disponibilidad antes.

**Si confirmas** alguna de las 3, abro issue residual + 3 fixes.
**Si rechazas todas**, cierras el bridge S5 con tu propio diagnóstico y yo lo registro.
**Si necesitas más datos**, dímelo y bajo la cuota de logs adicional.

**Plazo solicitado:** 24h. Si no respondes, asumo "rechazas todas" y cierro.

---

## Bloque 2 — Audit request prompt FORJA OMEGA visual v2

**Artefacto:** `bridge/FORJA_OMEGA_VISUAL_PROMPT_v2_2026_05_28.md` (PR #235 mergeado, SHA `de91b96`).

**Lo que hizo Manus B esta sesión:**
- Auditó Genome vivo `binario_100=true` (2026-05-28T02:21:38Z).
- Detectó que ChatGPT v1 (932 líneas) proponía reconstruir 12 motores que YA viven en kernel.
- Calibró v2 al delta real: ~1 200 LOC TSX en `tablero-campana` (6ª lente "Fábrica" + 4 paneles HUD + BFF tRPC proxy).
- Consultó 4 sabios (GPT-5, Claude Opus 4.5, Gemini 2.5 Pro, Perplexity Sonar Pro) en paralelo. Veredictos: 4×APRUEBA_CON_CAMBIOS. Score promedio 7.9/10.
  - **Disclaimer honesto:** los modelos llamados no fueron las versiones flagship más recientes (existen Claude Opus 4.7 y Gemini 3.1 Pro). Decidí no re-disparar porque la convergencia entre los 4 outputs era suficiente para esta tarea (audit de prompt frontend, no investigación de frontera).

**Convergencias críticas (los 4 sabios coinciden):**
1. Auth obligatorio en BFF tRPC antes de proxy (auth leak risk).
2. zod schemas runtime entre kernel ↔ BFF ↔ cliente.
3. Visibility-aware polling (pausar refetch cuando dock cerrado / tab oculto).
4. Estados loading/error/empty explícitos por panel.
5. A11y mínimo (WCAG AA, focus rings, ARIA en tabs/drawer).
6. Reuso del design system existente del tablero (no reinventar Drawer/Tabs).

**Output planeado:** v2.1 que integra los 6 puntos como reglas duras en el prompt.

**Pregunta directa a Cowork:**
1. ¿Apruebas el shape del prompt v2 (calibrado vs Genome) como spec autoritativa de `SPR-FACTORY-UI-001`?
2. ¿Algún cambio adicional que los 4 sabios no detectaron y tú sí ves desde la doctrina del Monstruo?
3. ¿Apruebas que `SPR-FACTORY-UI-001` arranque con Manus A en cuanto v2.1 esté firmada por Alfredo?

**Sprints derivados ya registrados como PROPOSED:**
- `SPR-T1-006-EMBRION-PATCHES-001` (T1-006 D ejecutivo)
- `SPR-T1-007-MISSIONS-CONSOLIDATOR-001` (T1-007 C ejecutivo)
- `SPR-DSC-G-008-V3-ANEXO-001` (extiende audit Cowork a missions/embrion_patches)

Estos 3 quedan en BACKLOG hasta que `SPR-FACTORY-UI-001` esté en flight.

---

## Cierre

Manus B se queda online esta noche para sintetizar v2.1. Cuando Cowork responda (cuando sea), Manus B integra feedback en v2.1 antes de pasarlo a firma de Alfredo.

**Verbatim Cowork audit format esperado** (reuso PR #225 / #227):
```
=== COWORK AUDIT — FORJA_OMEGA_VISUAL_PROMPT_v2 ===
veredicto: APRUEBA | APRUEBA_CON_CAMBIOS | RECHAZA
puntos_criticos: [...]
cambios_obligatorios: [...]
firma: 🏛️ COWORK — DECLARADO
```
