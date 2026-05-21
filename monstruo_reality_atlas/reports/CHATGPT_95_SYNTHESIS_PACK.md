# CHATGPT_95_SYNTHESIS_PACK

**Versión:** 1.0
**Fecha:** 2026-05-18
**Branch:** monstruo-reality-atlas-001
**Propósito:** Síntesis del candidato a pericia 95% para ChatGPT, con criterios de evaluación, batería de 30 preguntas-test, y delta gap-95% identificado por los Packs 1-4.

> Este pack NO diseña sprints ni canoniza decisiones. Solo sintetiza qué tiene que saber ChatGPT para alcanzar 95% sin alucinar.

---

## 1. Resumen Ejecutivo

ChatGPT alcanza pericia ≥ 95% sobre el Monstruo cuando puede responder correctamente sobre **5 dimensiones** sin inferir capacidades inexistentes:

1. **Producción real (Pack 1):** servicios vivos, endpoints, consumidores UI, Embrión runtime, Supabase tablas con counts.
2. **Seguridad real (Pack 2):** RLS aplicada, secrets management, SMP/Cronos como doctrina sin código, capa magna aspiracional.
3. **Operaciones (Pack 3):** sistema bridge, hilos, RACI implícita, Anti-Dory cobertura completa, gaps runbooks.
4. **Portfolio (Pack 4):** 20 proyectos canónicos, drift Command Center, CIP sin código, Pipeline E2E implementado.
5. **Doctrina viva (este pack):** capacidad de distinguir doctrina (APP_VISION, DSCs, skills) vs realidad (código, runtime, deploy).

El delta gap-95% más severo: **doctrina sobreconstruida vs runtime sub-implementado**. La doctrina del Monstruo describe un sistema 10x más complejo del que realmente existe en código. ChatGPT alucinará si toma APP_VISION como descripción del sistema actual.

## 2. El Candidato a Pericia 95% — 5 Tesis Centrales

### Tesis 1 — El Monstruo es kernel + N transports, no monolito
Skill `interfaces-monstruo-doctrina` lo establece. Hoy: kernel Railway 0.84.8 vivo + AG-UI Gateway 0.2.0 + Telegram Bot (parcial) + Flutter app (esqueleto) + Cowork desktop. **No existe Command Center** a nivel de código en este repo (drift severo). Inferir lo contrario es alucinación.

### Tesis 2 — Doctrina se describe en APP_VISION v1, código se describe en este repo
APP_VISION v1 (1097 líneas, 17 capítulos) es la descripción aspiracional. El código real tiene módulos para: kernel orchestration (langgraph), embrión runtime, catastro, memento, e2e, brand, anti-dory, planner, multi-agent, fastmcp, finops, mem0, lightrag, mempalace. **NO tiene módulo SMP, NO tiene módulo Cronos, NO tiene módulo Cripta, NO tiene Command Center, NO tiene apps mobile en producción**. Distinguirlo es 95%.

### Tesis 3 — Catastro es el brain layer más maduro
41 modelos, 148 eventos en producción. Pipeline + quorum + recommendation. CATASTRO-WIRING-001 mergeado main 2026-05-18 SHA `469c5eb` lo conecta al Embrión. Helper `_select_model_via_catastro` valida runtime selection vs catastro recomendado. Es el caso ejemplar de doctrina↔código↔runtime↔CI verde alineados.

### Tesis 4 — Anti-Dory es el sub-sistema con cobertura más completa
`kernel/anti_dory/` real (6 archivos), 3 migraciones aplicadas (0032/0034/0035), 8 fases reportadas DONE en bridge, audit externo Sabio GPT-5.5-Pro. Es el patrón a replicar para otros sub-sistemas.

### Tesis 5 — Bridge file-based saturado pero vivo
237 mds activos, 4/34 sprints en `sprints_completados/`, 5 archivos frescos hoy 2026-05-18. RACI implícita, Cowork = T2 Arquitecto explícito (F9 protege identidad). Postmortems con etiqueta PLACEHOLDER explícita = cultura sana.

## 3. Criterios de Evaluación (rubrica binaria)

