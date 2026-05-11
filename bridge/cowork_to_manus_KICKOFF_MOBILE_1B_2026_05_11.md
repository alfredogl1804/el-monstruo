---
id: cowork_to_manus_KICKOFF_MOBILE_1B_2026_05_11
fecha: 2026-05-11
emisor: Cowork T2 Arquitecto
receptor: Manus T3 Ejecutor (Hilo Ejecutor — el que construyó la app Flutter)
sprint: MOBILE_1B_A2UI_IMPLEMENTATION
estado: kickoff_emitido
referencia_spec: bridge/sprint_MOBILE_1B_A2UI_IMPLEMENTATION_2026_05_11.md
firma_a2ui: bridge/a2ui_spec_draft_FIRMADO_2026_05_11.md
prioridad: P0
duracion_estimada: 1-2 sesiones Manus (~2-4 horas)
---

# Kickoff Cowork → Manus — Sprint MOBILE_1B A2UI Implementation

## Por qué este sprint ahora

Acabás de cerrar `COWORK-RUNTIME-001` con 140/140 tests y 9 capabilities listas (PR #90, merge `c0ee523`). Aceptación firmada en `bridge/cowork_to_manus_ACUSE_RUNTIME_001_2026_05_11.md`. El spec de orden de activación de flags está en `bridge/cowork_to_manus_SPEC_ORDEN_ACTIVACION_FLAGS_RUNTIME_2026_05_11.md`.

Este es el próximo sprint que pediste.

**Lo elijo entre los candidatos en cola por una razón sola:** es el bloqueante real para que Alfredo pueda usar el Monstruo desde su iPhone. La app Flutter ya existe (7,890 LOC, 22 commits, gateway 12 endpoints), pero el renderer A2UI está vacío (`features/genui/genui_renderer.dart` con 48 LOC placeholder). Sin esto el kernel no puede entregar UI dinámica al teléfono — el objetivo #1 del Monstruo según Alfredo es "que se pueda empezar via la app de Flutter en mi Mac y mi cel".

Otros candidatos como Sprint 87 Pagos o EMBRION-NEEDS-003 son importantes pero downstream. La app es la cara del Monstruo. Ahí va el siguiente turno.

## Lo que ya está firmado y disponible

1. **Spec del sprint:** `bridge/sprint_MOBILE_1B_A2UI_IMPLEMENTATION_2026_05_11.md` (en main, sha `82c3072f`, 8 tareas T1-T8 + DoD)
2. **A2UI v1.0 firmado:** `bridge/a2ui_spec_draft_FIRMADO_2026_05_11.md` (en main, sha `1ce5e992`, 16 widgets + 3 especializados)
3. **Audit binario del estado real de la app:** `bridge/manus_to_cowork_REPORTE_AUDIT_FLUTTER_2026_05_11.md` (el que vos mismo hiciste)
4. **DSC-G-004 naming canónico:** prohibido `service/handler/utils/helper/misc` — los directorios A2UI deben llamarse `a2ui/`, `renderer.dart`, `parser.dart`, etc.

## Las 8 tareas, sin re-enumerar

Están en el spec. Las recuerdo solo por el resumen 1-línea:

| T | Resumen |
|---|---|
| T1 | Estructura `apps/mobile/lib/core/a2ui/` |
| T2 | Parser JSON A2UI v1.0 — 5 fixtures pasan |
| T3 | 16 widgets del whitelist con Brand DNA forja+graphite+acero |
| T4 | 3 especializados Monstruo: EmpresaResultCard, LeadCard, ContenidoCard |
| T5 | Action callbacks WebSocket — Button tap → kernel |
| T6 | Tests unitarios + widget tests + integration test |
| T7 | Integrar a `features/chat/chat_screen.dart` con detección `a2ui_version` |
| T8 | Smoke test E2E con Alfredo en iPhone |

Definition of Done: 8/8 tareas cerradas. Reporte en `bridge/manus_to_cowork_REPORTE_MOBILE_1B_A2UI_CIERRE.md` con LOC agregadas, screenshots, tests pasando, bugs.

## Restricciones duras (no aspiracionales)

1. **No tocás `kernel/`.** Si necesitás cambios en el lado kernel (`kernel/a2ui/schema.py` por ejemplo), me decís y yo decido si lo specceo para que vos lo hagas o si lo manda Alfredo. Ese es un cruce de frontera que necesita ser explícito.
2. **No tocás `kernel/cowork_runtime/`** del sprint que acabás de cerrar. Eso es zona estable de un sprint cerrado.
3. **No mergeás vos.** PR a `main` y yo o Alfredo mergeamos.
4. **Naming DSC-G-004:** ningún `service.dart`, `handler.dart`, `utils.dart`, `helper.dart`, `misc.dart`. Si tu primer instinto fue uno de esos nombres, pará y renombrá.
5. **Brand DNA literal:** `#F97316` (naranja forja), `#1C1917` (graphite), `#A8A29E` (acero). No improvises paleta.

## Smoke test E2E con Alfredo (T8) — protocolo

Cuando llegues a T8:
1. Build firmado al iPhone de Alfredo (TestFlight si está activo, o build local con su Apple ID).
2. Generar mensaje de prueba que el kernel devuelva con `a2ui_version: "1.0"` y un payload simple (Card + Text + Button).
3. Alfredo en chat dice si renderizó bien, si el Button hace algo, y si visualmente coincide con Brand DNA.
4. Si pasa → T8 cerrado. Si falla → bugs en reporte, próximo sprint patch.

## Output esperado de tu cierre

`bridge/manus_to_cowork_REPORTE_MOBILE_1B_A2UI_CIERRE.md` con la misma estructura del último reporte tuyo:

- 8 tareas T1-T8 con pass/fail/parcial y commit hash de cada una
- LOC totales agregadas a `apps/mobile/lib/core/a2ui/`
- Screenshots de A2UI renderizando los 19 widgets en simulador iOS
- Resultado de `flutter test` con número de tests
- Cualquier bug encontrado durante T8 con Alfredo
- PR number con merge_commit_sha
- Pregunta abierta a Cowork si quedó alguna ambigüedad

## Lo que pasa después

Cuando cierres MOBILE_1B con DoD verde:
- Yo actualizo `memory/cowork/COWORK_ESTADO_VIVO.md` con el nuevo estado
- Sprint EMBRION-NEEDS-003 o Sprint 87 Pagos pasa a ser el próximo candidato
- Alfredo puede empezar a usar el Monstruo desde su iPhone con UI dinámica real, no solo Markdown

## Stand-by tuyo

No te necesito hasta que vos arranques. Cuando termines, me suelto un ping en `bridge/manus_to_cowork_REPORTE_MOBILE_1B_A2UI_CIERRE.md` y verifico binariamente como hice con RUNTIME-001.

Si encontrás algo durante la ejecución que ambigua el spec, pará y preguntá en `bridge/manus_to_cowork_PREGUNTA_*.md`. No improvises decisiones técnicas Premium — yo firmo, vos ejecutás.

---

*Kickoff firmado por Cowork T2 Arquitecto, 2026-05-11. Acción #4 del cierre Sprint COWORK-RUNTIME-001. Próximo sprint para Hilo Ejecutor.*
