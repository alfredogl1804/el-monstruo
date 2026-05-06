# Sprint 88 — Cierre v1.0 PRODUCTO COMERCIALIZABLE

**Owner:** Hilo Ejecutor (Manus)
**Zona protegida:** `kernel/e2e/` + paquetes nuevos
**ETA estimada:** 8-12h reales con Apéndice 1.3 factor velocity 5-8x
**Bloqueos:** ninguno
**Prerequisito:** Sprint 87.2 cerrado verde (ya está, commit `fb6d55e`)
**Dependencias:** ninguna externa

---

## 1. Contexto

Sprint 87.2 declaró **v1.0 BACKEND FUNCIONAL**: el Pipeline E2E lineal de 12 pasos orquesta correctamente, cada paso ejecuta, la URL sale viva, los 4 bloques reales (LLM steps, Critic Visual, Deploy, Traffic) integrados.

Pero el audit de Cowork sobre Sprint 87.2 separa dos conceptos distintos:

- **v1.0 BACKEND FUNCIONAL** = orquestación E2E demostrablemente correcta (✅ cerrado por Manus)
- **v1.0 PRODUCTO COMERCIALIZABLE** = output con Critic Score ≥ 80 + veredicto NO `descartar` + traffic ingestion realmente operando + repos limpios (❌ aún NO)

El Sprint 87 NUEVO original tenía como criterio de cierre *"veredicto comercializable."* El backend está, el output no. Este Sprint 88 cierra esa brecha.

Critic score actual con frase canónica de Alfredo *"hacé una landing premium para vender pintura al óleo artesanal hecha en Mérida"*: **1/100** (sub-scores estética 0, cta_claridad 0, profesionalismo 0, jerarquía visual 5). Veredicto: `descartar`. Esto NO es Gemini juzgando duro — es Gemini diciendo que el HTML que produce el pipeline no es comercializable. Si Alfredo entrega esto a un cliente, el cliente nos despide.

---

## 2. Objetivo único del sprint

Cerrar **v1.0 PRODUCTO COMERCIALIZABLE**: el mismo flow del Sprint 87.2, con el creativo arreglado, ejecutado contra una frase real de Alfredo, devolviendo Critic Score ≥ 80 en al menos una de las 3 sub-métricas principales (estética, cta_claridad, profesionalismo) y veredicto NO `descartar`. Validación humana de Alfredo confirmando "comercializable."

Adicional: arreglar las 4 notas técnicas que Manus reportó honestamente al cierre del 87.2.

---

## 3. Bloques del sprint

### 3.A — Arreglar las 2 notas críticas del cierre 87.2

**3.A.1 — Bypass middleware para `/v1/traffic/ingest`**

Estado actual: middleware global devuelve 401 a requests anónimos. El "traffic soberano" del Sprint 87.2 no funciona en producción — la tabla recibe inserts vía pipeline pero no vía visitantes reales del navegador.

Fix: lista blanca de endpoints que aceptan requests sin Auth header.

Archivos a tocar:
- `kernel/middleware/auth.py` o equivalente — agregar lista `PUBLIC_ENDPOINTS = ["/v1/traffic/ingest"]`
- Test nuevo en `kernel/tests/middleware/test_public_endpoints.py` — verificar que `/v1/traffic/ingest` acepta POST anónimo + endpoints sensibles siguen exigiendo Auth
- Audit log de cuáles públicos se llaman + IP + user-agent (anti-abuso)

Criterio de cierre: smoke productivo desde browser real (sin auth) → POST a `/v1/traffic/ingest` → 200 + insert en `e2e_traffic_log`.

**3.A.2 — Mejorar calidad del creativo HTML**

Estado actual: Critic Score 1/100. El HTML naïve generado por los steps `componentes` + `assembly` es pobre.

Dos paths posibles:
- **Path A (parche):** mejorar prompts de los 2 steps con few-shot examples de landings premium reales (Apple, Stripe, Linear, Anthropic, Vercel). Bajo costo, alto retorno marginal pero limitado.
- **Path B (arquitectónico):** conectar `kernel/embriones/creativo/` (existe en repo según Manus) en lugar del HTML naïve actual. Es la integración correcta con el ecosistema de Embriones — es lo que el patrón "el Pipeline invoca Embriones especializados" dice.

**Recomendación: Path B.**

Archivos a tocar:
- `kernel/e2e/pipeline.py` — reemplazar invocaciones HTML directas por `from kernel.embriones.creativo import generar_creativo` o equivalente
- Validar que el output del Embrión Creativo tiene la forma que espera `assembly`
- Adaptar `assembly` para consumir output del Creativo en lugar de output naïve
- Test E2E nuevo `kernel/tests/e2e/test_pipeline_creativo_real.py`

Si Path B no está listo (el Embrión Creativo no funciona), fallback a Path A con few-shot examples (4-6 landings premium en el prompt).

Criterio de cierre: smoke con frase canónica de Alfredo → Critic Score ≥ 80 en al menos 1 de 3 sub-métricas (estética / cta_claridad / profesionalismo) + veredicto NO `descartar`.

### 3.B — Arreglar la nota media + cosmética

**3.B.1 — TTL o repo único para GitHub Pages**

Estado actual: cada smoke productivo crea un repo público con basura. Acumulan ruido + costo + privacidad pobre.

Recomendación: **un solo repo `el-monstruo-pipeline-output` con branches por `run_id`.**

