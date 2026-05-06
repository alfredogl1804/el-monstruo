# Sprint Mobile 5 — Modo Cockpit Fase 3: 5 Finales = CARA DEL MONSTRUO COMPLETA (Computer Use, Coding, Hilos Manus, Bridge, Settings+Admin)

**Estado:** Propuesto  
**Hilo:** Ejecutor (Alfredo)  
**ETA (actualizado):** 15-30 min reales (UI stubs + data binding)  
**Objetivo Maestro:** #1 (Valor real) + #14 (Guardián)

---

## Audit Pre-Sprint

**Cockpit Phase 3 Scope:**
- 5 final high-impact surfaces
- Focus: Computer control, coding, agents, navigation, settings
- Completion: 15 total surfaces (5 Daily + 10 Cockpit after mobile_3/4)
- Milestone: "CARA DEL MONSTRUO COMPLETA"

---

## Tareas del Sprint

### Tarea 1: Computer Use / Sandbox — Remote Control UI

**Descripción:**
Interfaz para ejecutar computer use tasks (browser automation, file operations).

**UI Layout:**
```
┌────────────────────────────────────────┐
│ Computer Use / Sandbox            [⌨️]│
├────────────────────────────────────────┤
│                                        │
│ 🖥️ ACTIVE SESSION                     │
│    Device: MacBook Pro (5 mins active) │
│    Resolution: 1440 x 900              │
│    Status: 🟢 Connected                │
│    [Screenshot] [Disconnect]           │
│                                        │
│ ┌────────────────────────────────────┐│
│ │ [SCREENSHOT PREVIEW - 1440x900]    ││
│ │ ┌──────────────────────────────┐  ││
│ │ │ (Live screen capture)        │  ││
│ │ │                              │  ││
│ │ │ Clickable region detection   │  ││
│ │ │ [Click here to interact]     │  ││
│ │ │                              │  ││
│ │ └──────────────────────────────┘  ││
│ └────────────────────────────────────┘│
│                                        │
│ ⌨️ COMMAND INPUT                       │
│ [Type command or click on screen]      │
│ ┌────────────────────────────────────┐│
│ │ click(coordinate) | type(text)    ││
│ │ key(chord) | screenshot()          ││
│ │ [Send] [Clear] [History]           ││
│ └────────────────────────────────────┘│
│                                        │
│ 📋 HISTORY                             │
│ • screenshot() — 2m ago               │
│ • click(640, 360) — 1m ago            │
│ • type("Hello") — 30s ago             │
│ [Clear history]                        │
│                                        │
└────────────────────────────────────────┘
```

**Deliverables:**
- Screenshot viewer: Live display from connected device
- Click detection: Clickable regions highlighted
- Command input: Type-based commands (click, type, key, screenshot)
- History: Log of recent actions
- Session management: Connect/disconnect

**Metrics:**
- Files: 2 (computer_use_view.dart, screenshot_viewer.dart)
- Latency: Screenshot refresh < 500ms
- Test coverage: >75% (mock device)

---

### Tarea 2: Coding Embedded — IDE-Lite Integration

**Descripción:**
Editor de código integrado para editar archivos del proyecto en tiempo real.

**UI Layout:**
```
┌────────────────────────────────────────┐
│ Coding — Embedded IDE             [💻]│
├────────────────────────────────────────┤
│ [kernel/engine.py] [kernel/nodes.py] │ ← Tabs
│ [Close all] [New file]                │
├────────────────────────────────────────┤
│                                        │
│ 1  | def execute_stream(self):        │
│ 2  |     """Main LangGraph execution" │
│ 3  |                                 │
│ 4  |     # Load context             │
│ 5  |     context = self.enrich(...) │
│ 6  |                                 │
│ 7  |     # Execute nodes            │
│ 8  |     for node in self.graph:    │
│ 9  |         yield node.run(...)    │
│                                        │
│ ┌────────────────────────────────────┐│
│ │ Syntax: Python | Theme: Dark      ││
│ │ [Format] [Lint] [Save] [Discard]  ││
│ └────────────────────────────────────┘│
│                                        │
│ 📊 DIAGNOSTICS                         │
│ ⚠️  Line 8: Unused import             │
│ ⚠️  Line 5: Type hint missing          │
│ ✅ No errors                           │
│                                        │
│ [Git diff] [Commit] [Push]             │
│                                        │
└────────────────────────────────────────┘
```

