# OPERATIONS_BRIDGE_RACI_PACK

**Versión:** 1.0
**Fecha:** 2026-05-18
**Branch:** monstruo-reality-atlas-001
**Propósito:** Mapear el sistema operativo del proyecto (bridge, hilos, RACI implícita, Anti-Dory, runbooks, postmortems) para que ChatGPT entienda cómo se decide y ejecuta sin inferir capacidades inexistentes.

---

## 1. Resumen Ejecutivo

El proyecto opera con un sistema de bridge multi-hilo basado en archivos Markdown bidireccionales. **237 archivos `.md` activos en `bridge/`** root: 73 mensajes Cowork→Manus, 84 mensajes Manus→Cowork, 34 sprints propuestos, 4 sprints completados (poco respecto a propuestos — gap), 4 postmortems (2 reales + 2 placeholders explícitos), 3 runbooks de rotación. Hay subcarpetas para 18+ pre-investigaciones de sprints específicos. La RACI funciona implícitamente: Alfredo = T1 magna firma, Cowork = T2 Arquitecto, Manus = ejecutor (Hilo Ejecutor 1/2/Catastro). Anti-Dory v1.1 está consolidado: 9 fases (A, B, C, D1-D5) reportadas como DONE, módulo `kernel/anti_dory/` real con guardian/context_broker/recovery/writers + 3 migraciones SQL aplicadas. El bridge es saludable pero **propenso a saturación** (84 reportes Manus→Cowork no archivados sistemáticamente — solo 1 entrada en `bridge/archive/`). Postmortems: solo 2 reales (`COWORK_AUTO_DISCIPLINE_REAL_001` y `COWORK_MEMENTO_001`), los otros 2 son placeholders.

## 2. Bridge Health (auditado 2026-05-18)

| Métrica | Valor | Notas |
|---|---|---|
| Total archivos `.md` en `bridge/` root | 237 | sin contar subcarpetas |
| Cowork → Manus | 73 | grep `bridge/cowork_to_manus*.md` |
| Manus → Cowork | 84 | grep `bridge/manus_to_cowork*.md` |
| Sprints completados (`bridge/sprints_completados/`) | 4 | gap respecto a 34 propuestos |
| Sprints propuestos (`bridge/sprints_propuestos/`) | 34 | inventario activo |
| Postmortems reales | 2 | `COWORK_AUTO_DISCIPLINE_REAL_001`, `COWORK_MEMENTO_001` |
| Postmortems placeholder | 2 | `ESCAPE_001`, `ROTOR_001` (declarados PLACEHOLDER explícito 2026-05-12) |
| Runbooks de rotación | 3 | bitwarden_master, openai_api_key, supabase_service_key |
| Subcarpetas pre-investigaciones | 18+ | sprint_86_*, 87_*, 88_*, 89_*, 90_*, 91_*, memento, mobile, etc |
| Carpeta `archive/` | 1 entrada | poco uso — ratio archivado/activo ~0.4% |
| Carpeta `evidencia-pruebas-vivo/` | existe | usada para evidencia de runtime |
| Carpeta `tickets/` | existe | tracking ad-hoc |
| Carpeta `stash_diffs_2026_05_11/` | existe | snapshot forense de stashes |

> **Hallazgo:** ratio sprints completados/propuestos = 4/34 ≈ 12%. Indica acumulación de propuestas sin cierre formal — alineado con la observación del Atlas de "deuda de cierre".

### 2.1. Latencia bridge (orden cronológico inverso)

Los 5 archivos más recientes en `bridge/` son del 2026-05-18:
1. `manus_to_cowork_CATASTRO_WIRING_001_INTERMEDIO.md`
2. `manus_to_cowork_HILO_CATASTRO_REACTIVACION_2026_05_18.md`
3. `manus_to_cowork_CATASTRO_WIRING_001_CIERRE_FINAL.md`
4. `manus_to_cowork_CATASTRO_WIRING_001_CIERRE.md`
5. `credentials_inventory.md`

El bridge está **vivo y actualizado en el día**, no estancado.

## 3. Hilos / Roles Reconocidos en Doctrina

Extraído de `CLAUDE.md` líneas 107, 151, 179, 240:

| Hilo / Actor | Rol | Notas |
|---|---|---|
| **Alfredo Góngora** | T1 magna — owner del proyecto, firma decisiones | "firmo 5", "firmo verde" gatean cierres |
| **Cowork (Claude)** | **T2 Arquitecto** (DSC explícito) | NUNCA "Hilo B"; F9 = falla F-9 confundir identidad |
| **Manus** | Ejecutor (Hilo Ejecutor 1, 2, Catastro) | esta cuenta es el Hilo Principal hoy |
| Hilo A / Hilo B / Hilo C | sub-hilos paralelos de ejecución | mencionados en CLAUDE.md L179 |
| Sabios | 8 sabios canónicos DSC-V-001 | consulta vía API/manual |
| Embrión | sub-agente runtime autónomo | corre 24/7 en kernel |