Archivos a tocar:
- `kernel/e2e/deploy/github_pages.py` o equivalente — cambiar de "crear repo nuevo" a "crear branch en repo único"
- El repo `el-monstruo-pipeline-output` se crea una vez (puede ser via script de bootstrap one-shot)
- URL viva queda `https://alfredogl1804.github.io/el-monstruo-pipeline-output/<branch_or_path>/`

Alternativa si no funciona en GitHub Pages con branches (limitación conocida): branches con CNAME custom + GitHub Actions que despliega cada branch a un subdominio (más infra).

Si la alternativa es muy compleja, **fallback aceptable: TTL automático que borra repos > 7 días** vía GitHub API, ejecutado por cron del kernel.

Criterio de cierre: 3 smokes consecutivos → cero repos públicos creados nuevos (todos van al repo único en branches diferentes).

**3.B.2 — Propagar `provider` al `output_payload` del run**

Trivial. ~30 min. El campo `provider` está correcto en `e2e_step_log.payload.provider=github_pages` pero no llega al `output_payload` del run final. Fix: pasar el provider del step de deploy al campo del run.

Archivos a tocar:
- `kernel/e2e/pipeline.py` — al cerrar el run, leer `provider` del último step de deploy y propagarlo
- Test que verifica `output_payload['provider']` no está vacío

### 3.C — Cierre real de v1.0 PRODUCTO

**3.C.1 — Smoke productivo con frase real de Alfredo**

Mismo flow del Sprint 87.2 con el creativo arreglado. Frase canónica:

> *"hacé una landing premium para vender pintura al óleo artesanal hecha en Mérida"*

Criterio:
- Critic Score Gemini Vision ≥ 80 en al menos 1 de 3 sub-métricas
- Veredicto NO `descartar`
- URL viva HTTP 200
- Traffic ingestion funcionando (visitar URL → row en `e2e_traffic_log`)
- Pipeline 12/12 steps completados sin warnings críticos

**3.C.2 — Validación humana de Alfredo**

Alfredo abre la URL viva del 3.C.1 y emite veredicto:

- ✅ "comercializable" — Sprint 88 cerrado verde
- ❌ "no comercializable" — vuelta al 3.A.2 con feedback específico, sprint NO cerrado

Sin validación humana el cierre es solo automático. El Critic Score es necesario pero no suficiente.

### 3.D — Integración con v1.2 firmada (opcional si hay tiempo, mover a Sprint 89 si no)

**3.D.1 — Pipeline E2E gana paso pre-build "API contract de convergencia"**

Per DSC-X-006 firmado en v1.2. Cuando el pipeline genera una empresa-hija nueva, define qué APIs expone para integrarse con otras del portfolio en el futuro (CIP, Marketplace, etc.).

Archivos a tocar:
- `kernel/e2e/pipeline.py` — paso 0 nuevo `convergence_contract` antes de `intake`
- Output del paso: JSON con `provides_apis: [...]` y `consumes_apis: [...]` que se persiste en metadata del run

**3.D.2 — Critic Visual evoluciona a familia: + Critic Brand**

Per visión v1.2 Cap 4 ampliado. Critic Visual (existente) evalúa diseño general. Critic Brand (nuevo Embrión) valida coherencia con DSC-MO-002 (paleta forja+graphite+acero) + DSC-G-004 (naming, error format, etc.).

Para Tier Simple del Pipeline E2E basta los dos. Para Tier Regulated Financial (CIP futuro) entrarán Critic Legal + Critic Financial.

Archivos a tocar:
- `kernel/embriones/critic_brand/` (nuevo)
- `kernel/e2e/pipeline.py` — invocar Critic Brand en paralelo a Critic Visual
- Gate de cierre: AMBOS critics ≥ 80 (no solo Visual)

---

## 4. Magnitudes esperadas

- ~1,500 LOC nuevas
- ~6-10 archivos nuevos + ~3-5 modificados
- ~15-20 tests nuevos
- 3 smokes productivos durante el sprint (post-A.2, post-B.1, post-C.1)

---

## 5. Disciplina aplicada (recordatorio Brand DNA + Memento)

Toda la disciplina firmada en Sprint 87.x sigue activa:

- ✅ Capa Memento en cada componente nuevo (no bloquear pipeline si falla)
- ✅ Brand DNA: errores con identidad — `creativo_generar_*_failed`, `critic_brand_evaluate_*_failed`, `traffic_middleware_bypass_*_failed`, `deploy_pages_branch_create_*_failed`
- ✅ Anti-Dory: stash → pull rebase → pop antes de cada commit
- ✅ NO heredoc al bridge (semilla 40)
- ✅ LLM-as-parser con sanitización schema (semilla 39)
- ✅ Privacy-first
- ✅ Tests con prod real antes de declarar cierre (semilla 51 candidata, validar smoke productivo cada vez)

---

## 6. Cierre formal

Cuando los 4 bloques (3.A + 3.B + 3.C + opcional 3.D) cierren verde, Hilo Ejecutor declara:

> 🏛️ **v1.0 PRODUCTO COMERCIALIZABLE — DECLARADO**

Y reporta al bridge con tabla de evidencia (URL viva del smoke final + Critic Scores + run_id + commits + magnitudes).

---

## 7. Coordinación con Cowork (Hilo A)

- Cowork audita el cierre de v1.0 PRODUCTO igual que auditó el cierre de v1.0 BACKEND
- Cowork valida que las 4 notas técnicas quedaron resueltas (no parcheadas)
- Cowork firma Semilla 51 (tests con prod real) en Capilla cuando este sprint la valide empíricamente

---

— Cowork (Hilo A), spec preparada 2026-05-06 post v1.2 firmado.