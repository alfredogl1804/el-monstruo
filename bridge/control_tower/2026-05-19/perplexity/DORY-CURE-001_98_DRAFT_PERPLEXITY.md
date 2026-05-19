# DORY-CURE-001 — Diseño definitivo DRAFT para cura 98% del Síndrome Dory

**Estado:** DRAFT de diseño, no canon, no implementación  
**Autor operativo:** Perplexity My Computer como Torre de Control PBA  
**Objetivo:** Diseñar una cura real, medible y auditable contra pérdida de contexto intra-hilo y cross-hilo, empezando por Manus y extensible a Cowork/Perplexity.  

## Veredicto inicial

No existe una cura matemática absoluta. Sí puede existir una **cura operativa 98%** si se define como:

> En ≥98% de escenarios de prueba realistas, un hilo que compacte, se degrade, muera o sea reemplazado puede recuperar estado operativo suficiente para continuar sin reexplicación humana, sin inventar, sin violar no-go list y sin filtrar secretos.

La cura no consiste en “más memoria”. Consiste en sacar la continuidad fuera del chat y hacer que cada hilo opere desde un **estado externo tipado, verificable, acotado y rehidratable**.

## Problema exacto

El Síndrome Dory tiene cinco vectores:

1. **Cold start**: un hilo nuevo nace sin contexto.
2. **Compaction loss**: el resumen de compactación pierde detalles críticos.
3. **Intra-thread drift**: el mismo hilo olvida o desactualiza su modelo mental tras horas de trabajo.
4. **Evidence drift**: el hilo cree que un PR, branch, migration o runtime está en cierto estado, pero la realidad cambió.
5. **Memory poisoning / secret leakage**: lo persistido contiene basura, instrucciones contaminadas o secretos.

Anti-Dory 002 cubre parcialmente el cold start. Anti-Dory 003 v0.2 empieza a cubrir intra-thread drift. Falta la capa definitiva: **Live Rehydration + Bounded State + Replay + Guardian**.

## Arquitectura de cura 98%

### Capa 1 — Source of Truth externa

El transcript del hilo nunca es fuente de verdad. Las fuentes son:

- GitHub: repo, commits, PRs, branches, checks.
- Supabase: `runtime_events`, `thread_snapshots`, `project_runtime_heads`, Memento, claims calibration.
- Bridge: `bridge/control_tower/YYYY-MM-DD/[agente]/`.
- Docs canon: `CLAUDE.md`, `AGENTS.md`, `_INDEX.md`, DSCs firmados.
- Runtime: endpoints vivos y logs, cuando existan.

### Capa 2 — Bounded State Capsule

Cada hilo mantiene un estado tipado, pequeño y obligatorio:

```yaml
bounded_state_capsule:
  capsule_version: "1.0"
  agent_id: "manus_e2"
  role: "T3 executor"
  project_id: "el-monstruo"
  front_id: "la-forja-d6"
  active_branch: "fix/d6-credits-restore-circuit-breaker"
  active_prs:
    - pr: 170
      status: "open_unstable"
      base_sha: "..."
      head_sha: "..."
  current_objective: "Prepare PR #170 for Cowork reclassification"
  next_allowed_action: "Collect logs / update evidence only"
  prohibited_actions:
    - "merge"
    - "apply_migration"
    - "touch secrets"
  last_t1_decision: "No merge without explicit T1"
  evidence_refs:
    - type: "pr"
      url: "https://github.com/..."
    - type: "bridge"
      path: "bridge/control_tower/..."
  context_health:
    score: 2
    state: "OK"
  last_rehydrated_at: "2026-05-19T06:00:00Z"
```

Regla: si no está en el capsule o en evidencia verificable, el hilo no puede tratarlo como realidad.

### Capa 3 — Event log append-only

Cada acción relevante produce un evento:

