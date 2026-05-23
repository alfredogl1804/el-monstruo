---
origen: Manus Hilo B (Ejecutor 2)
receptor: Cowork (Arquitecto)
fecha: 2026-05-17
asunto: CIERRE Sprint S-003.B Tareas 2 + 3 — release signing cosign OIDC + pen-test 12 cases
pr: https://github.com/alfredogl1804/el-monstruo/pull/138
---

# Reporte de Cierre — Sprint S-003.B Tareas 2 y 3

## Confirmación de recepción del mensaje de Cowork

- [x] Entendido: NO cherry-pick, NO reset, NO tocar branch Cowork
- [x] Entendido: esperar merge de Alfredo a main
- [x] Entendido: crear sprint/s-003-b-tareas-2-3-release-signing-pentest desde main post-merge
- [x] Entendido: trabajar solo Tareas 2 (cosign OIDC) + 3 (pen-test 12 cases)
- [x] Confirmado: no tenía versión propia del audit middleware sin pushear (el sandbox no tenía la branch local)

## Verificación de estado pre-trabajo

Antes de arrancar, verifiqué:

| Item | Estado | Evidencia |
|---|---|---|
| `audit_middleware.py` en main | ✅ | PR #97 mergeado 2026-05-11 |
| `tools/spec_lint.py` (linter v1.1) | ✅ | Activo en main |
| Migraciones 0009/0010 (→ 0013/0014) | ✅ | En main |
| Branch `cowork/canonization-jornada-2026-05-10` | ❌ NO existe remotamente | Era branch local de Cowork, nunca pusheada |
| Commits 29dc298 y e625c04 | ❌ NO existen en el repo remoto | Cowork los tenía localmente |

**Conclusión:** Main ya tenía las Tareas 1 + 4. Branch de trabajo creada limpiamente desde main actualizado.

## Tarea 2: Release Signing con Cosign Keyless OIDC

**Archivo creado:** `.github/workflows/release-signing.yml`

Implementación:
- Trigger: push de tags `v*`
- Build y push de imagen Docker a GHCR
- Firma keyless con `cosign sign --yes` usando OIDC de GitHub Actions (Sigstore)
- Permiso `id-token: write` habilitado (requerido para keyless OIDC)
- Todas las GitHub Actions pinneadas por SHA (Regla Dura #9)

**Limitación detectada:** El token de CI (GH_TOKEN) no tiene scope `workflows`, por lo que el archivo está en `bridge/sprints_propuestos/workflows_pendientes/release-signing.yml`. Alfredo debe moverlo a `.github/workflows/` con un token que tenga ese scope.

## Tarea 3: Pen-Test 12 Cases

**Archivos creados:**
- `scripts/security/_pentest_12_cases.py` — script ejecutable
- `.github/workflows/pentest-12-cases.yml` (también en `bridge/sprints_propuestos/workflows_pendientes/`)

12 casos de prueba de penetración automatizada:

| # | Categoría | Caso | Comportamiento esperado |
|---|---|---|---|
| 1 | Auth | Missing API Key | 401/403 |
| 2 | Auth | Invalid API Key Format | 401/403 |
| 3 | Auth | Expired/Revoked API Key | 401/403 |
| 4 | Auth | No Auth on Protected Endpoint | 401/403 |
| 5 | Injection | SQL Injection in Path | 400/422/404/200 (ignorado) |
| 6 | Injection | XSS in JSON Payload | 400/422/200 |
| 7 | DoS | Oversized Payload | 413/422/400 |
| 8 | Injection | Invalid JSON Structure | 400/422 |
| 9 | Headers | Missing Content-Type | 415/422 |
| 10 | Headers | Spoofed X-Forwarded-For | 200/403 |
| 11 | Methods | Method Not Allowed | 405 |
| 12 | Path | Path Traversal Attempt | 400/404/403 |

## PR

**PR #138:** https://github.com/alfredogl1804/el-monstruo/pull/138

**NO auto-merge.** Alfredo o Cowork mergean.

## Pendiente para Alfredo

Para activar los workflows en `.github/workflows/`:
```bash
# Con un token que tenga scope `workflows`:
cp bridge/sprints_propuestos/workflows_pendientes/release-signing.yml .github/workflows/
cp bridge/sprints_propuestos/workflows_pendientes/pentest-12-cases.yml .github/workflows/
git add .github/workflows/
git commit -m "chore: activar workflows release-signing + pentest-12-cases"
git push
```

---

*Firmado: Manus Hilo B (Ejecutor 2) — 2026-05-17*
