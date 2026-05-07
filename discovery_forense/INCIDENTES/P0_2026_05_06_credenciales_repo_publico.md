# Incidente P0 — Credenciales en repo público

**Fecha de detección:** 2026-05-06
**Detectado por:** Manus Hilo Catastro durante audit pre-sprint Catastro-A
**Severidad:** P0 (crítico)
**Estado:** EN MITIGACIÓN (rotaciones en curso)
**Sprint asociado:** Sprint S-001 — Security Hardening (post-mitigación)

---

## 1. Resumen ejecutivo

Durante audit preventivo previo a Sprint Catastro-A (siguiendo DSC-G-008 firmado el 2026-05-06), Manus Hilo Catastro detectó que el password del DB Supabase del proyecto del Monstruo estaba hardcoded en al menos 5 scripts del repositorio público `alfredogl1804/el-monstruo` desde el commit `afc461b` (Sprint 51.5, 2026-05-03). En audit ampliado posterior, también se detectó un JWT `service_role` de Supabase con validez hasta 2036 hardcoded como default value en `biblia-github-motor/motor/github_radar.py:32-34` (anti-patrón "default value en `os.environ.get()` con secret real"). Ambos secretos comprometen acceso completo al backend del Monstruo.

Mitigación en curso: rotación del DB password + rotación del service_role JWT + cleanup de repos GitHub Pages acumulados (task 3.B.1 del Sprint 88) + audit ampliado de los repos restantes (`observatorio-merida-2027`, `honcho-railway`).

---

## 2. Cronología

| Fecha | Sprint | Commit | Quién | Acción |
|---|---|---|---|---|
| 2026-05-03 | Sprint 51.5 | `afc461b` | Manus | Pushea `run_migration_013.py`, `run_migration_014.py`, `run_fix_trigger.py` con DSN hardcoded. Cowork firma cierre verde sin auditar contenido de scripts. |
| 2026-05-04 04:36 | (sesión Cowork) | — | Cowork | Pido a Alfredo: "audit Supabase `thoughts`/`episodic` por tokens leakedos". Recomiendo política completa de credenciales como DSC. **No se firmó como DSC** — quedó como recomendación huérfana. |
| 2026-05-04 (post) | Sprint 84-85 | múltiples | Manus | Implementa mi pedido: crea `audit_supabase_tokens.py` + 5 scripts de auditoría de credenciales. **Anti-patrón paradigmático: el script de auditoría DE tokens contiene EL token expuesto.** |
| 2026-05-04 18:26 | (Falso Positivo TiDB) | — | Cowork | Hago `ls scripts/` durante incidente TiDB. Veo nombres `audit_supabase_tokens.py`, `run_migration_014.py`, `inventario_credenciales_ecosistema.sh`. **No audito contenido** — estoy enfocado en TiDB. |
| 2026-05-06 (mañana) | Pre-Catastro-A | — | Manus | Detecta el breach durante audit pre-sprint. **DSC-G-008 funcionando como diseñado.** |
| 2026-05-06 (después) | P0 audit | — | Manus | En audit ampliado detecta JWT `service_role` en `biblia-github-motor`. Severidad CRÍTICA — JWT bypassea RLS, validez 10 años. |
| 2026-05-06 (mediodía) | P0 mitigación | — | Alfredo + Manus | Rotación del DB password Supabase + update Railway env vars (`SUPABASE_DB_URL` en N services) + verify /health. |
| 2026-05-06 (tarde) | P0 mitigación | — | Manus | Rotación del service_role JWT + update Railway env vars (`SUPABASE_SERVICE_KEY` en N services) + refactor de `biblia-github-motor` para quitar default value antipatrón. |

---

## 3. Autoría firmada (3 tiers)

### Tier 1 — Manus (introduce el código vulnerable)

- Hardcodea DSN en al menos 5 scripts cuando podía usar `os.environ.get("DB_URL")`.
- Hardcodea JWT `service_role` como default value de `os.environ.get("SUPA_KEY", "eyJ...")` — anti-patrón peor que hardcoded directo, porque oculta el secret bajo apariencia de env var.
- Patrón se perpetúa por 3+ sprints (51.5 → 84 → 85 → futuro) sin self-correction.

### Tier 2 — Cowork (falla de revisión + recomendación huérfana)