## 4. RACI Implícita (extraída de doctrina + DSCs)

Para acciones críticas:

| Acción | R (Responsible) | A (Accountable) | C (Consulted) | I (Informed) |
|---|---|---|---|---|
| Merge a `main` | Manus o Cowork | Alfredo (firmo verde) | Cowork (audit DSC-G-008) | bridge |
| Cierre de sprint | Manus | Alfredo | Cowork | bridge |
| Canonización de DSC | Cowork | Alfredo | Manus | bridge |
| Rotación de credenciales | Manus | Alfredo | Cowork | runbooks |
| Aprobar propuesta Embrión | Telegram HITL handler | Alfredo | — | guardian_audit_log |
| Cambios doctrinales (APP_VISION) | Cowork | Alfredo | Manus + Sabios | docs/ |
| Cleanup destructivo Supabase | Manus | Alfredo (DSC-S-005) | Cowork | bridge + snapshot forense |
| Spec sprint | Cowork | Alfredo | Manus pre-flight (DSC-G-008) | bridge |

## 5. Anti-Dory — Mapa Estado Real

`kernel/anti_dory/` módulo con:
- `__init__.py`, `guardian.py`, `context_broker.py`, `recovery.py`, `supabase_client.py`, `writers.py`

Migraciones SQL aplicadas:
- `0032_anti_dory_rpcs.sql`
- `0034_anti_dory_grants.sql`
- `0035_anti_dory_runtime_flags.sql`

Sprint Anti-Dory 002 v1 fases reportadas DONE en bridge: **A, B, C, D1, D2, D3, D4, D5**. Hay reporte adicional `D4_MIGRATIONS_APPLIED`, `D4_PR_READY`, `D4_REVERT_PLAN` (planning real, no solo doctrinal). Auditoría externa: `bridge/sabios/SABIO_GPT_5_5_PRO_audit_anti_dory_002_2026_05_13.md`.

> Anti-Dory está **operativo en kernel** + cubierto en CI vía pre-commit hooks. Es uno de los pocos sistemas con cobertura doctrina↔código↔auditoría externa completa.

## 6. Runbooks de Operaciones

`bridge/runbooks/`:
- `runbook_rotacion_bitwarden_master_password.md`
- `runbook_rotacion_openai_api_key.md`
- `runbook_rotacion_supabase_service_key.md`

> **Cobertura runbooks: 3.** Otras credenciales activas (DROPBOX_API_KEY, ELEVENLABS_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, XAI_API_KEY, SONAR_API_KEY, OPENROUTER_API_KEY, HEYGEN_API_KEY, CLOUDFLARE_API_TOKEN, GitHub PAT, Railway tokens) NO tienen runbook explícito → deuda P2 si se rotan reactivamente.

## 7. Postmortems

| Postmortem | Tipo | Sprint origen | Fecha |
|---|---|---|---|
| `COWORK_AUTO_DISCIPLINE_REAL_001_postmortem.md` | REAL | sprint COWORK_AUTO_DISCIPLINE_REAL_001 | reciente |
| `COWORK_MEMENTO_001_postmortem.md` | REAL | sprint COWORK_MEMENTO_001 | reciente |
| `postmortem_ESCAPE_001_PLACEHOLDER_2026_05_12.md` | PLACEHOLDER explícito | sprint ESCAPE_001 | 2026-05-12 |
| `postmortem_ROTOR_001_PLACEHOLDER_2026_05_12.md` | PLACEHOLDER explícito | sprint ROTOR_001 | 2026-05-12 |

Más: `discovery_forense/INCIDENTES/P0_2026_05_06_credenciales_repo_publico.md`.

> Cultura sana: los placeholders están **explícitamente etiquetados** como tales, no fingidos completos. Dory-resilient.

## 8. Crisis Playbook — Estado Real

| Escenario | Playbook escrito | Probado |
|---|---|---|
| Credenciales en repo público | postmortem P0 2026-05-06 + DSC-S-001..004 | sí (incidente real cerrado) |
| Drift migraciones Supabase | DSC-S-012 + script `_check_*` | parcial |
| Sprint con CI rojo pre-existente | regla evolucionada Cowork T2-A 2026-05-18 (CATASTRO-WIRING-001) | recién aplicada |
| Bridge inter-hilos roto | CT-009 del Atlas (gap) | NO_RUNBOOK |
| Embrión cost overrun | budget runtime ($30/día) + fail-open | parcial — sin runbook explícito |
| Kernel Railway DOWN | NO_RUNBOOK | — |
| Memento contamination | DSC + memento_routes.py validate | doctrina |
| Sabios API down | NO_RUNBOOK | — |