**Deliverables:**
- Code editor: Syntax highlighting for multiple languages
- File tabs: Switch between open files
- Diagnostics: Linting + type checking
- Save/discard: Persist or revert changes
- Git integration: Diff, commit, push buttons

**Metrics:**
- Files: 2 (coding_view.dart, code_editor.dart)
- Syntax languages: Python, TypeScript, Dart, Markdown
- Test coverage: >75%

---

### Tarea 3: Hilos Manus — Agent Execution Threads

**Descripción:**
Monitor de hilos de ejecución de Manus agent (sprints, tasks, logs).

**UI Layout:**
```
┌────────────────────────────────────────┐
│ Hilos Manus — Agent Threads       [🧠]│
├────────────────────────────────────────┤
│                                        │
│ ✅ Sprint 88 Closure Thread           │
│    Status: Completed (15m runtime)    │
│    Tasks: 12/12 done                  │
│    Success: 100%                      │
│    [View logs] [Replay] [Export]      │
│                                        │
│ ⏳ Sprint 89 Execution Thread         │
│    Status: Running (47m elapsed)      │
│    Tasks: 8/12 done (66%)             │
│    ETA: 12m remaining                 │
│    Current task: Catastro refactoring │
│    [Pause] [Cancel] [Speed up]        │
│                                        │
│ ⏰ Sprint 90 Planning Thread           │
│    Status: Queued (starts in 2h)      │
│    Tasks: 0/15 estimated              │
│    Priority: P1                       │
│    [Move up] [View plan]              │
│                                        │
│ 📊 THREAD HISTORY                      │
│ • 50 threads in last 7 days           │
│ • Avg runtime: 22m                    │
│ • Success rate: 97.3%                 │
│ • Total tasks: 487                    │
│ [View analytics] [Export]             │
│                                        │
└────────────────────────────────────────┘
```

**Deliverables:**
- Active threads: List with status, progress, ETA
- Thread detail: Task breakdown, logs
- Controls: Pause, cancel, speed (for dev/testing)
- History: Past threads, analytics
- Export: Logs, metrics (CSV, JSON)

**Metrics:**
- Files: 2 (hilos_manus_view.dart, thread_card.dart)
- Real-time updates: WebSocket polling (2s)
- Test coverage: >75%

---

### Tarea 4: Bridge Navigator — Sprint + Project Browser

**Descripción:**
Navegador visual del bridge/ directory (sprints, specs, roadmaps).

**UI Layout:**
```
┌────────────────────────────────────────┐
│ Bridge Navigator — Specs & Sprints │├─┤
├────────────────────────────────────────┤
│ [📁 bridge/]                           │
│ ├─ sprints_propuestos/                 │
│ │  ├─ sprint_88_... 🟢 Proposed       │
│ │  ├─ sprint_89_... 🟢 Proposed       │
│ │  ├─ sprint_90_... 🟢 Proposed       │
│ │  ├─ sprint_mobile_1... 🔵 In prep   │
│ │  ├─ sprint_mobile_2... ⚪ Waiting   │
│ │  └─ ... [+5 more]                   │
│ │                                      │
│ ├─ sprints_en_ejecucion/              │
│ │  ├─ sprint_88_actual.md 🟡 70%     │
│ │  └─ sprint_89_actual.md 🟡 45%     │
│ │                                      │
│ ├─ docs/                               │
│ │  ├─ ROADMAP_EJECUCION_DEFINITIVO.md│
│ │  ├─ 14_OBJETIVOS_MAESTROS.md       │
│ │  └─ ... [+8 more]                   │
│ │                                      │
│ └─ [other directories]                │
│                                        │
│ ┌────────────────────────────────────┐│
│ │ SELECTED: sprint_88_cierre_...    ││
│ │ Status: 🟢 Proposed                ││
│ │ ETA: 30-60 min                     ││
│ │ Objective: #1 (Valor real)         ││
│ │ [Read] [Edit] [Schedule]           ││
│ └────────────────────────────────────┘│
│                                        │
│ [Search files] [Sync from Git]         │
│                                        │
└────────────────────────────────────────┘
```

