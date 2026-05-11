---
id: sprint_MOBILE_1B_A2UI_IMPLEMENTATION_2026_05_11
fecha_spec: 2026-05-11
arquitecto: Cowork T2
ejecutor_propuesto: Manus Hilo Ejecutor (el que construyó la app Flutter)
estado: spec_firme_pendiente_firma_a2ui
prioridad: P0
duracion_estimada: 1-2 sesiones Manus (~2-4 horas reales)
desbloquea:
  - Capabilities cotidianas (Visual Search, Photo Intelligence, etc — Cap 4 APP_VISION)
  - Cockpit denso con 12-15 superficies (Cap 3 APP_VISION)
  - Modo Confidente (Cap 6 APP_VISION)
  - Smart Rendering como capability (Cap 4 v1.2)
  - EmpresaResultCard del pipeline E2E Sprint 87
cruza_con:
  - bridge/a2ui_spec_draft_para_firma.md (BLOQUEANTE: requiere firma Alfredo)
  - docs/EL_MONSTRUO_APP_VISION_v1.md (cap 1 A2UI v0.9)
  - DSC-G-004 (naming canónico — services prohibido)
  - manus_to_cowork audit binario del Hilo Ejecutor 2026-05-11
---

# Sprint Mobile 1.B — A2UI Rendering Implementation

## Contexto verificado binariamente

Estado real de la app Flutter al 2026-05-11 (verificado por Hilo Ejecutor + Cowork via `find`, `git log`, `grep` ejecutables):

- App Flutter v0.1.0+1 compilada, corriendo en Mac + iPhone de Alfredo
- 7,890 LOC en `apps/mobile/lib/`
- 10 features funcionales
- Gateway propio en `apps/mobile/gateway/` con 622 LOC + 12 endpoints (REST + WebSocket)
- 22 commits hasta 2026-05-02
- `features/genui/genui_renderer.dart` existe pero solo 48 LOC = placeholder esperando spec A2UI firmado

## Bloqueante: firma A2UI Spec Draft

**Path:** `bridge/a2ui_spec_draft_para_firma.md`

16 tipos de componentes whitelist propuestos: Stack, Card, Section, Text, Markdown, Image, Link, Code, Divider, Button, ButtonGroup, KeyValueList, Table, Badge, Progress, Stepper + 3 especializados Monstruo: EmpresaResultCard, LeadCard, ContenidoCard.

## Tareas (8 totales)

### T1 — Estructura `core/a2ui/` (cumple DSC-G-004 + spec Mobile 1)
Crear `apps/mobile/lib/core/a2ui/` con renderer.dart, parser.dart, types/, actions.dart.

### T2 — Parser JSON A2UI v1.0
Implementar parser que reciba JSON y retorne tree de widgets Dart. Aceptación: 5 fixtures pasan.

### T3 — Implementar los 16 tipos del whitelist
1 widget Dart por tipo. Usar Brand DNA forja+graphite+acero. Slots para componentes con copy.

### T4 — Componentes especializados Monstruo
EmpresaResultCard, LeadCard, ContenidoCard según spec draft.

### T5 — Action callbacks WebSocket
Button tap → kernel via WebSocket con action_id + payload.

### T6 — Tests
Unit tests parser, widget tests cada tipo, integration test chat→A2UI.

### T7 — Integrar al chat existente
`features/chat/chat_screen.dart` detecta `a2ui_version` field → renderiza vía A2UIRenderer.

### T8 — Smoke test end-to-end con Alfredo
Manus envía build firmado al iPhone con A2UI activo. Alfredo prueba caso real.

## Definition of Done

8 de 8 tareas cerradas = sprint cerrado. Capability A2UI desbloqueada para sprints downstream.

## Output esperado

Hilo Ejecutor reporta cierre en `bridge/manus_to_cowork_REPORTE_MOBILE_1B_A2UI_CIERRE.md` con 8 tareas pass/fail, LOC agregadas, screenshots de A2UI renderizando, tests pasando, bugs encontrados.

---

*Spec firmado por Cowork como Arquitecto T2. 2026-05-11. Bajo modo "actuar sin preguntar" respetando clasificación S7.*
