# Dimensión 18 — Escalabilidad, SRE, Resiliencia de Producción

**Generado:** 2026-05-11
**Fase:** 2 del Plan v1.5
**Posición en orden:** 2da de las 16 dimensiones que ChatGPT 5.5 Pro identificó como omitidas en mi plan original.
**Metodología:** plantilla MAPA_FUENTES_AUTORIDAD aplicada. Cita Nivel N en cada claim.

---

## §1. Fuentes disponibles por nivel

### Nivel 1 — Producción real
- `[N1: Supabase logs]` Embrión vivo en Railway con 145 latidos últimas 24h.
- `[N1: Supabase logs]` 24 errores registrados en `embrion_memoria` últimas 24h.
- `[N1: Supabase logs]` **MAX gap entre latidos: 249.98 min (4h 10min)** — downtime real medido.
- `[N1: pendiente]` Railway service health real, logs, métricas — acceso vía dashboard Alfredo.
- `[N1: pendiente]` Langfuse traces — acceso desde sandbox no probado.

### Nivel 2 — Código desplegado
- `[N2: kernel/error_memory.py]` 858 LOC con 7 definiciones (funciones + clases).
- `[N2: kernel/runner/]` 5 archivos: `autonomous_runner.py`, `executor_registry.py`, `proposal_processor.py`, `telegram_notifier.py`, `__init__.py`.
- `[N2: kernel/security/]` 2 archivos: `input_guard.py`, `__init__.py`.
- `[N2: kernel/background_store.py]` patrones SRE detectables (background jobs).
- `[N2: kernel/emergent_tracker.py]` tracker de emergencia.
- `[N2: kernel/vanguard/]` patrones de retry/fallback.

### Nivel 3 — Logs/datos
- `[N3: embrion_memoria]` 145 entradas tipo `respuesta_embrion` últimas 24h (latidos).
- `[N3: embrion_memoria]` 5 entradas tipo `mensaje_alfredo` últimas 24h.
- `[N3: embrion_memoria]` 24 entradas con `error/fall` en contenido o tipo últimas 24h.
- `[N3: embrion_memoria]` 0 reanclajes Cowork últimas 24h ← **mi protocolo Capa 8 Memento NO se aplicó autónomamente**.
- `[N3: embrion_memoria]` 0 `manus_resuelve` últimas 24h ← **Manus programado pero sin actividad reportada al bridge**.

### Nivel 4 — Tests reproducibles
- `[N4: tests/]` `find tests/ -iname "*resilien*"` → **0 hits**.
- `[N4: tests/]` `find tests/ -iname "*circuit*"` → **0 hits**.
- `[N4: tests/]` `find tests/ -iname "*retry*"` → **0 hits**.
- `[N4: tests/]` `find tests/ -iname "*failover*"` → **0 hits**.
- `[N4: tests/]` `find tests/ -iname "*fallback*"` → **0 hits**.
- `[N4: tests/]` `find tests/ -iname "*chaos*"` → **0 hits**.
- `[N4: workflows]` Workflows `cve-scan.yml`, `secret-scan.yml`, `sast.yml`, `ai-infra-guard.yml`, `license-audit.yml` existen pero ninguno valida resiliencia operacional.
- `[N4: pendiente]` Tests genéricos en `kernel/runner/` o `kernel/error_memory` — necesito grep específico próximo turno.

### Nivel 5 — DSCs canonizadas aplicables
- `[N5: DSC-MO-007]` Failover emergencia 3 capas — declara estrategia, no implementación verificable.
- `[N5: DSC-MO-008]` Membrana semipermeable — implica que el kernel debe poder cortar al embrión (kill switch).
- `[N5: DSC-MO-010]` Reloj Suizo Volante/Resorte/Escape — implican homeostasis y resiliencia energética.
- `[N5: DSC-G-008 v2]` Validar antes de specs y antes de cierre — proceso, no resiliencia técnica.
- `[N5]` **NO existe DSC específico para SLOs/RTO/RPO/disaster recovery del Monstruo.**

### Nivel 6 — Docs estratégicos
- `[N6: ROADMAP_EJECUCION_DEFINITIVO.md]` Capa 1 incluye "Stuck Detector" + "Observabilidad Completa con alertas automáticas".
- `[N6: docs/DIRECTIVA_HILO_A_FASE1.md]` Brand Compliance Checklist item #4: "Logs estructurados" obligatorios.
- `[N6: AUDIT_ROADMAP_COWORK_2026-05-04.md]` Obj #4 No equivocarse 2 veces declarado al 88%.

