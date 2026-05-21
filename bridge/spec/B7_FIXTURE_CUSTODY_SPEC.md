# B7 — Hidden Fixture Custody no-compositor (Design Spec)

**Estado:** `DRAFT_T1_PENDING`
**Autor:** Manus E2 (autor NO-Cowork)
**Fuente normativa:** `bridge/control_tower/2026-05-20/manus_e2/B6_B12_DESIGN_CLOSURE_PACK_v0_2.md` §3
**Rama:** `control-tower/2026-05-20-b7-evidence-pack`
**Fecha:** 2026-05-20
**Lote:** ANTI_DORY_PARALLEL_GATES_BATCH_001

> Este documento NO canoniza B7. Es un design pack derivado y consolidado desde el closure v0.2 firmado. No implementa runtime. No modifica main. No declara Dory muerto.

---

## §1 Definición (verbatim closure v0.2 §3.1 — REDISEÑADA v0.2)

Este gate canoniza la custodia de los **50 hidden fixtures** referidos en B4 (DORY_BENCH + CVDS) y en B7 fuente. Los fixtures son casos de prueba ocultos que, al ser ejecutados contra DORY_BENCH, permiten medir la métrica CVDS = PASS_conocidos / PASS_ocultos ≥ 0.95. Si el compositor del spec conoce los fixtures ocultos, hay un riesgo binario de overfit (gating de Goodhart), y la métrica deja de ser señal.

**v0.2 corrige el fallo arquitectónico crítico identificado por el auditor Cowork T2-A en su §3:** los Sabios LLM (Opus 4.7, Gemini 3.1 Pro, DeepSeek R1, Kimi K2.6, etc.) son endpoints de inferencia **stateless**. No tienen filesystem, no tienen keychain, no tienen persistencia entre sesiones. Por lo tanto, **un Sabio LLM no puede ser custodio de un slice cifrado de fixtures**. Lo que un Sabio LLM sí puede hacer es actuar como **auditor/verificador** consumiendo inputs sanitizados (hashes, métricas agregadas, resultados sanitizados de ejecución).

Ningún fixture oculto entra al prompt o al model context de un Sabio LLM bajo ninguna circunstancia. **Esta es la regla binaria principal de v0.2.**

---

## §2 PASS criteria binarios (REDISEÑADOS v0.2)

