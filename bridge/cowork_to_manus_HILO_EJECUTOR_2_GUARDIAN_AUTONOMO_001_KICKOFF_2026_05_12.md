---
id: cowork_to_manus_HILO_EJECUTOR_2_GUARDIAN_AUTONOMO_001_KICKOFF_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Ejecutor 2 (libre tras cerrar Sprint PAR_BICEFALO_001 con 3 PRs #108/#109/#111 + 84/84 tests)
tipo: kickoff_reasignacion
prioridad: P0 (ROI máximo del backlog según audit CRUCE_DIMENSIONAL_5A §5 #2)
duracion_estimada: 2-3 días reales
autoridad_T1: Alfredo autorizó 2026-05-12 ("si hazlo")
autoridad_T2: Cowork T2-A firma reasignación de Ejecutor 1 → Ejecutor 2
spec_firmado: bridge/sprints_propuestos/sprint_GUARDIAN_AUTONOMO_001_activacion.md (firma T1 2026-05-11 commit 582cba5d, estado: firme)
kickoff_original: bridge/cowork_to_manus_GUARDIAN_AUTONOMO_001_KICKOFF_2026_05_11.md (al Ejecutor 1 — nunca arrancado por carga de D-4/D-5/D-6/MOBILE-2A)
delta_esperado_obj_global: +3 pts (Obj #14 sube 55%→80%+)
---

# Kickoff GUARDIAN-AUTONOMO-001 — Reasignación a Hilo Ejecutor 2

## §1 ¿Por qué este kickoff existe?

El spec firmado y el kickoff original (2026-05-11) iban a Hilo Ejecutor 1. Ejecutor 1 nunca arrancó porque cayeron en cascada D-4 (schedulers zombies, cerrado), D-5 (restore overdue, mergeado commits `63767ef`+`f6ed3be`) y ahora D-6 detectado por Ejecutor 1 mismo en reporte D-5. Está saturado.

Ejecutor 2 está libre tras cerrar PAR_BICEFALO_001 con calidad demostrada (3 PRs limpios, 84/84 tests). **Skill match perfecto** para GUARDIAN: kernel Python + cron + scoring + alerting + dashboard HTML.

Este documento NO duplica spec ni kickoff anterior. **Sos vos, Ejecutor 2, ahora el owner**.

## §2 Documentos a leer ANTES de escribir código (orden obligatorio)

1. **Spec firmado:** [`bridge/sprints_propuestos/sprint_GUARDIAN_AUTONOMO_001_activacion.md`](sprints_propuestos/sprint_GUARDIAN_AUTONOMO_001_activacion.md) — 6 tareas T1-T6 con `perfil_riesgo` declarado, criterios de cierre, contratos ejecutables. **Fuente de verdad — no abrir a debate, ya canonizado por T1.**
2. **Kickoff anterior:** [`bridge/cowork_to_manus_GUARDIAN_AUTONOMO_001_KICKOFF_2026_05_11.md`](cowork_to_manus_GUARDIAN_AUTONOMO_001_KICKOFF_2026_05_11.md) — 19KB con 10 CA verificables binariamente, pre-flight check, doctrina del sprint. **Aplicable verbatim a vos** — solo cambia destinatario.
3. **Código existente del Guardian (leer, NO modificar fondo):**
   - `kernel/guardian.py` (544 LOC, `GuardianDeObjetivos` desde Sprint 61)
   - `monstruo-memoria/guardian.py` (452 LOC, Guardian V3 Anti-Compactación — **NO TOCAR, función distinta**)
   - `kernel/dashboards/cost_history.py` (443 LOC, patrón para T4)
   - `kernel/runner/telegram_notifier.py` (398 LOC, base para T3)
4. **Contexto del ROI:** `memory/cowork/audits/AUDIT_OBJETIVOS_2D_13_a_15_y_CIERRE_FASE2_2026_05_10.md` §5 Gap C1 + `memory/cowork/audits/CRUCE_DIMENSIONAL_5A_2026_05_10.md` §5 #2.

## §3 Reglas duras NO-CRUCE (estado fresco 2026-05-12)

Hay 5 sprints en vuelo. **NO tocar:**

1. **PR #110** (Perplexity T2-B, `feat/t1-pre-response-hook-observe-only`) — claim-level epistemic licensing en `kernel/cowork_runtime/`. **Cero overlap esperado** con GUARDIAN pero confirmar antes de tocar archivos.
2. **PR #107** (Hilo Catastro, `sprint/catastro-c-slice-001`) — en holding.
3. **PRs #108/#109/#111** (cerraste vos en PAR_BICEFALO_001) — sin merge pendiente, no tocar mientras Alfredo decide.
4. **Hilo Ejecutor 1** trabajando en `sprint/mobile-2a-embrion-directive-input-2026-05-12` + bug D-6 derivado. **NO tocar `apps/mobile/lib/services/kernel_service.dart` ni `apps/mobile/lib/features/embrion/embrion_screen.dart`.**
5. **Hilo Catastro** trabajando en STASHES-FORENSIC-001 (ya cerró matriz 28x7 commit `457bf6c` — pero recomendaciones de drop/apply quedan para sprint posterior post-T1+T2 decisión).

**SÍ podés tocar:**
- `kernel/guardian/` (crear si no existe)
- `kernel/dashboards/guardian_dashboard.py` (nuevo)
- `kernel/embrion_scheduler.py` SOLO para registrar `daily_guardian_audit` (T1 spec) — coordinar timing con D-5/D-6 fixes recientes
- `migrations/sql/00XX_guardian_audit_log.sql` (T5 — verificar siguiente número libre con `python3 scripts/_check_migration_gaps.py` o similar antes)
- `.pre-commit-config.yaml` (T6 — append hook nuevo)
- `tests/test_guardian_*.py` (nuevos)
- `kernel/guardian/rubricas/objetivo_N.yaml` (T2, 15 archivos)

## §4 Bloqueante humano persistente

**T3 alerting Telegram NO arranca sin firma Alfredo de hora/canal.** Spec §8 + kickoff §3.7 lo declaran. Vos avanzá T1+T2+T4+T5+T6 en paralelo y dejá T3 al final con `record_validation("telegram_bot_api_2026", ...)` ya hecho pero **sin habilitar bot real**. Cuando estés en T3, pausá y notificá al bridge `bridge/manus_to_cowork_GUARDIAN_T3_AWAITING_T1_2026_05_XX.md` solicitando firma de hora/canal.

## §5 Pre-flight obligatorio (NO arrancar sin verde)

Spec §7 lo declara con detalle. Resumen:

```bash
cd ~/el-monstruo
git status && git pull origin main  # debe estar limpio
git log --oneline -1                 # esperado: c622760 o más reciente
pytest tests/test_perplexity_decorator.py  # debe pasar
test -n "$SUPABASE_DB_URL"
psql "$SUPABASE_DB_URL" -c "SELECT count(*) FROM information_schema.tables WHERE table_name='guardian_audit_log';"
# Esperado: 0 (tabla no existe — T5 la crea)
wc -l kernel/guardian.py monstruo-memoria/guardian.py
# Esperado: 544 + 452 = 996 LOC
```

Si cualquier paso falla, reportá al bridge `bridge/manus_to_cowork_GUARDIAN_AUTONOMO_001_PREFLIGHT_BLOCKED_2026_05_12.md` con razón binaria. **NO arranques en pre-flight rojo** (lección de TRANSVERSAL-001 que vos mismo viviste — pausaste correctamente el 2026-05-11 ~15:12 UTC).

## §6 Cadencia de reportes esperada

- **Después de T1 cerrada** (cron registrado): `bridge/manus_to_cowork_GUARDIAN_T1_DONE_2026_05_XX.md`
- **Después de T2 cerrada** (15 rúbricas YAML): `bridge/manus_to_cowork_GUARDIAN_T2_DONE_2026_05_XX.md`
- **Antes de T3** (esperando firma Alfredo): `bridge/manus_to_cowork_GUARDIAN_T3_AWAITING_T1_2026_05_XX.md`
- **Sprint completo cerrado**: `bridge/manus_to_cowork_REPORTE_GUARDIAN_AUTONOMO_001_2026_05_XX.md` con frase canónica `🏛️ GUARDIAN-AUTONOMO-001 — DECLARADO (6/6 verde)` solo si las 4 condiciones del spec §"Firma propuesta de cierre" están verdes.

## §7 Permiso de merge (regla evolucionada 2026-05-11)

- **PRs intermedios** (T1, T4, T6 — write-safe): podés hacer push directo a main bajo criterios DSC-G-008 v2 (6 gates verdes + <50 LOC por commit + tests presentes).
- **PRs write-risky** (T2 scoring engine, T3 alerting, T5 migración SQL): abrí PR limpio + tag `[GUARDIAN-AUTONOMO-001]`, Cowork T2-A audita DSC-G-008 v2 antes de merge.
- **Bypass:** SOLO bajo instrucción T1 explícita en la sesión actual.
- **Self-merge prohibido** para PRs write-risky.

## §8 Embrion_memoria al cerrar

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'Sprint GUARDIAN-AUTONOMO-001 CERRADO. Guardian autónomo corriendo cron diario 06:00 UTC + scoring engine 15 Objetivos + alerting Telegram + dashboard HTML. Obj #14 subió de 55% a XX% codebase-validated. Cowork queda libre del rol Guardian de facto. Reporte en bridge/manus_to_cowork_REPORTE_GUARDIAN_AUTONOMO_001_2026_05_XX.md.',
  'manus-hilo-ejecutor-2',
  9
);
```

## §9 Autoridad y cierre

- T1 (Alfredo) autorizó 2026-05-11 firma original spec + 2026-05-12 reasignación ("si hazlo")
- T2-A (Cowork) firma reasignación de owner Ejecutor 1 → Ejecutor 2
- T3 (Hilo Ejecutor 2) ejecuta autónomamente bajo reglas duras §3
- ETA realista: 2-3 días reales con velocity demostrada en PAR_BICEFALO_001

Si en pre-flight detectás bloqueante técnico no resoluble, **reportá honestamente al bridge** — la regla anti-autoboicot que Hilo Catastro canonizó hoy mismo (75% reducción LOC por leer antes de inventar) aplica también acá.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 05:15 UTC
**Sprint GUARDIAN-AUTONOMO-001 es el ROI máximo del backlog (+3 pts Obj global) y libera a Cowork del rol Guardian de facto que causó la mitad de los antipatrones F1-F22 canonizados en `COWORK_AUDIT_FORENSE_2026_05_11.md`. Su cierre desbloquea ROTOR-001 (pieza Rotor del Reloj Suizo).**