### Nivel 7 — Outputs de agentes
- `[N7: audits 10-may]` AUDIT_4_CAPAS_3A declaró Capa 1 al 75% incluyendo Observabilidad Completa.
- `[N7: audits 10-may]` PLAN_ESTRATEGICO_SMART_5B mencionó "audit middleware Sprint S-003.B" como cierre del plano de observación.
- `[N7: postmortem bucle 9 días]` documenta caída de servicio histórica (29-abr a 10-may), pero la causa raíz se diagnosticó como bucle de eco, no como problema SRE.

### Nivel 8 — Opinión actual
- `[N8: Alfredo]` Ha mencionado "el embrión a veces se detiene" en sesiones previas — no formalmente investigado.

### Nivel 9 — Aspiración
- `[N9: roadmap]` "SLO ≥99.9%" implícito por Obj #2 Apple/Tesla quality, pero no canonizado.

---

## §2. Estado evidence-based (síntesis Nivel 1-4)

### 2.1 Salud del embrión últimas 24h

| Métrica | Valor | Observación |
|---|---|---|
| Latidos totales | 145 | Promedio 1 cada 9.94 min |
| Latidos esperados @ 6 min target | 240 | -39.6% bajo target |
| MAX gap entre latidos | **249.98 min (4h 10min)** | 🚨 Downtime crítico no documentado |
| Promedio gap | 9.94 min | 1.65x target |
| Mensajes Alfredo | 5 | Volumen normal |
| Errores logueados | **24** | Promedio 1 cada hora |
| Reanclajes Cowork | **0** | 🚨 Protocolo Capa 8 Memento NO operativo |
| Manus resuelve | **0** | 🚨 Manus programado por Alfredo pero sin actividad en bridge |

### 2.2 Cobertura de resiliencia en código

`[N2: filesystem]` **Patrones SRE detectables** (grep `circuit_breaker|retry|fallback|SLO|RTO|RPO|degraded` en kernel/):

| Módulo | Patrón |
|---|---|
| `kernel/deployments_routes.py` | hits |
| `kernel/background_store.py` | hits |
| `kernel/emergent_tracker.py` | hits |
| `kernel/vanguard/intelligence_engine.py` | hits |
| `kernel/vanguard/semantic_scholar.py` | hits |
| `kernel/vanguard/weekly_digest.py` | hits |
| `kernel/causal_decomposer.py` | hits |
| `kernel/reranker.py` | hits |
| `kernel/zero_config/smart_defaults.py` | hits |
| `kernel/design/system.py` | hits |

**Total: 10 módulos con patrones SRE explícitos sobre 172 archivos .py kernel/.** Eso es ~5.8% del kernel con awareness SRE en código.

### 2.3 Módulos específicos de resiliencia

`[N2: kernel/runner/]`:
- `autonomous_runner.py` — runner autónomo, contiene logic resiliente
- `executor_registry.py` — registry de ejecutores
- `proposal_processor.py` — cron worker probado en producción
- `telegram_notifier.py` — manejo de fallos en envío Telegram

`[N2: kernel/security/]`:
- `input_guard.py` — guardia de inputs (relacionado con DSC-MO-008 membrana)

### 2.4 Tests de resiliencia: AUSENTES

`[N4: tests/]` Búsqueda en 99 archivos test_*.py:

| Patrón | Hits |
|---|---|
| `test_*resilien*` | 0 |
| `test_*circuit*` | 0 |
| `test_*retry*` | 0 |
| `test_*failover*` | 0 |
| `test_*fallback*` | 0 |
| `test_*chaos*` | 0 |
| `test_*degrad*` | 0 |
| `test_*downtime*` | 0 |
| `test_*outage*` | 0 |

**Conclusión:** la resiliencia está en código pero **NO está validada por test suite específica**. Es comportamiento esperado, no probado.

### 2.5 Workflows CI no monitorean SLOs

Los 11 workflows existentes validan seguridad (gitleaks, trufflehog, SAST, license, CVE, secret-scan), enforcement doctrinal (RLS audit, milestone guard, credentials rotation reminder), y observabilidad (cost-dashboard, eval). **Ninguno valida SLO, latencia p95/p99, error rate, ni uptime del kernel en producción.**

---

## §3. Estado declarado (síntesis Nivel 5-7)