| # | Criterio | Verificable por |
|---|----------|-----------------|
| B7.1 | Existen 50 fixtures ocultos almacenados cifrados en repositorio bajo control T1, accesible solo a custodios autorizados (definidos en B7.3 v0.2). | Auditoría documental |
| B7.2 | Custodio NO incluye Cowork T2-A (compositor de v1.0/v1.1/v1.1.1) ni Grok 4 (autor de PATCHES 1/2/3 sobre v1.1.1). Si en el futuro Manus E2 actuara como compositor de v2.0 RE-FUNDADO, también queda excluido como custodio. **Custodio NO incluye Sabios LLM como tales** (son auditores, no custodios). | Auditoría documental |
| **B7.3 (REDISEÑADO v0.2)** | **Custodios válidos:** terna fija de 3 actores entre las siguientes opciones, todas con almacenamiento persistente bajo control T1: (a) **T1 escrow humano** — Alfredo personalmente con keychain físico/digital; (b) **cuentas cloud privadas controladas por T1** — bucket GCS/S3 con IAM allow-list explícita a T1 + ≤2 humanos delegados, sin acceso de Sabios LLM ni de Cowork; (c) **HSM/KMS remoto** — Vault / AWS KMS / GCP KMS con audit log de cada acceso; (d) **humanos delegados por T1** — personas físicas con identidad verificada y commitment escrito; (e) **repos GitHub/Codeberg privados cifrados por el custodio antes del push**, con la clave de cifrado fuera del repo y bajo control del custodio. Cada custodio tiene un slice cifrado del set; reconstrucción requiere ≥2 de 3. | Auditoría documental + commit signature |
| **B7.4 (REDISEÑADO v0.2)** | **Auditor / verificador:** terna rotativa de Sabios LLM **separada** de la terna de custodios. Calendario fijo (ver B11): Q1 Opus 4.7, Q2 DeepSeek R1, Q3 Gemini 3.1 Pro, Q4 Kimi K2.6. El Sabio activo audita únicamente **hashes, métricas agregadas y resultados sanitizados** producidos por el runner DORY_BENCH. Bajo ninguna circunstancia el Sabio recibe contenido de fixtures en su prompt o contexto. | Audit log + procedimiento + log de prompts a Sabios |
| B7.5 | Rotación trimestral de fixtures: cada Q (90 días) se generan ≥10 fixtures nuevos, se retiran ≥10 fixtures viejos, y el custodio activo rota dentro de la terna de **custodios** (no de la terna de auditores). Reglas binarias: (a) compositor del trimestre actual nunca custodia ese mismo trimestre; (b) auditor B7 (Sabio LLM) del trimestre anterior no produce fixtures del trimestre siguiente; (c) custodio del trimestre actual no es el mismo que en los 2 trimestres anteriores (rotación obligatoria). **Fallback v0.2:** si la terna de custodios no alcanza quórum por indisponibilidad, T1 escrow humano funciona como custodio de emergencia con quórum reducido a 1 (T1) hasta que la terna se restaure. | Auditoría documental |
| B7.6 | Distribución de fixtures al runner DORY_BENCH se hace solo en runtime, vía decryption con quórum 2-de-3 de **custodios de almacenamiento** (no de Sabios LLM); el runner no almacena el set descifrado en disco persistente; el set descifrado vive solo en memoria del runner durante la ejecución y se purga al finalizar el run. | Log de ejecución firmado |
| B7.7 | Audit log público (no los fixtures) versionado: hash criptográfico del set actual, fecha de rotación, custodios que descifraron, run_id de DORY_BENCH consumidor, **identidad del Sabio LLM auditor** que recibió las métricas sanitizadas (sin contenido). | Repo público, auditable por cualquiera |
| **B7.8 (NUEVO v0.2)** | Verificación criptográfica binaria: ningún prompt enviado a un Sabio LLM en el ciclo DORY_BENCH contiene contenido de fixtures. Esto se verifica con un test runtime: (a) interceptar el prompt completo enviado al Sabio activo de la terna; (b) computar hash del prompt; (c) comparar contra blacklist de hashes de fixtures actuales (custodiada por los custodios B7.3); (d) si match, abortar la ejecución con evento `FIXTURE_LEAK_DETECTED_PROMPT`. | VERIFICADOR-001 + audit log |

---

## §3 FAIL criteria (cualquiera ⇒ FAIL)

- Custodia única (un solo actor controla los 50 fixtures, salvo el caso de fallback B7.5 con T1 escrow temporal).
- Cowork T2-A o Grok 4 entre los custodios.
- Compositor del spec actual entre los custodios.
- **v0.2: Sabio LLM listado como custodio en B7.3** (los Sabios solo son auditores en B7.4).
- Rotación trimestral ausente.
- Set descifrado almacenado en disco persistente del runner.
- Audit log de rotación ausente.
- **v0.2: Cualquier prompt a Sabio LLM en el ciclo DORY_BENCH contiene contenido de fixtures (verificado por B7.8).**

---

## §4 Evidencia requerida

| ID | Artefacto | Formato | Path o ubicación | Estado |
|----|-----------|---------|------------------|--------|
| B7-E1 | Inventario actual de los 50 fixtures (solo hashes, no contenido) | JSON | `bridge/control_tower/evidence/B7/B7_E1_fixture_hash_inventory.json` | PENDIENTE — runtime |
| B7-E2 | Declaración de custodios actuales (terna de almacenamiento, NO Sabios LLM) firmada por T1 | Markdown | `bridge/control_tower/evidence/B7/B7_E2_custodian_declaration.md` | PENDIENTE — T1 |
| B7-E3 | Procedimiento de rotación trimestral (incluye fallback T1 escrow) | Markdown | `bridge/control_tower/keys/DORY_BENCH_FIXTURE_ROTATION_PROCEDURE.md` | DRAFT (este pack) |
| B7-E4 | Audit log de últimas 4 rotaciones (1 año) | JSON Lines | `bridge/control_tower/evidence/B7/B7_E4_rotation_audit.jsonl` | PENDIENTE — runtime |
| B7-E5 | Logs de los runs DORY_BENCH consumidores que probaron PASS_oculto y CVDS | JSON Lines | `bridge/control_tower/evidence/B7/B7_E5_dory_bench_consumer_runs.jsonl` | PENDIENTE — runtime |
| **B7-E6 (NUEVO v0.2)** | Declaración de auditores Sabios LLM del año en curso (terna rotativa B7.4, calendario B11) firmada por T1 | Markdown | `bridge/control_tower/evidence/B7/B7_E6_auditor_declaration.md` | PENDIENTE — T1 (depende de B11) |
| **B7-E7 (NUEVO v0.2)** | Logs de prompts enviados a Sabios LLM auditores con verificación B7.8 (hash blacklist) | JSON Lines | `bridge/control_tower/evidence/B7/B7_E7_auditor_prompt_audit.jsonl` | PENDIENTE — runtime |

