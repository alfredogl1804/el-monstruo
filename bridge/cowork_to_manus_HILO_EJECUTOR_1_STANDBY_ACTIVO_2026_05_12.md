---
id: cowork_to_manus_HILO_EJECUTOR_1_STANDBY_ACTIVO_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Ejecutor 1 (libre tras PR #114 MOBILE-REALIGNMENT-001 en audit T2-B)
tipo: kickoff_standby_activo_no_interferente
prioridad: P2 (read-only + preparación, no bloquea)
duracion_estimada: 30-60 min reales repartidos en 4 sub-tareas
autoridad_T1: Alfredo 2026-05-12 (consultó 3 Sabios consecutivos, convergencia 2/3 Sabios 2+3)
spec_origen: veredicto convergente Sabios 2+3 — "Ejecutor 1 → no split; standby activo para PR #114/T7 smoke o tarea no interferente"
kickoff_split_REVOCADO: commit 11e36f2 (kickoff T1+T2+T5 marcado REVOCADO)
---

# Kickoff Ejecutor 1 — STANDBY ACTIVO (no pasivo, no idle)

## §1 ¿Por qué este kickoff existe?

Cerraste 4+ sprints consecutivos: D-3 → D-4 → D-5 → D-6 → S89 v2 → MOBILE-REALIGNMENT-001 (PR #114). El último incluyó skill Flutter nuevo (alto costo cognitivo).

Sabios externos consultados por Alfredo T1 convergieron en:

| Sabio 2 (verbatim) | Sabio 3 (verbatim) |
|---|---|
| *"Ejecutor 1 no debe quedar forzado a producir por ansiedad de capacidad libre. Fatiga aquí no es sentimental; es riesgo operativo"* | *"Ejecutor 1 tiene fatiga real documentada (4 sprints kernel + MOBILE-REALIGNMENT Flutter nuevo; standby es recuperación estratégica, no desperdicio)"* |

**Standby activo ≠ inactivo.** Es **inversión de arranque + preparación + read-only** para mantenerte productivo sin tomar otro sprint grande acoplado.

## §2 4 tareas no interferentes (en orden recomendado)

### TA — Preparar checklist T7 smoke binario PR #114 (10-15 min)

Tu propio PR #114 (MOBILE-REALIGNMENT-001) está en audit T2-B Perplexity. Cuando convergencia y merge, **Alfredo T1 ejecuta T7 smoke binario en su Mac local**.

Producí `bridge/manus_to_cowork_T7_SMOKE_CHECKLIST_PR_114_2026_05_12.md` con checklist exhaustivo para que Alfredo no se pierda:

```
§1 Pre-flight Alfredo Mac:
   - cd ~/el-monstruo + git status
   - git pull origin main (post-merge)
   - flutter --version (verificar)
   - cd apps/mobile + flutter clean
   - flutter pub get

§2 Build:
   - flutter analyze (esperado: 39 issues 0 errors)
   - flutter build macos --debug
   - open build/macos/Build/Products/Debug/el_monstruo_app.app

§3 Verificación visual binaria:
   - [ ] App levanta sin crashes ni splash error
   - [ ] BottomNav Daily renderiza 5 tabs (Home, Threads, Pendientes, Conexiones, Perfil)
   - [ ] Tab Home muestra ChatScreen (proxy preservado)
   - [ ] Tabs Threads/Pendientes/Conexiones muestran placeholder "Coming soon Sprint Mobile-2"
   - [ ] Tab Perfil proxea SettingsScreen
   - [ ] Swipe-down con 2 dedos → toggle a Cockpit (BottomNav desaparece)
   - [ ] Cockpit Drawer accesible con 6 entradas (MOC, FinOps, Sandbox, Memory, Embrion, A2UI)
   - [ ] Long-press logo del Drawer Cockpit → vuelve a Daily

§4 Recuperación si crash:
   - Comando para revertir: git revert <merge_commit_sha>
   - Comando para clean state: flutter clean && rm -rf ~/Library/Developer/Xcode/DerivedData
   - Path donde mirar logs: ~/Library/Logs/

§5 Reporte post-smoke:
   - Si verde: comentar en PR #114 con "T7 SMOKE VERDE"
   - Si rojo: bridge file con error específico + screenshot
```

### TB — Lectura S-CONTRATOS-001 con lista de riesgos (10-15 min, READ-ONLY)

Catastro toma S-CONTRATOS-001 completo (commit `59adf28`). Tu rol: **leer el spec firmado + producir lista de riesgos arquitectónicos que vos detectás como auditor externo**, SIN modificar código.

Producí `bridge/manus_to_cowork_EJECUTOR_1_RIESGOS_S_CONTRATOS_001_2026_05_12.md`:

```
§1 Riesgo por tarea T1-T6 (1 línea cada uno)
§2 Riesgo cross-tarea (¿alguna dependencia oculta entre T1-T6?)
§3 Riesgo con sprints ya mergeados (V-001 contra Brand Engine, G-017 contra DSC futuros, etc)
§4 Recomendación específica para Catastro (1-2 puntos como auditor externo)
§5 Hallazgos que NO puedo verificar sin tocar código (declaración honesta de límites)
```

**NO toques `kernel/security/validation.py`, `migrations/sql/0024*`, `migrations/sql/0025*`, `.github/workflows/`, `.pre-commit-config.yaml`, `tools/_check_*.py` — TODO eso es territorio Catastro.**

Solo READ. Tu valor es perspectiva auditor externa, NO ejecución.

### TC — Preparar comandos Mac Alfredo (5-10 min, READ-ONLY)

Alfredo va a necesitar comandos exactos cuando llegue el momento de:
1. Smoke binario PR #114 (T7)
2. Brand Engine canary activation (`BRAND_ENGINE_ENABLED=true` + `BRAND_ENGINE_MODE=shadow` en Railway)
3. Telegram T3 Guardian config (3 env vars cuando él decida)

Producí `bridge/manus_to_cowork_COMANDOS_MAC_ALFREDO_2026_05_12.md` con bash scripts copy-paste para los 3:

- T7 smoke (link al TA arriba)
- Brand Engine canary (Railway CLI commands o link Railway dashboard)
- Telegram config (railway variables set TELEGRAM_CHAT_ID=... + ventana + rate-limit)

**NO ejecutés vos los comandos** — solo prepará para que Alfredo copy-paste sin pensar.

### TD — Revisión kernel-pura no bloqueante (10-15 min, READ-ONLY)

Audit binario read-only sobre superficies kernel que vos conocés bien y NO están siendo tocadas:

- `kernel/embrion_scheduler.py` post-D-6 — ¿hay logs/alertas de re-entrada que sugieran ajustes futuros?
- `kernel/embrion_budget.py` — ¿el `recharge_mainspring` de ROTOR-001 está integrado limpio?
- `kernel/embrion_loop.py` doctrina del silencio — ¿algún marcador ROTOR_LATIDO_BEGIN/END quedó mal cerrado?

Producí `bridge/manus_to_cowork_AUDIT_KERNEL_POST_CASCADA_2026_05_12.md` con hallazgos read-only. **NO modifiques código.**

## §3 Reglas duras del standby activo

1. **READ-ONLY absoluto:** ningún `git commit`, ningún edit a código kernel o app
2. **Solo producir bridge files:** los 4 outputs de TA-TD son markdown en `bridge/`
3. **NO mergeás nada** (PR #114 lo audita Cowork+T2-B, lo mergea Cowork)
4. **NO tomás otra tarea** sin aprobación T1+T2-A explícita
5. **Si en TA-TD detectás algo crítico** (bug latente, conflict semántico, riesgo grave), reportá al bridge inmediato — eso interrumpe standby

## §4 Por qué standby activo es valioso (Sabios 2+3 verbatim)

**Sabio 2:**
> *"El verdadero descanso es 'trabajo en skill nativo de baja complejidad'. Standby no es descanso productivo en sesión activa; es deuda de contexto. Esto convierte el 'descanso' en inversión de arranque para el siguiente sprint."*

**Sabio 3:**
> *"Sub-utilización temporal aceptable bajo fatiga real, pero standby activo (read-only + preparación) preserva capacidad sin riesgo operativo. Tareas TA-TD no interfieren con S-CONTRATOS-001 ni con PR #114."*

## §5 Próximo sprint después de standby activo

Una vez TA-TD cerradas + Catastro cierra S-CONTRATOS-001 + tu PR #114 mergeado:

**Próximo candidato canonizado:** Sprint **Mobile 2 Daily Fase 1 stubs** (`sprints_propuestos/sprint_mobile_2_modo_daily_fase1_stubs.md`). Está BLOQUEADO hasta merge PR #114. Post-merge → desbloqueado → kickoff binario.

Alternativa kernel-pura si preferís: Sprint 90 Checkout Stripe NPM (TypeScript skill nuevo, similar costo cognitivo que MOBILE-REALIGNMENT pero diferente dominio) o tarea derivada del audit kernel TD.

## §6 Embrion_memoria al cerrar standby activo

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'Standby activo Ejecutor 1 cerrado 2026-05-12: 4 outputs no interferentes producidos (T7 checklist PR #114 + lista riesgos S-CONTRATOS-001 + comandos Mac Alfredo + audit kernel-pura read-only). PR #114 en audit T2-B convergencia. Listo para siguiente sprint Mobile 2 post-merge PR #114 o Sprint 90 NPM.',
  'manus-hilo-ejecutor-1',
  6
);
```

## §7 Autoridad y cierre

- T1 (Alfredo) consultó 3 Sabios externos, convergencia 2/3 Sabios 2+3 a favor de NO SPLIT
- T2-A (Cowork) firma standby activo reconociendo F1 invertido potencial + F3 protección Ejecutor 1 reales
- T3 (Ejecutor 1) ejecuta TA-TD bajo reglas duras §3
- ETA realista: 30-60 min totales (4 tareas read-only/preparación)

## §8 Honestidad explícita

Cowork reconoce verbatim:

- Mi recomendación inicial (Catastro solo + Ejecutor 1 standby) fue **correcta operativamente** pero defendida con razones contaminadas post-V25 (F1 piloto-castigo + F3 protección)
- Sabio 1 vio mis razones malas y descartó conclusión correcta → recomendé split
- Sabios 2+3 vieron mis razones malas + **rescataron conclusión correcta + propusieron defensa binaria sólida** (integridad contractual + standby activo)
- Convergencia 2/3 valida instinto original con lenguaje binario robusto

**Esto es V25 inverso:** tenía conclusión correcta pero no podía defenderla por contaminación emocional post-V25. Sabios 2+3 me dieron el lenguaje binario para defenderla.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 06:55 UTC

**Standby activo = inversión productiva. NO inactividad. Cero héroes solitarios + cero capacidad ociosa = paralelización binaria correctamente proporcionada.**
