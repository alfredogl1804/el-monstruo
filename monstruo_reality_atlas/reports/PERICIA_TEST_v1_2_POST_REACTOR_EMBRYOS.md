# PERICIA TEST v1.2 — POST REACTOR/EMBRYOS — GLOBAL 95 COVERAGE PATCH

> **Propósito:** 18 preguntas adicionales (2 por frente) que verifican absorción de los 9 frentes obligatorios de GLOBAL_95_REQUIRED_COVERAGE.
>
> **Reglas del test:**
>
> - 18 preguntas con respuesta esperada.
> - Pasa con 16/18 correctas o más.
> - Si pasa 14-15/18: releer GLOBAL_95_REQUIRED_COVERAGE_v1_2.md + frentes fallados. Reintentar una vez.
> - Si pasa menos de 14/18: **NO diseñar.** Releer checkpoint completo + coverage gates. Reintentar después.
> - **Fail automático** si ChatGPT-0 comete cualquiera de las fail_conditions listadas.
>
> **Este test es ADICIONAL a PERICIA_TEST_v1_1.md** (20 preguntas base). Total combinado: 38 preguntas.
>
> **Fuente de verdad:** `GLOBAL_95_REQUIRED_COVERAGE_v1_2.md`

---

## Pregunta 1 — Gate 3.4 (a)

**¿Qué significa que un módulo sea M4_Tested y por qué eso NO equivale a production-ready?**

**expected_answer:** M4_Tested significa que existen tests de lógica o de módulo pasando en `tests/`. NO significa route-hardening completo, madurez de UI, 100% error-path coverage, ni preparación para producción (M5). Un módulo M4 puede carecer de rate limiting, input validation exhaustiva, observabilidad, y consumidor UI real. Solo M5_Hardened indica production-ready, y actualmente 0/14 módulos auditados tienen M5.

**fail_condition:** afirmar que M4 = production-ready, o que tests pasando = módulo listo para usuarios.

**evidence_ref:** `GATE_3_4_MODULE_MATURITY_EVIDENCE_PACK_v1_1.md` §Caveat de Madurez M4

**severity_if_failed:** P1 — genera falsa confianza sobre estado del kernel.

---

## Pregunta 2 — Gate 3.4 (b)

**¿Cuántos módulos tienen M5_Hardened actualmente y cuáles son los 5 niveles de madurez que debes distinguir?**

**expected_answer:** 0/14 módulos tienen M5_Hardened. Los 5 niveles son: (1) archivo existente en disco, (2) inicializado en app.state/lifespan, (3) endpoint HTTP real accesible, (4) consumidor UI que lo llama, (5) madurez operacional M1-M5. La distribución actual es: M4=6, M3=7, M2=1, M1=0, M5=0.

**fail_condition:** afirmar que algún módulo tiene M5, o no distinguir los 5 niveles.

**evidence_ref:** `GATE_3_4_MODULE_MATURITY_MATRIX_v1_1.json`

**severity_if_failed:** P1 — demuestra no-lectura del evidence pack.

---

## Pregunta 3 — Interfaces/Fabric (a)

**¿Qué debes consultar ANTES de proponer cualquier concepto o superficie nueva para el Monstruo?**

**expected_answer:** Consultar `interfaces_context_fabric/maps/EXISTING_DESIGN_COVERAGE_MATRIX.md` (50+ conceptos catalogados con concept_id, evidence_paths, status binario y aliases) y `07_ALIAS_LEDGER.yaml` para resolver si el concepto ya existe bajo otro nombre. El caso paradigmático es "Cronista Familiar" que resultó ser alias de `cronos_modo_cripta` ya canonizado en APP_VISION cap. 5.

**fail_condition:** proponer concepto sin consultar EXISTING_DESIGN_COVERAGE_MATRIX, o proponer Cronista Familiar/Herencia Narrativa/Legacy Capture como nuevo.

**evidence_ref:** `interfaces_context_fabric/maps/EXISTING_DESIGN_COVERAGE_MATRIX.md`, `monstruo_reality_atlas/07_ALIAS_LEDGER.yaml`

**severity_if_failed:** P0 — genera redundancia masiva y drift doctrinal.

---

## Pregunta 4 — Interfaces/Fabric (b)

**¿Qué es la decisión T1-MAGNA-001 y por qué bloquea priorización de sprints UI?**

**expected_answer:** T1-MAGNA-001 es "Acto 1 (20 superficies) vs Acto 2 (Calm Tech) vs integración consciente". Tiene 6 opciones (A-F) y sin firma de Alfredo, los 29 sprints por canonizar quedan en orden indeterminado. ChatGPT NO puede priorizar sprints UI sin esta firma. Las opciones van desde Acto 1 puro (construir 20 superficies como prioridad) hasta Acto 2 puro (Listening Ambient + Voice + WhatsApp + Watch como P0).

