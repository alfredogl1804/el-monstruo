# Sprint Mobile 2 — Modo Daily Fase 1: 5 Superficies + Stubs (Home, Threads, Pendientes, Conexiones, Perfil)

**Estado:** Propuesto  
**Hilo:** Ejecutor (Alfredo)  
**ETA (actualizado):** 15-30 min reales (ui stubs + wiring, logic in future sprints)  
**Objetivo Maestro:** #6 (Velocidad sin sacrificar calidad) + #9 (Transversalidad)

---

## Audit Pre-Sprint

**Daily Mode Scope:**
- Purpose: Lightweight, everyday use (voice input, quick actions)
- Users: Everyone on El Monstruo (field work, mobile-first)
- Sessions: 5-15 min bursts (not long sessions)
- Contrast: vs Cockpit (desktop, deep work, 2+ hours)

**UI Framework:**
- Base: Flutter 3.19+ with Material 3
- State: Provider (existing, proven)
- Navigation: BottomNavigationBar (5 tabs)
- Theme: Brand DNA (forja/graphite/acero — from mobile_1)

---

## Tareas del Sprint

### Tarea 1: Home Surface — Voice Input + Camera + Río Cronos

**Descripción:**
Pantalla principal para Daily mode con entrada de voz, captura de cámara, y histórico comprimido (río cronos).

**UI Layout:**
```
┌─────────────────────────────────┐
│   [≡] Monstruo Daily      [👤] │ ← AppBar
├─────────────────────────────────┤
│                                 │
│    🎤 [START VOICE]             │
│                                 │
│    📷 [CAMERA CAPTURE]          │
│                                 │
│  ─────────────────────────────  │
│                                 │
│    RÍO CRONOS (compressed)      │
│    [✓] Last request (5m ago)    │
│    [→] Pending (2 actions)      │
│    [↻] In progress (1 task)     │
│                                 │
├─────────────────────────────────┤
│ [Home] [Threads] [Pendientes] │ ← BottomNavBar
│ [Conexiones] [Perfil]         │
└─────────────────────────────────┘
```

**Deliverables:**
- Voice input: Button + stub handler (full logic in sprint mobile_3+)
- Camera: Button + stub (full camera integration in sprint mobile_3+)
- Río Cronos: List widget showing last 5 events (compressed view)
- State: Connected to Provider, ready for real data

**Metrics:**
- Lines of code: 150-200 (UI only)
- Responsiveness: Smooth at 60fps
- Test coverage: Basic widget tests >80%

---

### Tarea 2: Threads Surface — Conversaciones Comprimidas

**Descripción:**
Vista de hilos de conversación con modo comprimido (titular + última respuesta).

**UI Layout:**
```
┌─────────────────────────────────┐
│   Threads                       │
├─────────────────────────────────┤
│                                 │
│  [Thread #1]  2m ago            │
│  "What is El Monstruo?"         │
│  ▸ "A sovereign multi-agent..." │
│                                 │
│  [Thread #2]  1h ago            │
│  "Deploy kernel to Railway?"    │
│  ▸ "Yes, ready: v0.50.0..."    │
│                                 │
│  [+ NEW THREAD]                 │
│                                 │
└─────────────────────────────────┘
```

**Deliverables:**
- Thread list: Scrollable list of threads
- Thread item: Title + timestamp + preview of last message
- Tap action: Opens thread detail (stub, logic in mobile_3)
- New thread: Button (creates stub, fills in mobile_3)

**Metrics:**
- Files: 1 (threads_screen.dart)
- Widget complexity: Simple (ListView + ListTile)
- Test coverage: >80%

---

### Tarea 3: Pendientes Surface — Quick Actions + Tasks

**Descripción:**
Vista de tareas pendientes y acciones rápidas.

**UI Layout:**
```
┌─────────────────────────────────┐
│   Pendientes                    │
├─────────────────────────────────┤
│                                 │
│  ⭐ HIGH PRIORITY               │
│  [ ] Deploy to prod (today)     │
│  [ ] Review PR #42 (today)      │
│                                 │
│  📌 NORMAL                      │
│  [ ] Catastro research (Thu)    │
│  [ ] Sprint planning (Fri)      │
│                                 │
│  ✓ COMPLETED (3)                │
│  ▸ (toggle to show)             │
│                                 │
│  [+ ADD TASK]                   │
│                                 │
└─────────────────────────────────┘
```

**Deliverables:**
- Task list: Grouped by priority (HIGH, NORMAL, LOW)
- Checkbox: Toggle complete (stub for state sync)
- Timestamps: Due date display
- Add button: New task dialog (stub)

**Metrics:**
- Files: 1 (pendientes_screen.dart)
- Widget count: 5-7
- Test coverage: >80%

---

### Tarea 4: Conexiones Surface — People + Links

