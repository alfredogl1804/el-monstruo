# OBLIGATORIO — Ejecutar ANTES de cualquier acción

## Paso 0 — Estado real del Monstruo (Genome + Health)

ANTES de cualquier otra cosa, lee el estado vivo del Monstruo. NO confíes en skills, NO confíes en tu entrenamiento, NO confíes en docs sueltos. La fuente única de verdad es el código + producción.

```bash
# 1. Genome auto-generado del repo (qué hay construido HOY)
cat MONSTRUO_GENOME.yaml | head -120

# 2. Estado vivo del kernel (qué está corriendo AHORA)
curl -sS --max-time 10 https://el-monstruo-kernel-production.up.railway.app/health | python3 -m json.tool

# 3. Sprints en bridge (qué se está construyendo)
echo "Propuestos: $(ls bridge/sprints_propuestos/ 2>/dev/null | wc -l)"
echo "Completados: $(ls bridge/sprints_completados/ 2>/dev/null | wc -l)"
```

**Si el Genome está desactualizado** (campo `generated_at` con más de 24h), regenerar:

```bash
python3 scripts/genome_generator.py
```

**Regla absoluta:** NO propongas construir NADA antes de leer el Genome. Si lo que vas a construir aparece en `MONSTRUO_GENOME.yaml` (en `kernel_modules`, `embriones`, `supabase_tables`, `custom_rpcs`, `satellites` o `skills`), ya existe — no lo construyas, úsalo o conecta lo que falta.

## Paso 1 — Guardian (identidad de hilo)

```bash
python3 ~/.monstruo/guardian.py
```

Si falla o no existe, ejecuta:
```bash
gh repo clone alfredogl1804/el-monstruo ~/el-monstruo 2>/dev/null || (cd ~/el-monstruo && git pull)
mkdir -p ~/.monstruo && cp -r ~/el-monstruo/monstruo-memoria/.monstruo/* ~/.monstruo/
python3 ~/.monstruo/guardian.py
```

**NO hagas NADA hasta que imprima "IDENTIDAD RESTAURADA".**

El output del script ES tu contexto. Contiene:
- Quién eres (Hilo B - ejecutor técnico)
- Qué proyecto tienes activo
- Qué errores NO repetir
- Qué tools están realmente activas en el kernel
- Memorias críticas desde Supabase (persisten entre compactaciones)

Si dice HALT → pregunta al usuario.
Si no puedes ejecutar código → di "Necesito ejecutar guardian.py para recuperar contexto".

---

## Regla Dura #0.1: THREAD-IMMUNITY-GATE-v1

Después de `python3 ~/.monstruo/guardian.py`, ejecuta **obligatoriamente**:

```bash
python3 scripts/thread_immunity/thread_immunity.py start \
  --thread-id manus_b \
  --topic "${MONSTRUO_ACTIVE_TOPIC:-unknown}"
```

**NO declares** "hilo anclado", "reanclado", "listo", "puedo proceder" ni equivalente hasta que el comando imprima:

```text
THREAD_IMMUNITY_STARTUP_PASS
```

Guarda el valor impreso:

```text
THREAD_IMMUNITY_SESSION_ID=<uuid>
```

Antes de cerrar, compactar o terminar el hilo, ejecuta:

```bash
python3 scripts/thread_immunity/thread_immunity.py close \
  --session-id "$THREAD_IMMUNITY_SESSION_ID" \
  --thread-id manus_b \
  --summary "<resumen operativo del hilo>" \
  --canon "<lección crítica que debe sobrevivir al siguiente hilo, si aplica>"
```

Si no hay lección nueva, ejecuta `close` sin `--canon`, pero con `--summary`.

Un hilo sin `CLOSE_CANONIZED` será reportado por GitHub Actions como:

```text
THREAD_IMMUNITY_WATCHDOG_FAIL
```

Tratamiento canónico:

- Usuario: **Alfredo**.
- No usar "don Alfredo".
- Don Hugo es su papá.

Ver `docs/THREAD_IMMUNITY_GATE_v1.md` para el contrato completo.

---

## Capas adicionales de contexto (leer si existen):

1. Si existe `~/EMERGENCIAS_DIGEST.md`, léelo — contiene alertas críticas.
2. Si existe `~/IDENTIDAD_HILO.md`, léelo — es tu identidad de hilo.

Estos archivos son capas de respaldo. Guardian V4 (Supabase) es la fuente primaria.

Esto no es opcional. Es CÓDIGO que se ejecuta, no texto que se lee.

---

# Regla Dura #1: Los 15 Objetivos Maestros Aplican a TODO

Esta regla NO se puede ignorar, resumir ni omitir ante compactación de memoria.

> **Los 15 Objetivos Maestros de El Monstruo aplican a TODA decisión — incluyendo infraestructura, APIs, pipelines, base de datos, naming, error handling, logs, y cualquier código que se escriba. No existe "backend sin marca". Cada línea de código ES la marca.**