---

## §5 Productores autorizados de evidencia

| Evidencia | Productor autorizado |
|-----------|----------------------|
| B7-E1 | Custodio activo del trimestre (uno de la terna B7.3, entidad con almacenamiento persistente), con quórum 2-de-3 para descifrar y producir hashes |
| B7-E2 | T1 verbatim — declaración de la terna de custodios |
| B7-E3 | Autor NO-Cowork (Manus E2 o Sabio externo en rol de auditor documental). NO Cowork T2-A. |
| B7-E4 | Custodio que ejecuta la rotación + firma de auditor LLM (B7.4) sobre las métricas resultantes |
| B7-E5 | VERIFICADOR-001 + runner DORY_BENCH (CI o sandbox firmado) |
| **B7-E6 (v0.2)** | T1 verbatim — declaración de la terna de auditores Sabios LLM |
| **B7-E7 (v0.2)** | VERIFICADOR-001 ejecutándose en el runner que envía prompts a Sabios; logs firmados |

---

## §6 Auditores autorizados

| Evidencia | Auditor autorizado | Restricción |
|-----------|--------------------|-------------|
| B7-E1 | Sabio LLM externo distinto del auditor activo del trimestre + T1 | Sabio recibe solo hashes, no contenido |
| B7-E2 | Cowork T2-A está autorizado a auditar (no a custodiar) | OK |
| B7-E3 | Sabio LLM externo + T1 | Ambos requeridos |
| B7-E4 | Sabio LLM externo distinto de los auditores del trimestre auditado + T1 | No autoauditoría |
| B7-E5 | Cowork T2-A + Sabio LLM externo | Cowork puede auditar resultados, no fixtures |
| **B7-E6 (v0.2)** | Cowork T2-A + Sabio LLM externo distinto de la terna | OK |
| **B7-E7 (v0.2)** | T1 + Sabio LLM externo | T1 firma OK final por implicaciones de seguridad |

---

## §7 Riesgos identificados

- **R-B7-1: Filtración inadvertida del set por un Sabio.** v0.1 mencionaba este riesgo asumiendo que el Sabio era custodio. **v0.2 elimina la causa raíz al retirar a los Sabios del rol custodio.** Riesgo residual: si el Sabio recibe contenido de fixtures inadvertidamente (bug del runner que olvida sanitizar), puede loggear el contenido. Mitigación: B7.8 verificación criptográfica de prompts + B7-E7 audit log.
- **R-B7-2: Quórum no alcanzable por indisponibilidad de custodios.** Si 2 de 3 custodios externos no responden, la rotación se atrasa. Mitigación v0.2: B7.5 fallback T1 escrow humano con quórum reducido a 1 hasta restauración.
- **R-B7-3: Convergencia cultural de auditores.** Si los Sabios LLM auditores convergen culturalmente en patrones similares (todos LLMs entrenados en datos públicos), incluso sin ver fixtures sus veredictos pueden ser predecibles y manipulables. Mitigación: B11 terna rotativa diversifica fuentes culturales en el rol auditor + KL divergence inter-modelo.
- **R-B7-4: Compositor que se filtra como custodio en futuro.** Si v2.0 RE-FUNDADO es compuesto por Manus E2 y Manus E2 actúa como custodio, vuelve F16. Mitigación: regla de exclusión binaria explícita (B7.2).
- **R-B7-5 (NUEVO v0.2): Bug de runtime que filtra fixtures al prompt del Sabio.** Si el runner DORY_BENCH tiene un bug que filtra contenido de fixtures al prompt de auditoría enviado al Sabio LLM (por ejemplo, debug log accidental), la separación rol custodio / rol auditor se rompe en runtime. Mitigación: B7.8 verificación criptográfica obligatoria del hash del prompt contra blacklist de fixtures; abort + evento `FIXTURE_LEAK_DETECTED_PROMPT`.
- **R-B7-6 (NUEVO v0.2): Cuenta cloud privada con permisos overshared.** Si la cuenta GCS/S3 que custodia un slice tiene IAM con `allUsers` o `allAuthenticatedUsers`, el slice es accesible a actores no autorizados. Mitigación: T1 documenta IAM allow-list explícita en B7-E2 + audit periódico de IAM por Sabio externo.

