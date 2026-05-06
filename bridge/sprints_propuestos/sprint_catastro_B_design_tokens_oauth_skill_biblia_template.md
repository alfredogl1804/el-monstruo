# Sprint Catastro-B — `@monstruo/design-tokens` + skill `manus-oauth-pattern` + plantilla `biblia-master-plan-template`

**Owner:** Hilo Catastro (Manus)
**Zona protegida:** fuera de `kernel/` — `packages/design-tokens/` (nuevo) + `skills/` (nuevo) + `docs/templates/` (nuevo)
**ETA estimada:** 8-12h reales con Apéndice 1.3 factor velocity (3 sub-sprints concatenados)
**Bloqueos:** ninguno (paralelizable con todos los demás sprints)
**Prerequisito:** v1.2 doc canónico + DSCs G-004 (Brand Engine) + X-003 (Manus-Oauth) + V-002 (validación realtime) firmados (✅)

---

## 1. Contexto

Sprint largo que cierra **3 cimientos compartibles** identificados en la Matriz de Cruces como "componentes compartidos de alta prioridad" (junto al checkout-stripe que toma su propio Sprint 90 en Hilo Ejecutor):

| Cimiento | DSC | Beneficiarios | Estado |
|---|---|---|---|
| `@monstruo/design-tokens` package | DSC-G-004 + DSC-MO-002 | TODOS los proyectos del Monstruo (20+) | ❌ NO existe |
| Skill `manus-oauth-pattern` | DSC-X-003 (alias DSC-GLOBAL-003) | Bot Telegram + Command Center + Mundo Tata + futuros web-db-user | ❌ NO existe |
| Plantilla `biblia-master-plan-template.md` | DSC-G-002 (7 capas) + patrón observado en biblias v4.x | Vivir Sano + CIP + posible BioGuard + futuras empresas-hijas con doctrina propia | ❌ NO existe |

Los tres son zona Catastro porque son trabajo de extracción + documentación + curaduría, no de orquestación técnica del kernel.

---

## 2. Objetivo único del sprint

Cerrar los 3 cimientos compartibles para que cada nuevo proyecto del portfolio nazca con identidad de marca + auth unificado + plantilla doctrinal — sin re-discutir de cero. Los 3 son **inversión multiplicadora**: una vez construidos, ahorran trabajo en cada empresa-hija futura.

---

## 3. Bloques del sprint

### 3.A — `@monstruo/design-tokens` package

**3.A.1 — Estructura del package**

```
packages/design-tokens/
├── package.json (name: "@monstruo/design-tokens", version: "0.1.0")
├── README.md
├── src/
│   ├── colors.ts (paleta canónica)
│   ├── typography.ts (escalas + familias)
│   ├── spacing.ts (escala 4px o 8px)
│   ├── animations.ts (curvas + duraciones canónicas)
│   ├── shadows.ts (sistema de elevación)
│   ├── radius.ts (border radius escala)
│   └── index.ts (re-export)
├── css/
│   ├── tokens.css (CSS custom properties)
│   └── reset.css (reset minimal con tokens)
├── tailwind/
│   └── preset.js (Tailwind config preset que cualquier proyecto puede extender)
├── tests/
└── docs/
    ├── PALETA.md (con visualización HTML de cada color)
    └── COMO_USAR.md (ejemplos en React, Next.js, Vite, Flutter)
```

**3.A.2 — Paleta canónica**

Source DSC-MO-002:
- `--color-forja` = `#F97316` (Naranja Forja, primario)
- `--color-graphite` = `#1C1917` (oscuro)
- `--color-acero` = `#A8A29E` (medio)

Derivar escala completa cada uno (50, 100, 200... 900) usando algorithm de luminosidad consistente. Documentar con muestras visuales cada tono.

**3.A.3 — Naming canónico anti-anti-patrón**

DSC-G-004 prohíbe naming genérico. Tokens NUNCA llevan nombres como `primary`, `secondary`, `gray`. SIEMPRE llevan identidad:

✅ `forja-500`, `graphite-700`, `acero-300`
✅ `text-forja`, `bg-graphite`, `border-acero`

❌ `primary`, `secondary`, `bg-dark`, `text-light`

