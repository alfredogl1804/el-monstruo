# Sprint Catastro B — Cimientos Compartidos: @monstruo/design-tokens + manus-oauth-pattern + biblia-master-plan-template

**Estado:** Propuesto  
**Hilo:** Ejecutor (Alfredo) + Manus (npm publish)  
**ETA (actualizado):** 45-90 min reales (velocity: 3 paquetes, setup + testing + publishing)  
**Objetivo Maestro:** #7 (No reinventar la rueda) + #5 (Documentación Magna)

---

## Audit Pre-Sprint

**Current Brand DNA State:**
- Design System: Definido en CLAUDE.md (forja #F97316, graphite #1C1917, acero #A8A29E)
- Implementation: Scattered across projects (kukulkan, mobile, dashboard)
- Problem: Zero centralization → inconsistent color usage, token duplication
- Velocity impact: Each project re-implements design tokens (3-5 hrs per project)

**Current OAuth Pattern:**
- Location: Multiple implementations (Manus, El Monstruo, kukulkan-tickets)
- Maturity: Production-tested but not formalized
- Pattern: OAuth 2.0 with PKCE, token refresh, error handling
- Duplication: Similar code in 3+ places

**Current Biblia State:**
- Status: Conceptual (14 Objetivos, 4 Capas, but no executable plan template)
- Use: Referenced in docs but hard to apply
- Gap: Teams don't have clear "master plan template" to start sprints
- Impact: New sprints miss foundational alignment

---

## Tareas del Sprint

### Tarea 1: @monstruo/design-tokens — Paquete NPM de Design System

**Descripción:**
Centralizar tokens de diseño (colores, tipografía, spacing, shadows) en paquete NPM reutilizable.

**Estructura:**
```
@monstruo/design-tokens/
├── src/
│   ├── colors.ts
│   │   ├── primary: { forja: '#F97316', graphite: '#1C1917', acero: '#A8A29E' }
│   │   ├── semantic: { success: '#10B981', warning: '#F59E0B', error: '#EF4444' }
│   │   └── palette: { ... 50+ named colors }
│   ├── typography.ts
│   │   ├── fonts: { sans: 'Inter', mono: 'JetBrains Mono' }
│   │   ├── scales: { xs: 11px, sm: 13px, base: 14px, ... }
│   │   └── weights: { light, regular, medium, semibold, bold }
│   ├── spacing.ts
│   │   └── scale: { 4, 8, 12, 16, 24, 32, 48, 64 }px
│   ├── shadows.ts
│   │   └── elevation: { sm, md, lg, xl }
│   ├── radius.ts
│   │   └── corners: { xs, sm, md, lg, full }
│   └── index.ts (export all)
├── dist/
│   ├── tokens.json      # For design tools (Figma, etc.)
│   ├── tokens.css       # CSS variables
│   └── tokens.ts        # TypeScript (main)
├── tests/
│   ├── tokens.test.ts
│   └── contrast.test.ts  # A11y validation
├── package.json
└── README.md
```

**Exports (multi-format):**
```typescript
// TypeScript (primary)
export const colors = { ... }
export const typography = { ... }

// CSS
:root {
  --color-forja: #F97316;
  --color-graphite: #1C1917;
  --spacing-base: 16px;
}

// JSON (for design tools)
{ "colors": { "forja": "#F97316" } }
```

**Deliverables:**
- NPM package: v1.0.0-alpha
- Formats: TypeScript + CSS variables + JSON
- Tests: Contrast ratio validation (A11y), naming consistency
- Docs: Token guide, usage examples per framework

**Metrics:**
- Token count: 100+ (colors, typography, spacing, shadows, radius)
- Test coverage: 95%+
- Bundle size: < 5KB (gzipped)
- A11y: All colors meet WCAG AA contrast ratio

---

### Tarea 2: manus-oauth-pattern — Skill Reutilizable para OAuth

**Descripción:**
Formalizar patrón OAuth 2.0 + PKCE como skill Manus reutilizable (no package npm, sino "skill" = prompt + handlers).

**Skill Structure:**
```
manus-oauth-pattern/
├── SKILL.md                    # Skill definition + prompt
│   # Pasos: generate_code_verifier, request_auth, handle_callback, refresh_token
├── handlers/
│   ├── generate_code_verifier.js
│   ├── request_auth_url.js
│   ├── exchange_code_for_token.js
│   └── refresh_access_token.js
├── config/
│   ├── oauth.schema.json       # Expected env vars (client_id, redirect_uri, etc.)
├── tests/
│   ├── flow.test.js
│   └── error.test.js
└── README.md
```

**Pattern Coverage:**
- Init: Generate PKCE code_verifier + code_challenge
- Auth: Build authorization URL, redirect user
- Callback: Exchange code for access token (validate state)
- Refresh: Auto-refresh token when expired
- Error handling: Invalid grant, token revoked, network errors

**Deliverables:**
- Skill: Registered in Manus marketplace
- Handlers: 4 JavaScript modules (copy-paste ready)
- Tests: Happy path + error scenarios
- Docs: Setup guide, environment vars, troubleshooting

**Metrics:**
- Token exchange latency: < 500ms
- Error recovery: > 95% (graceful fallback)
- Coverage: OAuth 2.0 + PKCE fully spec-compliant

---

### Tarea 3: biblia-master-plan-template — Plan Master Ejecutable

**Descripción:**
Crear template ejecutable de "master plan" que cualquier hilo (Ejecutor, Catastro, Memento) puede usar para alinear sprints a los 14 Objetivos Maestros.

**Template Structure:**
```markdown
# [PROJECT_NAME] — Master Plan 2026

## Identidad
- **Owner:** [Name]
- **Objetivo Primario:** [Maestro #1-#15]
- **Objetivo Secundario:** [Maestro #N]
- **Key Metrics:** [3-5 measurable outcomes]

## Los 4 Capas (Roadmap)
### Capa 0 — Cimientos
- [ ] Task A (ETA: X min)
- [ ] Task B (ETA: Y min)

### Capa 1 — Manos
- [ ] Task A
- [ ] Task B

### Capa 2 — Inteligencia Emergente
- [ ] Task A
- [ ] Task B

### Capa 3 — Soberanía
- [ ] Task A
- [ ] Task B

### Capa 4 — Del Mundo
- [ ] Task A
- [ ] Task B

## Sprint Breakdown
| Sprint | Capas | ETA | Owner | Status |
|--------|-------|-----|-------|--------|
| Sprint A | 0 → 1 | 30min | Alfredo | Pending |
| Sprint B | 1 → 2 | 60min | Manus | Pending |

## Objetivo Alignment Matrix
| Objetivo # | Affected by | Status |
|------------|------------|--------|
| #1 (Valor real) | Sprint A, B | On track |
| #7 (No reinventar) | Sprint A | On track |

## Métricas + Monitoreo
- **Critic Score:** Current 78 → Target 95
- **Velocity:** 2 sprints/week
- **Quality:** 0 critical bugs

## Guardian of Objectives (Auto-check)
- Run this template monthly
- Verify each Objetivo is covered in roadmap
- Flag if any Objetivo not in active/upcoming sprints
```

**Implementation:**
```python
# biblia_master_plan_validator.py (included in kit)
def validate_master_plan(plan: Dict) -> ValidationResult:
    """Check that all 14 Objetivos are covered in roadmap"""
    uncovered = [obj for obj in MAESTRO_OBJETIVOS if obj not in plan['roadmap']]
    if uncovered:
        return ValidationError(f"Missing: {uncovered}")
    return ValidationSuccess("All 14 Objetivos covered")
```

**Deliverables:**
- Template: Markdown + JSON schema
- Validator: Python script to check alignment
- Examples: 2-3 filled templates (El Monstruo, kukulkan, future project)
- Docs: How to fill template, common mistakes, examples

**Metrics:**
- Coverage: 100% of 14 Objetivos must be addressed
- Alignment: No sprint exists that doesn't serve ≥1 Objetivo
- Auto-check: Runs monthly, alerts if gaps detected

---

### Tarea 4: Integración + Testing de los 3 Cimientos

**Descripción:**
Conectar los 3 cimientos (design-tokens, oauth-pattern, biblia-template) en flujo cohesivo.

**Integration Points:**
1. **Design tokens → Flutter app:** Import from @monstruo/design-tokens
2. **OAuth pattern → Manus skill:** Skill available in Manus marketplace
3. **Biblia template → sprint planning:** Auto-generate sprints from master plan

**Testing:**
```typescript
// test/integration.test.ts
describe('Cimientos Integration', () => {
  it('Design tokens load in Flutter app', () => {
    const colors = require('@monstruo/design-tokens').colors;
    expect(colors.forja).toBe('#F97316');
  });
  
  it('OAuth skill executes in Manus', async () => {
    const result = await manus.runSkill('manus-oauth-pattern', {
      provider: 'github'
    });
    expect(result.auth_url).toMatch(/^https:\/\/github.com\/login/);
  });
  
  it('Master plan validator checks alignment', () => {
    const plan = loadTemplate('biblia-master-plan-template');
    const validation = validateMasterPlan(plan);
    expect(validation.isValid).toBe(true);
    expect(validation.uncoveredObjectives).toHaveLength(0);
  });
});
```

**Deliverables:**
- Tests: 15+ integration tests
- CI/CD: GitHub Actions workflow for all 3 packages
- Docs: How 3 cimientos work together

**Metrics:**
- Test pass rate: 100%
- Build time: < 5 minutes (all 3 packages)
- Coverage: 90%+

---

## Aceptación

**Definición de Listo:**
1. @monstruo/design-tokens: NPM published, all tokens exported ✅
2. manus-oauth-pattern: Skill registered, all 4 handlers working ✅
3. biblia-master-plan-template: Validator passing, docs complete ✅
4. Integration: All 3 connected, 15+ tests passing ✅

**Quality Gates:**
- Design tokens: A11y compliance (WCAG AA)
- OAuth: PKCE spec-compliant, error handling complete
- Biblia: All 14 Objetivos covered, validator 100% accurate

**Post-sprint:**
- Sprint 88: Uses design tokens (v1.0 product quality)
- Sprint Mobile 1: Imports design tokens (Brand DNA fix)
- All future sprints: Use biblia-template for alignment

---

## Notas Técnicas

1. **Monorepo:** Los 3 paquetes viven en `/packages/@monstruo/`
2. **Versioning:** All start at v1.0.0-alpha, move to v1.0.0 post-testing
3. **Publishing:** Manus handles NPM (design-tokens, oauth-pattern), GitHub for template
4. **Backward compat:** Zero breaking changes (all new packages)

---

**Cowork (Hilo A), spec preparada 2026-05-06**