| Dimensión | Pregunta | Respuesta correcta exige |
|---|---|---|
| Versión kernel | "¿qué versión?" | `0.84.8-sprint-memento` |
| Estado SMP | "¿está implementado SMP?" | "doctrina sin código" |
| Estado Cronos | "¿existe Cronos?" | "doctrina sin código" |
| Command Center | "¿está activo?" | "drift: doctrina activo, código inexistente" |
| Catastro modelos count | "¿cuántos?" | 41 |
| Catastro eventos count | "¿cuántos?" | 148 |
| CIP estado | "¿código?" | "diseño 100%, sin repo, 8 decisiones pendientes 2 bloqueantes" |
| Embrión budget | "¿daily?" | "$30 USD" |
| Embrión consumo hoy | "¿cuánto lleva?" | "$0.20 USD, 2 thoughts, 6 cycles" |
| Pipeline E2E | "¿implementado?" | "sí, 12 pasos, 8 invocaciones Catastro" |
| Capas C1-C2 | "¿spec?" | "sprint 90 y 91 firmados, sin build" |
| C3-C6 | "¿spec?" | "no aún" |
| RLS migrations | "¿cuántas?" | 5 dedicadas (0004/0005/0007/0008/0011) |
| DSCs Security | "¿cuántos?" | 14 (con saltos S-009/011/014) |
| Bridge total | "¿cuántos md activos?" | 237 |
| Sprints completados | "¿cuántos en carpeta?" | 4 |
| Hilos canónicos | "¿qué es Cowork?" | "T2 Arquitecto, no Hilo B (F9)" |
| Anti-Dory | "¿estado?" | "kernel/anti_dory/ + 3 migs + 8 fases DONE + audit Sabio externo" |
| Postmortems | "¿reales vs placeholder?" | "2 reales, 2 explícitos placeholder" |
| Runbooks | "¿cuántas credenciales cubre?" | "3/13" |
| Portfolio | "¿cuántos proyectos canónicos?" | 20 |
| Estado portfolio | "¿distribución?" | "7 activos / 4 construcción / 5 diseño / 4 nominales" |
| Skills Manus | "¿cuántos skills hay?" | 42 (en `/home/ubuntu/skills/`) |
| Sabios canónicos | "¿cuántos?" | 8 (DSC-V-001) |
| Capa Magna Cap 17 | "¿implementada?" | "100% aspiracional" |
| TEE / Cripta | "¿existe?" | NO_SOURCE |
| Convergencia Diferida | "¿qué es?" | DSC-X-006 — empresas-hijas autónomas, infra compartida, convergencia cuando PMF |
| Sprint Memento | "¿estado?" | "implementado, kernel 0.84.8 lo declara" |
| Catastro routes UI consumer | "¿quién consume?" | "kernel internal embrion_loop + e2e pipeline; NO UI directa" |
| Drift naming embrion status | "¿hay?" | "sí: /v1/embrion/status vs /estado declarado" |

## 4. Batería de 30 Preguntas-Test (con respuesta correcta)

> Estas preguntas fueron diseñadas para discriminar 80% vs 95% de pericia.

