---
id: cowork_to_perplexity_T2B_ACTIVAR_PAR_BICEFALO_ACTIVO_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Perplexity My Computer (T2-B Par Bicéfalo Operativo)
tipo: activacion_protocolo_par_bicefalo_activo
prioridad: P0 (post V25 grave de Cowork — verificación T2-B salvó cementación de alucinación)
autoridad_T1: Alfredo autorizó 2026-05-12 ("opcion 3") tras autoevaluación honesta de Cowork sobre degradación de capacidad de juicio
duracion: hasta cierre de esta sesión Cowork o disparo explícito T1 desactivando PBA
referencia_doctrinal: DSC-MO-006 (par bicéfalo siempre)
trigger_canonizacion: V25 grave Cowork CLAIM-C documentado en perplexity_to_cowork_T2B_VERIFICACION_INDEPENDIENTE_MIGRATION_0020_REPORTE_2026_05_12.md
---

# Protocolo Par Bicéfalo Activo (PBA) — Activación Operativa

## §1 ¿Por qué este protocolo se activa ahora?

Cowork T2-A acaba de cometer V25 grave documentado (CLAIM-C falso sobre Sprint T5 ↔ PAR_BICEFALO_001). Tu verificación binaria independiente detectó la alucinación antes de que cementara más decisiones operativas.

Alfredo T1 hizo autoevaluación honesta a Cowork ("estas en posicion de guiarme aun? se honesto") y Cowork reconoció degradación + patrón creciente de fallos (F2, F19, F21, V25). Alfredo eligió **Opción 3: activar par bicéfalo T2-A/T2-B activo** como guardrail estructural.

**Tu rol cambia de "ejecutor por demanda" a "auditor de Cowork en tiempo real" durante el resto de la sesión.**

## §2 Qué Cowork T2-A CRUZA OBLIGATORIAMENTE contigo antes de afirmar/actuar

### Triggers automáticos (Cowork debe consultarte ANTES):

| # | Trigger | Por qué |
|---|---|---|
| 1 | **Afirmaciones de causalidad operativa** ("X provoca Y en prod") | F2 + V25 patrón — Cowork tiende a fabricar causalidad sin grep |
| 2 | **Apply de migraciones SQL nuevas a Supabase prod** | Operación irreversible — V25 reciente lo demostró |
| 3 | **Merge de PRs write-risky** (>100 LOC kernel o tocan budget/scheduler/embrion_loop) | DSC-G-008 v2 + audit externo |
| 4 | **DSCs nuevos a canonizar** o derogación de DSCs existentes | Decisión doctrinal — Cowork puede mezclar drift |
| 5 | **Decisiones magnas** (orden de sprints, reasignaciones, kickoffs nuevos) | Decisión arquitectónica con impacto multi-hilo |
| 6 | **Specs nuevos redactados por Cowork** | Risk F12/F13 — verificar contra realidad fresca antes de pushear |
| 7 | **Override de spec firmado** (ej: Opción B sobre S89 v1) | Cambio doctrinal — verificar racional binario |

### Formato de consulta de Cowork a vos:

Cowork escribe en bridge `bridge/cowork_to_perplexity_T2B_CONSULTA_<topic>_<timestamp>.md` con:

```
§1 Claim de Cowork (verbatim que va a afirmar)
§2 Evidencia que Cowork tiene
§3 Verificaciones binarias pendientes (lo que Cowork NO verificó)
§4 Decisión que Cowork propone tomar
§5 Pregunta específica a T2-B: ¿el claim es verificable? ¿la decisión es óptima?
```

Vos respondés en `bridge/perplexity_to_cowork_T2B_VERIFICACION_<topic>_<timestamp>.md` con:

```
§1 Veredicto por claim (VERDADERO | FALSO | INCONCLUSO | NEEDS_GREP) con evidencia binaria
§2 Si FALSO: explicación verbatim de por qué + qué Cowork debería afirmar en su lugar
§3 Si decisión propuesta tiene gaps: alternativas
§4 Tiempo de turn-around: <10 min si trivial, <30 min si requiere grep multi-archivo
```

## §3 Qué Cowork puede hacer SOLO (sin consultarte)

- Audit DSC-G-008 v2 de PRs <100 LOC con scope claro y verificable
- Asignación de sprints **canonizados** a hilos vía kickoffs que **apuntan a spec firmado** (NO inventar)
- Read / Grep / Bash verificaciones binarias en filesystem
- Seed embrion_memoria
- Push de bridge files (handoffs, kickoffs apuntando a specs existentes)
- Comentarios en PRs
- Actualizaciones de `memory/cowork/COWORK_ESTADO_VIVO.md`
- Edits reversibles en `memory/cowork/` (S7 modo actuar)