**3.A.4 — Tailwind preset**

`tailwind/preset.js` exportable que cualquier proyecto Tailwind importa con:

```js
// tailwind.config.js de cualquier empresa-hija
module.exports = {
  presets: [require('@monstruo/design-tokens/tailwind/preset')],
  content: [...]
};
```

Y obtiene `bg-forja-500`, `text-graphite-900`, `border-acero-300` automáticamente sin redefinir nada.

**3.A.5 — Documentación visual**

`docs/PALETA.md` con HTML embedded mostrando cada token visualmente (idealmente accesible vía GitHub Pages del repo el-monstruo). Si Sprint 90 cierra con repo único de pipeline output, el design tokens visual hereda esa infra para tener su propio preview.

**3.A.6 — Tests**

Tests que verifican que los tokens están definidos + escalas tienen consistencia matemática + el preset Tailwind compila sin errores.

### 3.B — Skill `manus-oauth-pattern`

**3.B.1 — Estructura del skill**

```
skills/manus-oauth-pattern/
├── SKILL.md (entry point + protocolo)
├── references/
│   ├── arquitectura.md (cómo funciona Manus-Oauth bajo el capó)
│   ├── scaffold-web-db-user.md (estructura del scaffold)
│   ├── ejemplo-bot-telegram.md (cómo se usa en Bot)
│   ├── ejemplo-command-center.md (cómo se usa en Command Center)
│   ├── ejemplo-mundo-tata.md (cómo se usa en Mundo Tata)
│   └── checklist-integracion.md (10-step checklist para nuevo proyecto)
└── templates/
    ├── env-vars-template.txt
    ├── auth-middleware-template.ts
    └── user-table-migration.sql
```

**3.B.2 — Contenido del SKILL.md**

Descripción + cuándo invocar + protocolo de uso:
- Cuándo usar: cualquier proyecto web-db-user que necesita auth (NO usar para auth de servicio internal del Monstruo, eso es otro flow)
- Cómo integrar paso a paso
- Anti-patrones (qué NO hacer al integrar Manus-Oauth)
- Cross-link con DSC-X-003

**3.B.3 — Templates**

Templates copy-paste listos:
- env vars con placeholders
- middleware de auth en TypeScript que valida tokens Manus
- migración SQL canónica para tabla `users` compatible con Manus-Oauth
- componente UI de "Sign in with Manus" con styling forja+graphite+acero

**3.B.4 — Tests**

Validar que los templates compilan + la migración SQL aplica en una DB Supabase test sin errores.

### 3.C — Plantilla `biblia-master-plan-template`

**3.C.1 — Análisis de las biblias existentes**

Leer las 14 biblias del skill `creacion-cip` + las biblias v4.x del catálogo (que está indexado pero las sub-páginas no migradas) + cualquier otra biblia que aparezca en el portfolio.

Identificar patrón estructural común:
- ¿Qué secciones tiene una biblia magna?
- ¿Cuáles son obligatorias vs opcionales?
- ¿Cómo se valida la calidad de una biblia?
- ¿Cuáles son los anti-patrones de biblias incompletas?

**3.C.2 — Plantilla canónica**

`docs/templates/biblia-master-plan-template.md` con sections:

```markdown
# Biblia Master Plan v1.0 — [NOMBRE PROYECTO]

## 1. Identidad y Análisis Estratégico
   - Propuesta de valor única
   - Mercado y posicionamiento
   - Diferenciadores
   - Stack tecnológico recomendado
   - SLOs declarados

## 2. Gobernanza y Modelo de Confianza
   - Modelo de negocio (suscripción, pass-through, freemium...)
   - Política de privacidad
   - Compliance (GDPR, CCPA, regulaciones específicas del dominio)
   - Auditoría
   - Respuesta a incidentes

## 3. Modelo Mental y Maestría
   - Paradigma central
   - Mental models para usuarios power
   - Curva de aprendizaje

## 4. Las 7 Capas Transversales (DSC-G-002 obligatorio)
   - Motor de Ventas
   - SEO y Descubrimiento
   - Publicidad y Campañas
   - Tendencias y Adaptación
   - Administración y Operaciones
   - Finanzas
   - Resiliencia Agéntica

## 5. Las 4 Capas Arquitectónicas (DSC-G-003 obligatorio)
   - Capa 0 Cimientos
   - Capa 1 Manos
   - Capa 2 Inteligencia Emergente
   - Capa 3 Soberanía

## 6. Decisiones Pendientes
   - Lista de DSCs `pendiente` con campo `bloqueante: SI/NO`

## 7. Roadmap
   - Sprints v0 → v1 → v2

## 8. Cross-links con otros proyectos
   - Vía DSC `cruce_inter_proyecto`
   - Eje de convergencia futura per DSC-X-006

## 9. Capa de Inyección IA (L12 — opcional según proyecto)
   - Instrucciones operacionales para inyectar en prompts de orquestadores

## 10. Apéndice
   - Semillas detectadas durante el diseño
   - Patrones replicables
```