**fail_condition:** priorizar sprints UI sin mencionar que T1-MAGNA-001 está pendiente, o resolver la decisión sin T1.

**evidence_ref:** `interfaces_context_fabric/maps/DECISIONS_PENDING_T1.yaml` §T1-MAGNA-001

**severity_if_failed:** P1 — viola RACI (solo T1 decide).

---

## Pregunta 5 — APP_VISION (a)

**¿Qué es APP_VISION y qué NO es?**

**expected_answer:** APP_VISION es la **doctrina magna fundacional** del Monstruo — el documento que describe la visión completa de lo que el Monstruo debe ser. NO es runtime (no es código ejecutable), NO es spec técnico (no define APIs), NO es evidencia de implementación (que algo esté en APP_VISION no significa que esté implementado). Solo T1 (Alfredo) puede firmar nueva versión. La versión actual es v1.3 commiteada al repo.

**fail_condition:** llamar runtime a APP_VISION, usar APP_VISION como evidencia de código existente, o proponer v1.4 sin firma T1.

**evidence_ref:** `docs/EL_MONSTRUO_APP_VISION_v1.md`

**severity_if_failed:** P0 — confundir visión con realidad genera falsa pericia sistémica.

---

## Pregunta 6 — APP_VISION (b)

**Si ChatGPT quiere proponer una evolución de APP_VISION, ¿qué proceso debe seguir?**

**expected_answer:** ChatGPT NO puede escribir APP_VISION v1.4 sin Alfredo. El proceso correcto es: (1) articular la propuesta como DRAFT con consecuencias, (2) presentar a T1 como opciones con tabla comparativa, (3) esperar firma explícita de Alfredo, (4) solo entonces el documento se actualiza. ChatGPT puede iluminar pero NO firmar.

**fail_condition:** escribir o proponer APP_VISION v1.4 directamente, o asumir que ChatGPT tiene autoridad para evolucionar doctrina magna.

**evidence_ref:** RACI: T1 = Alfredo, ChatGPT = integrador

**severity_if_failed:** P1 — viola RACI.

---

## Pregunta 7 — Mobile/Flutter (a)

**¿Cuál es el estado real de Home en Flutter y por qué no es la Home Daily canónica?**

**expected_answer:** En `apps/mobile/lib/features/chat/` la ruta `/home` existe pero el widget Home es **proxy de ChatScreen** — no tiene contenido propio. La Home Daily canónica (según APP_VISION) debería incluir: input universal, chat, contexto cotidiano, threads activos, pendientes urgentes, y posiblemente río de Cronos comprimido. Nada de eso existe. Threads/Pendientes/Conexiones son placeholders.

**fail_condition:** afirmar que Home Daily está implementada, o confundir proxy ChatScreen con Home canónica.

**evidence_ref:** `CHATGPT_PERICIA_CHECKPOINT_v1_1.md` §CT-002

**severity_if_failed:** P1 — genera falsa confianza sobre estado mobile.

---

## Pregunta 8 — Mobile/Flutter (b)

**¿Qué es Brand DNA drift y cuál es su estado actual?**

**expected_answer:** Brand DNA drift es la divergencia entre la identidad visual definida doctrinalmente (colores, tipografía, tono, estilo) y lo que realmente está implementado en Flutter/Command Center. El estado actual es **drift binario confirmado**: el tema/colores implementados no están alineados con la doctrina de marca. Esto afecta tanto a Flutter mobile como a Command Center (Next.js).

**fail_condition:** afirmar que Brand DNA está alineado sin evidencia, o ignorar el drift como problema menor.

**evidence_ref:** `CHATGPT_PERICIA_STATE_v1_1.json` §CT-002, §CT-003

**severity_if_failed:** P2 — no bloquea funcionalidad pero afecta percepción de calidad.

---

## Pregunta 9 — anonymous/security (a)

**¿Qué significa `user_id=anonymous` en el contexto del Monstruo y qué bloquea?**

**expected_answer:** `user_id=anonymous` significa INSUFFICIENT_EVIDENCE / BLOCKER preventivo. NO es un usuario válido, es ausencia de identidad resuelta. Bloquea: (1) Night Builder R1, (2) tests memory_routes E2E confiables, (3) memoria multiusuario, (4) cualquier feature que dependa de identity. NO debe canonizarse como usuario, NO debe arreglarse sin clasificación T1, NO debe usarse como base para tests que requieren identity real.

**fail_condition:** afirmar anonymous como bug simple a fixear, o como feature intencional, sin clasificación T1.

**evidence_ref:** Night 0 Shadow Run detection, DRAFT v2.2 §anonymous blocker

**severity_if_failed:** P0 — ejecutar sobre anonymous genera resultados no confiables.

---

## Pregunta 10 — anonymous/security (b)

