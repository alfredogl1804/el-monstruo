# Sprint Mobile 4 — Modo Cockpit Fase 2: 5 Más Superficies (Memento, Portfolio Empresas-Hijas, FinOps, Pipeline E2E, Replay/Timelapse)

**Estado:** Propuesto  
**Hilo:** Ejecutor (Alfredo)  
**ETA (actualizado):** 15-30 min reales (UI stubs + data binding)  
**Objetivo Maestro:** #15 (Memoria Soberana) + #12 (Soberanía)

---

## Audit Pre-Sprint

**Cockpit Phase 2 Scope:**
- 5 more high-information surfaces
- Focus: Memory, portfolios, financials, execution, time-travel
- Continuation of mobile_3 (5 surfaces)
- Total after mobile_3 + mobile_4: 10 surfaces (15 by mobile_5)

---

## Tareas del Sprint

### Tarea 1: Memento — Memory Validation Dashboard

**Descripción:**
Monitor de fuentes de verdad y validación de contexto (anti-Síndrome-Dory).

**UI Layout:**
```
┌────────────────────────────────────────┐
│ Memento — Fuentes de Verdad       [🔒]│
├────────────────────────────────────────┤
│                                        │
│ ✅ SUPABASE (Primary Memory)          │
│    Tables: 8 | Rows: 12,456           │
│    Last backup: 2026-05-06 14:00      │
│    Integrity: ✅ 100% (CRC verified)   │
│    [View schema] [Backup now]          │
│                                        │
│ ✅ REDIS (Cache)                      │
│    Keys: 347 | Memory: 2.3 MB         │
│    Hit rate: 94.2%                    │
│    Status: ✅ Healthy                 │
│    [Flush] [Stats]                    │
│                                        │
│ ⚠️  GITHUB (Spec Source)              │
│    Commits: 1,247 | Last: 2h ago      │
│    Branches: main + 3 feature         │
│    Status: ✅ In sync                 │
│    [View changes] [Pull latest]       │
│                                        │
│ 🔍 CONTEXT VALIDATION                 │
│    Last validation: 15m ago            │
│    Status: ✅ All threads aligned     │
│    Contamination detected: 0           │
│    [Validate now] [History]            │
│                                        │
│ ✅ AUDIT LOG                          │
│    Events: 8,392                       │
│    Period: Last 30d                    │
│    Access: Alfredo (100%)              │
│    [View audit]                        │
│                                        │
└────────────────────────────────────────┘
```

**Deliverables:**
- Data source cards: Status, metrics, last updated
- Integrity check: CRC validation status
- Backup button: Trigger on-demand backup to S3
- Audit log: Recent access/modifications
- Validation: Context contamination detector

**Metrics:**
- Files: 2 (memento_dashboard.dart, data_source_card.dart)
- Real-time: WebSocket updates (10s interval)
- Test coverage: >80%

---

### Tarea 2: Portfolio Empresas-Hijas — Multi-Project View

**Descripción:**
Cartera de proyectos/empresas-hijas con estado agregado.

**UI Layout:**
```
┌────────────────────────────────────────┐
│ Portfolio — Empresas-Hijas        [+] │
├────────────────────────────────────────┤
│                                        │
│ 📊 PORTFOLIO OVERVIEW                  │
│    Total value: $2.3M (est.)           │
│    Active projects: 7                  │
│    Avg. maturity: Seed → Series A      │
│    Revenue (TTM): $340K                │
│                                        │
│ ┌──────────────────────────────────┐  │
│ │ El Monstruo (Flagship)           │  │
│ │ Stage: MVP→v1.0 | Health: 💚    │  │
│ │ Value: $1.2M | Revenue: $0      │  │
│ │ Team: 3 (Alfredo, Manus, Bot)   │  │
│ │ [Dashboard] [Details]            │  │
│ └──────────────────────────────────┘  │
│                                        │
│ ┌──────────────────────────────────┐  │
│ │ Kukulkan-Tickets                 │  │
│ │ Stage: Alpha | Health: 💛        │  │
│ │ Value: $450K | Revenue: $50K/mo  │  │
│ │ Team: 2 | Traction: 230 users    │  │
│ │ [Dashboard] [Details]            │  │
│ └──────────────────────────────────┘  │
│                                        │
│ [+ 5 more projects]                    │
│                                        │
│ [New Project] [Invest] [Exit]          │
│                                        │
└────────────────────────────────────────┘
```