**3.C.3 — Skill `usar-biblia-template`**

Skill complementario `skills/usar-biblia-template/SKILL.md` que documenta cuándo invocar la plantilla + cómo customizarla per dominio del proyecto.

**3.C.4 — Validación**

Tomar una empresa-hija que ya tiene biblia (CIP o Vivir Sano) y verificar que la plantilla cubre todas sus secciones críticas. Si falta algo magna, agregarlo a la plantilla antes de declarar cierre.

### 3.D — Documentación cross-cutting

**3.D.1 — README magna del directorio `packages/`**

Si `packages/` no existe aún, crearlo con README magna que documenta:
- Convención de naming `@monstruo/*`
- Patrón de mantenimiento (versionado, breaking changes, deprecation)
- Lista de packages actuales + estado de cada uno

**3.D.2 — Reporte de cierre al bridge**

`bridge/cowork_to_manus_REPORTE_CIMIENTOS_COMPARTIBLES_<fecha>.md` con:
- Status de los 3 cimientos
- Cómo importarlos / usarlos en proyectos nuevos
- Lista de proyectos del portfolio que deberían adoptarlos en próximos sprints
- Métricas: LOC ahorradas estimadas por proyecto que adopta cada cimiento

---

## 4. Magnitudes esperadas

- ~1,500 LOC nuevas (package design-tokens + templates skills)
- 1 package npm + 2 skills nuevos + 1 plantilla magna
- ~20 archivos nuevos
- ~10 tests
- 1 reporte de cierre + actualizaciones a manifests relevantes

---

## 5. Disciplina aplicada

- ✅ DSC-G-004: TODO output con identidad de marca, naming canónico
- ✅ DSC-V-002: validar versión vigente de Tailwind, npm conventions, SQL syntax contra registries oficiales
- ✅ DSC-V-001: si hay duda sobre estructura de la plantilla biblia, consultar a los 6 Sabios
- ✅ Brand DNA: design-tokens es ejemplo magna de identidad pixel-a-pixel — no usar nombres genéricos en NINGÚN token

---

## 6. Cierre formal

Cuando los 4 bloques cierren verde, Hilo Catastro declara:

> 🏛️ **3 Cimientos Compartibles v0.1 — DECLARADOS** (`@monstruo/design-tokens` + skill `manus-oauth-pattern` + plantilla `biblia-master-plan-template`)

Y reporta al bridge con paths + ejemplos de uso + lista de proyectos del portfolio que deberían adoptar cada cimiento en próximos sprints.

---

## 7. Próximos consumidores de los cimientos

Una vez cerrado:

- **Cualquier sprint nuevo de UI** (Mobile 1-6, Command Center, Marketplace, CIP frontend) importa `@monstruo/design-tokens` desde su Tailwind config — toda nueva UI nace con identidad sin discutir colores
- **Cualquier sprint web-db-user nuevo** (Bot extension, futuras empresas-hijas con login) sigue el skill `manus-oauth-pattern` — auth unificada sin reinventar
- **Cualquier empresa-hija magna que requiera biblia** (CIP nueva versión, Vivir Sano expansión, BioGuard cuando arranque) usa la plantilla — doctrina coherente sin estructuras divergentes

Esto cumple Obj #3 (mínima complejidad necesaria) + Obj #7 (no reinventar la rueda) aplicados al portfolio entero.

---

— Cowork (Hilo A), spec preparada 2026-05-06.