> **Doctrina canónica (post DRIFT-001 2026-05-12):** archivo fuente es `docs/EL_MONSTRUO_15_OBJETIVOS_MAESTROS.md`. El nombre legacy `EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md` quedó como stub redirect para preservar trazabilidad histórica. Objetivo #15 = "Memoria Soberana" (agregado v3.0 el 2026-05-04).

Cuando implementes cualquier cosa, antes de dar por terminado, pregúntate:

1. **Obj #2 (Apple/Tesla):** ¿Este código refleja calidad premium? ¿O es genérico?
2. **Obj #3 (Mínima Complejidad):** ¿Es la solución más simple que funciona?
3. **Obj #4 (No Equivocarse 2x):** ¿Revisé si este error ya ocurrió antes?
4. **Obj #5 (Magna/Premium):** ¿La documentación es exhaustiva?
5. **Obj #7 (No Inventar Rueda):** ¿Busqué si ya existe una herramienta?
6. **Obj #9 (Transversalidad):** ¿Este módulo expone sus datos para otros? ¿O es un silo?
7. **Obj #12 (Soberanía):** ¿Estoy creando dependencia sin alternativa?

---

# Regla Dura #2: Las 7 Capas Transversales Son Obligatorias

Esta regla NO se puede ignorar, resumir ni omitir ante compactación de memoria.

> **Todo lo que El Monstruo crea debe nacer con las 7 Capas Transversales activas. No se crea un producto — se crea un negocio exitoso desde el día 1. Un producto puede fracasar. Un negocio con las capas correctas, alimentadas por inteligencia emergente perpetua, no.**