**Deliverables:**
- Portfolio summary: Total value, count, avg stage
- Project cards: Stage, health, value, revenue, team
- Detail view: Tap → deep dive (linked to project dashboard)
- Add project: Create new portfolio entry

**Metrics:**
- Files: 2 (portfolio_view.dart, project_card.dart)
- Data source: Supabase (projects table)
- Test coverage: >80%

---

### Tarea 3: FinOps — Financial Operations

**Descripción:**
Dashboard financiero (burn rate, spend by provider, margins).

**UI Layout:**
```
┌────────────────────────────────────────┐
│ FinOps — Financial Dashboard      [📈]│
├────────────────────────────────────────┤
│                                        │
│ 💰 THIS MONTH                          │
│    Spend: $3,240 (78% of budget)       │
│    Runway: 16 months @ current rate    │
│    Burn: $4,154/month                  │
│                                        │
│ SPEND BY PROVIDER                      │
│ ┌────────────────────────────────────┐│
│ │ Railway:     $1,200 (37%)          ││
│ │ Stripe:      $840 (26%)            ││
│ │ Supabase:    $520 (16%)            ││
│ │ OpenAI:      $420 (13%)            ││
│ │ Anthropic:   $260 (8%)             ││
│ └────────────────────────────────────┘│
│                                        │
│ 📊 BURN RATE (Last 3 months)           │
│    Mar: $4,100 | Apr: $4,050           │
│    May: $4,240 (projected)             │
│    Trend: ↗ +3.5% (needs optimization) │
│                                        │
│ ✅ MARGINS (if $340K revenue/mo)      │
│    Gross: 83% | Operating: 45%         │
│    Breakeven: +8 customers @ $50/mo    │
│                                        │
│ [Detailed report] [Audit] [Forecast]   │
│                                        │
└────────────────────────────────────────┘
```

**Deliverables:**
- Spend summary: Total, budget %, runway
- Provider breakdown: Pie/bar chart by vendor
- Burn rate: Trend over time (line chart)
- Margins: Gross/operating if revenue scenarios
- Forecast: 6-12 month projection

**Metrics:**
- Files: 2 (finops_dashboard.dart, spend_chart.dart)
- Data source: Supabase (expenses table)
- Test coverage: >80%

---

### Tarea 4: Pipeline E2E — 12-Step Execution Flow

**Descripción:**
Visualización del flujo end-to-end de idea → shipped con 12 hitos y tier indicators.

**UI Layout:**
```
┌────────────────────────────────────────┐
│ Pipeline E2E — Idea → Shipped     [📊]│
├────────────────────────────────────────┤
│                                        │
│ Step 1: Concepto ..................... ✅ Done
│ Tier: [🟩 P0] | Owner: Alfredo | 2d
│                                        │
│ Step 2: Spec ........................ ✅ Done
│ Tier: [🟨 P1] | Owner: Alfredo | 1d
│                                        │
│ Step 3: Design ...................... ✅ Done
│ Tier: [🟨 P1] | Owner: Manus | 2d
│                                        │
│ Step 4: Code ........................ ⏳ 60%
│ Tier: [🟩 P0] | Owner: Manus | 2d left
│                                        │
│ Step 5: Test ........................ ⏰ Pending
│ Tier: [🟨 P1] | Owner: Bot | est. 1d
│                                        │
│ Step 6: Review ....................... ⏰ Pending
│ Step 7: Merge ........................ ⏰ Pending
│ Step 8: Deploy (staging) ............. ⏰ Pending
│ Step 9: QA ........................... ⏰ Pending
│ Step 10: Deploy (prod) ............... ⏰ Pending
│ Step 11: Monitor ..................... ⏰ Pending
│ Step 12: Shipped ..................... ⏰ Pending
│                                        │
│ [View details] [Unblock] [History]    │
│                                        │
└────────────────────────────────────────┘
```