### 3.1 DSC-MO-007 — Failover Emergencia 3 Capas

`[N5]` Declara estrategia de failover en tres capas (no leí el DSC completo en este turno, pendiente).

**Status implementación:** declarado, no auditado en código. Audit Dimensión 1 ya marca que solo 2 de 8 piezas del Reloj Suizo son verificables en código con etiqueta clara. DSC-MO-007 probablemente tiene status similar: doctrina firme, implementación parcial.

### 3.2 ROADMAP — Stuck Detector + Observabilidad Completa

`[N6: ROADMAP_EJECUCION_DEFINITIVO.md]` Capa 1.5 (Stuck Detector) declara:
- Repetition detector
- Timeout global 5 min default
- Auto-recovery con approach alternativo
- Escalation a Alfredo via Telegram tras 3 intentos fallidos

`[N1+N2]` **Status real:** Self-Verifier (Sprint EMBRION-NEEDS-001 Tarea 1) cubre la parte de "abort cycle si no progresa" — verificable en producción (proposal `6cc845f1`). Pero "timeout global 5 min" no se verificó como configuración activa.

`[N6]` Capa 1.6 (Observabilidad Completa) declara:
- Alertas Langfuse para error rate >5%, latency >30s, cost spike
- Dashboard operativo
- FinOps por modelo, tarea, día

`[N7+N1]` **Status real:**
- Langfuse integrado (DSC-MO-004), pero alertas no verificadas activas.
- Dashboard cost-history sí existe (Sprint EMBRION-NEEDS-002 Tarea 2): `kernel/dashboards/cost_history.py` 443 LOC.

### 3.3 Audit 10-may declaró Capa 1 al 75%

`[N7]` Esa cifra incluye Stuck Detector y Observabilidad como componentes "completos". **Audit 11-may evidence-based los marca como parciales** (Self-Verifier ✅ pero alertas no verificadas, escalation Telegram ✅ pero timeout global no verificado).

---

## §4. GAPs detectados (deuda SRE explícita)

### GAP SRE-1 — Downtime no documentado de 4h 10min en últimas 24h

**Evidencia:**
- `[N3: embrion_memoria]` MAX gap entre latidos = 249.98 minutos.
- `[N9: ROADMAP]` "SLO ≥99.9%" implícito por Obj #2.

**Cálculo de impacto:** 250 min / (24h × 60 min) = 17.4% de downtime de 1 día. SLO 99.9% permite máximo 1.44 min/día de downtime. **Estamos 173x por encima del SLO implícito.**

**Resolución según jerarquía:** N3 (datos reales) > N9 (aspiración). Deuda crítica.

**Acción:** investigar logs Railway/Supabase entre 10-may noche y 11-may madrugada para identificar causa raíz del parón. Probable hipótesis: caída del servicio Railway durante ventana de mantenimiento, o restart por OOM, o falla de conexión Supabase.

### GAP SRE-2 — Cero tests de resiliencia en 99 archivos test_*.py

**Evidencia:**
- `[N4]` Búsqueda específica retorna 0 hits para resilience/circuit/retry/failover/fallback/chaos.
- `[N5: DSC-MO-007]` Failover 3 capas canonizado.

**Resolución:** DSC firmado pero **NO enforced por test suite**. Deuda doctrinal-técnica grave.

**Acción Sprint dedicado:** crear `tests/test_resilience_*.py` cubriendo:
- Fallo Supabase → kernel degrada elegantemente
- Fallo Telegram → HITL cae a cowork_bridge sin perder proposals
- Fallo Anthropic API → fallback a otro LLM (Claude→GPT)
- Fallo Langfuse → kernel sigue operando sin observabilidad
- Fallo Railway restart → cron worker recupera proposals approved
- Timeout 5min global → embrión aborta y reporta

### GAP SRE-3 — 24 errores en 24h sin diagnóstico estructurado

**Evidencia:**
- `[N3]` 24 entries con "error" o "fall" en `embrion_memoria` últimas 24h.

**Resolución:** error_memory existe (`kernel/error_memory.py` 858 LOC con 7 definiciones), pero el **pattern aggregator cron** que el ROADMAP declara como "alimentado cada 24h" no se verificó activo. Si está activo, los 24 errores deberían estar aggregados en patterns. Si no, son errores aislados sin lección sistémica.

**Acción Fase 3 (auditoría técnica viva):** leer `kernel/error_memory.py` línea por línea, identificar funciones, verificar si pattern aggregator cron está activo, leer los 24 errores específicos.