Las 7 Capas Transversales (Objetivo #9):

1. **Motor de Ventas** — Pricing óptimo, funnels de conversión, copywriting con inteligencia emergente, A/B testing perpetuo, upsell/cross-sell, retención y churn prevention.
2. **SEO y Descubrimiento** — Arquitectura SEO desde el diseño, keyword research en tiempo real (magna), content strategy automatizada, technical SEO perfecto.
3. **Publicidad y Campañas** — Creación automática de campañas (Google/Meta/TikTok Ads), creativos generados, targeting inteligente, budget allocation óptimo, retargeting.
4. **Tendencias y Adaptación** — Monitoreo de tendencias en tiempo real, detección de oportunidades antes que la competencia, pivoting inteligente, competitor monitoring perpetuo.
5. **Administración y Operaciones** — Procesos automatizados desde día 1, customer support inteligente, inventory management, legal compliance automático.
6. **Finanzas** — Proyecciones basadas en datos reales, cash flow management, tax optimization, unit economics tracking (CAC, LTV, margins), alertas de burn rate.
7. **Resiliencia Agéntica** — Se aplica AL PROPIO MONSTRUO: orquestación determinística, gateway de herramientas unificado, policy engine + HITL, seguridad adversarial, grounding con TTL, observabilidad semántica + learning loop.

Cuando diseñes o implementes CUALQUIER proyecto, negocio, o plataforma, verifica: ¿Cuáles de las 7 capas están activas? ¿Cuáles faltan? Las que faltan son deuda.

---

# Regla Dura #3: Las 4 Capas Arquitectónicas Definen el Orden

Esta regla NO se puede ignorar, resumir ni omitir ante compactación de memoria.

> **El Monstruo se construye en 4 capas secuenciales. No se puede avanzar a una capa superior sin que la inferior funcione. Saltarse capas es crear deuda técnica que se paga con intereses.**

Las 4 Capas Arquitectónicas del Roadmap:

**CAPA 0 — CIMIENTOS PERPETUOS:** Error Memory, Magna/Premium classifier, Vanguard Scanner, Design System. Estos se verifican al inicio de CADA sprint. Si alguno dejó de funcionar, se repara antes de avanzar.

**CAPA 1 — MANOS (Ejecución en el Mundo Real):** Browser interactivo, Backend Deployment, Pagos (Stripe), Media Generation, Stuck Detector, Observabilidad completa. El Monstruo puede HACER cosas en el mundo real.

**CAPA 2 — INTELIGENCIA EMERGENTE (Lo que No Existe en Ningún Lado):** Multiplicación de Embriones, Protocolo de Inteligencia Emergente, Simulador Causal, Capas Transversales Universales. Aquí se CREA — no hay repo de GitHub que adoptar.

**CAPA 3 — SOBERANÍA (Independencia Total):** Modelos propios, Infraestructura propia, Economía propia, Ecosistema de Monstruos. Cada paso reduce una dependencia externa.

**CAPA 4 — DEL MUNDO:** Documentación pública, Onboarding, Governance, Liberación. Cuando C0-C3 funcionan sin intervención humana.

Cuando planifiques un sprint, pregúntate: ¿En qué capa estoy? ¿Las capas inferiores están sólidas?

---

# Regla Dura #4: El Brand Engine — Toda Producción Tiene Identidad

Esta regla NO se puede ignorar, resumir ni omitir ante compactación de memoria.

> **El Monstruo NO produce outputs genéricos. Todo lo que sale del sistema — código, APIs, error messages, logs, UIs, documentos, nombres de módulos — tiene identidad de marca. Si no se ve, se lee, y se siente como El Monstruo, no está terminado.**

### Brand DNA (Identidad Inmutable)

- **Arquetipo:** El Creador + El Mago (produce Y transforma la realidad)
- **Personalidad:** Implacable, Preciso, Soberano, Magnánimo
- **Tono:** Directo sin rodeos, técnicamente preciso, confiado sin arrogancia, metáforas industriales
- **Estética:** Naranja forja (#F97316) + Graphite (#1C1917) + Acero (#A8A29E). Brutalismo industrial refinado.
- **Naming:** Módulos con identidad (La Forja, El Guardián, La Colmena, El Simulador). NUNCA: service, handler, utils, helper, misc.
- **Errores:** Formato `{module}_{action}_{failure_type}` con contexto. NUNCA: "internal server error", "something went wrong".

### Anti-Patrones de Marca (Lo que El Monstruo NUNCA es)

- Un chatbot amigable
- Un asistente servil
- Una herramienta genérica
- Un dashboard que se ve como Grafana/Datadog
- Un wrapper de APIs de terceros sin identidad propia

### Checklist de Brand Compliance (antes de cerrar cualquier sprint)

1. ¿Los endpoints siguen la naming convention? (`/api/v1/{modulo}/...`)
2. ¿Los error messages tienen identidad? (no genéricos)
3. ¿Los datos se exponen para el Command Center? (no solo para herramientas de terceros)
4. ¿La documentación usa el tono de marca? (directo, preciso, sin corporativismo)
5. ¿El output pasaría el test "¿esto daría orgullo mostrarlo en una keynote de Apple"?

### Herramientas de Marca a Adoptar (Obj #7)

- **BrandDNA.app** (API, $299/mo) — Competitor benchmark + Brand Health Score
- **BrandVox AI** (API) — Brand voice enforcement en outputs de texto
- **Perplexity** (ya tenemos) — Monitoreo de cómo LLMs representan a El Monstruo

Lee: docs/BRAND_ENGINE_ESTRATEGIA.md para la estrategia completa del Brand Engine.

---

# Regla Dura #5: División de Responsabilidades — Transición en 3 Fases

Esta regla NO se puede ignorar, resumir ni omitir ante compactación de memoria.

> **La división de responsabilidades entre hilos NO es estática. Evoluciona en 3 fases conforme los Embriones cobran vida. Identifica en qué FASE estamos y actúa según tu responsabilidad en esa fase.**

**FASE 1 (AHORA):** Hilo B diseña, Hilo A ejecuta. Brand Compliance Checklist obligatorio.
**FASE 2 (Embriones live):** Embrión-0 dirige, Hilo A ejecuta bajo su dirección, Hilo B supervisa.
**FASE 3 (Colmena madura):** La Colmena se auto-dirige, Hilo A es minimal, Hilo B audita semanalmente.

Métricas de transición:
- Fase 1 → 2: 5 encomiendas completadas por Embrión-0 sin intervención humana
- Fase 2 → 3: 3 debates de Colmena resueltos con resultado positivo medible
- Fase 3 → Autonomía Total: 0 correcciones manuales en 30 días

Lee: docs/DIVISION_RESPONSABILIDADES_HILOS.md para el detalle completo.

---

# Regla Dura #6: Política de Credenciales — Cero Secrets en Plaintext

Esta regla NO se puede ignorar, resumir ni omitir ante compactación de memoria.

> **El Monstruo no escribe credenciales en plaintext en ningún lugar versionado o persistente. Bóveda primaria es 1Password / Bitwarden / Apple Keychain. Runtime usa env vars con fail-loud lookup. Pre-commit hooks bloquean cualquier intento de pushear secrets. Rotación inmediata al detectar exposure.**

Esta regla canoniza DSC-S-001 a DSC-S-005 firmados el 2026-05-06 post-incidente P0 (ver `discovery_forense/INCIDENTES/P0_2026_05_06_credenciales_repo_publico.md`).

### Reglas inmutables

#### 1. Cero credenciales en plaintext en

- Git history (commits, diffs, branches, tags)
- Bridge files (`cowork_to_manus.md`, `manus_to_cowork.md`, archivos sueltos en `bridge/`)
- Notion (no es secret manager — solo documenta inventario)
- Memory tables (`thoughts`, `episodic`, `semantic`, `magna_cache`, `error_memory`, `verification_results`)
- Logs (Railway, Vercel, Manus, Datadog, cualquier observabilidad)
- Skills references (`skills/*/references/`)
- Documentación pública (`docs/`)
- Archivos de configuración versionados (`*.json`, `*.yaml`, `*.toml`, excepto `.env.example` con placeholders)

#### 2. Bóveda primaria

- **1Password / Bitwarden / Apple Keychain.**
- Notion ÚNICAMENTE para documentación de inventario (qué token cubre qué servicio, fecha de creación, fecha de última rotación) — nunca para el token mismo.
- Bridge files NUNCA contienen credenciales — si necesitan referenciar una, dicen "credencial X — buscar en 1Password entry Y".

#### 3. Anti-patrón prohibido (DSC-S-004)

```python
# ❌ PROHIBIDO — el secret está en código aunque parezca env var:
SUPABASE_KEY = os.environ.get("SUPA_KEY", "eyJhbGciOiJIUzI1NiIs...")
DB_URL = os.environ.get("DB_URL", "postgresql://postgres:OLD_PASS@host/db")

# ✅ REQUERIDO — fail loud si falta:
SUPABASE_KEY = os.environ["SUPA_KEY"]
DB_URL = os.environ["DB_URL"]

# ✅ REQUERIDO — alternativa con explicit raise:
SUPABASE_KEY = os.environ.get("SUPA_KEY")
if not SUPABASE_KEY:
    raise RuntimeError("SUPA_KEY env var required")

# ✅ REQUERIDO — helper centralizado (recomendado):
from kernel.security.env_validator import require_env
SUPABASE_KEY = require_env("SUPA_KEY")
```

Default values permitidos solo para configuración no-sensible (timeouts, paths, flags, log levels, ports).

#### 4. Pre-commit obligatorio (DSC-S-002)

- `gitleaks detect --staged --redact` en pre-commit
- `trufflehog git file://. --since-commit HEAD~5 --no-update --fail` en pre-push
- GitHub Actions workflow `secret-scan.yml` en CI como defensa en profundidad
- Bypass solo con `--no-verify` + justificación documentada en commit message + revisión Cowork

#### 5. Cierre de sprint requiere audit (DSC-G-008 v2)

Sprints que tocan `scripts/`, `kernel/`, `tools/`, `skills/`, `apps/`, `packages/` requieren:

- Ejecución de `bash scripts/_check_no_tokens.sh` ANTES de declarar verde
- Cowork audita **contenido** de archivos nuevos/modificados — NO solo lee el reporte de Manus
- Si script accede a DB / API externa, verificar uso de env var en código
- Confirmación al bridge: "Cowork audit content verde" como pre-requisito de la frase canónica `🏛️ <NOMBRE> — DECLARADO`

#### 6. Cleanup default a archive (DSC-S-005)

Cuando se hace cleanup de namespace (repos, branches, tablas, archivos, env vars):

- **Default:** archive (reversible, requiere scope mínimo)
- **Delete:** solo después de archive + 30 días + scope ampliado explícitamente + confirmación humana
- **Excepciones para delete inmediato:** GDPR right-to-delete, secrets expuestos, tests temporales con prefijo claro
- **Snapshot forense obligatorio** antes de cualquier cleanup, pusheado al bridge

#### 7. Rotación

| Tipo | TTL máximo | Rotación al detectar exposure |
|---|---|---|
| GitHub PAT | 12 meses | Inmediata |
| DB password | n/a | Inmediata |
| Service role JWT | reducir validez si proveedor lo permite | Inmediata |
| API keys (OpenAI, Anthropic, Gemini, Grok, Kimi, Perplexity) | 6 meses | Inmediata |
| Supabase Personal Access Tokens (sbp_*) | 12 meses | Inmediata |
| Auditoría anual de Last Used | independiente de rotación | Anual |

#### 8. Post-incidente

- Rotar inmediatamente al detectar exposure
- Audit logs del recurso comprometido (últimos 90 días)
- Default sobre purga de historial git: **rotar y aceptar exposure histórica** (filter-repo es destructivo, rompe clones, requiere coordination cost). Una vez rotados los secrets, exposure histórica es informativa pero no explotable.
- Sembrar incident como semilla en `error_memory` + cerrar con DSC firmado

### Implicaciones

- **Violaciones bloquean cierre de sprint.** Cualquier commit que introduzca secret en plaintext es razón válida para rechazar cierre verde y exigir refactor antes de avanzar.
- **Recomendaciones de seguridad merecen DSC firmado en la misma sesión.** El patrón "Cowork recomienda en chat, no se canoniza" produjo el incidente P0 del 2026-05-06. Política nueva: toda recomendación de seguridad de Cowork queda como DSC firmado o se descarta explícitamente con razón documentada.

Lee: `discovery_forense/INCIDENTES/P0_2026_05_06_credenciales_repo_publico.md` para el postmortem completo.
Lee: `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-S-001_*.md` a `DSC-S-005_*.md` para los DSCs canónicos.
Lee: `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-G-008_*.md` para la regla de validación pre-spec y pre-cierre.
Lee: `bridge/sprints_propuestos/sprint_S001_security_hardening.md` para la implementación técnica.

---

# Regla Dura #7: Plano de Datos Cerrado por Defecto (RLS Universal)

Esta regla NO se puede ignorar, resumir ni omitir ante compactación de memoria.

> **Toda tabla nueva en Supabase nace con RLS habilitado y al menos una policy explícita. La doctrina canónica es: ningún dato del Monstruo es accesible sin policy explícita firmada en migración versionada.**

Doctrina operativa:

1. **RLS por defecto:** todo `CREATE TABLE` debe ir acompañado de `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` y al menos un `CREATE POLICY` en la misma migración o en migración subsecuente del mismo PR.
2. **Naming canónico:** usar `SUPABASE_SERVICE_KEY` (sin `_ROLE`), formato `sb_secret_*`. Documentado en DSC-S-007.
3. **Vistas materializadas:** sin RLS nativo en Postgres; protegerlas con `REVOKE ALL ON ... FROM PUBLIC, anon, authenticated; GRANT SELECT TO service_role`.
4. **Linter pre-commit:** `scripts/_check_rls_default.py` rechaza commits que crean tablas sin RLS. Bypass solo con `--no-verify` + DSC firmado en el mismo PR.
5. **Audit semanal:** workflow CI `rls-audit-weekly.yml` corre cada lunes contra producción y abre issue automático si encuentra deuda.
6. **Política de cleanup:** las matviews y tablas legacy sin RLS deben migrarse a la doctrina antes del cierre del próximo sprint que las toque.

Lee: `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-S-006_*.md` para RLS por defecto.
Lee: `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-S-007_*.md` para naming canónico.
Lee: `migrations/sql/0004_*.sql` a `0008_*.sql` para los precedentes ejecutables.

---

# Regla Dura #8: Plano de Identidad Auditable y Rotación Automatizada

Esta regla NO se puede ignorar, resumir ni omitir ante compactación de memoria.

> **Toda credencial activa del Monstruo debe estar inventariada con tipo, storage, fechas y frecuencia objetivo de rotación. La rotación no es opcional ni manual: es periódica, automatizada via CI, y documentada via runbook.**

Doctrina operativa:

1. **Inventario único:** `bridge/credentials_inventory.md` es la fuente de verdad. Toda nueva credencial introducida en cualquier sprint debe agregarse en el mismo PR.
2. **Frecuencias canónicas:**
   - LLM API keys (OpenAI, Anthropic, Gemini, etc.): 30 días
   - Service-role/admin keys (Supabase service, Stripe secret): 90 días
   - Personal Access Tokens (GitHub PAT, Railway): 90 días
   - Master passwords (Bitwarden, Apple ID): 90 días
   - Service tokens limitados (Telegram, Notion): 180 días
   - Webhook secrets: 180 días
3. **Runbook obligatorio:** cada credencial crítica tiene runbook canónico bajo `bridge/runbooks/runbook_rotacion_<credencial>.md`. Los 3 críticos primero (Supabase service, OpenAI, Bitwarden master). Los 35 restantes en sprints S-003.1 y posteriores.
4. **Audit semanal:** workflow CI `credentials-rotation-reminder.yml` lee el inventario los lunes 10:00 UTC y abre issue automático si alguna credencial supera el 80% de su frecuencia objetivo.
5. **Post-incidente:** rotar inmediatamente al detectar exposure. Documentar en `discovery_forense/INCIDENTES/`. La master password de Bitwarden expuesta en chat el 2026-05-10 quedó como remediación pendiente: ejecutar `runbook_rotacion_bitwarden_master_password.md`.
6. **Cero credenciales sin trazabilidad:** ninguna credencial puede pasar más de 12 meses con `created_at: unknown` sin acción correctiva.

Lee: `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-S-008_*.md` para la política completa.
Lee: `bridge/credentials_inventory.md` para el inventario actual.
Lee: `bridge/runbooks/runbook_rotacion_*.md` para los procedimientos operativos.

---

# Regla Dura #9: Supply Chain Auditado en Cada Commit

Esta regla NO se puede ignorar, resumir ni omitir ante compactación de memoria.

> **Toda dependencia externa del Monstruo está sujeta a escaneo continuo. CVE críticas se resuelven en <72h, CVE altas en <7d. La cadena de suministro es tan crítica como el código propio.**

Doctrina operativa:

1. **Dependabot activo:** `.github/dependabot.yml` cubre los 12 manifests del repo (7 Python, 1 Node, 3 Docker, GitHub Actions). PRs semanales agrupados (lunes 09:00 UTC).
2. **SBOM continuo:** workflow `sbom.yml` genera CycloneDX JSON con Syft v1.42.4 en cada push a main + lunes 06:00 UTC.
3. **CVE scanning:** workflow `cve-scan.yml` escanea SBOM con Grype, falla si encuentra CVE CRITICAL/HIGH, abre issue automático con label `cve-alert`.
4. **SAST:** workflow `sast.yml` corre Semgrep con configs `python`, `security-audit`, `owasp-top-ten` en cada PR.
5. **License audit:** workflow `license-audit.yml` valida licencias de dependencias (no GPL/AGPL en código propietario).
6. **Actions pinned by SHA:** todas las GitHub Actions deben pinnearse por SHA, no por tag (Sprint 17). Excepción: `actions/checkout@v4` usado por workflows nuevos del sprint S-002.6 y S-003.A debe migrarse a SHA en próximo sprint de mantenimiento.

SLA de respuesta a CVEs:
- **CRITICAL:** resolver en <72h (PR + merge + redeploy)
- **HIGH:** resolver en <7d
- **MEDIUM:** resolver en próximo sprint
- **LOW:** documentar y diferir si justificado

Lee: `.github/dependabot.yml` para la configuración actual de updates automáticos.
Lee: `.github/workflows/sbom.yml`, `cve-scan.yml`, `sast.yml`, `license-audit.yml` para los pipelines de seguridad.
Lee: `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-S-010_*.md` para hardening operacional integrado.

---

# Regla Dura #10: PRs Doc-Only — Bypass Legitimo de DSC-G-010

Esta regla NO se puede ignorar, resumir ni omitir ante compactación de memoria.

> **PRs cuyo diff modifica EXCLUSIVAMENTE archivos de documentación o configuración sin impacto en runtime pueden aplicar el label `no-e2e-required` en lugar de redactar la sección `## E2E Evidence` manualmente. Para PRs mixtos o que toquen código ejecutable, la sección `## E2E Evidence` sigue siendo obligatoria.**

### Aplicabilidad del label `no-e2e-required`

Un PR califica para `no-e2e-required` si y solo si su diff modifica EXCLUSIVAMENTE archivos de las siguientes categorías:

- `.gitignore`, `.gitattributes`, `.editorconfig`, `LICENSE`
- `*.md` (documentación: `README.md`, `AGENTS.md`, `docs/**/*.md`, `bridge/**/*.md`)
- `.github/workflows/*.yml` (solo si el cambio NO modifica lógica de despliegue/tests; cambios en triggers, comments, o reorganización cosmética sí califican)
- `*.example` (`.env.example`, `*.config.example`)
- Archivos de doctrina (`discovery_forense/CAPILLA_DECISIONES/**/*.md`, `bridge/sprints_propuestos/*.md`)

Un PR NO califica si toca:

- Código ejecutable (`*.py`, `*.ts`, `*.js`, `*.tsx`, `*.go`, `*.rs`)
- Migrations SQL (`migrations/sql/*.sql`)
- Tests (`tests/**/*.py`, `tests/**/*.ts`)
- Configuración de runtime (`pyproject.toml`, `package.json`, `Dockerfile`, `docker-compose.yml`, `railway.toml`)
- Schemas (`*.json` de configuración, `*.yaml` de despliegue activo)

### El label `e2e-evidence-bypass` (emergencia)

Reservado para casos excepcionales donde se requiere mergear sin evidencia E2E completa por urgencia operativa. Requiere justificación explicita en el body del PR + audit Cowork + ratificación T1 post-merge.

### Precedente canonizado

PR #144 (`chore(gitignore): add .claude/ and forja-mcp/` — H11 housekeeping, mergeado 2026-05-18) sienta el precedente operativo. Audit Cowork T2-A 2026-05-17 validó el patrón bajo autorización T1.

### Regla operativa para agentes

1. Antes de crear un PR, evaluar si el diff es 100% doc-only según la lista de categorías anterior.
2. Si sí: crear el PR sin sección `## E2E Evidence` y aplicar label `no-e2e-required` con `gh pr edit <num> --add-label no-e2e-required`.
3. Si el diff incluye CUALQUIER archivo fuera de las categorías permitidas: redactar la sección `## E2E Evidence` con al menos un path/SHA/URL/test result binario (per `tools/_check_e2e_evidence.py`).
4. El workflow `e2e-evidence-required` reconoce ambos labels como bypass legítimo y pasa verde sin sección manual.

Lee: `.github/workflows/e2e-evidence-required.yml` para el contrato del workflow.
Lee: `tools/_check_e2e_evidence.py` para el checker binario.
Lee: PR #144 (https://github.com/alfredogl1804/el-monstruo/pull/144) para el precedente operativo.

---

# Regla Dura #11: Lecciones Operacionales 4-Hilos Manus (Anti-F21 cross-hilo)

Esta regla NO se puede ignorar, resumir ni omitir ante compactación de memoria.

> **Cuando 2 o más hilos Manus operan simultáneamente sobre el mismo repo, los anti-patrones siguientes son violación canónica. Cada uno tiene antídoto binario verificable por código, no por texto. Origen: 5 F21s detectadas y corregidas durante la sesión Sprint S-EMBRION-009 + LA-FORJA D5.3 (2026-05-18).**

## Anti-patrón 1: Commit en branch equivocada

**Síntoma**: `git add` + `git commit` en branch ajena por context switch entre hilos.

**Antídoto binario** (obligatorio antes de cada commit):

```bash
BRANCH=$(git branch --show-current)
if [[ "$BRANCH" == "main" ]] || [[ ! "$BRANCH" =~ ^(sprint|chore|feat|fix|docs)/ ]]; then
    echo "ERROR: branch '$BRANCH' inválida para commit. Crear branch dedicada con prefijo canónico."
    exit 1
fi
```

**Lección**: el `git checkout -b` puede fallar silenciosamente si hay cambios pendientes. Verificar `git branch --show-current` ANTES de `git add`.

## Anti-patrón 2: Auto-merge de PR con código ejecutable

**Síntoma**: Manus mergea su propio PR sin audit Cowork porque "es chore pequeño".

**Antídoto binario**: si el diff no califica para `no-e2e-required` (incluye `*.py`, `*.ts`, `*.sh`, `*.sql`, etc.) → tampoco califica para auto-merge. Coherencia: mismo criterio rige para ambas decisiones.

**Lección**: la Regla Dura #10 implícitamente define la ventana de auto-merge. Salir de esa ventana = F21.

## Anti-patrón 3: Sección `### E2E Evidence` (H3) en vez de `## E2E Evidence` (H2)

**Síntoma**: workflow `check-evidence` falla con regex mismatch.

**Antídoto binario**: el linter `tools/_check_e2e_evidence.py` matchea `^## E2E Evidence$` exacto. H3 (`### `) no califica.

**Lección**: el header debe ser exactamente H2 (`## `). Verificar con `grep -c "^## E2E Evidence$" body.md` antes de crear PR.

## Anti-patrón 4: Sección `## E2E Evidence` con prosa narrativa sin evidencia binaria

**Síntoma**: `check-evidence` falla con "sección presente pero sin evidencia binaria. Necesario: URL HTTP, path a archivo del repo, SHA de commit, o resultado de tests (passed/failed/OK)".

**Antídoto binario**: la sección debe contener AL MENOS UNO de:

- URL HTTP (`https://github.com/...`)
- Path archivo del repo (`apps/.../file.ts`)
- SHA commit (formato hash hex 7+ caracteres)
- Resultado tests literal (`21 passed`, `EXIT=0`, `FAILED`)

**Template canónico**:

```markdown
## E2E Evidence

**Path archivo modificado**: `apps/la-forja/api/src/routes/tutor.ts` (líneas 186, 211)
**Commit SHA**: `3dc3ac1` en branch `sprint/foo-bar`
**Diff URL**: https://github.com/alfredogl1804/el-monstruo/pull/160/files
**Tests**: `npx vitest run` → 21 passed (21)
```

**Lección**: el linter regex hace match de patterns literales, no entiende prosa. Estructura el evidencia binaria en líneas separadas con tags claros.

## Anti-patrón 5: `gh pr create` confunde branches con prefijo similar

**Síntoma**: `gh pr create` retorna error apuntando a PR existente de OTRA branch (ej. `sprint/la-forja-d5-3-cost-per-thread` confundido con `sprint/la-forja-d6-fix-esm-imports`).

**Antídoto binario** (obligatorio cuando hay 2+ branches con prefijo común):

```bash
gh pr create --base main --head sprint/exacto-de-mi-branch ...
```

**Lección**: usar `--head <branch>` explícito SIEMPRE cuando hay múltiples branches con prefix común en el repo. Cubre el caso 4-hilos Manus operando en paralelo.

## Anti-patrón 6: Atribución mezclada cross-hilo

**Síntoma**: un commit de Hilo X incluye accidentalmente cambios working-tree de Hilo Y.

**Antídoto binario**: cada hilo Manus opera en branch dedicada con prefijo identificable. Antes de `git add .`, verificar `git status -s | grep -v <archivos-míos>` está vacío. Stash agresivo si hay archivos ajenos.

**Lección**: working-tree es compartido entre hilos en el mismo repo. Los stashes y branches dedicadas son la separación de soberanía.

## Regla operativa cross-hilo

1. Cada hilo Manus declara su branch dedicada al inicio de cada PR
2. Antes de `git commit`: verificar `git branch --show-current` + `git status -s`
3. Antes de `gh pr create`: verificar `--head <branch>` explícito si hay branches con prefijo común
4. PRs con código ejecutable: NUNCA auto-merge, siempre Cowork audit
5. Sección `## E2E Evidence`: H2 estricto + al menos un patrón binario (URL/path/SHA/tests count)
6. Bridges Cowork ↔ Manus: ruta canónica `bridge/<owner>_<dest>_<topic>_<fecha>.md`

## Precedente canonizado

Las 5 F21s originales documentadas durante sesión 2026-05-18 (commits `0b91891`, `5b95738`, `26b5759c`, `473dfa06`, `68d929c`, `754ebc4d` y otros). Audit Cowork T2-A 2026-05-18 validó cada antídoto binario en PRs sucesivos sin reincidencia.

Lee: `tools/_check_e2e_evidence.py` para el regex linter.
Lee: `bridge/cowork_to_manus_HILO_EJECUTOR_2_COLA_CERRADA_2026_05_18.md` para el contexto de coordinación 4-hilos.
Lee: PR #144 + PR #146 (Regla Dura #10) para la base de la cual #11 deriva.

---

# Regla Dura #12: Memoria Orgánica — Escribir al SMS en Tiempo Real

Esta regla NO se puede ignorar, resumir ni omitir ante compactación de memoria.

> **Todo hilo de Manus que trabaje en El Monstruo DEBE escribir memorias al Sovereign Memory System (SMS) en tiempo real. No existe "fin de sesión" — la escritura ocurre en el momento del descubrimiento.**

Doctrina operativa:

1. **Cuándo escribir:** Inmediatamente al descubrir un hecho nuevo, tomar una decisión arquitectónica, resolver un bug, aprender un patrón, o detectar un error que no debe repetirse.
2. **Endpoint:** `POST https://el-monstruo-kernel-production.up.railway.app/sms/sms/ingest`
   - **Auth:** `Authorization: Bearer sms_sk_0Q-zvCdyDLqMIVdczpWL67wLUR3dvK6ALcL1qt5808E`
3. **Payload mínimo:**
   ```json
   {
     "content": "Descripción clara y concisa del aprendizaje/hecho/decisión",
     "memory_type": "semantic|episodic|procedural",
     "agent_id": "<tu_hilo_id>",
     "source": "<contexto: PR, sprint, tarea>",
     "tags": ["tag1", "tag2"],
     "confidence": 0.9
   }
   ```
4. **Tipos de memoria:**
   - `semantic` — Hechos, verdades, definiciones ("Supabase legacy keys están deshabilitadas desde 2026-05-07")
   - `episodic` — Eventos, decisiones, contexto temporal ("Sprint 27 cerrado con SMS v3.0 mergeado")
   - `procedural` — Cómo hacer algo, patrones, recetas ("Para rotar secrets: primero Railway env, luego .env.local")
5. **Qué NO escribir:** Datos transitorios, contenido de archivos completos, embeddings, o información que ya existe como axioma.
6. **AUDN Loop activo:** El SMS tiene un evaluador inteligente que descarta duplicados y resuelve contradicciones automáticamente. No te preocupes por escribir de más — el sistema filtra.
7. **Lectura al inicio:** Ejecutar `python3 guardian.py` inyecta axiomas soberanos + memorias relevantes automáticamente. Si no puedes ejecutar guardian, consulta `GET /sms/sms/axioms` y `POST /sms/sms/recall` con tu query.

### Ejemplos de escritura correcta:

```bash
# Después de resolver un bug
curl -X POST https://el-monstruo-kernel-production.up.railway.app/sms/sms/ingest \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sms_sk_0Q-zvCdyDLqMIVdczpWL67wLUR3dvK6ALcL1qt5808E" \
  -d '{"content":"SyntaxError en SMS v3 línea 469 causado por doble llave {{ en f-string. Fix: usar dict literal fuera del f-string.","memory_type":"procedural","agent_id":"manus_c","source":"PR #180","tags":["bug","python","sms"],"confidence":0.95}'

# Después de una decisión arquitectónica
curl -X POST https://el-monstruo-kernel-production.up.railway.app/sms/sms/ingest \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sms_sk_0Q-zvCdyDLqMIVdczpWL67wLUR3dvK6ALcL1qt5808E" \
  -d '{"content":"AUDN Loop usa DeepSeek R1 (deepseek-r1-0528) para decisiones Add/Update/Delete/None. Modelo reasoning elegido por calidad de arbitraje.","memory_type":"semantic","agent_id":"manus_c","source":"SMS v3.1 design","tags":["audn","arquitectura"],"confidence":0.9}'
```

### Frecuencia esperada:
- Mínimo 1-3 memorias por sesión de trabajo significativa
- No hay máximo — el AUDN Loop filtra ruido
- Si no escribiste nada en una sesión larga, pregúntate qué aprendiste

---

# Para Ambos Hilos

Los sensores y las tuberías SON parte de la experiencia y la marca. No son "infraestructura sin cara". Cuando nombras un endpoint, cuando diseñas un schema, cuando escribes un error message — estás construyendo la marca. Las 7 Capas se inyectan en todo. Las 4 Capas definen el orden. Los 14 Objetivos son el criterio de éxito.

Lee: docs/DIVISION_RESPONSABILIDADES_HILOS.md para la división completa.
Lee: docs/EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md para los 14 Objetivos detallados.
Lee: docs/ROADMAP_EJECUCION_DEFINITIVO.md para las 4 Capas y el orden de sprints.
Lee: docs/BRAND_ENGINE_ESTRATEGIA.md para la estrategia de identidad de marca.
