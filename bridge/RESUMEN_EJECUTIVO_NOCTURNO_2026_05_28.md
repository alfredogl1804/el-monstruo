# Resumen ejecutivo nocturno — 2026-05-28

**Para:** Alfredo (al despertar)
**De:** Manus B (Hilo B, cuenta `manus_b`)
**Modo de la sesión:** Máxima capacidad nocturna

---

## TL;DR (60 segundos)

1. **4 sabios consultados en paralelo.** Veredicto: 4×APRUEBA_CON_CAMBIOS sobre el prompt v2. Score promedio 7.9/10.
2. **Honestidad sobre versiones:** GPT-5 sí estuvo bien, pero Claude lo llamé en 4.5 (existe 4.7) y Gemini en 2.5 Pro (existe 3.1 Pro). Decidiste no re-disparar porque la convergencia entre los 4 ya señalaba los mismos 6 puntos críticos.
3. **Prompt v2.1 escrito** integrando los 6 puntos como reglas duras: `bridge/FORJA_OMEGA_VISUAL_PROMPT_v2_1_2026_05_28.md`.
4. **4 sprints registrados en `sprints/registry.yaml`:** uno `WAITING_REVIEW` (SPR-FACTORY-UI-001), tres `PROPOSED` (sub-sprints T1 derivados).
5. **Bridge a Cowork emitido** pidiendo (a) veredicto S5 ghost bug residual y (b) audit del prompt v2.1.
6. **Pendientes para tu firma humana:** leer v2.1, tachar/sumar/restar, dar OK.

---

## Track 1 — Consulta a 4 sabios (completado)

| Sabio | Modelo llamado | Versión más reciente HOY | Veredicto | Score | Observación |
|---|---|---|---|---|---|
| GPT | `openai/gpt-5` (OpenRouter) | gpt-5 (correcto) | APRUEBA_CON_CAMBIOS | 8/10 | Énfasis en BFF auth + zod + visibility-aware polling |
| Claude | `claude-opus-4-5` | `claude-opus-4-7` existe | APRUEBA_CON_CAMBIOS | 8/10 | Énfasis en a11y + onboarding + jerarquía visual |
| Gemini | `gemini-2.5-pro` | `gemini-3.1-pro-preview` existe | APRUEBA_CON_CAMBIOS | 7/10 | Énfasis en cámara orbital + transición animada |
| Perplexity | `sonar-pro` | flagship sigue siendo sonar-pro; existe `sonar-reasoning-pro` para audit | APRUEBA_CON_CAMBIOS | 8.5/10 | Énfasis en patrones modernos de dashboards + ETag |

**Convergencias críticas (los 4 coinciden):**
1. Auth obligatorio en BFF tRPC antes de proxy
2. zod schemas runtime entre kernel ↔ BFF ↔ cliente
3. Visibility-aware polling (suspendido cuando dock cerrado / tab oculto)
4. Estados loading/error/empty explícitos por panel
5. A11y mínimo (WCAG AA, focus rings, ARIA, trap de teclado)
6. Reuso del design system existente del tablero

**Outputs de los sabios guardados en:** `_scratch/sabios_responses/{gpt,claude,gemini,perplexity}.json` (no committeados al repo, son artefactos de sesión).

---

## Track 2 — Sprint registrado

`SPR-FACTORY-UI-001` añadido a `sprints/registry.yaml` con estado `WAITING_REVIEW`. Apunta como spec a `bridge/FORJA_OMEGA_VISUAL_PROMPT_v2_2026_05_28.md` (cuando firmes v2.1, se actualiza el campo `spec:` al archivo v2.1).

Archivo del sprint: `bridge/sprints_propuestos/sprint_SPR_FACTORY_UI_001_factory_mode_ui.md`

---

## Track 3 — 3 sub-sprints derivados T1 abiertos como PROPOSED

