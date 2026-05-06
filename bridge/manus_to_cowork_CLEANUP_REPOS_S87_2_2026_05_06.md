# SNAPSHOT FORENSE — Cleanup Repos GitHub Pages Sprint 87.2

**Fecha:** 2026-05-06
**Sprint:** 88 — Tarea 3.B.1
**Operador:** Manus Memento (Hilo B / Ejecutor `kernel/`)
**Comando GO:** Cowork (Hilo A) firmado 2026-05-06
**Modo:** `--keep-last-n 5 --archive --execute` (DSC-S-005: archive default reversible)

---

## Contexto

El pipeline E2E del Sprint 87.2 acumuló 12 repos públicos `monstruo-*-{run_id_short}` durante la fase de smoke productivo iterativo. Este cleanup conserva los 5 más recientes (suficientes para auditoría visual y rollback) y **archiva** los 7 más viejos.

**Decisión Magna DSC-S-005** (Cowork firmado 2026-05-06): se prefirió `gh repo archive` sobre `gh repo delete` por:
1. `archive` solo requiere scope `repo` (ya disponible). `delete` requiere scope `delete_repo` (no disponible, requeriría browser flow de Alfredo).
2. **Reversible** > irreversible. Si en 30 días confirmamos que ninguno hace falta, los borramos en bulk.
3. Cumple objetivo de la task 3.B.1 (≤5 repos `monstruo-*` activos).
4. Snapshot forense (este archivo) cubre el registro auditable.

El script `scripts/cleanup_github_pages_repos.py` (Sprint 88 Tarea 3.B.1) implementa la política TTL del Monstruo. Esta es la primera ejecución productiva.

---

## Guardrails Magna Aplicados

### Guardrail 1 — Snapshot forense

Tabla con los 7 repos a borrar (ordenados por createdAt asc):

| # | Created (UTC) | Last Push (UTC) | Visibility | Repo Name | Files | Sospechosos |
|---|---|---|---|---|---|---|
| 1 | 2026-05-05 20:30:41 | 2026-05-05 20:30:42 | PUBLIC | `monstruo-hac--una-landing-premium-para--3_888e5d` | 1 (solo README) | 0 |
| 2 | 2026-05-05 20:40:29 | 2026-05-05 20:40:30 | PUBLIC | `monstruo-hac--una-landing-premium-para--4_401772` | 1 (solo README) | 0 |
| 3 | 2026-05-05 20:40:33 | 2026-05-05 20:40:34 | PUBLIC | `monstruo-hac--una-landing-premium-para--0_9e2e6c` | 1 (solo README) | 0 |
| 4 | 2026-05-05 20:43:24 | 2026-05-05 20:43:29 | PUBLIC | `monstruo-hace-una-landing-premium-para--9_4a4e12` | 5 (canónicos) | 0 |
| 5 | 2026-05-05 20:44:46 | 2026-05-05 20:44:51 | PUBLIC | `monstruo-hace-una-landing-premium-para--7_f71120` | 5 (canónicos) | 0 |
| 6 | 2026-05-05 20:49:56 | 2026-05-05 20:50:01 | PUBLIC | `monstruo-hace-una-landing-premium-para--3_e85981` | 5 (canónicos) | 0 |
| 7 | 2026-05-05 20:54:09 | 2026-05-05 20:54:15 | PUBLIC | `monstruo-hace-una-landing-premium-para--7_c4ec87` | 5 (canónicos) | 0 |

**Patrón canónico** (4 repos): `.nojekyll`, `README.md`, `index.html`, `monstruo-tracking.js`, `style.css`.
**Patrón fallido** (3 repos): solo `README.md` — fueron creados durante hotfixes pre-fix slugify (rama `monstruo-hac--una-...` con `é` mal escapado, deploy a GitHub Pages falló silenciosamente).

### Guardrail 2 — Verificar secrets

Ejecutado `scripts/_audit_secrets_before_cleanup.py` con `gh api repos/<owner>/<repo>/contents`.

```
VERIFICADO: 0 archivos sospechosos en 7 repos. Safe to delete.
```

Patrones buscados: `.env`, `secrets.json`, `credentials.md`, `*.pem`, `*.key`, `id_rsa`, `api_keys`, `tokens.{json,txt,md}`, `firebase_adminsdk`, `service_account`, `DATABASE_URL`, `SUPABASE_SERVICE`. **Cero coincidencias.**