**Descripción:**
Red de personas y conexiones externas (catastro suppliers humanos).

**UI Layout:**
```
┌─────────────────────────────────┐
│   Conexiones                    │
├─────────────────────────────────┤
│                                 │
│  🔗 DIRECT COLLABORATORS        │
│  👤 Alfredo (PM, Mérida)        │
│  👤 Manus (Agente, always-on)   │
│  👤 Embrión (Agente, bg loop)   │
│                                 │
│  🌐 EXTERNAL LINKS              │
│  [GitHub] [Slack] [Manus] [API] │
│                                 │
│  📞 QUICK CONTACT               │
│  [Send message] [Call] [Email]  │
│                                 │
└─────────────────────────────────┘
```

**Deliverables:**
- Supplier list: Loaded from catastro_suppliers.json (sprint Catastro A)
- Link buttons: GitHub, Slack, Manus, etc. (stubs)
- Contact actions: Send message (stub), call (stub)

**Metrics:**
- Files: 1 (conexiones_screen.dart)
- Data source: catastro via API
- Test coverage: >80%

---

### Tarea 5: Perfil Surface — User Settings + Bio

**Descripción:**
Perfil del usuario con settings rápidos y bio.

**UI Layout:**
```
┌─────────────────────────────────┐
│   Perfil                        │
├─────────────────────────────────┤
│                                 │
│        👤 Alfredo González      │
│                                 │
│  ⚙️ SETTINGS                     │
│  [Theme] [Dark] ◉ Light         │
│  [Language] ◉ Español   [ ] Eng │
│  [Notifications] [ON] [OFF]     │
│                                 │
│  📊 STATS                       │
│  Sprints closed: 50             │
│  Critic score: 78               │
│  Uptime: 99.5%                  │
│                                 │
│  [LOGOUT] [DELETE ACCOUNT]      │
│                                 │
└─────────────────────────────────┘
```

**Deliverables:**
- User info: Name, avatar (stub)
- Settings: Theme toggle, language selector, notifications
- Stats: Display key metrics (read-only)
- Logout: Button (wired to auth service)

**Metrics:**
- Files: 1 (perfil_screen.dart)
- Widget count: 8-10
- Test coverage: >80%

---

### Tarea 6: Navigation + Routing

**Descripción:**
Wiring de las 5 superficies vía BottomNavigationBar.

**Implementation:**
```dart
// lib/screens/daily/daily_home.dart
class DailyHomePage extends StatefulWidget {
  @override
  _DailyHomePageState createState() => _DailyHomePageState();
}

class _DailyHomePageState extends State<DailyHomePage> {
  int _selectedIndex = 0;
  
  final List<Widget> screens = [
    HomeScreen(),
    ThreadsScreen(),
    PendientesScreen(),
    ConexionesScreen(),
    PerfilScreen(),
  ];
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Monstruo Daily')),
      body: screens[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        items: [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.chat), label: 'Threads'),
          BottomNavigationBarItem(icon: Icon(Icons.tasks), label: 'Pendientes'),
          BottomNavigationBarItem(icon: Icon(Icons.people), label: 'Conexiones'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Perfil'),
        ],
        currentIndex: _selectedIndex,
        onTap: (index) => setState(() => _selectedIndex = index),
      ),
    );
  }
}
```

**Deliverables:**
- Navigation: BottomNavigationBar with 5 items
- Routing: Smooth transitions between screens
- State: Preserved when switching tabs (PageStorage)

**Metrics:**
- Files: 1 (daily_home.dart)
- Test coverage: >85%

---

## Aceptación

**Definición de Listo:**
1. All 5 surfaces rendered (no crashes) ✅
2. Navigation works (tab switching smooth) ✅
3. UI matches brand DNA (forja/graphite/acero) ✅
4. Tests: >80% coverage per surface ✅
5. Build: `flutter run` succeeds ✅

**Quality Gates:**
- Visual: No layout errors, text readable
- Performance: Smooth scrolling (60fps)
- Stubs: All UI in place, logic stubs ready
- Code: Zero linting warnings

**Post-sprint:**
- Sprint mobile_3: Fill Cockpit mode (5 more surfaces)
- Sprint mobile_4: 5 more Cockpit surfaces
- Sprint mobile_5: Final 5 Cockpit surfaces
- Result: 15-surface app (5 Daily + 15 Cockpit) = "CARA DEL MONSTRUO COMPLETA"

---

## Notas Técnicas

1. **Storage:** PageStorage keeps tab state when switching
2. **State management:** Provider for global state (auth, user, settings)
3. **Theming:** Uses @monstruo/design-tokens (mobile_1 output)
4. **Stubs:** `// TODO: implement logic in mobile_3+` comments for all complex handlers

---

**Cowork (Hilo A), spec preparada 2026-05-06**