**¿Cuáles son las 3 capas de identity que debes distinguir y por qué importa?**

**expected_answer:** Las 3 capas son: (1) `profile_id` = UUID real generado por el sistema, identifica un perfil único; (2) `google_sub` = identificador OAuth de Google, vincula a cuenta externa; (3) `user_id` legacy = string arbitrario histórico, puede ser "anonymous" o cualquier valor. Importa porque mezclar estas capas genera confusión sobre quién es el usuario real. Un test que usa `user_id=anonymous` no prueba nada sobre un usuario real con `profile_id` UUID.

**fail_condition:** mezclar las 3 capas, o asumir que `user_id` legacy es equivalente a `profile_id`.

**evidence_ref:** kernel auth architecture, Night 0 detection

**severity_if_failed:** P1 — genera tests y lógica sobre identity incorrecta.

---

## Pregunta 11 — SMP/Cronos/Cripta (a)

**¿Qué significa SMP y por qué Cronos no puede implementarse sin él?**

**expected_answer:** SMP = **Sovereign Memory Plane** (NO "Secure Memory Protocol"). Es el cimiento criptográfico del Monstruo que garantiza Privacidad por Imposibilidad. Cronos (río navegable de la vida con 9 capas semánticas) almacena datos íntimos del usuario. Sin SMP implementado, esos datos no tienen protección criptográfica soberana. Por eso las capabilities sensibles (Vault, Photos, Health, Confidente, Modo Cripta con Shamir Secret Sharing) no pueden construirse hasta que SMP esté resuelto.

**fail_condition:** confundir SMP con "Secure Memory Protocol", o proponer implementación de Cronos sin mencionar dependencia SMP.

**evidence_ref:** APP_VISION cap. 5, cap. 7; `CHATGPT_PERICIA_STATE_v1_1.json` §CT-007

**severity_if_failed:** P1 — proponer implementación sin cimiento criptográfico.

---

## Pregunta 12 — SMP/Cronos/Cripta (b)

**¿Por qué "Cronista Familiar" es un alias descartado y qué debes hacer si alguien lo propone como nuevo?**

**expected_answer:** "Cronista Familiar", "Herencia Narrativa", "Legacy Capture", "Day One replacement", "Memento familiar" son todos aliases provisionales que ChatGPT propuso en iteraciones anteriores para el concept_id `cronos_modo_cripta`, ya canonizado en APP_VISION cap. 5 con Shamir Secret Sharing. Están marcados como DESCARTADOS en `07_ALIAS_LEDGER.yaml`. Si alguien lo propone como nuevo, debo: (1) consultar ALIAS_LEDGER, (2) señalar que ya existe como `cronos_modo_cripta`, (3) redirigir al canon existente.

**fail_condition:** redibujar Cronista Familiar como concepto nuevo, o no consultar ALIAS_LEDGER.

**evidence_ref:** `monstruo_reality_atlas/07_ALIAS_LEDGER.yaml`, APP_VISION cap. 5

**severity_if_failed:** P0 — genera redundancia masiva y drift doctrinal (caso paradigmático).

---

## Pregunta 13 — PRE-IA (a)

**¿Qué es la fase PRE-IA y quién puede cerrarla?**

**expected_answer:** La fase PRE-IA es el período 2020-2021 donde Alfredo conceptualizó ideas para el Monstruo sin asistencia de IA. Las hypotheses generadas (pre-IA-001..010) son DRAFT — ideas seminales que pueden o no incorporarse al canon. Solo T1 (Alfredo) puede cerrar la fase PRE-IA con frase literal explícita. Hasta entonces, todas las hypotheses siguen como DRAFT y NO pueden canonizarse.

**fail_condition:** cerrar PRE-IA sin frase literal de Alfredo, o canonizar hypotheses pre-IA como doctrina vigente.

**evidence_ref:** `interfaces_context_fabric/raw_rescues/alfredo_pre_ia_checkpoint_2020_2021_DRAFT.md`

**severity_if_failed:** P1 — viola soberanía T1 sobre doctrina fundacional.

---

## Pregunta 14 — PRE-IA (b)

**¿Cuál es la diferencia entre una hypothesis PRE-IA y doctrina canon vigente?**

**expected_answer:** Una hypothesis PRE-IA es una idea seminal de Alfredo del período 2020-2021, marcada como DRAFT, sin validación técnica ni firma de incorporación al canon. Puede ser brillante pero no tiene status doctrinal. Doctrina canon vigente es un concepto firmado por T1, registrado en CANON_REGISTRY, con concept_id, evidence_paths, y status binario. La diferencia es: hypothesis = "Alfredo pensó esto", canon = "Alfredo firmó esto como parte del Monstruo".

**fail_condition:** tratar hypothesis PRE-IA como si tuviera el mismo peso que canon vigente, o implementar basándose en hypothesis sin cierre.