**Deliverables:**
- Step list: 12 linear steps with status indicators
- Tier badges: P0/P1/P2 color coding
- Owner: Assignment per step
- Duration: Time spent + estimated remaining
- Blocker detection: Flag if step stuck > 24h

**Metrics:**
- Files: 2 (pipeline_view.dart, step_card.dart)
- Data source: Supabase (pipeline_steps table)
- Test coverage: >80%

---

### Tarea 5: Replay / Timelapse — Time-Travel Analysis

**Descripción:**
Visualización temporal del proyecto (rewind/play/fast-forward).

**UI Layout:**
```
┌────────────────────────────────────────┐
│ Replay — Timelapse Analysis       [🎬]│
├────────────────────────────────────────┤
│                                        │
│ [◀◀] [◀] [▶] [▶▶] [🔄 Speed: 1x]     │
│                                        │
│ ─────────────────────────────────────  │
│ Timeline: 2026-03-01 ←→ 2026-05-06    │
│ ───[●]────────────────────────────────│
│     │ Today (50% complete)            │
│                                        │
│ 📊 SNAPSHOT (2026-05-06 14:30)        │
│    Sprints: 10 | Objectives: 78/100  │
│    Burn: $4,240 | Revenue: $0         │
│    Team: 3 | Morale: 🟢 High         │
│                                        │
│ 📈 METRICS OVER TIME                  │
│ ┌────────────────────────────────────┐│
│ │ Critic Score: 45→78 (73%)         ││
│ │ Sprint velocity: 8→14 (75%)       ││
│ │ Code quality: 62%→88% (+26%)      ││
│ │ Team size: 1→3 (+200%)            ││
│ └────────────────────────────────────┘│
│                                        │
│ 🎯 KEY EVENTS                          │
│ 2026-03-15: First commit (Kernel)     │
│ 2026-04-01: Gateway + AG-UI           │
│ 2026-04-20: Mobile app skeleton       │
│ 2026-05-06: v1.0 approaching          │
│                                        │
│ [Export video] [Share timeline]       │
│                                        │
└────────────────────────────────────────┘
```

**Deliverables:**
- Timeline slider: Scrub through project history
- Playback controls: Play, pause, speed
- Snapshot: Metrics at selected date
- Event markers: Key milestones
- Metrics chart: Track score, velocity, quality over time

**Metrics:**
- Files: 2 (replay_view.dart, timeline_chart.dart)
- Data source: Supabase (audit_log, snapshots)
- Test coverage: >80%

---

### Tarea 6: Cockpit Navigation (Extended)

**Descripción:**
Agregar 5 nuevas superficies a sidebar de cockpit (total: 10 en mobile_3 + mobile_4).

**Deliverables:**
- Sidebar: Extended with 5 new items (Memento, Portfolio, FinOps, Pipeline, Replay)
- Routing: All 10 surfaces accessible
- Icons: Clear visual distinction

---

## Aceptación

**Definición de Listo:**
1. All 5 surfaces rendered ✅
2. Data binding: Real data from Supabase ✅
3. Charts: Render correctly (no axis errors) ✅
4. Tests: >80% coverage per surface ✅
5. Build: `flutter run` succeeds ✅

**Quality Gates:**
- Performance: Smooth at 60fps
- Data accuracy: Financial numbers validated
- Stubs: All logic placeholders ready
- Code: Zero linting warnings

**Post-sprint:**
- Sprint mobile_5: Final 5 surfaces
- Total: 15 surfaces (5 Daily + 10 Cockpit) = "CARA DEL MONSTRUO COMPLETA"

---

**Cowork (Hilo A), spec preparada 2026-05-06**
