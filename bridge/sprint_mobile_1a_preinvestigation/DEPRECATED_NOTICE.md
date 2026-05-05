# ⚠️ DEPRECATED — Sprint Mobile 1.A spec viejo anulado

> **Fecha de anulación:** 2026-05-05
> **Spec original:** `bridge/sprint_mobile_1a_preinvestigation/spec_file_upload_ux_polish.md` (commit `1c5b05d`)
> **Estado:** **NO EJECUTAR. Visión obsoleta.**
> **Razón:** la visión de la app Flutter cambió radicalmente después de feedback magna de Alfredo el mismo día.

---

## Por qué se anula

El spec original asumía que la app Flutter era "chat con AI mejorado + file upload + UX polish". Después de iterar con Alfredo el 2026-05-05, la visión correcta es **mucho más ambiciosa**:

**UNA sola app Flutter con dos modos del mismo cuerpo:**
- **Modo Daily** — superficie minimalista Apple/Tesla, conectada nativamente a WhatsApp + Maps + Google + Mail + Calendar. Reemplaza 20 apps con 1. Para cotidianidad de personas reales.
- **Modo Cockpit** — superficie densa Bloomberg + Cursor + Manus, 12-15 pantallas con todo el poder del Monstruo (Catastro + Embriones + Guardian + Memento + Replay + Computer Use + FinOps + etc.). Para Alfredo como arquitecto.

Ambos modos comparten **mismo bundle, mismo state, mismo backend, mismo brand DNA**. El toggle entre modos es vía biometría + gesto secreto (Daily es lo que ven todos, Cockpit es exclusivo del owner).

El spec viejo NO contempla:
- La existencia del Modo Cockpit
- Las integraciones nativas (WhatsApp, Maps, Mail, Google) como núcleo del Modo Daily
- El A2UI streaming-first como base de outputs
- La filosofía "menos es más" aplicada al Modo Daily
- El toggle biometría entre modos
- La validación contra los 15 Objetivos y 8 Capas Transversales

## Qué se preserva del commit `1c5b05d`

- ✅ `bridge/a2ui_spec_draft_para_firma.md` — sigue siendo válido. A2UI es transversal a ambos modos.
- ✅ `bridge/checklist_ios_code_signing_para_alfredo.md` — sigue siendo válido. Necesario para build firmado a iPhone físico de cualquier sprint Mobile futuro.

## Qué se descarta del commit `1c5b05d`

- ❌ `bridge/sprint_mobile_1a_preinvestigation/spec_file_upload_ux_polish.md` — anulado por este aviso.
- ❌ La task consolidada para Hilo Memento que apuntaba al spec viejo — Alfredo confirmó que **NO se la mandó al Memento**, por lo que ningún trabajo arrancó bajo visión obsoleta.

## Próximos specs (en redacción / pendientes)

Cuando Alfredo firme la visión completa de la app (en curso), Cowork (Hilo B) escribe:

1. `docs/EL_MONSTRUO_APP_VISION_v1.md` — documento magna de visión (~30-50 páginas)
2. `bridge/sprint_mobile_1_preinvestigation/spec_esqueleto_unificado_app.md` — Sprint Mobile 1: chasis + mode_provider + biometría toggle + A2UI renderer streaming + brand DNA, sin pantallas todavía
3. Sprints Mobile 2-6 — cada uno con su spec firmado

## Política firmada que aplica

**Mientras Alfredo coordina activamente, NINGÚN hilo Manus entra en standby.** El Hilo Memento se mantiene libre hasta que Alfredo confirme visión completa, momento en el que arranca Sprint Mobile 1 con spec firmado en frío.

— Cowork (Hilo B)