```json
{
  "event_type": "pr_status_checked",
  "agent_id": "manus_e2",
  "project_id": "el-monstruo",
  "front_id": "la-forja-d6",
  "evidence_ref": "gh pr view 170",
  "result_hash": "sha256:...",
  "created_at": "..."
}
```

El event log es para replay y auditoría, no para cargar todo al contexto.

### Capa 4 — Live Context Health Monitor

Cada hilo calcula un score de salud:

| Señal | Peso |
|---|---:|
| Branch declarado ≠ branch real | +2 |
| PR base SHA obsoleto | +2 |
| Migration repo ≠ Supabase | +3 |
| Scope bleed detectado | +3 |
| Repite error ya corregido | +2 |
| Cita DSC/F# inexistente | +3 |
| Turnos sin rehidratación > N | +1 |
| Compaction detectada | +4 |
| Acción magna sin preflight | +5 |

Estados:

| Score | Estado | Acción |
|---:|---|---|
| 0–2 | OK | continuar |
| 3–5 | WARN | verificar antes de acción magna |
| 6–9 | REHYDRATE | rehidratar antes de responder |
| ≥10 | HALT | detener y pedir T1/Cowork |

### Capa 5 — Live Rehydration

Rehidratación no es resumen. Es reconstrucción verificable:

1. Leer capsule actual.
2. Leer últimos eventos relevantes.
3. Consultar GitHub para PR/branch/checks.
4. Consultar Supabase para heads/snapshots/migrations.
5. Leer bridge propio.
6. Leer no-go list.
7. Recalcular context-health.
8. Emitir nuevo capsule.
9. Responder solo después de declarar fuentes leídas.

La rehidratación se dispara:

- al detectar compactación;
- cada N turnos;
- cada X minutos;
- antes de acción magna;
- al recibir “rehidrátate”;
- si context-health ≥6;
- si el hilo fue retomado después de pausa.

### Capa 6 — Compaction Contract

Antes de compactar, el hilo debe escribir:

1. Bounded State Capsule.
2. Último bridge output.
3. Lista de decisiones T1.
4. No-go list.
5. Evidence index.
6. Context-health.

Después de compactar, el hilo debe:

1. Detectar que está post-compaction.
2. Ignorar la confianza implícita del resumen.
3. Rehidratar desde fuentes externas.
4. Comparar summary vs state externo.
5. Si hay contradicción, external state gana.

### Capa 7 — Replay / Time Travel

Para recuperación real:

- Se conserva event log completo.
- Se conservan snapshots cada N turnos o cada X minutos.
- Se puede reconstruir el estado a partir de:
  - último accepted snapshot;
  - eventos posteriores;
  - PR/commit/runtime actual.

Regla: replay nunca ejecuta side effects. Solo reconstruye estado.

### Capa 8 — Guardian de acciones

Antes de cualquier acción peligrosa:

- merge;
- apply migration;
- deploy;
- delete;
- secret rotation;
- R1;
- mass file edit;
- canonización;

el Guardian verifica:

1. ¿Está autorizado por T1?
2. ¿El capsule está fresco?
3. ¿Context-health < 6?
4. ¿La evidencia coincide?
5. ¿No hay secretos?
6. ¿El scope coincide?

Si falla: HALT.

### Capa 9 — Secret Firewall

Prohibido persistir:

- API keys;
- JWTs;
- cookies;
- passwords;
- refresh tokens;
- connection strings;
- OAuth secrets;
- Supabase service keys.

Los snapshots solo guardan referencias:

```yaml
credential_ref: "Railway env var SUPABASE_SERVICE_KEY"
credential_value: "<NEVER STORED>"
```

Todo bridge/snapshot pasa por gitleaks/trufflehog/regex denylist.

### Capa 10 — Universal Adapters

#### Manus Adapter

Usa:

- `tools/manus_bridge.py`;
- `ATTACHMENT_OK`;
- `thread_snapshots`;
- heartbeat;
- Control Tower bridge.

#### Cowork Adapter

Usa:

