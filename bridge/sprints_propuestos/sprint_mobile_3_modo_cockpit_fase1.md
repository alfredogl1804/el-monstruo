# Sprint Mobile 3 — Modo Cockpit Fase 1: 5 Superficies Densas (MOC Dashboard, Threads Denso, Catastro, Embriones, Guardian)

**Estado:** Propuesto  
**Hilo:** Ejecutor (Alfredo)  
**ETA (actualizado):** 15-30 min reales (UI stubs + data binding, logic in future sprints)  
**Objetivo Maestro:** #9 (Transversalidad) + #14 (Guardián de los Objetivos)

---

## Audit Pre-Sprint

**Cockpit Mode Scope:**
- Purpose: Deep work, monitoring, decision-making (desktop UI adapted for tablet)
- Users: PM, architects, ops (Alfredo primarily)
- Sessions: 30 min - 2 hours (sustained work)
- Contrast: vs Daily (lightweight, 5-15 min)

**Architecture:**
- Navigation: Sidebar (not bottom bar)
- Density: Information-rich, multiple widgets per surface
- Theme: Same brand DNA (forja/graphite/acero)
- State: Provider + Redux-style actions

**Key Surfaces to Build:**
1. MOC Dashboard — Map of Contents (all projects, sprints, status)
2. Threads Denso — Expanded conversation view
3. Catastro — 3-tab view (Modelos, Suppliers, Tools)
4. Embriones — 9+ autonomous agents status
5. Guardian — 15 Maestro Objetivos tracking

---

## Tareas del Sprint

### Tarea 1: MOC Dashboard — Map of Contents

**Descripción:**
Dashboard que muestra vista aérea de todos los contenidos (sprints, projects, docs).

**UI Layout:**
```
┌─────────────────────────────────────────┐
│ Monstruo Cockpit — MOC Dashboard  [≡]  │
├─────────────────────────────────────────┤
│ PROJECTS                                │
│ ┌─────────────┐ ┌─────────────┐        │
│ │ El Monstruo │ │ Kukulkan    │        │
│ │ 12 sprints  │ │ 5 sprints   │        │
│ │ [→ view]    │ │ [→ view]    │        │
│ └─────────────┘ └─────────────┘        │
│                                         │
│ ACTIVE SPRINTS                          │
│ [Sprint 88] ...... 45% (2 days left)   │
│ [Sprint 89] ...... 60% (3 days left)   │
│ [Sprint 90] ...... 20% (5 days left)   │
│                                         │
│ KEY DOCS                                │
│ • CLAUDE.md (last edit: 2h ago)        │
│ • ROADMAP_EJECUCION (last edit: 1d ago)│
│ • 14_OBJETIVOS (last edit: 3d ago)     │
│                                         │
└─────────────────────────────────────────┘
```

**Deliverables:**
- Project cards: Summary view with sprint counts
- Sprint progress: Bar charts showing completion %
- Doc list: Recently edited docs with timestamps
- Tap actions: Navigate to project/sprint detail (stubs)

**Metrics:**
- Files: 2 (moc_dashboard.dart, moc_service.dart)
- Data source: Supabase (projects, sprints, docs)
- Test coverage: >85%

---

### Tarea 2: Threads Denso — Expanded Conversations

**Descripción:**
Vista expandida de conversaciones con full context (no comprimida como en Daily).

**UI Layout:**
```
┌─────────────────────────────────────┐
│ Threads — Expanded View        [✕]  │
├─────────────────────────────────────┤
│                                     │
│ [Thread] "Kernel deployment"    [↕]│
│ Started: 2026-05-06 14:30           │
│ Participants: Alfredo, Manus, Bot   │
│                                     │
│ ───────────────────────────────────│
│                                     │
│ Alfredo (14:30)                     │
│ "Should we deploy v0.51 to prod?"   │
│                                     │
│ Manus (14:32)                       │
│ "Ready. 15-min closure. Risk: low"  │
│                                     │
│ Alfredo (14:35)                     │
│ "✅ Approved. Deploy now."          │
│                                     │
│ ───────────────────────────────────│
│                                     │
│ [Type reply...]                     │
│ [Send] [Attach] [Emoji]             │
│                                     │
└─────────────────────────────────────┘
```