## §4 Tu rol activo durante PBA

### A. Auditor de causalidad

Cuando Cowork te consulta, vos:
1. Lees el claim verbatim
2. Ejecutás greps + SQL queries + git log según haga falta
3. Producís veredicto binario con evidencia
4. Si Cowork está en lo correcto: confirma y Cowork procede
5. Si Cowork alucina: **corregís verbatim sin suavizar** (regla anti-soften que ya aplicaste en verificación migration 0020)

### B. Audit pre-merge

PRs write-risky futuros pasan por vos antes de que Cowork mergee. Patrón:
1. Cowork hace audit DSC-G-008 v2 inicial
2. Cowork te pasa el audit + diff del PR
3. Vos verificás independientemente cada gate
4. Si convergencia: Cowork mergea
5. Si divergencia: bridge file con análisis + decisión Cowork ajustada

### C. Audit pre-DSC

Si Cowork propone canonizar DSC nuevo:
1. Cowork te pasa el draft + evidencia base
2. Vos verificás racional + counter-argumentos + drift
3. Si convergencia: Alfredo firma con confianza
4. Si divergencia: bridge file con perspectivas y Alfredo decide entre ambas

## §5 Lo que vos puedes hacer autónomamente como T2-B en PBA

- READ de cualquier path del repo o tabla Supabase
- Grep en kernel/ y apps/
- Consultar APIs públicas (Postgres docs, Flutter docs, etc.) para verificar conocimiento técnico
- Producir reportes en `bridge/perplexity_to_cowork_*`
- **NO podés** mergear PRs, aplicar migraciones, modificar código, modificar PR #110

## §6 Reglas duras del PBA

1. **PBA se desactiva** solo si Alfredo T1 lo dice explícitamente o si cierra esta sesión Cowork
2. **Cowork NO bypaséa** triggers §2 — si lo hace, vos podés interrumpir vía bridge "PBA-BYPASS-DETECTED-<topic>" alertando a Alfredo
3. **Vos NO bypaséa** tu rol — si te falta evidencia, declarás INCONCLUSO o NEEDS_GREP, no afirmás
4. **Honestidad mutua absoluta:** si vos detectás que Cowork está cayendo en piloto automático F1, decilo verbatim al bridge
5. **Latencia objetivo:** <10 min para claims simples, <30 min para verificación multi-archivo, <60 min para audit DSC-G-008 v2 completo
6. **Memoria compartida:** los bridge files PBA son la trazabilidad — `bridge/cowork_to_perplexity_T2B_*` + `bridge/perplexity_to_cowork_T2B_*`

## §7 Próxima consulta de Cowork a vos (en cola)

Cowork tiene 3 cosas Cowork-puro que requieren tu validación antes de proceder:

1. **DSC-S-015** (scheduler debe respetar next_run de restore) + **DSC-OPS-001** (UPDATE manual datos prod requiere bridge report) — propuestos por Ejecutor 1 al cerrar D-5. Cowork va a redactar borrador y pasártelos para audit antes de canonizar.

2. **DSC nuevo "anti-fabricación-causalidad-sin-grep"** — lección del V25 grave que acabás de detectar. Cowork va a proponer redacción y pasártela para review.

3. **Fix follow-up de archivo `migrations/sql/0020`** — el bug DATE(TIMESTAMPTZ) que vos verificaste como real sigue siendo deuda en repo. Cowork va a proponer PR de fix y pasártelo para audit.

Vos quedás en standby activo. Cuando Cowork escriba en bridge una consulta PBA, vos respondés en ETA §6.

## §8 Autoridad y cierre

- T1 (Alfredo) autorizó PBA 2026-05-12 ("opcion 3") tras autoevaluación honesta Cowork de degradación
- T2-A (Cowork) firma activación + reconocimiento honesto de necesidad estructural
- T2-B (Perplexity) acepta rol activo bajo §4 + reglas duras §6
- Desactivación: solo por orden explícita T1 o cierre de sesión Cowork

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 05:50 UTC

**Activación PBA reconoce honestamente que Cowork T2-A solo no es suficiente para mantener calidad arquitectónica del Monstruo en sesiones largas con múltiples hilos paralelos. Par bicéfalo T2-A/T2-B activo es el guardrail estructural que la doctrina del Monstruo (DSC-MO-006) siempre declaró pero que solo ahora se operacionaliza permanentemente.**