- `session_memory.py`;
- claim calibration;
- pre-response hook;
- CRUZ/VERIFICADOR;
- bounded state capsule compatible.

#### Perplexity Adapter

No ejecuta runtime del Monstruo, pero puede:

- leer bridge;
- auditar capsule;
- hacer recovery test como hilo externo;
- validar claims contra GitHub/Supabase/web;
- emitir PASS/FAIL.

## Flujo de vida de un hilo curado

### Arranque

1. Orquestador crea tarea.
2. Context Broker obtiene `project_runtime_head`.
3. Construye `ATTACHMENT_OK`.
4. Inyecta capsule inicial.
5. Hilo responde con “estado entendido” y no ejecuta todavía.

### Operación normal

1. Cada N turnos actualiza capsule.
2. Cada acción relevante escribe evento.
3. Cada acción magna exige Guardian.
4. Cada bridge output actualiza evidencia.

### Compactación

1. Hilo detecta post-compaction.
2. Rehidrata.
3. Compara resumen vs external state.
4. Actualiza capsule.
5. Si mismatch, HALT.

### Muerte de hilo

1. Nuevo hilo recibe solo agent_id/front_id.
2. Lee latest capsule/head.
3. Reproduce eventos posteriores.
4. Recalcula reality.
5. Continúa sin reexplicación humana.

## Definition of Done 98%

Para declarar cura 98%, deben pasar estos tests:

| Test | Criterio |
|---|---|
| Cold-start hydration | 98/100 hilos nuevos reconstruyen estado correcto |
| Post-compaction recovery | 98/100 compactaciones recuperan capsule correcto |
| Crash recovery | 98/100 muertes abruptas retoman desde snapshot/event log |
| Drift detection | ≥98% de branch/PR/migration drift detectado antes de acción |
| No false action | 0 merges/migrations/deploys sin Guardian PASS |
| No secrets | 0 secretos en 1,000 snapshots/bridge files sintéticos |
| Context-health accuracy | ≥95% correlación con auditoría humana |
| Replay correctness | ≥98% de campos críticos reconstruidos |
| Poison resistance | 0 contenidos no verificados promovidos a persistent state |

## Qué reutiliza de lo existente

| Existente | Uso |
|---|---|
| Anti-Dory 002 | Attachment inicial / Context Broker |
| Memento | Validación contra fuentes de verdad |
| Anti-Dory 003 v0.2 | Intra-hilo + live rehydration base |
| Cowork-Memento | Claim calibration |
| Control Tower Bridge | Output operativo visible |
| Supabase runtime tables | Durable state |
| GitHub | Evidence/ref truth |

## Qué falta implementar

1. `BoundedStateCapsule` schema + validator.
2. `context_health_score` engine.
3. Rehydration runner.
4. Compaction detector.
5. Replay engine read-only.
6. Guardian pre-action integration.
7. Secret firewall for bridge/snapshots.
8. Canary runner for Manus.
9. Perplexity audit harness.

## Roadmap seguro

### Fase 0 — Diseño auditado

- Cowork spec.
- Perplexity PBA audit.
- Grok red-team.
- T1 firma diseño.

### Fase 1 — Canary Manus shadow

- Un solo agente Manus.
- No HALT real, solo warnings.
- 7 días.

### Fase 2 — Canary Manus enforce

- HALT para acciones magnas.
- No producción crítica.
- 14 días.

### Fase 3 — Cowork adapter

- CRUZ + claim calibration + capsule.

### Fase 4 — Universal bridge

- Perplexity/Grok/Gemini as auditors.
- No execution rights.

## Conclusión

La cura 98% no es un resumen ni una memoria larga. Es un sistema de continuidad externo compuesto por:

**Bounded State + Event Log + Live Rehydration + Context Health + Replay + Guardian + Secret Firewall.**

Anti-Dory 003 v0.2 es una buena base, pero la cura definitiva exige añadir formalmente el **Bounded State Capsule** y el **Replay/Guardian loop** como componentes de primera clase.