**Deliverables:**
- Thread display: Full message history
- Message bubbles: Author + timestamp + content
- Actions: Reply, react, pin (stubs)
- Input field: Text + media (wired to API)

**Metrics:**
- Files: 2 (threads_denso.dart, thread_detail.dart)
- Message rendering: Handles 100+ messages smoothly
- Test coverage: >80%

---

### Tarea 3: Catastro — 3-Tab View (Modelos, Suppliers, Tools)

**Descripción:**
Vista centralizada de los 3 catastros poblados en sprints 89 + Catastro A.

**UI Layout:**
```
┌─────────────────────────────────────┐
│ Catastro Completo             [≡]   │
├─────────────────────────────────────┤
│ [Modelos] [Suppliers] [Tools] ←─ Tabs
├─────────────────────────────────────┤
│                                     │
│ TAB 1: MODELOS (LLM)                │
│ ┌─────────────────────────────────┐ │
│ │ GPT-5.5                         │ │
│ │ Provider: OpenAI | Cost: $0.01  │ │
│ │ Status: ✅ Active (99.8% uptime)│ │
│ │ [Details] [Switch]              │ │
│ └─────────────────────────────────┘ │
│ ┌─────────────────────────────────┐ │
│ │ Claude Opus 4.7                 │ │
│ │ Provider: Anthropic | Cost: ... │ │
│ │ Status: ✅ Active               │ │
│ └─────────────────────────────────┘ │
│ [+ 4 more models]                   │
│                                     │
│ TAB 2: SUPPLIERS                    │
│ [Alfredo] [Manus] [Embrión] [Hires] │
│                                     │
│ TAB 3: TOOLS                        │
│ [Perplexity] [GitHub] [DALL-E]      │
│ [+ 20+ more tools]                  │
│                                     │
└─────────────────────────────────────┘
```

**Deliverables:**
- Tab view: 3 tabs with smooth transitions
- Model list: Cards showing name, provider, cost, status
- Supplier list: Linked from catastro_suppliers.json
- Tools list: Linked from catastro_tools.json
- Detail view: Tap to see full details (stub)

**Metrics:**
- Files: 3 (catastro_view.dart, catastro_models_tab.dart, catastro_suppliers_tab.dart, catastro_tools_tab.dart)
- Data source: Catastro JSON + API
- Test coverage: >85%

---

### Tarea 4: Embriones — 9+ Autonomous Agents Status

**Descripción:**
Dashboard de agentes autónomos (Embrión, Manus, future agents) con estado + logs.

**UI Layout:**
```
┌────────────────────────────────────────┐
│ Embriones (9+)                    [🔄] │
├────────────────────────────────────────┤
│                                        │
│ ✅ Embrión (Main)                     │
│    Status: Running (cycle #47)         │
│    CPU: 2% | Memory: 124MB             │
│    Last action: plan_generation       │
│    Next heartbeat: in 2m 15s           │
│    [View logs] [Kill] [Restart]        │
│                                        │
│ ✅ Manus (Executor)                   │
│    Status: Idle (ready)                │
│    Last task: sprint_88 closure        │
│    Completed: 847 tasks                │
│    Success rate: 98.7%                 │
│    [View history] [Run task]           │
│                                        │
│ ⏸️ [Agent #3] (paused)                │
│ ⏸️ [Agent #4] (paused)                │
│ ✅ [Agent #5]                         │
│ ... [+ 4 more agents]                 │
│                                        │
│ [+ ADD NEW AGENT]                     │
│                                        │
└────────────────────────────────────────┘
```

**Deliverables:**
- Agent cards: Status (running/idle/paused), metrics (CPU, memory)
- Logs: Recent actions, next scheduled action
- Controls: View logs, kill, restart (wired to API)
- Health: CPU + memory gauges

**Metrics:**
- Files: 2 (embriones_dashboard.dart, agent_card.dart)
- Real-time updates: WebSocket polling (5s interval)
- Test coverage: >80%

---

### Tarea 5: Guardian — 15 Maestro Objetivos Tracking

**Descripción:**
Monitor de los 15 Maestro Objetivos con status + progress.