### Guardrail 3 — Ejecución y verificación post-archive

**Comando ejecutado:**
```bash
python3 scripts/cleanup_github_pages_repos.py --keep-last-n 5 --archive --execute
```

**Salida del script:**
```
Total repos pipeline (monstruo-*): 12
Total repos protegidos (excluidos): 6
A archivar (todos excepto los 5 más recientes): 7
  [OK] monstruo-hac--una-landing-premium-para--3_888e5d
  [OK] monstruo-hac--una-landing-premium-para--4_401772
  [OK] monstruo-hac--una-landing-premium-para--0_9e2e6c
  [OK] monstruo-hace-una-landing-premium-para--9_4a4e12
  [OK] monstruo-hace-una-landing-premium-para--7_f71120
  [OK] monstruo-hace-una-landing-premium-para--3_e85981
  [OK] monstruo-hace-una-landing-premium-para--7_c4ec87
Resultado: 7 archivardos, 0 fallaron
```

**Verificación post-archive (`gh repo list ... isArchived`):**
- Total `monstruo-*`: 12
- **Activos (no archivados): 5** ✅ (los 5 más recientes, conservados)
- **Archivados: 7** ✅ (coincide con plan)

**Estado de los 7 archivados:**

| # | Repo Name | Estado |
|---|---|---|
| 1 | `monstruo-hac--una-landing-premium-para--3_888e5d` | ARCHIVED |
| 2 | `monstruo-hac--una-landing-premium-para--4_401772` | ARCHIVED |
| 3 | `monstruo-hac--una-landing-premium-para--0_9e2e6c` | ARCHIVED |
| 4 | `monstruo-hace-una-landing-premium-para--9_4a4e12` | ARCHIVED |
| 5 | `monstruo-hace-una-landing-premium-para--7_f71120` | ARCHIVED |
| 6 | `monstruo-hace-una-landing-premium-para--3_e85981` | ARCHIVED |
| 7 | `monstruo-hace-una-landing-premium-para--7_c4ec87` | ARCHIVED |

**TODO 30-day window**: si nadie reporta necesidad de estos repos antes de 2026-06-05, se solicita scope `delete_repo` y se borran en bulk.

---

## Repos Conservados (5 más recientes)

| Created | Repo Name |
|---|---|
| 2026-05-05 20:54:51 | `monstruo-hace-una-landing-premium-para--9_a95211` |
| 2026-05-05 20:54:52 | `monstruo-hace-una-landing-premium-para--1_2c15ec` |
| 2026-05-05 20:55:49 | `monstruo-hace-una-landing-premium-para--2_df60e8` |
| 2026-05-05 20:56:36 | `monstruo-hace-una-landing-premium-para--4_d260cc` |
| 2026-05-05 20:58:53 | `monstruo-hace-una-landing-premium-para--2_bcafee` |

El run **`d260cc`** corresponde al smoke productivo final del Sprint 87.2 (Critic Score 1/100 con frase canónica de Alfredo). Se conserva como referencia base para comparar el Sprint 88 (Critic Score esperado ≥80).

---

## Política TTL del Monstruo (canonizada, DSC-S-005)

Documentada en docstring de `scripts/cleanup_github_pages_repos.py`:

- **Default semanal**: cron Lunes con `--older-than-days 7 --archive --execute` (reversible)
- **Manual aggressive**: `--keep-last-n 5 --archive --execute` antes de cada cierre de sprint mayor
- **Delete irreversible** (`--delete --execute`): solo cuando se confirme tras 30 días de archive sin reclamos, requiere scope `delete_repo` agregado
- **Wipe completo**: `--all --archive --execute --confirm` solo en migraciones forzadas
- **Repos protegidos** (lista hardcoded): `el-monstruo`, `monstruo-memoria`, `monstruo-tickets`, `monstruo-mvp`, `monstruo-app`, `monstruo-tracking` — nunca se tocan aunque empiecen con `monstruo-`

## DSC-S-005 (firmado 2026-05-06)

**Default a archive antes que delete (reversible > irreversible para limpieza de namespace).**

Aplica a:
- Limpieza de repos GitHub temporales
- Cleanup de cualquier recurso que tenga primitiva archive disponible
- Operaciones de namespace donde reversibilidad sea razonable

No aplica a:
- Datos sensibles (secrets, PII) → siempre delete con auditoría
- Resources con costo continuo → delete tras snapshot
- Resources que no soporten archive → delete con backup explícito

---