- 2026-05-03: firmé Sprint 51.5 verde sin auditar `scripts/run_migration_*.py`.
- 2026-05-04 04:36: pedí audit de Supabase memory tables sin guardrail explícito de "el script de audit NO debe hardcodear el secret que va a auditar".
- 2026-05-04 18:26: vi los nombres de los scripts en `ls` y no los audité — estaba enfocado en TiDB.
- Recomendé política de credenciales completa (Cero secrets en plaintext, 1Password como bóveda, env vars con scope mínimo, rotación 12 meses, etc.) pero **no la firmé como DSC** — quedó como párrafo en chat de Cowork sin canonización.

### Tier 3 — Estructural (sistema)

- No había pre-commit hook con `gitleaks`/`trufflehog` que bloqueara estos commits en el momento.
- AGENTS.md no prohibía explícitamente DSN hardcoded ni el anti-patrón de default value con secret real.
- El propio script de auditoría de credenciales (`audit_supabase_tokens.py`) era él mismo vulnerable — paradigma de "auditor sin self-audit".
- Ningún CI test rechazaba commits con strings que matcheaban patrones de secrets.

---

## 4. Daños evaluados

### Lo que SE comprometió (potencial)

- DB password del proyecto Supabase `xsumzuhwmivjgftsneov` (rotado 2026-05-06).
- JWT `service_role` del mismo proyecto con validez hasta 2036 (rotado 2026-05-06).
- Acceso teórico completo al backend del Monstruo (memorias `thoughts`, `episodic`, `semantic`, `magna_cache`, `error_memory`, `verification_results`, etc.).

### Lo que NO se comprometió (verificado)

- Backups automáticos Supabase (12h, externos al control con esos secrets).
- API keys de proveedores LLM (OpenAI, Anthropic, Gemini, Grok, Kimi) — estas viven en Railway env vars distintas, no fueron expuestas en repos.
- Stripe / financial credentials (Sprint 90 todavía no integró Stripe).
- Tokens GitHub `gh` PAT (rotados 2026-05-04 en sesión previa de Cowork).

### Indicadores de actividad sospechosa

- **11,159 solicitudes en Supabase últimas 24h** — consistente con uso normal del kernel + Embrión, NO con exfiltración masiva.
- Backups recientes íntegros — no hay evidencia de DROP/DELETE masivos.
- /health verde post-rotación.

**Probabilidad de explotación activa antes de detección: BAJA.** Repo público con tokens visibles 2-3 días, pero patrón de tráfico normal y backup íntegro sugieren que los scrapers automáticos de credenciales o no encontraron los tokens en este repo específico, o no llegaron a usarlos contra el proyecto.

---

## 5. Mitigaciones aplicadas

| # | Acción | Estado | Quién |
|---|---|---|---|
| 1 | Rotación DB password Supabase | EN CURSO / VERDE | Alfredo + Manus |
| 2 | Update Railway `SUPABASE_DB_URL` en todos los services | EN CURSO / VERDE | Manus |
| 3 | Rotación service_role JWT Supabase | EN CURSO | Manus |
| 4 | Update Railway `SUPABASE_SERVICE_KEY` en todos los services | EN CURSO | Manus |
| 5 | Refactor `biblia-github-motor/motor/github_radar.py` (quitar default value) | EN CURSO | Manus |
| 6 | Cleanup repos GitHub Pages acumulados (Sprint 88 task 3.B.1) | EN CURSO | Manus |
| 7 | Audit ampliado en `observatorio-merida-2027` + `honcho-railway` | PAUSADO, retomar | Manus |
| 8 | Pre-commit hooks (gitleaks + trufflehog) | DIFERIDO a Sprint S-001 | Manus |
| 9 | Audit + cleanup de memory tables (`thoughts`, `episodic`, `semantic`) | DIFERIDO a Sprint S-001 | Manus |
| 10 | Refactor de TODOS los scripts (`os.environ[]` fail loud) | DIFERIDO a Sprint S-001 | Manus |

### Decisión sobre purga de historial git

**NO purgar.** Razones:
- Los secrets rotados ya no funcionan — un atacante con el password viejo no puede entrar.
- `git filter-repo` rompe todos los clones existentes (Mac de Alfredo, sandbox de Manus, kernel de Railway si tiene git history, todos los hilos).
- Coordinación es cara y de alto riesgo — un error en filter-repo y el repo queda corrupto.
- Aceptamos exposure histórica + rotación + lección aprendida (codificada en DSCs S-001 a S-005).

---

## 6. DSCs firmados a raíz del incidente

### DSC-S-001 — Política de Credenciales

**Origen:** 2026-05-04 sesión Cowork (recomendado, no firmado). Disparador final: 2026-05-06 breach Supabase password en repo público.