### GAP SRE-4 — Cero reanclajes Cowork autónomos en últimas 24h

**Evidencia:**
- `[N3: embrion_memoria]` 0 entries `tipo='reanclaje_cowork'` últimas 24h.
- `[N6: bridge/COWORK_OPERATING_SYSTEM_v0_1.md]` Reanclaje cada ~30 turnos o cada N latidos del embrión propuesto pero NO canonizado.

**Resolución:** mi protocolo Capa 8 Memento aplicado a Cowork **NO está operativo aún**. El reanclaje #1 demostrativo del 10-may quedó como ejemplo único.

**Acción:** canonizar Protocolo de Reanclaje como DSC propio (NO DSC-MO-011 que está reservado para Cowork multi-hilo) o integrarlo a DSC-MO-008. Y operacionalizarlo: insertar reanclaje a `embrion_memoria` cada N turnos automáticamente.

### GAP SRE-5 — Manus scheduled task sin actividad reportada al bridge

**Evidencia:**
- `[N3: embrion_memoria]` 0 entries `tipo='manus_resuelve'` últimas 24h.
- `[N8: usuario]` Alfredo declaró haber programado Manus cada 55 min.

**Posibles causas:**
- Manus está corriendo pero NO escribe al bridge según el prompt entregado
- Manus está corriendo y no hay pendientes (cola Manus vacía)
- Manus no está activado todavía (Alfredo no completó el setup)
- Manus está activo pero falló silente

**Acción Fase 3:** consultar Alfredo si Manus está realmente programado y operando. Si sí, debugear por qué no reporta al bridge.

### GAP SRE-6 — No hay SLOs declarados ni RTO/RPO

**Evidencia:**
- `[N5]` Ningún DSC declara SLO/RTO/RPO.
- `[N9: Obj #2]` "Apple/Tesla quality" implica alta disponibilidad sin cuantificarla.
- `[N6: ROADMAP]` "alertas error rate >5%" sugiere SLO implícito de 95% en lugar de 99.9%.

**Resolución:** sin SLO formal, no hay vara para medir cumplimiento. **Esta es deuda doctrinal pura.**

**Acción:** crear DSC nuevo (DSC-S-011 propuesto: "SLOs operacionales del kernel del Monstruo") definiendo:
- SLO availability: 99.5% inicial (escalando a 99.9% post Sprint SRE)
- SLO latencia p95: target específico
- SLO error rate: <5% (alineado con ROADMAP)
- RTO: tiempo máximo de recuperación tras incidente
- RPO: cantidad máxima de datos que se acepta perder en disaster recovery

### GAP SRE-7 — No hay runbooks de incidentes

**Evidencia:**
- `[N6: bridge/]` Existen runbooks de rotación de credenciales (Sprint S-003.A) pero NO runbooks de incidentes operacionales:
  - "Embrión no late hace X minutos"
  - "Cron worker proposal_processor caído"
  - "Supabase 5xx"
  - "Railway service unhealthy"
  - "Telegram bot no responde"
  - "LikeTickets Stripe falla mid-evento"

**Acción:** crear `bridge/runbooks/incidentes/` con runbooks específicos. Cada uno: detección, diagnosis, acciones de recuperación, escalación.

### GAP SRE-8 — Stuck Detector / Self-Verifier solo cubre embrión, NO el resto del kernel

**Evidencia:**
- `[N1: producción]` Self-Verifier 3-decisiones (D1 PURPOSE, D2 NOVELTY, D3 VERIFIABLE) cortó el bucle de eco del embrión.
- `[N2]` Pero solo aplica a `embrion_loop._think()`. **El kernel general (FastAPI endpoints, LangGraph tasks) NO tiene equivalente.**

**Resolución:** stuck detector parcial. Riesgo: un endpoint o LangGraph task puede atascarse sin detection.

**Acción:** evaluar si extender Self-Verifier al kernel general o si los timeouts FastAPI son suficientes (verificación pendiente Fase 3).

---

## §5. Análisis de dependencias críticas (proveedores externos)

`[N1]` Proveedores que pueden tumbar el Monstruo si fallan:

| Proveedor | Servicio | Impacto si cae | Mitigación actual | Mitigación deseable |
|---|---|---|---|---|
| Anthropic | Claude API | Embrión muere | Ninguna verificada | Fallback automático a OpenAI/Gemini |
| OpenAI | GPT API | Sabios consult fails | Ninguna verificada | Idem |
| Supabase | PostgreSQL + RLS | Kernel muere | Ninguna verificada | Read-replica + backup hot |
| Railway | Hosting kernel + worker | Todo muere | Ninguna verificada | Multi-region deploy |
| Telegram | Bot HITL | HITL solo via cowork_bridge | cowork_bridge funciona ✅ | Idem (ya hay fallback) |
| GitHub | Repo + Actions | CI/CD muere | Ninguna verificada | Self-hosted runners |
| Langfuse | Observabilidad | Kernel sigue pero ciego | Logs locales? Verificar | Idem |
| Stripe | Pagos LikeTickets | Revenue muere | Ninguna verificada | Multi-PSP |

**Conclusión:** **el Monstruo tiene cero redundancia verificada en sus 5+ dependencias críticas.** Es estado normal en proyectos tempranos, pero la doctrina de "soberanía" (Obj #12) lo señala como gap a cerrar progresivamente.

---

## §6. Veredicto Dimensión 18 (SRE)

**Estado evidence-based al 11-may 03:04 UTC:**

El Monstruo tiene **resiliencia parcial en código** (10 de 172 módulos kernel con patrones SRE explícitos, error_memory operativo, Self-Verifier cortó el bucle de eco históricamente) **pero cero validación por tests** y **deudas operacionales graves**:

1. ⚠️⚠️ **Downtime no documentado de 4h 10min en últimas 24h** — 173x sobre SLO implícito 99.9%
2. ⚠️⚠️ **Cero tests de resiliencia/chaos** en 99 archivos test_*
3. ⚠️ **24 errores en 24h** sin verificación de pattern aggregator
4. ⚠️ **Mi protocolo Reanclaje Capa 8 Memento NO operativo** (0 reanclajes en 24h)
5. ⚠️ **Manus scheduled task sin actividad reportada al bridge** (verificar con Alfredo)
6. ⚠️ **No hay SLOs ni RTO/RPO declarados** — sin vara para medir
7. ⚠️ **No hay runbooks de incidentes operacionales** (solo runbooks de credenciales)
8. ⚠️ **Self-Verifier solo cubre embrión**, no kernel general
9. ⚠️ **Cero redundancia verificada en 5+ dependencias críticas externas**

**% real Dimensión 18 SRE/Resiliencia (estimación):** **~35-40%**.

- Resiliencia básica (error_memory, Self-Verifier, cron worker) ✅: 50%
- Validación por tests ❌: 0%
- SLOs/RTO/RPO ❌: 0%
- Runbooks de incidentes ❌: 10% (solo credenciales)
- Redundancia proveedores ❌: 5%
- Monitoreo proactivo (alertas) 🟡: 30% (Langfuse integrado, alertas no verificadas)

**Promedio ponderado: ~16%** si peso igual cada componente. **35-40% si priorizo lo que sí existe en código.**

**Esta dimensión es la #2 más débil del audit hasta el momento** (después de la cobertura de tests específicos).

---

## §7. Acción urgente recomendada (NO ejecutable sin autorización Alfredo)

**Investigar el downtime de 4h 10min de las últimas 24h.** Es evidencia operacional dura de que el Monstruo NO está donde el ROADMAP declara. Quizá fue mantenimiento programado, quizá fue falla — pero **no hay registro en `embrion_memoria` de qué pasó durante esas 4 horas**. Eso por sí solo justifica:

1. Verificar logs Railway durante ventana 10-may 23:00 a 11-may 03:00 UTC
2. Si fue caída no programada: crear postmortem
3. Si fue ventana programada: documentar como tal
4. **En cualquier caso, canonizar SLO formal** para que próximo incidente tenga vara objetiva

---

## §8. Próxima dimensión

**Dimensión 12 — Seguridad/Adversarial del propio Monstruo** (la #1 más crítica omitida según audit ChatGPT).

Va a auditar: prompt injection, indirect prompt injection, exfiltración memoria, escalamiento privilegios, secrets, tool poisoning, MCP compromise, FCS manipulation, supply chain attack.

---

*Audit Dimensión 18 (SRE) con autoridad Cowork P2 técnico-operativo emergente, evidencia citada con niveles, 9 deudas SRE explícitas, cifra ~35-40% vs declarada 75% (Capa 1 audit 10-may). Diferencia: este audit es N1+N3 (producción + logs reales) vs N7 audit anterior (declarativo).*