**Deliverables:**
- Directory tree: Visual file browser
- Status indicators: 🟢/🟡/🔵 for different states
- File preview: Tap to view spec content
- Search: Filter by name, objective, status
- Git sync: Pull latest from GitHub

**Metrics:**
- Files: 2 (bridge_navigator.dart, file_tree.dart)
- Search: Real-time filtering
- Test coverage: >75%

---

### Tarea 5: Settings + Admin Panel

**Descripción:**
Configuración global + panel administrativo para gestionar El Monstruo.

**UI Layout:**
```
┌────────────────────────────────────────┐
│ Settings & Admin                  [⚙️]│
├────────────────────────────────────────┤
│                                        │
│ DISPLAY SETTINGS                       │
│ [Theme] 🌙 Dark  ⭕ Light             │
│ [Font size] [100%] ──●───────── [150%]│
│ [Language] ⭕ Español [ ] English     │
│                                        │
│ NOTIFICATIONS                          │
│ [✓] Sprint completions                │
│ [✓] High-priority alerts              │
│ [✓] Daily digest (10 AM)              │
│ [Sound] [Desktop]                      │
│                                        │
│ DATA & PRIVACY                         │
│ [Export all data] [Download backup]    │
│ [Clear cache] [Reset to defaults]      │
│ [Data retention] [90 days]             │
│                                        │
│ ADMIN PANEL (Alfredo only)             │
│ ┌────────────────────────────────────┐│
│ │ 🔑 API Keys Management             ││
│ │ [Show keys] [Rotate] [Audit]       ││
│ │                                    ││
│ │ 👥 User Management                 ││
│ │ [Add user] [Permissions] [Audit]   ││
│ │                                    ││
│ │ 🗄️  Database Tools                 ││
│ │ [Query] [Backup] [Restore]         ││
│ │                                    ││
│ │ 🔐 Security                         ││
│ │ [2FA] [Session timeout] [Audit log]││
│ │                                    ││
│ │ 📊 System Health                    ││
│ │ [Logs] [Metrics] [Uptime]          ││
│ └────────────────────────────────────┘│
│                                        │
│ [About] [Help] [Contact] [Logout]      │
│                                        │
└────────────────────────────────────────┘
```

**Deliverables:**
- Display: Theme, font, language settings
- Notifications: Preference toggles
- Data: Export, backup, reset options
- Admin panel: API keys, users, database, security, health
- Help: Links to docs, support

**Metrics:**
- Files: 2 (settings_view.dart, admin_panel.dart)
- Admin gate: Role-based access (Alfredo only)
- Test coverage: >75%

---

### Tarea 6: Cockpit Navigation (Complete)

**Descripción:**
Agregar últimas 5 superficies a sidebar (total: 15 en mobile_3 + mobile_4 + mobile_5).

**Deliverables:**
- Sidebar: Complete with all 10 cockpit items
- Routing: All 15 surfaces accessible (5 Daily + 10 Cockpit)
- Icons: 15 unique, clear visual identity

---

## Aceptación

**Definición de Listo:**
1. All 5 final surfaces rendered ✅
2. Cockpit complete: 10 surfaces accessible ✅
3. Data binding: Real data where applicable ✅
4. Tests: >75% coverage per surface ✅
5. Build: `flutter run` succeeds ✅

**Quality Gates:**
- Performance: 60fps across all surfaces
- Visual: Consistent with brand DNA
- Stubs: All logic placeholders documented
- Code: Zero linting warnings

**Final Milestone:**
- **CARA DEL MONSTRUO COMPLETA**
- 15 total surfaces (5 Daily + 10 Cockpit)
- Mobile app feature-complete for v1.0
- Ready for beta release

**Post-sprint:**
- Sprint 88: v1.0 release (kernel + app)
- Marketing: Announce to public
- Next: Feature iterations based on feedback

---

## Notas Técnicas

1. **State management:** Provider for all features
2. **Real-time:** WebSocket for live updates
3. **Theme:** Design tokens from sprint Catastro B
4. **Backward compat:** All existing features stable

---

**Cowork (Hilo A), spec preparada 2026-05-06**