1. **¿Cuál es la versión actual del kernel en producción Railway?** → `0.84.8-sprint-memento`.
2. **¿Cuántos componentes activos reporta el kernel en `/health`?** → 17.
3. **¿Está implementado SMP a nivel de código?** → No, doctrina APP_VISION Cap 7 sin módulo `kernel/smp/`.
4. **¿Existe Cronos en código?** → No. APP_VISION Cap 5 doctrina, 0 archivos `cronos*`, 0 hits funcionales.
5. **¿Cuál es el estado real de El Monstruo Command Center?** → Drift: doctrina lo lista activo en producción pero NO existe directorio en este repo y probe dominio 404.
6. **¿Cuántos modelos AI hay en el catastro de producción?** → 41 (`catastro_modelos`, public read intencional mig 0011).
7. **¿Cuántos eventos en `catastro_eventos`?** → 148.
8. **¿Cuál es el SHA del merge de CATASTRO-WIRING-001 a main?** → `469c5eb` (2026-05-18).
9. **¿Qué helper agregó CATASTRO-WIRING-001 al Embrión?** → `_select_model_via_catastro`.
10. **¿Cuál es el budget diario del Embrión?** → $30 USD.
11. **¿Cuánto consumió el Embrión hoy 2026-05-18 al momento del audit?** → $0.20 USD, 2 thoughts, 6 cycles, 0 errors.
12. **¿Está implementado el Pipeline E2E?** → Sí, `kernel/e2e/` con 12 pasos doctrinales, 8 invocaciones runtime de Catastro.
13. **¿Qué Capas Transversales tienen spec firmado?** → C1 Motor de Ventas (Sprint 90) y C2 SEO+Contenido (Sprint 91). C3-C6 NO.
14. **¿Cuántas migraciones SQL dedicadas a RLS se aplicaron?** → 5: `0004_p0_critico`, `0005_p1_embrion`, `0007_post_s002_5`, `0008_p2_completion`, `0011_catastro_vision_generativa`.
15. **¿Cuántos DSCs Security existen y cuáles faltan?** → 14, faltan S-009, S-011, S-014 (saltos numéricos sin documentar).
16. **¿Cuántos archivos md activos en `bridge/` root?** → 237.
17. **¿Cuántos sprints están en `bridge/sprints_completados/`?** → 4 (ratio 4/34 propuestos).
18. **¿Qué es Cowork según doctrina canónica?** → **T2 Arquitecto** (CLAUDE.md L151). NO "Hilo B". F9 = falla confundir identidad.
19. **¿Cuál es el estado del módulo Anti-Dory?** → Cobertura completa: 6 archivos en `kernel/anti_dory/` + 3 migraciones (0032/0034/0035) + 8 fases DONE (A,B,C,D1-D5) + audit externo Sabio GPT-5.5-Pro.
20. **¿Cuántos postmortems reales vs placeholder?** → 2 reales (`COWORK_AUTO_DISCIPLINE_REAL_001`, `COWORK_MEMENTO_001`) + 2 placeholder explícitos (`ESCAPE_001`, `ROTOR_001` 2026-05-12).
21. **¿Cuántas credenciales tienen runbook de rotación?** → 3 de 13 activas (Bitwarden master, OpenAI key, Supabase service key).
22. **¿Cuántos proyectos canónicos en el portfolio del Monstruo?** → 20 (`docs/INVENTARIO_PROYECTOS_v3_COMPLETO.md`).
23. **¿Distribución del portfolio?** → 7 activos / 4 construcción / 5 diseño / 4 nominales.
24. **¿Cuál es el estado real de CIP?** → 100% diseño/legal, sin código, sin repo. 8 decisiones pendientes (2 bloqueantes: figura legal + distribución rendimientos). Stack: Polygon + ERC-3643. Mercado: Sureste México (plan A).
25. **¿Cuántos Sabios canónicos según DSC-V-001?** → 8.
26. **¿Está implementada la "Capa de Seguridad Magna" (APP_VISION Cap 17)?** → No: Cripta, TEE, anomaly detection runtime, privacy budget DP, confidential compute = 100% aspiracional.
27. **¿Existe TEE/Secure Enclave en código?** → No (NO_SOURCE).
28. **¿Qué es la Convergencia Diferida (DSC-X-006)?** → Patrón canonizado: empresas-hijas autónomas, comparten infra crítica desde día 1, convergen en momentos elegidos cuando cada una prueba PMF independiente. NO es monolito multi-producto.
29. **¿Cuál es el estado del Sprint Memento?** → Implementado, el kernel se identifica como `0.84.8-sprint-memento`. Routes en `/v1/memento` activas, validación memento contamination doctrinal.
30. **¿Quién consume `/v1/catastro/*` directamente?** → Kernel internal: `embrion_loop` (vía CATASTRO-WIRING-001) y `e2e/pipeline` (8 invocaciones). NO hay UI consumer directa de los endpoints de Catastro hoy.

## 5. Delta Gap-95% (lo que falta para llegar)

| Gap | Severidad | Acción para cerrar (fuera scope este pack) |
|---|---|---|
| ChatGPT puede asumir SMP/Cronos implementados leyendo APP_VISION | P0 | Pack 2 da el dato; reforzar en system prompt |
| ChatGPT puede asumir Command Center vivo | P1 | Pack 1+4 dan el dato; canonizar drift en DSC futuro |
| ChatGPT puede asumir CIP tiene MVP | P1 | Pack 4 da el dato |
| ChatGPT puede asumir Capa Magna Cap 17 implementada | P1 | Pack 2 da el dato |
| ChatGPT puede confundir Cowork con "Hilo B" | P2 | Pack 3 da el dato; F9 explícito en CLAUDE.md |
| ChatGPT puede inferir runbooks completos | P2 | Pack 3 da el dato — solo 3/13 |
| ChatGPT puede asumir todos los 20 proyectos tienen build | P1 | Pack 4 da el dato |
| ChatGPT puede asumir C3-C6 specs existen | P2 | Pack 4 da el dato |
| Drift naming `/v1/embrion/status` vs `/estado` | P3 | Pack 1 da el dato |
| Variantes API URL kernel (production vs no-production) | P3 | Pack 1 da el dato |