**Reglas inmutables:**

1. CERO credenciales en plaintext en:
   - Git history (commits, diffs, branches)
   - Bridge files (cowork_to_manus.md, manus_to_cowork.md)
   - Notion (no es secret manager)
   - Memory tables (thoughts, episodic, semantic)
   - Logs de Railway/Vercel
   - Skills references/

2. BÓVEDA PRIMARIA: 1Password / Bitwarden / Apple Keychain. Notion solo para documentación de "qué token cubre qué servicio", nunca para el token mismo.

3. RUNTIME:
   - Mac local: `gh auth login` web flow (no PAT manual)
   - Railway/Vercel/Manus: env vars con scope mínimo, una variable por servicio
   - Scripts: `os.environ.get("VAR_NAME")` obligatorio, fail loud si no está set

4. PRE-COMMIT (DSC-S-002 anidado):
   - `gitleaks detect` en pre-commit hook
   - `trufflehog` en pre-push hook
   - Bloquea commit si encuentra patrones de secrets

5. AUDIT EN CIERRE DE SPRINT:
   - Cualquier sprint que toque scripts/, kernel/, tools/, skills/ requiere `bash scripts/_check_no_tokens.sh` ANTES de cierre verde
   - Cowork audita contenido de scripts nuevos antes de firmar verde, no solo lee el reporte de Manus
   - Si script accede a DB/API externa, verificar uso de env var

6. ROTACIÓN:
   - PATs: 12 meses máx
   - DB passwords: rotar al detectar exposure (sin esperar TTL)
   - JWTs service_role: rotar al detectar exposure + revisar política de validez (default Supabase es 10 años — reducir si posible)
   - Auditoría anual de Last Used independiente de rotación

7. POST-INCIDENT:
   - Rotar inmediatamente al detectar exposure
   - Audit logs del recurso comprometido (últimos 90 días)
   - Decisión sobre purga de historial git: caso por caso, default "rotar y aceptar exposure histórica"
   - Sembrar incident como semilla en error_memory + cerrar con DSC

**Violaciones = bloqueo de cierre de sprint hasta remediación.**

### DSC-S-002 — Pre-commit Hooks Obligatorios

- Pre-commit: `gitleaks detect --staged --redact`
- Pre-push: `trufflehog git file://. --since-commit HEAD~5`
- Bloqueo automático si match de patrón de secret
- Bypass solo con `--no-verify` + justificación documentada en commit message

### DSC-S-003 — Scripts Deben Usar Env Vars Sin Defaults Sensibles

- PROHIBIDO: `os.environ.get("VAR", "real_secret")` (default con secret real)
- PROHIBIDO: hardcoded DSN, API key, JWT, password en código fuente
- REQUERIDO: `os.environ["VAR"]` (raise KeyError si no está) o `os.environ.get("VAR")` con explicit raise si None
- DEFAULT VALUES permitidos solo para configuración no-sensible (timeouts, paths, flags)

### DSC-S-004 — Anti-patrón "Default Value con Secret Real"

Sub-patrón específico de DSC-S-003, codificado por separado por su severidad paradigmática:

```python
# PROHIBIDO — el secret está en código aunque parezca env var:
SUPABASE_KEY = os.environ.get("SUPA_KEY", "eyJhbGciOiJIUzI1NiIs...")

# REQUERIDO — fail loud si falta:
SUPABASE_KEY = os.environ["SUPA_KEY"]
# O con manejo de error explícito:
SUPABASE_KEY = os.environ.get("SUPA_KEY")
if not SUPABASE_KEY:
    raise RuntimeError("SUPA_KEY env var required")
```

Este patrón es PEOR que hardcoded directo porque oculta el secret bajo apariencia de env var, dificultando detección visual.

### DSC-S-005 — Default a Archive antes que Delete (cleanup de namespace)

Cuando se hace cleanup de repos / branches / tablas / archivos:
- **Default:** archive (reversible, requiere scope mínimo)
- **Delete:** solo después de archive + 30 días de monitoreo + scope ampliado explícitamente
- **Razón:** reversibilidad > expediencia. Deletes irreversibles solo cuando hay certeza absoluta y registro forense completo.

---

## 7. Semilla operativa para `kernel/error_memory.py`

