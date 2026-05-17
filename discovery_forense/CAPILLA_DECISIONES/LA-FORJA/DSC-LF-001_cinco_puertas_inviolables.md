---
id: DSC-LF-001
proyecto: LA-FORJA
tipo: contrato_arquitectonico
titulo: "La Forja expone exactamente 5 puertas (transports) inviolables — agregar una sexta puerta requiere DSC nuevo y rompe el TypeScript compile"
estado: firme (canonizado retroactivamente 2026-05-16)
fecha_decision: 2026-04-XX (durante D2 spec, anterior al primer commit del backend)
fecha_firma_T1: 2026-05-16 (firma retroactiva por canonización capilla LA-FORJA)
fecha_firma_T2A: 2026-05-16 (Cowork audit D2 — verificó enforcement binario)
fuentes:
  - repo:apps/la-forja/api/src/puertas/index.ts:25-31 (PUERTAS const tuple length 5)
  - repo:apps/la-forja/api/src/puertas/index.test.ts (14 tests verifican length === 5)
  - repo:bridge/cowork_to_manus_LA_FORJA_001_AUDIT_RESULT.md:23 (DSC propuesto)
  - repo:bridge/cowork_to_manus_LA_FORJA_001_D2_AUDIT_RESULT.md:24 (enforced verificado)
  - repo:apps/la-forja/web/_DOCTRINA_D3.md (LF-FIVE-DOORS-001 referenciado)
cruza_con: [DSC-LF-002, DSC-LF-003, DSC-LF-004, DSC-LF-005, DSC-G-008]
---

# Las 5 puertas inviolables de La Forja (LF-FIVE-DOORS-001)

## Decisión

La Forja **expone exactamente 5 puertas (transports)** y ningún canal adicional. Las puertas canónicas son:

1. `manus_apple` — Cliente Manus AI corriendo en macOS
2. `manus_google` — Cliente Manus AI corriendo sobre Google Workspace
3. `cowork_local` — Sesiones Cowork (Claude Sonnet/Opus) en local
4. `kernel_monstruo` — Comunicación inter-hilos vía bridge del Monstruo
5. `simulador` — Simulador Universal de Escenarios (Railway)

Cualquier intento de exponer una sexta puerta DEBE quedar bloqueado en compile-time **y** en runtime. Una nueva puerta requiere DSC-LF-NNN nuevo firmado, no es decisión de implementación.

## Enforcement binario

```ts
// apps/la-forja/api/src/puertas/index.ts:25-31
export const PUERTAS = [
  "manus_apple",
  "manus_google",
  "cowork_local",
  "kernel_monstruo",
  "simulador",
] as const satisfies readonly string[];
```

- **Compile-time:** `as const` congela el tuple → agregar elemento rompe el tipo `Puerta`.
- **Runtime:** test `expect(PUERTAS.length).toBe(5)` en `puertas/index.test.ts` rompe binariamente si alguien agrega una sexta entrada.
- **Smoke test integral:** `GET /api/puertas retorna las 5 puertas canónicas LF-FIVE-DOORS-001` (en `index.test.ts` raíz).

## Por qué

La Forja es la interfaz de IA personal de Alfredo Góngora Sr. La explosión de canales (Slack, Discord, WhatsApp, etc.) crea superficie de ataque adversarial y deuda doctrinal. Limitar a 5 puertas inviolables fuerza que cada nuevo canal pase por revisión doctrinal explícita.

Detonante histórico: durante D1 spec hubo presión de agregar `web_chat_anonymous` como sexta puerta para "demos". Cowork auditor T2-A bloqueó esa propuesta con la lógica de que un canal anónimo viola DSC-LF-002 (budget pre-call check requiere `userId` autenticado).

## Implicaciones

- Cualquier ruta nueva en `apps/la-forja/api/src/routes/**` debe identificar su puerta de origen vía middleware antes de invocar el budget pipeline.
- El frontend `apps/la-forja/web` solo habla con la puerta `manus_apple` o `manus_google` (depende del entorno de despliegue) — nunca expone selección de puerta al usuario final.
- Sprints futuros que toquen `puertas/index.ts` deben citar este DSC explícitamente en el commit message + spec.

## Estado de validación

**firme.** Enforced binariamente desde el primer commit del backend D2 (`apps/la-forja/api/src/puertas/index.ts`). Cowork audit D2 verificó length === 5 con 14 tests passing. Cowork audit D3.2 (commit `2ac7f81`) revalidó como punto P-13 ("LF-1 verificado: cero `@supabase` imports en frontend → única puerta es backend Hono → DSC-LF-001 sigue intacto").