---

## §8 No-go binarios

- No se diseña con custodio único (salvo fallback temporal B7.5 con T1 escrow).
- No se diseña con Cowork T2-A o Grok 4 como custodios.
- No se diseña con compositor activo como custodio.
- **v0.2:** No se diseña con Sabio LLM como custodio de slice cifrado.
- No se diseña con persistencia descifrada en runner.
- No se diseña sin audit log público.
- **v0.2:** No se diseña con prompt a Sabio LLM auditor que contenga fixtures.

---

## §9 Decisión T1 requerida (verbatim closure v0.2 §3.9)

T1 debe firmar verbatim, antes de que B7 pueda producir evidencia, los siguientes ítems:

- **D-B7-1:** Selección de la terna inicial de custodios entre las opciones B7.3 v0.2 (a)-(e): T1 escrow / cuenta cloud privada / HSM/KMS / humano delegado / repo privado cifrado por custodio. NO Sabios LLM.
- **D-B7-2:** Selección de la terna inicial de auditores Sabios LLM entre {Gemini 3.1 Pro, DeepSeek R1, Opus 4.7, Kimi K2.6} con calendario trimestral fijo (cross-ref B11).
- **D-B7-3:** Frecuencia de rotación de fixtures (propuesta: 90 días o post-incidente).
- **D-B7-4:** Quórum de descifrado (propuesta: 2-de-3 custodios; fallback 1-de-1 con T1 escrow temporal).
- **D-B7-5:** Repo / almacenamiento concreto para los slices cifrados (propuesta: 3 buckets GCS privados con CMEK + IAM allow-list a custodios; fallback: 3 repos GitHub privados, uno por custodio, con slices cifrados con `age` antes del push y la clave de cifrado fuera del repo bajo control del custodio).

---

## §10 Estado actual del gate

- **Veredicto:** `DRAFT_T1_PENDING`
- **Bloqueado por:** D-B7-1, D-B7-2, D-B7-3, D-B7-4, D-B7-5 (firma magna T1).
- **No-runtime:** este pack es solo diseño documental; no produce B7-E1, B7-E2, B7-E4, B7-E5, B7-E6, B7-E7 (estos requieren runtime real + firma humana).
- **Productores no-runtime cubiertos:** B7-E3 incluido en este pack como DRAFT.
- **Próximo paso:** T1 firma decisiones D-B7-1..D-B7-5 ⇒ custodios producen slices cifrados ⇒ runner DORY_BENCH produce B7-E1, B7-E4, B7-E5, B7-E7 ⇒ Sabio externo audita ⇒ T1 firma magna PASS.

---

## §11 Cross-refs

- **B4** consume los fixtures via DORY_BENCH (medición CVDS).
- **B6** custodios B7 pueden compartir infraestructura criptográfica con custodios B6, pero claves son distintas (slice B7 cifrado con clave del custodio B7, no con clave kill switch B6).
- **B8** la lista taxonómica (a)-(m) incluye "rotación de claves B6 / fixtures B7" como acción magna (categoría h) ⇒ rotación B7 es bloqueada por `local_unreachable: DISABLED_FOR_MAGNA_ACTIONS`.
- **B11** calendario de auditores Sabios LLM B7.4 (Q1 Opus, Q2 DeepSeek, Q3 Gemini, Q4 Kimi) es **el mismo** que el calendario B11. Cross-ref D-B7-2 ↔ D-B11-1.
- **B9** matriz autoridad cubre VERIFICADOR-001 ⇒ Sabio auditor B7 actúa como capa adicional, no sustituye a VERIFICADOR.

---

**Firma magna pendiente.** Este documento es DRAFT y NO canoniza B7.