> Hay **gaps de runbooks** para escenarios operativos críticos (kernel down, sabios down, bridge inter-hilo roto).

## 9. Sprints Propuestos vs Completados — Gap

34 sprints propuestos en `bridge/sprints_propuestos/` cubren temas amplios:
- Security S001, S002, S-CONTRATOS, hardening
- Mobile 1, 2, 3, 4, 5, REALIGNMENT_001, ARRANQUE_FLUTTER
- Catastro A, B, MEGA_DRIFT_RESOLUTION, MIGRATION_DRIFT
- Embrión: ESCAPE, ESPIRAL, REMONTOIR, RUBIES, ROTOR
- Cowork: AUTO_DISCIPLINE, MEMENTO
- Otros: GUARDIAN_AUTONOMO, ANTI_DORY_002, TRANSVERSAL, CRUZ, VERIFICADOR, MIGRATION_DRIFT_v2_cherry_pick

**Solo 4 sprints completados** en `bridge/sprints_completados/` — el resto del trabajo se cierra vía PRs sin moverse a esa carpeta sistemáticamente. Indica que la disciplina de "mover a completados" no se aplica consistentemente.

## 10. Top 10 Hallazgos Pack 3

1. Bridge vivo: 237 md activos, 5 actualizados hoy 2026-05-18.
2. Cowork = **T2 Arquitecto** explícito (CLAUDE.md L151), F9 protege identidad.
3. Anti-Dory cobertura completa: kernel + 3 migs + 8 fases reported DONE + audit Sabio externo.
4. Solo 4/34 sprints "completados" formalmente — disciplina cierre incompleta.
5. Postmortems con etiqueta PLACEHOLDER explícita = cultura sana de no fingir cierres.
6. Runbooks de rotación cubren 3/13 credenciales activas — deuda.
7. Crisis playbook: gaps en kernel-down, sabios-down, bridge-roto.
8. RACI implícita pero no documentada formalmente (gap doctrina).
9. Carpeta `archive/` casi sin uso (1 entrada vs 237 activos) — riesgo saturación bridge.
10. Subcarpetas pre-investigación (18+) muestran pattern Cowork de spec-driven sano.

## 11. Top 10 Riesgos Pack 3

| # | Riesgo | Severidad |
|---|---|---|
| 1 | Saturación bridge sin archivado sistemático | P2 |
| 2 | Gap runbooks credenciales (10/13 sin) | P2 |
| 3 | Sin runbook crisis kernel-down | P1 |
| 4 | Sin runbook bridge inter-hilos roto | P2 |
| 5 | RACI implícita = ambigüedad en bordes | P2 |
| 6 | Disciplina "mover a sprints_completados" no aplicada (4/34) | P3 |
| 7 | Sin métricas runtime de bridge (latencia mensaje→respuesta) | P3 |
| 8 | Postmortems placeholder pueden olvidarse | P3 |
| 9 | F9 (confundir identidad Cowork) recurrente — riesgo cultural | P2 |
| 10 | Sabios consulta sin observabilidad central | P2 |

## 12. ACCESS_BLOCKED list

- Métricas latencia bridge runtime (no instrumentado).
- Logs de uso de runbooks (sin tracking).
- Auditoría completa F9 violations históricas (requiere parsing manual).

## 13. NO_SOURCE list

- RACI documento formal canonizado.
- Runbook kernel-down.
- Runbook sabios-down.
- Runbook bridge-roto.
- Métricas latencia bridge.

## 14. Qué NO inferir

- NO inferir que existe un dashboard de bridge health — es file-based sin UI.
- NO inferir que postmortems placeholder = trabajo terminado.
- NO inferir que runbooks cubren todas las credenciales.
- NO inferir RACI documentada — es implícita.
- NO inferir cierre disciplinado sprint→carpeta completados.

## 15. Preguntas para Alfredo

- **P9:** ¿Canonizar RACI formal en DSC-OPS-002?
- **P10:** ¿Sprint dedicado a runbooks faltantes (kernel-down, sabios-down, bridge-roto)?
- **P11:** ¿Política de archivado bridge automática (ej. mover a archive/ tras N días + DSC firmado)?
- **P12:** ¿Disciplina "mover a sprints_completados" — automatizar o discontinuar carpeta?