```python
ErrorRule(
    name="seed_credenciales_dispersas_sin_audit",
    sanitized_message=(
        "Scripts de migración/auditoría con DSN o JWT hardcoded en lugar de "
        "env var. Detectado en commits afc461b, 30fb65f, 021a5c1, 942be4e, "
        "9274813, 1575e22, 4808569, 7c43ba9 (Sprint 51.5 + 84-85). Anti-patrón "
        "específico: default value en os.environ.get() con secret real."
    ),
    resolution=(
        "Sprint debe terminar con `bash scripts/_check_no_tokens.sh` verde + "
        "Cowork audita contenido de scripts nuevos antes de firmar verde. "
        "Scripts que tocan DB/API DEBEN usar os.environ[VAR] (fail loud), NO "
        "os.environ.get() con default value. Pre-commit con gitleaks + "
        "trufflehog obligatorio. Sprint S-001 implementa la infraestructura."
    ),
    confidence=0.99,
    module="kernel.security",
    severity="critical",
)
```

---

## 8. Lo que estaba alertado y no se firmó (auto-crítica de Cowork)

En sesión Cowork 2026-05-04 04:36 UTC, recomendé textualmente a Alfredo:

> "Política duradera (agregar a AGENTS.md):
> 1. Cero credenciales en plaintext en git history, bridge files, ni Notion
> 2. Bóveda primaria: 1Password/Bitwarden
> 3. Mac local: `gh auth login` web flow, no PAT manual
> 4. Servicios remotos: env vars con scope mínimo
> 5. Rotación: 12 meses para PATs, anual auditoría de Last Used"

> "Sembrar como semilla: `seed_credenciales_dispersas_sin_audit`. 8va semilla del proyecto."

> "Query Supabase `thoughts` y `episodic` por leakage de tokens... Si encuentra rows, esos tokens están leakedos en memoria persistente del Monstruo y hay que borrar las rows + matar tokens."

**Esa recomendación no se firmó como DSC, ni se ejecutó la query contra memory tables.** Si ambas hubieran sido firmadas/ejecutadas el 2026-05-04, el breach habría sido detectado y mitigado 2 días antes. Esta es deuda de canonización que se cierra firmando DSC-S-001 a S-005 + ejecutando audit de memory tables como parte de Sprint S-001.

---

## 9. Lo que se hizo bien

- **DSC-G-008 funcionó como diseñado.** Manus auditó codebase ANTES de iniciar Sprint Catastro-A y detectó el breach. Sin DSC-G-008, el sprint habría arrancado con secrets activos en producción.
- **Detección antes de explotación.** Tráfico normal en Supabase, backups íntegros — sugiere que los secrets no fueron explotados pese a 2-3 días de exposure pública.
- **Coordinación humano + agente fluida.** Alfredo + Manus + Cowork colaboraron en el P0 sin pérdida de contexto crítico.
- **Mitigación en curso sin parálisis.** El P0 corre en paralelo con cierre de Sprint 88 (task 3.B.1 cleanup repos avanza simultáneamente). DSC-X-006 (Convergencia Diferida) aplicado al incident response.

---

## 10. Lecciones magna

1. **Recomendaciones huérfanas son deuda.** Si Cowork recomienda algo importante y no se firma como DSC, eso queda como párrafo perdido en chat de sesión y se olvida. Política: toda recomendación de seguridad merece DSC firmado en la misma sesión.

2. **DSC-G-008 debe extenderse a "antes de cierre" además de "antes de specs".** El cierre Sprint 51.5 firmó verde con scripts vulnerables porque Cowork no auditó el contenido de los archivos pusheados, solo leyó el reporte de Manus. Cierre de sprint requiere audit de archivos nuevos, no solo del reporte.

3. **Anti-patrón "default value con secret real" merece codificación específica.** Es peor que hardcoded directo porque oculta el secret bajo apariencia de env var. DSC-S-004 lo nombra y lo prohíbe.

4. **Auditor sin self-audit es paradigma de fallo.** Un script que audita credenciales NO debe contener credenciales hardcoded. Aplicable a cualquier herramienta de seguridad: el hash function debe pasar su propio test.

5. **Rotación coordinada > rotación serial.** Cuando hay múltiples secrets relacionados (DB password + service_role JWT del mismo proyecto), planear rotación coordinada para minimizar downtime y evitar ventanas inconsistentes.

---

**Postmortem firmado por:** Cowork (Hilo A) + Manus (Hilo Catastro + Hilo Ejecutor) + Alfredo González
**Fecha de firma:** 2026-05-06 (al cierre de la jornada, post-mitigación verde)
**Próxima revisión:** Sprint S-001 al cierre — verificar que las 10 acciones de mitigación están en estado COMPLETED.