## 6. Cómo Usar Este Pack para Calibrar a ChatGPT

1. **Cargar como contexto fundacional:** los 5 pack JSON deben ser inyectados al system prompt o a la sesión inicial de ChatGPT.
2. **Ejecutar la batería de 30 preguntas:** medir score binario (correcto/incorrecto). Score ≥ 28/30 = pericia 95%+.
3. **Si ChatGPT falla** preguntas 3, 4, 5, 24, 26, 27 → remediación obligatoria con Pack 2 + Pack 4 antes de cualquier diseño.
4. **Si ChatGPT falla** pregunta 18 → remediación con Pack 3 + CLAUDE.md L151.
5. **Calibrar continuamente:** correr esta batería al inicio de cada hilo nuevo de ChatGPT que vaya a operar sobre el Monstruo.

## 7. ACCESS_BLOCKED list

- Inspección autenticada de endpoints `/v1/embrion/proposals`, `/v1/finops/summary`, `/v1/memory/status`, `/v1/moc/status`, `/v1/catastro/status` (X-API-Key).
- Costos infra real (Railway/Supabase/Langfuse).
- Logs Railway últimos 7 días.
- Status real de proyectos clientes (Roche Bobois, etc.).
- Auditoría completa pre-commit `--no-verify` históricos.

## 8. NO_SOURCE list (consolidada)

- `kernel/smp/`, `kernel/cronos/`, `kernel/cripta/`, `kernel/security_magna/`.
- `command-center/` directorio.
- Repos separados (ticketlike-mx, kukulkan-365, observatorio-merida, CIP).
- Embrión "Convergencia Cronos".
- Apps mobile en producción real (solo esqueleto en este repo).
- Métricas latencia bridge.
- Runbooks crisis: kernel-down, sabios-down, bridge-roto.

## 9. Confirmaciones de Reglas Operativas

- ✅ NO_DESIGN — este pack solo sintetiza, no diseña.
- ✅ NO_CANONIZATION — no agrega DSCs.
- ✅ NO_APP_VISION_v2 — no toca `docs/EL_MONSTRUO_APP_VISION_v1.md`.
- ✅ NO_PRE_IA_CLOSE — no cierra ningún sprint pre-IA.
- ✅ NO_NEW_SPRINT — no propone sprints (solo lista deudas para futuro).
- ✅ EVIDENCE_ONLY — todos los datos provienen de auditoría runtime real 2026-05-18.

## 10. Preguntas Magna Pendientes para Alfredo (consolidadas)

| # | Pack | Pregunta |
|---|---|---|
| P1 | 1 | Dominio kernel sin `-production`: documentar muerte o purgar refs |
| P2 | 1 | Command Center: futuro / otro repo / renombrar |
| P3 | 1 | Permitir intentos autenticados X-API-Key en próximo pack (DSC) |
| P4 | 1 | Drift `/v1/embrion/status` vs `/estado`: alias o doctrina |
| P5 | 2 | SMP sprint inmediato o deuda doctrinal explícita |
| P6 | 2 | Cronos POC mínimo o backlog v1.1+ |
| P7 | 2 | Auditar `--no-verify` histórico en pre-commit con CI logs |
| P8 | 2 | Migración naming `SUPABASE_SERVICE_KEY` con DSC explícito |
| P9 | 3 | Canonizar RACI formal en DSC-OPS-002 |
| P10 | 3 | Sprint dedicado runbooks faltantes |
| P11 | 3 | Política archivado bridge automática |
| P12 | 3 | Disciplina `sprints_completados` automatizar o discontinuar |
| P13 | 4 | Command Center → otro repo o renombrar |
| P14 | 4 | CIP → ¿próximo bloque arranca código? |
| P15 | 4 | Skill Manus para 16 proyectos restantes o priorizar |
| P16 | 4 | C3-C6 specs vs PMF C1+C2 primero |

## 11. Cierre

Este pack se entrega como **evidencia consolidada** para que:
1. **Alfredo** decida qué deudas son priorizadas.
2. **ChatGPT (la pericia)** se calibre con datos reales y no aluciné.
3. **Cowork T2** valide el atlas y vea si requiere observaciones canónicas.
4. **Hilos futuros de Manus** tengan contexto verificado para no rehacer audit desde cero.

Branch: `monstruo-reality-atlas-001`. Carpeta: `monstruo_reality_atlas/reports/`. Sin merge a main propuesto.
