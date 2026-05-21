# GLOBAL_95_REQUIRED_COVERAGE v1.2

> **Propósito:** definir los 9 frentes obligatorios que separan pericia parcial (Reactor/Embriones ~73%) de pericia global 95%.
>
> **Regla binaria:** si CUALQUIERA de estos 9 frentes no está cubierto con score >= 9/10, el max_global_score queda capado según la tabla de §10.
>
> **Creado por:** Manus B, por instrucción T1 (Alfredo Góngora), 2026-05-18.
>
> **NO canoniza.** NO es APP_VISION. NO cierra PRE-IA. Es coverage gate obligatorio para el kit de pericia.

---

## 1. GATE_3_4_COMPLETO

**Exige que ChatGPT-0 distinga:**

| Nivel | Significado | Ejemplo |
|---|---|---|
| Archivo existente | .py en disco con imports | `kernel/moc/moc_routes.py` existe |
| Inicializado en app.state/lifespan | Registrado en FastAPI startup | `app.state.moc_router` asignado |
| Endpoint HTTP real | Ruta accesible via curl/test | `GET /v1/moc/status` responde 200 |
| Consumidor UI | Flutter/CC/Bot lo llama | `apps/mobile/gateway/server.py` importa |
| Madurez operacional | M1-M5 según evidencia | Tests, error-paths, hardening |

**Caveat obligatorio:**

> M4_Tested NO significa M5_Hardened, ni UI maturity, ni route-hardening completo. Un módulo M4 tiene tests de lógica pasando pero puede carecer de: error-path coverage, rate limiting, input validation exhaustiva, observabilidad, y consumidor UI real.

**Evidencia requerida:** `GATE_3_4_MODULE_MATURITY_EVIDENCE_PACK_v1_1.md` + `GATE_3_4_MODULE_MATURITY_MATRIX_v1_1.json`

**Fail condition:** afirmar que M4 = production-ready, o confundir endpoint existente con consumidor UI activo.

---

## 2. INTERFACES_CONTEXT_FABRIC

**Exige lectura de:**

- `interfaces_context_fabric/maps/EXISTING_DESIGN_COVERAGE_MATRIX.md` (50+ conceptos catalogados)
- `interfaces_context_fabric/maps/SURFACE_REGISTRY.yaml`
- `interfaces_context_fabric/maps/HYPOTHESIS_REGISTRY.yaml`
- `interfaces_context_fabric/maps/DECISIONS_PENDING_T1.yaml`
- `interfaces_context_fabric/maps/CANON_TRUTH_MATRIX.md`
- 20 superficies Daily/Cockpit (APP_VISION cap. 3-4)

**Exige comprensión de:**

- Acto 1 (20 superficies como métrica) vs Acto 2 (Calm Tech ambient)
- Interfaz latente (no manifesta a menos que converja)
- Calm Tech (si abrís dashboard, ya falló)
- Schema-First (hipótesis activa, no canon firmado)
- Diseño co-creado (Alfredo + IA, no IA sola)

**Bloquea:** rediseñar interfaces sin leer Fabric. Proponer superficies nuevas sin consultar EXISTING_DESIGN_COVERAGE_MATRIX.

**Fail condition:** proponer "Cronista Familiar" como concepto nuevo (es alias de `cronos_modo_cripta`), o diseñar UI sin verificar si ya existe en el fabric.

---

## 3. APP_VISION

**Exige:**

- Entender APP_VISION como **doctrina magna** (el documento fundacional del Monstruo, no un spec técnico)
- NO tratar APP_VISION como runtime (no es código ejecutable, es visión)
- NO escribir APP_VISION v1.4 sin Alfredo (solo T1 puede firmar nueva versión)
- NO usar APP_VISION para afirmar código existente (APP_VISION describe el futuro deseado, no el presente implementado)

**Fuente:** `docs/EL_MONSTRUO_APP_VISION_v1.md`

**Fail condition:** llamar runtime a APP_VISION, afirmar que algo "ya está implementado porque APP_VISION lo dice", o proponer v1.4 sin firma T1.

---

## 4. MOBILE_FLUTTER_REALITY

**Exige distinguir:**

| Capa | Estado real |
|---|---|
| Diseño mobile (APP_VISION caps 3-4) | Doctrina firmada |
| Implementación Flutter real | Chasis parcial con brechas |
| Home Daily canónica | NO existe (Home actual = proxy ChatScreen) |
| Daily/Cockpit superficies | Parcialmente implementadas |
| Brand DNA | En drift (tema/colores no alineados con doctrina) |
| Auth/secure storage/i18n | Pendientes como capabilities transversales |

**Exige conocer gaps de mobile:**

- Home es proxy de ChatScreen, no la Home Daily canónica
- Threads/Pendientes/Conexiones son placeholders
- A2UI renderer es placeholder (schema existe, renderer no)
- Brand DNA en drift binario

**Fail condition:** afirmar Mobile/Cockpit/Portfolio implementado sin evidencia de código real, o confundir placeholder con implementación funcional.

---

## 5. ANONYMOUS_SECURITY_IDENTITY

**Exige:**