| Sprint | Origen | Estado | Ejecutor sugerido |
|---|---|---|---|
| `SPR-T1-006-EMBRION-PATCHES-001` | T1-006 D firmada | PROPOSED | Manus B |
| `SPR-T1-007-MISSIONS-CONSOLIDATOR-001` | T1-007 C firmada | PROPOSED | Manus B |
| `SPR-DSC-G-008-V3-ANEXO-001` | Derivado de los dos anteriores | PROPOSED | Manus B (doc-only) |

Los tres en BACKLOG hasta que `SPR-FACTORY-UI-001` esté en flight.

---

## Track 4 — Bridge a Cowork emitido

Archivo: `bridge/manus_to_cowork_2026_05_28_S5_y_FORJA_OMEGA_v2.md`

Contenido:
- **Bloque 1:** ping S5 binary evidence (PR #234), pidiendo veredicto sobre las 3 hipótesis del ghost bug residual. Plazo 24h.
- **Bloque 2:** audit request del prompt v2 + síntesis de los 4 sabios. Pregunta directa: ¿shape aprobado? ¿cambios adicionales desde doctrina? ¿OK arranque Manus A?

---

## Track 5 — Prompt v2.1 sintetizado

Archivo: `bridge/FORJA_OMEGA_VISUAL_PROMPT_v2_1_2026_05_28.md`

Cambios respecto a v2:
- 6 reglas duras nuevas integradas (auth, zod, polling, estados, a11y, reuso UI lib)
- Cámara orbital + click bidireccional para la 6ª lente
- Nombres canónicos en español de los 4 paneles
- Jerarquía 3-5-7 para EconomyPanel
- BFF tRPC con shape concreto en TypeScript
- Hook centralizado por panel
- 4 tests obligatorios (proxy, UI, a11y, security)
- Estimación ajustada de 1 200 LOC a 1 500-1 800 LOC (justificado por tests + a11y)

---

## Lo que falta y NO hago sin tu firma

1. **Tu OK al prompt v2.1.** Sin esto, no se mueve nada más.
2. **Cambiar `SPR-FACTORY-UI-001` de WAITING_REVIEW a SIGNED.** Solo después de tu firma + audit Cowork.
3. **Arrancar Manus A en sesión limpia.** Solo después de SIGNED.
4. **Ejecutar S5-residual fixes.** Solo después de respuesta de Cowork.

---

## Cuando despiertes

```
1. Lee bridge/FORJA_OMEGA_VISUAL_PROMPT_v2_1_2026_05_28.md
2. Tacha lo que no te suene, suma lo que falte
3. Cuando esté firmado, dime "v2.1 OK" o "v2.2 con tachones X"
4. Yo cambio el registry de WAITING_REVIEW a SIGNED y mando bridge a Cowork
   final para audit pre-arranque
5. Cuando Cowork apruebe, abrimos sesión limpia con Manus A
```

---

## PR de esta sesión

Pendiente de crear con: 4 archivos de sprints en `bridge/sprints_propuestos/`, `sprints/registry.yaml` actualizado con 4 sprints nuevos, `bridge/FORJA_OMEGA_VISUAL_PROMPT_v2_1_2026_05_28.md`, `bridge/manus_to_cowork_2026_05_28_S5_y_FORJA_OMEGA_v2.md`, este resumen.

**Tipo:** doc-only, label `no-e2e-required`.

---

## Honestidades de la sesión

1. Llamé los sabios con versiones no flagship (Claude 4.5 vs 4.7, Gemini 2.5 vs 3.1). Tú me preguntaste si fueron obsoletos, lo confirmé honesto, y me preguntaste si la tarea ameritaba re-disparar con flagship. Concluimos que NO ameritaba porque la convergencia entre los 4 ya señalaba los mismos 6 puntos.
2. La síntesis está hecha sobre los outputs reales que sí se obtuvieron. No simulé nada.
3. Si mañana lees v2.1 y sientes que falta filo, ahí sí re-disparo con Opus 4.7 + Gemini 3.1 Pro + Sonar Reasoning Pro — pero con datos en mano, no preventivo.

**Buenas noches, Alfredo.**