**UI Layout:**
```
┌────────────────────────────────────────┐
│ Guardian — 15 Maestro Objetivos   [?] │
├────────────────────────────────────────┤
│ SCORE: 78/100 ↗ Target: 95            │
│ ════════════░░░░░░ 78%                 │
│                                        │
│ ✅ #1 Valor Real (100%)                │
│    [El Monstruo v1.0 shipped]          │
│                                        │
│ ✅ #2 Calidad Apple/Tesla (95%)        │
│    [Minor UI polish pending]           │
│    [Target: mobile_1 refactor]         │
│                                        │
│ ⚠️  #3 Mínima Complejidad (72%)        │
│    [Kernel refactoring: 80% done]      │
│    [Target: sprint 89]                 │
│                                        │
│ ⚠️  #4 No Equivocarse (65%)            │
│    [Error Memory: 3 incidents logged]  │
│    [Action: pre-flight checks]         │
│                                        │
│ ✅ #5 Documentación Magna (100%)       │
│ ✅ #6 Velocidad (88%)                  │
│ ... [+ 9 more objectives]              │
│                                        │
│ [Details] [History] [Compliance Plan] │
│                                        │
└────────────────────────────────────────┘
```

**Deliverables:**
- Score card: Overall score with gauge
- Objective list: Status (✅/⚠️/❌), % complete
- Drill-down: Tap objective → detail + action items
- History: Track score over time (line chart)

**Metrics:**
- Files: 3 (guardian_dashboard.dart, objective_card.dart, guardian_chart.dart)
- Data source: Supabase (objectives table)
- Test coverage: >85%

---

### Tarea 6: Sidebar Navigation + Routing

**Descripción:**
Sidebar para navegar entre las 5 superficies de Cockpit.

**Implementation:**
```dart
// lib/screens/cockpit/cockpit_home.dart
class CockpitHomePage extends StatefulWidget {
  @override
  _CockpitHomePageState createState() => _CockpitHomePageState();
}

class _CockpitHomePageState extends State<CockpitHomePage> {
  int _selectedIndex = 0;
  
  final List<Widget> screens = [
    MOCDashboard(),
    ThreadsDenso(),
    CatastroView(),
    EmbrionesD ashboard(),
    GuardianDashboard(),
  ];
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Monstruo Cockpit')),
      body: Row(
        children: [
          NavigationRail(
            selectedIndex: _selectedIndex,
            onDestinationSelected: (index) =>
              setState(() => _selectedIndex = index),
            destinations: [
              NavigationRailDestination(icon: Icon(Icons.map), label: Text('MOC')),
              NavigationRailDestination(icon: Icon(Icons.chat), label: Text('Threads')),
              NavigationRailDestination(icon: Icon(Icons.collections), label: Text('Catastro')),
              NavigationRailDestination(icon: Icon(Icons.android), label: Text('Embriones')),
              NavigationRailDestination(icon: Icon(Icons.shield), label: Text('Guardian')),
            ],
          ),
          Expanded(child: screens[_selectedIndex]),
        ],
      ),
    );
  }
}
```

**Deliverables:**
- Sidebar: NavigationRail with 5 items
- Routing: Smooth transitions
- Icons: Clear visual identity

**Metrics:**
- Files: 1 (cockpit_home.dart)
- Test coverage: >85%

---

## Aceptación

**Definición de Listo:**
1. All 5 surfaces rendered ✅
2. Navigation works (sidebar switching) ✅
3. Data binding: Catastro + Guardian linked ✅
4. Tests: >85% coverage per surface ✅
5. Build: `flutter run` succeeds ✅

**Quality Gates:**
- Visual: No layout errors
- Performance: 60fps scrolling
- Stubs: Logic placeholders for future sprints
- Code: Zero linting warnings

**Post-sprint:**
- Sprint mobile_4: 5 more Cockpit surfaces (Memento, Portfolio, FinOps, Pipeline, Replay)
- Sprint mobile_5: Final 5 Cockpit surfaces (Computer Use, Coding, Hilos Manus, Bridge, Settings)
- Result: 15-surface Cockpit = "CARA DEL MONSTRUO COMPLETA"

---

**Cowork (Hilo A), spec preparada 2026-05-06**