- `user_id=anonymous` = INSUFFICIENT_EVIDENCE / BLOCKER preventivo según contexto
- NO canonizar anonymous (no es un usuario válido, es ausencia de identidad)
- NO arreglar anonymous sin clasificación T1 (requiere decisión magna sobre auth architecture)
- NO tests memory_routes E2E si dependen de anonymous (resultados no confiables)
- Diferenciar: `profile_id` (UUID real), `google_sub` (OAuth identity), `user_id` legacy (string arbitrary)

**Contexto:** anonymous fue detectado como default en Night 0 Shadow Run. Es BLOCKER preventivo para R1/tests/memoria/multiusuario.

**Fail condition:** afirmar anonymous como bug simple o feature sin T1, o ejecutar tests que dependen de anonymous como si fueran válidos.

---

## 6. SMP_CRONOS_CRIPTA

**Exige:**

- SMP = **Sovereign Memory Plane** (NO "Secure Memory Protocol")
- Cronos = río navegable de la vida con 9 capas semánticas
- Modo Cripta = sub-modo de Cronos con Shamir Secret Sharing
- CRONOS_1/2/3 y AUTH_TIERS_001 son sprints propuestos por Cowork, pendientes firma T1
- Cronista Familiar / Herencia Narrativa / Legacy Capture / Day One = aliases DESCARTADOS de `cronos_modo_cripta`

**Fuentes:** APP_VISION cap. 5, `07_ALIAS_LEDGER.yaml`, `interfaces_context_fabric/context_packs/PACK_04_CRONOS_RIO_DE_VIDA.md`

**Fail condition:** redibujar Cronista Familiar como concepto nuevo, confundir SMP con "Secure Memory Protocol", o proponer implementación Cronos sin SMP resuelto.

---

## 7. PRE_IA

**Exige:**

- NO cerrar PRE-IA sin frase literal de Alfredo (solo T1 puede cerrar la fase)
- Pre-IA hypotheses (pre-IA-001..010) siguen DRAFT hasta cierre explícito
- NO canonizar pre-IA hypotheses sin cierre (son ideas pre-Monstruo, no doctrina)
- La fase PRE-IA es el período 2020-2021 donde Alfredo conceptualizó sin IA

**Fuente:** `interfaces_context_fabric/raw_rescues/alfredo_pre_ia_checkpoint_2020_2021_DRAFT.md`

**Fail condition:** cerrar PRE-IA, canonizar hypotheses pre-IA como doctrina vigente, o ignorar que son DRAFT.

---

## 8. COMMAND_CENTER

**Exige:**

- Diferenciar Command Center actual (consola parcial) vs canon cockpit (superficie completa)
- 7 superficies actuales reales: Chat, Runs, FinOps, Security, Memory, Settings, (parcial)
- 12-15 superficies canónicas (si sigue vigente según APP_VISION)
- NO llamar cockpit read-only "control plane" (control plane implica write authority)
- NO confundir UI visible con runtime/control real

**Estado real:** Command Center existe como Next.js app con nav real pero tema en drift y funcionalidad parcial. NO es el Cockpit canónico completo.

**Fail condition:** llamar control plane a cockpit read-only, afirmar 12+ superficies implementadas cuando solo hay 7, o confundir UI visible con autoridad de control.

---

## 9. PORTFOLIO_UI_EMPRESAS_HIJAS

**Exige:**

- Conocer que portfolio UI es gap/superficie pendiente
- NO tratarlo como implementado si no hay código
- Distinguir: proyectos-hijos (CIP, ticketlike, SoftRestaurant) / UIs satélite / Monstruo core
- Los proyectos-hijos tienen sus propias UIs independientes del Monstruo
- El portfolio view dentro del Monstruo (vista consolidada de todos los proyectos) NO existe

**Fail condition:** afirmar portfolio UI implementado sin evidencia, o confundir UIs de proyectos-hijos con superficie del Monstruo.

---

## 10. REGLA DE SCORE (cap máximo)

| Condición | max_global_score |
|---|---|
| Gate 3.4 no absorbido | 85 |
| Interfaces/Fabric/APP_VISION/mobile no absorbidos | 88 |
| anonymous/security no absorbido | 90 |
| SMP/Cronos/Cripta/PRE-IA no absorbidos | 90 |
| Command Center/Portfolio UI no absorbidos | 92 |
| GLOBAL_95_REQUIRED_COVERAGE no cubierto completo | 90 |
| **Para reclamar GLOBAL_95:** | cada frente >= 9/10 + 0 P0 abiertos por falsa clasificación |

---

## 11. RELACIÓN CON OTROS ARCHIVOS

| Archivo | Relación |
|---|---|
| `PERICIA_SCORE_RUBRIC_v1_2.yaml` | Implementa estas reglas de score como YAML parseable |
| `PERICIA_TEST_v1_2_POST_REACTOR_EMBRYOS.md` | 18 preguntas nuevas (2 por frente) |
| `CHATGPT_PERICIA_STATE_v1_2_POST_REACTOR_EMBRYOS.json` | Registra scores por frente |
| `CHATGPT_PERICIA_CHECKPOINT_v1_2_POST_REACTOR_EMBRYOS.md` | Checkpoint narrativo post-patch |
| `PERICIA_GAPS_TO_95_v1_2.md` | Mapa de gaps específicos por frente |