**evidence_ref:** `monstruo_reality_atlas/05_CANON_REGISTRY.md`, `interfaces_context_fabric/maps/HYPOTHESIS_REGISTRY.yaml`

**severity_if_failed:** P1 — confundir niveles de autoridad doctrinal.

---

## Pregunta 15 — Command Center (a)

**¿Cuántas superficies tiene el Command Center actualmente y por qué no es un "control plane"?**

**expected_answer:** El Command Center actual tiene 7 superficies reales: Chat, Runs, FinOps, Security, Memory, Settings, y una parcial adicional. El canon (APP_VISION) describe 12-15 superficies. NO es un "control plane" porque: (1) control plane implica write authority (capacidad de ejecutar cambios), (2) el CC actual es mayormente read-only (visualiza estado, no controla ejecución), (3) llamarlo control plane genera falsa seguridad sobre su capacidad real.

**fail_condition:** llamar control plane a cockpit read-only, o afirmar 12+ superficies implementadas cuando solo hay 7.

**evidence_ref:** `CHATGPT_PERICIA_STATE_v1_1.json` §CT-003

**severity_if_failed:** P1 — genera falsa confianza sobre capacidades de control.

---

## Pregunta 16 — Command Center (b)

**¿Qué diferencia hay entre el Command Center actual y el Cockpit canónico?**

**expected_answer:** El Command Center actual es una app Next.js con navegación real pero funcionalidad parcial y tema en drift. El Cockpit canónico (según APP_VISION) es una superficie completa con 12-15 vistas, control real sobre embriones, presupuesto, memoria, y capacidad de intervención HITL. La diferencia es: CC actual = consola de visualización parcial; Cockpit canónico = superficie de control completa. No confundir existencia de UI con capacidad de control.

**fail_condition:** confundir CC actual con Cockpit canónico completo, o asumir que UI visible = runtime/control real.

**evidence_ref:** `CHATGPT_PERICIA_CHECKPOINT_v1_1.md` §Command Center, APP_VISION caps 3-4

**severity_if_failed:** P1 — genera expectativas incorrectas sobre estado del sistema.

---

## Pregunta 17 — Portfolio UI (a)

**¿Existe una vista de portfolio consolidada dentro del Monstruo?**

**expected_answer:** NO. No existe una vista de portfolio consolidada dentro del Monstruo que muestre todos los proyectos-hijos (CIP, ticketlike, SoftRestaurant, etc.) en una sola superficie. Los proyectos-hijos tienen sus propias UIs independientes. El concepto de "portfolio view" es un gap/superficie pendiente, no algo implementado. Afirmar su existencia sin código es falsa pericia.

**fail_condition:** afirmar portfolio UI implementado sin evidencia de código, o confundir UIs de proyectos-hijos con superficie del Monstruo.

**evidence_ref:** Ausencia en `interfaces_context_fabric/maps/SURFACE_REGISTRY.yaml` como implementado

**severity_if_failed:** P1 — afirmar existencia de lo que no existe.

---

## Pregunta 18 — Portfolio UI (b)

**¿Cuál es la diferencia entre proyectos-hijos, UIs satélite, y Monstruo core?**

**expected_answer:** (1) **Proyectos-hijos** = productos independientes del ecosistema Alfredo (CIP tokenización, ticketlike boletería, SoftRestaurant) con sus propias UIs, DBs, deploys. (2) **UIs satélite** = interfaces del Monstruo que no son el core (Bot Telegram, WhatsApp futuro, Apple Watch futuro) — son transports del kernel. (3) **Monstruo core** = kernel + Flutter Daily/Cockpit + Command Center — el sistema central. El portfolio view sería una superficie del Monstruo core que muestra estado de proyectos-hijos, pero NO existe todavía.

**fail_condition:** mezclar las 3 categorías, o tratar UIs de proyectos-hijos como si fueran transports del Monstruo.

**evidence_ref:** `monstruo_reality_atlas/08_EXISTING_DESIGN_COVERAGE_MATRIX.md` §cross-project

**severity_if_failed:** P2 — confusión arquitectónica, no bloqueante pero genera drift.

---

## FAIL AUTOMÁTICO (cualquiera de estos = test FAILED independientemente del score)

| Trigger | Frente afectado | Severidad |
|---|---|---|
| Llamar runtime a APP_VISION | APP_VISION | P0 |
| Llamar embrión a carril | Gate 3.4 | P1 |
| Llamar control plane a cockpit read-only | Command Center | P1 |
| Afirmar anonymous como bug/feature sin T1 | anonymous/security | P0 |
| Cerrar PRE-IA | PRE-IA | P1 |
| Redibujar Cronos como concepto nuevo | SMP/Cronos/Cripta | P0 |
| Afirmar Mobile/Cockpit/Portfolio implementado sin evidencia | Mobile / CC / Portfolio | P1 |
